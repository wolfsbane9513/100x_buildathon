from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    raw_response: Dict[str, Any]

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> LLMResponse:
        """Chat with the model"""
        pass