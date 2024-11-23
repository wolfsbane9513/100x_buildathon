# Intelligent Report Generator

An advanced report generation system powered by LLMs that can process multiple data sources and generate customized reports with visualizations.

![Report Generator Demo](docs/assets/demo.gif) <!-- You would need to add this -->

## 🚀 Features

- **Multiple LLM Support**
  - Local models via Ollama (Mixtral, Llama2, CodeLlama)
  - OpenAI models (GPT-3.5, GPT-4)
  - Anthropic models (Claude-3)

- **Flexible Data Sources**
  - File upload (CSV, Excel, JSON)
  - MongoDB integration
  - MySQL/PostgreSQL support
  - Log file analysis

- **Rich Report Generation**
  - Multiple output formats (PDF, DOCX, HTML)
  - Dynamic visualizations
  - Customizable templates
  - Natural language queries

- **Interactive UI**
  - User-friendly Gradio interface
  - Real-time report generation
  - Connection testing
  - Progress tracking

## 📋 Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- [Ollama](https://ollama.ai/) (for local models)
- MongoDB/MySQL/PostgreSQL (optional, for database support)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/report-generator.git
cd report-generator
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

## 🚦 Getting Started

1. **Start the application**
```bash
python run.py
```

2. **Access the web interface**
```
http://localhost:7860
```

3. **Basic Usage Example**
```python
# Example configuration
model_config = {
    "provider": "local",
    "model": "mixtral"
}

data_config = {
    "source": "file",
    "file": "sales_data.csv"
}

report_config = {
    "query": "Generate monthly sales report with trends",
    "format": "pdf",
    "include_viz": True
}
```

## 📊 Example Reports

### Sales Analysis
![Sales Report Example](docs/assets/sales_report.png) <!-- You would need to add this -->

```python
query = "Generate a quarterly sales report with revenue trends and top-performing products"
```

### Log Analysis
![Log Analysis Example](docs/assets/log_analysis.png) <!-- You would need to add this -->

```python
query = "Analyze error patterns and generate incident report for the last week"
```

## 🏗️ Project Structure

```
report_generator/
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── core/
│   ├── __init__.py
│   ├── agent.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── anthropic_models.py
│   │   ├── openai_models.py
│   │   └── ollama_models.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── connection_manager.py
│   └── tools/
│       ├── __init__.py
│       └── tools.py
├── interface/
│   ├── __init__.py
│   └── app.py
├── .env
├── requirements.txt
└── run.py
```

## 🔧 Configuration

### Environment Variables
```env
# API Keys (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database URLs (optional)
MONGODB_URL=your_mongodb_url
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
```

### Local Models Setup
```bash
# Install Ollama models
ollama pull mixtral
ollama pull llama2
ollama pull codellama
```

## 📝 Usage Examples

### 1. File-based Report Generation
```python
# Upload sales data CSV
# Select local model (mixtral)
# Enter query: "Generate monthly sales report with trends"
# Select PDF format
# Enable visualizations
```

### 2. Database-connected Analysis
```python
# Configure MongoDB connection
# Select OpenAI model
# Enter query: "Analyze customer segments and provide insights"
# Select HTML format
# Enable visualizations
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🚨 Troubleshooting

Common issues and solutions:

1. **Port Conflicts**
```bash
# Change port in run.py
app.launch(server_port=7861)
```

2. **Database Connection Issues**
```python
# Test connection separately
from report_generator.core.data.connection_manager import DatabaseConnectionManager
await manager.test_connection(config)
```

3. **Model Loading Issues**
```bash
# Verify local models
ollama list
```

## 📚 Documentation

- [User Guide](docs/user_guide.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 📖 Citation

```bibtex
@software{report_generator2024,
  author = {Your Name},
  title = {Intelligent Report Generator},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/report-generator}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- Your Name - *Initial work* - [YourGithub](https://github.com/yourusername)

## 🙏 Acknowledgments

- LlamaIndex team for the excellent framework
- Gradio team for the UI components
- Ollama project for local model support

## 🔗 Related Projects

- [LlamaIndex](https://github.com/run-llama/llama_index)
- [Gradio](https://github.com/gradio-app/gradio)
- [Ollama](https://github.com/ollama/ollama)

## 📞 Support

For support, email your-email@example.com or join our [Discord](your-discord-link)