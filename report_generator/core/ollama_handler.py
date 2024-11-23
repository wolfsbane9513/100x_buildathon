import requests
import subprocess
import time
import platform
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaHandler:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.status_endpoint = f"{self.base_url}/api/tags"
        self.is_windows = platform.system() == "Windows"

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
        """Ensure the specified model is pulled."""
        try:
            response = requests.get(f"{self.base_url}/api/show", 
                                  params={"name": model_name},
                                  timeout=5)
            if response.status_code != 200:
                logger.info(f"Pulling model {model_name}...")
                result = subprocess.run(["ollama", "pull", model_name], 
                                      capture_output=True, 
                                      text=True)
                return result.returncode == 0
            return True
        except Exception as e:
            logger.error(f"Error checking/pulling model: {str(e)}")
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
        
        # Check and pull required models
        required_models = ["llama3", "mistral", "llama3.2-vision"]
        for model in required_models:
            if not self.handler.ensure_model_pulled(model):
                logger.warning(f"Failed to pull model: {model}")
        
        return True
