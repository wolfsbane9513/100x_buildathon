import logging
from pathlib import Path
from app.config import Config

def setup_logger(name: str) -> logging.Logger:
    """Configure and return logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(
        Config.BASE_DIR / "logs" / f"{name}.log"
    )
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger