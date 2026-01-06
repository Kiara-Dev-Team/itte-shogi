"""
Move representation for Shogi.

A move can be:
1. A regular move: from_sq -> to_sq (optionally with promotion)
2. A drop move: drop a piece from hand to to_sq
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Move:
    """
    Represents a Shogi move.
    
    Attributes:
        from_sq: Source square index (0-80), or None for drop moves
        to_sq: Destination square index (0-80)
        drop_piece: Piece type to drop (for drop moves), or None
        is_promote: Whether this move promotes the piece
    """
    from_sq: Optional[int]
    to_sq: int
    drop_piece: Optional[int] = None
    is_promote: bool = False
    
    def is_drop(self) -> bool:
        """Check if this is a drop move."""
        return self.drop_piece is not None
    
    def __str__(self) -> str:
        """Convert move to USI format string."""
        if self.is_drop():
            # Drop move format: P*5e (piece type + * + destination)
            from shogi_mate1.core.pieces import PIECE_SFEN, PieceType
            piece_type = abs(self.drop_piece)
            piece_char = PIECE_SFEN.get(piece_type, '?').replace('+', '')
            to_file, to_rank = index_to_square(self.to_sq)
            return f"{piece_char}*{to_file}{to_rank}"
        else:
            # Regular move format: 7g7f (from + to + optional promotion)
            from_file, from_rank = index_to_square(self.from_sq)
            to_file, to_rank = index_to_square(self.to_sq)
            promo_suffix = '+' if self.is_promote else ''
            return f"{from_file}{from_rank}{to_file}{to_rank}{promo_suffix}"
    
    def __repr__(self) -> str:
        return f"Move({str(self)})"


def index_to_square(index: int) -> tuple[str, str]:
    """
    Convert board index to square notation (e.g., 0 -> '9a').
    
    Args:
        index: Board index (0-80)
        
    Returns:
        Tuple of (file_char, rank_char)
    """
    file = 9 - (index % 9)  # Files go from 9 (left) to 1 (right)
    rank = (index // 9) + 1  # Ranks go from 1 (top) to 9 (bottom)
    file_char = str(file)
    rank_char = chr(ord('a') + rank - 1)  # 'a' for rank 1, 'b' for rank 2, etc.
    return file_char, rank_char


def index_to_file_rank(index: int) -> tuple[int, int]:
    """
    Convert board index to (file, rank) tuple.
    
    Args:
        index: Board index (0-80)
        
    Returns:
        Tuple of (file, rank) as integers
    """
    rank = (index // 9) + 1
    file = 9 - (index % 9)
    return file, rank


def square_to_index(file: int, rank: int) -> int:
    """
    Convert file and rank to board index.
    
    Args:
        file: File number (1-9, where 1 is rightmost)
        rank: Rank number (1-9, where 1 is top)
        
    Returns:
        Board index (0-80)
    """
    # index = (rank - 1) * 9 + (9 - file)
    return (rank - 1) * 9 + (9 - file)


def parse_move(move_str: str, board: 'Board') -> Optional[Move]:
    """
    Parse a move from USI format string.
    
    Args:
        move_str: Move string in USI format
        board: Board object to validate the move against
        
    Returns:
        Move object, or None if invalid
    """
    from shogi_mate1.core.pieces import piece_from_sfen
    
    move_str = move_str.strip()
    
    # Check for drop move (e.g., "P*5e")
    if '*' in move_str:
        parts = move_str.split('*')
        if len(parts) != 2:
            return None
        
        piece_char = parts[0]
        dest = parts[1]
        
        if len(dest) < 2:
            return None
        
        try:
            file = int(dest[0])
            rank = ord(dest[1]) - ord('a') + 1
            to_sq = square_to_index(file, rank)
        except (ValueError, IndexError):
            return None
        
        # Determine piece type (Sente or Gote based on board turn)
        piece = piece_from_sfen(piece_char)
        if piece is None:
            return None
        
        # Adjust sign based on side to move
        if board.side_to_move == 1:  # Sente
            drop_piece = abs(piece)
        else:  # Gote
            drop_piece = -abs(piece)
        
        return Move(from_sq=None, to_sq=to_sq, drop_piece=drop_piece)
    
    # Regular move (e.g., "7g7f" or "7g7f+")
    is_promote = move_str.endswith('+')
    if is_promote:
        move_str = move_str[:-1]
    
    if len(move_str) < 4:
        return None
    
    try:
        from_file = int(move_str[0])
        from_rank = ord(move_str[1]) - ord('a') + 1
        to_file = int(move_str[2])
        to_rank = ord(move_str[3]) - ord('a') + 1
        
        from_sq = square_to_index(from_file, from_rank)
        to_sq = square_to_index(to_file, to_rank)
        
        return Move(from_sq=from_sq, to_sq=to_sq, is_promote=is_promote)
    except (ValueError, IndexError):
        return None
