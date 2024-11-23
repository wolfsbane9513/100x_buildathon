# report_generator/interface/app.py
import gradio as gr
from typing import Dict, Optional, Any
from dataclasses import dataclass
from report_generator.core.models.manager import ModelManager
from report_generator.core.agent import ReportGeneratorAgent
from report_generator.core.data.connection_manager import DatabaseConnectionManager

@dataclass
class ConnectionConfig:
    type: str
    config: Dict[str, Any]

class ReportGeneratorInterface:
    def __init__(self):
        self.model_manager = ModelManager()
        self.db_manager = DatabaseConnectionManager()
        self.current_connections: Dict[str, ConnectionConfig] = {}
        
    def create_interface(self):
        with gr.Blocks(title="Report Generator Agent") as app:
            gr.Markdown("# Intelligent Report Generator")
            
            # States for configurations
            api_key_state = gr.State({})
            db_config_state = gr.State({})
            
            with gr.Tabs():
                # Model Configuration Tab
                with gr.Tab("Model Configuration"):
                    with gr.Row():
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
                        api_key_input = gr.Textbox(
                            label="API Key",
                            placeholder="Enter API key if required",
                            type="password",
                            visible=False
                        )

                # Data Source Configuration Tab
                with gr.Tab("Data Source"):
                    with gr.Row():
                        data_source = gr.Radio(
                            choices=["file", "mongodb", "mysql", "postgresql"],
                            value="file",
                            label="Data Source"
                        )
                    
                    # File Upload Section
                    with gr.Group() as file_group:
                        file_input = gr.File(
                            label="Upload Data File",
                            file_types=[".csv", ".json", ".xlsx", ".xls"]
                        )
                    
                    # MongoDB Configuration
                    with gr.Group(visible=False) as mongo_group:
                        mongo_uri = gr.Textbox(
                            label="MongoDB URI",
                            placeholder="mongodb://username:password@host:port"
                        )
                        mongo_db = gr.Textbox(
                            label="Database Name"
                        )
                        mongo_collection = gr.Textbox(
                            label="Collection Name"
                        )
                    
                    # MySQL Configuration
                    with gr.Group(visible=False) as mysql_group:
                        mysql_host = gr.Textbox(label="Host")
                        mysql_port = gr.Number(label="Port", value=3306)
                        mysql_user = gr.Textbox(label="Username")
                        mysql_password = gr.Textbox(
                            label="Password",
                            type="password"
                        )
                        mysql_db = gr.Textbox(label="Database Name")
                    
                    # PostgreSQL Configuration
                    with gr.Group(visible=False) as postgres_group:
                        postgres_host = gr.Textbox(label="Host")
                        postgres_port = gr.Number(label="Port", value=5432)
                        postgres_user = gr.Textbox(label="Username")
                        postgres_password = gr.Textbox(
                            label="Password",
                            type="password"
                        )
                        postgres_db = gr.Textbox(label="Database Name")
                    
                    # Test Connection Button
                    test_connection_btn = gr.Button("Test Connection")
                    connection_status = gr.Textbox(
                        label="Connection Status",
                        interactive=False
                    )

                # Report Configuration Tab
                with gr.Tab("Report Generation"):
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
                    
                    generate_btn = gr.Button("Generate Report")
                    with gr.Row():
                        output = gr.File(label="Generated Report")
                        status_output = gr.Textbox(
                            label="Status",
                            interactive=False
                        )

            def update_data_source_visibility(source):
                """Update visibility of data source configuration groups"""
                return {
                    file_group: source == "file",
                    mongo_group: source == "mongodb",
                    mysql_group: source == "mysql",
                    postgres_group: source == "postgresql"
                }
            
            async def test_connection(
                source: str,
                mongo_uri: str,
                mongo_db: str,
                mongo_collection: str,
                mysql_host: str,
                mysql_port: int,
                mysql_user: str,
                mysql_password: str,
                mysql_db: str,
                postgres_host: str,
                postgres_port: int,
                postgres_user: str,
                postgres_password: str,
                postgres_db: str
            ) -> str:
                """Test database connection based on selected source"""
                try:
                    if source == "mongodb":
                        config = {
                            "uri": mongo_uri,
                            "database": mongo_db,
                            "collection": mongo_collection
                        }
                        await self.db_manager.test_mongodb_connection(config)
                    elif source == "mysql":
                        config = {
                            "host": mysql_host,
                            "port": mysql_port,
                            "user": mysql_user,
                            "password": mysql_password,
                            "database": mysql_db
                        }
                        await self.db_manager.test_mysql_connection(config)
                    elif source == "postgresql":
                        config = {
                            "host": postgres_host,
                            "port": postgres_port,
                            "user": postgres_user,
                            "password": postgres_password,
                            "database": postgres_db
                        }
                        await self.db_manager.test_postgresql_connection(config)
                    else:
                        return "No connection test needed for file input"
                    
                    return "Connection successful! ✅"
                except Exception as e:
                    return f"Connection failed: {str(e)} ❌"
            
            async def generate_report(
                source: str,
                provider: str,
                model_name: str,
                api_key: str,
                query: str,
                format: str,
                include_viz: bool,
                **db_params
            ):
                """Generate report with dynamic configuration"""
                try:
                    # Validate and set up model
                    if provider in ['openai', 'anthropic'] and not api_key:
                        return None, "API key is required"
                    
                    model = self.model_manager.get_model(provider, model_name, api_key)
                    
                    # Set up data source
                    data_config = self._get_data_config(source, **db_params)
                    data_source = await self.db_manager.get_data_source(
                        source,
                        data_config
                    )
                    
                    # Generate report
                    agent = ReportGeneratorAgent(model)
                    result = await agent.generate_report(
                        query=query,
                        context={
                            "data_source": data_source,
                            "format": format,
                            "include_viz": include_viz
                        }
                    )
                    
                    return result, "Report generated successfully"
                except Exception as e:
                    return None, f"Error: {str(e)}"
                
            def _get_data_config(self, source: str, **params) -> Dict[str, Any]:
                """Build data source configuration"""
                if source == "mongodb":
                    return {
                        "uri": params["mongo_uri"],
                        "database": params["mongo_db"],
                        "collection": params["mongo_collection"]
                    }
                elif source == "mysql":
                    return {
                        "host": params["mysql_host"],
                        "port": params["mysql_port"],
                        "user": params["mysql_user"],
                        "password": params["mysql_password"],
                        "database": params["mysql_db"]
                    }
                elif source == "postgresql":
                    return {
                        "host": params["postgres_host"],
                        "port": params["postgres_port"],
                        "user": params["postgres_user"],
                        "password": params["postgres_password"],
                        "database": params["postgres_db"]
                    }
                return {}

            # Set up event handlers
            data_source.change(
                fn=update_data_source_visibility,
                inputs=[data_source],
                outputs=[file_group, mongo_group, mysql_group, postgres_group]
            )
            
            test_connection_btn.click(
                fn=test_connection,
                inputs=[
                    data_source,
                    mongo_uri, mongo_db, mongo_collection,
                    mysql_host, mysql_port, mysql_user, mysql_password, mysql_db,
                    postgres_host, postgres_port, postgres_user, postgres_password, postgres_db
                ],
                outputs=[connection_status]
            )
            
            generate_btn.click(
                fn=generate_report,
                inputs=[
                    data_source, provider, model_name, api_key_input,
                    query_input, format_input, viz_input,
                    mongo_uri, mongo_db, mongo_collection,
                    mysql_host, mysql_port, mysql_user, mysql_password, mysql_db,
                    postgres_host, postgres_port, postgres_user, postgres_password, postgres_db
                ],
                outputs=[output, status_output]
            )
            
        return app