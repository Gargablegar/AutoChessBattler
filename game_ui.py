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
        self.board_size = board_size
        
        # Calculate dimensions
        self.square_size = min(600 // board_size, 30)  # Adaptive square size
        self.board_width = self.square_size * board_size
        self.board_height = self.square_size * board_size
        
        # Side panel dimensions
        self.side_panel_width = 200
        self.top_panel_height = 80
        
        # Calculate minimum height needed for piece selections
        # Each piece takes 35 pixels height, we have 6 pieces per player
        pieces_per_player = 6
        piece_height = 35
        piece_area_height = pieces_per_player * piece_height
        side_panel_padding = 60  # Space for points display and label
        min_side_panel_height = piece_area_height + side_panel_padding
        
        # Total window dimensions - ensure enough height for piece selections
        self.window_width = self.board_width + 2 * self.side_panel_width
        min_window_height = self.top_panel_height + min_side_panel_height
        board_window_height = self.board_height + self.top_panel_height
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
        if (0 <= x < self.side_panel_width and 
            self.top_panel_height + 60 <= y < self.window_height):
            piece_index = (y - (self.top_panel_height + 60)) // 35
            return (None, 'white', piece_index)
        
        # Check if click is on right side panel (black pieces)
        right_panel_x = self.side_panel_width + self.board_width
        if (right_panel_x <= x < self.window_width and 
            self.top_panel_height + 60 <= y < self.window_height):
            piece_index = (y - (self.top_panel_height + 60)) // 35
            return (None, 'black', piece_index)
        
        return None
    
    def get_clicked_piece(self, mouse_pos: Tuple[int, int], player_color: str) -> Optional:
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
            for min_row, max_row, min_col, max_col in frontline_zones:
                # Draw red border around the frontline zone
                zone_x = board_start_x + min_col * self.square_size
                zone_y = board_start_y + min_row * self.square_size
                zone_width = (max_col - min_col + 1) * self.square_size
                zone_height = (max_row - min_row + 1) * self.square_size
                
                # Draw red border (3 pixel thick)
                pygame.draw.rect(self.screen, self.colors['frontline'], 
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
        
        # Left panel (White pieces)
        left_panel_rect = pygame.Rect(0, self.top_panel_height, self.side_panel_width, self.board_height)
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
        
        # Right panel (Black pieces)
        right_panel_rect = pygame.Rect(
            self.side_panel_width + self.board_width, 
            self.top_panel_height, 
            self.side_panel_width, 
            self.board_height
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
    
    def render_top_panel(self, turn_counter: int, auto_turns: int = 1):
        """Render the top panel with turn counter, play button, and auto turns field"""
        top_panel_rect = pygame.Rect(0, 0, self.window_width, self.top_panel_height)
        pygame.draw.rect(self.screen, self.colors['background'], top_panel_rect)
        
        # Turn counter
        turn_text = f"Turn: {turn_counter}"
        turn_surface = self.large_font.render(turn_text, True, self.colors['white'])
        self.screen.blit(turn_surface, (20, 25))
        
        # Play turn button
        pygame.draw.rect(self.screen, self.colors['button'], self.play_button_rect)
        pygame.draw.rect(self.screen, self.colors['black'], self.play_button_rect, 2)
        
        button_text = self.font.render("Play Turn", True, self.colors['white'])
        button_text_rect = button_text.get_rect(center=self.play_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
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
        """Render error message or win message at the bottom of the screen"""
        if error_message:
            # Check if it's a win message
            is_win_message = "wins" in error_message.lower() or "draw" in error_message.lower()
            
            # Choose colors and styling based on message type
            if is_win_message:
                text_color = self.colors['selected']  # Yellow for win messages
                bg_alpha = 220  # More opaque for win messages
                font = self.large_font  # Larger font for win messages
            else:
                text_color = self.colors['error']  # Light red for error messages
                bg_alpha = 180
                font = self.font
            
            # Create message text surface
            message_surface = font.render(error_message, True, text_color)
            
            # Position at bottom center of screen
            message_rect = message_surface.get_rect()
            message_rect.centerx = self.window_width // 2
            message_rect.bottom = self.window_height - (20 if is_win_message else 10)
            
            # Draw background
            bg_rect = message_rect.inflate(40 if is_win_message else 20, 20 if is_win_message else 10)
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.set_alpha(bg_alpha)
            bg_surface.fill(self.colors['black'])
            self.screen.blit(bg_surface, bg_rect)
            
            # Draw border for win messages
            if is_win_message:
                pygame.draw.rect(self.screen, text_color, bg_rect, 3)
            
            # Draw message text
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
        
        # Update display
        pygame.display.flip()
