#!/usr/bin/env python3
"""
AutoChess Game
A chess variant where players use a point-based system to place pieces on an n x n board.
Each player gets pieces on the side and can place them multiple times as long as they have points.

Usage: python game.py [board_size] [frontline] [turn_time]
Example: python game.py 16 3 0.5  (creates a 16x16 board with 3-row frontline and 0.5s move delay)
Default: 24x24 board with 2-row frontline and 0.5s move delay if not specified
"""

import pygame
import sys
import random
from typing import Dict, List, Optional, Tuple, Any
from autochess_pieces import (
    AutoChessPiece, King, Queen, Rook, Bishop, Knight, Pawn
)
from board import ChessBoard
from game_ui import GameUI


class AutoChessGame:
    """Main game controller for AutoChess."""
    
    def __init__(self, board_size: int = 24, frontline: int = 2, turn_time: float = 0.5):
        # Initialize pygame
        pygame.init()
        
        # Game state
        self.board = ChessBoard(size=board_size)  # Board size from parameter
        self.ui = GameUI(board_size=board_size)  # Pass the board size
        self.running = True
        self.current_player = "white"  # For UI display purposes, but both can place pieces
        self.turn_counter = 1
        self.frontline = frontline  # How many rows from king pieces can be placed
        self.error_message = ""  # Error message to display
        self.auto_turns = 1  # Number of turns to play automatically
        self.game_over = False  # Flag to track if game is over
        self.winner = ""  # Winner of the game
        self.turn_time = turn_time  # Delay between moves in seconds
        
        # Points system
        self.points = {"white": 10, "black": 10}
        # Configuration: Points awarded to each player per turn (change this value to adjust economy)
        self.pointsRate = 5  # Points added per turn for each player
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
        print("Both players can place pieces simultaneously! Click 'Play Turn' to make all pieces move.")
        print("Selected pieces stay selected for multiple placements. Right-click to deselect.")
        print("White pieces can be placed from frontline distance above their kings to the bottom of the board.")
        print("Black pieces can be placed from the top of the board to frontline distance below their kings.")
        
        # Place starting kings
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
    
    def get_frontline_zones(self, color: str) -> List[Tuple[int, int, int, int]]:
        """Get all frontline zones for a color as list of (min_row, max_row, min_col, max_col)."""
        king_positions = self.get_king_positions(color)
        zones = []
        
        for king_row, king_col in king_positions:
            if color == "white":
                # White zone extends from frontline distance above the king to the bottom of the board
                min_row = max(0, king_row - self.frontline)
                max_row = self.board.size - 1
            else:  # black
                # Black zone extends from the top of the board to frontline distance below the king
                min_row = 0
                max_row = min(self.board.size - 1, king_row + self.frontline)
            
            zones.append((min_row, max_row, 0, self.board.size - 1))
        
        return zones
    
    def check_win_condition(self) -> bool:
        """Check if the game has ended due to one player having no kings"""
        white_kings = self.get_king_positions("white")
        black_kings = self.get_king_positions("black")
        
        if not white_kings and not black_kings:
            # Both players have no kings - this shouldn't happen normally
            self.game_over = True
            self.winner = "Draw - No kings remaining"
            return True
        elif not white_kings:
            # White has no kings - Black wins
            self.game_over = True
            self.winner = "Black wins!"
            print(f"\n🏆 GAME OVER: {self.winner}")
            return True
        elif not black_kings:
            # Black has no kings - White wins
            self.game_over = True
            self.winner = "White wins!"
            print(f"\n🏆 GAME OVER: {self.winner}")
            return True
        
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
    
    def play_turn(self):
        """Execute a turn - make all pieces move randomly and give both players points"""
        print(f"\n🎮 PLAYING TURN {self.turn_counter} with {self.auto_turns} move rounds...")
        
        if not self.board.get_all_pieces():
            print("No pieces on board to move!")
        else:
            total_moves_made = 0
            
            # Execute multiple move rounds based on auto_turns setting
            for move_round in range(self.auto_turns):
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
                            # Pick a random valid move
                            target_row, target_col = random.choice(available_moves)
                            target_piece = self.board.get_piece((target_row, target_col))
                            
                            # Make the move
                            success = self.board.move_piece((row, col), (target_row, target_col))
                            if success:
                                moves_this_round += 1
                                total_moves_made += 1
                                if target_piece:
                                    print(f"    {piece.color.capitalize()} {piece.__class__.__name__} captured {target_piece.color} {target_piece.__class__.__name__} ({row},{col}) → ({target_row},{target_col})")
                                else:
                                    print(f"    {piece.color.capitalize()} {piece.__class__.__name__} moved ({row},{col}) → ({target_row},{target_col})")
                                
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
            
            print(f"Turn complete! {total_moves_made} total moves made across {self.auto_turns} move rounds.")
        
        # Both players gain points at the end of each turn
        self.points["white"] += self.pointsRate
        self.points["black"] += self.pointsRate
        print(f"Both players gained {self.pointsRate} points. White: {self.points['white']}, Black: {self.points['black']}")
        
        # Reset all piece behaviors after the turn
        self.reset_all_piece_behaviors()
        
        # Increment turn counter but don't switch players - both can continue placing pieces
        self.turn_counter += 1
        print("Both players can continue placing pieces for the next turn!")
        
        # Check for win condition after the turn
        self.check_win_condition()
    
    def reset_all_piece_behaviors(self):
        """Reset all piece behaviors to default after a turn"""
        pieces_with_behavior = []
        passive_pieces_count = 0
        
        for piece, pos in self.board.get_all_pieces():
            if piece.behavior != "default":
                pieces_with_behavior.append(f"{piece.color} {piece.piece_type}")
                if piece.behavior == "passive":
                    passive_pieces_count += 1
                piece.reset_behavior()
        
        if pieces_with_behavior:
            print(f"Reset behaviors for: {', '.join(pieces_with_behavior)}")
            if passive_pieces_count > 0:
                print(f"  → {passive_pieces_count} passive pieces returned to normal movement")
    
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
        
        # Also hide behavior icons
        self.ui.hide_behavior_icons()
    
    def handle_piece_selection_click(self, mouse_pos: Tuple[int, int]):
        """Handle clicks on the piece selection area."""
        # Check both white and black piece areas, regardless of current_player
        white_piece_index = self.ui.get_clicked_piece(mouse_pos, "white")
        black_piece_index = self.ui.get_clicked_piece(mouse_pos, "black")
        
        if white_piece_index is not None and 0 <= white_piece_index < len(self.available_pieces["white"]):
            piece = self.available_pieces["white"][white_piece_index]
            self.select_piece_for_placement(piece)
        elif black_piece_index is not None and 0 <= black_piece_index < len(self.available_pieces["black"]):
            piece = self.available_pieces["black"][black_piece_index]
            self.select_piece_for_placement(piece)
    
    def handle_board_click(self, mouse_pos: Tuple[int, int]):
        """Handle clicks on the game board."""
        board_pos = self.ui.get_board_position(mouse_pos)
        if not board_pos:
            return
        
        row, col = board_pos
        
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
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle all mouse clicks."""
        # Don't allow interactions if game is over
        if self.game_over:
            return
        
        # Check if a behavior icon was clicked first (before any other checks)
        clicked_behavior = self.ui.get_clicked_behavior_icon(mouse_pos)
        if clicked_behavior:
            if self.ui.selected_piece_for_behavior:
                self.ui.selected_piece_for_behavior.set_behavior(clicked_behavior)
                print(f"Set {self.ui.selected_piece_for_behavior.piece_type} behavior to {clicked_behavior}")
                self.ui.hide_behavior_icons()
            return
            
        # Check if click is on play turn button
        if self.ui.is_click_on_play_button(mouse_pos):
            self.play_auto_turns()
        # Check if click is on auto turns input field
        elif self.ui.is_click_on_auto_turns_field(mouse_pos):
            # Set the text field to current auto_turns value before activating
            self.ui.auto_turns_text = str(self.auto_turns)
            self.ui.activate_auto_turns_input()
        # Check if click is on piece selection area
        elif self.ui.is_click_on_piece_area(mouse_pos):
            self.handle_piece_selection_click(mouse_pos)
        # Check if click is on the board
        elif self.ui.is_click_on_board(mouse_pos):
            self.handle_board_click(mouse_pos)
        else:
            # Click was somewhere else, hide behavior icons
            self.ui.hide_behavior_icons()
    
    def run(self):
        """Main game loop."""
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
                elif event.type == pygame.KEYDOWN:
                    # Handle keyboard input for auto turns field
                    if self.ui.auto_turns_input_active:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            # Enter pressed - finalize input
                            try:
                                new_value = max(1, int(self.ui.auto_turns_text))
                                self.auto_turns = new_value
                                print(f"AutoTurns set to: {self.auto_turns}")
                            except ValueError:
                                print("Invalid AutoTurns value, keeping current setting")
                                # Reset text field to current valid value
                                self.ui.auto_turns_text = str(self.auto_turns)
                            self.ui.deactivate_auto_turns_input()
                        elif event.key == pygame.K_ESCAPE:
                            # Escape pressed - cancel input
                            self.ui.deactivate_auto_turns_input()
                        elif event.key == pygame.K_BACKSPACE:
                            # Backspace - remove last character
                            self.ui.auto_turns_text = self.ui.auto_turns_text[:-1]
                        else:
                            # Add character if it's a digit
                            if event.unicode.isdigit() and len(self.ui.auto_turns_text) < 3:  # Limit to 3 digits
                                self.ui.auto_turns_text += event.unicode
            
            # Update UI
            # Ensure AutoTurns display is synced when not in input mode
            if not self.ui.auto_turns_input_active:
                self.ui.set_auto_turns_display_value(self.auto_turns)
            
            # Display winner message if game is over
            display_message = self.winner if self.game_over else self.error_message
            
            self.ui.render(
                board=self.board,
                white_pieces=self.available_pieces["white"],
                black_pieces=self.available_pieces["black"],
                turn_counter=self.turn_counter,
                player_points=self.points,
                selected_piece=self.selected_piece_for_placement,
                piece_costs=self.piece_costs,
                error_message=display_message,
                frontline_zones=self.get_frontline_zones("white") + self.get_frontline_zones("black") if self.selected_piece_for_placement else [],
                auto_turns=self.auto_turns
            )
            
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

    def update_display_during_moves(self):
        """Update the display immediately to show moves as they happen."""
        # Display winner message if game is over
        display_message = self.winner if self.game_over else self.error_message
        
        self.ui.render(
            board=self.board,
            white_pieces=self.available_pieces["white"],
            black_pieces=self.available_pieces["black"],
            turn_counter=self.turn_counter,
            player_points=self.points,
            selected_piece=self.selected_piece_for_placement,
            piece_costs=self.piece_costs,
            error_message=display_message,
            frontline_zones=self.get_frontline_zones("white") + self.get_frontline_zones("black") if self.selected_piece_for_placement else [],
            auto_turns=self.auto_turns
        )
        # Process events to keep the window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def main():
    """Entry point for the game."""
    # Parse command line arguments for board size and frontline
    board_size = 24  # Default size
    frontline = 2    # Default frontline distance
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Check for help
        if arg in ['-h', '--help', 'help']:
            print("AutoChess Game")
            print("Usage: python game.py [board_size] [frontline] [turn_time]")
            print("")
            print("Arguments:")
            print("  board_size    Size of the n x n board (default: 24, min: 8, max: 50)")
            print("  frontline     Rows from king where pieces can be placed (default: 2, min: 1, max: 10)")
            print("  turn_time     Delay between moves in seconds (default: 0.5, min: 0, max: 5.0)")
            print("")
            print("Examples:")
            print("  python game.py               # 24x24 board, 2-row frontline, 0.5s delay")
            print("  python game.py 16            # 16x16 board, 2-row frontline, 0.5s delay")
            print("  python game.py 16 3          # 16x16 board, 3-row frontline, 0.5s delay")
            print("  python game.py 16 3 1.0      # 16x16 board, 3-row frontline, 1.0s delay")
            print("  python game.py 32 1 0        # 32x32 board, 1-row frontline, no delay")
            print("")
            print("Frontline Rules:")
            print("  White pieces can be placed from frontline distance above their kings to the bottom of the board")
            print("  Black pieces can be placed from the top of the board to frontline distance below their kings")
            print("  Multiple kings create multiple frontline zones")
            return
        
        # Parse board size
        try:
            board_size = int(arg)
            if board_size < 8:
                print(f"Warning: Board size {board_size} is too small. Minimum size is 8x8. Using 8x8.")
                board_size = 8
            elif board_size > 50:
                print(f"Warning: Board size {board_size} is very large. Using 50x50 for performance.")
                board_size = 50
        except ValueError:
            print(f"Invalid board size '{arg}'. Using default size 24x24.")
            print("Use 'python game.py --help' for usage information.")
            board_size = 24
    
    # Parse frontline distance if provided
    if len(sys.argv) > 2:
        try:
            frontline = int(sys.argv[2])
            if frontline < 1:
                print(f"Warning: Frontline {frontline} is too small. Minimum is 1. Using 1.")
                frontline = 1
            elif frontline > 10:
                print(f"Warning: Frontline {frontline} is very large. Using 10 for balance.")
                frontline = 10
        except ValueError:
            print(f"Invalid frontline '{sys.argv[2]}'. Using default frontline 2.")
            print("Use 'python game.py --help' for usage information.")
            frontline = 2
    
    # Parse turn time if provided
    turn_time = 0.5  # Default turn time
    if len(sys.argv) > 3:
        try:
            turn_time = float(sys.argv[3])
            if turn_time < 0:
                print(f"Warning: Turn time {turn_time} is negative. Using 0 (no delay).")
                turn_time = 0
            elif turn_time > 5.0:
                print(f"Warning: Turn time {turn_time} is very long. Using 5.0 seconds.")
                turn_time = 5.0
        except ValueError:
            print(f"Invalid turn time '{sys.argv[3]}'. Using default turn time 0.5.")
            print("Use 'python game.py --help' for usage information.")
            turn_time = 0.5

    print(f"Starting AutoChess with {board_size}x{board_size} board, {frontline}-row frontline, and {turn_time}s move delay")
    game = AutoChessGame(board_size=board_size, frontline=frontline, turn_time=turn_time)
    game.run()


if __name__ == "__main__":
    main()
