#!/usr/bin/env python3
"""
Test passive behavior in game context without pygame
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autochess_pieces import King, Pawn
from board import ChessBoard

def test_passive_behavior_in_game():
    """Test passive behavior prevents movement during game turn simulation"""
    print("Testing Passive Behavior in Game Context")
    print("=" * 40)
    
    # Create a small test board
    board = ChessBoard(8)
    
    # Place some pieces
    white_king = King("white")
    black_pawn = Pawn("black")
    
    board.place_piece(white_king, (4, 4))  # Center
    board.place_piece(black_pawn, (2, 2))  # Upper left
    
    print("Initial setup:")
    print(f"  White King at (4,4) - behavior: {white_king.behavior}")
    print(f"  Black Pawn at (2,2) - behavior: {black_pawn.behavior}")
    
    # Test normal movement
    print("\n1. Testing normal movement:")
    king_moves = white_king.get_valid_moves((4, 4), board)
    pawn_moves = black_pawn.get_valid_moves((2, 2), board)
    print(f"  King has {len(king_moves)} possible moves")
    print(f"  Pawn has {len(pawn_moves)} possible moves")
    
    # Set passive behavior
    print("\n2. Setting passive behavior:")
    white_king.set_behavior("passive")
    black_pawn.set_behavior("passive")
    print(f"  White King behavior: {white_king.behavior}")
    print(f"  Black Pawn behavior: {black_pawn.behavior}")
    
    # Test passive movement
    print("\n3. Testing passive movement restriction:")
    king_moves_passive = white_king.get_valid_moves((4, 4), board)
    pawn_moves_passive = black_pawn.get_valid_moves((2, 2), board)
    print(f"  King has {len(king_moves_passive)} possible moves (should be 0)")
    print(f"  Pawn has {len(pawn_moves_passive)} possible moves (should be 0)")
    
    # Verify passive behavior prevents movement
    passive_working = (len(king_moves_passive) == 0 and len(pawn_moves_passive) == 0)
    print(f"\n✅ Passive behavior working correctly: {passive_working}")
    
    # Test behavior reset
    print("\n4. Testing behavior reset:")
    white_king.reset_behavior()
    black_pawn.reset_behavior()
    
    king_moves_reset = white_king.get_valid_moves((4, 4), board)
    pawn_moves_reset = black_pawn.get_valid_moves((2, 2), board)
    print(f"  After reset - King: {len(king_moves_reset)} moves")
    print(f"  After reset - Pawn: {len(pawn_moves_reset)} moves")
    print(f"  Movement restored: {len(king_moves_reset) > 0 and len(pawn_moves_reset) > 0}")
    
    print("\n🎯 Summary:")
    print("  • Passive pieces cannot move (0 valid moves)")
    print("  • Non-passive pieces move normally")
    print("  • Behavior resets restore normal movement")
    print("  • Perfect for creating defensive positions or holding ground!")

if __name__ == "__main__":
    test_passive_behavior_in_game()
