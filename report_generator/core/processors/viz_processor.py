import plotly.express as px
from pathlib import Path
import pandas as pd
from datetime import datetime
from app.config import Config
import plotly.graph_objects as go

class Visualizer:
    def __init__(self):
        self.output_dir = Config.TEMP_DIR
    
    def create_bar_chart(self, 
                        data: pd.DataFrame,
                        x: str,
                        y: str,
                        title: str) -> str:
        """Create bar chart and save to file"""
        fig = px.bar(data, x=x, y=y, title=title)
        return self._save_figure(fig, "bar_chart")
    
    def create_line_chart(self,
                         data: pd.DataFrame,
                         x: str,
                         y: str,
                         title: str) -> str:
        """Create line chart and save to file"""
        fig = px.line(data, x=x, y=y, title=title)
        return self._save_figure(fig, "line_chart")
    
    def create_pie_chart(self,
                        data: pd.DataFrame,
                        names: str,
                        values: str,
                        title: str) -> str:
        """Create pie chart and save to file"""
        fig = px.pie(data, names=names, values=values, title=title)
        return self._save_figure(fig, "pie_chart")
    
    def _save_figure(self, fig, prefix: str) -> str:
        """Save figure to file and return path"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f"{prefix}_{timestamp}.png"
        fig.write_image(str(output_path))
        return str(output_path)