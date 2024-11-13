import json
from typing import List

from code_saver import SaveStrategy,CodeSaver
from common_models import QuestionAnswer
from response_formats.code_refactoring import CodeChange

class BatchCodeSaver:
    def __init__(self, save_strategy: SaveStrategy):
        self.save_strategy = save_strategy

    async def save(self, result: List[QuestionAnswer]):
        # for question_model_answers in result:
            for question_answer in result:
                try:
                    # print(f"answer to be saved as code: {question_answer.answer}")
                    content_dict = json.loads(question_answer.answer)
                    changes = [CodeChange(**change) for change in content_dict.get('changes', [])]
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    print(f"Error parsing content: {e}")
                    changes = []
                
                print(f"changes to save: {len(changes)}")
                for code_change in changes:
                    # print(f"saving code: {code_change.code} at {code_change.destination_file_name}")
                    code_saver = CodeSaver(code_change, self.save_strategy)
                    await code_saver.save_code_to_file()