from typing import Dict, Type, Optional
from .base import BaseLLM
from .ollama_models import OllamaLLM
from .openai_models import OpenAILLM
from .anthropic_models import AnthropicLLM
from report_generator.app.config import config  # Updated import

class ModelManager:
    def get_model(self, provider: str, model_name: str, api_key: Optional[str] = None):
        if provider == 'local':
            return self._get_local_model(model_name)
        elif provider == 'openai':
            if not api_key:
                raise ValueError("OpenAI API key is required")
            return self._get_openai_model(model_name, api_key)
        elif provider == 'anthropic':
            if not api_key:
                raise ValueError("Anthropic API key is required")
            return self._get_anthropic_model(model_name, api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
