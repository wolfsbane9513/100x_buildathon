import gradio as gr
from typing import Dict, Optional, Any
from report_generator.core.models.manager import ModelManager
from report_generator.core.agent import ReportGeneratorAgent

class ReportGeneratorInterface:
    def __init__(self):
        self.model_manager = ModelManager()
        
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="Report Generator Agent") as app:
            gr.Markdown("# Intelligent Report Generator")
            
            with gr.Row():
                with gr.Column():
                    # Get available providers and models
                    default_provider, default_model = self.model_manager.get_default_model()
                    available_providers = self.model_manager.get_available_providers()
                    
                    provider = gr.Radio(
                        choices=available_providers,
                        value=default_provider,
                        label="Model Provider"
                    )
                    
                    model_name = gr.Dropdown(
                        choices=self.model_manager.get_available_models(default_provider),
                        value=default_model,
                        label="Model"
                    )
                    
                    api_key = gr.Textbox(
                        label="API Key (if required)",
                        type="password",
                        visible=default_provider != 'local'
                    )
                    
                    file_input = gr.File(
                        label="Upload Data File",
                        file_types=[".csv", ".json", ".xlsx", ".xls"]
                    )
                    
                    query_input = gr.Textbox(
                        label="What kind of report do you need?",
                        placeholder="E.g., Generate a sales report for Q3 with monthly trends",
                        lines=3
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
                    status = gr.Textbox(label="Status", interactive=False)

            def update_model_choices(provider_value):
                """Update model choices based on provider"""
                models = self.model_manager.get_available_models(provider_value)
                return {
                    model_name: gr.Dropdown(choices=models),
                    api_key: gr.Textbox(visible=provider_value != 'local')
                }

            provider.change(
                fn=update_model_choices,
                inputs=provider,
                outputs=[model_name, api_key]
            )
            
            generate_btn = gr.Button("Generate Report")
            
            @generate_btn.click
            async def generate_report(
                provider_value,
                model_name_value,
                api_key_value,
                file,
                query,
                format_value,
                include_viz
            ):
                try:
                    # Get model instance
                    model = self.model_manager.get_model(
                        provider_value,
                        model_name_value,
                        api_key_value
                    )
                    
                    # Create agent
                    agent = ReportGeneratorAgent(model)
                    
                    # Generate report
                    result = await agent.generate_report(
                        file=file,
                        query=query,
                        output_format=format_value,
                        include_viz=include_viz
                    )
                    
                    return result, "Report generated successfully!"
                except Exception as e:
                    return None, f"Error: {str(e)}"
            
            generate_btn.click(
                fn=generate_report,
                inputs=[
                    provider,
                    model_name,
                    api_key,
                    file_input,
                    query_input,
                    format_input,
                    viz_input
                ],
                outputs=[output, status]
            )
        
        return app