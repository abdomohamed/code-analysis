import asyncio
from threading import Lock
import threading
from openai import AsyncAzureOpenAI
import os
import os

from chunker import ChunkPerFile, Chunker
from common_models import FileType, PipelineSteps, Question
from file_processor import FileProcessor
from model_config import ModelConfigParser
from openai_client_factory import OpenAIClientFactory
from output_persistor import OutputPersistor
from pipeline import Pipeline
from progress_reporter import ProgressReporter
from repository_copilot import RepositoryCoPilot
from dotenv import load_dotenv
from response_formats.code_refactoring import CodeRefactoringResponseFormat
from batch_code_saver import BatchCodeSaver
from code_saver import FileSaveStrategy


# Load environment variables from .env file
load_dotenv(".env")

async def main():
    # You can change this to any directory you want to analyze

    questions = [
        Question(text="What is the purpose of this repository?", enabled=False),
        Question(text="How can I set up the development environment?",
                 enabled=False),
        Question(
            text="Are there any known issues or limitations?", 
            enabled=False
        ),
        Question(
            text="Can you provide a summary of the main functionalities?", 
            enabled=False
        ),
        Question(
            text="What are the key dependencies of this project?",
            enabled=False
        ),
        Question(
            text="What are the cloud services used in this project?", 
            enabled=False,
            models=["gpt-4o", "gpt-4o-mini"]
        ),
        Question(
            text="Provide a brief overview of the architecture of this project?", 
            enabled=False
        ),
        Question(
            text="What are the main features of this project?", 
            enabled=False
        ),
        Question(
            text="What is the complexity of this application?", 
            system_prompt="""
                 You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user.
                 
                 Application Complexity can be categorized into three levels:
                  - Low Complexity: Typically involves simple scripts or applications with straightforward logic and minimal external dependencies.
                  - Medium Complexity: Involves asynchronous programming, multiple interacting components, and integration with external services, but does not require extensive real-time processing or highly complex algorithms.
                  - High Complexity: Involves real-time processing, highly complex algorithms, extensive use of concurrency, and/or large-scale distributed systems.
                  
                  Answer the question in the following format:
                   - The complexity is: "<Low|Medium|High>"
                 """, 
            enabled=False,
            models=["codellama"]
        ),
        Question(
            text="""Refactor the code in the context. Things to consider:
                    - Migrate the code from AWS services to Azure services
                    - Respect the original functionality of the code
                    - Generate unit tests for the refactored code
                    - Add azure documentation references for the refactored Azure services
                    - Don't make your own answer, limit the refactoring to the passed context
                    - Stick to the original file name
                    - Stick to the original file programming language
                    """, 
            enabled=False,
            system_prompt="""You are a knowledgeable code assistant. Use the provided context to answer user questions with detailed explanations. Assist in migrating source files within the given context only. Generate unit tests for the refactored code before and after changes to validate. Read the context before responding and think step-by-step. If the context is insufficient to answer a question, inform the user and avoid using outside information. Do not provide your own answers.""", 
            models=[ "gpt-4o"], 
            allowed_file_types=[FileType.CODE],
            structured_output=True,
            response_format=CodeRefactoringResponseFormat
        ),
        Question(
            text="""Refactor the code in the context. Things to consider:
                    - Migrate the code where it uses PCF cloud foundary services connectors to Azure services
                    - Respect the original functionality of the code
                    - Generate unit tests for the refactored code
                    - Don't make your own answer, limit the refactoring to the passed context
                    - Stick to the original file name
                    - Stick to the original file programming language
                    """, 
            enabled=False,
            system_prompt="""You are a helpful code assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user""", 
            models=[ "gpt-4o"], 
            allowed_file_types=[FileType.CODE, FileType.TEXT],
            structured_output=True,
            response_format=CodeRefactoringResponseFormat
        ),
        Question(
            text="Generate a dependency graph of the app dependencies using GraphVIZ format",
            enabled=False,
            system_prompt="You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations. You will help in migrating source files in the context. Make sure to limit the refactoring to the passed context don't make your own answer. You must generate unit tests for the refactored code before and after the refactoring to validate the change. Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user.",
            models=["gpt-4o-mini", "gpt-4o", "gpt4", "codellama"],
            allowed_file_types=[FileType.CODE, FileType.TEXT]
        ),
                Question(
            text="""Update Imports based on the following instructions:
                    - Stick to the original file programming language: The language used in the original file must remain unchanged.
                    - Locate and replace AWS SDK imports: Locate all AWS SDK imports in your Java files.
                    You must met the following creteria:
                        - AWS imports have been replaced by Azure equivalent.
                        - No linting or unnecessary refactoring: Do not lint the files or perform any refactoring unless it is absolutely necessary for the import replacement.
                        - Do not remove or modify any comments or documentation in the code.
                        - Do not change or remove any annotations in the code.
                        - No other modifications: Focus only on replacing the AWS SDK imports with the corresponding Azure SDK imports. Do not make any other changes to the code.
                    """,
            enabled=True,
            system_prompt="""You are a helpful code assistant, you have good knowledge in coding and you will use the provided context to answer user questions""",
            models=[ "gpt-4o"], 
            allowed_file_types=[FileType.CODE],
            structured_output=True,
            response_format=CodeRefactoringResponseFormat
        ),
                        Question(
            text="""Change API Calls for the aws sdks based on the following instructions:
                    - Locate code sections where AWS service APIs are used.
                    - Replace AWS-specific API calls with Azure-specific API calls.
                    - No linting or unnecessary refactoring: Do not lint the files or perform any refactoring unless it is absolutely necessary for the import replacement.
                    - Ignore comments and documentations: Do not remove or modify any comments or documentation in the code.
                    - Ignore annotations: Do not change or remove any annotations in the code.
                    - No other modifications: Focus only on Changing API Calls with the corresponding Azure API Calls. Do not make any other changes to the code.
                """,
            enabled=True,
            system_prompt="""You are a helpful code assistant, you have good knowledge in coding and you will use the provided context to answer user questions""",
            models=[ "gpt-4o"], 
            allowed_file_types=[FileType.CODE],
            structured_output=True,
            response_format=CodeRefactoringResponseFormat
        ),
                        Question(
            text="""Rename Variables and Methods based on the following instructions:
                    - Locate variables and methods with AWS-specific names.
                    - Rename variables and methods to use Azure-specific names.
                    - Only change names that are related to the context provided.
                    - Apply the changes consistently throughout the code.
                    - Use meaningful names for variables and methods to improve code readability.
                    - For example, change awsS3Client to azureBlobClient.
                    - No linting or unnecessary refactoring: Do not lint the files or perform any refactoring unless it is absolutely necessary for the import replacement.
                    - Ignore comments and documentations: Do not remove or modify any comments or documentation in the code.
                    - Ignore annotations: Do not change or remove any annotations in the code.
                    - No other modifications: Focus only on renaming Variables and Methods. Do not make any other changes to the code.
                """ ,
            enabled=False,
            system_prompt="""You are a helpful code assistant, you have good knowledge in coding and you will use the provided context to answer user questions""",
            models=[ "gpt-4o"], 
            allowed_file_types=[FileType.CODE, FileType.TEXT],
            structured_output=True,
            response_format=CodeRefactoringResponseFormat
        ),
    ]

    directory = "./repos/mmf-java-consume-cost-change"
    lock = Lock()
    
    stop_event = threading.Event()
    
    progress_reporter = ProgressReporter(lock=lock, steps=[
        PipelineSteps.READING_FILES,
        PipelineSteps.CHUNKING,
        PipelineSteps.ANSWERING_QUESTIONS,
        PipelineSteps.REFINING_ANSWERS,
        PipelineSteps.GENERATING_OUTPUT
    ], stop_event=stop_event)

    progress_reporter_thread = threading.Thread(target=progress_reporter.report, daemon=True)
    progress_reporter_thread.start()
    
    fileProcessor = FileProcessor(directory=directory, progress_reporter=progress_reporter)
    openAIClientFactory = OpenAIClientFactory(model_config_parser=ModelConfigParser())
    repoCoPilot = RepositoryCoPilot(openai_client_factory=openAIClientFactory, progress_reporter=progress_reporter)
    chunker = ChunkPerFile(progress_reporter=progress_reporter)
    outputPersistor = OutputPersistor()
    batchCodeSaver = BatchCodeSaver(save_strategy=FileSaveStrategy())

    pipeline = Pipeline(questions, fileProcessor,
                        repoCoPilot, chunker, outputPersistor, batchCodeSaver)
    
    await pipeline.run()
    
    stop_event.set()

if __name__ == "__main__":
    asyncio.run(main())
