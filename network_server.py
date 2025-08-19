#!/usr/bin/env python3
"""
AutoChess Network Server
Manages authoritative game state and communicates with clients.
"""

import asyncio
import json
import websockets
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from autochess_pieces import AutoChessPiece, King, Queen, Rook, Bishop, Knight, Pawn
from board import ChessBoard


@dataclass
class GameState:
    """Represents the complete game state that needs to be synchronized"""
    board_state: List[List[Optional[dict]]]  # Serializable board representation
    white_points: int
    black_points: int
    current_player: str
    turn_counter: int
    frontline: int
    auto_turns: int
    game_over: bool
    winner: Optional[str]
    error_message: str


@dataclass
class PlayerAction:
    """Represents a player action"""
    action_type: str  # "place_piece", "play_turn", "set_behavior", etc.
    player_color: str
    data: dict  # Action-specific data


class NetworkGameServer:
    """Manages a networked AutoChess game session"""
    
    def __init__(self, board_size: int = 24, frontline: int = 2, 
                 turn_time: float = 0.1, points_rate: int = 5, start_points: int = 20):
        self.board = ChessBoard(size=board_size)
        self.board_size = board_size
        self.frontline = frontline
        self.turn_time = turn_time
        self.points_rate = points_rate
        
        # Game state
        self.white_points = start_points
        self.black_points = start_points
        self.current_player = "white"
        self.turn_counter = 1
        self.auto_turns = 1
        self.game_over = False
        self.winner = None
        self.error_message = ""
        
        # Network state
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.player_assignments: Dict[str, str] = {}  # client_id -> color
        self.game_id = str(uuid.uuid4())
        
        # Initialize kings
        self._initialize_kings()
    
    def _initialize_kings(self):
        """Place starting kings on the board"""
        mid = self.board_size // 2
        
        # Place white king
        white_king = King("white")
        self.board.place_piece(white_king, (self.board_size - 1, mid))
        
        # Place black king  
        black_king = King("black")
        self.board.place_piece(black_king, (0, mid))
    
    def _serialize_board(self) -> List[List[Optional[dict]]]:
        """Convert board to serializable format"""
        serialized = []
        for row in range(self.board_size):
            serialized_row = []
            for col in range(self.board_size):
                piece = self.board.get_piece((row, col))
                if piece:
                    piece_data = {
                        'type': piece.piece_type,
                        'color': piece.color,
                        'has_moved': piece.has_moved,
                        'behavior': getattr(piece, 'behavior', 'default')
                    }
                    serialized_row.append(piece_data)
                else:
                    serialized_row.append(None)
            serialized.append(serialized_row)
        return serialized
    
    def get_game_state(self) -> GameState:
        """Get current game state for synchronization"""
        return GameState(
            board_state=self._serialize_board(),
            white_points=self.white_points,
            black_points=self.black_points,
            current_player=self.current_player,
            turn_counter=self.turn_counter,
            frontline=self.frontline,
            auto_turns=self.auto_turns,
            game_over=self.game_over,
            winner=self.winner,
            error_message=self.error_message
        )
    
    async def handle_client_action(self, client_id: str, action: PlayerAction) -> bool:
        """Process a client action and return success status"""
        if client_id not in self.player_assignments:
            return False
            
        player_color = self.player_assignments[client_id]
        
        if action.action_type == "place_piece":
            return await self._handle_place_piece(player_color, action.data)
        elif action.action_type == "play_turn":
            return await self._handle_play_turn(player_color)
        elif action.action_type == "set_behavior":
            return await self._handle_set_behavior(player_color, action.data)
        elif action.action_type == "set_auto_turns":
            return await self._handle_set_auto_turns(player_color, action.data)
        
        return False
    
    async def _handle_place_piece(self, player_color: str, data: dict) -> bool:
        """Handle piece placement action"""
        try:
            piece_type = data['piece_type']
            position = tuple(data['position'])
            
            # Validate placement (similar to original game logic)
            if not self._can_place_piece(player_color, piece_type, position):
                self.error_message = f"Cannot place {piece_type} at {position}"
                return False
            
            # Create and place piece
            piece = self._create_piece(piece_type, player_color)
            if self.board.place_piece(piece, position):
                # Deduct points
                if player_color == "white":
                    self.white_points -= piece.point_value
                else:
                    self.black_points -= piece.point_value
                
                self.error_message = ""
                return True
            
        except Exception as e:
            self.error_message = f"Error placing piece: {str(e)}"
        
        return False
    
    async def _handle_play_turn(self, player_color: str) -> bool:
        """Handle play turn action"""
        try:
            # Implement turn logic (similar to original game)
            # This would include piece movement, point allocation, etc.
            
            # Award points
            self.white_points += self.points_rate
            self.black_points += self.points_rate
            self.turn_counter += 1
            
            # Check win conditions
            self._check_win_conditions()
            
            return True
            
        except Exception as e:
            self.error_message = f"Error processing turn: {str(e)}"
            return False
    
    async def _handle_set_behavior(self, player_color: str, data: dict) -> bool:
        """Handle setting piece behavior"""
        try:
            position = tuple(data['position'])
            behavior = data['behavior']
            
            piece = self.board.get_piece(position)
            if piece and piece.color == player_color:
                piece.behavior = behavior
                return True
                
        except Exception as e:
            self.error_message = f"Error setting behavior: {str(e)}"
        
        return False
    
    async def _handle_set_auto_turns(self, player_color: str, data: dict) -> bool:
        """Handle setting auto turns"""
        try:
            auto_turns = data['auto_turns']
            if 1 <= auto_turns <= 10:
                self.auto_turns = auto_turns
                return True
        except Exception as e:
            self.error_message = f"Error setting auto turns: {str(e)}"
        
        return False
    
    def _can_place_piece(self, player_color: str, piece_type: str, position: tuple) -> bool:
        """Validate if a piece can be placed at the given position"""
        # Check if position is empty
        if not self.board.is_empty(position):
            return False
        
        # Check if player has enough points
        piece = self._create_piece(piece_type, player_color)
        current_points = self.white_points if player_color == "white" else self.black_points
        if current_points < piece.point_value:
            return False
        
        # Check frontline restrictions (implement frontline logic)
        return self._is_in_frontline(player_color, position)
    
    def _is_in_frontline(self, player_color: str, position: tuple) -> bool:
        """Check if position is within frontline zone"""
        # Implement frontline logic similar to original game
        # This is a simplified version
        row, col = position
        
        if player_color == "white":
            # White can place in bottom portion
            return row >= self.board_size - self.frontline - 1
        else:
            # Black can place in top portion
            return row <= self.frontline
    
    def _create_piece(self, piece_type: str, color: str) -> AutoChessPiece:
        """Create a piece instance from type string"""
        piece_classes = {
            "King": King,
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
            "Pawn": Pawn
        }
        return piece_classes[piece_type](color)
    
    def _check_win_conditions(self):
        """Check if game has ended"""
        # Count kings for each player
        white_kings = 0
        black_kings = 0
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board.get_piece((row, col))
                if piece and piece.piece_type == "King":
                    if piece.color == "white":
                        white_kings += 1
                    else:
                        black_kings += 1
        
        if white_kings == 0:
            self.game_over = True
            self.winner = "black"
        elif black_kings == 0:
            self.game_over = True
            self.winner = "white"
    
    async def broadcast_game_state(self):
        """Send current game state to all connected clients"""
        if not self.clients:
            return
        
        game_state = self.get_game_state()
        message = {
            'type': 'game_state_update',
            'data': asdict(game_state)
        }
        
        # Send to all clients
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                # Remove disconnected client
                del self.clients[client_id]
                if client_id in self.player_assignments:
                    del self.player_assignments[client_id]
    
    async def add_client(self, websocket, client_id: str) -> str:
        """Add a new client and assign them a color"""
        self.clients[client_id] = websocket
        
        # Assign color (white for first player, black for second)
        assigned_colors = set(self.player_assignments.values())
        if "white" not in assigned_colors:
            self.player_assignments[client_id] = "white"
            return "white"
        elif "black" not in assigned_colors:
            self.player_assignments[client_id] = "black"
            return "black"
        else:
            # Game is full, client becomes spectator
            return "spectator"


class AutoChessServer:
    """Main server class that manages multiple game sessions"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.games: Dict[str, NetworkGameServer] = {}
    
    async def handle_client(self, websocket, path):
        """Handle new client connection"""
        client_id = str(uuid.uuid4())
        
        try:
            # Wait for initial connection message
            initial_message = await websocket.recv()
            data = json.loads(initial_message)
            
            if data['type'] == 'join_game':
                game_id = data.get('game_id', 'default')
                
                # Create game if it doesn't exist
                if game_id not in self.games:
                    self.games[game_id] = NetworkGameServer()
                
                game = self.games[game_id]
                assigned_color = await game.add_client(websocket, client_id)
                
                # Send assignment confirmation
                await websocket.send(json.dumps({
                    'type': 'player_assignment',
                    'data': {
                        'client_id': client_id,
                        'assigned_color': assigned_color,
                        'game_id': game_id
                    }
                }))
                
                # Send initial game state
                await game.broadcast_game_state()
                
                # Handle client messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        if data['type'] == 'player_action':
                            action = PlayerAction(**data['data'])
                            success = await game.handle_client_action(client_id, action)
                            
                            # Broadcast updated game state
                            await game.broadcast_game_state()
                            
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from client {client_id}")
                    except Exception as e:
                        print(f"Error handling message from {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"Client {client_id} disconnected")
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"Starting AutoChess server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            print("Server started! Waiting for connections...")
            await asyncio.Future()  # Run forever


if __name__ == "__main__":
    server = AutoChessServer()
    asyncio.run(server.start_server())
