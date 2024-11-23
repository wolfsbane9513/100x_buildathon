from typing import Dict, Any, Union
import pandas as pd
from pathlib import Path
from app.config import Config

class DataProcessor:
    @classmethod
    def process_file(cls, file_path: Union[str, Path]) -> pd.DataFrame:
        """Process input file and return DataFrame"""
        file_path = Path(file_path)
        if file_path.suffix not in Config.SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        if file_path.suffix == '.csv':
            return cls.read_csv(file_path)
        elif file_path.suffix == '.json':
            return cls.read_json(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            return cls.read_excel(file_path)
    
    @staticmethod
    def read_csv(file_path: Path) -> pd.DataFrame:
        return pd.read_csv(file_path)
    
    @staticmethod
    def read_json(file_path: Path) -> pd.DataFrame:
        return pd.read_json(file_path)
    
    @staticmethod
    def read_excel(file_path: Path) -> pd.DataFrame:
        return pd.read_excel(file_path)
