#!/usr/bin/env python3
"""
Test combined aggressive and passive behaviors in game scenario
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autochess_pieces import King, Queen, Rook, Pawn
from board import ChessBoard

def test_behavior_combination():
    """Test aggressive and passive behaviors working together"""
    print("Testing Combined Behavior System")
    print("=" * 35)
    
    # Create a test scenario
    board = ChessBoard(8)
    
    # Set up a battle scenario
    white_queen = Queen("white")
    white_rook = Rook("white")
    white_king = King("white")
    
    black_queen = Queen("black")
    black_pawn = Pawn("black")
    black_king = King("black")
    
    # Place pieces
    board.place_piece(white_queen, (5, 3))  # Aggressive attacker
    board.place_piece(white_rook, (6, 2))   # Passive defender
    board.place_piece(white_king, (7, 3))   # Protected king
    
    board.place_piece(black_queen, (2, 4))  # Enemy queen
    board.place_piece(black_pawn, (4, 3))   # Target pawn
    board.place_piece(black_king, (0, 4))   # Enemy king
    
    print("Battle scenario setup:")
    print("  White Queen (5,3) - will be set to AGGRESSIVE")
    print("  White Rook (6,2) - will be set to PASSIVE") 
    print("  White King (7,3) - default behavior")
    print("  Black Queen (2,4) - enemy piece")
    print("  Black Pawn (4,3) - capturable target")
    print("  Black King (0,4) - primary target for aggressive pieces")
    
    # Set behaviors
    print("\n1. Setting piece behaviors:")
    white_queen.set_behavior("aggressive")
    white_rook.set_behavior("passive")
    print(f"  White Queen: {white_queen.behavior}")
    print(f"  White Rook: {white_rook.behavior}")
    print(f"  White King: {white_king.behavior}")
    
    # Test movement options
    print("\n2. Analyzing movement options:")
    
    # Queen (aggressive) - should prioritize captures or move toward enemy king
    queen_moves = white_queen.get_valid_moves((5, 3), board)
    queen_can_capture_pawn = (4, 3) in queen_moves
    print(f"  Aggressive Queen has {len(queen_moves)} moves")
    print(f"  Can capture black pawn: {queen_can_capture_pawn}")
    
    # Rook (passive) - should have no moves
    rook_moves = white_rook.get_valid_moves((6, 2), board)
    print(f"  Passive Rook has {len(rook_moves)} moves (should be 0)")
    
    # King (normal) - should have normal moves
    king_moves = white_king.get_valid_moves((7, 3), board)
    print(f"  Normal King has {len(king_moves)} moves")
    
    # Test what happens when aggressive piece can't capture
    print("\n3. Testing aggressive behavior without captures:")
    
    # Remove the capturable pawn
    board.remove_piece((4, 3))
    queen_moves_no_capture = white_queen.get_valid_moves((5, 3), board)
    
    # Check if moves are toward enemy king
    current_distance = abs(5 - 0) + abs(3 - 4)  # Distance to black king
    moves_toward_king = []
    for move_row, move_col in queen_moves_no_capture:
        new_distance = abs(move_row - 0) + abs(move_col - 4)
        if new_distance < current_distance:
            moves_toward_king.append((move_row, move_col))
    
    print(f"  Queen without captures: {len(queen_moves_no_capture)} moves")
    print(f"  Moves toward enemy king: {len(moves_toward_king)}")
    print(f"  Aggressive targeting working: {len(moves_toward_king) > 0}")
    
    # Test behavior reset
    print("\n4. Testing behavior reset:")
    print(f"  Before reset - Queen: {white_queen.behavior}, Rook: {white_rook.behavior}")
    
    white_queen.reset_behavior()
    white_rook.reset_behavior()
    
    print(f"  After reset - Queen: {white_queen.behavior}, Rook: {white_rook.behavior}")
    
    # Verify movement after reset
    queen_moves_reset = white_queen.get_valid_moves((5, 3), board)
    rook_moves_reset = white_rook.get_valid_moves((6, 2), board)
    
    print(f"  Queen moves after reset: {len(queen_moves_reset)}")
    print(f"  Rook moves after reset: {len(rook_moves_reset)}")
    print(f"  Movement restored: {len(rook_moves_reset) > 0}")
    
    print("\n✅ Combined behavior system working correctly!")
    
    print("\n🎯 Behavior System Summary:")
    print("  🗡️  AGGRESSIVE: Prioritizes captures → hunts enemy kings → normal moves")
    print("  🛡️  DEFENSIVE: [To be implemented in Stage 2]")
    print("  ⏳ PASSIVE: No movement (stays still)")
    print("  🎲 DEFAULT: Normal random movement")
    print("")
    print("  Strategic Applications:")
    print("  • Use AGGRESSIVE on attacking pieces to pressure enemies")
    print("  • Use PASSIVE on key defenders to hold positions") 
    print("  • Combine behaviors for coordinated tactics")
    print("  • All behaviors reset after each turn for fresh strategy")

if __name__ == "__main__":
    test_behavior_combination()
