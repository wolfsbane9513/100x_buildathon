from typing import Optional
from .base import BaseLLM, LLMResponse
import openai

class OpenAILLM(BaseLLM):
    def __init__(self, model_name: str, api_key: Optional[str]):
        """Initialize OpenAILLM with model name and API key."""
        self.model_name = model_name
        self.api_key = api_key
        self.metadata = {"model_name": model_name, "provider": "openai"}
        self.context_window = 4096 if "gpt-4" in model_name else 2048

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using OpenAI's ChatCompletion API."""
        openai.api_key = self.api_key
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(content=response["choices"][0]["message"]["content"], raw_response=response)

    async def chat(self, messages: list, **kwargs) -> LLMResponse:
        """
        Chat with the model using a sequence of messages.
        
        Args:
            messages (list): A list of dictionaries containing the chat history, 
                             e.g., [{"role": "system", "content": "You are a helpful assistant."}, ...]
                             
        Returns:
            LLMResponse: The response from the OpenAI API.
        """
        openai.api_key = self.api_key
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=messages,
            **kwargs
        )
        return LLMResponse(content=response["choices"][0]["message"]["content"], raw_response=response)
