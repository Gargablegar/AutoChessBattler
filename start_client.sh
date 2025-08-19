#!/bin/bash
# Start AutoChess Network Client

echo "Starting AutoChess Network Client..."
echo "Connecting to localhost:8765 by default"
echo ""
echo "Usage:"
echo "  ./start_client.sh                    # Connect to localhost"
echo "  ./start_client.sh --host 192.168.1.100  # Connect to specific IP"
echo "  ./start_client.sh --game room1       # Join specific game room"
echo ""

python network_client.py "$@"
