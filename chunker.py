from abc import ABC
import time

from file_processor import FileContent
from progress_reporter import ProgressReporter
"""
A class used to chunk files into smaller pieces based on a maximum chunk size. A chunk can have a max of one file.
Any file that exceeds the maximum chunk size will be moved to a new chunk.

Attributes
----------
max_chunk_size : int
    The maximum size of each chunk. Default is 2000.
Methods
-------
chunk_files(files_content)
    Add files to chunks based on the maximum chunk size.
"""
from common_models import FileType, PipelineSteps

class Chunker(ABC):
    def __init__(self, max_chunk_size=2000, progress_reporter: ProgressReporter=None):
        self.max_chunk_size = max_chunk_size
        self.progress_reporter = progress_reporter

    def _chunk_files(self, _: dict[str, list[FileContent]]):
        pass
    
    def report_progress(self, files_content: dict[str, list[FileContent]]):
        if(self.progress_reporter):
            totals = 0
            for file_type in files_content.keys():
                totals += len(files_content[file_type])
            self.progress_reporter.init_step(PipelineSteps.CHUNKING, total_tasks=totals)    
            
    def chunk_files(self, files_content: dict[str, list[FileContent]]):
        self.report_progress(files_content)
        return self._chunk_files(files_content=files_content)


class MaxSizeChunker(Chunker):
    def __init__(self, max_chunk_size=2000, progress_reporter: ProgressReporter=None):
        self.max_chunk_size = max_chunk_size
        self.progress_reporter = progress_reporter

    def _chunk_files(self, files_content: dict[str, list[FileContent]]):
        chunks = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        for file_type in files_content.keys():
            print(f"Going to chunk {file_type} {len(files_content[file_type])} files")

            start_time = time.time()
            
            current_chunk = ""

            for file_content in  files_content[file_type]:
                if(self.progress_reporter):
                    self.progress_reporter.update(PipelineSteps.CHUNKING)
                                    
                if len(current_chunk) + len(file_content.content) + len(file_content.filename) + len(file_type) + len("file_name,") + len("file_type,") + len("content") > self.max_chunk_size:
                    chunks[file_type].append(current_chunk)
                    current_chunk = ""
                current_chunk += f"### source_file:{file_content.filepath} file_name:{file_content.filename}, file_type: {file_content.file_type}, content:\n{file_content.content}\n\n"

            if current_chunk:
                chunks[file_type].append(current_chunk)

            print(f"Chunked {len(files_content[file_type])} files into {len(chunks[file_type])} chunks in {time.time() - start_time:.2f} seconds")

        return chunks
    

class ChunkPerFile(Chunker):
    def __init__(self, max_chunk_size=2000, progress_reporter: ProgressReporter=None):
        super().__init__(max_chunk_size, progress_reporter=progress_reporter)
    
    
    def _chunk_files(self, files_content):
        chunks = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        for file_type in files_content.keys():
            print(f"Going to chunk {file_type} {len(files_content[file_type])} files")

            start_time = time.time()

            for file_content in  files_content[file_type]:
                if(self.progress_reporter):
                    self.progress_reporter.update(PipelineSteps.CHUNKING)
                
                chunks[file_type].append(f"### source_file:{file_content.filepath} file_name:{file_content.filepath}, file_type: {file_type}, content:\n{file_content.content}")

            print(f"Chunked {len(files_content[file_type])} files into {len(chunks[file_type])} chunks in {time.time() - start_time:.2f} seconds")

        return chunks