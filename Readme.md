### README.md

# Application Overview

This application is designed to assist with various coding tasks using AI models. It can handle tasks such as refactoring code from AWS to Azure services, generating dependency graphs, and more. The application leverages asynchronous programming, multiple interacting components, and integration with external AI services.

## Features

- **Refactoring Code**: Suggest refactoring changes to a migrate a code from using AWS services to Azure services.
- **Dependency Graph Generation**: Generate a dependency graph of the app dependencies in GraphVIZ format.
- **Model Configuration**: Configure different AI models to be used by the application.
- **Asynchronous Processing**: Efficiently handle long-running I/O operations without blocking.


## Setup

### Prerequisites

- Python 3.7 or higher
- Virtual environment (optional but recommended)
- Required Python packages (listed in [`requirements.txt`]
- [Optional] Ollama installed https://ollama.com/
- Azure OpenAI Deployments named the following:
  - gpt4
  - gpt-4o
  - gpt-4o-mini

### Installation

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment** (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   - Ensure the `.env` file in the root directory contains the necessary environment variables for the models you are configuring.
   - Example:
     ```env
     MODELS_CONFIGURATION_PATH=./model_config.json
     ```

5. **Create a json file for e.g. `model_config.json` File**:
   - To configure different AI models, follow these steps:
      - Add entries in the `model_config.json` file to include the models you want to configure. Each entry should include the model name, version, endpoint, API key, platform, and retries.
      - Example:
      ```json
      [
         {
            "model_name": ["gpt4", "gpt-4o", "gpt-4o-mini"], => These are must
            "model_version": "<version>", => optional it depends on the platform. For Azure platform is a must.
            "model_endpoint": "<endpoint>", => A must
            "api_key": "<api_key>", => A must for Azure. 
            "platform": "azure", => A must.
            "retries": 4 => 
         },
         {
            "model_name": ["codellama"],
            "model_endpoint": "<endpoint>",
            "platform": "ollama",
            "retries": 2
         }
      ]



     ```

6. [Optional] **Local Models** 
 - The Application can work with a locally hosted models that are compliant with OpenAI API endpoints. The application is tested with ollama. Like we've used codellama for the expriementation. 
  - You can download ollama from here https://ollama.com/
  - Once it's ready, you would need to download the ollama model. 
  - Then host the model. You can achieve both steps in one command ```ollama run codellama```
  - Then you can use endpoint ```http://<ollama_host_name>:11434/v1``` for the OpenAI client.  

## Usage

1. **Run the Application**:
   ```sh
   python ask-openai.py
   ```

2. **Configure Questions**:
   - Modify the [`questions`] list in [`ask-openai.py`] to enable or disable specific questions and adjust their prompts as needed.

## Debugging and Troubleshooting

### Debugging

1. **Enable Debugging in VS Code**:
   - Open the project in Visual Studio Code.
   - Set breakpoints in the code where you want to inspect the execution.
   - Use the built-in debugger to step through the code.

### Troubleshooting

1. **Common Issues**:
   - **Missing Environment Variables**: Ensure all required environment variables are set in the [`.env`]file.
   - **Dependency Issues**: Ensure all dependencies are installed correctly using `pip install -r requirements.txt`.

2. **Error Handling**:
   - **API Errors**: Check the API key and endpoint URL. Ensure they are correct and have the necessary permissions.
   - **File I/O Errors**: Ensure the output directory exists and has the correct permissions.

3. **Asynchronous Issues**:
   - Ensure that all asynchronous functions are awaited properly.
   - Use `asyncio.run()` to run the main asynchronous function.

### Examples

The below is an example of running the expriement of migrating code in this repository ``` https://github.com/luckyPrice/online-e-commerce-marketplace-project-backend.git``` from AWS to Azure using the below prompt:
```
      Refactor the code in the context. Things to consider:
                    - Migrate the code where it uses AWS services to Azure services
                    - Respect the original functionality of the code
                    - Generate unit tests for the refactored code
                    - Don't make your own answer, limit the refactoring to the passed context
                    - Stick to the original file name adding the suffix "_refactored" to the file name
                    - Stick to the original file programming language
```

Which ended up refactoring some of the Java and .xml file, here is a sample of the one migrated Java files:
![alt text](./docs/image.png)

**Some of the observations:**
- The LLM did remove the injected secrets and structure that are AWS focused. Replaced them with more Azure focused. 
- The refactoring for configuration keys like "azure.storage.connection-string" these maybe one of the things that can we can ask LLM to don't migrate. 


## Conclusion

This application leverages AI models to assist with various coding tasks, making it a powerful tool for developers. By following the setup, debugging, and troubleshooting steps outlined in this README, you can effectively use and maintain the application.