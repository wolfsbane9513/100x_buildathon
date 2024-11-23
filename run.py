import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from report_generator.interface.app import ReportGeneratorInterface
from report_generator.core.ollama_handler import OllamaManager

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )
    return logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded.")

        # Initialize Ollama
        ollama_manager = OllamaManager()
        if not ollama_manager.initialize():
            logger.warning(
                "Ollama initialization incomplete. Some models may not be available."
            )

        # Create and launch interface
        interface = ReportGeneratorInterface()
        logger.info("Starting Report Generator application...")
        interface.launch()

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    finally:
        logger.info("Application shutdown complete.")

if __name__ == "__main__":
    # Initialize logger
    logger = setup_logging()

    # Run the application
    main()
