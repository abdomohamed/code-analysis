import asyncio
from openai import AsyncAzureOpenAI
import os
import os

from chunker import Chunker
from common_models import FileType, Question
from file_processor import FileProcessor
from output_persistor import OutputPersistor
from pipeline import Pipeline
from repository_copilot import RepositoryCoPilot
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Initialize Azure OpenAI client with key-based authentication
client = AsyncAzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-05-01-preview",
    max_retries=4,
)

async def main():
    # You can change this to any directory you want to analyze
    
    questions = [
        Question(text="What is the purpose of this repository?", enabled=False),
        Question(text="How can I set up the development environment?", enabled=False),
        Question(text="Are there any known issues or limitations?", enabled=False),
        Question(text="Can you provide a summary of the main functionalities?", enabled=False),
        Question(text="What are the key dependencies of this project?", enabled=False),
        Question(text="What are the cloud services used in this project?",enabled=False),
        Question(text="Provide a brief overview of the architecture of this project?", enabled=False),
        Question(text="What are the main features of this project?", enabled=False),
        Question(text="What is the complexity of this application?", system_prompt="""
                 You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user.
                 
                 Application Complexity can be categorized into three levels:
                  - Low Complexity: Typically involves simple scripts or applications with straightforward logic and minimal external dependencies.
                  - Medium Complexity: Involves asynchronous programming, multiple interacting components, and integration with external services, but does not require extensive real-time processing or highly complex algorithms.
                  - High Complexity: Involves real-time processing, highly complex algorithms, extensive use of concurrency, and/or large-scale distributed systems.
                 """, enabled=False),
        Question(text="Refer to the code snippet where it uses AWS services to the same services in Azure. Apply the refactoring changes to a new file, use the same old file name. List down the differences in the code. Make sure to include the file name and line number.", enabled=False,
                 system_prompt= """You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user"""
                 ,models=["gpt-4o-mini", "gpt-4o", "gpt4"], allowed_file_types=[FileType.CODE]),
        Question(text="Generate a dependency graph of the app dependencies using GraphVIZ format", enabled=True,
                 system_prompt="You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user.",
                 models=["gpt-4o-mini", "gpt-4o", "gpt4"], allowed_file_types=[FileType.CODE, FileType.TEXT]),
    ]

    directory = "./repos/aws-java-sample"
    
    fileProcessor = FileProcessor(directory)
    repoCoPilot = RepositoryCoPilot(client=client)
    chunker = Chunker()
    outputPersistor = OutputPersistor()
    
    pipeline = Pipeline(questions,fileProcessor, repoCoPilot, chunker, outputPersistor)
    await pipeline.run()

if __name__ == "__main__":
    asyncio.run(main())
