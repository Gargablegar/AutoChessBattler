"""
Debug functionality for AutoChess Game
Handles all debug mode implementations including fog of war, heat maps, etc.
"""

import pygame
from typing import List, Tuple, Set, Dict, Optional
from autochess_pieces import AutoChessPiece
from board import ChessBoard


class DebugManager:
    """Manages all debug functionality for the AutoChess game"""
    
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.fog_colors = {
            'light_fog': (200, 200, 200),  # Light grey for fog squares
            'dark_fog': (150, 150, 150),   # Dark grey for fog squares
        }
    
    def calculate_white_fog_of_war(self, board: ChessBoard) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Calculate what white pieces can see (territory + enemy pieces)
        
        Returns:
            Tuple of (white_territory, enemy_pieces_visible)
        """
        white_territory = set()
        enemy_pieces_visible = set()
        
        # Get all white pieces
        white_pieces = []
        for piece, pos in board.get_all_pieces():
            if piece.color == "white":
                white_pieces.append((piece, pos))
        
        # Calculate territory around white pieces (within 2 squares)
        for piece, pos in white_pieces:
            row, col = pos
            
            # Territory extends 2 squares in all directions from each white piece
            for d_row in range(-2, 3):
                for d_col in range(-2, 3):
                    territory_row, territory_col = row + d_row, col + d_col
                    if self._is_valid_position(territory_row, territory_col):
                        white_territory.add((territory_row, territory_col))
        
        # Calculate piece vision (what enemy pieces white can see)
        for piece, pos in white_pieces:
            visible_squares, enemy_pieces = self._calculate_piece_vision(piece, pos, board)
            
            # Add enemy pieces to the visible set
            for enemy_pos in enemy_pieces:
                enemy_pieces_visible.add(enemy_pos)
        
        return white_territory, enemy_pieces_visible
    
    def _get_white_territory_squares(self, frontline_zones: List[Tuple[int, int, int, int]] = None) -> Set[Tuple[int, int]]:
        """Get all squares in white's territory (below frontline)"""
        territory_squares = set()
        
        if frontline_zones:
            # Find white's frontline zone (assuming it's in the lower half of the board)
            white_frontline = None
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # White frontline is typically in the lower part of the board
                if min_row > self.board_size // 2:
                    white_frontline = (min_row, max_row, min_col, max_col)
                    break
            
            if white_frontline:
                min_row, max_row, min_col, max_col = white_frontline
                # Add all squares from the frontline to the bottom of the board
                for row in range(min_row, self.board_size):
                    for col in range(self.board_size):
                        territory_squares.add((row, col))
            else:
                # Fallback: assume bottom quarter of board is white territory
                start_row = (3 * self.board_size) // 4
                for row in range(start_row, self.board_size):
                    for col in range(self.board_size):
                        territory_squares.add((row, col))
        else:
            # Fallback: assume bottom quarter of board is white territory
            start_row = (3 * self.board_size) // 4
            for row in range(start_row, self.board_size):
                for col in range(self.board_size):
                    territory_squares.add((row, col))
        
        return territory_squares
    
    def _calculate_piece_vision(self, piece: AutoChessPiece, position: Tuple[int, int], board: ChessBoard) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Calculate what squares a piece can see and enemy pieces it can spot.
        
        Returns:
            Tuple of (visible_squares, enemy_pieces_spotted)
        """
        visible_squares = set()
        enemy_pieces_spotted = set()
        
        # Use directional vision for all pieces
        vision_lines = self._get_piece_vision_lines(piece, position)
        for direction in vision_lines:
            vision_path, enemy_piece = self._trace_directional_vision(
                position, direction, board, piece.color
            )
            visible_squares.update(vision_path)
            if enemy_piece:
                enemy_pieces_spotted.add(enemy_piece)
        
        return visible_squares, enemy_pieces_spotted
    
    def _get_piece_vision_lines(self, piece: AutoChessPiece, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get the directional vision lines for a piece"""
        directions = []
        
        if piece.piece_type == "Rook":
            # Straight lines: up, down, left, right
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        elif piece.piece_type == "Bishop":
            # Diagonal lines
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.piece_type == "Queen":
            # All 8 directions
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.piece_type == "King":
            # One square in all 8 directions
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.piece_type == "Knight":
            # Knight moves (L-shaped)
            directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        elif piece.piece_type == "Pawn":
            # Pawn vision (forward and diagonal attacks)
            if piece.color == "white":
                directions = [(-1, 0), (-1, -1), (-1, 1)]  # Forward and diagonal
            else:
                directions = [(1, 0), (1, -1), (1, 1)]
        
        return directions
    
    def _trace_directional_vision(self, start_pos: Tuple[int, int], direction: Tuple[int, int], board: ChessBoard, piece_color: str) -> Tuple[Set[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """
        Trace vision in a specific direction until hitting an obstacle or board edge.
        
        Returns:
            Tuple of (visible_squares, enemy_piece_position)
        """
        visible_squares = set()
        enemy_piece = None
        
        row, col = start_pos
        d_row, d_col = direction
        
        # For knight moves, only check the target square
        if abs(d_row) == 2 or abs(d_col) == 2:
            target_row, target_col = row + d_row, col + d_col
            if self._is_valid_position(target_row, target_col):
                visible_squares.add((target_row, target_col))
                piece_at_target = board.get_piece((target_row, target_col))
                if piece_at_target and piece_at_target.color != piece_color:
                    enemy_piece = (target_row, target_col)
            return visible_squares, enemy_piece
        
        # For other pieces, trace along the direction
        current_row, current_col = row + d_row, col + d_col
        max_range = 1  # Default for King and Pawn
        
        # Determine the piece type at start position to set range
        piece_at_start = board.get_piece(start_pos)
        if piece_at_start and piece_at_start.piece_type in ["Queen", "Rook", "Bishop"]:
            max_range = board.size  # Long range pieces
        
        squares_traced = 0
        while self._is_valid_position(current_row, current_col) and squares_traced < max_range:
            visible_squares.add((current_row, current_col))
            squares_traced += 1
            
            # Check if there's a piece at this position
            piece_at_position = board.get_piece((current_row, current_col))
            if piece_at_position:
                if piece_at_position.color != piece_color:
                    # Found enemy piece - this is visible and blocks further vision
                    enemy_piece = (current_row, current_col)
                # Stop tracing in this direction (piece blocks vision)
                break
            
            # Move to next square in direction
            current_row += d_row
            current_col += d_col
        
        return visible_squares, enemy_piece
    
    def _trace_line_of_sight(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], board: ChessBoard, piece_color: str) -> Tuple[Set[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """
        Trace line of sight from start to end position.
        
        Returns:
            Tuple of (visible_squares, enemy_piece_position)
        """
        visible_squares = set()
        enemy_piece = None
        
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Calculate direction
        d_row = 0 if end_row == start_row else (1 if end_row > start_row else -1)
        d_col = 0 if end_col == start_col else (1 if end_col > start_col else -1)
        
        current_row, current_col = start_row + d_row, start_col + d_col
        
        while (current_row, current_col) != (end_row, end_col) and self._is_valid_position(current_row, current_col):
            visible_squares.add((current_row, current_col))
            
            # Check if there's a piece blocking the path
            piece_at_position = board.get_piece((current_row, current_col))
            if piece_at_position:
                if piece_at_position.color != piece_color:
                    enemy_piece = (current_row, current_col)
                break
            
            current_row += d_row
            current_col += d_col
        
        # Add the end position if it's valid
        if self._is_valid_position(end_row, end_col):
            visible_squares.add((end_row, end_col))
            piece_at_end = board.get_piece((end_row, end_col))
            if piece_at_end and piece_at_end.color != piece_color:
                enemy_piece = (end_row, end_col)
        
        return visible_squares, enemy_piece
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < self.board_size and 0 <= col < self.board_size
    
    def render_white_fog_of_war(self, screen: pygame.Surface, board: ChessBoard, ui, frontline_zones: List[Tuple[int, int, int, int]] = None):
        """
        Render the board with white fog of war applied.
        Only renders white pieces and visible enemy pieces.
        """
        
        # Calculate what's visible to white
        visible_squares, enemy_pieces_visible = self.calculate_white_fog_of_war(board)
        
        # Get white territory (areas that should never have fog)
        white_territory = self._get_white_territory_squares(frontline_zones)
        
        board_start_x = ui.side_panel_width
        board_start_y = ui.top_panel_height
        
        # Render board squares with fog
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = board_start_x + col * ui.square_size
                y = board_start_y + row * ui.square_size
                
                # Square is clear (no fog) if it's in white territory OR visible to white pieces
                is_clear = (row, col) in white_territory or (row, col) in visible_squares
                
                if is_clear:
                    # Clear square - use normal colors
                    color = ui.colors['light_square'] if (row + col) % 2 == 0 else ui.colors['dark_square']
                else:
                    # Fog of war square - use grey colors
                    color = self.fog_colors['light_fog'] if (row + col) % 2 == 0 else self.fog_colors['dark_fog']
                
                pygame.draw.rect(screen, color, (x, y, ui.square_size, ui.square_size))
        
        # Render frontline zones if provided and visible
        if frontline_zones:
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # Only render frontline zones that are at least partially clear
                zone_visible = False
                for row in range(min_row, max_row + 1):
                    for col in range(min_col, max_col + 1):
                        is_clear = (row, col) in white_territory or (row, col) in visible_squares
                        if is_clear:
                            zone_visible = True
                            break
                    if zone_visible:
                        break
                
                if zone_visible:
                    zone_x = board_start_x + min_col * ui.square_size
                    zone_y = board_start_y + min_row * ui.square_size
                    zone_width = (max_col - min_col + 1) * ui.square_size
                    zone_height = (max_row - min_row + 1) * ui.square_size
                    pygame.draw.rect(screen, zone_color, 
                                   (zone_x - 3, zone_y - 3, zone_width + 6, zone_height + 6), 3)
        
        # Render pieces based on visibility
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board.get_piece((row, col))
                if piece:
                    should_render = False
                    
                    if piece.color == "white":
                        # Always render white pieces
                        should_render = True
                    elif piece.color == "black":
                        # Render black pieces if they're in white territory OR visible to white pieces
                        if (row, col) in white_territory or (row, col) in enemy_pieces_visible:
                            should_render = True
                    
                    if should_render:
                        x = board_start_x + col * ui.square_size
                        y = board_start_y + row * ui.square_size
                        square_rect = pygame.Rect(x, y, ui.square_size, ui.square_size)
                        ui.render_piece(piece, square_rect)
                        
                        # Show behavior indicator if piece has non-default behavior
                        if piece.behavior != "default":
                            ui.render_behavior_indicator(piece, square_rect)
        
        # Add visual indicators for vision
        self._render_vision_indicators(screen, visible_squares, enemy_pieces_visible, white_territory, ui)
    
    def _render_vision_indicators(self, screen: pygame.Surface, visible_squares: Set[Tuple[int, int]], enemy_pieces_visible: Set[Tuple[int, int]], white_territory: Set[Tuple[int, int]], ui):
        """Render subtle visual indicators for vision areas"""
        board_start_x = ui.side_panel_width
        board_start_y = ui.top_panel_height
        
        # Create a semi-transparent surface for vision overlay
        vision_surface = pygame.Surface((ui.square_size, ui.square_size))
        vision_surface.set_alpha(30)
        
        # Highlight visible squares (outside territory) with a subtle blue tint
        vision_surface.fill((100, 150, 255))
        for row, col in visible_squares:
            # Only highlight squares that aren't already in white territory
            if (row, col) not in white_territory:
                x = board_start_x + col * ui.square_size
                y = board_start_y + row * ui.square_size
                screen.blit(vision_surface, (x, y))
        
        # Highlight spotted enemy pieces with a red border
        for row, col in enemy_pieces_visible:
            x = board_start_x + col * ui.square_size
            y = board_start_y + row * ui.square_size
            pygame.draw.rect(screen, (255, 100, 100), 
                           (x - 1, y - 1, ui.square_size + 2, ui.square_size + 2), 2)
    
    def calculate_black_fog_of_war(self, board: ChessBoard, frontline_zones: List[Tuple[int, int, int, int]] = None) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Calculate black fog of war visibility (similar to white but for black pieces).
        
        Returns:
            Tuple of (visible_squares, enemy_pieces_visible)
        """
        # TODO: Implement black fog of war (mirror of white fog logic)
        pass
    
    def render_heat_map(self, screen: pygame.Surface, board: ChessBoard, ui):
        """
        Render a heat map showing piece movement and attack patterns.
        """
        # TODO: Implement heat map visualization
        pass
    
    def enable_incremental_test_mode(self):
        """
        Enable incremental game mode testing features.
        """
        # TODO: Implement incremental testing features
        pass
