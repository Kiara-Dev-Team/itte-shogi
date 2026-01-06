"""Tests for pieces module."""

import pytest
from shogi_mate1.core.pieces import (
    PieceType, promote, unpromote, can_promote, is_promoted,
    piece_to_string, piece_from_sfen, get_piece_moves, get_piece_directions,
    is_sliding_piece
)


def test_promote():
    """Test piece promotion."""
    assert promote(PieceType.ROOK) == PieceType.PROMOTED_ROOK
    assert promote(-PieceType.ROOK) == -PieceType.PROMOTED_ROOK
    assert promote(PieceType.PAWN) == PieceType.PROMOTED_PAWN
    assert promote(PieceType.KING) == PieceType.KING  # King can't promote


def test_unpromote():
    """Test piece unpromotion."""
    assert unpromote(PieceType.PROMOTED_ROOK) == PieceType.ROOK
    assert unpromote(-PieceType.PROMOTED_PAWN) == -PieceType.PAWN
    assert unpromote(PieceType.GOLD) == PieceType.GOLD  # Gold is not promoted


def test_can_promote():
    """Test if piece can promote."""
    assert can_promote(PieceType.ROOK)
    assert can_promote(PieceType.PAWN)
    assert not can_promote(PieceType.KING)
    assert not can_promote(PieceType.GOLD)
    assert not can_promote(PieceType.PROMOTED_ROOK)


def test_is_promoted():
    """Test if piece is promoted."""
    assert is_promoted(PieceType.PROMOTED_ROOK)
    assert is_promoted(-PieceType.PROMOTED_PAWN)
    assert not is_promoted(PieceType.ROOK)
    assert not is_promoted(PieceType.GOLD)


def test_piece_to_string():
    """Test piece to string conversion."""
    assert piece_to_string(PieceType.KING, japanese=True) == '玉'
    assert piece_to_string(-PieceType.KING, japanese=True) == 'v玉'
    assert piece_to_string(PieceType.KING, japanese=False) == 'K'
    assert piece_to_string(-PieceType.KING, japanese=False) == 'k'
    assert piece_to_string(0, japanese=True) == '・'


def test_piece_from_sfen():
    """Test parsing piece from SFEN."""
    assert piece_from_sfen('K') == PieceType.KING
    assert piece_from_sfen('k') == -PieceType.KING
    assert piece_from_sfen('+R') == PieceType.PROMOTED_ROOK
    assert piece_from_sfen('+p') == -PieceType.PROMOTED_PAWN


def test_is_sliding_piece():
    """Test sliding piece detection."""
    assert is_sliding_piece(PieceType.ROOK)
    assert is_sliding_piece(PieceType.BISHOP)
    assert is_sliding_piece(PieceType.LANCE)
    assert is_sliding_piece(PieceType.PROMOTED_ROOK)
    assert not is_sliding_piece(PieceType.KING)
    assert not is_sliding_piece(PieceType.GOLD)


def test_get_piece_moves():
    """Test getting piece moves."""
    # King has 8 moves
    king_moves = get_piece_moves(PieceType.KING)
    assert len(king_moves) == 8
    
    # Pawn has 1 move (forward)
    pawn_moves = get_piece_moves(PieceType.PAWN)
    assert len(pawn_moves) == 1
    assert pawn_moves[0] == (0, -1)  # Up
    
    # Gote pawn moves opposite direction
    gote_pawn_moves = get_piece_moves(-PieceType.PAWN)
    assert len(gote_pawn_moves) == 1
    assert gote_pawn_moves[0] == (0, 1)  # Down


def test_get_piece_directions():
    """Test getting piece directions for sliding pieces."""
    # Rook has 4 directions
    rook_dirs = get_piece_directions(PieceType.ROOK)
    assert len(rook_dirs) == 4
    
    # Bishop has 4 directions
    bishop_dirs = get_piece_directions(PieceType.BISHOP)
    assert len(bishop_dirs) == 4
    
    # Lance has 1 direction (forward)
    lance_dirs = get_piece_directions(PieceType.LANCE)
    assert len(lance_dirs) == 1
