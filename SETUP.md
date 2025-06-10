# LLM Benchmark Tool - Full Stack Setup Guide

This guide will help you set up both the FastAPI backend and React frontend for the LLM benchmarking tool.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- [Ollama](https://ollama.com/) installed and running
- [uv](https://github.com/astral-sh/uv) (optional, but recommended for Python package management)

## Project Structure

```
llm-benchmark-fullstack/
├── backend/
│   ├── api.py                    # FastAPI backend
│   ├── benchmark.py              # Original benchmark logic
│   ├── requirements-api.txt      # Backend dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── App.css              # Styles
│   │   └── index.js             # React entry point
│   ├── public/
│   │   └── index.html           # HTML template
│   ├── package.json             # Frontend dependencies
│   └── README.md
└── SETUP.md                     # This file
```

## Setup Instructions

### 1. Backend Setup (FastAPI)

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   
   Using uv (recommended):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
   
   Or using standard Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # Using uv
   uv pip install -r requirements-api.txt
   
   # Or using pip
   pip install -r requirements-api.txt
   ```

4. **Make sure Ollama is running:**
   ```bash
   ollama serve
   ```

5. **Start the FastAPI server:**
   ```bash
   # Using uv
   uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
   
   # Or using python directly
   python api.py
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### 2. Frontend Setup (React)

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## Usage Guide

### Starting a Benchmark

1. **Open the web interface** at `http://localhost:3000`

2. **Check the health indicator** in the top right to ensure Ollama is connected

3. **Configure your benchmark:**
   - Select which models to test (all are selected by default)
   - Add custom prompts or use the default ones
   - Click "Start Benchmark"

4. **Monitor progress:**
   - View real-time progress updates
   - See which model is currently being tested
   - Watch the progress bar fill up

5. **View results:**
   - Interactive charts showing tokens per second comparison
   - Detailed results table with performance metrics
   - Export data for further analysis

### API Endpoints

The backend provides several REST endpoints:

- `GET /models` - List available Ollama models
- `POST /benchmark` - Start a new benchmark
- `GET /benchmark/{id}` - Get benchmark results
- `GET /benchmarks` - List all benchmarks
- `DELETE /benchmark/{id}` - Delete benchmark results
- `GET /health` - Health check

### Example API Usage

```bash
# Get available models
curl http://localhost:8000/models

# Start a benchmark
curl -X POST http://localhost:8000/benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["Why is the sky blue?", "Explain quantum computing"],
    "skip_models": [],
    "verbose": false
  }'

# Check benchmark status
curl http://localhost:8000/benchmark/{benchmark_id}
```

## Features

### Backend Features
- **Asynchronous benchmarking** - Non-blocking benchmark execution
- **Real-time progress tracking** - Monitor benchmark progress
- **RESTful API** - Clean API design with proper HTTP methods
- **Error handling** - Robust error handling and logging
- **Health monitoring** - Check Ollama connection status

### Frontend Features
- **Modern React UI** - Clean, responsive design
- **Real-time updates** - Live progress monitoring
- **Interactive charts** - Visual performance comparisons using Recharts
- **Model selection** - Easy model filtering
- **Custom prompts** - Add/remove prompts dynamically
- **Results export** - View detailed performance metrics

## Troubleshooting

### Common Issues

1. **Ollama not connected:**
   - Ensure Ollama is installed and running (`ollama serve`)
   - Check if models are available (`ollama list`)

2. **CORS issues:**
   - The backend is configured to allow requests from `localhost:3000`
   - If running on different ports, update the CORS settings in `api.py`

3. **Port conflicts:**
   - Backend uses port 8000, frontend uses port 3000
   - Change ports in the respective configuration files if needed

4. **Dependencies issues:**
   - Ensure you're using compatible Python/Node.js versions
   - Try clearing package caches and reinstalling

### Performance Tips

1. **Model optimization:**
   - Use smaller models for faster benchmarking
   - Consider using quantized models for better performance

2. **System resources:**
   - Ensure sufficient RAM for running multiple models
   - GPU acceleration will significantly improve performance

3. **Benchmarking:**
   - Use shorter prompts for quicker iterations
   - Start with fewer models to test the setup

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Modify `api.py` to add new endpoints
- Background tasks handle long-running benchmarks

### Frontend Development
- The frontend uses modern React with hooks
- Recharts library provides interactive charts
- CSS Grid and Flexbox for responsive layout

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project extends the original LLM Benchmark tool and maintains the same MIT license.
