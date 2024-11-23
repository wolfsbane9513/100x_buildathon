from pathlib import Path
import asyncio
from interface.app import ReportGeneratorInterface
from app.config import Config
from utils.logger import setup_logger

async def main():
    # Initialize configuration
    Config.initialize()
    
    # Setup logging
    logger = setup_logger("report_generator")
    logger.info("Starting Report Generator application")
    
    # Create and launch interface
    interface = ReportGeneratorInterface()
    app = interface.create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    asyncio.run(main())