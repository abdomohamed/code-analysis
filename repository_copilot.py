import asyncio
from typing import List

from openai import AsyncAzureOpenAI
from chunker import Chunker
from common_models import Question, ModelAnswer

class RepositoryCoPilot:
    def __init__(self, max_chunk_size=2000, client: AsyncAzureOpenAI = None):
        self.chunker = Chunker(max_chunk_size)
        self.client = client
        self.default_system_prompt = "You're an AI assistant that helps people to have more understanding about their source code repositories. Make sure your answers are based on the content of the repository. Another task you can do is by helping in migrating code from one cloud provider libraries to another. In-case of migrating code, make sure to validate the approach of the migration by writing unit tests for the change before and after the migration to validate the change."

    async def ask(self, question: Question, chunks) -> List[ModelAnswer]:
        async def get_response(chunk, model) -> ModelAnswer:
            system_prompt = question.system_prompt if question.system_prompt else self.default_system_prompt

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"{system_prompt} ```\nContext:\n" + chunk + "\n```"},
                    {"role": "user", "content": question.text}
                ],
                temperature=0,
                stream=False
            )
            return ModelAnswer(model=model, answer=response.choices[0].message.content.strip(), content=chunk)

        tasks = []

        for chunk in chunks:
            for model in question.models:
                tasks.append(get_response(chunk, model))

        modelAnswers = await asyncio.gather(*tasks)
        return modelAnswers

    async def refine_answer(self, answers: List[ModelAnswer], question: Question) -> List[ModelAnswer]:
        system_prompt = question.system_prompt if question.system_prompt else self.default_system_prompt

        model_answers = {}

        for answer in answers:
            if answer.model not in model_answers:
                model_answers[answer.model] = []
            model_answers[answer.model].append(answer)

        tasks = []

        async def refine(model, answers: List[ModelAnswer]) -> ModelAnswer:
            combined_answers = "\n\n".join([answer.answer for answer in answers])
            chunks = [answer.content for answer in answers]

            # Calculate the number of tokens needed
            token_count = len(system_prompt.split()) + len(combined_answers.split()) + len(question.text.split())
            print(f"Token count for deployment {model}: {token_count}")

            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"{system_prompt} ```\nContext:\n" + combined_answers + "\n```"},
                        {"role": "user", "content": question.text}
                    ],
                    temperature=1,
                    stream=False
                )
                return ModelAnswer(model=model, answer=response.choices[0].message.content.strip(), content=combined_answers)
            except Exception as e:
                print(f"Error refining answer for model {model}: {e}")
                raise e

        for model, answers in model_answers.items():
            task = refine(model, answers)
            tasks.append(task)

        return await asyncio.gather(*tasks)
