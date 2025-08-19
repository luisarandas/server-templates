#!/bin/bash

# flask-web-macos122 runner script
# Creates local venv and runs Flask app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== flask-web-macos122 ===${NC}"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found. Run this script from flask-web-macos122 directory${NC}"
    exit 1
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Detect Python version (prefer python3, fallback to python)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Using Python 3: $(python3 --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Using Python: $(python --version)${NC}"
else
    echo -e "${RED}Error: No Python found${NC}"
    exit 1
fi

# Create local venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate venv and install requirements
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${YELLOW}Installing/updating requirements...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Check if all required packages are installed
echo -e "${YELLOW}Verifying dependencies...${NC}"
python -c "import flask, flask_socketio; print('✓ Dependencies verified')" 2>/dev/null || {
    echo -e "${RED}Error: Required packages not properly installed${NC}"
    exit 1
}

echo -e "${GREEN}Setup complete! Starting Flask app...${NC}"

# Set Flask environment variables with defaults
export FLASK_APP=app
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5000}
export HOST=${HOST:-0.0.0.0}

echo -e "${BLUE}Environment: ${FLASK_ENV}${NC}"
echo -e "${BLUE}Host: ${HOST}:${PORT}${NC}"

# Graceful shutdown handler
cleanup() {
    echo -e "\n${YELLOW}Shutting down gracefully...${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run the app
echo -e "${GREEN}Starting Flask application...${NC}"
python app.py
