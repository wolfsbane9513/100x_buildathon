from typing import Dict, List, Type, Optional
from llama_index.llms.base import LLM
from .base import BaseLLM
from .ollama_models import OllamaLLM
from .openai_models import OpenAILLM
from .anthropic_models import AnthropicLLM
from report_generator.app.config import config

class ModelManager:
    def __init__(self):
        """Initialize the Model Manager with available models."""
        self.models: Dict[str, Dict[str, callable]] = {
            'local': {
                'llama2': lambda: OllamaLLM('llama2'),
                'mistral': lambda: OllamaLLM('mistral'),
                'codellama': lambda: OllamaLLM('codellama'),
                'mixtral': lambda: OllamaLLM('mixtral'),
            },
            'openai': {
                'gpt-3.5-turbo': lambda: OpenAILLM('gpt-3.5-turbo', config.OPENAI_API_KEY),
                'gpt-4': lambda: OpenAILLM('gpt-4', config.OPENAI_API_KEY),
            },
            'anthropic': {
                'claude-3-opus': lambda: AnthropicLLM('claude-3-opus', config.ANTHROPIC_API_KEY),
                'claude-3-sonnet': lambda: AnthropicLLM('claude-3-sonnet', config.ANTHROPIC_API_KEY),
            }
        }
        
        # Filter out unavailable API models
        if not config.OPENAI_API_KEY:
            self.models.pop('openai', None)
        if not config.ANTHROPIC_API_KEY:
            self.models.pop('anthropic', None)

    def get_available_providers(self) -> List[str]:
        """Get list of available model providers."""
        return list(self.models.keys())

    def get_available_models(self, provider: str) -> List[str]:
        """Get list of available models for a provider."""
        if provider not in self.models:
            raise ValueError(f"Unknown provider: {provider}")
        return list(self.models[provider].keys())

    def get_model(self, provider: str, model_name: str, api_key: Optional[str] = None) -> BaseLLM:
        """Get model instance."""
        if provider not in self.models:
            raise ValueError(f"Unknown provider: {provider}")
        
        if model_name not in self.models[provider]:
            raise ValueError(f"Unknown model: {model_name} for provider {provider}")
        
        # Create model instance
        model_instance = self.models[provider][model_name]()
        
        # Set API key if provided
        if api_key and hasattr(model_instance, 'set_api_key'):
            model_instance.set_api_key(api_key)
        
        return model_instance

    def verify_model_availability(self, provider: str, model_name: str) -> bool:
        """Verify if a specific model is available."""
        try:
            if provider == 'local':
                from report_generator.core.ollama_handler import OllamaHandler
                handler = OllamaHandler()
                return handler.ensure_model_pulled(model_name)
            elif provider == 'openai':
                return bool(config.OPENAI_API_KEY)
            elif provider == 'anthropic':
                return bool(config.ANTHROPIC_API_KEY)
            return False
        except Exception as e:
            print(f"Error verifying model availability: {str(e)}")
            return False

    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models grouped by provider."""
        available_models = {}
        for provider in self.get_available_providers():
            models = self.get_available_models(provider)
            available_models[provider] = [
                model for model in models
                if self.verify_model_availability(provider, model)
            ]
        return available_models

    def get_default_model(self) -> tuple:
        """Get default model provider and name."""
        # Prefer local models if available
        if 'local' in self.models and self.models['local']:
            return 'local', next(iter(self.models['local'].keys()))
        # Fall back to any available provider
        for provider in self.models:
            if self.models[provider]:
                return provider, next(iter(self.models[provider].keys()))
        raise ValueError("No models available")