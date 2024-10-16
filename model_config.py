import asyncio
from enum import StrEnum
import os
import json
from typing import Optional, Self
import aiofiles
from dotenv import load_dotenv
from pydantic import BaseModel,  model_validator
from pydantic_core import PydanticUndefined


class Platform(StrEnum):
    AZURE = "azure"
    OPENAI = "openai"
    OLLAMA = "ollama"    
    
# Load environment variables from .env file
load_dotenv('/workspaces/code-analysis/.env')

class ModelConfig(BaseModel):
    """
    ModelConfig represents the configuration for a machine learning model.
    Attributes:
        name (str): The name of the model/depolyment.
        endpoint (str): The endpoint URL where the model is hosted.
        platform (Platform): The platform on which the model is deployed (e.g., Azure, AWS).
        version (Optional[str]): The version of the model. Required for Azure models.
        api_key (Optional[str]): The API key for accessing the model. Required for Azure models.
    Methods:
        required_if() -> Self:
            Validates that the `api_key` and `version` fields are provided when the platform is Azure.
            Raises:
                ValueError: If `api_key` or `version` is not provided for Azure models.
        __repr__() -> str:
            Returns a string representation of the ModelConfig instance.
    """
    name: str
    endpoint: str
    platform: Platform
    version: Optional[str]
    api_key: Optional[str]
    retries: Optional[int] = 0
    
    @model_validator(mode="after")
    def required_if(self) -> Self:
        if self.platform == Platform.AZURE and not self.api_key or self.api_key == PydanticUndefined or self.api_key == '':
            raise ValueError('API key is required for Azure models')
                
        if self.platform == Platform.AZURE and not self.version or self.version == PydanticUndefined or self.version == '':
            raise ValueError('Model version is required for Azure models')
        
        return self

    def __repr__(self):
        return f"ModelConfig(name={self.name}, version={self.version}, endpoint={self.endpoint}, api_key={self.api_key}, platform={self.platform.value}, retries={self.retries})"   

class ModelConfigParser:
    
    def __init__(self, models_configuration_path: str = None):
        self._models_configuration_path = models_configuration_path if models_configuration_path else os.getenv('MODELS_CONFIGURATION_PATH')
                
    async def _read_file(self, filepath):
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as file:
                return await file.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return filepath.name

    async def parse(self) -> dict[str, ModelConfig]:
        models_configuration_json = await self._read_file(self._models_configuration_path)
        models_configuration = json.loads(models_configuration_json)
        model_configs = {}
        for model in models_configuration:
            for name in model.get("model_name"):
                version = model.get('model_version')
                endpoint = model.get('model_endpoint')
                api_key = model.get('api_key')
                platform = model.get('platform')
                retries = model.get('retries', 0)
                model_configs[name] = ModelConfig(name=name, version=version, endpoint=endpoint, api_key=api_key, platform=platform, retries=retries)
        return model_configs

# Example usage
async def main():
    model_config_reader = ModelConfigParser()
    model_configs = await model_config_reader.parse()
    for k,v in model_configs.items():
        print(k, v, "\n")
        
if __name__ == "__main__":
    asyncio.run(main())