from typing import Optional, Dict, Any
from .base import BaseLLM, LLMResponse
import aiohttp
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize Ollama LLM."""
        self.model_name = model_name
        self.base_url = base_url
        self.metadata = {
            "model_name": model_name,
            "provider": "local",
            "base_url": base_url
        }
        self.context_window = 2048  # Default context window

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using Ollama API."""
        try:
            logger.info(f"Sending request to {self.base_url}/api/generate")
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                **kwargs
            }
            logger.info(f"Payload size: {len(str(prompt))} characters")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API returned status {response.status}: {error_text}")

                    # Initialize response text
                    full_response = ""
                    async for line in response.content:
                        try:
                            if line:
                                # Decode and parse each line
                                line_text = line.decode('utf-8').strip()
                                if line_text:
                                    try:
                                        json_response = json.loads(line_text)
                                        if 'response' in json_response:
                                            full_response += json_response['response']
                                    except json.JSONDecodeError as je:
                                        logger.warning(f"Failed to parse JSON line: {line_text}")
                                        continue
                        except Exception as e:
                            logger.warning(f"Error processing line: {str(e)}")
                            continue

                    logger.info("Successfully generated response")
                    return LLMResponse(
                        content=full_response,
                        raw_response={"full_response": full_response}
                    )

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error while calling Ollama API: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {str(e)}")
            raise Exception(f"Error parsing Ollama response: {str(e)}")
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
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

    async def _process_stream(self, response: aiohttp.ClientResponse) -> str:
        """Process streaming response from Ollama."""
        full_response = []
        try:
            async for line in response.content:
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text:
                        try:
                            json_response = json.loads(line_text)
                            if 'response' in json_response:
                                full_response.append(json_response['response'])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON: {line_text}")
                            continue
            return "".join(full_response)
        except Exception as e:
            logger.error(f"Error processing stream: {str(e)}")
            raise
