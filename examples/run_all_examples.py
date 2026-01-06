#!/usr/bin/env python3
"""
Run All Examples Script

This script runs all example operations in sequence, demonstrating
CLI commands programmatically with clear output for each operation.
"""

import sys
import subprocess
from pathlib import Path


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_command(description: str, command: list, show_output: bool = True) -> bool:
    """
    Run a command and display results.
    
    Args:
        description: Description of what the command does
        command: Command to run as a list
        show_output: Whether to show command output
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"▶ {description}")
    print(f"  Command: {' '.join(command)}\n")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if show_output and result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print("✓ Success\n")
            return True
        else:
            print(f"✗ Failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Command timed out after 60 seconds\n")
        return False
    except Exception as e:
        print(f"✗ Error running command: {e}\n")
        return False


def check_python_module():
    """Check if the shogi_mate1 module is installed."""
    print_header("Checking Installation")
    
    try:
        import shogi_mate1
        print(f"✓ shogi_mate1 module is installed (version {shogi_mate1.__version__})")
        return True
    except ImportError:
        print("✗ shogi_mate1 module is not installed")
        print("\nPlease install it with:")
        print("  pip install -e .")
        return False


def run_demo_script():
    """Run the demo.py script."""
    print_header("1. Running Comprehensive Demo Script")
    
    demo_path = Path(__file__).parent / "demo.py"
    
    if not demo_path.exists():
        print(f"✗ Demo script not found at {demo_path}")
        return False
    
    return run_command(
        "Running demo.py to showcase all features",
        ["python", str(demo_path)],
        show_output=True
    )


def run_cli_render():
    """Run CLI render command."""
    print_header("2. CLI Example: Rendering a Position")
    
    sfen = "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
    
    return run_command(
        f"Rendering position: {sfen}",
        ["python", "-m", "shogi_mate1.cli.main", "render", "--sfen", sfen],
        show_output=True
    )


def run_cli_verify():
    """Run CLI verify command."""
    print_header("3. CLI Example: Verifying a Position")
    
    # Use a simple position that should work
    sfen = "8k/9/8G/9/9/9/9/9/K8 b - 1"
    
    return run_command(
        f"Verifying if position is mate-in-1: {sfen}",
        ["python", "-m", "shogi_mate1.cli.main", "verify", "--sfen", sfen],
        show_output=True
    )


def run_cli_generate_reverse():
    """Run CLI generate command with reverse method."""
    print_header("4. CLI Example: Generating Puzzles (Reverse Method)")
    
    return run_command(
        "Generating 1 puzzle using reverse method with seed=42",
        [
            "python", "-m", "shogi_mate1.cli.main",
            "generate", "--method", "reverse", "--n", "1", "--seed", "42"
        ],
        show_output=True
    )


def run_cli_list_puzzles():
    """Run CLI list command."""
    print_header("5. CLI Example: Listing Saved Puzzles")
    
    success = run_command(
        "Listing all saved puzzles",
        ["python", "-m", "shogi_mate1.cli.main", "list"],
        show_output=True
    )
    
    if not success:
        print("Note: This is expected if no puzzles have been saved yet.")
        print("      Use 'create' command to save puzzles.\n")
    
    return True  # Don't fail on this


def demonstrate_api_usage():
    """Demonstrate using the API directly."""
    print_header("6. Direct API Usage Example")
    
    print("Demonstrating direct API usage in Python:\n")
    
    code = '''
from shogi_mate1.core.board import Board
from shogi_mate1.solver.mate1 import verify_mate_position

# Create a board from SFEN
sfen = "8k/9/8G/9/9/9/9/9/K8 b - 1"
print(f"Testing position: {sfen}\\n")

board = Board.from_sfen(sfen)

# Display the board
print("Board visualization:")
print(board)
print()

# Verify the position
result = verify_mate_position(board)
print(f"Is mate-in-1: {result['is_mate']}")
print(f"Unique solution: {result['is_unique']}")
print(f"Mate moves found: {result['mate_count']}")

if result['mate_moves']:
    print("\\nMate move(s):")
    for move in result['mate_moves']:
        print(f"  {move}")

print("\\n✓ API usage demonstration complete")
'''
    
    try:
        exec(code)
        print()
        return True
    except Exception as e:
        print(f"✗ Error in API demonstration: {e}\n")
        return False


def show_help_info():
    """Show helpful information."""
    print_header("7. Getting Help")
    
    print("For more information about available commands:")
    print("  python -m shogi_mate1.cli.main --help\n")
    
    print("For help on specific commands:")
    print("  python -m shogi_mate1.cli.main generate --help")
    print("  python -m shogi_mate1.cli.main verify --help")
    print("  python -m shogi_mate1.cli.main create --help\n")
    
    run_command(
        "Showing main help",
        ["python", "-m", "shogi_mate1.cli.main", "--help"],
        show_output=True
    )
    
    return True


def show_next_steps():
    """Show next steps for users."""
    print_header("Next Steps")
    
    print("Now that you've seen the examples, try these next:")
    print()
    print("1. Create your own puzzle:")
    print("   python -m shogi_mate1.cli.main create")
    print()
    print("2. Generate more puzzles:")
    print("   python -m shogi_mate1.cli.main generate --method reverse --n 5")
    print()
    print("3. Test saved puzzles:")
    print("   python -m shogi_mate1.cli.main test")
    print()
    print("4. Read the tutorial:")
    print("   cat examples/TUTORIAL.md")
    print()
    print("5. Explore the API in your own scripts:")
    print("   from shogi_mate1.core.board import Board")
    print("   from shogi_mate1.solver.mate1 import verify_mate_position")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  ITTE-SHOGI: Running All Examples")
    print("  一手詰め将棋自動生成システム")
    print("=" * 70)
    print("\nThis script demonstrates various features of itte-shogi")
    print("by running examples and CLI commands.\n")
    
    success_count = 0
    total_count = 0
    
    # Check installation first
    if not check_python_module():
        print("\n✗ Cannot proceed without installation")
        return 1
    
    # Run all examples
    examples = [
        ("Demo Script", run_demo_script),
        ("CLI Render", run_cli_render),
        ("CLI Verify", run_cli_verify),
        ("CLI Generate", run_cli_generate_reverse),
        ("CLI List", run_cli_list_puzzles),
        ("API Usage", demonstrate_api_usage),
        ("Help Info", show_help_info),
    ]
    
    for name, func in examples:
        total_count += 1
        try:
            if func():
                success_count += 1
        except KeyboardInterrupt:
            print("\n\n✗ Interrupted by user")
            return 1
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}\n")
    
    # Show next steps
    show_next_steps()
    
    # Summary
    print_header("Summary")
    print(f"Completed {success_count}/{total_count} examples successfully")
    
    if success_count == total_count:
        print("\n✓ All examples ran successfully!")
        print("You're ready to use itte-shogi!\n")
        return 0
    else:
        print(f"\n⚠ {total_count - success_count} example(s) had issues")
        print("Some functionality may not be working as expected.\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
