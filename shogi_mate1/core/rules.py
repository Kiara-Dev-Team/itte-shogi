"""
Shogi rules validation.

This module handles:
- Double pawn (二歩) check
- Drop pawn mate (打ち歩詰め) check
- Promotion rules
- Piece placement restrictions (行き所なし)
"""

from typing import Optional
from shogi_mate1.core.board import Board
from shogi_mate1.core.move import Move, index_to_file_rank
from shogi_mate1.core.pieces import PieceType, can_promote


def is_promotion_zone(rank: int, side: int) -> bool:
    """
    Check if a rank is in the promotion zone for a side.
    
    Args:
        rank: Rank number (1-9)
        side: Side (1 for Sente, -1 for Gote)
        
    Returns:
        True if in promotion zone
    """
    if side > 0:
        return rank <= 3  # Sente's promotion zone is ranks 1-3
    else:
        return rank >= 7  # Gote's promotion zone is ranks 7-9


def must_promote(piece: int, to_rank: int) -> bool:
    """
    Check if a piece must promote (行き所なし - no legal moves from destination).
    
    Args:
        piece: Piece value
        to_rank: Destination rank
        
    Returns:
        True if promotion is mandatory
    """
    piece_type = abs(piece)
    is_gote = piece < 0
    
    # Pawns and Lances must promote if they reach the last rank
    if piece_type == PieceType.PAWN or piece_type == PieceType.LANCE:
        if (is_gote and to_rank == 9) or (not is_gote and to_rank == 1):
            return True
    
    # Knights must promote if they reach the last two ranks
    if piece_type == PieceType.KNIGHT:
        if (is_gote and to_rank >= 8) or (not is_gote and to_rank <= 2):
            return True
    
    return False


def can_move_promote(board: Board, move: Move) -> bool:
    """
    Check if a move can include promotion.
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if promotion is allowed
    """
    if move.is_drop():
        return False
    
    piece = board.squares[move.from_sq]
    if not can_promote(piece):
        return False
    
    from_file, from_rank = index_to_file_rank(move.from_sq)
    to_file, to_rank = index_to_file_rank(move.to_sq)
    
    side = 1 if piece > 0 else -1
    
    # Can promote if either from or to square is in promotion zone
    return is_promotion_zone(from_rank, side) or is_promotion_zone(to_rank, side)


def has_double_pawn(board: Board, file: int, side: int) -> bool:
    """
    Check if there is already an unpromoted pawn on the file for the given side.
    
    Args:
        board: Board position
        file: File number (1-9)
        side: Side to check (1 for Sente, -1 for Gote)
        
    Returns:
        True if there's already a pawn on this file
    """
    pawn = PieceType.PAWN if side > 0 else -PieceType.PAWN
    
    for rank in range(1, 10):
        piece = board.get_piece(file, rank)
        if piece == pawn:
            return True
    
    return False


def is_drop_pawn_mate(board: Board, move: Move) -> bool:
    """
    Check if a pawn drop is an illegal drop pawn mate (打ち歩詰め).
    
    This is a simplified check: a pawn drop that gives checkmate is illegal
    if the king has no escape and the pawn cannot be captured.
    
    Args:
        board: Board position
        move: Drop move to check
        
    Returns:
        True if this is an illegal drop pawn mate
    """
    if not move.is_drop():
        return False
    
    piece_type = abs(move.drop_piece)
    if piece_type != PieceType.PAWN:
        return False
    
    # Apply move temporarily
    temp_board = board.copy()
    captured, promoted = temp_board.apply_move(move)
    
    # Check if opponent king is in check
    from shogi_mate1.core.attack import is_check
    opponent_side = temp_board.side_to_move  # After move, it's opponent's turn
    
    if not is_check(temp_board, opponent_side):
        # Not even check, so not drop pawn mate
        temp_board.undo_move(move, captured, promoted)
        return False
    
    # Check if it's mate (opponent has no legal moves)
    from shogi_mate1.core.movegen import legal_moves
    opponent_moves = legal_moves(temp_board, opponent_side)
    
    if len(opponent_moves) == 0:
        # It's checkmate by pawn drop - this is illegal
        temp_board.undo_move(move, captured, promoted)
        return True
    
    temp_board.undo_move(move, captured, promoted)
    return False


def is_legal_drop(board: Board, move: Move) -> bool:
    """
    Check if a drop move is legal according to Shogi rules.
    
    Args:
        board: Board position
        move: Drop move to check
        
    Returns:
        True if the drop is legal
    """
    if not move.is_drop():
        return True
    
    piece_type = abs(move.drop_piece)
    to_file, to_rank = index_to_file_rank(move.to_sq)
    side = 1 if move.drop_piece > 0 else -1
    
    # Check if piece can be legally placed on this square
    if must_promote(move.drop_piece, to_rank):
        # Can't drop a piece where it would have no legal moves
        return False
    
    # Check for double pawn
    if piece_type == PieceType.PAWN:
        if has_double_pawn(board, to_file, side):
            return False
        
        # Check for drop pawn mate
        if is_drop_pawn_mate(board, move):
            return False
    
    return True


def is_legal_move_promotion(board: Board, move: Move) -> bool:
    """
    Check if a move's promotion is legal.
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if promotion is legal (or if no promotion)
    """
    if move.is_drop() or not move.is_promote:
        return True
    
    # Check if promotion is allowed
    if not can_move_promote(board, move):
        return False
    
    return True


def requires_promotion(board: Board, move: Move) -> bool:
    """
    Check if a move requires promotion (行き所なし).
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if promotion is mandatory
    """
    if move.is_drop():
        return False
    
    piece = board.squares[move.from_sq]
    to_file, to_rank = index_to_file_rank(move.to_sq)
    
    return must_promote(piece, to_rank)
