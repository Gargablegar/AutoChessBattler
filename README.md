# AutoChess Game

A Python chess game with strategic piece placement and point-based economy system.

## Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip (Python package installer)

### Quick Start
1. **Clone or download** the project to your local machine
2. **Navigate** to the AutoChess directory:
   ```bash
   cd AutoChess
   ```
3. **Run the game** (automatically sets up virtual environment):
   ```bash
   ./run_game.sh
   ```

### Manual Setup (Alternative)
If you prefer to set up manually:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**:
   ```bash
   python game.py
   ```

### Always Use Virtual Environment
**Important**: Always make sure to activate the virtual environment before running the game:
```bash
source venv/bin/activate && python game.py
```

Or use the provided script which handles this automatically:
```bash
./run_game.sh
```

## Features

- Configurable board size (default 24x24, minimum 8x8)
- Point-based piece placement system
- Each player starts with 10 points and gains 5 points per turn
- One piece of each type available per player:
  - King, Queen, Rook, Bishop, Knight, Pawn
- Interactive piece placement from side panels
- Chess pieces with accurate movement rules based on official chess rules
- Random piece movement simulation after placement
- Turn-based gameplay
- Visual representation of pieces using SVG images
- Point values for each piece:
  - Pawn: 1 point
  - Knight: 3.5 points
  - Bishop: 3.5 points
  - Rook: 5.25 points
  - Queen: 10 points
  - King: 20 points

## Gameplay

1. Each player has a set of pieces available in their side panel
2. Players gain 5 points each turn (displayed in green at the top of each column)
3. Click on a piece in your side panel to select it (if you can afford it)
4. Click on an empty board square to place the selected piece
5. Placing a piece deducts its point value from your total
6. Click "Play Turn" to make all pieces on the board move randomly
7. Pieces follow standard chess movement rules
8. Pieces cannot move through other pieces (except Knights)
9. Pieces can capture enemy pieces by moving to their square

## Controls

- **Select Piece**: Click on an affordable piece in your side panel (white pieces on left, black pieces on right)
- **Place Piece**: Click on an empty board square while a piece is selected
- **Play Turn**: Click the "Play Turn" button to advance the game and give both players points
- **Close**: Close window to exit

## Point System

- **Starting Points**: Each player begins with 10 points
- **Points Per Turn**: Players gain 5 points each turn
- **Piece Costs**: Players must spend points equal to the piece's value to place it
- **Affordable Pieces**: Pieces you can afford are shown in white text
- **Unaffordable Pieces**: Pieces you cannot afford are shown in gray text
- **Selected Pieces**: Selected pieces are highlighted in yellow

## Requirements

- Python 3.7+
- pygame

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the `svgs/` folder contains the chess piece images in the format:
   - `King_White.svg.png`, `King_Black.svg.png`
   - `Queen_White.svg.png`, `Queen_Black.svg.png`
   - `Rook_White.svg.png`, `Rook_Black.svg.png`
   - `Bishop_White.svg.png`, `Bishop_Black.svg.png`
   - `Knight_White.svg.png`, `Knight_Black.svg.png`
   - `Pawn_White.svg.png`, `Pawn_Black.svg.png`

## Usage

Run the game with default 24x24 board:
```bash
python game.py
```

Run with custom board size (e.g., 16x16):
```bash
python game.py 16
```

## How to Play

1. The game starts with an empty board
2. Each player has one of each piece type available in their side panel:
   - White pieces: left side panel
   - Black pieces: right side panel
3. Players start with 10 points and gain 5 points each turn
4. Click on a piece in your side panel to select it (must be affordable)
5. Click on an empty board square to place the selected piece
6. Click the "Play Turn" button to:
   - Make all pieces on the board move randomly
   - Give both players 5 additional points
7. The turn counter at the top shows the current turn number
8. Points are displayed in green at the top of each player's column

## Game Rules

- Pieces move according to standard chess rules:
  - **King**: One square in any direction
  - **Queen**: Any number of squares horizontally, vertically, or diagonally
  - **Rook**: Any number of squares horizontally or vertically
  - **Bishop**: Any number of squares diagonally
  - **Knight**: L-shaped move (2 squares in one direction, 1 in perpendicular)
  - **Pawn**: Forward one square (or two on first move), captures diagonally

- Pieces cannot move through other pieces (except Knights)
- Pieces can capture enemy pieces by moving to their square
- The game focuses on strategic piece placement and movement simulation rather than traditional chess victory conditions
- Players must manage their points wisely to build an effective army
- Kings are expensive (20 points) but essential pieces

## File Structure

- `game.py` - Main game file and entry point
- `autochess_pieces.py` - Chess piece classes with movement logic
- `board.py` - Chess board management
- `game_ui.py` - Pygame-based user interface
- `svgs/` - Directory containing piece images
- `requirements.txt` - Python dependencies

## Controls

- **Select Piece**: Click on an affordable piece in your side panel
- **Place Piece**: Click on an empty board square while a piece is selected  
- **Play Turn**: Click "Play Turn" button to advance the game
- **Close**: Close window to exit

Enjoy playing AutoChess!
