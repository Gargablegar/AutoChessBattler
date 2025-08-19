#!/usr/bin/env python3
"""
Enhanced GameUI for network play
Adds network-specific UI elements and player perspective handling
"""

import pygame
from typing import Optional, Tuple, List
from game_ui import GameUI as OriginalGameUI


class NetworkGameUI(OriginalGameUI):
    """Enhanced GameUI for network multiplayer"""
    
    def __init__(self, board_size: int, player_color: str):
        super().__init__(board_size)
        self.player_color = player_color
        
        # Network-specific UI elements
        self.connection_status = "Connected"
        self.opponent_color = "black" if player_color == "white" else "white"
        
        # Update window title
        pygame.display.set_caption(f"AutoChess - {player_color.title()} Player")
        
        # Player-specific color scheme adjustments
        if player_color == "black":
            # Optionally adjust colors or layout for black player
            pass
    
    def render_connection_status(self, status: str):
        """Render network connection status"""
        self.connection_status = status
        
        # Choose color based on status
        if status == "Connected":
            color = self.colors['green']
        elif status == "Connecting...":
            color = self.colors['blue']
        else:
            color = self.colors['red']
        
        # Render status in top-right corner
        status_text = self.font.render(f"Network: {status}", True, color)
        status_rect = status_text.get_rect()
        status_rect.topright = (self.window_width - 10, 10)
        self.screen.blit(status_text, status_rect)
    
    def render_player_info(self, white_points: int, black_points: int, 
                          current_turn: int, is_my_turn: bool = True):
        """Render player-specific information"""
        # Highlight current player's side panel
        my_points = white_points if self.player_color == "white" else black_points
        opponent_points = black_points if self.player_color == "white" else white_points
        
        # Render side panels with emphasis on current player
        self.render_side_panels(white_points, black_points, 
                              highlight_player=self.player_color if is_my_turn else None)
        
        # Render turn indicator
        turn_text = f"Turn {current_turn}"
        if is_my_turn:
            turn_text += f" - Your move ({self.player_color})"
        else:
            turn_text += f" - Opponent's move ({self.opponent_color})"
        
        text_color = self.colors['green'] if is_my_turn else self.colors['red']
        turn_surface = self.font.render(turn_text, True, text_color)
        turn_rect = turn_surface.get_rect()
        turn_rect.center = (self.window_width // 2, 50)
        self.screen.blit(turn_surface, turn_rect)
    
    def render_side_panels(self, white_points: int, black_points: int, 
                          selected_piece: Optional[str] = None,
                          current_player: str = "white",
                          highlight_player: Optional[str] = None):
        """Enhanced side panel rendering with player highlighting"""
        # Call original method first
        super().render_side_panels(white_points, black_points, selected_piece, current_player)
        
        # Add highlighting for active player
        if highlight_player:
            if highlight_player == "white":
                # Highlight left panel
                panel_rect = pygame.Rect(10, self.top_panel_height + 10, 
                                       self.side_panel_width - 20, 
                                       self.window_height - self.top_panel_height - 20)
            else:
                # Highlight right panel
                panel_rect = pygame.Rect(self.window_width - self.side_panel_width + 10, 
                                       self.top_panel_height + 10,
                                       self.side_panel_width - 20,
                                       self.window_height - self.top_panel_height - 20)
            
            # Draw highlight border
            pygame.draw.rect(self.screen, self.colors['green'], panel_rect, 3)
    
    def get_clicked_piece_type(self, pos: Tuple[int, int], player_color: str) -> Optional[str]:
        """Get piece type clicked by specific player"""
        # Only allow clicks on the current player's side panel
        if player_color == "white":
            # Check left panel
            if pos[0] < self.side_panel_width:
                return self._get_piece_from_side_panel(pos, "white")
        else:
            # Check right panel
            if pos[0] > self.window_width - self.side_panel_width:
                return self._get_piece_from_side_panel(pos, "black")
        
        return None
    
    def _get_piece_from_side_panel(self, pos: Tuple[int, int], side: str) -> Optional[str]:
        """Helper to get piece type from side panel click"""
        # This would implement the same logic as the original game
        # but restricted to the player's own side panel
        
        # Simplified version - you'd want to copy the exact logic from the original
        piece_types = ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]
        
        # Calculate which piece was clicked based on position
        # This is a simplified implementation
        y_offset = pos[1] - self.top_panel_height - 50  # Adjust for panel start
        if y_offset > 0:
            piece_index = y_offset // 35  # Assuming 35 pixels per piece
            if 0 <= piece_index < len(piece_types):
                return piece_types[piece_index]
        
        return None
    
    def render_waiting_message(self, message: str = "Waiting for opponent..."):
        """Render waiting message when opponent is thinking"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Render waiting message
        text_surface = self.large_font.render(message, True, self.colors['white'])
        text_rect = text_surface.get_rect()
        text_rect.center = (self.window_width // 2, self.window_height // 2)
        self.screen.blit(text_surface, text_rect)
    
    def render_game_over(self, winner: str, is_winner: bool):
        """Render game over screen with network-specific messaging"""
        # Create overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(192)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Determine message and color
        if is_winner:
            message = "🎉 VICTORY! 🎉"
            detail = f"You defeated the {self.opponent_color} player!"
            color = self.colors['green']
        else:
            message = "💀 DEFEAT 💀"
            detail = f"The {winner} player has won!"
            color = self.colors['red']
        
        # Render main message
        main_text = self.large_font.render(message, True, color)
        main_rect = main_text.get_rect()
        main_rect.center = (self.window_width // 2, self.window_height // 2 - 30)
        self.screen.blit(main_text, main_rect)
        
        # Render detail message
        detail_text = self.font.render(detail, True, self.colors['white'])
        detail_rect = detail_text.get_rect()
        detail_rect.center = (self.window_width // 2, self.window_height // 2 + 10)
        self.screen.blit(detail_text, detail_rect)
        
        # Render instructions
        instruction_text = self.font.render("Press ESC to quit", True, self.colors['white'])
        instruction_rect = instruction_text.get_rect()
        instruction_rect.center = (self.window_width // 2, self.window_height // 2 + 50)
        self.screen.blit(instruction_text, instruction_rect)
    
    def get_board_position(self, screen_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board coordinates"""
        x, y = screen_pos
        
        # Calculate board area
        board_start_x = self.side_panel_width
        board_start_y = self.top_panel_height
        
        # Check if click is within board area
        if (board_start_x <= x <= board_start_x + self.board_width and
            board_start_y <= y <= board_start_y + self.board_height):
            
            # Convert to board coordinates
            col = (x - board_start_x) // self.square_size
            row = (y - board_start_y) // self.square_size
            
            # Validate coordinates
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                return (row, col)
        
        return None
    
    def render_piece_preview(self, piece_type: str, mouse_pos: Tuple[int, int]):
        """Render preview of piece being placed"""
        if not piece_type:
            return
        
        # Load piece image
        piece_image = self._get_piece_image(piece_type, self.player_color)
        if piece_image:
            # Scale image to square size
            scaled_image = pygame.transform.scale(piece_image, 
                                                (self.square_size, self.square_size))
            
            # Make it semi-transparent
            scaled_image.set_alpha(128)
            
            # Position at mouse cursor
            preview_rect = scaled_image.get_rect()
            preview_rect.center = mouse_pos
            
            self.screen.blit(scaled_image, preview_rect)
    
    def _get_piece_image(self, piece_type: str, color: str) -> Optional[pygame.Surface]:
        """Get piece image for preview"""
        try:
            import os
            filename = f"{piece_type}_{color.title()}.svg.png"
            filepath = os.path.join('svgs', filename)
            return pygame.image.load(filepath)
        except:
            return None
