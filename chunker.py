import time
from common_models import FileType

class Chunker:
    def __init__(self, max_chunk_size=2000):
        self.max_chunk_size = max_chunk_size

    def chunk_files(self, files_content):
        chunks = {FileType.CODE: [], FileType.TEXT: [], FileType.IMAGE: [], FileType.OTHER: []}
        
        for file_type in files_content.keys():
            print(f"Going to chunk {file_type} {len(files_content[file_type])} files")

            start_time = time.time()
            
            current_chunk = ""

            for filename, content in  files_content[file_type]:
                if len(current_chunk) + len(content) + len(filename) > self.max_chunk_size:
                    chunks[file_type].append(current_chunk)
                    current_chunk = ""
                current_chunk += f"### {filename}\n{content}\n\n"

            if current_chunk:
                chunks[file_type].append(current_chunk)

            print(f"Chunked {len(files_content[file_type])} files into {len(chunks[file_type])} chunks in {time.time() - start_time:.2f} seconds")

        return chunks