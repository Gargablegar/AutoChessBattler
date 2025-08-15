"""
Chess Board - Manages the game board and piece positions
"""

from typing import Optional, Tuple, List
from autochess_pieces import AutoChessPiece

class ChessBoard:
    """Represents the chess board and manages piece positions"""
    
    def __init__(self, size: int):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
    
    def get_piece(self, position: Tuple[int, int]) -> Optional[AutoChessPiece]:
        """Get the piece at the given position"""
        row, col = position
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.board[row][col]
        return None
    
    def place_piece(self, piece: AutoChessPiece, position: Tuple[int, int]) -> bool:
        """Place a piece at the given position"""
        row, col = position
        if 0 <= row < self.size and 0 <= col < self.size:
            self.board[row][col] = piece
            return True
        return False
    
    def remove_piece(self, position: Tuple[int, int]) -> Optional[AutoChessPiece]:
        """Remove and return the piece at the given position"""
        row, col = position
        if 0 <= row < self.size and 0 <= col < self.size:
            piece = self.board[row][col]
            self.board[row][col] = None
            return piece
        return None
    
    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Move a piece from one position to another"""
        piece = self.remove_piece(from_pos)
        if piece:
            # Mark piece as having moved (important for pawns and castling)
            piece.has_moved = True
            return self.place_piece(piece, to_pos)
        return False
    
    def find_piece_position(self, target_piece: AutoChessPiece) -> Optional[Tuple[int, int]]:
        """Find the position of a specific piece on the board"""
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] is target_piece:
                    return (row, col)
        return None
    
    def is_empty(self, position: Tuple[int, int]) -> bool:
        """Check if a position is empty"""
        return self.get_piece(position) is None
    
    def get_all_pieces(self) -> List[Tuple[AutoChessPiece, Tuple[int, int]]]:
        """Get all pieces on the board with their positions"""
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board[row][col]
                if piece:
                    pieces.append((piece, (row, col)))
        return pieces
    
    def clear(self):
        """Clear the entire board"""
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
    
    def __str__(self):
        """String representation of the board for debugging"""
        lines = []
        for row in range(self.size):
            line = []
            for col in range(self.size):
                piece = self.board[row][col]
                if piece:
                    symbol = piece.piece_type[0].upper() if piece.color == 'white' else piece.piece_type[0].lower()
                    line.append(symbol)
                else:
                    line.append('.')
            lines.append(' '.join(line))
        return '\n'.join(lines)
