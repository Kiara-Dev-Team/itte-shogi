"""
Attack and check detection for Shogi.

This module handles:
- Calculating which squares a piece attacks
- Checking if a square is attacked by a side
- Detecting check situations
"""

from typing import List, Optional
from shogi_mate1.core.board import Board
from shogi_mate1.core.pieces import (
    PieceType, get_piece_moves, get_piece_directions, is_sliding_piece
)
from shogi_mate1.core.move import square_to_index, index_to_file_rank


def is_valid_square(file: int, rank: int) -> bool:
    """Check if a square is within board bounds."""
    return 1 <= file <= 9 and 1 <= rank <= 9


def is_attacked_by_piece(board: Board, target_sq: int, attacker_sq: int) -> bool:
    """
    Check if a piece at attacker_sq attacks target_sq.
    
    Args:
        board: Board position
        target_sq: Target square index
        attacker_sq: Attacker piece square index
        
    Returns:
        True if the piece attacks the target square
    """
    piece = board.squares[attacker_sq]
    if piece == 0:
        return False
    
    target_file, target_rank = index_to_file_rank(target_sq)
    attacker_file, attacker_rank = index_to_file_rank(attacker_sq)
    
    # Calculate delta
    df = target_file - attacker_file
    dr = target_rank - attacker_rank
    
    # Check if piece can move in this direction
    if is_sliding_piece(piece):
        # Sliding piece (Rook, Bishop, Lance, promoted versions)
        directions = get_piece_directions(piece)
        
        for dir_df, dir_dr in directions:
            if dir_df == 0 and dir_dr == 0:
                continue
            
            # Check if target is in this direction
            if df * dir_dr == dr * dir_df and (df * dir_df >= 0 and dr * dir_dr >= 0):
                # Check if same direction
                if (df == 0 and dir_df == 0) or (dr == 0 and dir_dr == 0) or \
                   (df != 0 and dir_df != 0 and df * dir_df > 0 and dr * dir_dr > 0):
                    # Check if path is clear
                    steps = max(abs(df), abs(dr))
                    for step in range(1, steps):
                        check_file = attacker_file + (dir_df * step)
                        check_rank = attacker_rank + (dir_dr * step)
                        check_sq = square_to_index(check_file, check_rank)
                        if board.squares[check_sq] != 0:
                            return False
                    return True
        
        # Also check non-sliding moves for promoted pieces
        piece_type = abs(piece)
        if piece_type in [PieceType.PROMOTED_ROOK, PieceType.PROMOTED_BISHOP]:
            moves = get_piece_moves(piece)
            for move_df, move_dr in moves:
                if df == move_df and dr == move_dr:
                    return True
    else:
        # Non-sliding piece
        moves = get_piece_moves(piece)
        for move_df, move_dr in moves:
            if df == move_df and dr == move_dr:
                return True
    
    return False


def is_attacked(board: Board, square: int, attacker_side: int) -> bool:
    """
    Check if a square is attacked by any piece of the given side.
    
    Args:
        board: Board position
        square: Target square index
        attacker_side: Side of the attacker (1 for Sente, -1 for Gote)
        
    Returns:
        True if the square is attacked by any piece of attacker_side
    """
    for i, piece in enumerate(board.squares):
        if piece == 0:
            continue
        
        # Check if piece belongs to attacker side
        if (piece > 0 and attacker_side > 0) or (piece < 0 and attacker_side < 0):
            if is_attacked_by_piece(board, square, i):
                return True
    
    return False


def is_check(board: Board, side: int) -> bool:
    """
    Check if the king of the given side is in check.
    
    Args:
        board: Board position
        side: Side to check (1 for Sente, -1 for Gote)
        
    Returns:
        True if the king is in check
    """
    king_sq = board.find_king(side)
    if king_sq is None:
        return False
    
    return is_attacked(board, king_sq, -side)


def get_attackers(board: Board, square: int, attacker_side: int) -> List[int]:
    """
    Get all pieces of attacker_side that attack the given square.
    
    Args:
        board: Board position
        square: Target square index
        attacker_side: Side of the attackers
        
    Returns:
        List of square indices of attacking pieces
    """
    attackers = []
    for i, piece in enumerate(board.squares):
        if piece == 0:
            continue
        
        if (piece > 0 and attacker_side > 0) or (piece < 0 and attacker_side < 0):
            if is_attacked_by_piece(board, square, i):
                attackers.append(i)
    
    return attackers


def attacks_square(board: Board, from_sq: int, to_sq: int) -> bool:
    """
    Check if a piece at from_sq attacks to_sq.
    
    Args:
        board: Board position
        from_sq: Source square index
        to_sq: Target square index
        
    Returns:
        True if the piece attacks the target
    """
    return is_attacked_by_piece(board, to_sq, from_sq)
