from report_generator.core.processors.viz_processor import Visualizer


def get_default_tools():
    """
    This function returns a default set of tools for the agent.
    These tools include visualizations wrapped using LlamaIndex tools.
    """
    # Import BaseTool inside the function to avoid circular import issues
    from llama_index.core.tools import BaseTool

    visualizer = Visualizer()
    
    tools = [
        # Example of LlamaIndex integration
        BaseTool(
            name="query_engine",
            description="Executes a query using a base query engine",
            query_engine=None,  # Placeholder until a valid query engine is provided
            metadata=None
        )
    ]
    
    return tools
