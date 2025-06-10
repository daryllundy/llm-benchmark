# 🚀 LLM Benchmark Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.com/)

A comprehensive benchmarking tool for Large Language Models (LLMs) running locally with Ollama. Features both a command-line interface and a modern web application for performance testing and comparison.

## ✨ Features

### 🖥️ Command Line Interface

- **Performance Metrics**: Measure tokens per second for prompt evaluation, response generation, and total throughput
- **Multiple Models**: Test all available Ollama models or select specific ones
- **Custom Prompts**: Use default prompts or provide your own test cases
- **Detailed Statistics**: Get comprehensive timing and token count information
- **Flexible Configuration**: Skip models, adjust verbosity, and customize test parameters

### 🌐 Web Interface

- **Real-time Monitoring**: Live progress tracking with visual progress bars
- **Interactive Charts**: Beautiful visualizations using Recharts for performance comparison
- **Model Management**: Easy selection and deselection of models to test
- **Dynamic Prompts**: Add, remove, and manage test prompts through the UI
- **Health Dashboard**: Monitor Ollama connection status and available models
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Export Ready**: Detailed results tables with performance metrics

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm (for web interface)
- **[Ollama](https://ollama.com/)** installed and running
- **[uv](https://github.com/astral-sh/uv)** (recommended for Python package management)

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/daryllundy/llm-benchmark.git
   cd llm-benchmark
   ```
2. **Start Ollama** (if not already running)

   ```bash
   ollama serve
   ```
3. **Choose your interface:**

   **Option A: Command Line Only**

   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   uv run benchmark.py --verbose
   ```

   **Option B: Full Stack Web Application**

   ```bash
   # Backend setup
   cd backend
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -r requirements-api.txt
   python api.py &

   # Frontend setup (new terminal)
   cd frontend
   npm install
   npm start
   ```
4. **Access the web interface** at `http://localhost:3000`

## 📊 Usage Examples

### Command Line Interface

```bash
# Basic benchmark with default prompts
uv run benchmark.py

# Verbose mode with custom prompts
uv run benchmark.py --verbose --prompts "Explain quantum computing" "Write a Python function"

# Skip specific models
uv run benchmark.py --skip-models llama2:latest dolphin-mistral:7b

# Custom configuration
uv run benchmark.py --verbose \
  --prompts "What is machine learning?" "Describe the solar system" \
  --skip-models model1 model2
```

### Web Interface API

```bash
# Get available models
curl http://localhost:8000/models

# Start a benchmark
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["Why is the sky blue?", "Explain quantum computing"],
    "skip_models": ["llama2:latest"],
    "verbose": false
  }'

# Check benchmark status
curl http://localhost:8000/benchmark/{benchmark_id}

# Health check
curl http://localhost:8000/health
```

## 📈 Sample Output

### Command Line Results

```
Evaluating models: ['llama3:latest', 'dolphin-mistral:latest', 'everythinglm:latest']

Average stats:
----------------------------------------------------
        llama3:latest
                Prompt eval: 150.13 t/s
                Response: 28.50 t/s
                Total: 49.51 t/s

        Stats:
                Prompt tokens: 22
                Response tokens: 20
                Model load time: 5.36s
                Prompt eval time: 0.15s
                Response time: 0.70s
                Total time: 6.21s
----------------------------------------------------
```

### Web Interface Features

- **Interactive Charts**: Bar charts comparing tokens/second across models
- **Real-time Progress**: Live updates during benchmark execution
- **Detailed Tables**: Comprehensive performance metrics
- **Model Selection**: Easy checkbox interface for model filtering
- **Health Monitoring**: Connection status and model availability

## 🏗️ Architecture

### Project Structure

```
llm-benchmark/
├── benchmark.py              # Original CLI tool
├── requirements.txt          # CLI dependencies
├── backend/
│   ├── api.py               # FastAPI backend
│   └── requirements-api.txt # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styling
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # Frontend dependencies
└── README.md               # This file
```

### Technology Stack

- **Backend**: FastAPI, Python, Pydantic, Uvicorn
- **Frontend**: React, Recharts, Modern CSS
- **LLM Engine**: Ollama
- **Package Management**: uv (Python), npm (Node.js)

## 🔧 API Reference

### Endpoints

| Method     | Endpoint            | Description                    |
| ---------- | ------------------- | ------------------------------ |
| `GET`    | `/models`         | List available Ollama models   |
| `POST`   | `/benchmark`      | Start a new benchmark          |
| `GET`    | `/benchmark/{id}` | Get benchmark results          |
| `GET`    | `/benchmarks`     | List all benchmarks            |
| `DELETE` | `/benchmark/{id}` | Delete benchmark results       |
| `GET`    | `/health`         | Health check and Ollama status |

### Request/Response Examples

**Start Benchmark**

```json
POST /benchmark
{
  "prompts": ["Why is the sky blue?"],
  "skip_models": ["model1"],
  "verbose": false
}

Response:
{
  "benchmark_id": "uuid-string",
  "status": "started"
}
```

**Get Results**

```json
GET /benchmark/{id}
{
  "benchmark_id": "uuid-string",
  "status": "completed",
  "progress": 1.0,
  "results": {
    "llama3:latest": [
      {
        "model": "llama3:latest",
        "prompt_eval_ts": 150.13,
        "response_ts": 28.50,
        "total_ts": 49.51,
        ...
      }
    ]
  }
}
```

## 🎯 Performance Tips

1. **Model Optimization**

   - Use quantized models for better performance
   - Start with smaller models for initial testing
   - Consider GPU acceleration for faster inference
2. **System Requirements**

   - Ensure sufficient RAM (8GB+ recommended)
   - SSD storage for faster model loading
   - GPU with adequate VRAM for larger models
3. **Benchmarking Best Practices**

   - Use consistent prompts across tests
   - Allow models to warm up before formal benchmarking
   - Test multiple prompt lengths for comprehensive results

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Add features, fix bugs, improve documentation
4. **Test thoroughly**: Ensure both CLI and web interfaces work
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Submit a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/llm-benchmark.git
cd llm-benchmark

# Set up development environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r backend/requirements-api.txt

# Install frontend dependencies
cd frontend
npm install
```

## 📋 Roadmap

- [ ] **Export Functionality**: CSV/JSON export of benchmark results
- [ ] **Historical Tracking**: Store and compare benchmark results over time
- [ ] **Custom Metrics**: User-defined performance measurements
- [ ] **Batch Processing**: Queue multiple benchmark jobs
- [ ] **Model Comparison**: Side-by-side detailed comparisons
- [ ] **Cloud Integration**: Support for cloud-based LLM services

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Issues**

```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve
```

**Port Conflicts**

- Backend runs on port 8000
- Frontend runs on port 3000
- Modify ports in configuration files if needed

**CORS Issues**

- Ensure backend CORS settings allow frontend origin
- Check browser console for detailed error messages

**Dependencies**

```bash
# Clear and reinstall Python packages
uv pip freeze | uv pip uninstall -r /dev/stdin
uv pip install -r requirements.txt

# Clear and reinstall Node packages
rm -rf node_modules package-lock.json
npm install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Ollama](https://ollama.com/)** for providing the local LLM infrastructure
- **[FastAPI](https://fastapi.tiangolo.com/)** for the excellent API framework
- **[React](https://reactjs.org/)** and **[Recharts](https://recharts.org/)** for the frontend framework and charting
- **[uv](https://github.com/astral-sh/uv)** for modern Python package management

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/daryllundy/llm-benchmark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/daryllundy/llm-benchmark/discussions)
- **Documentation**: Check the `/docs` folder for detailed guides

---

**Made with ❤️ for the LLM community**
