# Advanced GenAI RAG System

This project implements an advanced Retrieval-Augmented Generation (RAG) system that supports multiple LLM models, data sources, and file types. It's built using LlamaIndex and Gradio, providing a user-friendly interface for interacting with different language models while leveraging various data sources for context-aware responses.

## Features

- **Multiple LLM Models Support**:
  - Local models via Ollama (phi, llama2, codellama)
  - API-based models (GPT-3.5-turbo, GPT-4)

- **Multiple Data Sources**:
  - MongoDB Atlas Vector Search
  - MySQL database
  - File-based input (PDF, CSV, logs)

- **Interactive Web Interface**:
  - Model selection dropdown
  - Data source selection
  - File upload capability
  - Real-time chat interface

## Prerequisites

- Python 3.8+
- Ollama (for local models)
- MongoDB Atlas account (for vector search)
- MySQL server (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/advanced-genai-rag.git
cd advanced-genai-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export MONGODB_URL="your_mongodb_url"
export MONGODB_DBNAME="your_database_name"
export MYSQL_HOST="your_mysql_host"
export MYSQL_USER="your_mysql_user"
export MYSQL_PASSWORD="your_mysql_password"
export MYSQL_DATABASE="your_mysql_database"
export OPENAI_API_KEY="your_openai_api_key"  # If using OpenAI models
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:7860`

3. Select your preferred:
   - Model type (local/API)
   - Specific model
   - Data source
   - Upload files (if using file-based input)

4. Start chatting with the model

## Project Structure

```
advanced-genai-rag/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables (create from .env.example)
└── README.md            # Project documentation
```

## Configuration

The application can be configured through environment variables or by modifying the config dictionary in `app.py`. Key configurations include:

- Database connections (MongoDB, MySQL)
- Model settings
- Embedding model selection
- Vector search parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- LlamaIndex team for their excellent framework
- Gradio team for the user interface components
- Ollama project for local model support

## References

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [MongoDB Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/)
