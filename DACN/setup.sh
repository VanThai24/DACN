#!/bin/bash
# Automatic Setup Script for DACN Project (Linux/Mac)

echo "====================================="
echo "DACN Project - Automatic Setup"
echo "====================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")/backend_src"

echo "[1/5] Checking Python installation..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "✓ $python_version found"
else
    echo "✗ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo ""
echo "[2/5] Setting up virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "[5/5] Running tests..."
pytest tests/ -v --tb=short
if [ $? -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "⚠ Some tests failed"
fi

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file if needed"
echo "2. Start backend: python -m uvicorn app.main:app --reload"
echo "3. Start AI backend: cd ../AI && python app.py"
echo "4. Visit API docs: http://localhost:8000/docs"
echo ""
