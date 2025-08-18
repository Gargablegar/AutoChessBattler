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
    
    def calculate_white_fog_of_war(self, board: ChessBoard, frontline_zones: List[Tuple[int, int, int, int]] = None) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Calculate what white pieces can see (frontline-based territory + piece vision)
        
        Returns:
            Tuple of (white_territory, enemy_pieces_visible)
        """
        enemy_pieces_visible = set()
        
        # Get white territory based on frontline zones (not piece proximity)
        white_territory = self._get_white_territory_squares(frontline_zones)
        
        # Get all white pieces
        white_pieces = []
        for piece, pos in board.get_all_pieces():
            if piece.color == "white":
                white_pieces.append((piece, pos))
        
        # Calculate piece vision (what enemy pieces white can see)
        for piece, pos in white_pieces:
            visible_squares, enemy_pieces = self._calculate_piece_vision(piece, pos, board)
            
            # Add enemy pieces to the visible set
            for enemy_pos in enemy_pieces:
                enemy_pieces_visible.add(enemy_pos)
        
        return white_territory, enemy_pieces_visible
    
    def _get_white_territory_squares(self, frontline_zones: List[Tuple[int, int, int, int]] = None) -> Set[Tuple[int, int]]:
        """Get all squares in white's territory (includes frontline zones and below)"""
        territory_squares = set()
        
        if frontline_zones:
            # Add all white frontline zones to territory
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # White frontline zones are typically in the lower part of the board
                if min_row > self.board_size // 2:
                    # Add the entire frontline zone to white territory
                    for row in range(min_row, max_row + 1):
                        for col in range(min_col, max_col + 1):
                            territory_squares.add((row, col))
                    
                    # Also add all squares below the frontline zone
                    for row in range(max_row + 1, self.board_size):
                        for col in range(self.board_size):
                            territory_squares.add((row, col))
            
            # If no white frontline zones found, use fallback
            if not territory_squares:
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
        visible_squares, enemy_pieces_visible = self.calculate_white_fog_of_war(board, frontline_zones)
        
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
        Calculate black fog of war visibility (uses frontline-based territory + piece vision).
        
        Returns:
            Tuple of (black_territory, enemy_pieces_visible)
        """
        enemy_pieces_visible = set()
        
        # Get black territory based on frontline zones (not piece proximity)
        black_territory = self._get_black_territory_squares(frontline_zones)
        
        # Get all black pieces
        black_pieces = []
        for piece, pos in board.get_all_pieces():
            if piece.color == "black":
                black_pieces.append((piece, pos))
        
        # Calculate piece vision (what enemy pieces black can see)
        for piece, pos in black_pieces:
            visible_squares, enemy_pieces = self._calculate_piece_vision(piece, pos, board)
            
            # Add enemy pieces to the visible set
            for enemy_pos in enemy_pieces:
                enemy_pieces_visible.add(enemy_pos)
        
        return black_territory, enemy_pieces_visible
    
    def _get_black_territory_squares(self, frontline_zones: List[Tuple[int, int, int, int]] = None) -> Set[Tuple[int, int]]:
        """Get all squares in black's territory (includes frontline zones and above)"""
        territory_squares = set()
        
        if frontline_zones:
            # Add all black frontline zones to territory
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # Black frontline zones are typically in the upper part of the board
                if min_row < self.board_size // 2:
                    # Add the entire frontline zone to black territory
                    for row in range(min_row, max_row + 1):
                        for col in range(min_col, max_col + 1):
                            territory_squares.add((row, col))
                    
                    # Also add all squares above the frontline zone
                    for row in range(0, min_row):
                        for col in range(self.board_size):
                            territory_squares.add((row, col))
            
            # If no black frontline zones found, use fallback
            if not territory_squares:
                end_row = self.board_size // 2
                for row in range(0, end_row):
                    for col in range(self.board_size):
                        territory_squares.add((row, col))
        else:
            # Fallback: assume top half of board is black territory
            end_row = self.board_size // 2
            for row in range(0, end_row):
                for col in range(self.board_size):
                    territory_squares.add((row, col))
        
        return territory_squares
    
    def render_black_fog_of_war(self, screen: pygame.Surface, board: ChessBoard, ui, frontline_zones: List[Tuple[int, int, int, int]] = None):
        """
        Render the board with black fog of war applied.
        Only renders black pieces and visible enemy pieces.
        """
        
        # Calculate what's visible to black
        visible_squares, enemy_pieces_visible = self.calculate_black_fog_of_war(board, frontline_zones)
        
        # Get black territory (areas that should never have fog)
        black_territory = self._get_black_territory_squares(frontline_zones)
        
        board_start_x = ui.side_panel_width
        board_start_y = ui.top_panel_height
        
        # Render board squares with fog
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = board_start_x + col * ui.square_size
                y = board_start_y + row * ui.square_size
                square_rect = pygame.Rect(x, y, ui.square_size, ui.square_size)
                
                # Determine if this square should be clear or fogged
                is_clear = (row, col) in black_territory or (row, col) in visible_squares
                
                if is_clear:
                    # Render normal board square
                    color = ui.colors['light_square'] if (row + col) % 2 == 0 else ui.colors['dark_square']
                    pygame.draw.rect(screen, color, square_rect)
                else:
                    # Render fogged square
                    fog_color = self.fog_colors['light_fog'] if (row + col) % 2 == 0 else self.fog_colors['dark_fog']
                    pygame.draw.rect(screen, fog_color, square_rect)
        
        # Render frontline zones if provided and visible
        if frontline_zones:
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # Only render frontline if it's in visible area or black territory
                frontline_visible = False
                for f_row in range(min_row, max_row + 1):
                    for f_col in range(min_col, max_col + 1):
                        if (f_row, f_col) in black_territory or (f_row, f_col) in visible_squares:
                            frontline_visible = True
                            break
                    if frontline_visible:
                        break
                
                if frontline_visible:
                    x = board_start_x + min_col * ui.square_size
                    y = board_start_y + min_row * ui.square_size
                    width = (max_col - min_col + 1) * ui.square_size
                    height = (max_row - min_row + 1) * ui.square_size
                    pygame.draw.rect(screen, zone_color, (x - 3, y - 3, width + 6, height + 6), 3)
        
        # Render pieces based on visibility
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board.get_piece((row, col))
                if piece:
                    should_render = False
                    
                    if piece.color == "black":
                        # Always render black pieces
                        should_render = True
                    elif piece.color == "white":
                        # Render white pieces if they're in black territory OR visible to black pieces
                        if (row, col) in black_territory or (row, col) in enemy_pieces_visible:
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
        self._render_black_vision_indicators(screen, visible_squares, enemy_pieces_visible, black_territory, ui)
    
    def _render_black_vision_indicators(self, screen: pygame.Surface, visible_squares: Set[Tuple[int, int]], enemy_pieces_visible: Set[Tuple[int, int]], black_territory: Set[Tuple[int, int]], ui):
        """Render subtle visual indicators for black's vision areas"""
        board_start_x = ui.side_panel_width
        board_start_y = ui.top_panel_height
        
        # Create a semi-transparent surface for vision overlay
        vision_surface = pygame.Surface((ui.square_size, ui.square_size))
        vision_surface.set_alpha(30)
        
        # Highlight visible squares (outside territory) with a subtle orange tint
        vision_surface.fill((255, 150, 100))
        for row, col in visible_squares:
            # Only highlight squares that aren't already in black territory
            if (row, col) not in black_territory:
                x = board_start_x + col * ui.square_size
                y = board_start_y + row * ui.square_size
                screen.blit(vision_surface, (x, y))
        
        # Highlight spotted enemy pieces with a red border
        for row, col in enemy_pieces_visible:
            x = board_start_x + col * ui.square_size
            y = board_start_y + row * ui.square_size
            pygame.draw.rect(screen, (255, 100, 100), 
                           (x - 1, y - 1, ui.square_size + 2, ui.square_size + 2), 2)
    
    def render_heat_map(self, screen: pygame.Surface, board: ChessBoard, ui):
        """
        Render a heat map showing piece movement and attack patterns.
        Shows how many pieces can move to each square with color intensity and numbers.
        """
        # Calculate heat map data for both colors
        white_heat_map, black_heat_map = self._calculate_heat_map_data(board)
        
        board_start_x = ui.side_panel_width
        board_start_y = ui.top_panel_height
        
        # Render board squares with heat map overlay
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = board_start_x + col * ui.square_size
                y = board_start_y + row * ui.square_size
                square_rect = pygame.Rect(x, y, ui.square_size, ui.square_size)
                
                # Start with normal board colors
                base_color = ui.colors['light_square'] if (row + col) % 2 == 0 else ui.colors['dark_square']
                pygame.draw.rect(screen, base_color, square_rect)
                
                # Get move counts for this square
                white_moves = white_heat_map.get((row, col), 0)
                black_moves = black_heat_map.get((row, col), 0)
                
                # Apply heat map overlay if there are moves to this square
                if white_moves > 0 or black_moves > 0:
                    # Check if both colors can move to this square (contested square)
                    if white_moves > 0 and black_moves > 0:
                        # Contested square - use red text and color based on dominance
                        text_color = (255, 0, 0)  # Red text for contested squares
                        if white_moves >= black_moves:
                            heat_color = self._get_white_heat_color(white_moves)
                            move_count = white_moves
                        else:
                            heat_color = self._get_black_heat_color(black_moves)
                            move_count = black_moves
                    elif white_moves > 0:
                        # White only - white dominance
                        heat_color = self._get_white_heat_color(white_moves)
                        text_color = (0, 0, 0)  # Black text
                        move_count = white_moves
                    else:
                        # Black only - black dominance
                        heat_color = self._get_black_heat_color(black_moves)
                        text_color = (255, 255, 255)  # White text
                        move_count = black_moves
                    
                    # Draw heat overlay
                    heat_surface = pygame.Surface((ui.square_size, ui.square_size))
                    heat_surface.set_alpha(120)  # Semi-transparent
                    heat_surface.fill(heat_color)
                    screen.blit(heat_surface, (x, y))
                    
                    # Draw move count number
                    font = pygame.font.Font(None, max(12, ui.square_size // 3))
                    text = font.render(str(move_count), True, text_color)
                    text_rect = text.get_rect(center=(x + ui.square_size // 2, y + ui.square_size // 2))
                    screen.blit(text, text_rect)
        
        # Render pieces on top of heat map
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board.get_piece((row, col))
                if piece:
                    x = board_start_x + col * ui.square_size
                    y = board_start_y + row * ui.square_size
                    square_rect = pygame.Rect(x, y, ui.square_size, ui.square_size)
                    ui.render_piece(piece, square_rect)
                    
                    # Show behavior indicator if piece has non-default behavior
                    if piece.behavior != "default":
                        ui.render_behavior_indicator(piece, square_rect)
    
    def _calculate_heat_map_data(self, board: ChessBoard) -> Tuple[Dict[Tuple[int, int], int], Dict[Tuple[int, int], int]]:
        """
        Calculate heat map data for both colors.
        Returns tuple of (white_heat_map, black_heat_map) where each is a dict of position -> move_count
        """
        white_heat_map = {}
        black_heat_map = {}
        
        # Get all pieces and their possible moves
        for piece, position in board.get_all_pieces():
            valid_moves = piece.get_valid_moves(position, board)
            
            # Count moves for each target square
            for move_pos in valid_moves:
                if piece.color == "white":
                    white_heat_map[move_pos] = white_heat_map.get(move_pos, 0) + 1
                else:  # black
                    black_heat_map[move_pos] = black_heat_map.get(move_pos, 0) + 1
        
        return white_heat_map, black_heat_map
    
    def _get_white_heat_color(self, move_count: int) -> Tuple[int, int, int]:
        """
        Get color for white heat map based on move count.
        More moves = whiter color
        """
        # Base intensity calculation (cap at 10 moves for color scaling)
        intensity = min(move_count, 10) / 10.0
        
        # Start with light color and make it whiter
        base_white = 200
        white_value = int(base_white + (255 - base_white) * intensity)
        
        return (white_value, white_value, white_value)
    
    def _get_black_heat_color(self, move_count: int) -> Tuple[int, int, int]:
        """
        Get color for black heat map based on move count.
        More moves = blacker color
        """
        # Base intensity calculation (cap at 10 moves for color scaling)
        intensity = min(move_count, 10) / 10.0
        
        # Start with dark color and make it blacker
        base_black = 100
        black_value = int(base_black * (1 - intensity))
        
        return (black_value, black_value, black_value)
    
    def enable_incremental_test_mode(self):
        """
        Enable incremental game mode testing features.
        """
        # TODO: Implement incremental testing features
        pass
