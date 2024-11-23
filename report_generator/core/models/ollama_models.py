from typing import Optional, Dict, Any
from .base import BaseLLM, LLMResponse
import aiohttp
import logging

logger = logging.getLogger(__name__)

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize Ollama LLM.
        
        Args:
            model_name: Name of the Ollama model
            base_url: Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Required attributes
        self.metadata = {
            "model_name": model_name,
            "provider": "local",
            "base_url": base_url
        }
        self.context_window = 2048  # Default context window for local models
        
        logger.info(f"Initialized OllamaLLM with model: {model_name}")

import httpx
import logging
import json
from .base import BaseLLM, LLMResponse

logger = logging.getLogger(__name__)

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.metadata = {
            "model_name": model_name,
            "provider": "local",
            "base_url": base_url
        }
        self.context_window = 2048  # Adjust as needed
        logger.info(f"Initialized OllamaLLM with model: {self.metadata}")

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/api/generate"
                payload = {"prompt": prompt, "model": self.model_name, **kwargs}
                logger.info(f"Sending request to {url} with payload: {payload}")
                logger.info(f"Payload size: {len(str(payload))} characters")

                response = await client.post(url, json=payload)

                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")
                logger.info(f"Response content: {response.text}")

                if response.status_code != 200:
                    raise httpx.RequestError(f"Request failed with status {response.status_code}")

                # Parse JSON response
                try:
                    content = response.json()
                    return LLMResponse(content=content.get("text", ""), raw_response=content)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decoding error: {e}")
                    raise
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            raise
        
    async def chat(self, messages: list, **kwargs) -> LLMResponse:
        """Chat with the model."""
        try:
            formatted_prompt = self._format_chat_messages(messages)
            return await self.generate(formatted_prompt, **kwargs)
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    def _format_chat_messages(self, messages: list) -> str:
        """Format chat messages for Ollama."""
        try:
            formatted = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                formatted.append(f"{role}: {content}")
            return "\n".join(formatted)
        except Exception as e:
            logger.error(f"Error formatting messages: {str(e)}")
            raise