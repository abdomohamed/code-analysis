import asyncio
from pathlib import Path
import aiofiles

from common_models import FileType, PipelineSteps
from progress_reporter import ProgressReporter

class FileContent:
    def __init__(self, filepath ,filename,filetype, content ):
        self.filename = filename
        self.content = content
        self.filepath = filepath
        self.filetype = filetype

class FileProcessor:
    def __init__(self, 
                 directory, 
                 folders_to_ignore=[".git", ".github", ".vscode", "node_modules", "__pycache__", "gradle"], 
                 files_to_ignore=['.css', '.js'], progress_reporter: ProgressReporter=None):
        
        self.directory = directory
        self.folders_to_ignore = folders_to_ignore
        self.files_to_ignore = files_to_ignore
        self.progress_reporter = progress_reporter

    async def _read_file(self, filepath):
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as file:
                file_content = await file.read()
                if self.progress_reporter:
                    self.progress_reporter.update(PipelineSteps.READING_FILES, 1)
                return FileContent(filepath,filepath.name,self._get_file_type(filepath=filepath), file_content) 
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

            self.progress_reporter.init_step(PipelineSteps.READING_FILES, len(tasks))
            
            results = await asyncio.gather(*tasks)

            for fileContent in results:
                if fileContent.filetype is not None and fileContent.filetype is not None:
                    files_content[fileContent.filetype].append(fileContent)

        return files_content