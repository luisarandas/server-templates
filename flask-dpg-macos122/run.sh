#!/bin/bash

# Flask + DearPyGUI Server Runner
# Simple script to run the integrated server

echo "Flask + DearPyGUI Server"
echo "========================"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one"
    python3 -m venv venv
fi

echo "Activating virtual environment"
source venv/bin/activate

echo "Checking dependencies"
python -c "import flask, dearpygui" 2>/dev/null || {
    echo "Installing dependencies"
    pip install -r requirements.txt
}

echo "Starting Flask + DearPyGUI server"
echo "Web interface: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python app.py
