from abc import ABC, abstractmethod
import aiofiles

from response_formats.code_refactoring import CodeChange

class SaveStrategy(ABC):
    @abstractmethod
    def save(self, file_path: str, code_content: str):
        pass

class FileSaveStrategy(SaveStrategy):
    async def save(self, file_path: str, code_content: str):
        # Write the code content to the file asynchronously
        try:
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(code_content)
            print(f"Code saved to {file_path}")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")

class CodeSaver:
    def __init__(self, code_change: CodeChange, save_strategy: SaveStrategy):
        self.code_change = code_change
        self.save_strategy = save_strategy

    async def save_code_to_file(self):
        file_path = self.code_change.source_file
        code_content = self.code_change.code
        await self.save_strategy.save(file_path, code_content)