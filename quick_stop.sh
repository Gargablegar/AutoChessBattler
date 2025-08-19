#!/bin/bash
# Quick shutdown script for AutoChess network processes
# This is a simplified version of end_server.sh for fast cleanup

echo "🛑 Quick AutoChess Shutdown..."

# Kill all AutoChess processes immediately
pkill -f "network_server.py" 2>/dev/null
pkill -f "network_client.py" 2>/dev/null  
pkill -f "main.py" 2>/dev/null

# Free up the default port
lsof -ti:8765 | xargs kill -9 2>/dev/null

echo "✅ All AutoChess processes stopped!"
