@echo off
echo Cleaning up old environment...
if exist venv (
    call venv\Scripts\deactivate.bat
    rmdir /s /q venv
)

echo Creating new virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo Installing specific versions of core packages...

:: Install base dependencies first
pip install numpy>=1.24.0
pip install pandas>=2.0.0

:: Install LlamaIndex and related packages
pip install llama-index==0.9.3
pip install langchain==0.0.316
pip install openai>=1.12.0

:: UI and utilities
pip install gradio>=4.0.0
pip install python-dotenv>=1.0.0
pip install plotly>=5.18.0
pip install fpdf
pip install kaleido>=0.2.1

echo Installation complete!
echo Verifying installation...

python -c "from llama_index import ServiceContext; from llama_index.langchain_helpers.agents import create_llama_agent; print('LlamaIndex imports successful')"
python -c "from llama_index.llms import OpenAI; print('OpenAI import successful')"

pause
