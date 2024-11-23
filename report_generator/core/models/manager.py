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
        """Initialize the Model Manager with available models."""
        self._available_models = None  # Lazy loading
        self._providers = {
            'local': {
                'name': 'Local Models (Ollama)',
                'requires_key': False
            },
            'openai': {
                'name': 'OpenAI',
                'requires_key': True
            }
        }
        self.logger = logging.getLogger(__name__)

    def _lazy_load_models(self) -> None:
        """Load models only when needed."""
        if self._available_models is None:
            self._available_models = {}
            
            # Load OpenAI models
            if config.OPENAI_API_KEY:
                self._available_models['openai'] = {
                    'gpt-3.5-turbo': lambda: OpenAILLM('gpt-3.5-turbo', config.OPENAI_API_KEY),
                    'gpt-4': lambda: OpenAILLM('gpt-4', config.OPENAI_API_KEY),
                }
            else:
                self._available_models['openai'] = {
                    'gpt-3.5-turbo': lambda: OpenAILLM('gpt-3.5-turbo', None),
                    'gpt-4': lambda: OpenAILLM('gpt-4', None),
                }

            # Load local Ollama models
            self._available_models['local'] = {}
            models = self._get_available_local_models()
            for model in models:
                self._available_models['local'][model] = lambda: OllamaLLM(model)

    def _get_available_local_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'], capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                return [line.split()[0] for line in lines if line.strip()]
            return []
        except Exception as e:
            self.logger.error(f"Error checking local Ollama models: {str(e)}")
            return []


    def get_available_providers(self) -> List[str]:
        """Get list of available model providers."""
        providers = ['local']  # Local is always available
        
        if config.OPENAI_API_KEY:
            providers.append('openai')
            
        return providers

    def get_available_models(self, provider: str) -> List[str]:
        """Get list of available models for a provider."""
        self._lazy_load_models()
        models = list(self._available_models.get(provider, {}).keys())
        logger.info(f"Available models for provider '{provider}': {models}")  # Debugging
        return models


    def _get_local_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            # Check if models are available locally first
            available_models = self._get_available_local_models()
            if available_models:
                return available_models

            # If not available locally, fallback to running 'ollama list'
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    parts = line.split()
                    if parts:  # Check if line has content
                        models.append(parts[0])  # Model name is first column
                return models
            return []
            
        except Exception as e:
            self.logger.error(f"Error checking Ollama models: {str(e)}")
            return []


    def get_model(self, provider: str, model_name: str, api_key: Optional[str] = None) -> BaseLLM:
        """Get model instance."""
        try:
            if provider == 'local':
                # Check if model is available locally first
                if self.verify_model_availability(provider, model_name):
                    return OllamaLLM(model_name)
                else:
                    # If not available locally, attempt to pull the model
                    if self.ensure_model_pulled(model_name):
                        return OllamaLLM(model_name)
                    else:
                        raise ValueError(f"Model '{model_name}' is not available")
            
            if provider == 'openai':
                key = api_key or config.OPENAI_API_KEY
                if not key:
                    raise ValueError("OpenAI API key required")
                return OpenAILLM(model_name, key)
            
            raise ValueError(f"Unknown provider: {provider}")
            
        except Exception as e:
            self.logger.error(f"Error getting model: {str(e)}")
            raise

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