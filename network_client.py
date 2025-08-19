#!/usr/bin/env python3
"""
AutoChess Network Client
Connects to server and displays player-specific game view.
"""

import asyncio
import json
import websockets
import pygame
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from autochess_pieces import AutoChessPiece, King, Queen, Rook, Bishop, Knight, Pawn
from board import ChessBoard
from game_ui import GameUI


@dataclass
class NetworkGameState:
    """Client-side representation of game state"""
    board_state: list
    white_points: int
    black_points: int
    current_player: str
    turn_counter: int
    frontline: int
    auto_turns: int
    game_over: bool
    winner: Optional[str]
    error_message: str


class NetworkGameClient:
    """Client-side game logic and rendering"""
    
    def __init__(self, player_color: str, board_size: int = 24):
        # Initialize pygame
        pygame.init()
        
        self.player_color = player_color
        self.board_size = board_size
        self.board = ChessBoard(size=board_size)
        self.ui = GameUI(board_size=board_size)
        
        # Client-specific state
        self.running = True
        self.selected_piece_type = None
        self.error_message = ""
        self.game_state: Optional[NetworkGameState] = None
        
        # Network state
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.client_id: Optional[str] = None
        
        # Update UI title to show player color
        pygame.display.set_caption(f"AutoChess - {player_color.title()} Player")
    
    def apply_game_state(self, game_state_data: Dict[str, Any]):
        """Apply received game state to local board"""
        self.game_state = NetworkGameState(**game_state_data)
        
        # Clear and rebuild board
        self.board.clear()
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece_data = self.game_state.board_state[row][col]
                if piece_data:
                    piece = self._create_piece_from_data(piece_data)
                    self.board.place_piece(piece, (row, col))
        
        # Update error message
        self.error_message = self.game_state.error_message
    
    def _create_piece_from_data(self, piece_data: Dict[str, Any]) -> AutoChessPiece:
        """Create piece instance from serialized data"""
        piece_classes = {
            "King": King,
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
            "Pawn": Pawn
        }
        
        piece_class = piece_classes[piece_data['type']]
        piece = piece_class(piece_data['color'])
        piece.has_moved = piece_data['has_moved']
        piece.behavior = piece_data.get('behavior', 'default')
        
        return piece
    
    async def send_action(self, action_type: str, data: Dict[str, Any]):
        """Send player action to server"""
        if not self.websocket:
            return
        
        message = {
            'type': 'player_action',
            'data': {
                'action_type': action_type,
                'player_color': self.player_color,
                'data': data
            }
        }
        
        try:
            await self.websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            print("Lost connection to server")
            self.running = False
    
    async def handle_click(self, pos: tuple):
        """Handle mouse click events"""
        # Check if click is on side panel (piece selection)
        piece_type = self.ui.get_clicked_piece_type(pos, self.player_color)
        if piece_type:
            self.selected_piece_type = piece_type
            return
        
        # Check if click is on play turn button
        if self.ui.play_button_rect.collidepoint(pos):
            await self.send_action('play_turn', {})
            return
        
        # Check if click is on board
        board_pos = self.ui.get_board_position(pos)
        if board_pos and self.selected_piece_type:
            # Attempt to place piece
            await self.send_action('place_piece', {
                'piece_type': self.selected_piece_type,
                'position': board_pos
            })
            self.selected_piece_type = None
            return
        
        # Check if click is on existing piece (for behavior setting)
        if board_pos:
            piece = self.board.get_piece(board_pos)
            if piece and piece.color == self.player_color:
                # Show behavior selection (implement UI for this)
                pass
    
    def render_game(self):
        """Render the current game state"""
        if not self.game_state:
            return
        
        # Calculate frontline zones for this player's perspective
        frontline_zones = self._calculate_frontline_zones()
        
        # Render the game
        self.ui.screen.fill(self.ui.colors['background'])
        
        # Render board with player-specific perspective
        self._render_player_perspective()
        
        # Render UI elements
        self.ui.render_side_panels(
            self.game_state.white_points,
            self.game_state.black_points,
            selected_piece=self.selected_piece_type,
            current_player=self.player_color  # Always show current player as active
        )
        
        # Render turn info
        self.ui.render_turn_info(
            self.game_state.turn_counter,
            self.game_state.auto_turns,
            show_play_button=True  # Always show play button for this player
        )
        
        # Render error/status messages
        if self.error_message:
            self.ui.render_error_message(self.error_message)
        elif self.game_state.game_over and self.game_state.winner:
            win_message = f"{self.game_state.winner.title()} wins!"
            if self.game_state.winner == self.player_color:
                win_message = f"🎉 You win! ({self.player_color})"
            else:
                win_message = f"💀 You lose! ({self.game_state.winner} wins)"
            self.ui.render_error_message(win_message)
        
        pygame.display.flip()
    
    def _render_player_perspective(self):
        """Render board with appropriate perspective for this player"""
        if not self.game_state:
            return
        
        # For this example, render normally
        # Could implement board rotation for black player if desired
        frontline_zones = self._calculate_frontline_zones()
        self.ui.render_board(self.board, frontline_zones, show_coordinates=True)
    
    def _calculate_frontline_zones(self) -> list:
        """Calculate frontline zones for piece placement"""
        zones = []
        
        # Find all kings and create frontline zones
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board.get_piece((row, col))
                if piece and piece.piece_type == "King":
                    if piece.color == "white":
                        # White frontline zone (bottom area)
                        min_row = max(0, self.board_size - self.game_state.frontline - 1)
                        max_row = self.board_size - 1
                        zones.append((min_row, max_row, 0, self.board_size - 1, self.ui.colors['frontline']))
                    else:
                        # Black frontline zone (top area)
                        min_row = 0
                        max_row = min(self.board_size - 1, self.game_state.frontline)
                        zones.append((min_row, max_row, 0, self.board_size - 1, self.ui.colors['frontline']))
        
        return zones
    
    async def run_client(self):
        """Main client game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        await self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.selected_piece_type = None
            
            # Render game
            self.render_game()
            clock.tick(60)  # 60 FPS
            
            # Small async yield
            await asyncio.sleep(0.01)
        
        # Cleanup
        if self.websocket:
            await self.websocket.close()
        pygame.quit()


class AutoChessClient:
    """Main client class that handles network connection"""
    
    def __init__(self, server_host: str = "localhost", server_port: int = 8765, game_id: str = "default"):
        self.server_host = server_host
        self.server_port = server_port
        self.game_id = game_id
        self.game_client: Optional[NetworkGameClient] = None
    
    async def connect_to_server(self):
        """Connect to the game server"""
        uri = f"ws://{self.server_host}:{self.server_port}"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to server at {uri}")
                
                # Send join game message
                join_message = {
                    'type': 'join_game',
                    'game_id': self.game_id
                }
                await websocket.send(json.dumps(join_message))
                
                # Wait for player assignment
                assignment_message = await websocket.recv()
                assignment_data = json.loads(assignment_message)
                
                if assignment_data['type'] == 'player_assignment':
                    player_color = assignment_data['data']['assigned_color']
                    client_id = assignment_data['data']['client_id']
                    
                    print(f"Assigned as {player_color} player (ID: {client_id})")
                    
                    if player_color == "spectator":
                        print("Game is full. Joining as spectator.")
                        # Could implement spectator mode
                        return
                    
                    # Create game client
                    self.game_client = NetworkGameClient(player_color)
                    self.game_client.websocket = websocket
                    self.game_client.client_id = client_id
                    
                    # Handle incoming messages
                    async def message_handler():
                        async for message in websocket:
                            try:
                                data = json.loads(message)
                                if data['type'] == 'game_state_update':
                                    self.game_client.apply_game_state(data['data'])
                            except json.JSONDecodeError:
                                print("Received invalid JSON from server")
                            except Exception as e:
                                print(f"Error handling server message: {e}")
                    
                    # Run both message handler and game client
                    await asyncio.gather(
                        message_handler(),
                        self.game_client.run_client()
                    )
                
        except ConnectionRefusedError:
            print(f"Could not connect to server at {uri}")
            print("Make sure the server is running!")
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server was closed")
        except OSError as e:
            print(f"Network error: {e}")
            print("Check your network connection and server address")
        except Exception as e:
            print(f"Connection error: {e}")


async def main():
    """Main entry point for the client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoChess Network Client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--game", default="default", help="Game ID to join")
    
    args = parser.parse_args()
    
    client = AutoChessClient(args.host, args.port, args.game)
    await client.connect_to_server()


if __name__ == "__main__":
    asyncio.run(main())
