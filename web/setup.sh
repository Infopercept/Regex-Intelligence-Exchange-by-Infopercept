#!/bin/bash

# Setup script for Regex Intelligence Exchange Web Application

echo "Setting up Regex Intelligence Exchange Web Application..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo ""
echo "For development:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run with debug mode: python run.py --debug"