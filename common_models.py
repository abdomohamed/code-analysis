from collections import namedtuple
from enum import Enum


ModelAnswer = namedtuple('ModelAnswer', ['model', 'answer', 'content'])

class QuestionAnswer:
    def __init__(self, model: str, question: str, answer: str, time_taken, start_time, end_time, content: str):
        self.model = model
        self.question = question
        self.answer = answer
        self.time_taken = time_taken
        self.start_time = start_time
        self.end_time = end_time
        self.content = content

class FileType(Enum):
    CODE = "Code"
    TEXT = "Text"
    IMAGE = "Image"
    OTHER = "Other"
    ALL = "All"

class Question:
    def __init__(self, text: str, enabled: bool = False, system_prompt: str = None, models=["gpt-4o"], allowed_file_types=[FileType.ALL]):
        self.text = text
        self.enabled = enabled
        self.system_prompt = system_prompt
        self.models = models
        self.allowed_file_types = allowed_file_types

    @staticmethod
    def from_dict(data):
        return Question(data["text"], data["enabled"], data["system_prompt"])