from setuptools import setup, find_packages

setup(
    name="report_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-index-core>=0.10.1",
        "llama-index-llms-openai>=0.10.1",
        "llama-index-llms-anthropic>=0.1.1",
        "llama-index-embeddings-huggingface>=0.1.3",
        "llama-index-callbacks>=0.1.0",
        "gradio>=4.0.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "python-docx>=0.8.11",
        "fpdf2>=2.7.6",
        "plotly>=5.18.0",
        "matplotlib>=3.7.1",
        "fpdf",
    ],
    python_requires=">=3.8",
)
