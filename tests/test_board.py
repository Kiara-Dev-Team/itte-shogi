"""Tests for board module."""

import pytest
from shogi_mate1.core.board import Board
from shogi_mate1.core.pieces import PieceType
from shogi_mate1.core.move import Move, square_to_index


def test_empty_board():
    """Test creating an empty board."""
    board = Board()
    assert len(board.squares) == 81
    assert all(sq == 0 for sq in board.squares)
    assert board.side_to_move == 1


def test_get_set_piece():
    """Test getting and setting pieces."""
    board = Board()
    board.set_piece(5, 5, PieceType.KING)
    assert board.get_piece(5, 5) == PieceType.KING
    
    board.set_piece(1, 1, -PieceType.ROOK)
    assert board.get_piece(1, 1) == -PieceType.ROOK


def test_find_king():
    """Test finding king position."""
    board = Board()
    board.set_piece(5, 9, PieceType.KING)
    board.set_piece(5, 1, -PieceType.KING)
    
    sente_king = board.find_king(1)
    gote_king = board.find_king(-1)
    
    assert sente_king == square_to_index(5, 9)
    assert gote_king == square_to_index(5, 1)


def test_board_copy():
    """Test board copying."""
    board = Board()
    board.set_piece(5, 5, PieceType.KING)
    board.hand_sente[PieceType.PAWN] = 2
    
    board2 = board.copy()
    assert board2.get_piece(5, 5) == PieceType.KING
    assert board2.hand_sente[PieceType.PAWN] == 2
    
    # Modify copy
    board2.set_piece(5, 5, 0)
    board2.hand_sente[PieceType.PAWN] = 3
    
    # Original should be unchanged
    assert board.get_piece(5, 5) == PieceType.KING
    assert board.hand_sente[PieceType.PAWN] == 2


def test_sfen_empty():
    """Test SFEN for empty board."""
    board = Board()
    sfen = board.to_sfen()
    assert '9/9/9/9/9/9/9/9/9 b - 1' == sfen


def test_sfen_simple_position():
    """Test SFEN for a simple position."""
    board = Board()
    board.set_piece(5, 1, -PieceType.KING)
    board.set_piece(5, 9, PieceType.KING)
    sfen = board.to_sfen()
    # Should have kings on 5a and 5i
    assert 'k' in sfen.lower()
    assert 'K' in sfen or 'k' in sfen


def test_sfen_with_hand():
    """Test SFEN with pieces in hand."""
    board = Board()
    board.set_piece(5, 9, PieceType.KING)
    board.set_piece(5, 1, -PieceType.KING)
    board.hand_sente[PieceType.PAWN] = 2
    board.hand_gote[PieceType.ROOK] = 1
    
    sfen = board.to_sfen()
    assert '2P' in sfen or 'P' in sfen  # Sente has pawns
    assert 'r' in sfen  # Gote has rook


def test_from_sfen():
    """Test parsing SFEN."""
    # Simple position: Kings only
    sfen = "4k4/9/9/9/9/9/9/9/4K4 b - 1"
    board = Board.from_sfen(sfen)
    
    # Check kings
    assert board.get_piece(5, 1) == -PieceType.KING
    assert board.get_piece(5, 9) == PieceType.KING
    assert board.side_to_move == 1


def test_from_sfen_with_hand():
    """Test parsing SFEN with hand pieces."""
    sfen = "4k4/9/9/9/9/9/9/9/4K4 b 2Pr 1"
    board = Board.from_sfen(sfen)
    
    assert board.hand_sente.get(PieceType.PAWN, 0) == 2
    assert board.hand_gote.get(PieceType.ROOK, 0) == 1


def test_sfen_roundtrip():
    """Test SFEN round-trip conversion."""
    original_sfen = "4k4/9/9/9/9/9/9/9/4K4 b - 1"
    board = Board.from_sfen(original_sfen)
    generated_sfen = board.to_sfen()
    board2 = Board.from_sfen(generated_sfen)
    
    # Boards should be identical
    assert board.squares == board2.squares
    assert board.side_to_move == board2.side_to_move


def test_apply_undo_move():
    """Test applying and undoing moves."""
    board = Board()
    board.set_piece(5, 5, PieceType.ROOK)
    
    move = Move(from_sq=square_to_index(5, 5), to_sq=square_to_index(5, 1))
    captured, promoted = board.apply_move(move)
    
    assert board.get_piece(5, 1) == PieceType.ROOK
    assert board.get_piece(5, 5) == 0
    assert board.side_to_move == -1
    
    board.undo_move(move, captured, promoted)
    assert board.get_piece(5, 5) == PieceType.ROOK
    assert board.get_piece(5, 1) == 0
    assert board.side_to_move == 1


def test_apply_capture():
    """Test capturing a piece."""
    board = Board()
    board.set_piece(5, 5, PieceType.ROOK)
    board.set_piece(5, 1, -PieceType.PAWN)
    
    move = Move(from_sq=square_to_index(5, 5), to_sq=square_to_index(5, 1))
    captured, promoted = board.apply_move(move)
    
    assert captured == -PieceType.PAWN
    assert board.hand_sente.get(PieceType.PAWN, 0) == 1
    
    board.undo_move(move, captured, promoted)
    assert board.get_piece(5, 1) == -PieceType.PAWN
    assert board.hand_sente.get(PieceType.PAWN, 0) == 0


def test_apply_drop():
    """Test drop move."""
    board = Board()
    board.hand_sente[PieceType.PAWN] = 1
    
    move = Move(from_sq=None, to_sq=square_to_index(5, 5), drop_piece=PieceType.PAWN)
    captured, promoted = board.apply_move(move)
    
    assert board.get_piece(5, 5) == PieceType.PAWN
    assert board.hand_sente.get(PieceType.PAWN, 0) == 0
    
    board.undo_move(move, captured, promoted)
    assert board.get_piece(5, 5) == 0
    assert board.hand_sente.get(PieceType.PAWN, 0) == 1
