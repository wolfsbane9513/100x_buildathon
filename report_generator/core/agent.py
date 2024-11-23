# report_generator/core/agent.py
from typing import Dict, Any
from llama_index.core import Settings
from llama_index.core.agent.react.base import ReActAgent  # Updated import path
from llama_index.core.base.response import Response
from llama_index.llms.base import LLM
from llama_index.core.callbacks import CallbackManager
from report_generator.core.tools.tools import get_default_tools

class ReportGeneratorAgent:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        Settings.llm = llm
        self.tools = get_default_tools()
        self.agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            callback_manager=CallbackManager()
        )
    
    async def generate_report(self, query: str, context: Dict[str, Any]) -> str:
        prompt = self._build_prompt(query, context)
        response = await self.agent.achat(prompt)
        return response.response
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        return f"""
        Generate a report based on the following request: {query}
        Context: {context}
        Include data analysis and insights.
        Include appropriate visualizations if requested.
        """