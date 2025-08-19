# AutoChess Network Multiplayer Guide

This guide explains how to set up and play AutoChess as a networked multiplayer game where each player gets their own window.

## Architecture Overview

The networked version consists of three main components:

1. **Game Server** (`network_server.py`) - Manages authoritative game state
2. **Game Client** (`network_client.py`) - Player-specific game windows
3. **Network Protocol** - WebSocket-based communication

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
./start_server.sh
# Or manually: python network_server.py
```

The server will start on `localhost:8765` by default.

### 3. Start Client Windows

Open **two separate terminals** and run:

**Terminal 1 (Player 1):**
```bash
./start_client.sh
# Or manually: python network_client.py
```

**Terminal 2 (Player 2):**
```bash
./start_client.sh
# Or manually: python network_client.py
```

The first client becomes the **White** player, the second becomes the **Black** player.

### 4. Stop All Processes

When you're done playing, you can cleanly shut down all network processes:

```bash
./end_server.sh
# Or for quick shutdown: ./quick_stop.sh
```

## How Network Play Works

### Player Windows
- Each player gets their own dedicated game window
- Players can only interact with their own pieces and side panel
- Both players see the same board state, updated in real-time
- Window titles show player color: "AutoChess - White Player" / "AutoChess - Black Player"

### Synchronized Actions
- **Piece Placement**: Click your pieces in the side panel, then click the board to place
- **Turn Progression**: Either player can click "Play Turn" to advance the game
- **Behavior Setting**: Click your placed pieces to set their behaviors
- **Real-time Updates**: All actions are immediately synchronized between clients

### Network Features
- **Connection Status**: Shows "Connected", "Connecting...", or "Disconnected" in top-right
- **Player Identification**: Window title and UI indicate which player you are
- **Error Handling**: Network errors and invalid moves are displayed clearly
- **Game Rooms**: Multiple games can run simultaneously using different game IDs

## Advanced Usage

### Custom Server Configuration

```bash
# Start server on different host/port
python network_server.py --host 0.0.0.0 --port 9000
```

### Connect to Remote Server

```bash
# Connect to server on different machine
python network_client.py --host 192.168.1.100 --port 9000
```

### Multiple Game Rooms

```bash
# Start clients in different game rooms
python network_client.py --game room1
python network_client.py --game room2
```

### Shutdown Scripts

**Graceful Shutdown:**
```bash
./end_server.sh           # Graceful shutdown with status reporting
./end_server.sh --force   # Force kill all processes immediately
./end_server.sh --quiet   # Silent shutdown
```

**Quick Shutdown:**
```bash
./quick_stop.sh           # Fast shutdown for development
```

### Management Scripts

**Complete Session Management:**
```bash
./start_multiplayer.sh     # Start server + both clients automatically
./start_multiplayer.sh -a  # Auto-start without prompts
./start_multiplayer.sh -g room1  # Start in specific game room
```

**Process Monitoring:**
```bash
./check_status.sh          # Check running processes and resource usage
```

## Network Protocol

The clients and server communicate using JSON messages over WebSockets:

### Client → Server Messages

**Join Game:**
```json
{
  "type": "join_game",
  "game_id": "default"
}
```

**Player Action:**
```json
{
  "type": "player_action",
  "data": {
    "action_type": "place_piece",
    "player_color": "white",
    "data": {
      "piece_type": "Pawn",
      "position": [23, 12]
    }
  }
}
```

### Server → Client Messages

**Player Assignment:**
```json
{
  "type": "player_assignment",
  "data": {
    "client_id": "uuid-string",
    "assigned_color": "white",
    "game_id": "default"
  }
}
```

**Game State Update:**
```json
{
  "type": "game_state_update",
  "data": {
    "board_state": [...],
    "white_points": 25,
    "black_points": 30,
    "current_player": "white",
    "turn_counter": 5,
    "game_over": false,
    "winner": null,
    "error_message": ""
  }
}
```

## Troubleshooting

### Common Issues

**"Could not connect to server"**
- Ensure the server is running: `./start_server.sh`
- Check if the host/port are correct
- Verify firewall settings if connecting remotely

**"module 'websockets.exceptions' has no attribute 'ConnectionRefused'"**
- This indicates an outdated websockets library version
- Update websockets: `pip install --upgrade websockets`
- The minimum required version is websockets>=11.0.0

**"Game is full"**
- The game already has 2 players
- Use a different game room: `--game room2`
- Wait for a player to disconnect

**"Piece placement failed"**
- Ensure you have enough points
- Check that the position is within frontline zones
- Verify the square is empty

**"Network lag or desync"**
- Check network connection stability
- Restart both clients if state becomes inconsistent
- Server maintains authoritative state

### Performance Tips

- Run server and clients on the same machine for best performance
- Use `localhost` instead of IP addresses when possible
- Close unnecessary applications to ensure smooth 60 FPS gameplay

## Game Features in Network Play

All original AutoChess features work in network mode:

- ✅ **Piece Behaviors** (Aggressive, Defensive, Passive)
- ✅ **Frontline System** with visual zones
- ✅ **Point Economy** and piece costs
- ✅ **Auto-turns** for multiple movement rounds
- ✅ **Turn-based Strategy** with real-time placement
- ✅ **Win Conditions** and game over detection
- ✅ **Debug Features** (per-client debug menus)

## Extending the Network System

### Adding Spectator Mode

The server already supports spectator assignment. To implement:
1. Modify `network_client.py` to handle `"spectator"` color assignment
2. Create a read-only spectator UI
3. Allow multiple spectators per game

### Adding Chat System

1. Add chat UI elements to `network_ui.py`
2. Create new message types: `"chat_message"`
3. Implement server-side message broadcasting

### Adding Replay System

1. Log all game actions on the server
2. Create replay file format
3. Build replay viewer client

### Adding Matchmaking

1. Create lobby system in server
2. Queue players for automatic matching
3. Add ranking/ELO system

## Security Considerations

The current implementation is designed for trusted environments. For production use:

- Add authentication/authorization
- Implement rate limiting
- Validate all client inputs server-side
- Use TLS/SSL for encrypted communication
- Add anti-cheat measures

## Performance Scaling

For larger deployments:

- Use Redis for shared game state
- Implement horizontal server scaling
- Add load balancing
- Optimize message serialization
- Use binary protocols instead of JSON

---

**Enjoy your networked AutoChess battles!** 🎮♕
