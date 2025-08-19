#!/bin/bash
# End AutoChess Network Server and Clients
# This script gracefully shuts down all running AutoChess network processes

echo "🛑 Shutting down AutoChess Network Processes..."
echo ""

# Function to check if a process is running
check_process() {
    local process_name="$1"
    local count=$(pgrep -f "$process_name" | wc -l)
    echo "$count"
}

# Function to kill processes gracefully
kill_processes() {
    local process_name="$1"
    local description="$2"
    
    local pids=$(pgrep -f "$process_name")
    
    if [ -n "$pids" ]; then
        echo "📱 Found $description processes: $pids"
        
        # First try graceful shutdown (SIGTERM)
        echo "   Sending SIGTERM to $description..."
        for pid in $pids; do
            kill -TERM "$pid" 2>/dev/null
        done
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Check if any are still running
        local remaining_pids=$(pgrep -f "$process_name")
        if [ -n "$remaining_pids" ]; then
            echo "   Some processes still running, sending SIGKILL..."
            for pid in $remaining_pids; do
                kill -KILL "$pid" 2>/dev/null
            done
            sleep 1
        fi
        
        # Final check
        local final_pids=$(pgrep -f "$process_name")
        if [ -z "$final_pids" ]; then
            echo "   ✅ $description stopped successfully"
        else
            echo "   ⚠️  Some $description processes may still be running: $final_pids"
        fi
    else
        echo "   ℹ️  No $description processes found"
    fi
}

# Function to show running processes before shutdown
show_running_processes() {
    echo "🔍 Checking for running AutoChess processes..."
    
    local server_count=$(check_process "network_server.py")
    local client_count=$(check_process "network_client.py")
    local main_count=$(check_process "main.py")
    
    echo "   AutoChess Servers: $server_count"
    echo "   AutoChess Clients: $client_count" 
    echo "   AutoChess Main Games: $main_count"
    echo ""
    
    if [ "$server_count" -eq 0 ] && [ "$client_count" -eq 0 ] && [ "$main_count" -eq 0 ]; then
        echo "ℹ️  No AutoChess processes are currently running."
        echo ""
        return 1
    fi
    
    return 0
}

# Function to show final status
show_final_status() {
    echo ""
    echo "🔍 Final process check..."
    
    local server_count=$(check_process "network_server.py")
    local client_count=$(check_process "network_client.py")
    local main_count=$(check_process "main.py")
    
    echo "   AutoChess Servers: $server_count"
    echo "   AutoChess Clients: $client_count"
    echo "   AutoChess Main Games: $main_count"
    
    if [ "$server_count" -eq 0 ] && [ "$client_count" -eq 0 ] && [ "$main_count" -eq 0 ]; then
        echo ""
        echo "✅ All AutoChess processes have been stopped successfully!"
    else
        echo ""
        echo "⚠️  Some processes may still be running. You can manually kill them with:"
        echo "   kill -9 \$(pgrep -f 'network_server.py|network_client.py|main.py')"
    fi
}

# Parse command line arguments
FORCE_KILL=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_KILL=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Gracefully shutdown all AutoChess network processes"
            echo ""
            echo "Options:"
            echo "  -f, --force    Use SIGKILL immediately instead of graceful shutdown"
            echo "  -q, --quiet    Suppress output (except errors)"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0             # Graceful shutdown"
            echo "  $0 --force     # Force kill all processes"
            echo "  $0 --quiet     # Silent shutdown"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Redirect output if quiet mode
if [ "$QUIET" = true ]; then
    exec > /dev/null
fi

# Main execution
if ! show_running_processes; then
    exit 0
fi

# Kill network servers
echo "🖥️  Shutting down AutoChess Network Servers..."
if [ "$FORCE_KILL" = true ]; then
    pkill -KILL -f "network_server.py" 2>/dev/null
    echo "   ✅ Force killed all servers"
else
    kill_processes "network_server.py" "Network Servers"
fi

# Kill network clients
echo ""
echo "📱 Shutting down AutoChess Network Clients..."
if [ "$FORCE_KILL" = true ]; then
    pkill -KILL -f "network_client.py" 2>/dev/null
    echo "   ✅ Force killed all clients"
else
    kill_processes "network_client.py" "Network Clients"
fi

# Kill any running main.py instances (single-player games)
echo ""
echo "🎮 Shutting down AutoChess Main Games..."
if [ "$FORCE_KILL" = true ]; then
    pkill -KILL -f "main.py" 2>/dev/null
    echo "   ✅ Force killed all main games"
else
    kill_processes "main.py" "Main Games"
fi

# Also kill any Python processes that might be running our game
echo ""
echo "🐍 Checking for additional Python AutoChess processes..."
if [ "$FORCE_KILL" = true ]; then
    pkill -KILL -f "python.*AutoChess" 2>/dev/null
    echo "   ✅ Force killed additional processes"
else
    kill_processes "python.*AutoChess" "Additional AutoChess processes"
fi

# Free up the default ports
echo ""
echo "🔌 Checking for processes using AutoChess ports..."

# Check for processes using port 8765 (default server port)
local port_8765_pid=$(lsof -ti:8765 2>/dev/null)
if [ -n "$port_8765_pid" ]; then
    echo "   Found process using port 8765: $port_8765_pid"
    if [ "$FORCE_KILL" = true ]; then
        kill -KILL "$port_8765_pid" 2>/dev/null
        echo "   ✅ Force killed process on port 8765"
    else
        kill -TERM "$port_8765_pid" 2>/dev/null
        sleep 1
        if kill -0 "$port_8765_pid" 2>/dev/null; then
            kill -KILL "$port_8765_pid" 2>/dev/null
        fi
        echo "   ✅ Freed port 8765"
    fi
else
    echo "   ℹ️  Port 8765 is free"
fi

# Show final status
show_final_status

echo ""
echo "🎯 AutoChess shutdown complete!"
echo ""
echo "To start new games:"
echo "   ./start_server.sh    # Start network server"
echo "   ./start_client.sh    # Start network client"
echo "   python main.py       # Start single-player game"
