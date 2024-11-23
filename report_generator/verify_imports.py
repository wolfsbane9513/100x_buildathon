
import sys
from typing import Tuple, List

def check_import(import_statement: str) -> Tuple[bool, str]:
    """Try an import and return success/failure with message."""
    try:
        exec(import_statement)
        return True, "Success"
    except Exception as e:
        return False, str(e)

def verify_imports() -> bool:
    """Verify all required imports are working."""
    imports_to_check = [
        # Core LlamaIndex imports
        ("from llama_index import ServiceContext, VectorStoreIndex", "LlamaIndex Core"),
        ("from llama_index.llms import OpenAI", "LlamaIndex LLMs"),
        ("from llama_index.tools import QueryEngineTool, ToolMetadata", "LlamaIndex Tools"),
        ("from llama_index.indices.query.base import BaseQueryEngine", "LlamaIndex Query Engine"),
        
        # LangChain imports
        ("from langchain.agents import Tool, AgentExecutor", "LangChain Agents"),
        ("from langchain.chains import LLMChain", "LangChain Chains"),
        
        # Other dependencies
        ("import gradio as gr", "Gradio"),
        ("import pandas as pd", "Pandas"),
        ("import numpy as np", "NumPy"),
        ("import plotly.express as px", "Plotly"),
        ("from dotenv import load_dotenv", "Python-dotenv")
    ]
    
    print("Verifying imports...")
    print("-" * 50)
    
    all_success = True
    for import_stmt, description in imports_to_check:
        success, message = check_import(import_stmt)
        status = "✓" if success else "✗"
        print(f"{status} {description}")
        if not success:
            print(f"  Error: {message}")
            all_success = False
        
    print("-" * 50)
    if all_success:
        print("\nAll imports verified successfully! ✓")
    else:
        print("\nSome imports failed. Please check the errors above. ✗")
    
    return all_success

def verify_package_versions() -> None:
    """Verify installed package versions."""
    try:
        import pkg_resources
        
        required_packages = {
            'llama-index': '0.9.3',
            'openai': '1.12.0',
            'langchain': '0.0.316',
            'gradio': '4.0.0',
            'pandas': '2.0.0',
            'numpy': '1.24.0'
        }
        
        print("\nChecking package versions:")
        print("-" * 50)
        
        for package, required_version in required_packages.items():
            try:
                installed_version = pkg_resources.get_distribution(package).version
                status = "✓" if installed_version >= required_version else "!"
                print(f"{status} {package}: {installed_version} (required: >={required_version})")
            except pkg_resources.DistributionNotFound:
                print(f"✗ {package}: Not installed (required: >={required_version})")
                
    except Exception as e:
        print(f"Error checking package versions: {str(e)}")

if __name__ == "__main__":
    print("Running import verification...\n")
    success = verify_imports()
    
    print("\nChecking package versions...")
    verify_package_versions()
    
    if not success:
        sys.exit(1)
