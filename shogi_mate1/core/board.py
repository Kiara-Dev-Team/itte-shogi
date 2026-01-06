"""
Board representation for Shogi.

The board is represented as a 1D array of 81 elements (9x9).
Index mapping: index = rank * 9 + file_offset
- File: 9 (left) to 1 (right) -> file_offset = 9 - file
- Rank: 1 (top) to 9 (bottom) -> starts at 0
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from shogi_mate1.core.pieces import (
    PieceType, piece_to_string, piece_from_sfen, unpromote
)
from shogi_mate1.core.move import Move, square_to_index


@dataclass
class Board:
    """
    Represents a Shogi board position.
    
    Attributes:
        squares: 1D array of 81 squares (0 = empty, positive = Sente, negative = Gote)
        side_to_move: Current side to move (1 = Sente, -1 = Gote)
        hand_sente: Dict of piece types in Sente's hand {piece_type: count}
        hand_gote: Dict of piece types in Gote's hand {piece_type: count}
    """
    squares: List[int] = field(default_factory=lambda: [0] * 81)
    side_to_move: int = 1  # 1 for Sente, -1 for Gote
    hand_sente: dict = field(default_factory=dict)
    hand_gote: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize hand dictionaries if needed."""
        if not self.hand_sente:
            self.hand_sente = {}
        if not self.hand_gote:
            self.hand_gote = {}
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        return Board(
            squares=self.squares[:],
            side_to_move=self.side_to_move,
            hand_sente=self.hand_sente.copy(),
            hand_gote=self.hand_gote.copy()
        )
    
    def get_piece(self, file: int, rank: int) -> int:
        """
        Get piece at given file and rank.
        
        Args:
            file: File number (1-9)
            rank: Rank number (1-9)
            
        Returns:
            Piece value
        """
        index = square_to_index(file, rank)
        return self.squares[index]
    
    def set_piece(self, file: int, rank: int, piece: int):
        """Set piece at given file and rank."""
        index = square_to_index(file, rank)
        self.squares[index] = piece
    
    def find_king(self, side: int) -> Optional[int]:
        """
        Find the king position for the given side.
        
        Args:
            side: 1 for Sente, -1 for Gote
            
        Returns:
            Square index of the king, or None if not found
        """
        king_piece = PieceType.KING if side > 0 else -PieceType.KING
        for i, piece in enumerate(self.squares):
            if piece == king_piece:
                return i
        return None
    
    def apply_move(self, move: Move) -> Tuple[int, Optional[int]]:
        """
        Apply a move to the board.
        
        Args:
            move: Move to apply
            
        Returns:
            Tuple of (captured_piece, promoted_from) for undo
        """
        from shogi_mate1.core.pieces import promote, unpromote
        
        if move.is_drop():
            # Drop move
            self.squares[move.to_sq] = move.drop_piece
            
            # Remove from hand
            piece_type = abs(move.drop_piece)
            if self.side_to_move > 0:
                self.hand_sente[piece_type] = self.hand_sente.get(piece_type, 0) - 1
                if self.hand_sente[piece_type] <= 0:
                    del self.hand_sente[piece_type]
            else:
                self.hand_gote[piece_type] = self.hand_gote.get(piece_type, 0) - 1
                if self.hand_gote[piece_type] <= 0:
                    del self.hand_gote[piece_type]
            
            self.side_to_move = -self.side_to_move
            return (0, None)
        else:
            # Regular move
            moving_piece = self.squares[move.from_sq]
            captured_piece = self.squares[move.to_sq]
            
            # Apply promotion if needed
            if move.is_promote:
                moving_piece = promote(moving_piece)
            
            # Move the piece
            self.squares[move.to_sq] = moving_piece
            self.squares[move.from_sq] = 0
            
            # Handle capture
            if captured_piece != 0:
                # Add to hand (unpromoted)
                piece_type = abs(unpromote(captured_piece))
                if self.side_to_move > 0:
                    self.hand_sente[piece_type] = self.hand_sente.get(piece_type, 0) + 1
                else:
                    self.hand_gote[piece_type] = self.hand_gote.get(piece_type, 0) + 1
            
            self.side_to_move = -self.side_to_move
            return (captured_piece, moving_piece if move.is_promote else None)
    
    def undo_move(self, move: Move, captured_piece: int, promoted_from: Optional[int]):
        """
        Undo a move.
        
        Args:
            move: Move to undo
            captured_piece: Piece that was captured (0 if none)
            promoted_from: Original piece before promotion (None if no promotion)
        """
        from shogi_mate1.core.pieces import unpromote
        
        # Switch side back
        self.side_to_move = -self.side_to_move
        
        if move.is_drop():
            # Undo drop
            self.squares[move.to_sq] = 0
            
            # Add back to hand
            piece_type = abs(move.drop_piece)
            if self.side_to_move > 0:
                self.hand_sente[piece_type] = self.hand_sente.get(piece_type, 0) + 1
            else:
                self.hand_gote[piece_type] = self.hand_gote.get(piece_type, 0) + 1
        else:
            # Undo regular move
            moving_piece = self.squares[move.to_sq]
            
            # Restore original piece (unpromote if it was promoted)
            if promoted_from is not None:
                moving_piece = unpromote(moving_piece)
            
            self.squares[move.from_sq] = moving_piece
            self.squares[move.to_sq] = captured_piece
            
            # Remove from hand if there was a capture
            if captured_piece != 0:
                piece_type = abs(unpromote(captured_piece))
                if self.side_to_move > 0:
                    self.hand_sente[piece_type] = self.hand_sente.get(piece_type, 0) - 1
                    if self.hand_sente[piece_type] <= 0:
                        del self.hand_sente[piece_type]
                else:
                    self.hand_gote[piece_type] = self.hand_gote.get(piece_type, 0) - 1
                    if self.hand_gote[piece_type] <= 0:
                        del self.hand_gote[piece_type]
    
    def to_sfen(self) -> str:
        """
        Convert board to SFEN notation.
        
        Returns:
            SFEN string
        """
        # Board part
        sfen_rows = []
        for rank in range(9):
            row_sfen = ""
            empty_count = 0
            for file in range(9, 0, -1):
                piece = self.get_piece(file, rank + 1)
                if piece == 0:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_sfen += str(empty_count)
                        empty_count = 0
                    row_sfen += piece_to_string(piece, japanese=False)
            if empty_count > 0:
                row_sfen += str(empty_count)
            sfen_rows.append(row_sfen)
        
        board_sfen = '/'.join(sfen_rows)
        
        # Side to move
        side_sfen = 'b' if self.side_to_move > 0 else 'w'
        
        # Hand pieces
        hand_sfen = ""
        if self.hand_sente or self.hand_gote:
            # Sente's hand (uppercase)
            for piece_type in [PieceType.ROOK, PieceType.BISHOP, PieceType.GOLD,
                              PieceType.SILVER, PieceType.KNIGHT, PieceType.LANCE, PieceType.PAWN]:
                count = self.hand_sente.get(piece_type, 0)
                if count > 0:
                    piece_str = piece_to_string(piece_type, japanese=False)
                    if count > 1:
                        hand_sfen += str(count)
                    hand_sfen += piece_str
            
            # Gote's hand (lowercase)
            for piece_type in [PieceType.ROOK, PieceType.BISHOP, PieceType.GOLD,
                              PieceType.SILVER, PieceType.KNIGHT, PieceType.LANCE, PieceType.PAWN]:
                count = self.hand_gote.get(piece_type, 0)
                if count > 0:
                    piece_str = piece_to_string(-piece_type, japanese=False)
                    if count > 1:
                        hand_sfen += str(count)
                    hand_sfen += piece_str
        
        if not hand_sfen:
            hand_sfen = "-"
        
        return f"{board_sfen} {side_sfen} {hand_sfen} 1"
    
    @staticmethod
    def from_sfen(sfen: str) -> 'Board':
        """
        Create a board from SFEN notation.
        
        Args:
            sfen: SFEN string
            
        Returns:
            Board object
        """
        parts = sfen.strip().split()
        if len(parts) < 3:
            raise ValueError("Invalid SFEN: not enough parts")
        
        board_part = parts[0]
        side_part = parts[1]
        hand_part = parts[2] if len(parts) > 2 else "-"
        
        board = Board()
        
        # Parse board
        ranks = board_part.split('/')
        if len(ranks) != 9:
            raise ValueError("Invalid SFEN: board must have 9 ranks")
        
        for rank_idx, rank_str in enumerate(ranks):
            file = 9
            i = 0
            while i < len(rank_str):
                ch = rank_str[i]
                if ch.isdigit():
                    # Empty squares
                    empty_count = int(ch)
                    file -= empty_count
                else:
                    # Piece
                    if ch == '+' and i + 1 < len(rank_str):
                        piece_str = ch + rank_str[i + 1]
                        i += 1
                    else:
                        piece_str = ch
                    
                    piece = piece_from_sfen(piece_str)
                    if piece is not None:
                        board.set_piece(file, rank_idx + 1, piece)
                    file -= 1
                i += 1
        
        # Parse side to move
        board.side_to_move = 1 if side_part == 'b' else -1
        
        # Parse hand
        if hand_part != "-":
            i = 0
            while i < len(hand_part):
                # Check for count
                count = 0
                while i < len(hand_part) and hand_part[i].isdigit():
                    count = count * 10 + int(hand_part[i])
                    i += 1
                if count == 0:
                    count = 1
                
                if i >= len(hand_part):
                    break
                
                # Get piece character
                piece_char = hand_part[i]
                if piece_char == '+' and i + 1 < len(hand_part):
                    piece_char = piece_char + hand_part[i + 1]
                    i += 1
                
                piece = piece_from_sfen(piece_char)
                if piece is not None:
                    piece_type = abs(piece)
                    if piece > 0:
                        board.hand_sente[piece_type] = board.hand_sente.get(piece_type, 0) + count
                    else:
                        board.hand_gote[piece_type] = board.hand_gote.get(piece_type, 0) + count
                
                i += 1
        
        return board
    
    def __str__(self) -> str:
        """
        Convert board to text representation.
        
        Returns:
            Text diagram of the board
        """
        lines = []
        
        # Header
        lines.append("  ９ ８ ７ ６ ５ ４ ３ ２ １")
        
        # Board rows
        for rank in range(1, 10):
            row_str = chr(ord('一') + rank - 1) + " "
            for file in range(9, 0, -1):
                piece = self.get_piece(file, rank)
                row_str += piece_to_string(piece, japanese=True) + " "
            lines.append(row_str)
        
        # Hand pieces
        if self.hand_sente:
            hand_str = "先手持ち駒: "
            for piece_type, count in sorted(self.hand_sente.items()):
                piece_name = piece_to_string(piece_type, japanese=True)
                if count > 1:
                    hand_str += f"{piece_name}×{count} "
                else:
                    hand_str += f"{piece_name} "
            lines.append(hand_str)
        
        if self.hand_gote:
            hand_str = "後手持ち駒: "
            for piece_type, count in sorted(self.hand_gote.items()):
                piece_name = piece_to_string(piece_type, japanese=True)
                if count > 1:
                    hand_str += f"{piece_name}×{count} "
                else:
                    hand_str += f"{piece_name} "
            lines.append(hand_str)
        
        side_str = "先手番" if self.side_to_move > 0 else "後手番"
        lines.append(side_str)
        
        return '\n'.join(lines)
