#!/bin/bash
# Start AutoChess Network Server

echo "Starting AutoChess Network Server..."
echo "Players can connect by running: python network_client.py"
echo "Press Ctrl+C to stop the server"
echo ""

python network_server.py
