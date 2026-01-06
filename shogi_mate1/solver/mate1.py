"""
One-move mate detection for Shogi.

This module handles:
- Detecting if a move is a mate-in-1
- Finding all mate-in-1 moves
- Checking for unique solution
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from shogi_mate1.core.board import Board
from shogi_mate1.core.move import Move
from shogi_mate1.core.movegen import checking_moves, legal_moves, generates_check
from shogi_mate1.core.attack import is_check


@dataclass
class MateSearchStats:
    """Statistics from mate search."""
    total_legal_moves: int = 0
    total_checking_moves: int = 0
    mate_moves: int = 0
    average_responses: float = 0.0


def is_mate_in_1(board: Board, move: Move) -> bool:
    """
    Check if a move is a mate-in-1.
    
    Args:
        board: Board position
        move: Move to check
        
    Returns:
        True if the move is checkmate
    """
    # Apply the move
    temp_board = board.copy()
    captured, promoted = temp_board.apply_move(move)
    
    # Must be check
    opponent_side = temp_board.side_to_move
    if not is_check(temp_board, opponent_side):
        temp_board.undo_move(move, captured, promoted)
        return False
    
    # Check if opponent has any legal moves (if not, it's mate)
    opponent_moves = legal_moves(temp_board, opponent_side)
    is_mate = len(opponent_moves) == 0
    
    temp_board.undo_move(move, captured, promoted)
    return is_mate


def find_mate_moves(board: Board, stats: Optional[MateSearchStats] = None) -> List[Move]:
    """
    Find all mate-in-1 moves for the side to move.
    
    Args:
        board: Board position
        stats: Optional stats object to populate
        
    Returns:
        List of moves that are mate-in-1
    """
    mate_moves = []
    
    # Get all legal moves
    all_moves = legal_moves(board, board.side_to_move)
    
    # Get checking moves
    check_moves = []
    response_counts = []
    
    for move in all_moves:
        if generates_check(board, move):
            check_moves.append(move)
            
            # Count responses for stats
            temp_board = board.copy()
            captured, promoted = temp_board.apply_move(move)
            opponent_side = temp_board.side_to_move
            responses = len(legal_moves(temp_board, opponent_side))
            response_counts.append(responses)
            temp_board.undo_move(move, captured, promoted)
    
    # Check which checking moves are mate
    for i, move in enumerate(check_moves):
        if response_counts[i] == 0:
            mate_moves.append(move)
    
    # Populate stats if requested
    if stats is not None:
        stats.total_legal_moves = len(all_moves)
        stats.total_checking_moves = len(check_moves)
        stats.mate_moves = len(mate_moves)
        if check_moves:
            stats.average_responses = sum(response_counts) / len(check_moves)
        else:
            stats.average_responses = 0.0
    
    return mate_moves


def has_unique_mate(board: Board) -> bool:
    """
    Check if the position has exactly one mate-in-1 move.
    
    Args:
        board: Board position
        
    Returns:
        True if there is exactly one mate move
    """
    mate_moves = find_mate_moves(board)
    return len(mate_moves) == 1


def get_unique_mate(board: Board) -> Optional[Move]:
    """
    Get the unique mate-in-1 move if it exists.
    
    Args:
        board: Board position
        
    Returns:
        The mate move if unique, None otherwise
    """
    mate_moves = find_mate_moves(board)
    if len(mate_moves) == 1:
        return mate_moves[0]
    return None


def verify_mate_position(board: Board) -> Dict[str, any]:
    """
    Verify a position and return detailed information.
    
    Args:
        board: Board position to verify
        
    Returns:
        Dict with verification results
    """
    stats = MateSearchStats()
    mate_moves = find_mate_moves(board, stats)
    
    return {
        'is_mate': len(mate_moves) > 0,
        'is_unique': len(mate_moves) == 1,
        'mate_count': len(mate_moves),
        'mate_moves': mate_moves,
        'stats': stats
    }
