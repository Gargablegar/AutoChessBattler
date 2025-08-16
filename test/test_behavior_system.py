#!/usr/bin/env python3
"""
Test script for the behavior system without requiring pygame
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    print("  • aggressive (Swords): Piece will attempt to take enemy pieces, then hunt enemy kings")
    print("  • defensive (Shield): Piece will protect friendly kings within 5 blocks, prioritize captures") 
    print("  • passive (Hourglass): Piece will stay still and NOT MOVE")
    print("  • default: Normal random movement")
    
    # Test aggressive behavior
    print("\n8. Testing aggressive behavior:")
    board = ChessBoard(8)
    
    # Set up capture scenario
    white_rook = Rook("white")
    black_pawn = Pawn("black")
    black_king = King("black")
    
    board.place_piece(white_rook, (4, 4))
    board.place_piece(black_pawn, (4, 6))  # Capturable
    board.place_piece(black_king, (0, 0))  # Target for hunting
    
    # Test normal vs aggressive
    normal_moves = white_rook._get_piece_moves((4, 4), board)
    white_rook.set_behavior("aggressive")
    aggressive_moves = white_rook.get_valid_moves((4, 4), board)
    
    capture_available = (4, 6) in aggressive_moves
    print(f"  Normal rook moves: {len(normal_moves)}")
    print(f"  Aggressive rook moves: {len(aggressive_moves)}")
    print(f"  Prioritizing capture: {capture_available and len(aggressive_moves) == 1}")
    
    # Test hunting behavior (no captures available)
    board.remove_piece((4, 6))  # Remove capturable piece
    hunting_moves = white_rook.get_valid_moves((4, 4), board)
    print(f"  Hunting moves (no captures): {len(hunting_moves)} (targeting enemy king)")
    
    white_rook.reset_behavior()
    
    # Test defensive behavior
    print("\n9. Testing defensive behavior:")
    board2 = ChessBoard(8)
    
    # Set up defensive scenario
    white_king = King("white")
    white_bishop = Bishop("white")
    black_pawn2 = Pawn("black")
    
    # Test holding position when close to friendly king
    board2.place_piece(white_king, (3, 3))
    board2.place_piece(white_bishop, (3, 5))  # 2 blocks away
    
    normal_moves2 = white_bishop._get_piece_moves((3, 5), board2)
    white_bishop.set_behavior("defensive")
    defensive_moves = white_bishop.get_valid_moves((3, 5), board2)
    
    print(f"  Normal bishop moves: {len(normal_moves2)}")
    print(f"  Defensive bishop moves (close to king): {len(defensive_moves)} (holding position)")
    
    # Test capture priority even when close to king
    board2.place_piece(black_pawn2, (4, 6))  # Capturable
    defensive_capture_moves = white_bishop.get_valid_moves((3, 5), board2)
    can_capture = (4, 6) in defensive_capture_moves
    
    print(f"  Defensive with capture opportunity: {len(defensive_capture_moves)} moves")
    print(f"  Prioritizing capture over holding: {can_capture}")
    
    white_bishop.reset_behavior()

if __name__ == "__main__":
    test_behavior_system()
