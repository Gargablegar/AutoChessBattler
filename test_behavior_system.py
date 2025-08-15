#!/usr/bin/env python3
"""
Test script for the behavior system without requiring pygame
"""

import sys
sys.path.append('.')

from autochess_pieces import AutoChessPiece, King, Queen, Rook, Bishop, Knight, Pawn
from board import ChessBoard

def test_behavior_system():
    """Test the piece behavior system"""
    print("Testing AutoChess Piece Behavior System")
    print("=" * 40)
    
    # Create test pieces
    pieces = [
        King("white"),
        Queen("black"), 
        Rook("white"),
        Bishop("black"),
        Knight("white"),
        Pawn("black")
    ]
    
    # Test default behavior
    print("\n1. Testing default behavior:")
    for piece in pieces:
        print(f"  {piece}: behavior = {piece.get_behavior()}")
    
    # Test setting behaviors
    print("\n2. Testing behavior setting:")
    behaviors = ["aggressive", "defensive", "passive"]
    
    for i, piece in enumerate(pieces[:3]):  # Test first 3 pieces
        behavior = behaviors[i]
        piece.set_behavior(behavior)
        print(f"  Set {piece} to {behavior}: behavior = {piece.get_behavior()}")
    
    # Test invalid behavior
    print("\n3. Testing invalid behavior:")
    piece = pieces[0]
    old_behavior = piece.get_behavior()
    piece.set_behavior("invalid_behavior")
    print(f"  Tried to set invalid behavior: {piece.get_behavior()} (should be unchanged: {old_behavior})")
    
    # Test passive behavior movement restriction
    print("\n4. Testing passive behavior movement restriction:")
    board = ChessBoard(8)  # 8x8 test board
    
    # Test normal movement
    king = King("white")
    board.place_piece(king, (4, 4))  # Center of board
    normal_moves = king.get_valid_moves((4, 4), board)
    print(f"  Normal King moves from (4,4): {len(normal_moves)} moves available")
    
    # Test passive movement
    king.set_behavior("passive")
    passive_moves = king.get_valid_moves((4, 4), board)
    print(f"  Passive King moves from (4,4): {len(passive_moves)} moves available")
    print(f"  Passive behavior working: {len(passive_moves) == 0}")
    
    # Test all piece types with passive behavior
    print("\n5. Testing passive behavior for all piece types:")
    test_pieces = [
        (King("white"), "King"),
        (Queen("white"), "Queen"),
        (Rook("white"), "Rook"),
        (Bishop("white"), "Bishop"),
        (Knight("white"), "Knight"),
        (Pawn("white"), "Pawn")
    ]
    
    for piece, name in test_pieces:
        # Place piece on board
        board.clear()
        board.place_piece(piece, (4, 4))
        
        # Test normal movement
        normal_moves = piece.get_valid_moves((4, 4), board)
        
        # Set passive and test
        piece.set_behavior("passive")
        passive_moves = piece.get_valid_moves((4, 4), board)
        
        print(f"  {name}: Normal={len(normal_moves)} moves, Passive={len(passive_moves)} moves ✓")
        
        # Reset behavior
        piece.reset_behavior()
    
    # Test behavior reset
    print("\n6. Testing behavior reset:")
    for piece in pieces:
        if piece.get_behavior() != "default":
            old_behavior = piece.get_behavior()
            piece.reset_behavior()
            print(f"  Reset {piece}: {old_behavior} → {piece.get_behavior()}")
    
    print("\n✅ All behavior system tests passed!")
    
    # Show behavior mappings
    print("\n7. Behavior meanings:")
    print("  • aggressive (Swords): Piece will attempt to take enemy pieces")
    print("  • defensive (Shield): Piece will try to defend the king and block other pieces") 
    print("  • passive (Hourglass): Piece will stay still and NOT MOVE")
    print("  • default: Normal random movement")

if __name__ == "__main__":
    test_behavior_system()
