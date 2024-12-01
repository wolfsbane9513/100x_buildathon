import os
import sys
import time
import signal
import logging
from pathlib import Path
from dotenv import load_dotenv
from report_generator.interface.app import ReportGeneratorInterface
from report_generator.core.ollama_handler import OllamaManager
from report_generator.core.tools.report_agent import ReportGenerationAgent
from report_generator.core.models.ollama_models import OllamaLLM
import asyncio
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def setup_logging():
    """Configure logging settings."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create handlers with formatting
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_dir / "app.log")
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )
    
    return logging.getLogger(__name__)

def check_environment():
    """Check required environment variables."""
    # Create temp and reports directories
    for dir_name in ['temp', 'reports', 'logs']:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
    
    # Check environment variables
    optional_vars = ['OPENAI_API_KEY']  # Made optional since we have local models
    missing = [var for var in optional_vars if not os.getenv(var)]
    if missing:
        logger.info(f"Optional environment variables not set: {missing}")
    return True

def initialize_ollama(max_retries=3):
    """Initialize Ollama with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to initialize Ollama (Attempt {attempt + 1}/{max_retries})")
            ollama_manager = OllamaManager()
            if ollama_manager.initialize():
                logger.info("Ollama initialized successfully")
                return ollama_manager
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:  # Don't sleep on last attempt
                time.sleep(2)
    return None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    logger.info("Initiating graceful shutdown...")
    sys.exit(0)

async def generate_report(agent, user_prompt, output_format, data):
    """Generate report using the agent and provided parameters."""
    try:
        report_path = await agent.generate_report(
            user_prompt=user_prompt,
            output_format=output_format,
            data=data
        )
        logger.info(f"Report generated at: {report_path}")
    except Exception as e:
        logger.error(f"Error generating report: {e}")

def main():
    """Main application entry point."""
    try:
        # Set up signal handling
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize directories and environment
        logger.info("Initializing application...")
        check_environment()
        
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")

        # Initialize Ollama
        ollama_manager = initialize_ollama()
        if not ollama_manager:
            logger.warning(
                "Ollama initialization incomplete. Only API models may be available."
            )
        else:
            logger.info("Ollama initialization completed successfully")
        
        # Create and launch Gradio interface
        logger.info("Creating interface...")
        interface = ReportGeneratorInterface(ollama_manager=ollama_manager)  # Pass OllamaManager instance
        
        logger.info("Starting Report Generator application...")
        try:
            interface.launch()
        except Exception as e:
            logger.error(f"Interface launch failed: {e}")
            return 1

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        return 0
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        return 1
    finally:
        logger.info("Application shutdown complete")
        return 0

if __name__ == "__main__":
    # Initialize logger
    logger = setup_logging()
    
    try:
        # Run the application
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
