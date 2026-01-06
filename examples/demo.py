#!/usr/bin/env python3
"""
Comprehensive Demo Script for itte-shogi

This script demonstrates the main features of the itte-shogi system,
including puzzle generation, position verification, board rendering,
and SFEN format handling.
"""

import sys
from shogi_mate1.core.board import Board
from shogi_mate1.core.pieces import PieceType
from shogi_mate1.gen.random_gen import generate_random
from shogi_mate1.gen.reverse_gen import generate_reverse
from shogi_mate1.solver.mate1 import verify_mate_position, find_mate_moves
from shogi_mate1.gen.quality import calculate_difficulty


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_board_creation():
    """Demonstrate creating and displaying a board position."""
    print_section("1. Creating and Displaying Board Positions")
    
    # Create an empty board
    print("Creating an empty board:")
    board = Board()
    print("Empty board created successfully!\n")
    
    # Create a board from SFEN
    print("Creating a board from SFEN notation:")
    sfen = "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
    print(f"SFEN: {sfen}\n")
    
    try:
        board = Board.from_sfen(sfen)
        print("Board position:")
        print(board)
        print("\n✓ Board created successfully from SFEN")
    except Exception as e:
        print(f"✗ Error creating board: {e}")
        return None
    
    return board


def demo_sfen_handling():
    """Demonstrate SFEN format handling."""
    print_section("2. Working with SFEN Format")
    
    print("SFEN (Shogi Forsyth-Edwards Notation) is the standard format")
    print("for representing Shogi positions.\n")
    
    # Example 1: Simple position
    print("Example 1: Corner mate position")
    sfen1 = "8k/9/9/9/9/9/9/9/K8 b G 1"
    print(f"SFEN: {sfen1}")
    
    try:
        board1 = Board.from_sfen(sfen1)
        print("\nBoard visualization:")
        print(board1)
        
        # Convert back to SFEN
        reconstructed = board1.to_sfen()
        print(f"\nReconstructed SFEN: {reconstructed}")
        print("✓ SFEN parsing and reconstruction successful\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Example 2: Position with pieces in hand
    print("\nExample 2: Position with hand pieces")
    sfen2 = "4k4/9/9/9/9/9/9/9/4K4 b RBG 1"
    print(f"SFEN: {sfen2}")
    print("(Sente has Rook, Bishop, and Gold in hand)")
    
    try:
        board2 = Board.from_sfen(sfen2)
        print("\nBoard visualization:")
        print(board2)
        print("✓ Successfully parsed position with hand pieces\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")


def demo_position_verification():
    """Demonstrate position verification and mate detection."""
    print_section("3. Verifying Positions and Detecting Mate")
    
    # Test a mate-in-1 position
    print("Testing a classic mate-in-1 position:")
    # This is a position where dropping a rook gives mate
    mate_sfen = "4gk3/4gsg2/9/9/9/9/9/9/4K4 b R 1"
    print(f"SFEN: {mate_sfen}\n")
    
    try:
        board = Board.from_sfen(mate_sfen)
        print("Position:")
        print(board)
        print()
        
        # Verify the position
        result = verify_mate_position(board)
        
        print("Verification Results:")
        print(f"  Is mate-in-1: {result['is_mate']}")
        print(f"  Unique solution: {result['is_unique']}")
        print(f"  Number of mate moves: {result['mate_count']}")
        
        if result['mate_moves']:
            print(f"\n  Mate move(s) found:")
            for i, move in enumerate(result['mate_moves'], 1):
                print(f"    {i}. {move}")
        
        stats = result['stats']
        print(f"\n  Statistics:")
        print(f"    Total legal moves: {stats.total_legal_moves}")
        print(f"    Checking moves: {stats.total_checking_moves}")
        print(f"    Average opponent responses: {stats.average_responses:.1f}")
        
        if result['is_mate']:
            print("\n✓ Valid mate-in-1 position confirmed!")
        else:
            print("\n✗ This is not a valid mate-in-1 position")
    except Exception as e:
        print(f"✗ Error during verification: {e}")


def demo_puzzle_generation_reverse():
    """Demonstrate puzzle generation using reverse method."""
    print_section("4. Generating Puzzles (Reverse Method)")
    
    print("The reverse method generates puzzles by working backwards")
    print("from template mate positions.\n")
    
    print("Generating 1 puzzle with seed=42 for reproducibility...")
    
    try:
        puzzles = generate_reverse(n_problems=1, seed=42)
        
        if puzzles:
            print(f"\n✓ Generated {len(puzzles)} puzzle(s)!\n")
            
            for i, board in enumerate(puzzles, 1):
                print(f"Puzzle {i}:")
                print(board)
                print(f"\nSFEN: {board.to_sfen()}")
                
                # Calculate difficulty
                difficulty = calculate_difficulty(board)
                print(f"\nDifficulty Score: {difficulty.difficulty_score:.1f}")
                print(f"  Total pieces: {difficulty.total_pieces}")
                print(f"  Legal moves: {difficulty.legal_moves}")
                print(f"  Checking moves: {difficulty.checking_moves}")
                
                # Verify it's actually mate
                result = verify_mate_position(board)
                if result['is_mate']:
                    print(f"  ✓ Confirmed mate-in-1 with {result['mate_count']} solution(s)")
                else:
                    print(f"  Note: This position needs further refinement")
        else:
            print("✗ No puzzles generated")
    except Exception as e:
        print(f"✗ Error during generation: {e}")


def demo_puzzle_generation_random():
    """Demonstrate puzzle generation using random method."""
    print_section("5. Generating Puzzles (Random Method)")
    
    print("The random method generates puzzles by creating random")
    print("positions and filtering for mate-in-1.\n")
    
    print("Note: Random generation can take time to find valid positions.")
    print("Attempting to generate 1 puzzle with max 8 pieces...")
    print("(This may take a few moments...)\n")
    
    try:
        # Use smaller parameters for faster demo
        puzzles = generate_random(
            n_problems=1,
            max_pieces=8,
            require_unique=True,
            seed=123,
            max_attempts=100  # Limit attempts for demo purposes
        )
        
        if puzzles:
            print(f"✓ Generated {len(puzzles)} puzzle(s)!\n")
            
            for i, board in enumerate(puzzles, 1):
                print(f"Puzzle {i}:")
                print(board)
                print(f"\nSFEN: {board.to_sfen()}")
                
                # Verify
                result = verify_mate_position(board)
                print(f"\nUnique solution: {result['is_unique']}")
                if result['mate_moves']:
                    print(f"Mate move: {result['mate_moves'][0]}")
        else:
            print("✗ No valid puzzles found in the attempt limit")
            print("   (Random generation success rate varies)")
    except Exception as e:
        print(f"✗ Error during generation: {e}")


def demo_difficulty_calculation():
    """Demonstrate difficulty calculation for positions."""
    print_section("6. Calculating Puzzle Difficulty")
    
    print("The system can evaluate puzzle difficulty based on")
    print("several factors: piece count, legal moves, and mate moves.\n")
    
    # Test multiple positions with different difficulty levels
    positions = [
        ("Simple", "8k/9/8G/9/9/9/9/9/K8 b - 1"),
        ("Medium", "4gk3/4gsg2/9/9/9/9/9/9/4K4 b R 1"),
        ("Complex", "3gkg3/3sps3/4R4/9/9/9/9/9/4K4 b - 1"),
    ]
    
    for name, sfen in positions:
        print(f"{name} position:")
        print(f"SFEN: {sfen}")
        
        try:
            board = Board.from_sfen(sfen)
            difficulty = calculate_difficulty(board)
            
            print(f"  Difficulty score: {difficulty.difficulty_score:.1f}")
            print(f"  - Total pieces: {difficulty.total_pieces}")
            print(f"  - Legal moves: {difficulty.legal_moves}")
            print(f"  - Checking moves: {difficulty.checking_moves}")
            print(f"  - Mate moves: {difficulty.mate_moves}")
            print()
        except Exception as e:
            print(f"  ✗ Error: {e}\n")


def demo_error_handling():
    """Demonstrate error handling for invalid positions."""
    print_section("7. Error Handling and Validation")
    
    print("The system validates SFEN strings and handles errors gracefully.\n")
    
    # Test invalid SFEN
    print("Example 1: Invalid SFEN format")
    invalid_sfen = "invalid_sfen_string"
    print(f"SFEN: {invalid_sfen}")
    
    try:
        board = Board.from_sfen(invalid_sfen)
        print("✗ Should have raised an error!")
    except Exception as e:
        print(f"✓ Caught error as expected: {type(e).__name__}")
        print(f"  Message: {str(e)[:60]}...\n" if len(str(e)) > 60 else f"  Message: {e}\n")
    
    # Test valid SFEN but not mate position
    print("Example 2: Valid SFEN but not a mate-in-1")
    non_mate_sfen = "9/9/9/9/4k4/9/9/9/4K4 b - 1"
    print(f"SFEN: {non_mate_sfen}")
    
    try:
        board = Board.from_sfen(non_mate_sfen)
        result = verify_mate_position(board)
        
        if not result['is_mate']:
            print("✓ Position is valid but not mate-in-1 (as expected)")
            print(f"  Found {result['mate_count']} mate moves\n")
    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")


def demo_programmatic_usage():
    """Demonstrate programmatic usage of core modules."""
    print_section("8. Programmatic Usage Example")
    
    print("Example: Creating a position programmatically\n")
    
    try:
        # Create a new board
        board = Board()
        
        # Place pieces manually
        # Note: File 1 is rightmost (1筋), File 9 is leftmost (9筋)
        # Rank 1 is top row (一段), Rank 9 is bottom row (九段)
        print("Setting up a corner mate position...")
        board.set_piece(1, 1, -PieceType.KING)  # Gote king at 1a (corner)
        board.set_piece(2, 1, -PieceType.GOLD)  # Gote gold at 2a (blocking escape)
        board.set_piece(1, 2, -PieceType.GOLD)  # Gote gold at 1b (blocking escape)
        board.set_piece(5, 9, PieceType.KING)   # Sente king at 5i (safe position)
        
        # Add piece to Sente's hand
        board.hand_sente[PieceType.GOLD] = 1
        board.side_to_move = 1  # Sente to move
        
        print("\nCreated position:")
        print(board)
        
        sfen = board.to_sfen()
        print(f"\nSFEN: {sfen}")
        
        # Verify it
        result = verify_mate_position(board)
        print(f"\nIs mate-in-1: {result['is_mate']}")
        print(f"Unique solution: {result['is_unique']}")
        
        if result['mate_moves']:
            print(f"\nMate move(s):")
            for move in result['mate_moves']:
                print(f"  {move}")
        
        print("\n✓ Programmatic board creation successful!")
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  ITTE-SHOGI COMPREHENSIVE DEMONSTRATION")
    print("  一手詰め将棋自動生成システム")
    print("=" * 70)
    print("\nThis demo showcases the main features of the itte-shogi system.")
    print("Each section demonstrates a different aspect of the library.\n")
    
    try:
        # Run all demos
        demo_board_creation()
        demo_sfen_handling()
        demo_position_verification()
        demo_puzzle_generation_reverse()
        demo_puzzle_generation_random()
        demo_difficulty_calculation()
        demo_error_handling()
        demo_programmatic_usage()
        
        # Summary
        print_section("Demo Complete!")
        print("You've seen:")
        print("  ✓ Board creation and rendering")
        print("  ✓ SFEN format handling")
        print("  ✓ Position verification")
        print("  ✓ Puzzle generation (reverse and random methods)")
        print("  ✓ Difficulty calculation")
        print("  ✓ Error handling")
        print("  ✓ Programmatic API usage")
        print("\nFor more details, see:")
        print("  - examples/TUTORIAL.md")
        print("  - examples/README.md")
        print("  - Main README.md")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\n✗ Unexpected error in demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
