#!/bin/bash
set -e

echo "=== Cognitive Triad Simulation ==="

# Check Python
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python is not installed."
        exit 1
    fi
    PYTHON=python3
else
    PYTHON=python
fi

echo "Using: $($PYTHON --version)"

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        echo "Loading API key from .env file..."
        set -a
        # shellcheck disable=SC1091
        source .env
        set +a
    fi
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "Error: OPENAI_API_KEY is not set. Create a .env file or export the variable."
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
$PYTHON -m pip install -r requirements.txt -q

# Create directories
mkdir -p data/alpha data/beta data/gamma analysis csv_export

# Run simulation
echo "Starting simulation..."
$PYTHON main.py "$@"
