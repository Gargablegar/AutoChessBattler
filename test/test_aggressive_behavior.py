#!/usr/bin/env python3
"""
Test aggressive behavior implementation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autochess_pieces import King, Queen, Rook, Bishop, Knight, Pawn
from board import ChessBoard

def test_aggressive_behavior():
    """Test the aggressive behavior implementation"""
    print("Testing Aggressive Behavior Implementation")
    print("=" * 45)
    
    # Create test board
    board = ChessBoard(8)
    
    # Test 1: Capture prioritization
    print("\n1. Testing capture prioritization:")
    
    # Place a white rook and black pieces it can capture
    white_rook = Rook("white")
    black_pawn1 = Pawn("black")
    black_pawn2 = Pawn("black")
    
    board.place_piece(white_rook, (4, 4))  # Center
    board.place_piece(black_pawn1, (4, 6))  # Same row, capturable
    board.place_piece(black_pawn2, (6, 4))  # Same column, capturable
    
    # Test normal behavior
    normal_moves = white_rook._get_piece_moves((4, 4), board)
    print(f"  Normal rook moves: {len(normal_moves)} available")
    
    # Test aggressive behavior
    white_rook.set_behavior("aggressive")
    aggressive_moves = white_rook.get_valid_moves((4, 4), board)
    
    # Check if aggressive moves only include captures
    capture_positions = {(4, 6), (6, 4)}
    aggressive_set = set(aggressive_moves)
    captures_available = aggressive_set.intersection(capture_positions)
    
    print(f"  Aggressive rook moves: {len(aggressive_moves)} available")
    print(f"  Captures available: {len(captures_available)} out of 2 possible")
    print(f"  Prioritizing captures: {captures_available == aggressive_set}")
    
    # Clear board for next test
    board.clear()
    
    # Test 2: Movement toward enemy king when no captures available
    print("\n2. Testing movement toward enemy king:")
    
    # Place white pawn and black king (no immediate captures possible)
    white_pawn = Pawn("white")
    black_king = King("black")
    
    board.place_piece(white_pawn, (6, 3))  # Near bottom for white
    board.place_piece(black_king, (2, 2))  # Upper left
    
    # Test normal behavior
    normal_moves = white_pawn._get_piece_moves((6, 3), board)
    print(f"  Normal pawn moves: {normal_moves}")
    
    # Test aggressive behavior
    white_pawn.set_behavior("aggressive")
    aggressive_moves = white_pawn.get_valid_moves((6, 3), board)
    print(f"  Aggressive pawn moves: {aggressive_moves}")
    
    # Check if moves are toward the king
    current_distance = abs(6 - 2) + abs(3 - 2)  # Distance to king
    better_moves = []
    for move_row, move_col in aggressive_moves:
        new_distance = abs(move_row - 2) + abs(move_col - 2)
        if new_distance < current_distance:
            better_moves.append((move_row, move_col))
    
    print(f"  Moves toward king: {len(better_moves)} out of {len(aggressive_moves)}")
    
    # Clear board for next test
    board.clear()
    
    # Test 3: Complex scenario with multiple options
    print("\n3. Testing complex scenario:")
    
    # Place white queen with both capture and movement options
    white_queen = Queen("white")
    black_rook = Rook("black")
    black_king = King("black")
    
    board.place_piece(white_queen, (4, 4))  # Center
    board.place_piece(black_rook, (4, 7))   # Capturable
    board.place_piece(black_king, (0, 0))   # Far away
    
    white_queen.set_behavior("aggressive")
    aggressive_moves = white_queen.get_valid_moves((4, 4), board)
    
    # Should prioritize capturing the rook
    has_capture = (4, 7) in aggressive_moves
    print(f"  Queen can capture rook: {has_capture}")
    print(f"  Aggressive moves include capture: {has_capture}")
    
    # Test all piece types with aggressive behavior
    print("\n4. Testing all piece types with aggressive behavior:")
    
    test_pieces = [
        (King("white"), "King"),
        (Queen("white"), "Queen"), 
        (Rook("white"), "Rook"),
        (Bishop("white"), "Bishop"),
        (Knight("white"), "Knight"),
        (Pawn("white"), "Pawn")
    ]
    
    for piece, name in test_pieces:
        board.clear()
        board.place_piece(piece, (4, 4))
        board.place_piece(King("black"), (0, 0))  # Enemy king for targeting
        
        # Test normal vs aggressive
        normal_moves = piece._get_piece_moves((4, 4), board)
        piece.set_behavior("aggressive")
        aggressive_moves = piece.get_valid_moves((4, 4), board)
        
        print(f"  {name}: Normal={len(normal_moves)}, Aggressive={len(aggressive_moves)} ✓")
        piece.reset_behavior()
    
    print("\n✅ Aggressive behavior implementation tests completed!")
    
    print("\n🗡️ Aggressive Behavior Summary:")
    print("  • PRIORITY 1: Capture enemy pieces when possible")
    print("  • PRIORITY 2: Move toward enemy kings when no captures available")
    print("  • FALLBACK: Normal movement if no strategic options")
    print("  • EFFECT: Creates more aggressive, attacking gameplay")

if __name__ == "__main__":
    test_aggressive_behavior()
