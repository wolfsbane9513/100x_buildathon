from typing import Optional, Dict, Any
import aiohttp
from .base import BaseLLM, LLMResponse

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    **kwargs
                }
            ) as response:
                result = await response.json()
                return LLMResponse(
                    content=result['response'],
                    raw_response=result
                )
    
    async def chat(self, messages: list, **kwargs) -> LLMResponse:
        formatted_prompt = self._format_chat_messages(messages)
        return await self.generate(formatted_prompt, **kwargs)
    
    def _format_chat_messages(self, messages: list) -> str:
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)