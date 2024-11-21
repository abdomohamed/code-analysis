from typing import List
from pydantic import BaseModel
from enum import Enum

class StepCategory(Enum):
    Addition = "Addition"
    Replacement = "Replacement"
    NoChange = "NoChange"
    
    
class Code(BaseModel):
    before: str
    after: str
    
    def to_dict(self) -> dict:
        return {
            "before": self.before,
            "after": self.after,
        } 

class LineRange(BaseModel):
    start: int
    end: int
    
    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
        } 
        
class Step(BaseModel):
    step_no: int
    description: str
    line_num: str   # Line number of the code change in the source file
    code: Code
    category: StepCategory

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "description": self.description,
            "line_num": self.line_num,
            "code": self.code.to_dict(),
            "category": self.category.value,
        }

class PlanSteps(BaseModel):
    steps: List[Step]
    file_name: str
    
    def to_dict(self) -> dict:
        return {
            "steps": [step.to_dict() for step in self.steps],
            "file_name": self.file_name,
        }

class PlanChunk:
    def __init__(self, chunk, plan):
        self.chunk = chunk
        self.plan = plan
    plan: PlanSteps
    chunk: str