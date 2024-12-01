# report_generator/app/config.py
from typing import List, Optional
from pathlib import Path
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    # Base Paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    TEMP_DIR: Path = field(init=False)
    REPORTS_DIR: Path = field(init=False)
    
    # API Keys
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    
    # Model Settings
    DEFAULT_PROVIDER: str = "local"
    DEFAULT_MODEL: str = "mixtral"
    EMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    
    # Report Settings
    SUPPORTED_FORMATS: List[str] = field(
        default_factory=lambda: ["pdf", "docx", "html"]
    )
    DEFAULT_FORMAT: str = "pdf"
    
    def __post_init__(self) -> None:
        """Initialize paths after dataclass initialization"""
        # Initialize directory paths
        self.TEMP_DIR = self.BASE_DIR / "temp"
        self.REPORTS_DIR = self.BASE_DIR / "reports"
        # Ensure directories exist
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they do not exist"""
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.REPORTS_DIR.mkdir(exist_ok=True)
        logger.info(f"Temporary directory set to: {self.TEMP_DIR}")
        logger.info(f"Reports directory set to: {self.REPORTS_DIR}")

# Create and export config instance
config = Config()
