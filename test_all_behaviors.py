#!/usr/bin/env python3
"""
Test script for all three behaviors working together
"""

from autochess_pieces import *
from board import ChessBoard

def test_all_behaviors():
    print("Testing All Three Behaviors Together")
    print("="*50)
    
    # Create a battlefield scenario
    board = ChessBoard(8)
    
    # White pieces
    white_king = King("white")
    white_queen = Queen("white") 
    white_rook = Rook("white")
    white_bishop = Bishop("white")
    
    # Black pieces  
    black_king = King("black")
    black_queen = Queen("black")
    black_rook = Rook("black")
    black_pawn = Pawn("black")
    
    # Set up the board
    board.place_piece(white_king, (7, 4))      # White king bottom center
    board.place_piece(white_queen, (6, 3))     # Queen near king
    board.place_piece(white_rook, (5, 6))      # Rook further away
    board.place_piece(white_bishop, (4, 2))    # Bishop in middle
    
    board.place_piece(black_king, (0, 4))      # Black king top center
    board.place_piece(black_queen, (1, 3))     # Black queen near black king
    board.place_piece(black_rook, (2, 6))      # Black rook
    board.place_piece(black_pawn, (3, 3))      # Black pawn in middle
    
    print("Initial board setup:")
    print("  White King at (7,4), Queen at (6,3), Rook at (5,6), Bishop at (4,2)")
    print("  Black King at (0,4), Queen at (1,3), Rook at (2,6), Pawn at (3,3)")
    
    # Test 1: Passive behavior - no movement
    print("\n1. Testing passive behavior:")
    white_queen.set_behavior("passive")
    passive_moves = white_queen.get_valid_moves((6, 3), board)
    print(f"  White Queen (passive): {len(passive_moves)} moves (should be 0)")
    white_queen.reset_behavior()
    
    # Test 2: Aggressive behavior - hunt enemies
    print("\n2. Testing aggressive behavior:")
    white_rook.set_behavior("aggressive")
    aggressive_moves = white_rook.get_valid_moves((5, 6), board)
    
    # Check if can capture black rook
    can_capture_rook = (2, 6) in aggressive_moves
    
    # Check if targeting enemy pieces
    capture_moves = []
    for move in aggressive_moves:
        target = board.get_piece(move)
        if target and target.color != white_rook.color:
            capture_moves.append(move)
    
    print(f"  White Rook (aggressive): {len(aggressive_moves)} moves")
    print(f"  Can capture black rook at (2,6): {can_capture_rook}")
    print(f"  Total capture opportunities: {len(capture_moves)}")
    white_rook.reset_behavior()
    
    # Test 3: Defensive behavior - protect king
    print("\n3. Testing defensive behavior:")
    
    # Test defensive close to king (should hold position)
    white_queen.set_behavior("defensive")
    defensive_moves_close = white_queen.get_valid_moves((6, 3), board)
    distance_to_king = abs(6-7) + abs(3-4)  # Distance to white king
    
    print(f"  White Queen (defensive, {distance_to_king} blocks from king): {len(defensive_moves_close)} moves")
    print(f"  Expected: 0 moves (holding position within 5 blocks)")
    
    # Test defensive with capture opportunity
    # Move a black piece within capture range
    board.place_piece(black_pawn, (5, 3))  # Put pawn where queen can capture
    defensive_moves_capture = white_queen.get_valid_moves((6, 3), board)
    can_capture_pawn = (5, 3) in defensive_moves_capture
    
    print(f"  White Queen with capture opportunity: {len(defensive_moves_capture)} moves")
    print(f"  Can capture black pawn: {can_capture_pawn} (should prioritize capture)")
    
    # Clean up
    board.remove_piece((5, 3))
    
    # Test defensive far from king (should approach)
    white_bishop.set_behavior("defensive")
    bishop_distance = abs(4-7) + abs(2-4)
    defensive_moves_far = white_bishop.get_valid_moves((4, 2), board)
    
    print(f"  White Bishop (defensive, {bishop_distance} blocks from king): {len(defensive_moves_far)} moves")
    print(f"  Expected: >0 moves (approaching king beyond 5 blocks)")
    
    white_queen.reset_behavior()
    white_bishop.reset_behavior()
    
    # Test 4: Behavior interactions
    print("\n4. Testing behavior interactions:")
    
    # Set multiple pieces with different behaviors
    white_queen.set_behavior("aggressive")   # Hunt enemies
    white_bishop.set_behavior("defensive")   # Protect king
    black_queen.set_behavior("passive")      # Stay still
    
    white_aggressive = white_queen.get_valid_moves((6, 3), board)
    white_defensive = white_bishop.get_valid_moves((4, 2), board)
    black_passive = black_queen.get_valid_moves((1, 3), board)
    
    print(f"  White Queen (aggressive): {len(white_aggressive)} moves")
    print(f"  White Bishop (defensive): {len(white_defensive)} moves")  
    print(f"  Black Queen (passive): {len(black_passive)} moves")
    
    # Reset all behaviors
    white_queen.reset_behavior()
    white_bishop.reset_behavior() 
    black_queen.reset_behavior()
    
    print(f"\n✅ All behavior interaction tests completed!")
    print("\nBehavior Summary:")
    print("  🗡️ Aggressive: Captures enemies → hunts enemy kings")
    print("  🛡️ Defensive: Captures enemies → guards friendly king (≤5 blocks) → approaches king (>5 blocks)")
    print("  ⏳ Passive: No movement whatsoever")
    print("  🎲 Default: Normal random movement")

if __name__ == "__main__":
    test_all_behaviors()
