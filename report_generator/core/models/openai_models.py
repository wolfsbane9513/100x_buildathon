from typing import Optional
from .base import BaseLLM, LLMResponse
import openai

class OpenAILLM(BaseLLM):
    def __init__(self, model_name: str, api_key: Optional[str]):
        self.model_name = model_name
        self.api_key = api_key
        self.metadata = {"model_name": model_name, "provider": "openai"}
        self.context_window = 4096 if "gpt-4" in model_name else 2048

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        openai.api_key = self.api_key
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(content=response.choices[0].message.content, raw_response=response)
