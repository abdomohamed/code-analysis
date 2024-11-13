import asyncio
from threading import Event
from typing import List
import time

from chunker import Chunker
from common_models import FileType, Question, QuestionAnswer
from file_processor import FileProcessor
from output_persistor import OutputPersistor
from repository_copilot import RepositoryCoPilot
from batch_code_saver import BatchCodeSaver


class Pipeline:
    def __init__(self, questions, fileProcessor: FileProcessor, repoCoPilot: RepositoryCoPilot, chunker: Chunker, outputPersistor: OutputPersistor, batchCodeSaver: BatchCodeSaver):
        self.questions = questions
        self.repoCoPilot = repoCoPilot
        self.fileProcessor = fileProcessor
        self.chunker = chunker
        self.outputPersistor = outputPersistor
        self.batchCodeSaver = batchCodeSaver

    async def run(self) -> List[QuestionAnswer]:
        files_content = await self.fileProcessor.read_files()
        chunks = self.chunker.chunk_files(files_content)
        result = []
        pre_step_summary = []
        for step in self.questions:
            if step.enabled:
                answer = await self._ask(step, chunks, pre_step_summary)
                pre_step_summary = " ".join([ans.summary for ans in answer])
                result.extend(answer)
        # result = await asyncio.gather(*tasks)
        await self.outputPersistor.persist(result)
        await self.batchCodeSaver.save(result)
        
        return result
        

    async def _ask(self, question: Question, chunks , pre_step_summary) -> List[QuestionAnswer]:
        start_time = time.time()
        
        if(FileType.ALL not in question.allowed_file_types):
            allowed_chunks = [chunk for file_type, type_chunks in chunks.items() if file_type in question.allowed_file_types for chunk in type_chunks]
        else:
            allowed_chunks = [chunk for _, type_chunks in chunks.items() for chunk in type_chunks]
            
        chunks_answers = await self.repoCoPilot.ask(question, allowed_chunks , pre_step_summary)
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