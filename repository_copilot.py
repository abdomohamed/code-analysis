import asyncio
from typing import List

import aiofiles
from openai import AsyncOpenAI
from chunker import Chunker
from common_models import Question, ModelAnswer
from model_config import ModelConfigParser
from openai_client_factory import OpenAIClientFactory
from progress_reporter import ProgressReporter
from common_models import PipelineSteps

class RepositoryCoPilot:
    def __init__(self, max_chunk_size=2000, openai_client_factory: OpenAIClientFactory = None, max_tokens=16384, progress_reporter: ProgressReporter = None):
        self._chunker = Chunker(max_chunk_size)
        self._openai_client_factory = openai_client_factory
        self._default_system_prompt = "You're an AI assistant that helps people to have more understanding about their source code repositories. Make sure your answers are based on the content of the repository. Another task you can do is by helping in migrating code from one cloud provider libraries to another. In-case of migrating code, make sure to validate the approach of the migration by writing unit tests for the change before and after the migration to validate the change."
        self._max_tokens = max_tokens
        self._progress_reporter = progress_reporter
        
    async def ask(self, question: Question, chunks) -> List[ModelAnswer]:
        async def get_response(chunk, model) -> ModelAnswer:
            system_prompt = question.system_prompt if question.system_prompt else self._default_system_prompt
            max_completion_tokens = self._max_tokens - len(system_prompt.split()) - len(question.text.split()) - len(chunk.split())
            
            try:
                if(max_completion_tokens <= 0):
                    print(f"Skipping chunk {chunk} for model {model} as it exceeds the token limit")
                    return ModelAnswer(model=model, answer="skipped due to max token limit", content=chunk)
                
                client = await self._openai_client_factory.get_client(model)
                
                messages = [
                    {"role": "system", "content": f"{system_prompt} \n```Content Structure: file_name, file_type, content```\n ```\nContext:\n" + chunk + "\n```"},
                    {"role": "user", "content": question.text}
                ]
                
                ignore_answer = False
                
                if(not question.structured_output):
                    response = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        stream=False,
                        max_tokens=max_completion_tokens
                    )
                else:
                    response = await client.beta.chat.completions.parse(
                        model=model,
                        messages=messages,
                        temperature=0,
                        response_format=question.response_format,
                        max_tokens=max_completion_tokens
                    )
                    
                    ignore_answer = not any(code_change.is_refactored for code_change in response.choices[0].message.parsed.changes)
                
                return ModelAnswer(model=model, answer=response.choices[0].message.content.strip(), content=chunk, ignore=ignore_answer)
                
            except Exception as e:
                print(f"Question: {question.text} for model: {model}, had a skipped chunk due to {e}")
                
                async with aiofiles.open(f"./output/{question.text[:50]}_refined_iqnored_chunks.txt", 'a', encoding='utf-8') as f:
                    await f.write(f"Chunk failed for LLM Model: {model}, prompt: {messages}, and chunk {chunk} The reason was: {e}\n\n")

                return ModelAnswer(model=model, answer="error", content=chunk, ignore=True)
            finally:
                if(self._progress_reporter):
                    self._progress_reporter.update(PipelineSteps.ANSWERING_QUESTIONS, 1)
            
            
        tasks = []

        for chunk in chunks:
            for model in question.models:
                tasks.append(get_response(chunk, model))

        if(self._progress_reporter):
            self._progress_reporter.init_step(PipelineSteps.ANSWERING_QUESTIONS, len(tasks))
            
        modelAnswers = await asyncio.gather(*tasks)
        return modelAnswers

    async def refine_answer(self, answers: List[ModelAnswer], question: Question) -> List[ModelAnswer]:
        system_prompt = question.system_prompt if question.system_prompt else self._default_system_prompt
        
        
        model_answers = {}

        for answer in answers:
            if answer.model not in model_answers:
                model_answers[answer.model] = []
            
            if(answer.ignore):
                continue
            
            model_answers[answer.model].append(answer)

        tasks = []

        async def refine(model, answers: List[ModelAnswer]) -> ModelAnswer:
            combined_answers = "\n\n".join([answer.answer for answer in answers])
            chunks = [answer.content for answer in answers]
            max_completion_tokens = self._max_tokens - len(system_prompt.split()) - len(question.text.split())
            
            # Calculate the number of tokens needed
            token_count = len(system_prompt.split()) + len(combined_answers.split()) + len(question.text.split())
            print(f"Token count for deployment {model}: {token_count}")

            try:
                client = await self._openai_client_factory.get_client(model)
                
                if(not question.structured_output):
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": f"{system_prompt} ```\nContext:\n" + combined_answers + "\n```"},
                            {"role": "user", "content": question.text}
                        ],
                        temperature=0,
                        stream=False,
                        max_tokens=max_completion_tokens
                    )
                else:
                    response = await client.beta.chat.completions.parse(
                        model=model,
                        messages=[
                            {"role": "system", "content": f"{system_prompt} ```\nContext:\n" + combined_answers + "\n```"},
                            {"role": "user", "content": question.text}
                        ],
                        temperature=0,
                        response_format=question.response_format,
                        max_tokens=max_completion_tokens
                    )
                return ModelAnswer(model=model, answer=response.choices[0].message.content.strip(), content=combined_answers, ignore=False)
            except Exception as e:
                print(f"Error refining answer for model {model}: {e}")
                raise e
            finally:
                if(self._progress_reporter):
                    self._progress_reporter.update(PipelineSteps.REFINING_ANSWERS, 1)

        for model, answers in model_answers.items():
            task = refine(model, answers)
            tasks.append(task)

        if(self._progress_reporter):
            self._progress_reporter.init_step(PipelineSteps.REFINING_ANSWERS, len(tasks))
            
        return await asyncio.gather(*tasks)
