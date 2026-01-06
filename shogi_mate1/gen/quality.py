"""
Quality metrics and filtering for puzzle generation.

This module provides:
- Difficulty calculation
- Quality filters
- Position evaluation
"""

from typing import Dict, List
from dataclasses import dataclass
from shogi_mate1.core.board import Board
from shogi_mate1.core.movegen import legal_moves, checking_moves
from shogi_mate1.solver.mate1 import find_mate_moves, MateSearchStats


@dataclass
class DifficultyMetrics:
    """Difficulty metrics for a puzzle."""
    total_pieces: int
    legal_moves: int
    checking_moves: int
    mate_moves: int
    average_responses: float
    difficulty_score: float


def count_pieces(board: Board) -> int:
    """Count total pieces on the board."""
    return sum(1 for sq in board.squares if sq != 0)


def calculate_difficulty(board: Board) -> DifficultyMetrics:
    """
    Calculate difficulty metrics for a position.
    
    Args:
        board: Board position
        
    Returns:
        DifficultyMetrics object
    """
    # Count pieces
    total_pieces = count_pieces(board)
    
    # Get move statistics
    stats = MateSearchStats()
    mate_moves = find_mate_moves(board, stats)
    
    # Calculate difficulty score
    # Higher legal moves = harder to find the mate
    # Lower checking moves = harder (less obvious)
    # More responses = harder (more variations to calculate)
    difficulty = 0.0
    if stats.total_legal_moves > 0:
        difficulty += stats.total_legal_moves * 0.5
    if stats.total_checking_moves > 0:
        difficulty += (stats.total_legal_moves - stats.total_checking_moves) * 0.3
    difficulty += stats.average_responses * 1.0
    
    return DifficultyMetrics(
        total_pieces=total_pieces,
        legal_moves=stats.total_legal_moves,
        checking_moves=stats.total_checking_moves,
        mate_moves=len(mate_moves),
        average_responses=stats.average_responses,
        difficulty_score=difficulty
    )


def is_quality_position(board: Board, 
                       require_unique: bool = True,
                       min_pieces: int = 3,
                       max_pieces: int = 20) -> bool:
    """
    Check if a position meets quality criteria.
    
    Args:
        board: Board position
        require_unique: Whether to require unique solution
        min_pieces: Minimum number of pieces
        max_pieces: Maximum number of pieces
        
    Returns:
        True if position meets quality criteria
    """
    # Check piece count
    piece_count = count_pieces(board)
    if piece_count < min_pieces or piece_count > max_pieces:
        return False
    
    # Find mate moves
    mate_moves = find_mate_moves(board)
    
    # Check for mate existence
    if len(mate_moves) == 0:
        return False
    
    # Check for unique solution if required
    if require_unique and len(mate_moves) != 1:
        return False
    
    return True


def filter_positions(positions: List[Board], **kwargs) -> List[Board]:
    """
    Filter positions by quality criteria.
    
    Args:
        positions: List of board positions
        **kwargs: Arguments to pass to is_quality_position
        
    Returns:
        Filtered list of positions
    """
    return [pos for pos in positions if is_quality_position(pos, **kwargs)]
