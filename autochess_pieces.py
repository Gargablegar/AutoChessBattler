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
        # Behavior system - determines how piece acts in next turn
        self.behavior = "default"  # "aggressive", "defensive", "passive", "default"
        # Force move target - overrides behavior when set
        self.force_move_target = None  # (row, col) tuple or None
    
    def _get_image_path(self) -> str:
        """Get the path to the piece's image file"""
        color_name = "White" if self.color == "white" else "Black"
        filename = f"{self.piece_type}_{color_name}.svg.png"
        return os.path.join("svgs", filename)
    
    @abstractmethod
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for this piece from the given position"""
        pass
    
    def _get_base_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Helper method to check behavior before returning moves"""
        # If piece has passive behavior, it doesn't move (unless forced)
        if self.behavior == "passive" and not self.has_force_move_target():
            return []
        
        # Get the piece's normal valid moves
        normal_moves = self._get_piece_moves(position, board)
        
        # If piece has a force move target, prioritize moves toward that target
        if self.has_force_move_target():
            return self._get_force_move_toward_target(position, board, normal_moves)
        
        # If piece has aggressive behavior, prioritize attacks and moves toward enemy kings
        if self.behavior == "aggressive":
            return self._get_aggressive_moves(position, board, normal_moves)
        
        # If piece has defensive behavior, protect friendly kings
        if self.behavior == "defensive":
            return self._get_defensive_moves(position, board, normal_moves)
        
        # Otherwise, return normal moves
        return normal_moves
    
    def _get_aggressive_moves(self, position: Tuple[int, int], board, normal_moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get aggressive moves - prioritize captures of highest value pieces, then moves toward enemy kings or force target"""
        if not normal_moves:
            return []
        
        # First, check for capture moves and their values
        capture_moves = []
        for move_pos in normal_moves:
            target_piece = board.get_piece(move_pos)
            if target_piece and target_piece.color != self.color:
                capture_moves.append((move_pos, target_piece.value))
        
        # If we can capture, prioritize the highest value capture
        if capture_moves:
            # Sort by piece value in descending order (highest value first)
            capture_moves.sort(key=lambda x: x[1], reverse=True)
            highest_value = capture_moves[0][1]
            
            # Return all moves that capture pieces of the highest value
            # (in case there are multiple pieces of equal highest value)
            best_captures = [move_pos for move_pos, value in capture_moves if value == highest_value]
            return best_captures
        
        # No captures available, choose target based on force move or enemy kings
        if self.has_force_move_target():
            # Move toward forced target
            moves_toward_target = self._get_moves_toward_targets(position, normal_moves, [self.force_move_target])
            return moves_toward_target if moves_toward_target else normal_moves
        else:
            # Move toward enemy kings
            enemy_kings = self._find_enemy_kings(board)
            if not enemy_kings:
                # No enemy kings found, return all normal moves
                return normal_moves
            
            # Find moves that get us closer to the nearest enemy king
            moves_toward_enemies = self._get_moves_toward_targets(position, normal_moves, enemy_kings)
            return moves_toward_enemies if moves_toward_enemies else normal_moves
    
    def _get_force_move_toward_target(self, position: Tuple[int, int], board, normal_moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get moves toward the forced target, considering piece behavior for captures"""
        if not normal_moves or not self.force_move_target:
            return normal_moves
        
        # Check for capture moves first (behavior-dependent)
        capture_moves = []
        for move_pos in normal_moves:
            target_piece = board.get_piece(move_pos)
            if target_piece and target_piece.color != self.color:
                capture_moves.append((move_pos, target_piece.value))
        
        # Handle captures based on behavior
        if capture_moves:
            if self.behavior == "aggressive":
                # Aggressive: take highest value piece
                capture_moves.sort(key=lambda x: x[1], reverse=True)
                highest_value = capture_moves[0][1]
                best_captures = [move_pos for move_pos, value in capture_moves if value == highest_value]
                return best_captures
            elif self.behavior == "defensive":
                # Defensive: take closest piece to force move target
                target_row, target_col = self.force_move_target
                closest_capture = None
                min_distance = float('inf')
                
                for move_pos, value in capture_moves:
                    move_row, move_col = move_pos
                    distance = abs(move_row - target_row) + abs(move_col - target_col)
                    if distance < min_distance:
                        min_distance = distance
                        closest_capture = move_pos
                
                return [closest_capture] if closest_capture else []
            else:
                # Default/passive: take any available capture
                return [move_pos for move_pos, value in capture_moves]
        
        # No captures available, move toward the forced target
        moves_toward_target = self._get_moves_toward_targets(position, normal_moves, [self.force_move_target])
        return moves_toward_target if moves_toward_target else normal_moves
    
    def _get_defensive_moves(self, position: Tuple[int, int], board, normal_moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get defensive moves - prioritize capturing attacking pieces and protecting friendly pieces,
        or move toward force target if set"""
        if not normal_moves:
            return []
        
        # Check for force move target first
        if self.has_force_move_target():
            # For defensive pieces with force targets, prioritize captures closest to the target
            capture_moves = []
            for move_pos in normal_moves:
                target_piece = board.get_piece(move_pos)
                if target_piece and target_piece.color != self.color:
                    distance_to_target = abs(move_pos[0] - self.force_move_target[0]) + abs(move_pos[1] - self.force_move_target[1])
                    capture_moves.append((move_pos, distance_to_target))
            
            if capture_moves:
                # Sort by distance to target (closest first)
                capture_moves.sort(key=lambda x: x[1])
                closest_distance = capture_moves[0][1]
                best_captures = [move_pos for move_pos, distance in capture_moves if distance == closest_distance]
                return best_captures
            
            # No captures available, move toward forced target
            moves_toward_target = self._get_moves_toward_targets(position, normal_moves, [self.force_move_target])
            return moves_toward_target if moves_toward_target else normal_moves
        
        # Standard defensive behavior - look for threats
        capture_moves = []
        safe_moves = []
        
        for move_pos in normal_moves:
            target_piece = board.get_piece(move_pos)
            if target_piece and target_piece.color != self.color:
                # This is a capture move
                capture_moves.append(move_pos)
            else:
                # Check if this move puts us in a safer position
                safe_moves.append(move_pos)
        
        # Prioritize captures (eliminating threats)
        if capture_moves:
            return capture_moves
        
        # If no captures, try to find moves that protect friendly pieces or move toward our king
        friendly_king = self._find_friendly_king(board)
        if friendly_king:
            moves_toward_king = self._get_moves_toward_targets(position, normal_moves, [friendly_king])
            return moves_toward_king if moves_toward_king else safe_moves
        
        return safe_moves if safe_moves else normal_moves
    
    def _find_friendly_kings(self, board) -> List[Tuple[int, int]]:
        """Find all friendly king positions on the board"""
        friendly_kings = []
        for row in range(board.size):
            for col in range(board.size):
                piece = board.get_piece((row, col))
                if (piece and piece.color == self.color and 
                    piece.__class__.__name__ == "King"):
                    friendly_kings.append((row, col))
        return friendly_kings
    
    def _find_enemy_kings(self, board) -> List[Tuple[int, int]]:
        """Find all enemy king positions on the board"""
        enemy_kings = []
        for row in range(board.size):
            for col in range(board.size):
                piece = board.get_piece((row, col))
                if (piece and piece.color != self.color and 
                    piece.__class__.__name__ == "King"):
                    enemy_kings.append((row, col))
        return enemy_kings
    
    def _get_moves_toward_targets(self, current_pos: Tuple[int, int], 
                                  possible_moves: List[Tuple[int, int]], 
                                  targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get moves that bring us closer to any of the target positions"""
        if not targets or not possible_moves:
            return possible_moves
        
        current_row, current_col = current_pos
        
        # Calculate current distance to nearest target
        min_current_distance = float('inf')
        for target_row, target_col in targets:
            distance = abs(current_row - target_row) + abs(current_col - target_col)
            min_current_distance = min(min_current_distance, distance)
        
        # Find moves that reduce distance to any target
        better_moves = []
        for move_row, move_col in possible_moves:
            for target_row, target_col in targets:
                new_distance = abs(move_row - target_row) + abs(move_col - target_col)
                if new_distance < min_current_distance:
                    better_moves.append((move_row, move_col))
                    break  # This move is good, no need to check other targets
        
        return better_moves if better_moves else possible_moves
    
    @abstractmethod
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get piece-specific moves (implemented by each piece type)"""
        pass
    
    def is_valid_position(self, pos: Tuple[int, int], board_size: int) -> bool:
        """Check if a position is within the board bounds"""
        row, col = pos
        return 0 <= row < board_size and 0 <= col < board_size
    
    def is_square_empty_or_enemy(self, pos: Tuple[int, int], board) -> bool:
        """Check if a square is empty or contains an enemy piece"""
        piece = board.get_piece(pos)
        return piece is None or piece.color != self.color
    
    def set_behavior(self, behavior: str):
        """Set the behavior for this piece for the next turn"""
        valid_behaviors = ["aggressive", "defensive", "passive", "default"]
        if behavior in valid_behaviors:
            self.behavior = behavior
    
    def get_behavior(self) -> str:
        """Get the current behavior of this piece"""
        return self.behavior
    
    def reset_behavior(self):
        """Reset behavior to default after turn completion"""
        self.behavior = "default"
    
    def set_force_move_target(self, target_pos: Tuple[int, int]):
        """Set a target position for forced movement"""
        self.force_move_target = target_pos
    
    def clear_force_move_target(self):
        """Clear the forced movement target"""
        self.force_move_target = None
    
    def has_force_move_target(self) -> bool:
        """Check if this piece has a forced movement target"""
        return self.force_move_target is not None
    
    def __str__(self):
        return f"{self.color} {self.piece_type}"
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.color})"


class King(AutoChessPiece):
    """King piece - moves one square in any direction"""
    
    def __init__(self, color: str):
        super().__init__(color, "King", 20)
    
    def get_valid_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get King-specific moves"""
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
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get Queen-specific moves"""
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
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get Rook-specific moves"""
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
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get Bishop-specific moves"""
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
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get Knight-specific moves"""
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
        """Get all valid moves for this piece, considering behavior"""
        return self._get_base_valid_moves(position, board)
    
    def _get_piece_moves(self, position: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get Pawn-specific moves"""
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
