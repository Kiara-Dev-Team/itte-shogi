"""
Piece definitions for Shogi.

Pieces are represented as integers:
- Positive values: Sente (first player, 先手)
- Negative values: Gote (second player, 後手)
- Zero: Empty square

Piece types:
- 1/-1: King (玉/王)
- 2/-2: Rook (飛車)
- 3/-3: Bishop (角行)
- 4/-4: Gold (金将)
- 5/-5: Silver (銀将)
- 6/-6: Knight (桂馬)
- 7/-7: Lance (香車)
- 8/-8: Pawn (歩兵)
- 9/-9: Promoted Rook (龍王)
- 10/-10: Promoted Bishop (龍馬)
- 11/-11: Promoted Silver (成銀)
- 12/-12: Promoted Knight (成桂)
- 13/-13: Promoted Lance (成香)
- 14/-14: Promoted Pawn (と金)
"""

from typing import List, Tuple, Optional
from enum import IntEnum


class PieceType(IntEnum):
    """Piece type enumeration."""
    EMPTY = 0
    KING = 1
    ROOK = 2
    BISHOP = 3
    GOLD = 4
    SILVER = 5
    KNIGHT = 6
    LANCE = 7
    PAWN = 8
    PROMOTED_ROOK = 9
    PROMOTED_BISHOP = 10
    PROMOTED_SILVER = 11
    PROMOTED_KNIGHT = 12
    PROMOTED_LANCE = 13
    PROMOTED_PAWN = 14


# Piece movement vectors (file_delta, rank_delta)
# file: 1-9 from right to left (1 is rightmost)
# rank: 1-9 from top to bottom (1 is top)
# Vectors are from perspective of Sente (positive pieces)
# Gote pieces use negated vectors

# Direction vectors: (df, dr)
# df: positive = left, negative = right
# dr: positive = down, negative = up

KING_MOVES: List[Tuple[int, int]] = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
]

ROOK_DIRECTIONS: List[Tuple[int, int]] = [
    (0, -1),  # up
    (0, 1),   # down
    (-1, 0),  # left
    (1, 0),   # right
]

BISHOP_DIRECTIONS: List[Tuple[int, int]] = [
    (-1, -1),  # up-left
    (1, -1),   # up-right
    (-1, 1),   # down-left
    (1, 1),    # down-right
]

GOLD_MOVES: List[Tuple[int, int]] = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
              (0, 1),
]

SILVER_MOVES: List[Tuple[int, int]] = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 1),           (1, 1),
]

KNIGHT_MOVES: List[Tuple[int, int]] = [
    (-1, -2),  # two up, one left
    (1, -2),   # two up, one right
]

LANCE_DIRECTIONS: List[Tuple[int, int]] = [
    (0, -1),  # up only
]

PAWN_MOVES: List[Tuple[int, int]] = [
    (0, -1),  # up only
]

PROMOTED_ROOK_MOVES: List[Tuple[int, int]] = KING_MOVES  # Rook + King moves (King for diagonals)
PROMOTED_BISHOP_MOVES: List[Tuple[int, int]] = KING_MOVES  # Bishop + King moves (King for orthogonals)


def get_piece_moves(piece: int) -> List[Tuple[int, int]]:
    """
    Get movement vectors for a piece.
    
    Args:
        piece: Piece value (positive for Sente, negative for Gote)
        
    Returns:
        List of (file_delta, rank_delta) tuples
    """
    piece_type = abs(piece)
    is_gote = piece < 0
    
    if piece_type == PieceType.KING:
        moves = KING_MOVES
    elif piece_type == PieceType.GOLD:
        moves = GOLD_MOVES
    elif piece_type == PieceType.SILVER:
        moves = SILVER_MOVES
    elif piece_type == PieceType.KNIGHT:
        moves = KNIGHT_MOVES
    elif piece_type == PieceType.PAWN:
        moves = PAWN_MOVES
    elif piece_type in [PieceType.PROMOTED_SILVER, PieceType.PROMOTED_KNIGHT,
                        PieceType.PROMOTED_LANCE, PieceType.PROMOTED_PAWN]:
        moves = GOLD_MOVES  # All promoted pieces except Rook and Bishop move like Gold
    else:
        moves = []
    
    # Flip moves for Gote
    if is_gote:
        moves = [(-df, -dr) for df, dr in moves]
    
    return moves


def get_piece_directions(piece: int) -> List[Tuple[int, int]]:
    """
    Get sliding directions for a piece (for Rook, Bishop, Lance, and their promoted versions).
    
    Args:
        piece: Piece value
        
    Returns:
        List of (file_delta, rank_delta) direction tuples
    """
    piece_type = abs(piece)
    is_gote = piece < 0
    
    if piece_type == PieceType.ROOK:
        directions = ROOK_DIRECTIONS
    elif piece_type == PieceType.BISHOP:
        directions = BISHOP_DIRECTIONS
    elif piece_type == PieceType.LANCE:
        directions = LANCE_DIRECTIONS
    elif piece_type == PieceType.PROMOTED_ROOK:
        directions = ROOK_DIRECTIONS  # Still slides like Rook
    elif piece_type == PieceType.PROMOTED_BISHOP:
        directions = BISHOP_DIRECTIONS  # Still slides like Bishop
    else:
        directions = []
    
    # Flip directions for Gote
    if is_gote:
        directions = [(-df, -dr) for df, dr in directions]
    
    return directions


def is_sliding_piece(piece: int) -> bool:
    """Check if piece is a sliding piece (Rook, Bishop, Lance, or promoted versions)."""
    piece_type = abs(piece)
    return piece_type in [PieceType.ROOK, PieceType.BISHOP, PieceType.LANCE,
                          PieceType.PROMOTED_ROOK, PieceType.PROMOTED_BISHOP]


def can_promote(piece: int) -> bool:
    """Check if a piece can be promoted."""
    piece_type = abs(piece)
    return piece_type in [PieceType.ROOK, PieceType.BISHOP, PieceType.SILVER,
                          PieceType.KNIGHT, PieceType.LANCE, PieceType.PAWN]


def promote(piece: int) -> int:
    """
    Get the promoted version of a piece.
    
    Args:
        piece: Piece value
        
    Returns:
        Promoted piece value
    """
    if not can_promote(piece):
        return piece
    
    piece_type = abs(piece)
    is_gote = piece < 0
    
    promotion_map = {
        PieceType.ROOK: PieceType.PROMOTED_ROOK,
        PieceType.BISHOP: PieceType.PROMOTED_BISHOP,
        PieceType.SILVER: PieceType.PROMOTED_SILVER,
        PieceType.KNIGHT: PieceType.PROMOTED_KNIGHT,
        PieceType.LANCE: PieceType.PROMOTED_LANCE,
        PieceType.PAWN: PieceType.PROMOTED_PAWN,
    }
    
    promoted_type = promotion_map[piece_type]
    return -promoted_type if is_gote else promoted_type


def unpromote(piece: int) -> int:
    """
    Get the unpromoted version of a piece.
    
    Args:
        piece: Piece value
        
    Returns:
        Unpromoted piece value
    """
    piece_type = abs(piece)
    is_gote = piece < 0
    
    unpromotion_map = {
        PieceType.PROMOTED_ROOK: PieceType.ROOK,
        PieceType.PROMOTED_BISHOP: PieceType.BISHOP,
        PieceType.PROMOTED_SILVER: PieceType.SILVER,
        PieceType.PROMOTED_KNIGHT: PieceType.KNIGHT,
        PieceType.PROMOTED_LANCE: PieceType.LANCE,
        PieceType.PROMOTED_PAWN: PieceType.PAWN,
    }
    
    if piece_type in unpromotion_map:
        unpromoted_type = unpromotion_map[piece_type]
        return -unpromoted_type if is_gote else unpromoted_type
    
    return piece


def is_promoted(piece: int) -> bool:
    """Check if a piece is promoted."""
    piece_type = abs(piece)
    return piece_type in [PieceType.PROMOTED_ROOK, PieceType.PROMOTED_BISHOP,
                          PieceType.PROMOTED_SILVER, PieceType.PROMOTED_KNIGHT,
                          PieceType.PROMOTED_LANCE, PieceType.PROMOTED_PAWN]


# Japanese piece names
PIECE_NAMES_JP = {
    PieceType.KING: '玉',
    PieceType.ROOK: '飛',
    PieceType.BISHOP: '角',
    PieceType.GOLD: '金',
    PieceType.SILVER: '銀',
    PieceType.KNIGHT: '桂',
    PieceType.LANCE: '香',
    PieceType.PAWN: '歩',
    PieceType.PROMOTED_ROOK: '龍',
    PieceType.PROMOTED_BISHOP: '馬',
    PieceType.PROMOTED_SILVER: '成銀',
    PieceType.PROMOTED_KNIGHT: '成桂',
    PieceType.PROMOTED_LANCE: '成香',
    PieceType.PROMOTED_PAWN: 'と',
}

# SFEN piece notation
PIECE_SFEN = {
    PieceType.KING: 'K',
    PieceType.ROOK: 'R',
    PieceType.BISHOP: 'B',
    PieceType.GOLD: 'G',
    PieceType.SILVER: 'S',
    PieceType.KNIGHT: 'N',
    PieceType.LANCE: 'L',
    PieceType.PAWN: 'P',
    PieceType.PROMOTED_ROOK: '+R',
    PieceType.PROMOTED_BISHOP: '+B',
    PieceType.PROMOTED_SILVER: '+S',
    PieceType.PROMOTED_KNIGHT: '+N',
    PieceType.PROMOTED_LANCE: '+L',
    PieceType.PROMOTED_PAWN: '+P',
}


def piece_to_string(piece: int, japanese: bool = True) -> str:
    """
    Convert piece to string representation.
    
    Args:
        piece: Piece value
        japanese: If True, use Japanese notation; otherwise use SFEN
        
    Returns:
        String representation of the piece
    """
    if piece == 0:
        return '・' if japanese else '.'
    
    piece_type = abs(piece)
    is_gote = piece < 0
    
    if japanese:
        name = PIECE_NAMES_JP.get(piece_type, '?')
        return f'v{name}' if is_gote else name
    else:
        # SFEN notation
        sfen = PIECE_SFEN.get(piece_type, '?')
        return sfen.lower() if is_gote else sfen


def piece_from_sfen(sfen_char: str) -> Optional[int]:
    """
    Parse a piece from SFEN notation.
    
    Args:
        sfen_char: SFEN character(s) representing a piece
        
    Returns:
        Piece value, or None if invalid
    """
    if not sfen_char or sfen_char == '.':
        return 0
    
    has_plus = sfen_char.startswith('+')
    if has_plus:
        sfen_char = sfen_char[1:]
    
    is_gote = sfen_char.islower()
    sfen_upper = sfen_char.upper()
    
    # Reverse lookup
    for piece_type, sfen in PIECE_SFEN.items():
        base_sfen = sfen.replace('+', '')
        if base_sfen == sfen_upper:
            # If input had '+', look for the promoted version
            if has_plus and not sfen.startswith('+'):
                # This is a base piece, need promoted version
                piece = promote(piece_type if not is_gote else -piece_type)
            else:
                # Direct match or already promoted piece type
                piece = piece_type if not is_gote else -piece_type
            return piece
    
    return None
