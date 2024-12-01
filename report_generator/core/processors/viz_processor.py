import logging
from pathlib import Path  
import pandas as pd
from datetime import datetime
from report_generator.app.config import config
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import os

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self):
        self.output_dir = config.TEMP_DIR

    def create_bar_chart(self, data: pd.DataFrame, x: str, y: str, title: str) -> str:
        try:
            logger.info(f"Starting Matplotlib bar chart creation for {title}...")
            
            # Plot using Matplotlib
            fig, ax = plt.subplots()
            ax.bar(data[x], data[y])
            ax.set_title(title)
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path_png = self.output_dir / f"matplotlib_bar_chart_{timestamp}.png"

            start_time = datetime.now()
            fig.savefig(output_path_png)
            end_time = datetime.now()

            logger.info(f"Matplotlib bar chart saved successfully at {output_path_png}. Time taken: {end_time - start_time}")
            plt.close(fig)

            return str(output_path_png)
        except Exception as e:
            logger.error(f"Error while creating Matplotlib bar chart: {str(e)}")
            raise

    def create_line_chart(self, data: pd.DataFrame, x: str, y: str, title: str) -> str:
        try:
            logger.info(f"Starting Matplotlib line chart creation for {title}...")
            
            # Plot using Matplotlib
            fig, ax = plt.subplots()
            ax.plot(data[x], data[y])
            ax.set_title(title)
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path_png = self.output_dir / f"matplotlib_line_chart_{timestamp}.png"

            start_time = datetime.now()
            fig.savefig(output_path_png)
            end_time = datetime.now()

            logger.info(f"Matplotlib line chart saved successfully at {output_path_png}. Time taken: {end_time - start_time}")
            plt.close(fig)

            return str(output_path_png)
        except Exception as e:
            logger.error(f"Error while creating Matplotlib line chart: {str(e)}")
            raise

    def create_pie_chart(self, data: pd.DataFrame, names: str, values: str, title: str) -> str:
        try:
            logger.info(f"Starting Matplotlib pie chart creation for {title}...")
            
            # Plot using Matplotlib
            fig, ax = plt.subplots()
            ax.pie(data[values], labels=data[names], autopct='%1.1f%%')
            ax.set_title(title)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path_png = self.output_dir / f"matplotlib_pie_chart_{timestamp}.png"

            start_time = datetime.now()
            fig.savefig(output_path_png)
            end_time = datetime.now()

            logger.info(f"Matplotlib pie chart saved successfully at {output_path_png}. Time taken: {end_time - start_time}")
            plt.close(fig)

            return str(output_path_png)
        except Exception as e:
            logger.error(f"Error while creating Matplotlib pie chart: {str(e)}")
            raise

    def create_scatter_plot(self, data: pd.DataFrame, x: str, y: str, title: str) -> str:
        try:
            logger.info(f"Starting Matplotlib scatter plot creation for {title}...")
            
            # Plot using Matplotlib
            fig, ax = plt.subplots()
            ax.scatter(data[x], data[y])
            ax.set_title(title)
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path_png = self.output_dir / f"matplotlib_scatter_plot_{timestamp}.png"

            start_time = datetime.now()
            fig.savefig(output_path_png)
            end_time = datetime.now()

            logger.info(f"Matplotlib scatter plot saved successfully at {output_path_png}. Time taken: {end_time - start_time}")
            plt.close(fig)

            return str(output_path_png)
        except Exception as e:
            logger.error(f"Error while creating Matplotlib scatter plot: {str(e)}")
            raise

    def create_custom_bar_chart(self, year: list, production: list, title: str = "Production by Year") -> str:
        try:
            logger.info(f"Starting custom Matplotlib bar chart creation...")

            # Plot using Matplotlib
            fig, ax = plt.subplots()
            ax.bar(year, production)
            ax.set_title(title)
            ax.set_xlabel("Year")
            ax.set_ylabel("Production")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path_png = self.output_dir / f"custom_bar_chart_{timestamp}.png"

            # Save figure with default and custom parameters
            fig.savefig(output_path_png)
            fig.savefig(output_path_png.with_name(f"custom_bar_chart_facecolor_{timestamp}.png"), facecolor='y', bbox_inches="tight", pad_inches=0.3, transparent=True)

            logger.info(f"Custom Matplotlib bar charts saved successfully at {output_path_png} and {output_path_png.with_name(f'custom_bar_chart_facecolor_{timestamp}.png')}")
            plt.close(fig)

            return str(output_path_png)
        except Exception as e:
            logger.error(f"Error while creating custom Matplotlib bar chart: {str(e)}")
            raise

    def generate_report_with_images(self, image_paths: list, output_pdf: str) -> None:
        try:
            logger.info(f"Starting report generation with images...")
            doc = SimpleDocTemplate(output_pdf, pagesize=letter)
            elements = []

            for img_path in image_paths:
                elements.append(Image(img_path, width=400, height=300))  # Adjust size as needed
                elements.append(Paragraph("<br/><br/>", color=colors.white))  # Add space between images if needed

            # Add other elements to the document (text, tables, etc.)
            doc.build(elements)

            logger.info(f"Report generated successfully at {output_pdf}")
        except Exception as e:
            logger.error(f"Error while generating report with images: {str(e)}")
            raise
