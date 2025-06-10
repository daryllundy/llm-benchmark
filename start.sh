#!/bin/bash

# LLM Benchmark Tool - Quick Start Script
# This script helps you get started with the Docker setup quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from template"
        else
            print_warning ".env.example not found, creating basic .env file"
            cat > .env << EOL
OLLAMA_HOST=http://ollama:11434
REACT_APP_API_URL=http://localhost:8000
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
EOL
        fi
    else
        print_status ".env file already exists, skipping..."
    fi
}

# Function to check available ports
check_ports() {
    print_status "Checking if required ports are available..."
    
    ports=(3000 8000 11434)
    for port in "${ports[@]}"; do
        if lsof -ti:$port >/dev/null 2>&1; then
            print_error "Port $port is already in use. Please stop the service using this port or change the configuration."
            exit 1
        fi
    done
    
    print_success "All required ports are available!"
}

# Function to start services
start_services() {
    local mode=$1
    
    if [ "$mode" = "dev" ]; then
        print_status "Starting development environment..."
        docker-compose -f docker-compose.dev.yml up -d
    else
        print_status "Starting production environment..."
        docker-compose up -d
    fi
}

# Function to wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for frontend
    print_status "Waiting for frontend to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Frontend failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for ollama
    print_status "Waiting for Ollama to be ready..."
    for i in {1..60}; do
        if curl -f http://localhost:11434/api/version >/dev/null 2>&1; then
            print_success "Ollama is ready!"
            break
        fi
        if [ $i -eq 60 ]; then
            print_warning "Ollama might take longer to start. You can check manually with: docker-compose logs ollama"
            break
        fi
        sleep 1
    done
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  Backend Docs: http://localhost:8000/docs"
    echo "  Ollama API: http://localhost:11434"
    
    echo ""
    print_status "Health checks:"
    echo -n "  Backend: "
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "  Frontend: "
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "  Ollama: "
    if curl -f http://localhost:11434/api/version >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
}

# Function to download sample models
download_models() {
    print_status "Downloading sample models (this may take a while)..."
    
    models=("llama3" "mistral" "codellama:7b")
    
    for model in "${models[@]}"; do
        print_status "Downloading $model..."
        if docker-compose exec -T ollama ollama pull "$model"; then
            print_success "Downloaded $model"
        else
            print_warning "Failed to download $model (you can download it later)"
        fi
    done
}

# Function to show help
show_help() {
    echo "LLM Benchmark Tool - Quick Start Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start       Start the application (default)"
    echo "  dev         Start in development mode"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  models      Download sample models"
    echo "  clean       Clean up containers and volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  --skip-models    Skip downloading sample models"
    echo "  --no-wait        Don't wait for services to be ready"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start production environment"
    echo "  $0 dev                # Start development environment"
    echo "  $0 start --skip-models # Start without downloading models"
    echo "  $0 logs backend       # Show backend logs"
}

# Main script logic
main() {
    local command=${1:-start}
    local skip_models=false
    local no_wait=false
    
    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-models)
                skip_models=true
                shift
                ;;
            --no-wait)
                no_wait=true
                shift
                ;;
            *)
                # Unknown option
                shift
                ;;
        esac
    done
    
    case $command in
        start)
            check_prerequisites
            setup_environment
            check_ports
            start_services
            if [ "$no_wait" != true ]; then
                wait_for_services
            fi
            if [ "$skip_models" != true ]; then
                download_models
            fi
            show_status
            print_success "LLM Benchmark Tool is ready! Open http://localhost:3000 in your browser."
            ;;
        dev)
            check_prerequisites
            setup_environment
            check_ports
            start_services dev
            if [ "$no_wait" != true ]; then
                wait_for_services
            fi
            show_status
            print_success "Development environment is ready! Open http://localhost:3000 in your browser."
            ;;
        stop)
            print_status "Stopping services..."
            docker-compose down
            print_success "Services stopped!"
            ;;
        restart)
            print_status "Restarting services..."
            docker-compose restart
            wait_for_services
            show_status
            print_success "Services restarted!"
            ;;
        status)
            show_status
            ;;
        logs)
            service=${2:-}
            if [ -n "$service" ]; then
                docker-compose logs -f "$service"
            else
                docker-compose logs -f
            fi
            ;;
        models)
            download_models
            ;;
        clean)
            print_warning "This will remove all containers, networks, and volumes. Are you sure? [y/N]"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                print_status "Cleaning up..."
                docker-compose down -v --rmi local
                print_success "Cleanup complete!"
            else
                print_status "Cleanup cancelled."
            fi
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
