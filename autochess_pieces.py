"""
AutoChess Piece System - Chess piece classes with movement rules
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import os

class AutoChessPiece(ABC):
    """Base class for all chess pieces"""
    
    def __init__(self, color: str, piece_type: str, value: float):
        self.color = color  # 'white' or 'black'
        self.piece_type = piece_type
        self.value = value
        self.has_moved = False
        self.image_path = self._get_image_path()
    
    def _get_image_path(self) -> str:
        """Get the path to the piece's image file"""
        color_name = "White" if self.color == "white" else "Black"
        filename = f"{self.piece_type}_{color_name}.svg.png"
        return os.path.join("svgs", filename)
    
    @abstractmethod
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for this piece from the given position"""
        pass
    
    def is_valid_position(self, pos: Tuple[int, int], board_size: int) -> bool:
        """Check if a position is within the board bounds"""
        row, col = pos
        return 0 <= row < board_size and 0 <= col < board_size
    
    def is_square_empty_or_enemy(self, pos: Tuple[int, int], board) -> bool:
        """Check if a square is empty or contains an enemy piece"""
        piece = board.get_piece(pos)
        return piece is None or piece.color != self.color
    
    def __str__(self):
        return f"{self.color} {self.piece_type}"
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.color})"


class King(AutoChessPiece):
    """King piece - moves one square in any direction"""
    
    def __init__(self, color: str):
        super().__init__(color, "King", 20)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # King moves one square in any direction (8 possible moves)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            new_pos = (row + dr, col + dc)
            if (self.is_valid_position(new_pos, board.size) and 
                self.is_square_empty_or_enemy(new_pos, board)):
                moves.append(new_pos)
        
        return moves


class Queen(AutoChessPiece):
    """Queen piece - moves any number of squares horizontally, vertically, or diagonally"""
    
    def __init__(self, color: str):
        super().__init__(color, "Queen", 10)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Queen moves like rook + bishop (8 directions)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            for distance in range(1, board.size):
                new_pos = (row + dr * distance, col + dc * distance)
                
                if not self.is_valid_position(new_pos, board.size):
                    break
                
                piece_at_pos = board.get_piece(new_pos)
                if piece_at_pos is None:
                    moves.append(new_pos)
                elif piece_at_pos.color != self.color:
                    moves.append(new_pos)  # Can capture enemy piece
                    break
                else:
                    break  # Blocked by own piece
        
        return moves


class Rook(AutoChessPiece):
    """Rook piece - moves any number of squares horizontally or vertically"""
    
    def __init__(self, color: str):
        super().__init__(color, "Rook", 5.25)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Rook moves horizontally and vertically (4 directions)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for distance in range(1, board.size):
                new_pos = (row + dr * distance, col + dc * distance)
                
                if not self.is_valid_position(new_pos, board.size):
                    break
                
                piece_at_pos = board.get_piece(new_pos)
                if piece_at_pos is None:
                    moves.append(new_pos)
                elif piece_at_pos.color != self.color:
                    moves.append(new_pos)  # Can capture enemy piece
                    break
                else:
                    break  # Blocked by own piece
        
        return moves


class Bishop(AutoChessPiece):
    """Bishop piece - moves any number of squares diagonally"""
    
    def __init__(self, color: str):
        super().__init__(color, "Bishop", 3.5)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Bishop moves diagonally (4 directions)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for distance in range(1, board.size):
                new_pos = (row + dr * distance, col + dc * distance)
                
                if not self.is_valid_position(new_pos, board.size):
                    break
                
                piece_at_pos = board.get_piece(new_pos)
                if piece_at_pos is None:
                    moves.append(new_pos)
                elif piece_at_pos.color != self.color:
                    moves.append(new_pos)  # Can capture enemy piece
                    break
                else:
                    break  # Blocked by own piece
        
        return moves


class Knight(AutoChessPiece):
    """Knight piece - moves in an L-shape (2 squares in one direction, 1 in perpendicular)"""
    
    def __init__(self, color: str):
        super().__init__(color, "Knight", 3.5)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Knight moves in L-shape (8 possible moves)
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2),  (1, 2),  (2, -1),  (2, 1)
        ]
        
        for dr, dc in knight_moves:
            new_pos = (row + dr, col + dc)
            if (self.is_valid_position(new_pos, board.size) and 
                self.is_square_empty_or_enemy(new_pos, board)):
                moves.append(new_pos)
        
        return moves


class Pawn(AutoChessPiece):
    """Pawn piece - moves forward one square, captures diagonally"""
    
    def __init__(self, color: str):
        super().__init__(color, "Pawn", 1)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Determine forward direction based on color
        # White moves up the board (decreasing row numbers)
        # Black moves down the board (increasing row numbers)
        forward = -1 if self.color == "white" else 1
        
        # Move forward one square
        new_pos = (row + forward, col)
        if (self.is_valid_position(new_pos, board.size) and 
            board.get_piece(new_pos) is None):
            moves.append(new_pos)
            
            # Move forward two squares if on starting position and haven't moved
            if not self.has_moved:
                two_forward = (row + 2 * forward, col)
                if (self.is_valid_position(two_forward, board.size) and 
                    board.get_piece(two_forward) is None):
                    moves.append(two_forward)
        
        # Capture diagonally
        for dc in [-1, 1]:
            capture_pos = (row + forward, col + dc)
            if self.is_valid_position(capture_pos, board.size):
                piece_at_pos = board.get_piece(capture_pos)
                if piece_at_pos and piece_at_pos.color != self.color:
                    moves.append(capture_pos)
        
        return moves
