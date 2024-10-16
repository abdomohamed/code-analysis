import asyncio
from enum import Enum
from typing import Callable, Union
from openai import AsyncAzureOpenAI, AsyncOpenAI
from chunker import Chunker
from model_config import ModelConfig, ModelConfigParser, Platform


class OpenAIClientFactory:
    def __init__(self, model_config_parser: ModelConfigParser, model_key_strategy : Callable[[ModelConfig], str]=  None):
        self._model_config_parser = model_config_parser
        self._model_configs = None
        self._lock = asyncio.Lock()
        self._clients = {}
        self._model_key_strategy = model_key_strategy if model_key_strategy else self._default_model_key_strategy
        
    
    def _default_model_key_strategy(self, model_config: ModelConfig) -> str:
        return f"{model_config.platform.value}_{model_config.endpoint}_{model_config.version}"
    
    async def get_client(self, model_name: str) -> Union[AsyncOpenAI, AsyncAzureOpenAI]:
        if self._model_configs is None: 
            async with self._lock:
                if self._model_configs is None:
                    self._model_configs = await self._model_config_parser.parse()
        
        model_config = self._model_configs.get(model_name)
        
        if not model_config:
            raise ValueError(f"No configuration found for model: {model_name}")
        
        key = self._model_key_strategy(model_config)

        if key in self._clients:
            return self._clients[key]
        
        client: Union[AsyncOpenAI, AsyncAzureOpenAI] = None
        
        if (model_config.platform == Platform.AZURE):
            client = AsyncAzureOpenAI(
                    azure_endpoint=model_config.endpoint,
                    api_key=model_config.api_key,
                    api_version=model_config.version,
                    max_retries=model_config.retries,
            )
        elif (model_config.platform == Platform.OLLAMA):
            client = AsyncOpenAI(
                 base_url=model_config.endpoint,
                 api_key=model_name,
                 max_retries=model_config.retries,
            )
        elif (model_config.platform == Platform.OPENAI):
            client = AsyncOpenAI(
                 base_url=model_config.endpoint,
                 api_key=model_config.api_key,
                 max_retries=model_config.retries,
            )
        else: 
            raise ValueError(f"Unsupported platform: {model_config.platform}")
        
        async with self._lock:
            self._clients[key] = client
        
        return client
        
        