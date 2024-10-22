from typing import List
from pydantic import BaseModel

class CodeChange(BaseModel):
    source_file_name: str
    destination_file_name: str
    code: str
    is_refactored: bool
    generated_unit_tests: str
    can_generate_unit_tests: bool
    
class CodeRefactoringResponseFormat(BaseModel):
    changes: List[CodeChange]
    
    
