# run.py
import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from report_generator.app.config import Config
from report_generator.interface.app import ReportGeneratorInterface

def setup_logging():
    """Configure logging settings"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import gradio
        import llama_index
        import pandas
        import plotly
        logger.info("All core dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        return False

def check_directories():
    """Create necessary directories if they don't exist"""
    dirs = ['temp', 'reports', 'logs']
    for dir_name in dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")

def check_environment():
    """Check environment variables and model availability"""
    required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"Missing optional environment variables: {', '.join(missing_vars)}")
        logger.info("Local models will be used as fallback")

def verify_ollama():
    """Verify Ollama installation and model availability"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            logger.info("Ollama is running and accessible")
            return True
    except Exception as e:
        logger.warning(f"Ollama check failed: {str(e)}")
        logger.info("Please install Ollama for local model support: https://ollama.ai/")
    return False

async def main():
    """Main application entry point"""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")

        # Perform system checks
        if not check_dependencies():
            logger.error("Missing required dependencies. Please install all requirements.")
            sys.exit(1)

        # Create necessary directories
        check_directories()

        # Check environment and model availability
        check_environment()
        verify_ollama()

        # Initialize configuration
        Config.initialize()
        logger.info("Configuration initialized successfully")

        # Create and launch interface
        interface = ReportGeneratorInterface()
        app = interface.create_interface()
        
        logger.info("Starting Report Generator application...")
        # app.queue(concurrency_count=3)  # Allow multiple concurrent requests
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,  # Set to True to create a public link
            debug=True,
            auth=None,  # Add authentication if needed: auth=("username", "password")
            ssl_keyfile=None,  # Add SSL if needed
            ssl_certfile=None,
            max_threads=40
        )

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    # Initialize logger
    logger = setup_logging()
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shutdown requested")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        logger.info("Application shutdown complete")