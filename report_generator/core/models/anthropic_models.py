from typing import Optional
from .base import BaseLLM, LLMResponse

class AnthropicLLM(BaseLLM):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.api_key)
        response = await client.messages.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(
            content=response.content[0].text,
            raw_response=response
        )