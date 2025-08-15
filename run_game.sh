#!/bin/bash
# AutoChess Game Runner
# This script ensures the virtual environment is always activated before running the game

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ -f "requirements.txt" ]; then
    echo "Installing/updating requirements..."
    pip install -r requirements.txt
fi

# Run the game
echo "Starting AutoChess Game..."
python game.py
