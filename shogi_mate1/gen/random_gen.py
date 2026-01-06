"""
Random puzzle generation.

This module generates random Shogi positions and filters for mate-in-1.
"""

import random
from typing import List, Optional
from shogi_mate1.core.board import Board
from shogi_mate1.core.pieces import PieceType
from shogi_mate1.core.move import square_to_index
from shogi_mate1.gen.quality import is_quality_position
from shogi_mate1.solver.mate1 import has_unique_mate


def create_random_position(max_pieces: int = 10, seed: Optional[int] = None) -> Board:
    """
    Create a random board position.
    
    Args:
        max_pieces: Maximum number of pieces on the board
        seed: Random seed for reproducibility
        
    Returns:
        Random board position
    """
    if seed is not None:
        random.seed(seed)
    
    board = Board()
    
    # Always place both kings
    # Sente king in bottom area
    sente_king_file = random.randint(1, 9)
    sente_king_rank = random.randint(7, 9)
    board.set_piece(sente_king_file, sente_king_rank, PieceType.KING)
    
    # Gote king in top area
    gote_king_file = random.randint(1, 9)
    gote_king_rank = random.randint(1, 3)
    board.set_piece(gote_king_file, gote_king_rank, -PieceType.KING)
    
    # Add random pieces
    piece_types = [
        PieceType.ROOK, PieceType.BISHOP, PieceType.GOLD,
        PieceType.SILVER, PieceType.KNIGHT, PieceType.LANCE, PieceType.PAWN
    ]
    
    num_pieces = random.randint(0, max_pieces - 2)  # -2 for kings
    for _ in range(num_pieces):
        # Choose random piece and position
        piece_type = random.choice(piece_types)
        is_sente = random.choice([True, False])
        piece = piece_type if is_sente else -piece_type
        
        # Find empty square
        attempts = 0
        while attempts < 100:
            file = random.randint(1, 9)
            rank = random.randint(1, 9)
            if board.get_piece(file, rank) == 0:
                board.set_piece(file, rank, piece)
                break
            attempts += 1
    
    # Add some pieces to hand
    if random.random() < 0.3:
        for _ in range(random.randint(0, 3)):
            piece_type = random.choice([PieceType.PAWN, PieceType.SILVER, PieceType.GOLD])
            if random.choice([True, False]):
                board.hand_sente[piece_type] = board.hand_sente.get(piece_type, 0) + 1
            else:
                board.hand_gote[piece_type] = board.hand_gote.get(piece_type, 0) + 1
    
    # Randomly choose side to move
    board.side_to_move = random.choice([1, -1])
    
    return board


def generate_random(n_problems: int = 1, 
                   max_pieces: int = 10,
                   require_unique: bool = True,
                   seed: Optional[int] = None,
                   max_attempts: int = 10000) -> List[Board]:
    """
    Generate random mate-in-1 puzzles.
    
    Args:
        n_problems: Number of problems to generate
        max_pieces: Maximum pieces per position
        require_unique: Whether to require unique solutions
        seed: Random seed for reproducibility
        max_attempts: Maximum attempts before giving up
        
    Returns:
        List of valid puzzle positions
    """
    if seed is not None:
        random.seed(seed)
    
    puzzles = []
    attempts = 0
    
    while len(puzzles) < n_problems and attempts < max_attempts:
        # Generate random position
        board = create_random_position(max_pieces=max_pieces)
        
        # Check if it's a quality mate-in-1
        if is_quality_position(board, require_unique=require_unique, 
                              min_pieces=3, max_pieces=max_pieces):
            puzzles.append(board)
            print(f"Found puzzle {len(puzzles)}/{n_problems} (attempts: {attempts + 1})")
        
        attempts += 1
    
    if len(puzzles) < n_problems:
        print(f"Warning: Only found {len(puzzles)}/{n_problems} puzzles after {attempts} attempts")
    
    return puzzles
