import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import ollama
import logging
from datetime import datetime
import uuid

# Import from your existing benchmark.py
from benchmark import (
    OllamaResponse,
    Message,
    run_benchmark,
    get_benchmark_models,
    nanosec_to_sec
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure ollama client
if OLLAMA_HOST != "http://localhost:11434":
    import ollama
    ollama._client.base_url = OLLAMA_HOST

app = FastAPI(
    title="LLM Benchmark API",
    version="1.0.0",
    description="A comprehensive API for benchmarking Large Language Models with Ollama",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# In-memory storage for benchmark results
benchmark_results: Dict[str, Dict] = {}
active_benchmarks: Dict[str, Dict] = {}

class BenchmarkRequest(BaseModel):
    prompts: List[str] = ["Why is the sky blue?", "Write a report on the financials of Apple Inc."]
    skip_models: List[str] = []
    verbose: bool = False

class BenchmarkStats(BaseModel):
    model: str
    prompt_eval_ts: float
    response_ts: float
    total_ts: float
    prompt_tokens: int
    response_tokens: int
    model_load_time: float
    prompt_eval_time: float
    response_time: float
    total_time: float

class BenchmarkResult(BaseModel):
    benchmark_id: str
    status: str  # "running", "completed", "error"
    progress: float  # 0.0 to 1.0
    models_tested: List[str]
    current_model: Optional[str]
    results: Dict[str, List[BenchmarkStats]]
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

def ollama_response_to_stats(response: OllamaResponse) -> BenchmarkStats:
    """Convert OllamaResponse to BenchmarkStats"""
    prompt_ts = response.prompt_eval_count / nanosec_to_sec(response.prompt_eval_duration)
    response_ts = response.eval_count / nanosec_to_sec(response.eval_duration)
    total_ts = (response.prompt_eval_count + response.eval_count) / nanosec_to_sec(
        response.prompt_eval_duration + response.eval_duration
    )

    return BenchmarkStats(
        model=response.model,
        prompt_eval_ts=prompt_ts,
        response_ts=response_ts,
        total_ts=total_ts,
        prompt_tokens=response.prompt_eval_count,
        response_tokens=response.eval_count,
        model_load_time=nanosec_to_sec(response.load_duration),
        prompt_eval_time=nanosec_to_sec(response.prompt_eval_duration),
        response_time=nanosec_to_sec(response.eval_duration),
        total_time=nanosec_to_sec(response.total_duration)
    )

@app.get("/")
async def root():
    return {
        "message": "LLM Benchmark API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "ollama_host": OLLAMA_HOST
    }

@app.get("/models")
async def get_models():
    """Get list of available Ollama models"""
    try:
        models = get_benchmark_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

@app.post("/benchmark")
async def start_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    """Start a new benchmark"""
    benchmark_id = str(uuid.uuid4())

    # Initialize benchmark result
    benchmark_result = BenchmarkResult(
        benchmark_id=benchmark_id,
        status="running",
        progress=0.0,
        models_tested=[],
        current_model=None,
        results={},
        created_at=datetime.now()
    )

    benchmark_results[benchmark_id] = benchmark_result.dict()

    # Start benchmark in background
    background_tasks.add_task(run_benchmark_task, benchmark_id, request)

    logger.info(f"Started benchmark {benchmark_id} with {len(request.prompts)} prompts")
    return {"benchmark_id": benchmark_id, "status": "started"}

async def run_benchmark_task(benchmark_id: str, request: BenchmarkRequest):
    """Run benchmark in background task"""
    try:
        logger.info(f"Running benchmark task {benchmark_id}")
        model_names = get_benchmark_models(request.skip_models)
        total_models = len(model_names)
        total_prompts = len(request.prompts)
        total_tests = total_models * total_prompts
        completed_tests = 0

        benchmark_results[benchmark_id]["models_tested"] = model_names
        results = {}

        for model_name in model_names:
            logger.info(f"Testing model {model_name}")
            benchmark_results[benchmark_id]["current_model"] = model_name
            model_results = []

            for prompt in request.prompts:
                try:
                    # Run the actual benchmark
                    response = run_benchmark(model_name, prompt, verbose=False)
                    if response:
                        stats = ollama_response_to_stats(response)
                        model_results.append(stats.dict())

                    completed_tests += 1
                    progress = completed_tests / total_tests
                    benchmark_results[benchmark_id]["progress"] = progress
                    logger.debug(f"Benchmark {benchmark_id} progress: {progress:.2%}")

                except Exception as e:
                    logger.error(f"Error benchmarking {model_name} with prompt '{prompt}': {e}")
                    continue

            results[model_name] = model_results

        # Update final results
        benchmark_results[benchmark_id].update({
            "status": "completed",
            "progress": 1.0,
            "results": results,
            "completed_at": datetime.now().isoformat(),
            "current_model": None
        })

        logger.info(f"Completed benchmark {benchmark_id}")

    except Exception as e:
        logger.error(f"Benchmark {benchmark_id} failed: {e}")
        benchmark_results[benchmark_id].update({
            "status": "error",
            "error_message": str(e),
            "completed_at": datetime.now().isoformat()
        })

@app.get("/benchmark/{benchmark_id}")
async def get_benchmark_result(benchmark_id: str):
    """Get benchmark result by ID"""
    if benchmark_id not in benchmark_results:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    return benchmark_results[benchmark_id]

@app.get("/benchmarks")
async def list_benchmarks():
    """List all benchmarks"""
    return {"benchmarks": list(benchmark_results.keys())}

@app.delete("/benchmark/{benchmark_id}")
async def delete_benchmark(benchmark_id: str):
    """Delete benchmark result"""
    if benchmark_id not in benchmark_results:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    del benchmark_results[benchmark_id]
    logger.info(f"Deleted benchmark {benchmark_id}")
    return {"message": "Benchmark deleted"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        models = ollama.list()
        model_count = len(models.get("models", []))

        return {
            "status": "healthy",
            "ollama_connected": True,
            "ollama_host": OLLAMA_HOST,
            "models_available": model_count,
            "environment": ENVIRONMENT,
            "active_benchmarks": len([b for b in benchmark_results.values() if b["status"] == "running"])
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "ollama_host": OLLAMA_HOST,
            "error": str(e),
            "environment": ENVIRONMENT
        }

@app.get("/metrics")
async def get_metrics():
    """Get basic metrics about the service"""
    total_benchmarks = len(benchmark_results)
    completed_benchmarks = len([b for b in benchmark_results.values() if b["status"] == "completed"])
    failed_benchmarks = len([b for b in benchmark_results.values() if b["status"] == "error"])
    running_benchmarks = len([b for b in benchmark_results.values() if b["status"] == "running"])

    return {
        "total_benchmarks": total_benchmarks,
        "completed_benchmarks": completed_benchmarks,
        "failed_benchmarks": failed_benchmarks,
        "running_benchmarks": running_benchmarks,
        "success_rate": completed_benchmarks / total_benchmarks if total_benchmarks > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting LLM Benchmark API in {ENVIRONMENT} mode")
    logger.info(f"Ollama host: {OLLAMA_HOST}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")

    uvicorn.run(
        app,
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=ENVIRONMENT == "development",
        log_level=LOG_LEVEL.lower()
    )
