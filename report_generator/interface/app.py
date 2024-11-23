# report_generator/interface/app.py
import gradio as gr
from typing import Dict, Optional
from dataclasses import dataclass
from report_generator.core.models.manager import ModelManager
from report_generator.core.agent import ReportGeneratorAgent
from report_generator.app.config import Config

@dataclass
class ModelInfo:
    provider: str
    name: str
    requires_api: bool
    api_key: Optional[str] = None

class ReportGeneratorInterface:
    def __init__(self):
        self.model_manager = ModelManager()
        self.current_api_keys: Dict[str, str] = {}
        
    def create_interface(self):
        """Create Gradio interface with dynamic API key management"""
        with gr.Blocks(title="Report Generator Agent") as app:
            gr.Markdown("# Intelligent Report Generator")
            
            # Create state for API keys
            api_key_state = gr.State({})
            
            with gr.Row():
                with gr.Column():
                    # Model Selection
                    provider = gr.Radio(
                        choices=['local', 'openai', 'anthropic'],
                        value='local',
                        label="Model Provider"
                    )
                    
                    model_name = gr.Dropdown(
                        choices=self.model_manager.get_available_models('local'),
                        value='mixtral',
                        label="Model"
                    )
                    
                    # Dynamic API Key Input
                    api_key_input = gr.Textbox(
                        label="API Key",
                        placeholder="Enter API key if required",
                        type="password",
                        visible=False
                    )
                    
                    # File Upload and Options
                    file_input = gr.File(
                        label="Upload Data File",
                        file_types=[".csv", ".json", ".xlsx", ".xls"]
                    )
                    
                    query_input = gr.Textbox(
                        label="What kind of report do you need?",
                        placeholder="E.g., Generate a sales report for Q3 with monthly trends"
                    )
                    
                    format_input = gr.Dropdown(
                        choices=["pdf", "docx", "html"],
                        value="pdf",
                        label="Output Format"
                    )
                    
                    viz_input = gr.Checkbox(
                        label="Include Visualizations",
                        value=True
                    )
                
                with gr.Column():
                    output = gr.File(label="Generated Report")
                    status_output = gr.Textbox(label="Status", interactive=False)
            
            def update_model_visibility(provider: str):
                """Update model dropdown and API key input visibility"""
                models = self.model_manager.get_available_models(provider)
                needs_api = provider in ['openai', 'anthropic']
                return {
                    model_name: gr.Dropdown(choices=models),
                    api_key_input: gr.Textbox(visible=needs_api)
                }
            
            def validate_api_key(provider: str, api_key: str) -> str:
                """Validate API key based on provider"""
                if not api_key and provider in ['openai', 'anthropic']:
                    return "API key is required for this model provider"
                return ""
            
            def update_api_key(provider: str, api_key: str, state: Dict[str, str]) -> Dict[str, str]:
                """Update API key in state"""
                if provider in ['openai', 'anthropic']:
                    state[provider] = api_key
                return state
            
            async def generate_report(
                provider: str,
                model_name: str,
                api_key: str,
                file: gr.File,
                query: str,
                output_format: str,
                include_viz: bool,
                api_key_state: Dict[str, str]
            ):
                """Handle report generation with API key validation"""
                try:
                    # Validate API key if needed
                    if provider in ['openai', 'anthropic']:
                        if not api_key:
                            return None, "API key is required"
                        api_key_state[provider] = api_key
                    
                    # Initialize model with API key if needed
                    model = self.model_manager.get_model(
                        provider,
                        model_name,
                        api_key_state.get(provider)
                    )
                    
                    # Generate report
                    agent = ReportGeneratorAgent(model)
                    result = await agent.generate_report(
                        query=query,
                        context={
                            "file": file,
                            "format": output_format,
                            "include_viz": include_viz
                        }
                    )
                    
                    return result, "Report generated successfully"
                except Exception as e:
                    return None, f"Error: {str(e)}"
            
            # Set up event handlers
            provider.change(
                fn=update_model_visibility,
                inputs=[provider],
                outputs=[model_name, api_key_input]
            )
            
            api_key_input.change(
                fn=update_api_key,
                inputs=[provider, api_key_input, api_key_state],
                outputs=[api_key_state]
            )
            
            submit_btn = gr.Button("Generate Report")
            submit_btn.click(
                fn=generate_report,
                inputs=[
                    provider,
                    model_name,
                    api_key_input,
                    file_input,
                    query_input,
                    format_input,
                    viz_input,
                    api_key_state
                ],
                outputs=[output, status_output]
            )
        
        return app