import asyncio
from pathlib import Path
import aiofiles

from common_models import FileType

class FileProcessor:
    def __init__(self, 
                 directory, 
                 folders_to_ignore=[".git", ".github", ".vscode", "node_modules", "__pycache__", "gradle"], 
                 files_to_ignore=['.css', '.js']):
        self.directory = directory
        self.folders_to_ignore = folders_to_ignore
        self.files_to_ignore = files_to_ignore

    async def _read_file(self, filepath):
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as file:
                return filepath.name, self._get_file_type(filepath=filepath),  await file.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return filepath.name, None, None

    def _get_file_type(self, filepath):
        if filepath.suffix in ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.rs', '.go', '.ts', '.php', '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat', '.ps1', '.sql', '.rb', '.pl', '.swift', '.kt', '.groovy', '.scala', '.lua', '.m', '.h', '.hpp', '.hh', '.hxx']:
            return FileType.CODE
        elif filepath.suffix in ['.txt', '.md', '.rst']:
            return  FileType.TEXT
        elif filepath.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return  FileType.IMAGE
        return FileType.OTHER

    async def read_files(self):
        files_content = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        directories = [self.directory]

        while directories:
            dir = directories.pop()
            tasks = []

            for filepath in Path(dir).rglob('*.*'):
                if any(ignored_folder in filepath.parts for ignored_folder in self.folders_to_ignore):
                    continue
                
                if filepath.suffix in self.files_to_ignore:
                    print(f"\nIgnoring file {filepath}\n")
                    continue
                
                if filepath.is_dir():
                    directories.append(filepath)
                    continue
                tasks.append(self._read_file(filepath))

            results = await asyncio.gather(*tasks)

            for filename, type, content in results:
                if content is not None and type is not None:
                    files_content[type].append({filename: filename, content: content})

        return files_content
