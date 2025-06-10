import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [models, setModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState(new Set());
  const [prompts, setPrompts] = useState([
    "Why is the sky blue?",
    "Write a report on the financials of Apple Inc."
  ]);
  const [currentBenchmark, setCurrentBenchmark] = useState(null);
  const [benchmarkResults, setBenchmarkResults] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [newPrompt, setNewPrompt] = useState('');

  // Fetch available models on component mount
  useEffect(() => {
    fetchModels();
    checkHealth();
  }, []);

  // Poll for benchmark updates
  useEffect(() => {
    if (currentBenchmark && currentBenchmark.status === 'running') {
      const interval = setInterval(() => {
        fetchBenchmarkResult(currentBenchmark.benchmark_id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [currentBenchmark]);

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      const data = await response.json();
      setModels(data.models);
      // Select all models by default
      setSelectedModels(new Set(data.models));
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setHealth(data);
    } catch (error) {
      console.error('Error checking health:', error);
      setHealth({ status: 'unhealthy', ollama_connected: false });
    }
  };

  const startBenchmark = async () => {
    if (prompts.length === 0) {
      alert('Please add at least one prompt');
      return;
    }

    setIsLoading(true);
    try {
      const skipModels = models.filter(model => !selectedModels.has(model));
      const response = await fetch(`${API_BASE_URL}/benchmark`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompts: prompts,
          skip_models: skipModels,
          verbose: false
        }),
      });
      
      const data = await response.json();
      setCurrentBenchmark({ benchmark_id: data.benchmark_id, status: 'running' });
    } catch (error) {
      console.error('Error starting benchmark:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchBenchmarkResult = async (benchmarkId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/benchmark/${benchmarkId}`);
      const data = await response.json();
      setCurrentBenchmark(data);
      
      if (data.status === 'completed') {
        setBenchmarkResults(data.results);
      }
    } catch (error) {
      console.error('Error fetching benchmark result:', error);
    }
  };

  const toggleModelSelection = (model) => {
    const newSelection = new Set(selectedModels);
    if (newSelection.has(model)) {
      newSelection.delete(model);
    } else {
      newSelection.add(model);
    }
    setSelectedModels(newSelection);
  };

  const addPrompt = () => {
    if (newPrompt.trim()) {
      setPrompts([...prompts, newPrompt.trim()]);
      setNewPrompt('');
    }
  };

  const removePrompt = (index) => {
    setPrompts(prompts.filter((_, i) => i !== index));
  };

  const formatChartData = () => {
    if (!benchmarkResults || Object.keys(benchmarkResults).length === 0) return [];
    
    return Object.entries(benchmarkResults).map(([model, results]) => {
      if (!results || results.length === 0) return null;
      
      // Calculate averages
      const avgPromptTs = results.reduce((sum, r) => sum + r.prompt_eval_ts, 0) / results.length;
      const avgResponseTs = results.reduce((sum, r) => sum + r.response_ts, 0) / results.length;
      const avgTotalTs = results.reduce((sum, r) => sum + r.total_ts, 0) / results.length;
      
      return {
        model: model.replace(':latest', ''),
        promptTs: Number(avgPromptTs.toFixed(2)),
        responseTs: Number(avgResponseTs.toFixed(2)),
        totalTs: Number(avgTotalTs.toFixed(2))
      };
    }).filter(Boolean);
  };

  const chartData = formatChartData();

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 LLM Benchmark Tool</h1>
        <div className="health-indicator">
          <span className={`status-dot ${health?.status || 'unknown'}`}></span>
          Ollama: {health?.ollama_connected ? 'Connected' : 'Disconnected'}
          {health?.models_available && ` (${health.models_available} models)`}
        </div>
      </header>

      <div className="main-content">
        <div className="config-section">
          <div className="card">
            <h2>📋 Configuration</h2>
            
            <div className="section">
              <h3>Models ({selectedModels.size} selected)</h3>
              <div className="model-grid">
                {models.map(model => (
                  <label key={model} className="model-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedModels.has(model)}
                      onChange={() => toggleModelSelection(model)}
                    />
                    <span className="model-name">{model}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="section">
              <h3>Prompts ({prompts.length})</h3>
              <div className="prompt-input">
                <input
                  type="text"
                  value={newPrompt}
                  onChange={(e) => setNewPrompt(e.target.value)}
                  placeholder="Add a new prompt..."
                  onKeyPress={(e) => e.key === 'Enter' && addPrompt()}
                />
                <button onClick={addPrompt} disabled={!newPrompt.trim()}>Add</button>
              </div>
              <div className="prompt-list">
                {prompts.map((prompt, index) => (
                  <div key={index} className="prompt-item">
                    <span className="prompt-text">{prompt}</span>
                    <button 
                      className="remove-btn" 
                      onClick={() => removePrompt(index)}
                      title="Remove prompt"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <button 
              className="start-benchmark-btn"
              onClick={startBenchmark}
              disabled={isLoading || selectedModels.size === 0 || prompts.length === 0 || 
                       (currentBenchmark && currentBenchmark.status === 'running')}
            >
              {isLoading ? 'Starting...' : 'Start Benchmark'}
            </button>
          </div>
        </div>

        <div className="results-section">
          {currentBenchmark && (
            <div className="card">
              <h2>📊 Benchmark Progress</h2>
              <div className="progress-info">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${(currentBenchmark.progress || 0) * 100}%` }}
                  ></div>
                </div>
                <div className="progress-text">
                  {(currentBenchmark.progress * 100).toFixed(1)}% Complete
                </div>
              </div>
              
              {currentBenchmark.current_model && (
                <div className="current-model">
                  Currently testing: <strong>{currentBenchmark.current_model}</strong>
                </div>
              )}
              
              <div className="status">
                Status: <span className={`status ${currentBenchmark.status}`}>
                  {currentBenchmark.status}
                </span>
              </div>
            </div>
          )}

          {chartData.length > 0 && (
            <div className="card">
              <h2>📈 Results</h2>
              
              <div className="chart-container">
                <h3>Tokens per Second Comparison</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="promptTs" fill="#8884d8" name="Prompt Eval (t/s)" />
                    <Bar dataKey="responseTs" fill="#82ca9d" name="Response (t/s)" />
                    <Bar dataKey="totalTs" fill="#ffc658" name="Total (t/s)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="results-table">
                <h3>Detailed Results</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Prompt Eval (t/s)</th>
                      <th>Response (t/s)</th>
                      <th>Total (t/s)</th>
                      <th>Avg Total Time (s)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.map(row => {
                      const modelResults = benchmarkResults[row.model + ':latest'] || benchmarkResults[row.model];
                      const avgTotalTime = modelResults ? 
                        (modelResults.reduce((sum, r) => sum + r.total_time, 0) / modelResults.length).toFixed(2) : 
                        'N/A';
                      
                      return (
                        <tr key={row.model}>
                          <td className="model-cell">{row.model}</td>
                          <td>{row.promptTs}</td>
                          <td>{row.responseTs}</td>
                          <td>{row.totalTs}</td>
                          <td>{avgTotalTime}s</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
