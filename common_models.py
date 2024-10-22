from collections import namedtuple
from enum import Enum, StrEnum
from typing import Any


ModelAnswer = namedtuple('ModelAnswer', ['model', 'answer', 'content', 'ignore'])

class QuestionAnswer:
    def __init__(self, model: str, question: str, answer: str, time_taken, start_time, end_time, content: str):
        self.model = model
        self.question = question
        self.answer = answer
        self.time_taken = time_taken
        self.start_time = start_time
        self.end_time = end_time
        self.content = content

class FileType(StrEnum):
    CODE = "Code"
    TEXT = "Text"
    IMAGE = "Image"
    OTHER = "Other"
    ALL = "All"

class Question:
    def __init__(self, 
                 text: str, 
                 enabled: bool = False, 
                 system_prompt: str = None, 
                 models=["gpt-4o"], 
                 allowed_file_types=[FileType.ALL],
                 structured_output: bool=False,
                 response_format: Any=None):
        
        self.text = text
        self.enabled = enabled
        self.system_prompt = system_prompt
        self.models = models
        self.allowed_file_types = allowed_file_types
        self.structured_output = structured_output
        self.response_format = response_format

    @staticmethod
    def from_dict(data):
        return Question(data["text"], data["enabled"], data["system_prompt"])