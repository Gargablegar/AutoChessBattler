# AutoChessBattler Game

A Python chess game with strategic piece placement, point-based economy system, and advanced piece behavior controls.

## Features

### Core Gameplay
- **Configurable board size** (8x8 to 50x50, default 24x24)
- **Point-based piece placement system** with economic strategy
- **Frontline system** - pieces can only be placed within certain zones from kings
- **Turn-based gameplay** with simultaneous piece movement
- **Auto-turns system** - configure multiple movement rounds per turn
- **Real-time movement visualization** with configurable delays

### Piece Behavior System (COMPLETE!)
- **Interactive piece behavior selection** - click any placed piece to set its behavior
- **Three behavior modes** for strategic control:
  - 🗡️ **Aggressive (Swords)**: Piece will prioritize capturing enemy pieces, then hunt enemy kings
  - 🛡️ **Defensive (Shield)**: Piece will protect friendly kings within 5 blocks, prioritizing captures when available  
  - ⏳ **Passive (Hourglass)**: Piece will stay still and not move at all
- **Intelligent behavior logic**:
  - **Aggressive pieces**: Always prioritize captures → move toward enemy kings when no captures available
  - **Defensive pieces**: Always prioritize captures → hold position if within 5 blocks of friendly king → approach friendly king if beyond 5 blocks
  - **Passive pieces**: Never move, providing defensive anchors
- **Visual behavior indicators** - colored dots show each piece's current behavior
- **Behavior icons** appear above clicked pieces with intuitive symbols
- **Smart positioning** - icons automatically adjust to stay visible on screen
- **Automatic reset** - all behaviors return to default after each turn

### Chess Rules & Movement
- **Accurate chess piece movement** following official rules:
  - **King**: One square in any direction (20 points)
  - **Queen**: Any number of squares horizontally, vertically, or diagonally (10 points)
  - **Rook**: Any number of squares horizontally or vertically (5.25 points)
  - **Bishop**: Any number of squares diagonally (3.5 points)
  - **Knight**: L-shaped move, can jump over pieces (3.5 points)
  - **Pawn**: Forward one square (or two on first move), captures diagonally (1 point)

### User Interface
- **Interactive side panels** for piece selection
- **Visual piece affordability** - affordable pieces in white, unaffordable in gray
- **Selected piece highlighting** in yellow
- **Real-time points display** for both players
- **Turn counter** and game status
- **Error messages** and win condition notifications
- **Frontline zone visualization** when placing pieces
- **SVG-based piece graphics** for crisp visuals

### Advanced Features
- **Multiple kings support** - each king creates its own frontline zone
- **Win condition detection** - game ends when one player loses all kings
- **Configurable game parameters** via command line
- **Responsive UI** that adapts to board size
- **Background process support** for smooth gameplay

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start (Recommended)
1. **Clone or download** the project to your local machine
2. **Navigate** to the AutoChessBattler directory:
   ```bash
   cd AutoChessBattler
   ```
3. **Run the game** (automatically sets up virtual environment and installs dependencies):
   ```bash
   ./run_game.sh
   ```

### Manual Setup (Alternative)
If you prefer to set up manually or are on Windows:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv          # On Linux/Mac
   python -m venv venv           # On Windows
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate      # On Linux/Mac
   venv\Scripts\activate         # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**:
   ```bash
   python main.py
   ```

### Important Notes
- **Always use the virtual environment** when running the game
- **Dependencies**: The game requires pygame for graphics and user interface
- **Platform support**: Works on Linux, macOS, and Windows
- **Python version**: Tested with Python 3.7+, recommended Python 3.12+

### Quick Commands
```bash
# Activate venv and run with default settings
source venv/bin/activate && python main.py

# Or use the automated script
./run_game.sh

# Run with custom board size (16x16)
source venv/bin/activate && python main.py 16

# Run with custom settings (board size, frontline, move delay)
source venv/bin/activate && python main.py 20 3 1.0
```

### Network Multiplayer
For networked multiplayer where each player gets their own window:

```bash
# Quick start - automatically opens all windows
./start_multiplayer.sh

# Manual start
./start_server.sh          # Start the game server
./start_client.sh          # Start first client (White player)
./start_client.sh          # Start second client (Black player)

# Management
./check_status.sh          # Check running processes
./end_server.sh            # Stop all network processes
```

See `NETWORK_GUIDE.md` for detailed network setup instructions.

## Command Line Arguments

The game supports several command line arguments for customization:

### Usage
```bash
python main.py [board_size] [frontline] [turn_time]
```

### Arguments
- **board_size**: Size of the n×n board (default: 24, min: 8, max: 50)
- **frontline**: Rows from king where pieces can be placed (default: 2, min: 1, max: 10)  
- **turn_time**: Delay between moves in seconds (default: 0.5, min: 0, max: 5.0)

### Examples
```bash
# Default game: 24×24 board, 2-row frontline, 0.5s delay
python main.py

# Smaller board for faster games
python main.py 16

# Large board with extended frontline
python main.py 32 4

# Fast-paced game with no delays
python main.py 16 2 0

# Slow, strategic game
python main.py 20 3 2.0
```

### Help
```bash
python main.py --help
# or
python main.py -h
```

### Frontline Rules
- **White pieces**: Can be placed from frontline distance above their kings to the bottom of the board
- **Black pieces**: Can be placed from the top of the board to frontline distance below their kings  
- **Multiple kings**: Each king creates its own frontline zone
- **Strategic importance**: Frontline distance affects piece placement strategy and game dynamics

## How to Play

### Basic Gameplay Flow
1. **Start**: Each player begins with 10 points and one piece of each type available
2. **Select**: Click on an affordable piece in your side panel (white left, black right)
3. **Place**: Click on a valid board square within your frontline zone to place the piece
4. **Repeat**: Continue placing pieces for both players as desired
5. **Advance**: Click "Play Turn" to make all pieces move and advance the game
6. **Strategy**: Manage your points and piece behaviors to build an effective army

### Piece Placement Rules
- **Affordability**: Must have enough points to place a piece (cost shown in parentheses)
- **Frontline zones**: Pieces can only be placed within frontline distance from your kings
- **Empty squares**: Can only place pieces on unoccupied squares
- **Multiple placements**: Same piece type can be placed multiple times if affordable
- **Real-time placement**: Both players can place pieces simultaneously

### Setting Piece Behaviors (NEW!)
1. **Click any placed piece** to show behavior selection icons above it
2. **Choose a behavior** by clicking one of the three icons:
   - 🗡️ **Swords (Aggressive)**: Piece will prioritize attacking enemy pieces
   - 🛡️ **Shield (Defensive)**: Piece will defend the king and block enemies
   - ⏳ **Hourglass (Passive)**: Piece will stay still and not move
3. **Visual feedback**: Pieces show colored dots indicating their current behavior
4. **Automatic reset**: All behaviors return to default after playing a turn

### Turn System
- **Play Turn**: Click the "Play Turn" button to execute movement phase
- **Auto-turns**: Set how many movement rounds occur per turn (default: 1)
- **Points award**: Both players gain 5 points each turn
- **Movement order**: Pieces move in random order to ensure fairness
- **Real-time visualization**: Watch pieces move with configurable delays

### Advanced Controls
- **AutoTurns field**: Click the number field in top-right to change auto-turns setting
- **Right-click**: Deselect current piece or hide behavior icons
- **Multiple kings**: Place multiple kings to create multiple frontline zones
- **Strategic timing**: Set piece behaviors before playing turn for tactical advantage

## Game Rules

### Chess Movement Rules
- **King**: One square in any direction (20 points)
- **Queen**: Any number of squares horizontally, vertically, or diagonally (10 points)
- **Rook**: Any number of squares horizontally or vertically (5.25 points)
- **Bishop**: Any number of squares diagonally (3.5 points)
- **Knight**: L-shaped move (2+1 squares), can jump over pieces (3.5 points)
- **Pawn**: Forward one square (or two on first move), captures diagonally (1 point)

### General Rules
- **Piece interaction**: Pieces cannot move through other pieces (except Knights)
- **Capturing**: Pieces can capture enemy pieces by moving to their square
- **Frontline system**: Placement restricted to frontline zones around kings
- **Point economy**: Strategic point management essential for success
- **Win condition**: Game ends when one player loses all their kings
- **Behavior strategy**: Use piece behaviors to control tactical movements

### Strategic Elements
- **Economic planning**: Balance expensive powerful pieces vs. cheap numerous pieces
- **Frontline management**: King placement determines where you can deploy forces
- **Behavior tactics**: Set piece behaviors before turns for coordinated strategies
- **Timing**: When to place pieces vs. when to advance turns for optimal positioning

## Controls Reference

### Mouse Controls
- **Select Piece**: Click on an affordable piece in your side panel
- **Place Piece**: Click on an empty board square within frontline zone while piece is selected
- **Set Behavior**: Click on any placed piece to show behavior icons, then click desired behavior
- **Play Turn**: Click the "Play Turn" button to advance the game
- **AutoTurns**: Click the number field in top-right corner to modify auto-turns setting
- **Right-click**: Deselect current piece or hide behavior icons
- **Close Window**: Close the game window to exit

### Keyboard Controls
- **Number keys**: When AutoTurns field is active, type numbers to set auto-turns value
- **Enter**: Confirm AutoTurns input
- **Escape**: Cancel AutoTurns input
- **Backspace**: Delete digits in AutoTurns field

### Visual Indicators
- **White text**: Affordable pieces you can place
- **Gray text**: Unaffordable pieces (insufficient points)
- **Yellow highlight**: Currently selected piece
- **Colored dots on pieces**: Show current behavior (red=aggressive, blue=defensive, yellow=passive)
- **Red borders**: Frontline zones where pieces can be placed
- **Behavior icons**: Swords/Shield/Hourglass above clicked pieces

## Point System & Economy

### Starting Conditions
- **Starting Points**: Each player begins with 10 points
- **Initial Pieces**: Each player gets one of each piece type available for placement

### Points Economy
- **Points Per Turn**: Players gain 5 points each turn (configurable in code)
- **Piece Costs**: Players spend points equal to piece value to place them
- **Point Display**: Current points shown in green at top of each player's column
- **Strategic Planning**: Balance expensive powerful pieces vs. numerous cheap pieces

### Piece Values
- **Pawn**: 1 point - Cheap and expendable, good for frontline presence
- **Knight**: 3.5 points - Mobile and can jump over pieces
- **Bishop**: 3.5 points - Long-range diagonal movement
- **Rook**: 5.25 points - Powerful horizontal/vertical movement
- **Queen**: 10 points - Most versatile piece, very expensive
- **King**: 20 points - Essential but extremely expensive, creates frontline zones

## Technical Requirements

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.7 or higher (Python 3.12+ recommended)
- **Memory**: 100MB+ available RAM
- **Display**: Graphics capability for pygame window
- **Input**: Mouse and keyboard

### Dependencies
- **pygame**: Graphics and user interface library
- **Python standard library**: typing, os, sys, random, abc

### File Requirements
The `svgs/` folder must contain chess piece images in PNG format:
- `King_White.svg.png`, `King_Black.svg.png`
- `Queen_White.svg.png`, `Queen_Black.svg.png`  
- `Rook_White.svg.png`, `Rook_Black.svg.png`
- `Bishop_White.svg.png`, `Bishop_Black.svg.png`
- `Knight_White.svg.png`, `Knight_Black.svg.png`
- `Pawn_White.svg.png`, `Pawn_Black.svg.png`

## File Structure

```
AutoChessBattler/
├── main.py                 # Main game controller and entry point
├── autochess_pieces.py     # Chess piece classes with movement logic and behavior system
├── board.py                # Chess board management and piece positioning
├── game_ui.py              # Pygame-based user interface and behavior icon rendering
├── requirements.txt        # Python dependencies (pygame)
├── run_game.sh            # Automated setup and run script (Linux/Mac)
├── README.md              # This documentation file
├── venv/                  # Virtual environment (created after setup)
├── svgs/                  # Chess piece SVG images
│   ├── King_White.svg.png
│   ├── King_Black.svg.png
│   ├── Queen_White.svg.png
│   ├── Queen_Black.svg.png
│   ├── Rook_White.svg.png
│   ├── Rook_Black.svg.png
│   ├── Bishop_White.svg.png
│   ├── Bishop_Black.svg.png
│   ├── Knight_White.svg.png
│   ├── Knight_Black.svg.png
│   ├── Pawn_White.svg.png
│   └── Pawn_Black.svg.png
└── __pycache__/           # Python cache files (auto-generated)
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'pygame'"**
- Solution: Activate virtual environment and install dependencies
- Run: `source venv/bin/activate && pip install -r requirements.txt`

**"Permission denied: ./run_game.sh"**
- Solution: Make script executable
- Run: `chmod +x run_game.sh`

**Game window is too large/small**
- Solution: Use command line arguments to adjust board size
- Run: `python main.py 16` for smaller board or `python main.py 32` for larger

**Pieces not displaying correctly**
- Solution: Ensure all SVG images are in the `svgs/` folder with correct names
- Check that image files are in PNG format despite .svg.png extension

**Behavior icons not clickable**
- This has been fixed in the latest version - icons are now clickable even when positioned outside board area

### Performance Tips
- **Smaller boards** (8-16) run faster and use less memory
- **Reduce turn_time** to 0 for instant piece movements
- **Lower auto-turns** setting (1-2) for smoother gameplay
- **Close other applications** if experiencing lag

### Getting Help
- Check command line arguments with: `python main.py --help`
- Review this README for complete feature documentation
- Ensure virtual environment is activated before running
- Verify all dependencies are installed with `pip list`

---

**Enjoy playing AutoChessBattler!** 🏰♟️

*A strategic chess variant focusing on piece placement, economic management, and tactical behavior control.*


## vscode settings fix
	"python.experiments.optOutFrom": [
			"pythonTerminalEnvVarActivation"
		]


## TODO
- add pawns making to square moves on first move
- add en passant to counter the two move jump