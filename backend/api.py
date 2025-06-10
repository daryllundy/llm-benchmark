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

app = FastAPI(title="LLM Benchmark API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    return {"message": "LLM Benchmark API", "version": "1.0.0"}

@app.get("/models")
async def get_models():
    """Get list of available Ollama models"""
    try:
        models = get_benchmark_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    
    return {"benchmark_id": benchmark_id, "status": "started"}

async def run_benchmark_task(benchmark_id: str, request: BenchmarkRequest):
    """Run benchmark in background task"""
    try:
        model_names = get_benchmark_models(request.skip_models)
        total_models = len(model_names)
        total_prompts = len(request.prompts)
        total_tests = total_models * total_prompts
        completed_tests = 0
        
        benchmark_results[benchmark_id]["models_tested"] = model_names
        results = {}
        
        for model_name in model_names:
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
    return {"message": "Benchmark deleted"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        models = ollama.list()
        return {
            "status": "healthy",
            "ollama_connected": True,
            "models_available": len(models.get("models", []))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
