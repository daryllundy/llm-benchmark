# 🐳 Docker Setup Guide

This guide covers running the LLM Benchmark Tool using Docker for both development and production environments.

## 🚀 Quick Start

### Production (Recommended for Users)

```bash
# Clone the repository
git clone https://github.com/daryllundy/llm-benchmark.git
cd llm-benchmark

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access the application at `http://localhost:3000`

### Development (For Contributors)

```bash
# Clone the repository
git clone https://github.com/daryllundy/llm-benchmark.git
cd llm-benchmark

# Copy environment template and configure for development
cp .env.example .env

# Start development environment with hot reloading
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

## 📋 Prerequisites

- **Docker Engine** 20.10+ 
- **Docker Compose** 2.0+
- **Available Ports**: 3000 (frontend), 8000 (backend), 11434 (ollama)
- **Resources**: 4GB+ RAM recommended, 8GB+ for larger models

### GPU Support (Optional)

For NVIDIA GPU acceleration:

```bash
# Install NVIDIA Docker runtime
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Uncomment GPU sections in docker-compose.yml
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Ollama      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (LLM Engine)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 11434   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
llm-benchmark/
├── docker-compose.yml              # Production configuration
├── docker-compose.dev.yml         # Development configuration
├── .env.example                   # Environment template
├── backend/
│   ├── Dockerfile                 # Production backend image
│   ├── Dockerfile.dev             # Development backend image
│   ├── .dockerignore             # Backend build exclusions
│   └── ...
├── frontend/
│   ├── Dockerfile                # Production frontend image
│   ├── Dockerfile.dev            # Development frontend image
│   ├── nginx.conf                # Nginx configuration
│   ├── .dockerignore            # Frontend build exclusions
│   └── ...
└── DOCKER.md                     # This file
```

## 🛠️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Key configurations
OLLAMA_HOST=http://ollama:11434
REACT_APP_API_URL=http://localhost:8000
ENVIRONMENT=production
```

### Ollama Models

Download models after starting:

```bash
# Enter ollama container
docker-compose exec ollama bash

# Download models
ollama pull llama3
ollama pull mistral
ollama pull codellama

# List available models
ollama list
```

## 🔧 Management Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Check status
docker-compose ps
```

### Service-Specific Commands

```bash
# Backend only
docker-compose up -d backend

# Frontend only
docker-compose up -d frontend

# Ollama only
docker-compose up -d ollama
```

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Rebuild services
docker-compose -f docker-compose.dev.yml up -d --build

# Shell access
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Data Management

```bash
# View volumes
docker volume ls

# Backup ollama data
docker run --rm -v llm-benchmark_ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .

# Restore ollama data
docker run --rm -v llm-benchmark_ollama-data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-backup.tar.gz -C /data

# Clean up everything
docker-compose down -v --rmi all
```

## 🎯 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml llm-benchmark

# Check services
docker service ls
```

### Docker with Reverse Proxy

Using Traefik or Nginx:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.llm-benchmark.rule=Host(`benchmark.yourdomain.com`)"
      - "traefik.http.services.llm-benchmark.loadbalancer.server.port=3000"
```

### Environment-Specific Overrides

```bash
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

## 🔍 Troubleshooting

### Common Issues

**1. Ollama Connection Issues**
```bash
# Check ollama logs
docker-compose logs ollama

# Test ollama directly
curl http://localhost:11434/api/version

# Check ollama from backend
docker-compose exec backend curl http://ollama:11434/api/version
```

**2. Port Conflicts**
```bash
# Check what's using ports
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :11434

# Change ports in docker-compose.yml if needed
```

**3. Memory Issues**
```bash
# Check container memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or use: docker-compose up -d --scale ollama=0  # Disable ollama temporarily
```

**4. Frontend Build Issues**
```bash
# Clear build cache
docker-compose build --no-cache frontend

# Check frontend logs
docker-compose logs frontend
```

**5. Backend API Issues**
```bash
# Check backend health
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend

# Enter backend container for debugging
docker-compose exec backend bash
```

### Performance Optimization

**1. Multi-stage Build Optimization**
```bash
# Build with BuildKit
DOCKER_BUILDKIT=1 docker-compose build

# Use cache mounts
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

**2. Resource Limits**
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Monitoring

```bash
# Container stats
docker stats

# System resource usage
docker system df

# Clean up unused resources
docker system prune -a
```

## 🔐 Security Considerations

### Production Security

1. **Change default secrets**:
   ```bash
   # Generate secure secret key
   openssl rand -hex 32
   ```

2. **Use specific image tags**:
   ```yaml
   image: ollama/ollama:0.1.7  # Instead of :latest
   ```

3. **Limit container privileges**:
   ```yaml
   security_opt:
     - no-new-privileges:true
   ```

4. **Network isolation**:
   ```yaml
   networks:
     - llm-benchmark-network
   ```

### Health Checks

All services include health checks:

```bash
# Check health status
docker-compose ps

# Manual health check
docker-compose exec backend curl -f http://localhost:8000/health
docker-compose exec frontend wget --spider http://localhost:3000
```

## 🚀 Advanced Usage

### Custom Models

```bash
# Mount custom model directory
docker-compose exec ollama bash
ollama create mymodel -f /path/to/Modelfile
```

### Custom Configuration

```bash
# Override configuration
echo "CUSTOM_CONFIG=value" >> .env
docker-compose up -d
```

### Scaling

```bash
# Scale backend replicas
docker-compose up -d --scale backend=3

# Use load balancer (in production)
```

## 📊 Monitoring & Logs

### Centralized Logging

```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Metrics Collection

```bash
# Export metrics
docker-compose exec backend curl http://localhost:8000/metrics
```

This Docker setup provides a complete, production-ready deployment of the LLM Benchmark Tool with excellent developer experience and operational reliability.
