from typing import Dict, List, Type, Optional, Any
from llama_index.llms.base import LLM
from .base import BaseLLM
from .ollama_models import OllamaLLM
from .openai_models import OpenAILLM
from report_generator.app.config import config
import subprocess
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self._available_models = None
        self._providers = {
            'local': {'name': 'Local Models (Ollama)', 'requires_key': False},
            'openai': {'name': 'OpenAI', 'requires_key': True}
        }

    def _lazy_load_models(self) -> None:
        if self._available_models is None:
            self._available_models = {
                'openai': {
                    'gpt-3.5-turbo': lambda: OpenAILLM('gpt-3.5-turbo', None),
                    'gpt-4': lambda: OpenAILLM('gpt-4', None),
                },
                'local': {
                    model: lambda model_name=model: OllamaLLM(model_name)
                    for model in self._get_available_local_models()
                }
            }

    def _get_available_local_models(self) -> List[str]:
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                return [line.split()[0] for line in result.stdout.strip().split('\n')[1:] if line.strip()]
            return []
        except Exception as e:
            logger.error(f"Error fetching local models: {str(e)}")
            return []

    def get_available_providers(self) -> List[str]:
        return ['local', 'openai']

    def get_available_models(self, provider: str) -> List[str]:
        self._lazy_load_models()
        return list(self._available_models.get(provider, {}).keys())

    def get_model(self, provider: str, model_name: str, api_key: Optional[str] = None) -> BaseLLM:
        self._lazy_load_models()
        model_factory = self._available_models.get(provider, {}).get(model_name)
        if not model_factory:
            raise ValueError(f"Model '{model_name}' not found for provider '{provider}'")
        return model_factory()


    def verify_model_availability(self, provider: str, model_name: str) -> bool:
        """Verify if a specific model is available."""
        try:
            if provider == 'local':
                result = subprocess.run(
                    ['ollama', 'show', model_name],
                    capture_output=True
                )
                return result.returncode == 0
            elif provider == 'openai':
                return bool(config.OPENAI_API_KEY)
            return False
        except Exception as e:
            self.logger.error(f"Error verifying model: {str(e)}")
            return False

    def get_default_model(self) -> tuple:
        """Get default model provider and name."""
        try:
            # Default to local models if available
            local_models = self._get_local_models()
            if local_models:
                return 'local', local_models[0]
            
            # Fall back to OpenAI if configured
            if config.OPENAI_API_KEY:
                return 'openai', 'gpt-3.5-turbo'
            
            # Return local as default even if no models
            return 'local', 'Select a model'
            
        except Exception as e:
            self.logger.error(f"Error getting default model: {str(e)}")
            return 'local', 'Select a model'

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a provider"""
        return self._providers.get(provider, {})