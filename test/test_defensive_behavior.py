#!/usr/bin/env python3
"""
Test script for defensive behavior implementation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autochess_pieces import *
from board import ChessBoard

def test_defensive_behavior():
    print("Testing Defensive Behavior Implementation")
    print("="*50)
    
    # Test 1: Piece within 5 blocks of friendly king should hold position
    print("\n1. Testing defensive hold position (within 5 blocks):")
    board = ChessBoard(8)
    
    white_king = King("white")
    white_rook = Rook("white")
    
    # Place king and rook within 5 blocks of each other
    board.place_piece(white_king, (3, 3))
    board.place_piece(white_rook, (3, 6))  # 3 blocks away
    
    # Test normal vs defensive behavior
    normal_moves = white_rook._get_piece_moves((3, 6), board)
    white_rook.set_behavior("defensive")
    defensive_moves = white_rook.get_valid_moves((3, 6), board)
    
    distance = abs(3-3) + abs(6-3)  # Manhattan distance
    print(f"  King at (3,3), Rook at (3,6)")
    print(f"  Distance to friendly king: {distance} blocks")
    print(f"  Normal rook moves: {len(normal_moves)}")
    print(f"  Defensive rook moves: {len(defensive_moves)} (should be 0 - holding position)")
    print(f"  Defensive hold working: {len(defensive_moves) == 0}")
    
    # Test 2: Piece far from friendly king should move toward it
    print("\n2. Testing defensive approach (beyond 5 blocks):")
    board2 = ChessBoard(8)
    
    white_king2 = King("white")
    white_bishop = Bishop("white")
    
    # Place king and bishop more than 5 blocks apart
    board2.place_piece(white_king2, (0, 0))
    board2.place_piece(white_bishop, (7, 7))  # 14 blocks away
    
    normal_moves2 = white_bishop._get_piece_moves((7, 7), board2)
    white_bishop.set_behavior("defensive")
    defensive_moves2 = white_bishop.get_valid_moves((7, 7), board2)
    
    distance2 = abs(7-0) + abs(7-0)
    print(f"  King at (0,0), Bishop at (7,7)")
    print(f"  Distance to friendly king: {distance2} blocks")
    print(f"  Normal bishop moves: {len(normal_moves2)}")
    print(f"  Defensive bishop moves: {len(defensive_moves2)} (should move toward king)")
    
    # Check if moves are toward the king
    moves_toward_king = 0
    for move in defensive_moves2:
        move_distance = abs(move[0]-0) + abs(move[1]-0)
        if move_distance < distance2:  # Closer to king
            moves_toward_king += 1
    
    print(f"  Moves toward king: {moves_toward_king}/{len(defensive_moves2)}")
    print(f"  Defensive approach working: {moves_toward_king > 0}")
    
    # Test 3: Defensive piece should prioritize captures even when close to king
    print("\n3. Testing defensive capture priority:")
    board3 = ChessBoard(8)
    
    white_king3 = King("white")
    white_queen = Queen("white")
    black_pawn = Pawn("black")
    
    # Place pieces so queen is close to king but can capture
    board3.place_piece(white_king3, (4, 4))
    board3.place_piece(white_queen, (4, 6))  # 2 blocks from king
    board3.place_piece(black_pawn, (4, 7))   # Capturable by queen
    
    white_queen.set_behavior("defensive")
    defensive_moves3 = white_queen.get_valid_moves((4, 6), board3)
    
    distance3 = abs(4-4) + abs(6-4)
    can_capture = (4, 7) in defensive_moves3
    
    print(f"  King at (4,4), Queen at (4,6), Enemy pawn at (4,7)")
    print(f"  Distance to friendly king: {distance3} blocks (within 5)")
    print(f"  Queen can capture enemy pawn: {can_capture}")
    print(f"  Defensive moves: {len(defensive_moves3)}")
    print(f"  Capture priority working: {can_capture and len(defensive_moves3) >= 1}")
    
    # Test 4: Test different piece types with defensive behavior
    print("\n4. Testing defensive behavior for all piece types:")
    board4 = ChessBoard(8)
    
    pieces = [
        (King("white"), "King"),
        (Queen("white"), "Queen"), 
        (Rook("white"), "Rook"),
        (Bishop("white"), "Bishop"),
        (Knight("white"), "Knight"),
        (Pawn("white"), "Pawn")
    ]
    
    # Place friendly king
    friendly_king = King("white")
    board4.place_piece(friendly_king, (0, 0))
    
    for piece, name in pieces:
        if name == "King":
            continue  # Skip the king we're protecting
            
        # Place piece far from king
        board4.place_piece(piece, (7, 7))
        
        normal_moves = piece._get_piece_moves((7, 7), board4)
        piece.set_behavior("defensive")
        defensive_moves = piece.get_valid_moves((7, 7), board4)
        
        print(f"  {name}: Normal={len(normal_moves)} moves, Defensive={len(defensive_moves)} moves")
        
        # Clean up
        board4.remove_piece((7, 7))
    
    print(f"\n✅ All defensive behavior tests completed!")

if __name__ == "__main__":
    test_defensive_behavior()
