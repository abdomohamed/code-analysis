import asyncio
import json
from threading import Event
from typing import List
import time

import aiofiles

from chunker import Chunker
from common_models import FileType, Question, QuestionAnswer
from file_processor import FileProcessor
from output_persistor import OutputPersistor
from planner import Planner
from repository_copilot import RepositoryCoPilot
from batch_code_saver import BatchCodeSaver
from response_formats.planned_steps import PlanSteps
from steps_executor import StepsExecutor


class Pipeline:
    def __init__(self, questions: List[Question], fileProcessor: FileProcessor, repoCoPilot: RepositoryCoPilot, chunker: Chunker, outputPersistor: OutputPersistor, batchCodeSaver: BatchCodeSaver, planner: Planner, steps_executor: StepsExecutor):
        self.questions = questions
        self.repoCoPilot = repoCoPilot
        self.fileProcessor = fileProcessor
        self.chunker = chunker
        self.outputPersistor = outputPersistor
        self.batchCodeSaver = batchCodeSaver
        self.planner = planner
        self.steps_executor = steps_executor

    async def run(self) -> List[QuestionAnswer]:
        files_content = await self.fileProcessor.read_files()
        chunks = self.chunker.chunk_files(files_content)
        
        # filter chunks based on allowed file types
        
        result = []
        pre_step_summary = []
        
        for question in self.questions:
            prev_plans  = []
            if question.enabled:
                
                if(FileType.ALL not in question.allowed_file_types):
                     allowed_chunks = [chunk for file_type, type_chunks in chunks.items() if file_type in question.allowed_file_types for chunk in type_chunks]
                else:
                    allowed_chunks = [chunk for _, type_chunks in chunks.items() for chunk in type_chunks]
                
                plans_chunks = await self.planner.plan(question, allowed_chunks, prev_plans)
                plans_dict_list = [plan_chunk.plan.to_dict() for plan_chunk in plans_chunks]
                plans = [plan_chunk.plan for plan_chunk in plans_chunks]
                
                prev_plans.extend(plans)
                
                async with aiofiles.open(f"./output/{question.text[:50]}_plan.txt", 'w', encoding='utf-8') as f:
                    await f.write(f"Plan: \n\n{json.dumps(plans_dict_list, indent=4)} \n\n")
                    
                await self.steps_executor.execute(plans_chunks)
                
                # for plan_steps in plans_steps:
                #     answer = await self._ask(question, plan_steps)
                #     result.append(answer)
                # answer = await self._ask(step, chunks, pre_step_summary)
                # pre_step_summary = " ".join([ans.summary for ans in answer])
                # result.append(answer)
        # result = await asyncio.gather(*tasks)
        # await self.outputPersistor.persist(result)
        # await self.batchCodeSaver.save(result)
        
        return result
        

    async def _ask(self, question: Question, planned_steps: PlanSteps) -> List[QuestionAnswer]:
        start_time = time.time()
        chunks_answers = await self.repoCoPilot.ask(question, [])
        # refined_answers = await self.repoCoPilot.refine_answer(chunks_answers, question)
        end_time = time.time()

        result = []

        for answer in chunks_answers:
            result.append(
                            QuestionAnswer
                            (
                                model=answer.model, question=question.text, answer=answer.answer, 
                                summary=answer.summary,
                                time_taken=end_time - start_time, start_time=start_time, end_time=end_time, 
                                content=answer.content
                            )
                        )
        return result