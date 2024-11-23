from typing import Optional
from .base import BaseLLM, LLMResponse

class OpenAILLM(BaseLLM):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import openai
        openai.api_key = self.api_key
        
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            raw_response=response
        )