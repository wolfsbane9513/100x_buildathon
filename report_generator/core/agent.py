import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    def __init__(self, llm):
        """Initialize the Report Generator Agent.
        
        Args:
            llm: Language model instance with required attributes
        """
        # Validate and store the model
        self.llm = self._validate_model(llm)
        logger.info(f"Agent initialized with model: {self.llm.metadata}")

    def _validate_model(self, llm):
        """Validate that the model has required attributes."""
        try:
            # Ensure model has required attributes
            required_attrs = ['metadata', 'context_window', 'generate']
            
            # Check instance attributes
            if not hasattr(llm, 'metadata') or not isinstance(llm.metadata, dict):
                llm.metadata = {'model_name': 'unknown', 'provider': 'unknown'}
                logger.warning("Model missing metadata, using defaults")
            
            if not hasattr(llm, 'context_window'):
                llm.context_window = 2048  # Default context window
                logger.warning("Model missing context_window, using default: 2048")
            
            if not hasattr(llm, 'generate'):
                raise ValueError("Model must implement 'generate' method")
            
            logger.info(f"Model validation successful: {llm.metadata}")
            return llm
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise ValueError(f"Invalid model instance: {str(e)}")

    async def generate_report(
        self,
        query: str,
        context: Dict[str, Any],
        output_format: str = "pdf",
        include_viz: bool = True
    ) -> Dict[str, Any]:
        """Generate report based on query and context."""
        try:
            logger.info(f"Starting report generation with query: {query}")
            logger.info(f"Context: {context}")
            
            # Generate report content using the model
            prompt = self._build_prompt(query, context)
            
            response = await self.llm.generate(prompt)
            
            # Process the response
            result = {
                'content': response.content,
                'format': output_format,
                'visualizations': [] if include_viz else None,
                'metadata': {
                    'model': self.llm.metadata,
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            logger.info("Report generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build the prompt for report generation."""
        return f"""
        Generate a report based on the following request: {query}
        
        Context:
        {context}
        
        Instructions:
        1. Begin with a clear executive summary
        2. Include detailed analysis and insights
        3. Support findings with relevant data points
        4. Conclude with actionable recommendations
        
        Format the report professionally and clearly.
        """

    async def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data and provide insights."""
        try:
            analysis = {
                'summary': {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'missing_values': data.isnull().sum().to_dict()
                },
                'column_analysis': {}
            }
            
            for column in data.columns:
                analysis['column_analysis'][column] = self._analyze_column(data[column])
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            raise

    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column."""
        try:
            if pd.api.types.is_numeric_dtype(series):
                return {
                    'type': 'numeric',
                    'mean': series.mean(),
                    'median': series.median(),
                    'std': series.std(),
                    'min': series.min(),
                    'max': series.max()
                }
            elif pd.api.types.is_datetime64_dtype(series):
                return {
                    'type': 'datetime',
                    'min': series.min(),
                    'max': series.max(),
                    'range_days': (series.max() - series.min()).days
                }
            else:
                return {
                    'type': 'categorical',
                    'unique_values': series.nunique(),
                    'most_common': series.mode().iloc[0] if not series.mode().empty else None
                }
        except Exception as e:
            logger.error(f"Error analyzing column: {str(e)}")
            return {'type': 'unknown', 'error': str(e)}