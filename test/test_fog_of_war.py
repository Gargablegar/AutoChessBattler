#!/usr/bin/env python3
"""
Test script for White Fog of War debug functionality
This script demonstrates the fog of war implementation with a simple board setup.
"""

import pygame
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autochess_pieces import King, Queen, Rook, Bishop, Knight, Pawn
from board import ChessBoard
from game_ui import GameUI
from debug import DebugManager

def setup_test_board():
    """Set up a test board with some pieces for fog of war testing"""
    board = ChessBoard(8)
    
    # Place white pieces (bottom half)
    board.place_piece(King("white"), (7, 3))  # White king
    board.place_piece(Queen("white"), (7, 4))  # White queen
    board.place_piece(Rook("white"), (7, 0))   # White rook left
    board.place_piece(Rook("white"), (7, 7))   # White rook right
    board.place_piece(Bishop("white"), (6, 2)) # White bishop
    board.place_piece(Knight("white"), (6, 1)) # White knight
    board.place_piece(Pawn("white"), (5, 3))   # White pawn
    
    # Place black pieces (top half) - some visible, some hidden
    board.place_piece(King("black"), (0, 4))   # Black king
    board.place_piece(Queen("black"), (1, 4))  # Black queen
    board.place_piece(Rook("black"), (0, 0))   # Black rook (should be hidden)
    board.place_piece(Bishop("black"), (2, 5)) # Black bishop (might be visible)
    board.place_piece(Knight("black"), (3, 3)) # Black knight (should be visible)
    board.place_piece(Pawn("black"), (4, 3))   # Black pawn (blocking white pawn)
    
    return board

def test_fog_of_war():
    """Test the white fog of war implementation"""
    pygame.init()
    
    # Set up test components
    board = setup_test_board()
    ui = GameUI(8)
    debug_manager = DebugManager(8)
    
    print("=== White Fog of War Test ===")
    print("Board setup:")
    print("White pieces: King(7,3), Queen(7,4), Rooks(7,0),(7,7), Bishop(6,2), Knight(6,1), Pawn(5,3)")
    print("Black pieces: King(0,4), Queen(1,4), Rook(0,0), Bishop(2,5), Knight(3,3), Pawn(4,3)")
    print()
    
    # Calculate fog of war
    visible_squares, enemy_pieces_visible = debug_manager.calculate_white_fog_of_war(board)
    
    print(f"Visible squares: {len(visible_squares)}")
    print(f"Sample visible squares: {sorted(list(visible_squares))[:10]}...")
    print()
    print(f"Enemy pieces visible: {len(enemy_pieces_visible)}")
    print(f"Enemy piece positions: {sorted(list(enemy_pieces_visible))}")
    print()
    
    # Analyze specific piece vision
    print("=== Piece Vision Analysis ===")
    for piece, (row, col) in board.get_all_pieces():
        if piece.color == "white":
            piece_vision, enemy_vision = debug_manager._calculate_piece_vision(piece, (row, col), board)
            print(f"{piece.piece_type} at ({row},{col}): sees {len(piece_vision)} squares, spots {len(enemy_vision)} enemies")
            if enemy_vision:
                print(f"  Spots enemies at: {sorted(list(enemy_vision))}")
    
    print()
    print("=== Territory Analysis ===")
    territory = debug_manager._get_white_territory_squares([])
    print(f"White territory squares: {len(territory)}")
    print(f"Territory sample: {sorted(list(territory))[:10]}...")
    
    print()
    print("Fog of war test completed successfully!")
    print("In the game, enable 'White fog of war' from the Debug menu to see this in action.")

if __name__ == "__main__":
    test_fog_of_war()
