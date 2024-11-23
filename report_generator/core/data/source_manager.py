from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import asyncio
import json
import aiofiles
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from .connection_manager import ConnectionManager, DatabaseError

logger = logging.getLogger(__name__)

class DataProcessError(Exception):
    """Custom exception for data processing errors"""
    pass

class DataSourceManager:
    def __init__(self, connection_manager: Optional[ConnectionManager] = None):
        """Initialize DataSourceManager
        
        Args:
            connection_manager: Optional ConnectionManager instance. If not provided,
                              a new instance will be created.
        """
        self.connection_manager = connection_manager or ConnectionManager()
        self.data_cache: Dict[str, Any] = {}
        self._setup_logging()
        
        # Supported file types and their processors
        self.supported_file_types = {
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.json': self._process_json,
            '.txt': self._process_text,
            '.log': self._process_text
        }
        
        # Data analysis functions
        self.analysis_functions = {
            'numerical': self._analyze_numerical,
            'categorical': self._analyze_categorical,
            'temporal': self._analyze_temporal
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('data_processing.log')
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(log_format)
        file_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    async def process_file(self, file_path: Union[str, Path], file_type: Optional[str] = None) -> pd.DataFrame:
        """Process a file and return DataFrame
        
        Args:
            file_path: Path to the file
            file_type: Optional file type override
            
        Returns:
            pandas.DataFrame: Processed data
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise DataProcessError(f"File not found: {file_path}")
            
            if file_type is None:
                file_type = file_path.suffix.lower()
            
            if file_type not in self.supported_file_types:
                raise DataProcessError(f"Unsupported file type: {file_type}")
            
            processor = self.supported_file_types[file_type]
            df = await processor(file_path)
            
            # Cache the processed data
            cache_key = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.data_cache[cache_key] = {
                'data': df,
                'metadata': {
                    'filename': file_path.name,
                    'type': file_type,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'processed_at': datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"Successfully processed file: {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise DataProcessError(f"File processing failed: {str(e)}")

    async def _process_csv(self, file_path: Path) -> pd.DataFrame:
        """Process CSV file"""
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            return pd.read_csv(pd.StringIO(content))
        except Exception as e:
            raise DataProcessError(f"CSV processing error: {str(e)}")

    async def _process_excel(self, file_path: Path) -> pd.DataFrame:
        """Process Excel file"""
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            raise DataProcessError(f"Excel processing error: {str(e)}")

    async def _process_json(self, file_path: Path) -> pd.DataFrame:
        """Process JSON file"""
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            return pd.read_json(content)
        except Exception as e:
            raise DataProcessError(f"JSON processing error: {str(e)}")

    async def _process_text(self, file_path: Path) -> pd.DataFrame:
        """Process text/log file"""
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                lines = await f.readlines()
            return pd.DataFrame(lines, columns=['content'])
        except Exception as e:
            raise DataProcessError(f"Text processing error: {str(e)}")

    async def analyze_data(self, data: Union[pd.DataFrame, str], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze data and generate insights
        
        Args:
            data: DataFrame or cache key
            context: Optional analysis context
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Get DataFrame from cache if string provided
            if isinstance(data, str):
                if data not in self.data_cache:
                    raise DataProcessError(f"Data not found in cache: {data}")
                df = self.data_cache[data]['data']
            else:
                df = data

            analysis = {
                'basic_stats': {
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                },
                'columns': {},
                'missing_values': df.isnull().sum().to_dict(),
                'correlations': None
            }

            # Analyze each column
            for column in df.columns:
                col_type = self._detect_column_type(df[column])
                if col_type in self.analysis_functions:
                    analysis['columns'][column] = self.analysis_functions[col_type](df[column])

            # Calculate correlations for numerical columns
            numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numerical_cols) > 1:
                analysis['correlations'] = df[numerical_cols].corr().to_dict()

            self.logger.info("Data analysis completed successfully")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing data: {str(e)}")
            raise DataProcessError(f"Data analysis failed: {str(e)}")

    def _detect_column_type(self, series: pd.Series) -> str:
        """Detect the type of data in a column"""
        if pd.api.types.is_numeric_dtype(series):
            return 'numerical'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'temporal'
        else:
            return 'categorical'

    def _analyze_numerical(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze numerical data"""
        return {
            'type': 'numerical',
            'min': series.min(),
            'max': series.max(),
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'quartiles': series.quantile([0.25, 0.5, 0.75]).to_dict()
        }

    def _analyze_categorical(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze categorical data"""
        value_counts = series.value_counts()
        return {
            'type': 'categorical',
            'unique_values': series.nunique(),
            'most_common': value_counts.index[0] if not value_counts.empty else None,
            'most_common_count': value_counts.iloc[0] if not value_counts.empty else 0,
            'value_distribution': value_counts.head(10).to_dict()
        }

    def _analyze_temporal(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze temporal data"""
        return {
            'type': 'temporal',
            'min_date': series.min(),
            'max_date': series.max(),
            'date_range': (series.max() - series.min()).days,
            'missing_dates': series.isnull().sum()
        }

    async def create_visualization(
        self,
        data: Union[pd.DataFrame, str],
        viz_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create visualization
        
        Args:
            data: DataFrame or cache key
            viz_type: Type of visualization
            config: Visualization configuration
            
        Returns:
            Dict containing visualization figure and metadata
        """
        try:
            # Get DataFrame from cache if string provided
            if isinstance(data, str):
                if data not in self.data_cache:
                    raise DataProcessError(f"Data not found in cache: {data}")
                df = self.data_cache[data]['data']
            else:
                df = data

            if viz_type == 'bar':
                fig = px.bar(df, **config)
            elif viz_type == 'line':
                fig = px.line(df, **config)
            elif viz_type == 'scatter':
                fig = px.scatter(df, **config)
            elif viz_type == 'pie':
                fig = px.pie(df, **config)
            else:
                raise DataProcessError(f"Unsupported visualization type: {viz_type}")

            # Save visualization
            output_path = f"temp/viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(output_path)

            return {
                'type': viz_type,
                'path': output_path,
                'config': config
            }

        except Exception as e:
            self.logger.error(f"Error creating visualization: {str(e)}")
            raise DataProcessError(f"Visualization creation failed: {str(e)}")

    async def combine_data(
        self,
        data1: Union[pd.DataFrame, str],
        data2: Union[pd.DataFrame, str],
        method: str = 'merge',
        **kwargs
    ) -> pd.DataFrame:
        """Combine two datasets
        
        Args:
            data1: First DataFrame or cache key
            data2: Second DataFrame or cache key
            method: Combination method ('merge' or 'concat')
            **kwargs: Additional arguments for merge/concat
            
        Returns:
            Combined DataFrame
        """
        try:
            # Get DataFrames from cache if needed
            df1 = data1 if isinstance(data1, pd.DataFrame) else self.data_cache[data1]['data']
            df2 = data2 if isinstance(data2, pd.DataFrame) else self.data_cache[data2]['data']

            if method == 'merge':
                result = pd.merge(df1, df2, **kwargs)
            elif method == 'concat':
                result = pd.concat([df1, df2], **kwargs)
            else:
                raise DataProcessError(f"Unsupported combination method: {method}")

            return result

        except Exception as e:
            self.logger.error(f"Error combining data: {str(e)}")
            raise DataProcessError(f"Data combination failed: {str(e)}")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        return {
            key: value['metadata']
            for key, value in self.data_cache.items()
        }

    def clear_cache(self):
        """Clear the data cache"""
        self.data_cache.clear()
        self.logger.info("Data cache cleared")

    async def close(self):
        """Clean up resources"""
        await self.connection_manager.close_all_connections()
        self.clear_cache()
        self.logger.info("Resources cleaned up")