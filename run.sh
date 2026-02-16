#!/bin/bash
# Access to MySQL Converter - Linux/Mac Startup Script
# This script activates the virtual environment, installs dependencies, and starts the app

set -e

echo ""
echo "========================================"
echo "Access to MySQL Converter - Startup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# Start the app
echo ""
echo "========================================"
echo "Starting Access to MySQL Converter"
echo "========================================"
echo ""
echo "Server running at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python -m waitress --port=5000 --host=0.0.0.0 backend.app:app
