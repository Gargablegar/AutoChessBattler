#!/bin/bash
# Check status of AutoChess network processes

echo "🔍 AutoChess Process Status"
echo "=" * 40

# Function to get process info
get_process_info() {
    local pattern="$1"
    local description="$2"
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null)
    local count=$(echo "$pids" | grep -c '^' 2>/dev/null || echo "0")
    
    if [ "$count" -gt 0 ] && [ -n "$pids" ]; then
        echo "📊 $description: $count running"
        for pid in $pids; do
            local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
            local mem=$(ps -p "$pid" -o rss= 2>/dev/null | tr -d ' ')
            local cpu=$(ps -p "$pid" -o %cpu= 2>/dev/null | tr -d ' ')
            echo "   PID $pid: CPU $cpu%, Memory ${mem}KB"
            echo "   Command: $cmd"
        done
    else
        echo "📊 $description: 0 running"
    fi
    echo ""
}

# Check different types of processes
get_process_info "network_server.py" "Network Servers"
get_process_info "network_client.py" "Network Clients"  
get_process_info "main.py" "Single-player Games"

# Check port usage
echo "🔌 Port Usage:"
local port_8765=$(lsof -ti:8765 2>/dev/null)
if [ -n "$port_8765" ]; then
    echo "   Port 8765: In use by PID $port_8765"
    local cmd=$(ps -p "$port_8765" -o cmd= 2>/dev/null)
    echo "   Command: $cmd"
else
    echo "   Port 8765: Available"
fi
echo ""

# Check total AutoChess processes
local total_pids=$(pgrep -f "network_server.py|network_client.py|main.py" 2>/dev/null)
local total_count=$(echo "$total_pids" | grep -c '^' 2>/dev/null || echo "0")

if [ "$total_count" -gt 0 ] && [ -n "$total_pids" ]; then
    echo "📈 Total AutoChess processes: $total_count"
    echo "💾 Total memory usage: $(ps -p $(echo $total_pids | tr '\n' ',') -o rss= 2>/dev/null | awk '{sum+=$1} END {print sum}')KB"
else
    echo "📈 Total AutoChess processes: 0"
fi

echo ""
echo "🎮 Management Commands:"
echo "   ./start_server.sh    # Start network server"
echo "   ./start_client.sh    # Start network client"
echo "   ./end_server.sh      # Stop all processes"
echo "   ./quick_stop.sh      # Quick stop all processes"
