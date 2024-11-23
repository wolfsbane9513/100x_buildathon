# report_generator/app/config.py
from typing import List, Optional
from pathlib import Path
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

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
        self.TEMP_DIR = self.BASE_DIR / "temp"
        self.REPORTS_DIR = self.BASE_DIR / "reports"
    
    @classmethod
    def initialize(cls) -> None:
        """Create necessary directories"""
        instance = cls()
        instance.TEMP_DIR.mkdir(exist_ok=True)
        instance.REPORTS_DIR.mkdir(exist_ok=True)
        return instance

# Create and export config instance
config = Config()