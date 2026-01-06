"""
Move generation for Shogi.

This module handles:
- Pseudo-legal move generation
- Legal move filtering (removing moves that leave king in check)
- Checking move generation
"""

from typing import List
from shogi_mate1.core.board import Board
from shogi_mate1.core.move import Move, index_to_file_rank, square_to_index
from shogi_mate1.core.pieces import (
    PieceType, get_piece_moves, get_piece_directions, is_sliding_piece, can_promote
)
from shogi_mate1.core.rules import (
    is_legal_drop, can_move_promote, requires_promotion
)
from shogi_mate1.core.attack import is_check


def generate_piece_moves(board: Board, from_sq: int) -> List[Move]:
    """
    Generate all pseudo-legal moves for a piece at from_sq.
    
    Args:
        board: Board position
        from_sq: Source square index
        
    Returns:
        List of pseudo-legal moves
    """
    piece = board.squares[from_sq]
    if piece == 0:
        return []
    
    moves = []
    from_file, from_rank = index_to_file_rank(from_sq)
    
    if is_sliding_piece(piece):
        # Sliding piece
        directions = get_piece_directions(piece)
        for df, dr in directions:
            for step in range(1, 9):
                to_file = from_file + df * step
                to_rank = from_rank + dr * step
                
                if not (1 <= to_file <= 9 and 1 <= to_rank <= 9):
                    break
                
                to_sq = square_to_index(to_file, to_rank)
                target = board.squares[to_sq]
                
                # Can't capture own piece
                if target != 0 and ((piece > 0 and target > 0) or (piece < 0 and target < 0)):
                    break
                
                # Add move
                move = Move(from_sq=from_sq, to_sq=to_sq)
                moves.append(move)
                
                # Check for promotion
                if can_move_promote(board, move):
                    promo_move = Move(from_sq=from_sq, to_sq=to_sq, is_promote=True)
                    moves.append(promo_move)
                
                # Stop if captured
                if target != 0:
                    break
        
        # Add non-sliding moves for promoted Rook/Bishop
        piece_type = abs(piece)
        if piece_type in [PieceType.PROMOTED_ROOK, PieceType.PROMOTED_BISHOP]:
            non_sliding_moves = get_piece_moves(piece)
            for df, dr in non_sliding_moves:
                to_file = from_file + df
                to_rank = from_rank + dr
                
                if not (1 <= to_file <= 9 and 1 <= to_rank <= 9):
                    continue
                
                to_sq = square_to_index(to_file, to_rank)
                target = board.squares[to_sq]
                
                if target != 0 and ((piece > 0 and target > 0) or (piece < 0 and target < 0)):
                    continue
                
                move = Move(from_sq=from_sq, to_sq=to_sq)
                # Promoted pieces can't promote again
                moves.append(move)
    else:
        # Non-sliding piece
        piece_moves = get_piece_moves(piece)
        for df, dr in piece_moves:
            to_file = from_file + df
            to_rank = from_rank + dr
            
            if not (1 <= to_file <= 9 and 1 <= to_rank <= 9):
                continue
            
            to_sq = square_to_index(to_file, to_rank)
            target = board.squares[to_sq]
            
            # Can't capture own piece
            if target != 0 and ((piece > 0 and target > 0) or (piece < 0 and target < 0)):
                continue
            
            # Add move
            move = Move(from_sq=from_sq, to_sq=to_sq)
            
            # Check if must promote
            if requires_promotion(board, move):
                moves.append(Move(from_sq=from_sq, to_sq=to_sq, is_promote=True))
            else:
                moves.append(move)
                
                # Check if can optionally promote
                if can_move_promote(board, move) and can_promote(piece):
                    promo_move = Move(from_sq=from_sq, to_sq=to_sq, is_promote=True)
                    moves.append(promo_move)
    
    return moves


def generate_drops(board: Board, side: int) -> List[Move]:
    """
    Generate all pseudo-legal drop moves for a side.
    
    Args:
        board: Board position
        side: Side to generate drops for (1 for Sente, -1 for Gote)
        
    Returns:
        List of drop moves
    """
    moves = []
    hand = board.hand_sente if side > 0 else board.hand_gote
    
    if not hand:
        return moves
    
    for piece_type, count in hand.items():
        if count <= 0:
            continue
        
        drop_piece = piece_type if side > 0 else -piece_type
        
        for to_sq in range(81):
            if board.squares[to_sq] != 0:
                continue
            
            move = Move(from_sq=None, to_sq=to_sq, drop_piece=drop_piece)
            
            # Check basic drop legality
            if is_legal_drop(board, move):
                moves.append(move)
    
    return moves


def pseudo_legal_moves(board: Board, side: int) -> List[Move]:
    """
    Generate all pseudo-legal moves for a side.
    
    Args:
        board: Board position
        side: Side to generate moves for
        
    Returns:
        List of pseudo-legal moves
    """
    moves = []
    
    # Generate piece moves
    for from_sq, piece in enumerate(board.squares):
        if piece == 0:
            continue
        
        # Check if piece belongs to side
        if (piece > 0 and side > 0) or (piece < 0 and side < 0):
            moves.extend(generate_piece_moves(board, from_sq))
    
    # Generate drops
    moves.extend(generate_drops(board, side))
    
    return moves


def is_legal_move(board: Board, move: Move) -> bool:
    """
    Check if a move is legal (doesn't leave own king in check).
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if the move is legal
    """
    # Apply move
    temp_board = board.copy()
    captured, promoted = temp_board.apply_move(move)
    
    # Check if own king is in check (after the move, side_to_move has switched)
    our_side = -temp_board.side_to_move
    in_check = is_check(temp_board, our_side)
    
    # Undo move
    temp_board.undo_move(move, captured, promoted)
    
    return not in_check


def legal_moves(board: Board, side: int) -> List[Move]:
    """
    Generate all legal moves for a side.
    
    Args:
        board: Board position
        side: Side to generate moves for
        
    Returns:
        List of legal moves
    """
    pseudo_moves = pseudo_legal_moves(board, side)
    legal = []
    
    for move in pseudo_moves:
        if is_legal_move(board, move):
            legal.append(move)
    
    return legal


def checking_moves(board: Board) -> List[Move]:
    """
    Generate all legal moves that give check.
    
    Args:
        board: Board position (uses board.side_to_move)
        
    Returns:
        List of checking moves
    """
    moves = legal_moves(board, board.side_to_move)
    checking = []
    
    for move in moves:
        # Apply move
        temp_board = board.copy()
        captured, promoted = temp_board.apply_move(move)
        
        # Check if opponent king is in check
        opponent_side = temp_board.side_to_move
        if is_check(temp_board, opponent_side):
            checking.append(move)
        
        # Undo move
        temp_board.undo_move(move, captured, promoted)
    
    return checking


def generates_check(board: Board, move: Move) -> bool:
    """
    Check if a move generates check.
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if the move gives check
    """
    temp_board = board.copy()
    captured, promoted = temp_board.apply_move(move)
    
    opponent_side = temp_board.side_to_move
    in_check = is_check(temp_board, opponent_side)
    
    temp_board.undo_move(move, captured, promoted)
    
    return in_check
