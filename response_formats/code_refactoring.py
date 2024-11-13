from typing import List
from pydantic import BaseModel

class CodeChange(BaseModel):
    source_file: str
    code: str
    is_refactored: bool
    generated_unit_tests: str
    can_generate_unit_tests: bool
    
class CodeRefactoringResponseFormat(BaseModel):
    changes: List[CodeChange]
    summary: str