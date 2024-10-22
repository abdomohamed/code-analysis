from abc import ABC
import time
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
from common_models import FileType

class Chunker(ABC):
    def __init__(self, max_chunk_size=2000):
        self.max_chunk_size = max_chunk_size

    def chunk_files(self, files_content):
        chunks = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        for file_type in files_content.keys():
            print(f"Going to chunk {file_type} {len(files_content[file_type])} files")

            start_time = time.time()
            
            current_chunk = ""

            for filename, content in  files_content[file_type]:                
                if len(current_chunk) + len(content) + len(filename) + len(file_type) + len("file_name,") + len("file_type,") + len("content") > self.max_chunk_size:
                    chunks[file_type].append(current_chunk)
                    current_chunk = ""
                current_chunk += f"### file_name:{filename}, file_type: {file_type}, content:\n{content}\n\n"

            if current_chunk:
                chunks[file_type].append(current_chunk)

            print(f"Chunked {len(files_content[file_type])} files into {len(chunks[file_type])} chunks in {time.time() - start_time:.2f} seconds")

        return chunks

class ChunkPerFile(Chunker):
    def __init__(self, max_chunk_size=2000):
        super().__init__(max_chunk_size)
    
    
    def chunk_files(self, files_content):
        chunks = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        for file_type in files_content.keys():
            print(f"Going to chunk {file_type} {len(files_content[file_type])} files")

            start_time = time.time()

            for filename, content in  files_content[file_type]:                
                chunks[file_type].append(f"### file_name:{filename}, file_type: {file_type}, content:\n{content}")

            print(f"Chunked {len(files_content[file_type])} files into {len(chunks[file_type])} chunks in {time.time() - start_time:.2f} seconds")

        return chunks