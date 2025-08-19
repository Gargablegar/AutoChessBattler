#!/usr/bin/env python3
"""
AutoChess Game
A chess variant where players use a point-based system to place pieces on an n x n board.
Each player gets pieces on the side and can place them multiple times as long as they have points.

Usage: python main.py [board_size] [frontline] [turn_time] [points_rate]
Example: python main.py 16 3 0.5 10  (creates a 16x16 board with 3-row frontline, 0.5s move delay, 10 points/turn)
Default: 24x24 board with 2-row frontline, 0.5s move delay, and 5 points/turn if not specified
"""

# Pybag compatibility flag - set to True to enable web browser compatibility
DEBUG_PYBAG = False

import pygame
import sys
import random
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from autochess_pieces import (
    AutoChessPiece, King, Queen, Rook, Bishop, Knight, Pawn
)
from board import ChessBoard
from game_ui import GameUI
from debug import DebugManager

# Pybag compatibility imports
if DEBUG_PYBAG:
    import platform
    if platform.system() == "Emscripten":
        import asyncio


class AutoChessGame:
    """Main game controller for AutoChess."""
    
    def __init__(self, board_size: int = 24, frontline: int = 2, turn_time: float = 0.1, points_rate: int = 5, start_points: int = 20, traditional: bool = False, medium: bool = False):
        # Initialize pygame
        pygame.init()
        
        # Game state
        self.board = ChessBoard(size=board_size)  # Board size from parameter
        self.ui = GameUI(board_size=board_size)  # Pass the board size
        self.debug_manager = DebugManager(board_size=board_size)  # Debug functionality
        self.running = True
        self.current_player = "white"  # For UI display purposes, but both can place pieces
        self.turn_counter = 1
        self.frontline = frontline  # How many rows from king pieces can be placed
        self.error_message = ""  # Error message to display
        self.auto_turns = 1  # Number of turns to play automatically
        self.game_over = False  # Flag to track if game is over
        self.winner = ""  # Winner of the game
        self.turn_time = turn_time  # Delay between moves in seconds
        self.traditional = traditional  # Whether to use traditional chess starting layout
        
        # Points system
        self.points = {"white": start_points, "black": start_points}
        # Configuration: Points awarded to each player per turn (change this value to adjust economy)
        self.pointsRate = points_rate  # Points added per turn for each player (now from parameter)
        self.points_per_turn = self.pointsRate  # Keep backward compatibility
        
        # Available pieces for each player (templates that can be placed multiple times)
        self.available_pieces = {
            "white": [
                King("white"),
                Queen("white"),
                Rook("white"),
                Bishop("white"),
                Knight("white"),
                Pawn("white")
            ],
            "black": [
                King("black"),
                Queen("black"),
                Rook("black"),
                Bishop("black"),
                Knight("black"),
                Pawn("black")
            ]
        }
        
        # Piece costs
        self.piece_costs = {
            "King": 20,
            "Queen": 10,
            "Rook": 5.25,
            "Bishop": 3.5,
            "Knight": 3.5,
            "Pawn": 1
        }
        
        # Selected piece for placement
        self.selected_piece_for_placement: Optional[AutoChessPiece] = None
        self.placement_mode = False
        
        # Game mode: "placement" for placing pieces, "movement" for moving pieces
        self.game_mode = "placement"
        
        print("AutoChess Game Started!")
        print(f"Board size: {self.board.size}x{self.board.size}")
        print(f"Frontline distance: {self.frontline} rows from kings")
        print(f"Move delay: {self.turn_time}s between moves")
        print(f"Starting points: {self.points['white']} for each player")
        print(f"Points per turn: {self.pointsRate}")
        if traditional:
            print("Traditional chess starting layout enabled!")
        elif medium:
            print("Medium game mode enabled!")
        print("Both players can place pieces simultaneously! Click 'Play Turn' to make all pieces move.")
        print("Selected pieces stay selected for multiple placements. Right-click to deselect.")
        print("White pieces can be placed from frontline distance above their kings to the bottom of the board.")
        print("Black pieces can be placed from the top of the board to frontline distance below their kings.")
        
        # Place starting pieces (kings only, traditional layout, or medium layout)
        if traditional:
            self.place_traditional_starting_layout()
        elif medium:
            self.place_medium_starting_layout()
        else:
            self.place_starting_kings()
    
    def can_afford_piece(self, piece: AutoChessPiece, player: str) -> bool:
        """Check if player can afford to place this piece."""
        cost = self.piece_costs.get(piece.__class__.__name__, 0)
        return self.points[player] >= cost
    
    def get_king_positions(self, color: str) -> List[Tuple[int, int]]:
        """Get all positions of kings for the specified color."""
        king_positions = []
        all_pieces = self.board.get_all_pieces()
        
        for piece, (row, col) in all_pieces:
            if piece.color == color and piece.__class__.__name__ == "King":
                king_positions.append((row, col))
        
        return king_positions
    
    def is_within_frontline(self, row: int, col: int, color: str) -> bool:
        """Check if position is within frontline distance from any king of the same color."""
        king_positions = self.get_king_positions(color)
        
        if not king_positions:
            # If no kings exist for this color, allow placement anywhere
            return True
        
        for king_row, king_col in king_positions:
            if color == "white":
                # White pieces can be placed from frontline distance above their king
                # all the way to the bottom of the board
                if king_row - self.frontline <= row <= self.board.size - 1:
                    return True
            else:  # black
                # Black pieces can be placed from frontline distance below their king
                # all the way to the top of the board
                if 0 <= row <= king_row + self.frontline:
                    return True
        
        return False
    
    def get_frontline_zones(self, color: str) -> List[Tuple[int, int, int, int, Tuple[int, int, int]]]:
        """Get all frontline zones for a color as list of (min_row, max_row, min_col, max_col, zone_color)."""
        king_positions = self.get_king_positions(color)
        zones = []
        
        # Determine zone color based on player color
        zone_color = (255, 255, 255) if color == "white" else (0, 0, 0)  # White or Black
        
        for king_row, king_col in king_positions:
            if color == "white":
                # White zone extends from frontline distance above the king to the bottom of the board
                min_row = max(0, king_row - self.frontline)
                max_row = self.board.size - 1
            else:  # black
                # Black zone extends from the top of the board to frontline distance below the king
                min_row = 0
                max_row = min(self.board.size - 1, king_row + self.frontline)
            
            zones.append((min_row, max_row, 0, self.board.size - 1, zone_color))
        
        return zones
    
    def check_win_condition(self) -> bool:
        """Check if the game has ended due to one player having no kings"""
        white_kings = self.get_king_positions("white")
        black_kings = self.get_king_positions("black")
        
        white_king_count = len(white_kings)
        black_king_count = len(black_kings)
        
        if white_king_count == 0 and black_king_count == 0:
            # Both players have no kings - this shouldn't happen normally
            self.game_over = True
            self.winner = "Draw - No kings remaining"
            print(f"\n🏆 GAME OVER: {self.winner}")
            return True
        elif white_king_count == 0:
            # White has no kings - Black wins
            self.game_over = True
            self.winner = "Black wins!"
            print(f"\n🏆 GAME OVER: {self.winner} (White has no kings remaining)")
            return True
        elif black_king_count == 0:
            # Black has no kings - White wins
            self.game_over = True
            self.winner = "White wins!"
            print(f"\n🏆 GAME OVER: {self.winner} (Black has no kings remaining)")
            return True
        
        # Game continues - log current king counts for debugging
        if white_king_count > 0 and black_king_count > 0:
            print(f"Kings remaining - White: {white_king_count}, Black: {black_king_count}")
        
        return False
    
    def deduct_piece_cost(self, piece: AutoChessPiece, player: str):
        """Deduct the cost of placing a piece."""
        cost = self.piece_costs.get(piece.__class__.__name__, 0)
        self.points[player] -= cost
        print(f"{player.capitalize()} placed {piece.__class__.__name__} for {cost} points. Remaining: {self.points[player]}")
    
    def add_turn_points(self, player: str):
        """Add points at the start of each turn."""
        self.points[player] += self.pointsRate
        print(f"{player.capitalize()} gained {self.pointsRate} points. Total: {self.points[player]}")
    
    def select_piece_for_placement(self, piece: AutoChessPiece):
        """Select a piece for placement on the board."""
        # Only clear conflicting UI states, don't clear selection modes
        self.ui.auto_turns_input_active = False
        self.ui.hide_behavior_icons()
        
        # Determine which player is trying to place this piece based on piece color
        piece_owner = piece.color
        
        if not self.can_afford_piece(piece, piece_owner):
            self.error_message = f"Not enough points to place {piece.__class__.__name__}! Cost: {self.piece_costs.get(piece.__class__.__name__, 0)}, Available: {self.points[piece_owner]}"
            return
        
        self.selected_piece_for_placement = piece
        self.placement_mode = True
        self.error_message = ""  # Clear any error message when selecting a piece
        print(f"Selected {piece.color} {piece.__class__.__name__} for placement. Click on the board to place it (or right-click to deselect).")
    
    def place_piece_on_board(self, row: int, col: int) -> bool:
        """Place the selected piece on the board."""
        if not self.selected_piece_for_placement:
            return False
        
        # Check if the player can still afford this piece
        piece_owner = self.selected_piece_for_placement.color
        if not self.can_afford_piece(self.selected_piece_for_placement, piece_owner):
            self.error_message = f"Not enough points to place {self.selected_piece_for_placement.__class__.__name__}! Cost: {self.piece_costs.get(self.selected_piece_for_placement.__class__.__name__, 0)}, Available: {self.points[piece_owner]}"
            self.deselect_piece()  # Auto-deselect if can't afford
            return False
        
        # Check if position is valid (get_piece returns None for invalid positions)
        if not (0 <= row < self.board.size and 0 <= col < self.board.size):
            self.error_message = "Invalid position!"
            return False
        
        if self.board.get_piece((row, col)) is not None:
            self.error_message = "Position already occupied!"
            return False
        
        # Check frontline restrictions
        if not self.is_within_frontline(row, col, piece_owner):
            self.error_message = "Not in front line limits"
            return False
        
        # Create a new instance of the piece (don't remove from available pieces)
        piece_class = self.selected_piece_for_placement.__class__
        piece_owner = self.selected_piece_for_placement.color
        new_piece = piece_class(piece_owner)
        
        # Place the piece on the board
        success = self.board.place_piece(new_piece, (row, col))
        if success:
            self.deduct_piece_cost(self.selected_piece_for_placement, piece_owner)
            print(f"Placed {piece_owner} {new_piece.__class__.__name__} at ({row}, {col})")
            self.error_message = ""  # Clear any error message
            
            # Keep the piece selected for multiple placements - don't clear selection
            # self.selected_piece_for_placement = None
            # self.placement_mode = False
            
            return True
        
        return False
    
    def place_starting_kings(self):
        """Place starting kings on random squares"""
        # Place white king on bottom row (row 23)
        white_king_col = random.randint(0, self.board.size - 1)
        white_king = King("white")
        self.board.place_piece(white_king, (self.board.size - 1, white_king_col))
        print(f"White King placed at ({self.board.size - 1}, {white_king_col})")
        
        # Place black king on top row (row 0)
        black_king_col = random.randint(0, self.board.size - 1)
        black_king = King("black")
        self.board.place_piece(black_king, (0, black_king_col))
        print(f"Black King placed at (0, {black_king_col})")
    
    def place_traditional_starting_layout(self):
        """Place pieces in traditional chess starting positions"""
        print("Setting up traditional chess starting layout...")
        
        # Ensure board is at least 8x8 for traditional layout
        if self.board.size < 8:
            print(f"Warning: Board size {self.board.size}x{self.board.size} is too small for traditional layout. Need at least 8x8.")
            # Fall back to just placing kings
            self.place_starting_kings()
            return
        
        # Calculate center positions for 8x8 layout on larger boards
        center_offset = (self.board.size - 8) // 2
        
        # Traditional piece order: Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        # Place white pieces (bottom two rows)
        white_back_row = self.board.size - 1 - center_offset  # Bottom row
        white_pawn_row = self.board.size - 2 - center_offset  # Second from bottom
        
        for col in range(8):
            # Place white back row pieces
            piece_class = piece_order[col]
            white_piece = piece_class("white")
            board_col = center_offset + col
            self.board.place_piece(white_piece, (white_back_row, board_col))
            print(f"White {piece_class.__name__} placed at ({white_back_row}, {board_col})")
            
            # Place white pawns
            white_pawn = Pawn("white")
            self.board.place_piece(white_pawn, (white_pawn_row, board_col))
            print(f"White Pawn placed at ({white_pawn_row}, {board_col})")
        
        # Place black pieces (top two rows)
        black_back_row = center_offset  # Top row
        black_pawn_row = center_offset + 1  # Second from top
        
        for col in range(8):
            # Place black back row pieces
            piece_class = piece_order[col]
            black_piece = piece_class("black")
            board_col = center_offset + col
            self.board.place_piece(black_piece, (black_back_row, board_col))
            print(f"Black {piece_class.__name__} placed at ({black_back_row}, {board_col})")
            
            # Place black pawns
            black_pawn = Pawn("black")
            self.board.place_piece(black_pawn, (black_pawn_row, board_col))
            print(f"Black Pawn placed at ({black_pawn_row}, {board_col})")
        
        print("Traditional chess layout complete!")
        print(f"White pieces: rows {white_pawn_row}-{white_back_row}, columns {center_offset}-{center_offset + 7}")
        print(f"Black pieces: rows {black_back_row}-{black_pawn_row}, columns {center_offset}-{center_offset + 7}")
    
    def place_medium_starting_layout(self):
        """Place pieces for medium game mode - random placement with multiple pieces per type"""
        print("Setting up medium game mode layout...")
        print("16x16 board with randomly placed pieces for each player")
        
        # First place kings (required for frontline calculation)
        self.place_starting_kings()
        
        # Generate random number of pawns (same for both players)
        num_pawns = random.randint(5, 12)
        print(f"Each player will get {num_pawns} pawns")
        
        # Define piece counts for medium mode
        piece_counts = {
            "Pawn": num_pawns,
            "Rook": 3,
            "Bishop": 3,
            "Knight": 4
        }
        
        # Place pieces for each player
        for color in ["white", "black"]:
            print(f"\nPlacing {color} pieces...")
            
            for piece_type, count in piece_counts.items():
                placed_count = 0
                attempts = 0
                max_attempts = 1000  # Prevent infinite loops
                
                while placed_count < count and attempts < max_attempts:
                    attempts += 1
                    
                    # Get random position within player's territory
                    if color == "white":
                        # White territory: bottom half of board
                        row = random.randint(8, self.board.size - 1)
                    else:
                        # Black territory: top half of board
                        row = random.randint(0, 7)
                    
                    col = random.randint(0, self.board.size - 1)
                    
                    # Check if position is empty and within frontline
                    if (self.board.get_piece((row, col)) is None and 
                        self.is_within_frontline(row, col, color)):
                        
                        # Create and place the piece
                        if piece_type == "Pawn":
                            piece = Pawn(color)
                        elif piece_type == "Rook":
                            piece = Rook(color)
                        elif piece_type == "Bishop":
                            piece = Bishop(color)
                        elif piece_type == "Knight":
                            piece = Knight(color)
                        
                        success = self.board.place_piece(piece, (row, col))
                        if success:
                            placed_count += 1
                            print(f"{color.capitalize()} {piece_type} placed at ({row}, {col}) - {placed_count}/{count}")
                
                if placed_count < count:
                    print(f"Warning: Could only place {placed_count}/{count} {color} {piece_type}s")
        
        print("\nMedium game mode layout complete!")
        
        # Count and report total pieces placed
        white_pieces = 0
        black_pieces = 0
        for piece, (row, col) in self.board.get_all_pieces():
            if piece.color == "white":
                white_pieces += 1
            else:
                black_pieces += 1
        
        print(f"Total pieces placed - White: {white_pieces}, Black: {black_pieces}")
    
    def play_turn(self):
        """Execute a turn - make all pieces move randomly and give both players points"""
        print(f"\n🎮 PLAYING TURN {self.turn_counter} with {self.auto_turns} move rounds...")
        
        # Switch to movement mode during the turn
        previous_mode = self.game_mode
        self.game_mode = "movement"
        
        # Track kings at the start of the turn
        initial_white_kings = len(self.get_king_positions("white"))
        initial_black_kings = len(self.get_king_positions("black"))
        print(f"Turn start - White kings: {initial_white_kings}, Black kings: {initial_black_kings}")
        
        if not self.board.get_all_pieces():
            print("No pieces on board to move!")
        else:
            total_moves_made = 0
            turn_ended_early = False
            
            # Execute multiple move rounds based on auto_turns setting
            for move_round in range(self.auto_turns):
                if turn_ended_early:
                    print(f"Turn ended early due to king elimination after {move_round} move rounds")
                    break
                    
                if self.auto_turns > 1:
                    print(f"  === Move Round {move_round + 1} of {self.auto_turns} ===")
                
                # Get current piece positions at the start of this round
                current_pieces = self.board.get_all_pieces()
                moves_this_round = 0
                
                # Create a shuffled list of pieces to ensure fair movement order
                piece_list = [(piece, pos) for piece, pos in current_pieces]
                random.shuffle(piece_list)
                
                for piece, (row, col) in piece_list:
                    # Verify piece is still at this position (might have been captured)
                    current_piece_at_position = self.board.get_piece((row, col))
                    if current_piece_at_position != piece:
                        continue  # Piece was captured or moved, skip
                    
                    valid_moves = piece.get_valid_moves((row, col), self.board)
                    
                    # Check if piece has passive behavior
                    if piece.behavior == "passive":
                        # Passive pieces don't move - provide feedback
                        if self.auto_turns <= 3:  # Only show message for small auto-turns to avoid spam
                            print(f"    {piece.color.capitalize()} {piece.__class__.__name__} staying still (passive behavior)")
                        continue
                    
                    if valid_moves:
                        # Filter moves to only include empty squares or enemy pieces
                        available_moves = []
                        for move_row, move_col in valid_moves:
                            target_piece = self.board.get_piece((move_row, move_col))
                            if target_piece is None or target_piece.color != piece.color:
                                available_moves.append((move_row, move_col))
                        
                        if available_moves:
                            # For aggressive pieces, provide additional context
                            move_context = ""
                            if piece.behavior == "aggressive":
                                # Check if we're capturing
                                capture_moves = [pos for pos in available_moves 
                                               if self.board.get_piece(pos) is not None]
                                if capture_moves:
                                    move_context = " (aggressive - seeking capture)"
                                else:
                                    move_context = " (aggressive - hunting enemy king)"
                            elif piece.behavior == "defensive":
                                # Check if we're capturing
                                capture_moves = [pos for pos in available_moves 
                                               if self.board.get_piece(pos) is not None]
                                if capture_moves:
                                    move_context = " (defensive - capturing threat)"
                                else:
                                    # Check distance to friendly king
                                    friendly_kings = piece._find_friendly_kings(self.board)
                                    if friendly_kings:
                                        nearest_king = min(friendly_kings, key=lambda k: abs(row - k[0]) + abs(col - k[1]))
                                        distance = abs(row - nearest_king[0]) + abs(col - nearest_king[1])
                                        if distance <= 5:
                                            move_context = " (defensive - guarding king)"
                                        else:
                                            move_context = " (defensive - approaching king)"
                            
                            # Pick a random valid move
                            target_row, target_col = random.choice(available_moves)
                            target_piece = self.board.get_piece((target_row, target_col))
                            
                            # Make the move
                            success = self.board.move_piece((row, col), (target_row, target_col))
                            if success:
                                moves_this_round += 1
                                total_moves_made += 1
                                if target_piece:
                                    print(f"    {piece.color.capitalize()} {piece.__class__.__name__} captured {target_piece.color} {target_piece.__class__.__name__} ({row},{col}) → ({target_row},{target_col}){move_context}")
                                    
                                    # Check if the captured piece was a king - if so, check win condition immediately
                                    if target_piece.__class__.__name__ == "King":
                                        print(f"    🔥 KING CAPTURED! {target_piece.color.capitalize()} king eliminated!")
                                        # Check if this capture ended the game
                                        if self.check_win_condition():
                                            print(f"    ⚡ Game ends immediately - {self.winner}")
                                            turn_ended_early = True
                                            break  # Break out of piece movement loop
                                else:
                                    print(f"    {piece.color.capitalize()} {piece.__class__.__name__} moved ({row},{col}) → ({target_row},{target_col}){move_context}")
                                
                                # Add delay between moves if turn_time > 0
                                if self.turn_time > 0:
                                    # Update the display to show the move immediately
                                    self.update_display_during_moves()
                                    # Wait for the specified time
                                    pygame.time.wait(int(self.turn_time * 1000))  # Convert to milliseconds
                
                if self.auto_turns > 1:
                    print(f"  Round {move_round + 1} complete: {moves_this_round} moves made")
                elif moves_this_round > 0:
                    print(f"  {moves_this_round} moves made")
            
            if turn_ended_early:
                print(f"Turn ended early after {total_moves_made} moves due to king elimination.")
            else:
                print(f"Turn complete! {total_moves_made} total moves made across {self.auto_turns} move rounds.")
        
        # Only continue if the game hasn't ended
        if not self.game_over:
            # Both players gain points at the end of each turn
            self.points["white"] += self.pointsRate
            self.points["black"] += self.pointsRate
            print(f"Both players gained {self.pointsRate} points. White: {self.points['white']}, Black: {self.points['black']}")
            
            # Piece behaviors are now persistent - they keep their behavior until manually changed
            # (Removed automatic behavior reset)
            # self.reset_all_piece_behaviors()
            
            # Increment turn counter but don't switch players - both can continue placing pieces
            self.turn_counter += 1
            print("Both players can continue placing pieces for the next turn!")
            
            # Check for win condition after the turn (in case there were no captures but other conditions)
            self.check_win_condition()
        else:
            print("🏁 Game has ended - no points awarded and turn counter not incremented.")
        
        # Switch back to placement mode after the turn
        self.game_mode = "placement"
    
    def clear_all_force_move_targets(self):
        """Clear force move targets from all pieces after a turn is played"""
        print("Clearing all force move targets...")
        cleared_count = 0
        for piece, (row, col) in self.board.get_all_pieces():
            if piece.has_force_move_target():
                piece.clear_force_move_target()
                cleared_count += 1
        if cleared_count > 0:
            print(f"Cleared {cleared_count} force move targets")
    
    def reset_all_piece_behaviors(self):
        """Manually reset all piece behaviors to default (no longer called automatically)"""
        pieces_with_behavior = []
        aggressive_pieces_count = 0
        passive_pieces_count = 0
        defensive_pieces_count = 0
        
        for piece, pos in self.board.get_all_pieces():
            if piece.behavior != "default":
                pieces_with_behavior.append(f"{piece.color} {piece.piece_type}")
                if piece.behavior == "aggressive":
                    aggressive_pieces_count += 1
                elif piece.behavior == "passive":
                    passive_pieces_count += 1
                elif piece.behavior == "defensive":
                    defensive_pieces_count += 1
                piece.reset_behavior()
        
        if pieces_with_behavior:
            print(f"Manually reset behaviors for: {', '.join(pieces_with_behavior)}")
            behavior_summary = []
            if aggressive_pieces_count > 0:
                behavior_summary.append(f"{aggressive_pieces_count} aggressive")
            if defensive_pieces_count > 0:
                behavior_summary.append(f"{defensive_pieces_count} defensive")
            if passive_pieces_count > 0:
                behavior_summary.append(f"{passive_pieces_count} passive")
            
            if behavior_summary:
                print(f"  → {', '.join(behavior_summary)} pieces returned to normal movement")
        else:
            print("No pieces with special behaviors found to reset")
    
    def play_auto_turns(self):
        """Play a single turn where pieces move the number of times specified in auto_turns"""
        print(f"\n🔄 EXECUTING TURN WITH {self.auto_turns} MOVE ROUNDS (DEBUG: auto_turns = {self.auto_turns})...")
        self.play_turn()
        print(f"✅ Turn completed with {self.auto_turns} move rounds!")
    
    def deselect_piece(self):
        """Deselect the currently selected piece and hide behavior icons."""
        if self.selected_piece_for_placement:
            print(f"Deselected {self.selected_piece_for_placement.color} {self.selected_piece_for_placement.__class__.__name__}")
            self.selected_piece_for_placement = None
            self.placement_mode = False
        
        # Clear error message when deselecting
        self.error_message = ""
        
        # Also hide behavior icons
        self.ui.hide_behavior_icons()
    
    def handle_piece_selection_click(self, mouse_pos: Tuple[int, int]):
        """Handle clicks on the piece selection area."""
        # Check both white and black piece areas, regardless of current_player
        white_piece_index = self.ui.get_clicked_piece(mouse_pos, "white")
        black_piece_index = self.ui.get_clicked_piece(mouse_pos, "black")
        
        if white_piece_index is not None and 0 <= white_piece_index < len(self.available_pieces["white"]):
            piece = self.available_pieces["white"][white_piece_index]
            # If clicking the same piece that's already selected, deselect it
            if (self.selected_piece_for_placement and 
                self.selected_piece_for_placement.color == piece.color and 
                self.selected_piece_for_placement.__class__.__name__ == piece.__class__.__name__):
                self.deselect_piece()
            else:
                self.select_piece_for_placement(piece)
        elif black_piece_index is not None and 0 <= black_piece_index < len(self.available_pieces["black"]):
            piece = self.available_pieces["black"][black_piece_index]
            # If clicking the same piece that's already selected, deselect it
            if (self.selected_piece_for_placement and 
                self.selected_piece_for_placement.color == piece.color and 
                self.selected_piece_for_placement.__class__.__name__ == piece.__class__.__name__):
                self.deselect_piece()
            else:
                self.select_piece_for_placement(piece)
    
    def handle_board_click(self, mouse_pos: Tuple[int, int]):
        """Handle clicks on the game board."""
        board_pos = self.ui.get_board_position(mouse_pos)
        if not board_pos:
            return
        
        row, col = board_pos
        
        # Debug output
        print(f"Board click - Active selection color: {self.ui.active_selection_color}")
        print(f"Select mode states: {self.ui.select_mode}")
        print(f"Active action button: {self.ui.active_action_button}")
        print(f"Dragging selection: {self.ui.dragging_selection}")
        print(f"Force move active color: {self.ui.force_move_active_color}")
        
        # Check if we're in force move mode
        if self.ui.force_move_active_color:
            piece = self.board.get_piece((row, col))
            
            # If no piece is selected for force move yet
            if not self.ui.has_force_move_selection():
                # Try to select a piece of the active color
                if piece and piece.color == self.ui.force_move_active_color:
                    success = self.ui.select_piece_for_force_move(piece, (row, col))
                    if success:
                        self.error_message = f"Selected {piece.piece_type}. Now click target square."
                    return
                else:
                    self.error_message = f"Select a {self.ui.force_move_active_color} piece first."
                    return
            else:
                # A piece is already selected, this click is for target selection
                selected_piece = self.ui.force_move_selected_piece
                selected_pos = self.ui.force_move_selected_position
                
                # Check if clicking on the same piece (deselect)
                if piece == selected_piece:
                    self.ui.clear_force_move_selection()
                    self.error_message = f"Piece deselected. Select a piece to move."
                    return
                
                # Check if clicking on another piece of the same color (select different piece)
                if piece and piece.color == self.ui.force_move_active_color:
                    success = self.ui.select_piece_for_force_move(piece, (row, col))
                    if success:
                        self.error_message = f"Selected {piece.piece_type}. Now click target square."
                    return
                
                # This is a target selection - set force move target
                force_move_cost = 1
                player_color = self.ui.force_move_active_color
                
                # Check if player has enough points for force move
                if self.points[player_color] < force_move_cost:
                    self.error_message = f"Not enough points! Force move costs {force_move_cost} point."
                    return
                
                try:
                    # Deduct the cost and set the target
                    self.points[player_color] -= force_move_cost
                    selected_piece.set_force_move_target((row, col))
                    self.error_message = f"{selected_piece.piece_type} will move toward ({row}, {col}) next turn. Cost: {force_move_cost} point. Remaining: {self.points[player_color]}"
                    # Clear the force move selection but stay in force move mode for next piece
                    self.ui.clear_force_move_selection()
                    print(f"Set force move target for {selected_piece.piece_type} to ({row}, {col}) for {force_move_cost} point. {player_color} has {self.points[player_color]} points remaining.")
                except Exception as e:
                    # If there was an error, refund the points
                    self.points[player_color] += force_move_cost
                    self.error_message = f"Error setting target: {str(e)}"
                return
        
        # Check if we're in select mode - start drag selection
        if self.ui.active_selection_color and self.ui.select_mode[self.ui.active_selection_color]:
            print(f"Starting drag selection for {self.ui.active_selection_color} at {mouse_pos}")
            self.ui.start_drag_selection(mouse_pos)
            return
        
        # Check if we're in placement mode
        if self.placement_mode and self.selected_piece_for_placement:
            self.place_piece_on_board(row, col)
        else:
            # Check if there's a piece at this position for behavior selection
            piece = self.board.get_piece((row, col))
            if piece:
                # Show behavior icons for this piece
                self.ui.show_behavior_icons(piece, (row, col))
            else:
                # Hide behavior icons if clicking on empty square
                self.ui.hide_behavior_icons()
                # Clear error message when clicking on empty board space
                self.error_message = ""
    
    def render_game(self):
        """Render the game with debug modes applied if enabled"""
        # Get the display message
        display_message = self.error_message
        if self.game_over:
            display_message = f"{self.winner} wins!" if self.winner else "Game ended in a draw!"
        
        # Show AutoTurns input instruction when the field is active
        if self.ui.auto_turns_input_active and not display_message:
            display_message = "Type a number (auto-applies) or press Enter to finish."
        
        # Check if any debug fog of war modes are active
        debug_modes = self.ui.get_debug_active_modes()
        fog_of_war_active = debug_modes.get("white_fog", False) or debug_modes.get("black_fog", False)
        
        # Get frontline zones for rendering (only when fog of war is active or piece is being placed)
        frontline_zones = []
        if fog_of_war_active or self.selected_piece_for_placement:
            frontline_zones = self.get_frontline_zones("white") + self.get_frontline_zones("black")
        
        if debug_modes.get("white_fog", False):
            # Render with white fog of war
            self.render_with_white_fog_of_war(display_message, frontline_zones)
        elif debug_modes.get("black_fog", False):
            # Render with black fog of war
            self.render_with_black_fog_of_war(display_message, frontline_zones)
        elif debug_modes.get("heat_map", False):
            # Render with heat map overlay
            self.render_with_heat_map(display_message, frontline_zones)
        else:
            # Render normally (debug off)
            self.render_normal(display_message, frontline_zones)
    
    def render_normal(self, display_message: str, frontline_zones: List[Tuple[int, int, int, int]]):
        """Render the game normally without debug effects"""
        self.ui.render(
            board=self.board,
            white_pieces=self.available_pieces["white"],
            black_pieces=self.available_pieces["black"],
            turn_counter=self.turn_counter,
            player_points=self.points,
            selected_piece=self.selected_piece_for_placement,
            piece_costs=self.piece_costs,
            error_message=display_message,
            frontline_zones=frontline_zones,
            auto_turns=self.auto_turns
        )
    
    def render_with_white_fog_of_war(self, display_message: str, frontline_zones: List[Tuple[int, int, int, int]]):
        """Render the game with white fog of war applied"""
        # Clear screen
        self.ui.screen.fill(self.ui.colors['background'])
        
        # Render side panels and top panel normally
        self.ui.render_side_panels(
            self.available_pieces["white"],
            self.available_pieces["black"],
            self.points,
            self.selected_piece_for_placement,
            self.piece_costs
        )
        self.ui.render_top_panel(self.turn_counter, self.auto_turns)
        self.ui.render_error_message(display_message)
        
        # Render board with fog of war
        self.debug_manager.render_white_fog_of_war(
            self.ui.screen,
            self.board,
            self.ui,
            frontline_zones
        )
        
        # Render behavior icons on top of everything else
        if self.ui.behavior_icons_visible:
            self.ui.render_behavior_icons()

        # Render selection box and selected pieces if active
        if self.ui.select_mode['white'] or self.ui.select_mode['black']:
            self.ui.render_selection_overlay()
        
        # Render selected pieces highlights
        if any(self.ui.selected_pieces_group.values()):
            self.ui.render_selected_pieces(self.board)
        
        # Render force move highlights and status
        if any(self.ui.force_move_mode.values()):
            self.ui.render_force_move_highlights(self.board)
            
        # Update display
        pygame.display.flip()
    
    def render_with_black_fog_of_war(self, display_message: str, frontline_zones: List[Tuple[int, int, int, int]]):
        """Render the game with black fog of war applied"""
        # Clear screen
        self.ui.screen.fill(self.ui.colors['background'])
        
        # Render side panels and top panel normally
        self.ui.render_side_panels(
            self.available_pieces["white"],
            self.available_pieces["black"],
            self.points,
            self.selected_piece_for_placement,
            self.piece_costs
        )
        self.ui.render_top_panel(self.turn_counter, self.auto_turns)
        self.ui.render_error_message(display_message)
        
        # Render board with black fog of war
        self.debug_manager.render_black_fog_of_war(
            self.ui.screen,
            self.board,
            self.ui,
            frontline_zones
        )
        
        # Render behavior icons on top of everything else
        if self.ui.behavior_icons_visible:
            self.ui.render_behavior_icons()

        # Render selection box and selected pieces if active
        if self.ui.select_mode['white'] or self.ui.select_mode['black']:
            self.ui.render_selection_overlay()
        
        # Render selected pieces highlights
        if any(self.ui.selected_pieces_group.values()):
            self.ui.render_selected_pieces(self.board)
        
        # Render force move highlights and status
        if any(self.ui.force_move_mode.values()):
            self.ui.render_force_move_highlights(self.board)
            
        # Update display
        pygame.display.flip()
    
    def render_with_heat_map(self, display_message: str, frontline_zones: List[Tuple[int, int, int, int]]):
        """Render the game with heat map overlay showing piece movement possibilities"""
        # Clear screen
        self.ui.screen.fill(self.ui.colors['background'])
        
        # Render side panels and top panel normally
        self.ui.render_side_panels(
            self.available_pieces["white"],
            self.available_pieces["black"],
            self.points,
            self.selected_piece_for_placement,
            self.piece_costs
        )
        self.ui.render_top_panel(self.turn_counter, self.auto_turns)
        self.ui.render_error_message(display_message)
        
        # Render board with heat map overlay
        self.debug_manager.render_heat_map(
            self.ui.screen,
            self.board,
            self.ui
        )
        
        # Render frontline zones if provided
        if frontline_zones:
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                zone_x = self.ui.side_panel_width + min_col * self.ui.square_size
                zone_y = self.ui.top_panel_height + min_row * self.ui.square_size
                zone_width = (max_col - min_col + 1) * self.ui.square_size
                zone_height = (max_row - min_row + 1) * self.ui.square_size
                pygame.draw.rect(self.ui.screen, zone_color, 
                               (zone_x - 3, zone_y - 3, zone_width + 6, zone_height + 6), 3)
        
        # Render behavior icons on top of everything else
        if self.ui.behavior_icons_visible:
            self.ui.render_behavior_icons()

        # Render selection box and selected pieces if active
        if self.ui.select_mode['white'] or self.ui.select_mode['black']:
            self.ui.render_selection_overlay()
        
        # Render selected pieces highlights
        if any(self.ui.selected_pieces_group.values()):
            self.ui.render_selected_pieces(self.board)
        
        # Render force move highlights and status
        if any(self.ui.force_move_mode.values()):
            self.ui.render_force_move_highlights(self.board)
            
        # Update display
        pygame.display.flip()
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle all mouse clicks."""
        # Don't allow interactions if game is over
        if self.game_over:
            return
        
        # Check if debug dropdown was clicked first
        if self.ui.is_click_on_debug_dropdown(mouse_pos):
            self.ui.toggle_debug_dropdown()
            return
        
        # Check if debug dropdown option was clicked
        debug_option = self.ui.handle_debug_dropdown_click(mouse_pos)
        if debug_option:
            print(f"Debug option selected: {debug_option}")
            return
        
        # Close debug dropdown if clicking outside of it
        self.ui.close_debug_dropdown_if_outside_click(mouse_pos)
        
        # Check if an action button was clicked first
        action_click = self.ui.handle_action_button_click(mouse_pos)
        if action_click:
            # Clear error message when clicking action buttons
            self.error_message = ""
            color, action = action_click
            if action == 'select':
                # Toggle selection mode - if already active, turn it off
                if (self.ui.active_action_button == (color, 'select') and 
                    self.ui.select_mode[color] and 
                    self.ui.active_selection_color == color):
                    print(f"Stopping select mode for {color} player")
                    self.ui.stop_select_mode(color)
                else:
                    print(f"Starting select mode for {color} player")
                    self.ui.start_select_mode(color)
                return
            elif action == 'move':
                # Toggle force move mode - if already active, turn it off
                if (self.ui.active_action_button == (color, 'move') and 
                    self.ui.force_move_mode[color] and 
                    self.ui.force_move_active_color == color):
                    print(f"Stopping force move mode for {color} player")
                    self.ui.stop_force_move_mode(color)
                else:
                    # Check if player has enough points for force move
                    force_move_cost = 1
                    if self.points[color] < force_move_cost:
                        self.error_message = f"Not enough points! Force move costs {force_move_cost} point. {color.capitalize()} has {self.points[color]} points."
                    else:
                        print(f"Starting force move mode for {color} player")
                        self.ui.start_force_move_mode(color)
                return
            elif action == 'upgrade':
                print(f"Upgrade not implemented for {color} player")
                return

        # Check if a behavior icon was clicked
        clicked_behavior = self.ui.get_clicked_behavior_icon(mouse_pos)
        if clicked_behavior:
            # Clear error message when setting behavior
            self.error_message = ""
            # Check if we're setting behavior for a group of selected pieces
            if self.ui.active_selection_color and self.ui.selected_pieces_group[self.ui.active_selection_color]:
                # Apply behavior to all selected pieces
                selected_pieces = self.ui.selected_pieces_group[self.ui.active_selection_color]
                for piece in selected_pieces:
                    piece.set_behavior(clicked_behavior)
                print(f"Set {clicked_behavior} behavior for {len(selected_pieces)} {self.ui.active_selection_color} pieces")
                self.ui.hide_behavior_icons()
                # Clear the selection after setting behavior
                self.ui.clear_selection(self.ui.active_selection_color)
            elif self.ui.selected_piece_for_behavior:
                # Single piece behavior setting
                self.ui.selected_piece_for_behavior.set_behavior(clicked_behavior)
                print(f"Set {self.ui.selected_piece_for_behavior.piece_type} behavior to {clicked_behavior}")
                self.ui.hide_behavior_icons()
            return
            
        # Check if click is on play turn button
        if self.ui.is_click_on_play_button(mouse_pos):
            # Clear all UI states when playing a turn
            self.ui.clear_all_active_states()
            # Clear error message when playing turn
            self.error_message = ""
            self.play_auto_turns()
            # Clear all force move targets after the turn is played
            self.clear_all_force_move_targets()
        # Check if click is on auto turns input field
        elif self.ui.is_click_on_auto_turns_field(mouse_pos):
            # Clear the text field when activating (start fresh)
            self.ui.auto_turns_text = ""
            self.ui.activate_auto_turns_input()
            # Clear any existing error message when activating input
            self.error_message = ""
        # Check if click is on piece selection area
        elif self.ui.is_click_on_piece_area(mouse_pos):
            self.handle_piece_selection_click(mouse_pos)
        # Check if click is on the board
        elif self.ui.is_click_on_board(mouse_pos):
            print(f"Board click detected at {mouse_pos}")
            self.handle_board_click(mouse_pos)
        else:
            # Click was somewhere else, clear only certain UI interaction states but keep piece placement and selection modes
            print(f"Click outside recognized areas at {mouse_pos}")
            self.ui.active_action_button = None
            self.ui.auto_turns_input_active = False
            self.ui.hide_behavior_icons()
    
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion for drag selection"""
        # Update drag selection if active
        if self.ui.dragging_selection:
            self.ui.update_drag_selection(mouse_pos)
    
    def handle_mouse_up(self, mouse_pos: Tuple[int, int]):
        """Handle mouse button release"""
        # Finish drag selection if active
        if self.ui.dragging_selection:
            self.ui.finish_drag_selection(self.board)
            
            # Show behavior icons for selected pieces if any were selected
            if self.ui.active_selection_color and self.ui.selected_pieces_group[self.ui.active_selection_color]:
                print(f"Selected {len(self.ui.selected_pieces_group[self.ui.active_selection_color])} {self.ui.active_selection_color} pieces")
                # Show behavior selection for the group
                self.ui.show_group_behavior_selection(self.ui.active_selection_color)
    
    async def run_async(self):
        """Async main game loop for pybag compatibility."""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                    elif event.button == 3:  # Right click - deselect piece
                        self.deselect_piece()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        self.handle_mouse_up(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    # Handle drag selection
                    self.handle_mouse_motion(event.pos)
                    # Handle hover for action buttons
                    self.ui.handle_action_button_hover(event.pos)
                    # Handle hover for debug dropdown
                    self.ui.handle_debug_dropdown_hover(event.pos)
                elif event.type == pygame.KEYDOWN:
                    # Handle keyboard input for auto turns field
                    if self.ui.auto_turns_input_active:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            # Enter pressed - finalize input and exit
                            try:
                                if self.ui.auto_turns_text:
                                    new_value = max(1, int(self.ui.auto_turns_text))
                                    self.auto_turns = new_value
                                    print(f"AutoTurns set to: {self.auto_turns}")
                                else:
                                    # Empty field, keep current value
                                    print(f"AutoTurns remains: {self.auto_turns}")
                            except ValueError:
                                print("Invalid AutoTurns value, keeping current setting")
                            self.ui.deactivate_auto_turns_input()
                        elif event.key == pygame.K_ESCAPE:
                            # Escape pressed - cancel input
                            self.ui.deactivate_auto_turns_input()
                        elif event.key == pygame.K_BACKSPACE:
                            # Backspace - remove last character
                            self.ui.auto_turns_text = self.ui.auto_turns_text[:-1]
                            # Auto-apply if field becomes empty (revert to previous value)
                            if not self.ui.auto_turns_text:
                                print(f"Field cleared, AutoTurns remains: {self.auto_turns}")
                        else:
                            # Add character if it's a digit
                            if event.unicode.isdigit() and len(self.ui.auto_turns_text) < 3:  # Limit to 3 digits
                                self.ui.auto_turns_text += event.unicode
                                # Auto-apply the new value immediately
                                try:
                                    new_value = max(1, int(self.ui.auto_turns_text))
                                    self.auto_turns = new_value
                                    print(f"AutoTurns updated to: {self.auto_turns}")
                                except ValueError:
                                    # This shouldn't happen since we only allow digits
                                    pass
            
            # Update UI
            # Ensure AutoTurns display is synced when not in input mode
            if not self.ui.auto_turns_input_active:
                self.ui.set_auto_turns_display_value(self.auto_turns)
            
            self.render_game()
            
            clock.tick(60)  # 60 FPS
            
            # Allow async cooperation for pybag
            await asyncio.sleep(0)
        
        pygame.quit()
        if not DEBUG_PYBAG:
            sys.exit()

    def run(self):
        """Main game loop."""
        if DEBUG_PYBAG:
            # Use async loop for pybag compatibility
            asyncio.run(self.run_async())
        else:
            # Use synchronous loop for normal execution
            clock = pygame.time.Clock()
            
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            self.handle_click(event.pos)
                        elif event.button == 3:  # Right click - deselect piece
                            self.deselect_piece()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # Left click release
                            self.handle_mouse_up(event.pos)
                    elif event.type == pygame.MOUSEMOTION:
                        # Handle drag selection
                        self.handle_mouse_motion(event.pos)
                        # Handle hover for action buttons
                        self.ui.handle_action_button_hover(event.pos)
                    elif event.type == pygame.KEYDOWN:
                        # Handle keyboard input for auto turns field
                        if self.ui.auto_turns_input_active:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                # Enter pressed - finalize input and exit
                                try:
                                    if self.ui.auto_turns_text:
                                        new_value = max(1, int(self.ui.auto_turns_text))
                                        self.auto_turns = new_value
                                        print(f"AutoTurns set to: {self.auto_turns}")
                                    else:
                                        # Empty field, keep current value
                                        print(f"AutoTurns remains: {self.auto_turns}")
                                except ValueError:
                                    print("Invalid AutoTurns value, keeping current setting")
                                self.ui.deactivate_auto_turns_input()
                            elif event.key == pygame.K_ESCAPE:
                                # Escape pressed - cancel input
                                self.ui.deactivate_auto_turns_input()
                            elif event.key == pygame.K_BACKSPACE:
                                # Backspace - remove last character
                                self.ui.auto_turns_text = self.ui.auto_turns_text[:-1]
                                # Auto-apply if field becomes empty (revert to previous value)
                                if not self.ui.auto_turns_text:
                                    print(f"Field cleared, AutoTurns remains: {self.auto_turns}")
                            else:
                                # Add character if it's a digit
                                if event.unicode.isdigit() and len(self.ui.auto_turns_text) < 3:  # Limit to 3 digits
                                    self.ui.auto_turns_text += event.unicode
                                    # Auto-apply the new value immediately
                                    try:
                                        new_value = max(1, int(self.ui.auto_turns_text))
                                        self.auto_turns = new_value
                                        print(f"AutoTurns updated to: {self.auto_turns}")
                                    except ValueError:
                                        # This shouldn't happen since we only allow digits
                                        pass
                
                # Update UI
                # Ensure AutoTurns display is synced when not in input mode
                if not self.ui.auto_turns_input_active:
                    self.ui.set_auto_turns_display_value(self.auto_turns)
                
                # Display winner message if game is over
                display_message = self.winner if self.game_over else self.error_message
                
                # Show AutoTurns input instruction when the field is active
                if self.ui.auto_turns_input_active and not display_message:
                    display_message = "Type a number (auto-applies) or press Enter to finish."
                
                # Store the display message for rendering
                self.error_message = display_message
                
                # Use render_game instead of direct UI render to support debug modes
                self.render_game()
                
                clock.tick(60)  # 60 FPS
            
            pygame.quit()
            sys.exit()

    def update_display_during_moves(self):
        """Update the display immediately to show moves as they happen."""
        # Display winner message if game is over
        display_message = self.winner if self.game_over else self.error_message
        
        # Show AutoTurns input instruction when the field is active
        if self.ui.auto_turns_input_active and not display_message:
            display_message = "Type a number (auto-applies) or press Enter to finish."
        
        self.render_game()
        # Process events to keep the window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if DEBUG_PYBAG:
                    self.running = False
                else:
                    pygame.quit()
                    exit()


def main():
    """Entry point for the game."""
    # Parse command line arguments for board size and frontline
    board_size = 24  # Default size
    frontline = 2    # Default frontline distance
    traditional = False  # Default to AutoChess mode
    medium = False  # Default to standard mode
    turn_time = 0.5  # Default turn time
    points_rate = 5  # Default points rate
    start_points = 30  # Default start points
    
    # First, check for flag arguments
    args = sys.argv[1:]  # Remove script name
    
    # Look for --traditional flag and remove it from args if present
    if '--traditional' in args:
        traditional = True
        args.remove('--traditional')
        print("Traditional chess starting layout enabled.")
        # Set traditional chess defaults
        board_size = 8
        frontline = 1
        turn_time = 0.05
        points_rate = 5
        start_points = 5
        print("Traditional defaults: 8x8 board, 1-row frontline, 0.2s delay, 5 points/turn, 5 starting points")
    
    # Look for --medium flag and remove it from args if present
    if '--medium' in args:
        medium = True
        args.remove('--medium')
        print("Medium game mode enabled.")
        # Set medium game defaults
        board_size = 16
        frontline = 3
        turn_time = 0.1
        points_rate = 10
        start_points = 15
        print("Medium defaults: 16x16 board, 2-row frontline, 0.3s delay, 7 points/turn, 15 starting points")
    
    # Handle help
    if len(args) > 0 and args[0] in ['-h', '--help', 'help']:
        print("AutoChess Game")
        print("Usage: python main.py [--traditional|--medium] [board_size] [frontline] [turn_time] [points_rate] [start_points]")
        print("")
        print("Flags:")
        print("  --traditional     Use traditional chess starting layout with optimized settings")
        print("                    (8x8 board, 1-row frontline, 0.2s delay, 5 points/turn, 5 start points)")
        print("  --medium          Medium game mode with random piece placement")
        print("                    (16x16 board, 2-row frontline, 0.3s delay, 7 points/turn, 15 start points)")
        print("                    Each player gets 5-12 pawns (same random amount), 3 rooks, 3 bishops, 4 knights")
        print("")
        print("Arguments:")
        print("  board_size    Size of the n x n board (default: 24, traditional: 8, medium: 16, min: 8, max: 50)")
        print("  frontline     Rows from king where pieces can be placed (default: 2, traditional: 1, min: 1, max: 10)")
        print("  turn_time     Delay between moves in seconds (default: 0.5, traditional: 0.2, min: 0, max: 5.0)")
        print("  points_rate   Points awarded per turn to each player (default: 5, traditional: 5, min: 1, max: 50)")
        print("  start_points  Starting points for each player (default: 10, traditional: 5, min: 1, max: 100)")
        print("")
        print("Examples:")
        print("  python main.py                      # 24x24 board, 2-row frontline, 0.5s delay, 5 points/turn, 30 start points")
        print("  python main.py --traditional        # Traditional chess layout with default settings")
        print("  python main.py --medium             # Medium game mode with random piece placement")
        print("  python main.py --traditional 8      # Traditional chess layout on 8x8 board")
        print("  python main.py --medium 20          # Medium mode on 20x20 board")
        print("  python main.py 16                   # 16x16 board, 2-row frontline, 0.5s delay, 5 points/turn, 30 start points")
        print("  python main.py 16 3                 # 16x16 board, 3-row frontline, 0.5s delay, 5 points/turn, 30 start points")
        print("  python main.py 16 3 1.0             # 16x16 board, 3-row frontline, 1.0s delay, 5 points/turn, 30 start points")
        print("  python main.py 16 3 1.0 10          # 16x16 board, 3-row frontline, 1.0s delay, 10 points/turn, 30 start points")
        print("  python main.py 16 3 1.0 10 20       # 16x16 board, 3-row frontline, 1.0s delay, 10 points/turn, 20 start points")
        print("  python main.py 32 1 0 3 5           # 32x32 board, 1-row frontline, no delay, 3 points/turn, 5 start points")
        print("  python main.py --traditional 8 1 0  # Traditional 8x8, 1-row frontline, no delay (overrides defaults)")
        print("")
        print("Traditional Layout:")
        print("  Sets up pieces in standard chess positions: Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook")
        print("  Pawns on second rank for each side. Requires at least 8x8 board.")
        print("  On larger boards, the 8x8 layout is centered.")
        print("  When --traditional is used, all other arguments can still override the traditional defaults.")
        print("")
        print("Medium Layout:")
        print("  Places kings randomly, then adds random pieces to each player's territory:")
        print("  - 5-12 pawns (same random amount for both players)")
        print("  - 3 rooks, 3 bishops, 4 knights per player")
        print("  - All pieces randomly placed within frontline zones")
        print("  When --medium is used, all other arguments can still override the medium defaults.")
        print("")
        print("Frontline Rules:")
        print("  White pieces can be placed from frontline distance above their kings to the bottom of the board")
        print("  Black pieces can be placed from the top of the board to frontline distance below their kings")
        print("  Multiple kings create multiple frontline zones")
        return
    
    # Parse remaining positional arguments
    if len(args) > 0:
        # Parse board size
        try:
            board_size = int(args[0])
            if board_size < 8:
                print(f"Warning: Board size {board_size} is too small. Minimum size is 8x8. Using 8x8.")
                board_size = 8
            elif board_size > 50:
                print(f"Warning: Board size {board_size} is very large. Using 50x50 for performance.")
                board_size = 50
        except ValueError:
            print(f"Invalid board size '{args[0]}'. Using default size 24x24.")
            print("Use 'python main.py --help' for usage information.")
            board_size = 24
    
    # Parse frontline distance if provided
    if len(args) > 1:
        try:
            frontline = int(args[1])
            if frontline < 1:
                print(f"Warning: Frontline {frontline} is too small. Minimum is 1. Using 1.")
                frontline = 1
            elif frontline > 10:
                print(f"Warning: Frontline {frontline} is very large. Using 10 for balance.")
                frontline = 10
        except ValueError:
            print(f"Invalid frontline '{args[1]}'. Using default frontline 2.")
            print("Use 'python main.py --help' for usage information.")
            frontline = 2
    
    # Parse turn time if provided
    if len(args) > 2:
        try:
            turn_time = float(args[2])
            if turn_time < 0:
                print(f"Warning: Turn time {turn_time} is negative. Using 0 (no delay).")
                turn_time = 0
            elif turn_time > 5.0:
                print(f"Warning: Turn time {turn_time} is very long. Using 5.0 seconds.")
                turn_time = 5.0
        except ValueError:
            print(f"Invalid turn time '{args[2]}'. Using default turn time 0.5.")
            print("Use 'python main.py --help' for usage information.")
            turn_time = 0.5

    # Parse points rate if provided
    if len(args) > 3:
        try:
            points_rate = int(args[3])
            if points_rate < 1:
                print(f"Warning: Points rate {points_rate} is too low. Minimum is 1. Using 1.")
                points_rate = 1
            elif points_rate > 50:
                print(f"Warning: Points rate {points_rate} is very high. Using 50 for balance.")
                points_rate = 50
        except ValueError:
            print(f"Invalid points rate '{args[3]}'. Using default points rate 5.")
            print("Use 'python main.py --help' for usage information.")
            points_rate = 5

    # Parse start points if provided
    if len(args) > 4:
        try:
            start_points = int(args[4])
            if start_points < 1:
                print(f"Warning: Start points {start_points} is too low. Minimum is 1. Using 1.")
                start_points = 1
            elif start_points > 100:
                print(f"Warning: Start points {start_points} is very high. Using 100 for balance.")
                start_points = 100
        except ValueError:
            print(f"Invalid start points '{args[4]}'. Using default start points 10.")
            print("Use 'python main.py --help' for usage information.")
            start_points = 10

    layout_mode = "traditional" if traditional else ("medium" if medium else "AutoChess")
    print(f"Starting {layout_mode} with {board_size}x{board_size} board, {frontline}-row frontline, {turn_time}s move delay, {points_rate} points/turn, and {start_points} starting points")
    game = AutoChessGame(board_size=board_size, frontline=frontline, turn_time=turn_time, points_rate=points_rate, start_points=start_points, traditional=traditional, medium=medium)
    game.run()


if __name__ == "__main__":
    main()
