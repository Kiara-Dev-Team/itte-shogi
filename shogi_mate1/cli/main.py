"""
Command-line interface for shogi_mate1.

Commands:
- generate: Generate puzzles
- verify: Verify a SFEN position
- render: Display a SFEN position
- create: Create and save user puzzles
- test: Test saved puzzles
- list: List saved puzzles
"""

import argparse
import sys
from shogi_mate1.core.board import Board
from shogi_mate1.gen.random_gen import generate_random
from shogi_mate1.gen.reverse_gen import generate_reverse
from shogi_mate1.solver.mate1 import verify_mate_position
from shogi_mate1.gen.quality import calculate_difficulty
from shogi_mate1.puzzles.storage import PuzzleStorage


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


def cmd_create(args):
    """Create and save a user puzzle."""
    storage = PuzzleStorage(args.storage_dir)
    
    print("=== Create User Puzzle ===\n")
    
    # Get SFEN from command line or interactively
    if args.sfen:
        sfen = args.sfen
    else:
        print("Enter SFEN position (or press Ctrl+C to cancel):")
        try:
            sfen = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return 0
    
    # Validate and verify the puzzle
    try:
        board = Board.from_sfen(sfen)
    except Exception as e:
        print(f"Error: Invalid SFEN - {e}")
        return 1
    
    print("\nPosition:")
    print(board)
    print()
    
    # Verify it's a valid mate-in-1 puzzle
    result = verify_mate_position(board)
    
    print("Verification:")
    print(f"  Is mate-in-1: {result['is_mate']}")
    print(f"  Unique solution: {result['is_unique']}")
    print(f"  Number of mate moves: {result['mate_count']}")
    
    if result['mate_moves']:
        print(f"\n  Mate move(s):")
        for move in result['mate_moves']:
            print(f"    - {move}")
    
    if not result['is_mate']:
        print("\nWarning: This position is not a mate-in-1 puzzle!")
        if not args.force:
            print("Use --force to save anyway, or fix the position.")
            return 1
    
    if result['mate_count'] > 1 and not args.allow_multiple:
        print("\nWarning: This puzzle has multiple solutions!")
        if not args.force:
            print("Use --force or --allow-multiple to save anyway.")
            return 1
    
    # Get puzzle metadata
    name = args.name or ""
    description = args.description or ""
    author = args.author or ""
    tags = args.tags or []
    
    if not args.batch:
        # Interactive mode - ask for metadata
        if not name:
            name = input("\nPuzzle name (optional): ").strip()
        if not description:
            description = input("Description (optional): ").strip()
        if not author:
            author = input("Author (optional): ").strip()
        if not tags:
            tags_input = input("Tags (comma-separated, optional): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    
    # Save the puzzle
    try:
        puzzle = storage.save_puzzle(sfen, name, description, author, tags)
        print(f"\n✓ Puzzle saved successfully as: {puzzle['name']}")
        print(f"Total puzzles in storage: {storage.count_puzzles()}")
        return 0
    except Exception as e:
        print(f"\nError saving puzzle: {e}")
        return 1


def cmd_test(args):
    """Test saved puzzles."""
    storage = PuzzleStorage(args.storage_dir)
    puzzles = storage.load_all_puzzles()
    
    if not puzzles:
        print("No puzzles found in storage.")
        return 0
    
    print(f"=== Testing {len(puzzles)} Puzzle(s) ===\n")
    
    passed = 0
    failed = 0
    
    for i, puzzle_data in enumerate(puzzles):
        name = puzzle_data.get('name', f'Puzzle {i+1}')
        sfen = puzzle_data.get('sfen', '')
        
        if args.index is not None and i != args.index:
            continue
        
        print(f"[{i}] {name}")
        print(f"    SFEN: {sfen}")
        
        try:
            board = Board.from_sfen(sfen)
            result = verify_mate_position(board)
            
            if result['is_mate'] and result['is_unique']:
                print(f"    ✓ PASS - Valid unique mate-in-1")
                passed += 1
            elif result['is_mate']:
                print(f"    ⚠ PASS (with warnings) - Mate-in-1 with {result['mate_count']} solutions")
                passed += 1
            else:
                print(f"    ✗ FAIL - Not a mate-in-1 position")
                failed += 1
            
            if args.verbose:
                print(f"      Legal moves: {result['stats'].total_legal_moves}")
                print(f"      Checking moves: {result['stats'].total_checking_moves}")
                if result['mate_moves']:
                    print(f"      Mate moves: {', '.join(str(m) for m in result['mate_moves'])}")
        
        except Exception as e:
            print(f"    ✗ ERROR - {e}")
            failed += 1
        
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def cmd_list(args):
    """List saved puzzles."""
    storage = PuzzleStorage(args.storage_dir)
    puzzles = storage.load_all_puzzles()
    
    if not puzzles:
        print("No puzzles found in storage.")
        return 0
    
    print(f"=== Saved Puzzles ({len(puzzles)}) ===\n")
    
    for i, puzzle_data in enumerate(puzzles):
        name = puzzle_data.get('name', f'Puzzle {i+1}')
        author = puzzle_data.get('author', '')
        description = puzzle_data.get('description', '')
        tags = puzzle_data.get('tags', [])
        created_at = puzzle_data.get('created_at', '')
        
        print(f"[{i}] {name}")
        if author:
            print(f"    Author: {author}")
        if description:
            print(f"    Description: {description}")
        if tags:
            print(f"    Tags: {', '.join(tags)}")
        if created_at:
            print(f"    Created: {created_at}")
        if args.verbose:
            print(f"    SFEN: {puzzle_data.get('sfen', '')}")
        print()
    
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
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create and save a user puzzle')
    create_parser.add_argument('--sfen', type=str,
                              help='SFEN string of the puzzle (if not provided, will prompt)')
    create_parser.add_argument('--name', type=str,
                              help='Name for the puzzle')
    create_parser.add_argument('--description', type=str,
                              help='Description of the puzzle')
    create_parser.add_argument('--author', type=str,
                              help='Author name')
    create_parser.add_argument('--tags', type=str, nargs='+',
                              help='Tags for the puzzle')
    create_parser.add_argument('--storage-dir', type=str,
                              help='Directory to store puzzles (default: ./puzzles/)')
    create_parser.add_argument('--force', action='store_true',
                              help='Save puzzle even if validation fails')
    create_parser.add_argument('--allow-multiple', action='store_true',
                              help='Allow puzzles with multiple solutions')
    create_parser.add_argument('--batch', action='store_true',
                              help='Batch mode - do not prompt for metadata')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test saved puzzles')
    test_parser.add_argument('--storage-dir', type=str,
                            help='Directory where puzzles are stored (default: ./puzzles/)')
    test_parser.add_argument('--index', type=int,
                            help='Test only the puzzle at this index')
    test_parser.add_argument('--verbose', action='store_true',
                            help='Show detailed verification information')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List saved puzzles')
    list_parser.add_argument('--storage-dir', type=str,
                            help='Directory where puzzles are stored (default: ./puzzles/)')
    list_parser.add_argument('--verbose', action='store_true',
                            help='Show full puzzle details including SFEN')
    
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
    elif args.command == 'create':
        return cmd_create(args)
    elif args.command == 'test':
        return cmd_test(args)
    elif args.command == 'list':
        return cmd_list(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
