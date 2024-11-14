
from pathlib import Path
from typing import Callable, List
import aiofiles

from common_models import QuestionAnswer


class OutputPersistor:
    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def _default_name_strategy(self, output_dir: Path, question_answer: QuestionAnswer) -> str:
        return output_dir / f"{question_answer.model}_question_{question_answer.question[:50]}.txt"
    
    async def persist(self, result: List[QuestionAnswer], filename_strategy: Callable[[Path, QuestionAnswer], str] = None):
        # for question_model_answers in result:
            for question_answer in result:
                filename =  filename_strategy(self.output_dir, question_answer) if filename_strategy else self._default_name_strategy(self.output_dir, question_answer)

                async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
                    await f.write("---------------------Start Answer------------------------\n")
                    await f.write(f"LLM Model: {question_answer.model}\n\n")
                    await f.write(f"Content: {question_answer.content}\n\n")
                    await f.write(f"System Prompt: {question_answer.system_prompt}\n\n")
                    await f.write(f"Question: {question_answer.question}\n\n")
                    await f.write(f"Answer: {question_answer.answer}\n\n")
                    await f.write(f"Summary: {question_answer.summary}\n\n")
                    await f.write(f"Time taken: {question_answer.time_taken:.2f} seconds\n\n")
                    await f.write(f"Start time: {question_answer.start_time}\n\n")
                    await f.write(f"End time: {question_answer.end_time}\n\n")
                    await f.write("---------------------End Answer--------------------------\n")