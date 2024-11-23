# report_generator/core/agent.py
from typing import Dict, Any, Optional
import logging
from llama_index import (
    ServiceContext,
    LLMPredictor,
    VectorStoreIndex,
    SimpleDirectoryReader
)
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.indices.query.base import BaseQueryEngine
from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_agent

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    def __init__(self, llm: Optional[Any] = None):
        """Initialize the Report Generator Agent."""
        try:
            # Initialize LLM
            self.llm = llm or OpenAI(model="gpt-3.5-turbo")
            
            # Create service context
            self.service_context = ServiceContext.from_defaults(
                llm=self.llm
            )
            
            # Get tools
            self.tools = self._get_default_tools()
            
            # Create toolkit and agent
            self.toolkit = LlamaToolkit(
                tools=self.tools
            )
            
            # Initialize agent
            self.agent = create_llama_agent(
                toolkit=self.toolkit,
                llm=self.llm,
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise

    def _get_default_tools(self) -> list:
        """Get default tools for the agent."""
        try:
            tools = []
            # Basic query tool
            index = VectorStoreIndex([])  # Empty index for now
            query_engine = index.as_query_engine()
            
            tools.append(
                QueryEngineTool(
                    query_engine=query_engine,
                    metadata=ToolMetadata(
                        name="data_analyzer",
                        description="Analyzes data and provides insights"
                    )
                )
            )
            return tools
        except Exception as e:
            logger.error(f"Error creating tools: {str(e)}")
            return []

    async def generate_report(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate a report based on the query and context."""
        try:
            prompt = self._build_prompt(query, context)
            response = await self.agent.achat(prompt)
            return response.response
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build the prompt for report generation."""
        return f"""
        Generate a report based on the following request: {query}
        Context: {context}
        Instructions:
        1. Begin with a clear executive summary
        2. Include detailed data analysis and insights
        3. Support findings with relevant visualizations if requested
        4. Conclude with actionable recommendations
        
        Please provide a comprehensive and well-structured report.
        """
