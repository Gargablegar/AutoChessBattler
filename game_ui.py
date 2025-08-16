"""
Game UI - Handles rendering and user interface for the AutoChess game
"""

import pygame
import os
from typing import List, Tuple, Optional
from autochess_pieces import AutoChessPiece
from board import ChessBoard

class GameUI:
    """Handles the graphical user interface for the chess game"""
    
    def __init__(self, board_size: int):
        # Action button images
        self.action_icons = {
            'select': pygame.image.load(os.path.join('svgs', 'selection.svg')),
            'move': pygame.image.load(os.path.join('svgs', 'moveArrow.svg')),
            'upgrade': pygame.image.load(os.path.join('svgs', 'upgrade.svg')),
        }
        self.action_icon_size = 32
        # Button rects for click detection
        self.left_action_buttons = []
        self.right_action_buttons = []
        self.action_button_hover = None  # (side, index) if hovering
        self.active_action_button = None  # (side, action) for currently active button
        self.select_mode = {'white': False, 'black': False}
        self.selection_box = None  # (start_pos, end_pos)
        self.selected_pieces_group = {'white': [], 'black': []}
        self.drag_start_pos = None  # Starting position for drag selection
        self.dragging_selection = False  # Whether user is actively dragging
        self.active_selection_color = None  # Which color is doing selection
        self.board_size = board_size
        
        # Calculate dimensions
        self.square_size = min(600 // board_size, 30)  # Adaptive square size
        self.board_width = self.square_size * board_size
        self.board_height = self.square_size * board_size
        
        # Side panel dimensions
        self.side_panel_width = 200
        self.top_panel_height = 80
        self.message_area_height = 60  # New dedicated area for messages below board
        
        # Calculate minimum height needed for piece selections
        # Each piece takes 35 pixels height, we have 6 pieces per player
        pieces_per_player = 6
        piece_height = 35
        piece_area_height = pieces_per_player * piece_height
        side_panel_padding = 60  # Space for points display and label
        min_side_panel_height = piece_area_height + side_panel_padding
        
        # Total window dimensions - ensure enough height for piece selections and message area
        self.window_width = self.board_width + 2 * self.side_panel_width
        min_window_height = self.top_panel_height + min_side_panel_height
        board_window_height = self.board_height + self.top_panel_height + self.message_area_height
        self.window_height = max(min_window_height, board_window_height)
        
        # Initialize pygame display
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("AutoChess Game")
        
        # Colors
        self.colors = {
            'light_square': (240, 217, 181),
            'dark_square': (181, 136, 99),
            'background': (50, 50, 50),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'button': (100, 150, 200),
            'button_hover': (120, 170, 220),
            'text': (255, 255, 255),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'blue': (0, 150, 255),  # Blue for defensive behavior
            'selected': (255, 255, 0),
            'affordable': (0, 255, 0),
            'unaffordable': (128, 128, 128),
            'frontline': (255, 50, 50),  # Red for frontline zones
            'error': (255, 100, 100)     # Light red for error messages
        }
        
        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)
        
        # Button setup
        self.play_button_rect = pygame.Rect(
            self.window_width // 2 - 60, 
            20, 
            120, 
            40
        )
        
        # AutoTurns input field setup - positioned in top right corner
        self.auto_turns_rect = pygame.Rect(
            self.window_width - 90,  # 90 pixels from right edge (80 width + 10 margin)
            20,
            80,
            40
        )
        self.auto_turns_input_active = False
        self.auto_turns_text = "1"  # Default value
        
        # Behavior icon system
        self.behavior_icons_visible = False
        self.selected_piece_for_behavior = None
        self.selected_piece_position = None
        self.behavior_icon_size = 30
        self.behavior_icons = {}  # Will store icon positions and types
        
        # Load piece images
        self.piece_images = self.load_piece_images()
    
    def load_piece_images(self) -> dict:
        """Load all piece images"""
        images = {}
        piece_types = ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']
        colors = ['White', 'Black']
        
        for piece_type in piece_types:
            for color in colors:
                filename = f"{piece_type}_{color}.svg.png"
                filepath = os.path.join("svgs", filename)
                
                if os.path.exists(filepath):
                    try:
                        # Load and scale image to fit square
                        image = pygame.image.load(filepath)
                        scaled_image = pygame.transform.scale(
                            image, 
                            (int(self.square_size * 0.8), int(self.square_size * 0.8))
                        )
                        images[f"{piece_type}_{color}"] = scaled_image
                    except pygame.error as e:
                        print(f"Error loading {filepath}: {e}")
                        # Create a placeholder if image fails to load
                        images[f"{piece_type}_{color}"] = self.create_piece_placeholder(piece_type, color)
                else:
                    print(f"Image not found: {filepath}")
                    images[f"{piece_type}_{color}"] = self.create_piece_placeholder(piece_type, color)
        
        return images
    
    def create_piece_placeholder(self, piece_type: str, color: str) -> pygame.Surface:
        """Create a text-based placeholder for missing piece images"""
        surface = pygame.Surface((int(self.square_size * 0.8), int(self.square_size * 0.8)))
        surface.fill(self.colors['white'] if color == 'White' else self.colors['black'])
        
        text_color = self.colors['black'] if color == 'White' else self.colors['white']
        text = self.font.render(piece_type[0], True, text_color)
        text_rect = text.get_rect(center=surface.get_rect().center)
        surface.blit(text, text_rect)
        return surface
        
    def get_clicked_position(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple]:
        """Convert mouse position to board position or side panel click"""
        x, y = mouse_pos
        board_start_x = self.side_panel_width
        board_start_y = self.top_panel_height
        
        # Check if click is on board
        if (board_start_x <= x < board_start_x + self.board_width and 
            board_start_y <= y < board_start_y + self.board_height):
            col = (x - board_start_x) // self.square_size
            row = (y - board_start_y) // self.square_size
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                return ((row, col), None, -1)
        
        # Check if click is on left side panel (white pieces)
        side_panel_bottom = self.top_panel_height + self.board_height
        if (0 <= x < self.side_panel_width and 
            self.top_panel_height + 60 <= y < side_panel_bottom):
            piece_index = (y - (self.top_panel_height + 60)) // 35
            return (None, 'white', piece_index)
        
        # Check if click is on right side panel (black pieces)
        right_panel_x = self.side_panel_width + self.board_width
        if (right_panel_x <= x < self.window_width and 
            self.top_panel_height + 60 <= y < side_panel_bottom):
            piece_index = (y - (self.top_panel_height + 60)) // 35
            return (None, 'black', piece_index)
        
        return None
    
    def get_clicked_piece(self, mouse_pos: Tuple[int, int], player_color: str) -> Optional[int]:
        """Get the piece clicked in the side panel for the specified player color"""
        click_info = self.get_clicked_position(mouse_pos)
        if not click_info:
            return None
        
        board_pos, panel_color, piece_index = click_info
        
        # Return piece index if the clicked panel matches the requested color
        if panel_color == player_color and piece_index >= 0:
            return piece_index
        return None
    
    def get_board_position(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Get board position from mouse click"""
        click_info = self.get_clicked_position(mouse_pos)
        if click_info and click_info[0]:
            return click_info[0]
        return None
    
    def is_click_on_piece_area(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if click is on a side panel (piece selection area)"""
        click_info = self.get_clicked_position(mouse_pos)
        return click_info and click_info[1] is not None
    
    def is_click_on_board(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if click is on the game board"""
        click_info = self.get_clicked_position(mouse_pos)
        return click_info and click_info[0] is not None
    
    def is_click_on_play_button(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the mouse click is on the play turn button"""
        return self.play_button_rect.collidepoint(mouse_pos)
    
    def is_click_on_auto_turns_field(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the mouse click is on the auto turns input field"""
        return self.auto_turns_rect.collidepoint(mouse_pos)
    
    def activate_auto_turns_input(self):
        """Activate the auto turns input field for editing"""
        # Clear all other active states first
        self.clear_all_active_states()
        
        # Then activate auto turns input
        self.auto_turns_input_active = True
        # Don't change the text field here - it should show current value
        print("AutoTurns input activated. Type a number and press Enter.")
    
    def deactivate_auto_turns_input(self):
        """Deactivate the auto turns input field"""
        self.auto_turns_input_active = False
    
    def set_auto_turns_display_value(self, value: int):
        """Set the display value for auto turns when not in input mode"""
        if not self.auto_turns_input_active:
            self.auto_turns_text = str(value)
    
    def show_behavior_icons(self, piece: AutoChessPiece, board_position: Tuple[int, int]):
        """Show behavior icons above the selected piece"""
        self.behavior_icons_visible = True
        self.selected_piece_for_behavior = piece
        self.selected_piece_position = board_position
        
        # Calculate icon positions above the piece
        board_start_x = self.side_panel_width
        board_start_y = self.top_panel_height
        
        piece_x = board_start_x + board_position[1] * self.square_size
        piece_y = board_start_y + board_position[0] * self.square_size
        
        # Position icons above the piece, but ensure they're visible
        icon_y = piece_y - self.behavior_icon_size - 10
        
        # If icons would be above the board area, place them below the piece instead
        if icon_y < self.top_panel_height:
            icon_y = piece_y + self.square_size + 10
        
        icon_spacing = self.behavior_icon_size + 5
        
        # Center the three icons above/below the piece
        total_width = 3 * self.behavior_icon_size + 2 * 5
        start_x = piece_x + (self.square_size - total_width) // 2
        
        # Ensure icons don't go outside the window bounds
        if start_x < 0:
            start_x = 10
        elif start_x + total_width > self.window_width:
            start_x = self.window_width - total_width - 10
        
        self.behavior_icons = {
            "aggressive": pygame.Rect(start_x, icon_y, self.behavior_icon_size, self.behavior_icon_size),
            "defensive": pygame.Rect(start_x + icon_spacing, icon_y, self.behavior_icon_size, self.behavior_icon_size),
            "passive": pygame.Rect(start_x + 2 * icon_spacing, icon_y, self.behavior_icon_size, self.behavior_icon_size)
        }
    
    def hide_behavior_icons(self):
        """Hide behavior icons"""
        self.behavior_icons_visible = False
        self.selected_piece_for_behavior = None
        self.selected_piece_position = None
        self.behavior_icons = {}
    
    def get_clicked_behavior_icon(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Check if a behavior icon was clicked and return the behavior type"""
        if not self.behavior_icons_visible:
            return None
        
        for behavior, rect in self.behavior_icons.items():
            if rect.collidepoint(mouse_pos):
                return behavior
        return None
    
    def show_group_behavior_selection(self, color: str):
        """Show behavior selection for a group of selected pieces"""
        selected_pieces = self.selected_pieces_group[color]
        if not selected_pieces:
            return
            
        self.behavior_icons_visible = True
        # Use a dummy piece for behavior selection - we'll apply to all selected pieces
        self.selected_piece_for_behavior = selected_pieces[0] if selected_pieces else None
        self.selected_piece_position = None  # No specific position for group selection
        
        # Position icons in the center of the board
        board_start_x = self.side_panel_width
        board_center_x = board_start_x + self.board_width // 2
        board_center_y = self.top_panel_height + self.board_height // 2
        
        icon_spacing = self.behavior_icon_size + 10
        total_width = 3 * self.behavior_icon_size + 2 * 10
        start_x = board_center_x - total_width // 2
        icon_y = board_center_y - self.behavior_icon_size // 2
        
        self.behavior_icons = {
            "aggressive": pygame.Rect(start_x, icon_y, self.behavior_icon_size, self.behavior_icon_size),
            "defensive": pygame.Rect(start_x + icon_spacing, icon_y, self.behavior_icon_size, self.behavior_icon_size),
            "passive": pygame.Rect(start_x + 2 * icon_spacing, icon_y, self.behavior_icon_size, self.behavior_icon_size)
        }
    
    def create_behavior_icon(self, behavior: str, rect: pygame.Rect) -> pygame.Surface:
        """Create a visual representation of a behavior icon"""
        icon_surface = pygame.Surface((rect.width, rect.height))
        
        # Fill with a semi-transparent dark background
        icon_surface.fill((40, 40, 40))
        
        # Draw border
        pygame.draw.rect(icon_surface, self.colors['white'], icon_surface.get_rect(), 2)
        
        # Draw icon content based on behavior
        center_x, center_y = rect.width // 2, rect.height // 2
        
        if behavior == "aggressive":  # Swords
            # Draw crossed swords in red
            pygame.draw.line(icon_surface, self.colors['red'], (6, 6), (rect.width - 6, rect.height - 6), 3)
            pygame.draw.line(icon_surface, self.colors['red'], (rect.width - 6, 6), (6, rect.height - 6), 3)
            # Add small rectangles for sword hilts
            pygame.draw.rect(icon_surface, self.colors['red'], (center_x - 2, 4, 4, 6))
            pygame.draw.rect(icon_surface, self.colors['red'], (center_x - 2, rect.height - 10, 4, 6))
            
        elif behavior == "defensive":  # Shield
            # Draw shield shape in blue
            shield_points = [
                (center_x, 6),
                (center_x + 8, 9),
                (center_x + 8, center_y + 3),
                (center_x, rect.height - 6),
                (center_x - 8, center_y + 3),
                (center_x - 8, 9)
            ]
            pygame.draw.polygon(icon_surface, self.colors['blue'], shield_points)
            pygame.draw.polygon(icon_surface, self.colors['white'], shield_points, 2)
            
        elif behavior == "passive":  # Hourglass
            # Draw hourglass in yellow
            # Top triangle
            pygame.draw.polygon(icon_surface, self.colors['selected'], 
                              [(center_x - 8, 6), (center_x + 8, 6), (center_x, center_y)])
            # Bottom triangle
            pygame.draw.polygon(icon_surface, self.colors['selected'], 
                              [(center_x, center_y), (center_x - 8, rect.height - 6), (center_x + 8, rect.height - 6)])
            # Outline
            pygame.draw.polygon(icon_surface, self.colors['white'], 
                              [(center_x - 8, 6), (center_x + 8, 6), (center_x + 8, rect.height - 6), 
                               (center_x - 8, rect.height - 6)], 2)
        
        return icon_surface
    
    
    def render_board(self, board: ChessBoard, frontline_zones: List[Tuple[int, int, int, int]] = None):
        """Render the chess board with pieces and frontline zones"""
        board_start_x = self.side_panel_width
        board_start_y = self.top_panel_height
        
        # Draw board squares
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = board_start_x + col * self.square_size
                y = board_start_y + row * self.square_size
                
                # Alternate colors
                color = self.colors['light_square'] if (row + col) % 2 == 0 else self.colors['dark_square']
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
        
        # Draw frontline zones if provided
        if frontline_zones:
            for min_row, max_row, min_col, max_col, zone_color in frontline_zones:
                # Draw border around the frontline zone using the specified color
                zone_x = board_start_x + min_col * self.square_size
                zone_y = board_start_y + min_row * self.square_size
                zone_width = (max_col - min_col + 1) * self.square_size
                zone_height = (max_row - min_row + 1) * self.square_size
                
                # Draw colored border (3 pixel thick)
                pygame.draw.rect(self.screen, zone_color, 
                               (zone_x - 3, zone_y - 3, zone_width + 6, zone_height + 6), 3)
        
        # Draw pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board.get_piece((row, col))
                if piece:
                    x = board_start_x + col * self.square_size
                    y = board_start_y + row * self.square_size
                    square_rect = pygame.Rect(x, y, self.square_size, self.square_size)
                    self.render_piece(piece, square_rect)
                    
                    # Show behavior indicator if piece has non-default behavior
                    if piece.behavior != "default":
                        self.render_behavior_indicator(piece, square_rect)
    
    def render_piece(self, piece: AutoChessPiece, square_rect: pygame.Rect):
        """Render a piece on a square"""
        color_name = "White" if piece.color == "white" else "Black"
        image_key = f"{piece.piece_type}_{color_name}"
        
        if image_key in self.piece_images:
            image = self.piece_images[image_key]
            # Center the piece in the square
            image_rect = image.get_rect(center=square_rect.center)
            self.screen.blit(image, image_rect)
    
    def render_behavior_indicator(self, piece: AutoChessPiece, square_rect: pygame.Rect):
        """Render a small indicator showing the piece's current behavior"""
        if piece.behavior == "default":
            return
        
        # Choose color based on behavior
        color_map = {
            "aggressive": self.colors['red'],
            "defensive": self.colors['blue'], 
            "passive": self.colors['selected']
        }
        
        indicator_color = color_map.get(piece.behavior, self.colors['white'])
        
        # Draw small circle in corner of square
        indicator_radius = 4
        indicator_pos = (square_rect.right - 8, square_rect.top + 8)
        pygame.draw.circle(self.screen, indicator_color, indicator_pos, indicator_radius)
        pygame.draw.circle(self.screen, self.colors['black'], indicator_pos, indicator_radius, 1)
    
    def render_behavior_icons(self):
        """Render the behavior selection icons"""
        if not self.behavior_icons_visible:
            return
        
        # Check if this is group behavior selection
        is_group_selection = (self.active_selection_color and 
                            self.selected_pieces_group[self.active_selection_color] and 
                            self.selected_piece_position is None)
        
        # Draw group selection label if applicable
        if is_group_selection:
            group_count = len(self.selected_pieces_group[self.active_selection_color])
            label_text = f"Set behavior for {group_count} {self.active_selection_color} pieces:"
            label_surface = self.font.render(label_text, True, self.colors['white'])
            
            # Position label above the behavior icons
            first_icon_rect = list(self.behavior_icons.values())[0]
            label_x = first_icon_rect.x
            label_y = first_icon_rect.y - 30
            
            # Draw background for label
            label_bg = pygame.Rect(label_x - 5, label_y - 5, label_surface.get_width() + 10, label_surface.get_height() + 10)
            pygame.draw.rect(self.screen, (0, 0, 0), label_bg)
            pygame.draw.rect(self.screen, self.colors['white'], label_bg, 1)
            
            self.screen.blit(label_surface, (label_x, label_y))
        
        for behavior, rect in self.behavior_icons.items():
            # Create and draw the icon with a background
            icon_surface = self.create_behavior_icon(behavior, rect)
            
            # Draw a subtle drop shadow first
            shadow_rect = rect.copy()
            shadow_rect.move_ip(2, 2)
            shadow_surface = pygame.Surface((rect.width, rect.height))
            shadow_surface.fill((0, 0, 0))
            shadow_surface.set_alpha(100)
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Draw the main icon
            self.screen.blit(icon_surface, rect)
            
            # Highlight if this is the current behavior
            if (self.selected_piece_for_behavior and 
                self.selected_piece_for_behavior.behavior == behavior):
                pygame.draw.rect(self.screen, self.colors['selected'], rect, 3)
            else:
                # Draw a subtle border for unselected icons
                pygame.draw.rect(self.screen, self.colors['white'], rect, 1)
    
    def render_side_panels(self, white_pieces: List[AutoChessPiece], black_pieces: List[AutoChessPiece], 
                          player_points: dict, selected_piece: AutoChessPiece = None, piece_costs: dict = None):
        """Render the side panels with off-board pieces and points"""
        if piece_costs is None:
            piece_costs = {}
        
        # Left panel (White pieces) - exclude message area from panel height
        side_panel_height = self.board_height
        left_panel_rect = pygame.Rect(0, self.top_panel_height, self.side_panel_width, side_panel_height)
        pygame.draw.rect(self.screen, self.colors['background'], left_panel_rect)
        
        # White points display
        points_text = f"Points: {player_points['white']}"
        points_surface = self.font.render(points_text, True, self.colors['green'])
        self.screen.blit(points_surface, (10, self.top_panel_height + 10))
        
        # White pieces label
        white_label = self.font.render("White Pieces", True, self.colors['white'])
        self.screen.blit(white_label, (10, self.top_panel_height + 35))
        
        # Render white pieces
        y_offset = self.top_panel_height + 60
        for i, piece in enumerate(white_pieces):
            # Get piece cost
            piece_cost = piece_costs.get(piece.__class__.__name__, piece.value)
            
            # Determine if piece is affordable
            affordable = player_points['white'] >= piece_cost
            text_color = self.colors['white'] if affordable else self.colors['unaffordable']
            
            # Highlight selected piece
            if piece == selected_piece:
                highlight_rect = pygame.Rect(5, y_offset + i * 35 - 2, self.side_panel_width - 10, 30)
                pygame.draw.rect(self.screen, self.colors['selected'], highlight_rect)
            
            piece_text = f"{piece.piece_type} ({piece_cost})"
            text_surface = self.font.render(piece_text, True, text_color)
            self.screen.blit(text_surface, (10, y_offset + i * 35))
        
        # Right panel (Black pieces) - exclude message area from panel height
        right_panel_rect = pygame.Rect(
            self.side_panel_width + self.board_width, 
            self.top_panel_height, 
            self.side_panel_width, 
            side_panel_height
        )
        pygame.draw.rect(self.screen, self.colors['background'], right_panel_rect)
        
        # Black points display
        points_text = f"Points: {player_points['black']}"
        points_surface = self.font.render(points_text, True, self.colors['green'])
        self.screen.blit(points_surface, (right_panel_rect.x + 10, self.top_panel_height + 10))
        
        # Black pieces label
        black_label = self.font.render("Black Pieces", True, self.colors['white'])
        self.screen.blit(black_label, (right_panel_rect.x + 10, self.top_panel_height + 35))
        
        # Render black pieces
        for i, piece in enumerate(black_pieces):
            # Get piece cost
            piece_cost = piece_costs.get(piece.__class__.__name__, piece.value)
            
            # Determine if piece is affordable
            affordable = player_points['black'] >= piece_cost
            text_color = self.colors['white'] if affordable else self.colors['unaffordable']
            
            # Highlight selected piece
            if piece == selected_piece:
                highlight_rect = pygame.Rect(right_panel_rect.x + 5, y_offset + i * 35 - 2, 
                                           self.side_panel_width - 10, 30)
                pygame.draw.rect(self.screen, self.colors['selected'], highlight_rect)
            
            piece_text = f"{piece.piece_type} ({piece_cost})"
            text_surface = self.font.render(piece_text, True, text_color)
            self.screen.blit(text_surface, (right_panel_rect.x + 10, y_offset + i * 35))
    def handle_action_button_hover(self, mouse_pos):
        """Update hover state for action buttons."""
        self.action_button_hover = None
        for i, (rect, _, _) in enumerate(self.left_action_buttons):
            if rect.collidepoint(mouse_pos):
                self.action_button_hover = ('left', i)
                return
        for i, (rect, _, _) in enumerate(self.right_action_buttons):
            if rect.collidepoint(mouse_pos):
                self.action_button_hover = ('right', i)
                return

    def handle_action_button_click(self, mouse_pos):
        """Handle clicks on action buttons. Returns (side, action) or None."""
        for i, (rect, name, _) in enumerate(self.left_action_buttons):
            if rect.collidepoint(mouse_pos):
                return ('white', name)
        for i, (rect, name, _) in enumerate(self.right_action_buttons):
            if rect.collidepoint(mouse_pos):
                return ('black', name)
        return None

    def start_select_mode(self, color):
        print(f"DEBUG: start_select_mode called for {color}")
        
        # Clear only conflicting states, but preserve selection mode
        self.auto_turns_input_active = False
        self.hide_behavior_icons()
        
        # Set up selection mode for this color
        self.select_mode[color] = True
        self.selection_box = None
        self.selected_pieces_group[color] = []
        self.active_action_button = (color, 'select')
        self.active_selection_color = color
        print(f"DEBUG: active_selection_color set to: {self.active_selection_color}")
        
        # Deselect other player's select mode
        other_color = 'black' if color == 'white' else 'white'
        self.select_mode[other_color] = False
        self.selected_pieces_group[other_color] = []

    def stop_select_mode(self, color):
        print(f"DEBUG: stop_select_mode called for {color}")
        self.select_mode[color] = False
        self.selection_box = None
        self.drag_start_pos = None
        self.dragging_selection = False
        
        # Clear selection-related state
        if self.active_selection_color == color:
            self.active_selection_color = None
        
        # Clear selected pieces for this color
        self.selected_pieces_group[color] = []
        
        # Clear active action button if it's for this color's select mode
        if self.active_action_button == (color, 'select'):
            self.active_action_button = None
        
        # Hide behavior icons if they were shown for group selection
        if self.behavior_icons_visible and not self.selected_piece_for_behavior:
            self.hide_behavior_icons()

    def set_active_button(self, color, action):
        """Set the active button and deselect all others"""
        # Deactivate all modes first
        self.select_mode['white'] = False
        self.select_mode['black'] = False
        self.selection_box = None
        self.drag_start_pos = None
        
        # Set new active button
        self.active_action_button = (color, action)
        
        if action == 'select':
            self.select_mode[color] = True

    def start_drag_selection(self, start_pos):
        """Start drag selection at the given position"""
        if self.is_click_on_board(start_pos):
            self.drag_start_pos = start_pos
            self.selection_box = (start_pos, start_pos)
            self.dragging_selection = True
            print(f"Started drag selection at {start_pos}")

    def update_drag_selection(self, current_pos):
        """Update drag selection to current mouse position"""
        if self.dragging_selection and self.drag_start_pos:
            self.selection_box = (self.drag_start_pos, current_pos)
            # print(f"Updating drag selection to {current_pos}")  # Commented out to avoid spam

    def finish_drag_selection(self, board):
        """Finish drag selection and select pieces in the box"""
        if self.dragging_selection and self.selection_box and self.active_selection_color:
            selected_pieces = self.select_pieces_in_box(board, self.active_selection_color)
            self.dragging_selection = False
            print(f"Finished drag selection, selected {len(selected_pieces)} pieces")
            # Keep selection box visible to show what was selected
            
    def clear_selection(self, color):
        """Clear the selection for a color"""
        self.selected_pieces_group[color] = []
        if not any(self.selected_pieces_group.values()):  # If no selections remain
            self.selection_box = None
            self.drag_start_pos = None
            self.dragging_selection = False

    def update_drag_selection(self, current_pos):
        """Update drag selection to current mouse position"""
        if self.drag_start_pos:
            self.selection_box = (self.drag_start_pos, current_pos)

    def update_selection_box(self, start_pos, end_pos):
        self.selection_box = (start_pos, end_pos)

    def render_selection_box(self):
        if self.selection_box:
            start, end = self.selection_box
            x1, y1 = start
            x2, y2 = end
            rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
            pygame.draw.rect(self.screen, self.colors['selected'], rect, 2)

    def select_pieces_in_box(self, board, color):
        """Select all pieces of color under the selection box."""
        if not self.selection_box:
            return []
        start, end = self.selection_box
        x1, y1 = min(start[0], end[0]), min(start[1], end[1])
        x2, y2 = max(start[0], end[0]), max(start[1], end[1])
        selected = []
        for piece, (row, col) in board.get_all_pieces():
            if piece.color != color:
                continue
            # Convert board pos to pixel
            px = self.side_panel_width + col * self.square_size + self.square_size//2
            py = self.top_panel_height + row * self.square_size + self.square_size//2
            if x1 <= px <= x2 and y1 <= py <= y2:
                selected.append(piece)
        self.selected_pieces_group[color] = selected
        return selected

    def render_selected_pieces(self, board):
        """Render highlights around selected pieces"""
        for color in ['white', 'black']:
            if self.selected_pieces_group[color]:
                highlight_color = self.colors['selected']
                for piece in self.selected_pieces_group[color]:
                    # Find piece position on board
                    for p, (row, col) in board.get_all_pieces():
                        if p == piece:
                            x = self.side_panel_width + col * self.square_size
                            y = self.top_panel_height + row * self.square_size
                            highlight_rect = pygame.Rect(x - 2, y - 2, self.square_size + 4, self.square_size + 4)
                            pygame.draw.rect(self.screen, highlight_color, highlight_rect, 3)
                            break

    def get_selected_pieces_count(self, color):
        """Get count of selected pieces for a color"""
        return len(self.selected_pieces_group[color])

    def clear_selected_pieces(self, color):
        """Clear selected pieces for a color"""
        self.selected_pieces_group[color] = []
    
    def clear_all_active_states(self):
        """Clear all active button states, selection modes, and input fields"""
        print("DEBUG: clear_all_active_states called")
        # Clear action button states
        self.active_action_button = None
        
        # Clear selection modes
        self.select_mode['white'] = False
        self.select_mode['black'] = False
        self.selection_box = None
        self.drag_start_pos = None
        self.dragging_selection = False
        self.active_selection_color = None
        
        # Clear piece selections
        self.selected_pieces_group['white'] = []
        self.selected_pieces_group['black'] = []
        
        # Clear auto turns input
        self.auto_turns_input_active = False
        
        # Clear behavior icons
        self.hide_behavior_icons()
    
    def render_selection_overlay(self):
        """Render selection box and selected pieces overlay"""
        # Draw selection box if active
        if self.selection_box:
            start, end = self.selection_box
            x1, y1 = start
            x2, y2 = end
            
            # Calculate selection rectangle
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            print(f"Rendering selection box: {left},{top},{width},{height}")
            
            # Draw selection box
            selection_rect = pygame.Rect(left, top, width, height)
            pygame.draw.rect(self.screen, (255, 255, 0), selection_rect, 4)  # Bright yellow, thick line
            
            # Fill with semi-transparent overlay if actively dragging
            if self.dragging_selection and width > 0 and height > 0:
                overlay = pygame.Surface((width, height))
                overlay.set_alpha(50)
                overlay.fill((100, 150, 255))
                self.screen.blit(overlay, (left, top))
        else:
            # Debug: check if render is called when no selection box
            if self.select_mode['white'] or self.select_mode['black']:
                print(f"Render called but no selection box. Select modes: {self.select_mode}")
    
    def render_top_panel(self, turn_counter: int, auto_turns: int = 1):
        """Render the top panel with turn counter, play button, and auto turns field"""
        top_panel_rect = pygame.Rect(0, 0, self.window_width, self.top_panel_height)
        pygame.draw.rect(self.screen, self.colors['background'], top_panel_rect)
        
        # Turn counter
        turn_text = f"Turn: {turn_counter}"
        turn_surface = self.large_font.render(turn_text, True, self.colors['white'])
        self.screen.blit(turn_surface, (20, 25))
        
        # Calculate button height to match Play Turn button
        button_height = self.play_button_rect.height
        button_y = self.play_button_rect.y
        
        # Draw white player action buttons (left of Play Turn button)
        self.left_action_buttons = []
        button_spacing = 5
        total_white_width = 3 * button_height + 2 * button_spacing  # 3 buttons with spacing
        white_start_x = self.play_button_rect.left - total_white_width - 10  # 10px gap from Play Turn
        
        for i, (name, tooltip) in enumerate([
            ('select', 'Select group'),
            ('move', 'Force Move'),
            ('upgrade', 'Upgrade piece')
        ]):
            icon = pygame.transform.scale(self.action_icons[name], (button_height, button_height))
            rect = pygame.Rect(white_start_x + i * (button_height + button_spacing), button_y, button_height, button_height)
            self.screen.blit(icon, rect)
            self.left_action_buttons.append((rect, name, tooltip))
            # Draw border if hovered or active
            if self.action_button_hover == ('left', i):
                pygame.draw.rect(self.screen, self.colors['selected'], rect, 2)
            elif self.active_action_button == ('white', name):
                pygame.draw.rect(self.screen, self.colors['green'], rect, 3)
        
        # Draw black player action buttons (right of Play Turn button)
        self.right_action_buttons = []
        black_start_x = self.play_button_rect.right + 10  # 10px gap from Play Turn
        
        for i, (name, tooltip) in enumerate([
            ('select', 'Select group'),
            ('move', 'Force Move'),
            ('upgrade', 'Upgrade piece')
        ]):
            icon = pygame.transform.scale(self.action_icons[name], (button_height, button_height))
            rect = pygame.Rect(black_start_x + i * (button_height + button_spacing), button_y, button_height, button_height)
            self.screen.blit(icon, rect)
            self.right_action_buttons.append((rect, name, tooltip))
            # Draw border if hovered or active
            if self.action_button_hover == ('right', i):
                pygame.draw.rect(self.screen, self.colors['selected'], rect, 2)
            elif self.active_action_button == ('black', name):
                pygame.draw.rect(self.screen, self.colors['green'], rect, 3)
        
        # Play turn button
        pygame.draw.rect(self.screen, self.colors['button'], self.play_button_rect)
        pygame.draw.rect(self.screen, self.colors['black'], self.play_button_rect, 2)
        
        button_text = self.font.render("Play Turn", True, self.colors['white'])
        button_text_rect = button_text.get_rect(center=self.play_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Tooltip for buttons (render on top)
        if self.action_button_hover:
            side, button_index = self.action_button_hover
            if side == 'left' and button_index < len(self.left_action_buttons):
                _, _, tooltip = self.left_action_buttons[button_index]
                tip_surface = self.font.render(tooltip, True, self.colors['selected'])
                tip_rect = self.left_action_buttons[button_index][0]
                self.screen.blit(tip_surface, (tip_rect.x, tip_rect.bottom + 5))
            elif side == 'right' and button_index < len(self.right_action_buttons):
                _, _, tooltip = self.right_action_buttons[button_index]
                tip_surface = self.font.render(tooltip, True, self.colors['selected'])
                tip_rect = self.right_action_buttons[button_index][0]
                self.screen.blit(tip_surface, (tip_rect.x, tip_rect.bottom + 5))
        
        # AutoTurns label - positioned to the left of the input field
        auto_turns_label = self.font.render("AutoTurns:", True, self.colors['white'])
        label_rect = auto_turns_label.get_rect()
        label_rect.right = self.auto_turns_rect.left - 5  # 5 pixels gap
        label_rect.centery = self.auto_turns_rect.centery
        self.screen.blit(auto_turns_label, label_rect)
        
        # AutoTurns input field
        field_color = self.colors['selected'] if self.auto_turns_input_active else self.colors['white']
        pygame.draw.rect(self.screen, field_color, self.auto_turns_rect)
        pygame.draw.rect(self.screen, self.colors['black'], self.auto_turns_rect, 2)
        
        # AutoTurns text
        display_text = self.auto_turns_text if self.auto_turns_input_active else str(auto_turns)
        auto_turns_surface = self.font.render(display_text, True, self.colors['black'])
        text_rect = auto_turns_surface.get_rect(center=self.auto_turns_rect.center)
        self.screen.blit(auto_turns_surface, text_rect)
    
    def render_error_message(self, error_message: str):
        """Render error message or win message in dedicated area below the board"""
        # Calculate message area position (below the board)
        message_area_start_y = self.top_panel_height + self.board_height
        message_area_rect = pygame.Rect(
            self.side_panel_width,  # Start at board's left edge
            message_area_start_y,
            self.board_width,  # Same width as board
            self.message_area_height
        )
        
        # Draw message area background
        pygame.draw.rect(self.screen, self.colors['background'], message_area_rect)
        pygame.draw.rect(self.screen, self.colors['white'], message_area_rect, 1)  # Border
        
        if error_message:
            # Check if it's a win message
            is_win_message = "wins" in error_message.lower() or "draw" in error_message.lower()
            
            # Choose colors and styling based on message type
            if is_win_message:
                text_color = self.colors['selected']  # Yellow for win messages
                font = self.large_font  # Larger font for win messages
            else:
                text_color = self.colors['error']  # Light red for error messages
                font = self.font
            
            # Create message text surface
            message_surface = font.render(error_message, True, text_color)
            
            # Center the message in the message area
            message_rect = message_surface.get_rect()
            message_rect.center = message_area_rect.center
            
            # Ensure message fits within the area (truncate if necessary)
            if message_rect.width > message_area_rect.width - 20:
                # Text is too long, try to wrap or truncate
                words = error_message.split()
                if len(words) > 1:
                    # Try splitting into two lines
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                    
                    line1_surface = font.render(line1, True, text_color)
                    line2_surface = font.render(line2, True, text_color)
                    
                    # Position the two lines
                    line1_rect = line1_surface.get_rect()
                    line2_rect = line2_surface.get_rect()
                    
                    total_height = line1_rect.height + line2_rect.height + 5  # 5px spacing
                    start_y = message_area_rect.centery - total_height // 2
                    
                    line1_rect.centerx = message_area_rect.centerx
                    line1_rect.y = start_y
                    
                    line2_rect.centerx = message_area_rect.centerx
                    line2_rect.y = start_y + line1_rect.height + 5
                    
                    # Draw both lines if they fit
                    if (line1_rect.width <= message_area_rect.width - 20 and 
                        line2_rect.width <= message_area_rect.width - 20):
                        self.screen.blit(line1_surface, line1_rect)
                        self.screen.blit(line2_surface, line2_rect)
                    else:
                        # Fall back to truncated single line
                        truncated_message = error_message[:50] + "..." if len(error_message) > 50 else error_message
                        truncated_surface = font.render(truncated_message, True, text_color)
                        truncated_rect = truncated_surface.get_rect(center=message_area_rect.center)
                        self.screen.blit(truncated_surface, truncated_rect)
                else:
                    # Single word too long, truncate it
                    truncated_message = error_message[:50] + "..." if len(error_message) > 50 else error_message
                    truncated_surface = font.render(truncated_message, True, text_color)
                    truncated_rect = truncated_surface.get_rect(center=message_area_rect.center)
                    self.screen.blit(truncated_surface, truncated_rect)
            else:
                # Message fits, draw normally
                self.screen.blit(message_surface, message_rect)
    
    def render(self, board: ChessBoard, white_pieces: List[AutoChessPiece], 
               black_pieces: List[AutoChessPiece], turn_counter: int, 
               player_points: dict, selected_piece: AutoChessPiece = None, 
               piece_costs: dict = None, error_message: str = "", 
               frontline_zones: List[Tuple[int, int, int, int]] = None,
               auto_turns: int = 1):
        """Render the entire game state"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Render all components in order (background to foreground)
        self.render_board(board, frontline_zones)
        self.render_side_panels(white_pieces, black_pieces, player_points, selected_piece, piece_costs)
        self.render_top_panel(turn_counter, auto_turns)
        self.render_error_message(error_message)
        
        # Render behavior icons on top of everything else
        if self.behavior_icons_visible:
            self.render_behavior_icons()

        # Render selection box and selected pieces if active
        if self.select_mode['white'] or self.select_mode['black']:
            self.render_selection_overlay()
        
        # Render selected pieces highlights
        if any(self.selected_pieces_group.values()):
            self.render_selected_pieces(board)
        
        # Update display
        pygame.display.flip()
