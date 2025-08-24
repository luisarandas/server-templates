#!/bin/bash

# FastAPI Web Server Build Script for macOS
# This script sets up a clean Python virtual environment and runs the FastAPI server

set -e  # Exit on any error

echo "FastAPI Web Server Setup for macOS"
echo "======================================"
echo "Clean template for file handling and static file serving"

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

# Check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Found Python: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version)
        print_success "Found Python: $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip is not available. Please install pip first."
        exit 1
    fi
}

# Create virtual environment if it doesn't exist
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created successfully"
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Verify activation
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip
    print_success "pip upgraded successfully"
}

# Install requirements
install_requirements() {
    if [ -f "requirements.txt" ]; then
        print_status "Installing requirements from requirements.txt..."
        $PIP_CMD install -r requirements.txt
        print_success "Requirements installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Check if all required packages are installed
verify_installation() {
    print_status "Verifying installation..."
    
    # Check key packages
    python -c "import fastapi" 2>/dev/null && print_success "FastAPI installed" || print_error "FastAPI not found"
    python -c "import uvicorn" 2>/dev/null && print_success "Uvicorn installed" || print_error "Uvicorn not found"
    python -c "import PIL" 2>/dev/null && print_success "Pillow installed" || print_error "Pillow not found"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p images uploads media
    print_success "Directories created successfully"
}

# Run the server
run_server() {
    print_status "Starting FastAPI server..."
    echo ""
    echo "Server will be available at: http://localhost:8000"
    echo "API documentation at: http://localhost:8000/docs"
    echo "Upload and serve files with this clean FastAPI server!"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python app.py
}

# Main execution
main() {
    print_status "Starting setup process..."
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup environment
    setup_venv
    activate_venv
    upgrade_pip
    install_requirements
    verify_installation
    create_directories
    
    # Run server
    run_server
}

# Handle script interruption
trap 'echo ""; print_warning "Setup interrupted by user"; exit 1' INT

# Run main function
main

