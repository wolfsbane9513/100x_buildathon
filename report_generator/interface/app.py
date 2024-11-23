import gradio as gr
from typing import Dict, Optional, Any
from report_generator.core.models.manager import ModelManager
from report_generator.core.agent import ReportGeneratorAgent
import logging

logger = logging.getLogger(__name__)

class ReportGeneratorInterface:
    def __init__(self):
        self.model_manager = ModelManager()
        
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="Report Generator Agent") as app:
            gr.Markdown("# Intelligent Report Generator")
            
            with gr.Tabs():
                # Model Selection Tab
                with gr.Tab("Model Selection"):
                    provider = gr.Radio(
                        choices=self.model_manager.get_available_providers(),
                        label="Select Model Provider",
                        interactive=True
                    )
                    
                    model_name = gr.Dropdown(
                        choices=[],
                        label="Select Model",
                        interactive=True
                    )
                    
                    api_key = gr.Textbox(
                        label="API Key (if required)",
                        type="password",
                        visible=False,
                        interactive=True
                    )
                    
                    model_info = gr.JSON(
                        label="Model Information",
                        visible=False
                    )

                # Data Source Tab
                with gr.Tab("Data Source"):
                    source_type = gr.Radio(
                        choices=["File Upload", "Database", "Both"],
                        label="Select Data Source",
                        interactive=True
                    )
                    
                    # File Upload Section
                    with gr.Group() as file_group:
                        file_input = gr.File(
                            label="Upload Data Files",
                            file_types=[".csv", ".json", ".xlsx", ".xls"],
                            file_count="multiple",
                            visible=True,
                            interactive=True
                        )
                    
                    # Database Section
                    with gr.Group() as db_group:
                        db_type = gr.Radio(
                            choices=["MongoDB", "MySQL", "PostgreSQL"],
                            label="Database Type",
                            visible=False,
                            interactive=True
                        )
                        
                        connection_info = gr.JSON(
                            label="Connection Details",
                            visible=False
                        )
                        
                        test_connection = gr.Button(
                            "Test Connection",
                            visible=False
                        )

                # Report Configuration Tab
                with gr.Tab("Generate Report"):
                    query = gr.Textbox(
                        label="What would you like to analyze?",
                        placeholder="Describe what you'd like to learn from the data...",
                        lines=3,
                        interactive=True
                    )
                    
                    format_type = gr.Radio(
                        choices=["PDF", "HTML", "DOCX"],
                        label="Report Format",
                        value="PDF",
                        interactive=True
                    )
                    
                    include_viz = gr.Checkbox(
                        label="Include Visualizations",
                        value=True,
                        interactive=True
                    )
                    
                    generate_btn = gr.Button("Generate Report", variant="primary")
                    
                    with gr.Row():
                        output_file = gr.File(label="Generated Report")
                        status = gr.Textbox(label="Status")

            # Event Handlers
            def update_model_list(provider_value):
                """Update model list when provider is selected"""
                if not provider_value:
                    return [], gr.update(visible=False), gr.update(visible=False)
                
                models = self.model_manager.get_available_models(provider_value)
                provider_info = self.model_manager.get_provider_info(provider_value)
                
                return (
                    models,
                    gr.update(visible=provider_info.get('requires_key', False)),
                    gr.update(visible=True)
                )

            def update_data_source(source_type):
                """Update visible components based on data source selection"""
                show_files = source_type in ["File Upload", "Both"]
                show_db = source_type in ["Database", "Both"]
                
                return {
                    file_group: gr.update(visible=show_files),
                    db_group: gr.update(visible=show_db),
                    db_type: gr.update(visible=show_db),
                    connection_info: gr.update(visible=show_db),
                    test_connection: gr.update(visible=show_db)
                }

            def on_generate_click(
                provider_value,
                model_name,
                api_key,
                source_type,
                files,
                db_info,
                query_text,
                format_type,
                include_viz
            ):
                """Handle report generation"""
                try:
                    if not model_name:
                        return None, "Please select a model first"
                    
                    if not query_text:
                        return None, "Please enter a query"
                    
                    # Initialize model only when needed
                    model = self.model_manager.get_model(
                        provider_value,
                        model_name,
                        api_key
                    )
                    
                    # Initialize agent
                    agent = ReportGeneratorAgent(model)
                    
                    # Start report generation
                    return "Report.pdf", "Processing..."  # Placeholder
                    
                except Exception as e:
                    logger.error(f"Error in report generation: {str(e)}")
                    return None, f"Error: {str(e)}"

            # Connect event handlers
            provider.change(
                fn=update_model_list,
                inputs=provider,
                outputs=[model_name, api_key, model_info]
            )
            
            source_type.change(
                fn=update_data_source,
                inputs=source_type,
                outputs=[file_group, db_group, db_type, connection_info, test_connection]
            )
            
            generate_btn.click(
                fn=on_generate_click,
                inputs=[
                    provider,
                    model_name,
                    api_key,
                    source_type,
                    file_input,
                    connection_info,
                    query,
                    format_type,
                    include_viz
                ],
                outputs=[output_file, status]
            )

        return app

    def launch(self):
        """Launch the interface"""
        app = self.create_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )