#!/bin/bash
# Start a complete AutoChess multiplayer session
# This script starts the server and opens client windows automatically

echo "🚀 Starting AutoChess Multiplayer Session"
echo "=" * 50

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to start process in new terminal
start_in_terminal() {
    local cmd="$1"
    local title="$2"
    
    if command_exists gnome-terminal; then
        gnome-terminal --title="$title" -- bash -c "$cmd; echo 'Press Enter to close...'; read"
    elif command_exists xterm; then
        xterm -T "$title" -e bash -c "$cmd; echo 'Press Enter to close...'; read" &
    elif command_exists konsole; then
        konsole --title "$title" -e bash -c "$cmd; echo 'Press Enter to close...'; read" &
    else
        echo "⚠️  No terminal emulator found. Please install gnome-terminal, xterm, or konsole"
        echo "   Or manually run: $cmd"
        return 1
    fi
}

# Parse arguments
AUTO_START=false
GAME_ID="default"

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--auto)
            AUTO_START=true
            shift
            ;;
        -g|--game)
            GAME_ID="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Start a complete AutoChess multiplayer session"
            echo ""
            echo "Options:"
            echo "  -a, --auto         Auto-start both clients (no prompts)"
            echo "  -g, --game ID      Specify game room ID (default: 'default')"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "This script will:"
            echo "  1. Start the network server"
            echo "  2. Open first client window (White player)"
            echo "  3. Open second client window (Black player)"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if server is already running
if pgrep -f "network_server.py" > /dev/null; then
    echo "⚠️  AutoChess server is already running"
    echo "   Use ./check_status.sh to see current processes"
    echo "   Use ./end_server.sh to stop existing processes first"
    exit 1
fi

# Start the server
echo "🖥️  Starting AutoChess Network Server..."
start_in_terminal "./start_server.sh" "AutoChess Server"

# Wait a moment for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server started successfully
if ! pgrep -f "network_server.py" > /dev/null; then
    echo "❌ Failed to start server. Check server terminal for errors."
    exit 1
fi

echo "✅ Server started successfully"

# Start first client (White player)
if [ "$AUTO_START" = true ]; then
    echo "🎮 Starting White Player client..."
    start_in_terminal "./start_client.sh --game $GAME_ID" "AutoChess - White Player"
    sleep 2
else
    echo ""
    echo "🎮 Ready to start clients!"
    echo "Press Enter to start White Player client..."
    read
    start_in_terminal "./start_client.sh --game $GAME_ID" "AutoChess - White Player"
fi

# Start second client (Black player)
if [ "$AUTO_START" = true ]; then
    echo "🎮 Starting Black Player client..."
    start_in_terminal "./start_client.sh --game $GAME_ID" "AutoChess - Black Player"
else
    echo ""
    echo "Press Enter to start Black Player client..."
    read
    start_in_terminal "./start_client.sh --game $GAME_ID" "AutoChess - Black Player"
fi

echo ""
echo "🎉 AutoChess Multiplayer Session Started!"
echo ""
echo "Windows opened:"
echo "   📟 Server Terminal (running network_server.py)"
echo "   🎮 White Player (first client window)"
echo "   🎮 Black Player (second client window)"
echo ""
echo "Game Info:"
echo "   🏠 Server: localhost:8765"
echo "   🏷️  Game ID: $GAME_ID"
echo ""
echo "Management:"
echo "   ./check_status.sh    # Check process status"
echo "   ./end_server.sh      # Stop all processes"
echo ""
echo "Have fun playing AutoChess! 🎯"
