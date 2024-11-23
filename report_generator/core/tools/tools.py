from typing import List
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.tools.types import ToolMetadata
from core.processors.viz_processor import Visualizer

def get_default_tools() -> List[BaseTool]:

    """Get default set of tools for the agent"""
    visualizer = Visualizer()
    
    tools = [
        FunctionTool.from_defaults(
            fn=visualizer.create_bar_chart,
            name="create_bar_chart",
            description="Creates a bar chart from the data"
        ),
        FunctionTool.from_defaults(
            fn=visualizer.create_line_chart,
            name="create_line_chart",
            description="Creates a line chart from the data"
        ),
        FunctionTool.from_defaults(
            fn=visualizer.create_pie_chart,
            name="create_pie_chart",
            description="Creates a pie chart from the data"
        ),
    ]
    return tools
