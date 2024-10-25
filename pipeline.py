import asyncio
from threading import Event
from typing import List
import time

from chunker import Chunker
from common_models import FileType, Question, QuestionAnswer
from file_processor import FileProcessor
from output_persistor import OutputPersistor
from repository_copilot import RepositoryCoPilot

class Pipeline:
    def __init__(self, questions, fileProcessor: FileProcessor, repoCoPilot: RepositoryCoPilot, chunker: Chunker, outputPersistor: OutputPersistor):
        self.questions = questions
        self.repoCoPilot = repoCoPilot
        self.fileProcessor = fileProcessor
        self.chunker = chunker
        self.outputPersistor = outputPersistor

    async def run(self) -> List[QuestionAnswer]:
        files_content = await self.fileProcessor.read_files()
        chunks = self.chunker.chunk_files(files_content)
        tasks = [self._ask(question, chunks) for question in self.questions if question.enabled]
        result = await asyncio.gather(*tasks)
        await self.outputPersistor.persist(result)
        
        return result
        

    async def _ask(self, question: Question, chunks) -> List[QuestionAnswer]:
        start_time = time.time()
        
        if(FileType.ALL not in question.allowed_file_types):
            allowed_chunks = [chunk for file_type, type_chunks in chunks.items() if file_type in question.allowed_file_types for chunk in type_chunks]
        else:
            allowed_chunks = [chunk for _, type_chunks in chunks.items() for chunk in type_chunks]
            
        chunks_answer = await self.repoCoPilot.ask(question, allowed_chunks)
        refined_answers = await self.repoCoPilot.refine_answer(chunks_answer, question)
        end_time = time.time()

        result = []

        for answer in refined_answers:
            result.append(
                            QuestionAnswer
                            (
                                model=answer.model, question=question.text, answer=answer.answer, 
                                time_taken=end_time - start_time, start_time=start_time, end_time=end_time, 
                                content=answer.content
                            )
                        )
        return result