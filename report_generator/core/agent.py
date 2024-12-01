import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import os
import traceback
from report_generator.core.processors.viz_processor import Visualizer

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    def __init__(self, llm):
        """Initialize the Report Generator Agent."""
        self.llm = self._validate_model(llm)
        self.visualizer = Visualizer()
        logger.info(f"Agent initialized with model: {self.llm.metadata}")

    def _validate_model(self, llm):
        """Validate model has required attributes."""
        try:
            required_attrs = ['metadata', 'context_window', 'generate']
            for attr in required_attrs:
                if not hasattr(llm, attr):
                    raise ValueError(f"Model missing required attribute: {attr}")
            return llm
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise

    async def generate_report(self, query: str, context: Dict[str, Any], output_format: str = "pdf", include_viz: bool = True) -> Dict[str, Any]:
        """Generate report based on query and context."""
        try:
            # Step 1: Read data
            data = await self._read_data(context)
            if data is None:
                raise ValueError("No data available for analysis")

            # Step 2: Analyze data
            analysis = await self._analyze_data(data)

            # Step 3: Generate visualizations if requested
            visualizations = []
            if include_viz:
                logger.info("Generating visualizations...")
                visualizations = await self._generate_visualizations(data)

            # Step 4: Build the prompt for the language model
            prompt = self._build_prompt(query, context, analysis)

            # Step 5: Use the language model to generate report content
            response = await self.llm.generate(prompt)

            # Step 6: Compile the result
            result = {
                'content': response.content,
                'format': output_format,
                'visualizations': visualizations,
                'metadata': {
                    'model': self.llm.metadata,
                    'query': query,
                    'timestamp': pd.Timestamp.now().isoformat()
                },
                'analysis': analysis
            }

            logger.info("Report generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}\n{traceback.format_exc()}")
            raise

    async def _read_data(self, context: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Read data from provided sources with encoding handling."""
        try:
            if 'files' in context and context['files']:
                file_path = context['files'][0]  # Start with the first file
                if os.path.exists(file_path):
                    logger.info(f"Reading file: {file_path}")
                    
                    if file_path.endswith('.csv'):
                        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                        for encoding in encodings:
                            try:
                                logger.info(f"Attempting to read with {encoding} encoding")
                                df = pd.read_csv(file_path, encoding=encoding)
                                logger.info(f"Successfully read file with {encoding} encoding")
                                return df
                            except UnicodeDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"Error reading with {encoding}: {str(e)}")
                                continue
                        
                        raise ValueError(f"Unable to read file with any supported encoding: {encodings}")

                    elif file_path.endswith(('.xls', '.xlsx')):
                        try:
                            df = pd.read_excel(file_path)
                            logger.info("Successfully read Excel file")
                            return df
                        except Exception as e:
                            logger.error(f"Error reading Excel file: {str(e)}")
                            raise

                    else:
                        raise ValueError(f"Unsupported file type: {file_path}")

                else:
                    raise FileNotFoundError(f"File not found: {file_path}")

            return None
        except Exception as e:
            logger.error(f"Error reading data: {str(e)}")
            raise

    async def _analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the data and generate insights."""
        try:
            logger.info("Starting data analysis...")
            analysis = {
                'summary': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'columns': list(df.columns),
                    'dtypes': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
                    'missing_values': df.isnull().sum().to_dict()
                },
                'numeric_summary': {},
                'categorical_summary': {}
            }
            
            # Analyze numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            for col in numeric_cols:
                try:
                    analysis['numeric_summary'][str(col)] = {
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max())
                    }
                except Exception as e:
                    logger.warning(f"Error analyzing numeric column {col}: {str(e)}")
            
            # Analyze categorical columns
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                try:
                    value_counts = df[col].value_counts()
                    analysis['categorical_summary'][str(col)] = {
                        'unique_values': int(len(value_counts)),
                        'top_values': {str(k): int(v) for k, v in value_counts.head(5).to_dict().items()}
                    }
                except Exception as e:
                    logger.warning(f"Error analyzing categorical column {col}: {str(e)}")
            
            logger.info("Data analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            raise

    # Modified _generate_visualizations() in agent.py

    async def _generate_visualizations(self, data: pd.DataFrame) -> List[str]:
        """Generate visualizations from the analyzed data."""
        visualizations = []

        try:
            logger.info("Starting visualization generation...")

            # Create a bar chart for top product lines by sales
            if "PRODUCTLINE" in data.columns and "SALES" in data.columns:
                logger.info("Generating bar chart for Sales by Product Line...")
                chart_path = self.visualizer.create_bar_chart(
                    data.groupby("PRODUCTLINE").sum().reset_index(),
                    x="PRODUCTLINE",
                    y="SALES",
                    title="Sales by Product Line"
                )
                logger.info(f"Bar chart generated successfully: {chart_path}")
                visualizations.append(chart_path)

            # Create a pie chart for deal sizes
            if "DEALSIZE" in data.columns:
                logger.info("Generating pie chart for Sales by Deal Size...")
                chart_path = self.visualizer.create_pie_chart(
                    data,
                    names="DEALSIZE",
                    values="SALES",
                    title="Sales by Deal Size"
                )
                logger.info(f"Pie chart generated successfully: {chart_path}")
                visualizations.append(chart_path)

            # Create a scatter plot to visualize the relationship between price and sales
            if "PRICEEACH" in data.columns and "SALES" in data.columns:
                logger.info("Generating scatter plot for Price vs Sales...")
                chart_path = self.visualizer.create_scatter_plot(
                    data,
                    x="PRICEEACH",
                    y="SALES",
                    title="Price vs Sales"
                )
                logger.info(f"Scatter plot generated successfully: {chart_path}")
                visualizations.append(chart_path)

            logger.info("Visualization generation completed successfully.")

        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
        
        return visualizations

    def _build_prompt(self, query: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Build enhanced prompt with data insights."""
        return f"""
        Generate a report based on the following request: {query}

        Data Analysis:
        - Total Records: {analysis['summary']['total_rows']}
        - Available Columns: {', '.join(analysis['summary']['columns'])}
        - Numeric Summaries: {analysis['numeric_summary']}
        - Categorical Summaries: {analysis['categorical_summary']}

        Instructions:
        1. Begin with a clear executive summary
        2. Include detailed analysis and insights based on the data provided
        3. Support findings with specific numbers and statistics
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