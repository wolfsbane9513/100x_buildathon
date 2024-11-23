# setup.py
from setuptools import setup, find_packages

setup(
    name="report_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-index==0.9.3",
        "llama-index-core==0.10.1",
        "llama-index-llms-openai==0.10.1",
        "llama-index-embeddings-huggingface==0.1.3",
        "llama-index-agents==0.1.0",
        "llama-index-tools==0.1.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "plotly>=5.18.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'black>=23.11.0',
            'isort>=5.12.0',
            'flake8>=6.1.0',
        ],
    }
)