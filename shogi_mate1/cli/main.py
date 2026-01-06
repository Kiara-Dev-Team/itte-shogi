"""
Command-line interface for shogi_mate1.

Commands:
- generate: Generate puzzles
- verify: Verify a SFEN position
- render: Display a SFEN position
"""

import argparse
import sys
from shogi_mate1.core.board import Board
from shogi_mate1.gen.random_gen import generate_random
from shogi_mate1.gen.reverse_gen import generate_reverse
from shogi_mate1.solver.mate1 import verify_mate_position
from shogi_mate1.gen.quality import calculate_difficulty


def cmd_generate(args):
    """Generate puzzles."""
    print(f"Generating {args.n} puzzle(s) using {args.method} method...")
    print(f"Max pieces: {args.max_pieces}")
    if args.seed is not None:
        print(f"Random seed: {args.seed}")
    print()
    
    if args.method == "random":
        puzzles = generate_random(
            n_problems=args.n,
            max_pieces=args.max_pieces,
            require_unique=not args.allow_multiple,
            seed=args.seed
        )
    elif args.method == "reverse":
        puzzles = generate_reverse(
            n_problems=args.n,
            seed=args.seed
        )
    else:
        print(f"Error: Unknown method '{args.method}'")
        return 1
    
    print(f"\nGenerated {len(puzzles)} puzzle(s):\n")
    
    for i, board in enumerate(puzzles, 1):
        print(f"=== Puzzle {i} ===")
        print(board)
        print(f"\nSFEN: {board.to_sfen()}")
        
        # Show difficulty
        difficulty = calculate_difficulty(board)
        print(f"Difficulty score: {difficulty.difficulty_score:.1f}")
        print(f"  - Total pieces: {difficulty.total_pieces}")
        print(f"  - Legal moves: {difficulty.legal_moves}")
        print(f"  - Checking moves: {difficulty.checking_moves}")
        print(f"  - Mate moves: {difficulty.mate_moves}")
        print()
    
    return 0


def cmd_verify(args):
    """Verify a SFEN position."""
    try:
        board = Board.from_sfen(args.sfen)
    except Exception as e:
        print(f"Error parsing SFEN: {e}")
        return 1
    
    print("Position:")
    print(board)
    print()
    
    result = verify_mate_position(board)
    
    print("Verification results:")
    print(f"  Is mate-in-1: {result['is_mate']}")
    print(f"  Unique solution: {result['is_unique']}")
    print(f"  Number of mate moves: {result['mate_count']}")
    
    if result['mate_moves']:
        print(f"\nMate move(s):")
        for move in result['mate_moves']:
            print(f"  - {move}")
    
    stats = result['stats']
    print(f"\nStatistics:")
    print(f"  Total legal moves: {stats.total_legal_moves}")
    print(f"  Checking moves: {stats.total_checking_moves}")
    print(f"  Average responses: {stats.average_responses:.1f}")
    
    return 0


def cmd_render(args):
    """Render a SFEN position."""
    try:
        board = Board.from_sfen(args.sfen)
    except Exception as e:
        print(f"Error parsing SFEN: {e}")
        return 1
    
    print(board)
    print(f"\nSFEN: {board.to_sfen()}")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="一手詰め将棋自動生成システム (One-move checkmate Shogi puzzle generator)"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate puzzles')
    gen_parser.add_argument('--n', type=int, default=1,
                           help='Number of puzzles to generate (default: 1)')
    gen_parser.add_argument('--method', choices=['random', 'reverse'], default='reverse',
                           help='Generation method (default: reverse)')
    gen_parser.add_argument('--max-pieces', type=int, default=10,
                           help='Maximum pieces per position (default: 10)')
    gen_parser.add_argument('--seed', type=int, default=None,
                           help='Random seed for reproducibility')
    gen_parser.add_argument('--allow-multiple', action='store_true',
                           help='Allow multiple solutions (default: require unique)')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a SFEN position')
    verify_parser.add_argument('--sfen', type=str, required=True,
                              help='SFEN string to verify')
    
    # Render command
    render_parser = subparsers.add_parser('render', help='Render a SFEN position')
    render_parser.add_argument('--sfen', type=str, required=True,
                              help='SFEN string to render')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'verify':
        return cmd_verify(args)
    elif args.command == 'render':
        return cmd_render(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
