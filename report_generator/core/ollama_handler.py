import requests
import subprocess
import time
import platform
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class OllamaHandler:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.status_endpoint = f"{self.base_url}/api/tags"
        self.is_windows = platform.system() == "Windows"

    def _get_available_local_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'], capture_output=True, text=True, encoding="utf-8"
            )
            print("Raw Output from `ollama list`:", result.stdout)  # Debugging
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = [line.split()[0] for line in lines if line.strip()]
                print("Parsed Models:", models)  # Debugging
                return models
            return []
        except Exception as e:
            logger.error(f"Error checking local Ollama models: {str(e)}")
            return []


    def check_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(self.status_endpoint, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_ollama(self) -> bool:
        """Start Ollama server if not running."""
        if self.is_windows:
            logger.info("On Windows: Please start Ollama manually using the Windows application")
            return False
        
        try:
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            # Wait for server to start
            for _ in range(5):  # 5 attempts
                time.sleep(2)
                if self.check_ollama_running():
                    logger.info("Ollama server started successfully")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to start Ollama: {str(e)}")
            return False

    def ensure_model_pulled(self, model_name: str) -> bool:
        """Ensure the specified model is pulled and available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/show", params={"name": model_name}, timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Model {model_name} is already available locally.")
                return True

            logger.info(f"Pulling model {model_name}...")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                encoding="utf-8"  # Force UTF-8 encoding
            )
            if result.returncode == 0:
                logger.info(f"Model {model_name} pulled successfully.")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}. Output: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error ensuring model is pulled: {str(e)}")
            return False




    def get_ollama_instructions(self) -> str:
        """Get platform-specific Ollama installation instructions."""
        if self.is_windows:
            return """
            To use Ollama on Windows:
            1. Download Ollama from https://ollama.ai/download
            2. Install the Windows application
            3. Run Ollama from the Start menu
            4. Wait for the Ollama icon to appear in the system tray
            """
        else:
            return """
            To install Ollama on Linux/Mac:
            1. Run: curl https://ollama.ai/install.sh | sh
            2. The server will start automatically
            """

class OllamaManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.handler = OllamaHandler()
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize Ollama and required models."""
        if not self.handler.check_ollama_running():
            if self.handler.is_windows:
                logger.warning("Ollama is not running. Please start Ollama manually on Windows.")
                print(self.handler.get_ollama_instructions())
                return False
            else:
                if not self.handler.start_ollama():
                    logger.error("Failed to start Ollama server")
                    return False

        # Cache available models
        available_models = self.handler._get_available_local_models()

        # Check and pull required models only if not already available
        required_models = ['llama2:latest', 'llama3:latest', 'mistral:latest', 'llama3.2-vision:latest', 'llama3.2:latest', 'llava-llama3:latest', 'llava:latest', 'llava:7b']
        for model in required_models:
            if model not in available_models:
                if not self.handler.ensure_model_pulled(model):
                    logger.warning(f"Failed to pull model: {model}")

        return True
