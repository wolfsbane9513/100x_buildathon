import logging
from typing import List, Dict, Any, Optional
from llama_index import ServiceContext, VectorStoreIndex, Document
from llama_index.tools import QueryEngineTool, ToolMetadata
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.service_context = ServiceContext.from_defaults(llm=self.llm)
        
    def _build_schema_context(self, data_sources: List[Dict[str, Any]]) -> str:
        """Build context string from data sources"""
        context = []
        
        for source in data_sources:
            if source["type"] == "file":
                df = source["data"]
                context.append(f"""
                File Data Schema:
                - Columns: {', '.join(df.columns)}
                - Data Types: {df.dtypes.to_dict()}
                - Sample Size: {len(df)} rows
                - Summary Statistics: {df.describe().to_dict()}
                """)
            
            elif source["type"] == "database":
                context.append(f"""
                Database Schema ({source['connection']}):
                Tables/Collections:
                {self._format_schema(source['schema'])}
                """)
        
        return "\n".join(context)
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Format database schema for context"""
        formatted = []
        for table, info in schema.items():
            if "columns" in info:  # SQL databases
                columns = [f"- {col['name']} ({col['type']})" for col in info["columns"]]
                formatted.append(f"""
                Table: {table}
                Columns:
                {chr(10).join(columns)}
                """)
            else:  # MongoDB collections
                formatted.append(f"""
                Collection: {table}
                Fields: {', '.join(info['fields'])}
                Sample Document: {info['sample']}
                """)
        return "\n".join(formatted)

    async def generate_report(
        self,
        data_sources: List[Dict[str, Any]],
        query: str,
        output_format: str = "pdf",
        include_viz: bool = True
    ) -> Dict[str, Any]:
        """Generate report from multiple data sources"""
        try:
            # Build context from data schemas
            schema_context = self._build_schema_context(data_sources)
            
            # Analyze data and create initial insights
            analysis_results = await self._analyze_data(data_sources, query)
            
            # Generate visualizations if requested
            visualizations = []
            if include_viz:
                visualizations = await self._create_visualizations(
                    data_sources,
                    analysis_results
                )
            
            # Generate report content
            content = await self._generate_report_content(
                query,
                schema_context,
                analysis_results,
                visualizations
            )
            
            # Format report
            formatted_report = self._format_report(
                content,
                output_format,
                visualizations
            )
            
            return formatted_report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    async def _analyze_data(
        self,
        data_sources: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """Analyze data from all sources"""
        analysis_results = {
            "file_analysis": [],
            "database_analysis": [],
            "relationships": [],
            "insights": []
        }
        
        try:
            # Analyze file data
            for source in data_sources:
                if source["type"] == "file":
                    file_analysis = self._analyze_dataframe(source["data"])
                    analysis_results["file_analysis"].append(file_analysis)
                
                elif source["type"] == "database":
                    db_analysis = await self._analyze_database(
                        source["connection"],
                        source["schema"]
                    )
                    analysis_results["database_analysis"].append(db_analysis)
            
            # Find relationships between sources
            if len(data_sources) > 1:
                analysis_results["relationships"] = await self._find_relationships(data_sources)
            
            # Generate insights based on query
            analysis_results["insights"] = await self._generate_insights(
                query,
                analysis_results
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in data analysis: {str(e)}")
            raise

    def _analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze a pandas DataFrame"""
        analysis = {
            "summary_stats": df.describe().to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "column_types": df.dtypes.to_dict(),
            "unique_counts": {col: df[col].nunique() for col in df.columns},
            "correlations": {}
        }
        
        # Calculate correlations for numerical columns
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numerical_cols) > 1:
            analysis["correlations"] = df[numerical_cols].corr().to_dict()
        
        return analysis

    async def _analyze_database(
        self,
        connection_type: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze database structure and sample data"""
        try:
            analysis = {
                "structure": schema,
                "table_stats": {},
                "sample_queries": []
            }
            
            # Generate sample queries based on schema
            analysis["sample_queries"] = self._generate_sample_queries(
                connection_type,
                schema
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing database: {str(e)}")
            raise

    def _generate_sample_queries(
        self,
        connection_type: str,
        schema: Dict[str, Any]
    ) -> List[str]:
        """Generate sample queries based on schema"""
        queries = []
        
        if connection_type in ["mysql", "postgresql"]:
            for table, info in schema.items():
                # Basic SELECT query
                columns = [col["name"] for col in info["columns"]]
                queries.append(f"SELECT {', '.join(columns)} FROM {table}")
                
                # Aggregation query example
                numeric_cols = [col["name"] for col in info["columns"] 
                              if "int" in col["type"] or "numeric" in col["type"]]
                if numeric_cols:
                    queries.append(
                        f"SELECT AVG({numeric_cols[0]}) FROM {table}"
                    )
        
        elif connection_type == "mongodb":
            for collection, info in schema.items():
                # Basic find query
                queries.append(f'db.{collection}.find({{}})')
                
                # Aggregation example
                if "fields" in info:
                    numeric_fields = [f for f in info["fields"] 
                                    if isinstance(info["sample"].get(f), (int, float))]
                    if numeric_fields:
                        queries.append(
                            f'db.{collection}.aggregate([{{"$group": {{"_id": null, '
                            f'"avg_{numeric_fields[0]}": {{"$avg": "${numeric_fields[0]}"}}}}}}])'
                        )
        
        return queries

    async def _find_relationships(
        self,
        data_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find potential relationships between data sources"""
        relationships = []
        
        try:
            # Compare column names and data types
            for i, source1 in enumerate(data_sources):
                for source2 in data_sources[i+1:]:
                    relationship = self._compare_sources(source1, source2)
                    if relationship:
                        relationships.append(relationship)
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error finding relationships: {str(e)}")
            return []

    def _compare_sources(
        self,
        source1: Dict[str, Any],
        source2: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Compare two data sources for potential relationships"""
        try:
            common_fields = set()
            
            if source1["type"] == "file" and source2["type"] == "file":
                # Compare DataFrame columns
                common_fields = set(source1["data"].columns) & set(source2["data"].columns)
                
            elif source1["type"] == "database" and source2["type"] == "database":
                # Compare database schemas
                schema1 = set(self._get_all_fields(source1["schema"]))
                schema2 = set(self._get_all_fields(source2["schema"]))
                common_fields = schema1 & schema2
                
            elif source1["type"] == "file" and source2["type"] == "database":
                # Compare DataFrame columns with database fields
                fields1 = set(source1["data"].columns)
                fields2 = set(self._get_all_fields(source2["schema"]))
                common_fields = fields1 & fields2
            
            if common_fields:
                return {
                    "source1": source1["type"],
                    "source2": source2["type"],
                    "common_fields": list(common_fields)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error comparing sources: {str(e)}")
            return None

    def _get_all_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Extract all field names from a database schema"""
        fields = set()
        
        for table, info in schema.items():
            if "columns" in info:  # SQL databases
                fields.update(col["name"] for col in info["columns"])
            else:  # MongoDB collections
                fields.update(info["fields"])
        
        return list(fields)

    async def _generate_insights(
        self,
        query: str,
        analysis_results: Dict[str, Any]
    ) -> List[str]:
        """Generate insights based on analysis results"""
        try:
            # Build prompt for the LLM
            prompt = f"""
            Based on the following analysis results, generate key insights and recommendations:
            
            Query: {query}
            
            File Analysis:
            {analysis_results['file_analysis']}
            
            Database Analysis:
            {analysis_results['database_analysis']}
            
            Relationships:
            {analysis_results['relationships']}
            
            Focus on:
            1. Key trends and patterns
            2. Anomalies or outliers
            3. Significant relationships
            4. Business implications
            5. Actionable recommendations
            """
            
            # Generate insights using LLM
            response = await self.llm.acomplete(prompt)
            insights = response.text.split('\n')
            return [insight.strip() for insight in insights if insight.strip()]
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []

    async def _create_visualizations(
        self,
        data_sources: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create visualizations based on data analysis"""
        visualizations = []
        
        try:
            for source in data_sources:
                if source["type"] == "file":
                    viz = await self._create_dataframe_visualizations(
                        source["data"],
                        analysis_results
                    )
                    visualizations.extend(viz)
                
                elif source["type"] == "database":
                    viz = await self._create_database_visualizations(
                        source["connection"],
                        source["schema"],
                        analysis_results
                    )
                    visualizations.extend(viz)
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            return []

    # Add more methods for specific visualization types, report formatting, etc.