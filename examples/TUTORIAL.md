# ITTE-SHOGI Tutorial

Welcome to the itte-shogi (一手詰め将棋) tutorial! This guide will walk you through using the system to generate, verify, and work with one-move checkmate puzzles.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Running the Demo Script](#running-the-demo-script)
3. [Understanding SFEN Format](#understanding-sfen-format)
4. [Verifying Positions](#verifying-positions)
5. [Generating Puzzles](#generating-puzzles)
6. [Creating Custom Puzzles](#creating-custom-puzzles)
7. [Using the API](#using-the-api)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. Clone the repository and navigate to it:
```bash
git clone https://github.com/Kiara-Dev-Team/itte-shogi.git
cd itte-shogi
```

2. Install in editable mode:
```bash
pip install -e .
```

3. Verify the installation:
```bash
python -m shogi_mate1.cli.main --help
```

You should see the help message listing available commands.

## Running the Demo Script

The easiest way to get familiar with itte-shogi is to run the comprehensive demo:

```bash
python examples/demo.py
```

This script demonstrates:
- Creating and displaying board positions
- Working with SFEN format
- Verifying positions for mate-in-1
- Generating puzzles using different methods
- Calculating puzzle difficulty
- Error handling
- Using the API programmatically

### Expected Output

The demo runs 8 sections, each showing a different feature. You'll see:

- ✓ Success messages when operations work
- ✗ Error messages when demonstrating error handling
- Board visualizations in Japanese characters
- SFEN strings for each position
- Verification results and statistics

### Running All Examples

To run multiple examples including CLI commands:

```bash
python examples/run_all_examples.py
```

This script runs various operations in sequence and shows you how to use the CLI commands.

## Understanding SFEN Format

SFEN (Shogi Forsyth-Edwards Notation) is the standard format for representing Shogi positions. It's similar to FEN in chess.

### SFEN Structure

```
<board> <side_to_move> <hand_pieces> <move_number>
```

Example: `8k/9/7GG/9/9/9/9/9/K8 b - 1`

### Board Notation

- Rows are separated by `/` (9 rows total)
- Numbers represent empty squares
- Uppercase letters = Sente (先手/Black) pieces
- Lowercase letters = Gote (後手/White) pieces
- `+` prefix indicates promoted pieces

### Piece Letters

| Piece | Japanese | SFEN |
|-------|----------|------|
| King | 玉/王 | K/k |
| Rook | 飛 | R/r |
| Bishop | 角 | B/b |
| Gold | 金 | G/g |
| Silver | 銀 | S/s |
| Knight | 桂 | N/n |
| Lance | 香 | L/l |
| Pawn | 歩 | P/p |
| Promoted Rook | 竜 | +R/+r |
| Promoted Bishop | 馬 | +B/+b |
| Promoted Silver | 成銀 | +S/+s |
| Promoted Knight | 成桂 | +N/+n |
| Promoted Lance | 成香 | +L/+l |
| Promoted Pawn | と | +P/+p |

### Side to Move

- `b` = Black/Sente (先手) to move
- `w` = White/Gote (後手) to move

### Hand Pieces

Pieces held by each player:
- Format: `[count]PIECE` (e.g., `2P` = 2 pawns)
- Multiple pieces: `RBG` = Rook, Bishop, Gold
- No pieces: `-`

### Examples

1. **Empty board except kings:**
   ```
   4k4/9/9/9/9/9/9/9/4K4 b - 1
   ```

2. **Corner mate position:**
   ```
   8k/9/7GG/9/9/9/9/9/K8 b - 1
   ```

3. **Position with hand pieces:**
   ```
   4k4/9/9/9/9/9/9/9/4K4 b RBG 1
   ```
   (Sente has Rook, Bishop, and Gold in hand)

## Verifying Positions

To check if a position is a valid mate-in-1:

```bash
python -m shogi_mate1.cli.main verify --sfen "8k/9/7GG/9/9/9/9/9/K8 b - 1"
```

### Expected Output

```
Position:
  ９ ８ ７ ６ ５ ４ ３ ２ １
一 ・ ・ ・ ・ ・ ・ ・ ・ v玉 
丁 ・ ・ ・ ・ ・ ・ ・ ・ ・ 
丂 ・ ・ ・ ・ ・ ・ ・ 金 金 
...

Verification results:
  Is mate-in-1: True
  Unique solution: False
  Number of mate moves: 4

Mate move(s):
  - 2c1b
  - 2c2b
  - 1c1b
  - 1c2b

Statistics:
  Total legal moves: 7
  Checking moves: 4
  Average responses: 0.0
```

### Understanding the Results

- **Is mate-in-1**: Whether any move leads to immediate checkmate
- **Unique solution**: Whether exactly one move delivers mate
- **Number of mate moves**: How many different moves deliver mate
- **Mate move(s)**: List of moves that deliver checkmate
- **Statistics**: Information about move generation

## Generating Puzzles

### Reverse Method (Recommended)

Generates puzzles from predefined mate templates:

```bash
python -m shogi_mate1.cli.main generate --method reverse --n 3
```

Options:
- `--n NUMBER`: Number of puzzles to generate
- `--seed NUMBER`: Random seed for reproducibility

Example with seed:
```bash
python -m shogi_mate1.cli.main generate --method reverse --n 5 --seed 42
```

### Random Method (Experimental)

Generates random positions and filters for mate-in-1:

```bash
python -m shogi_mate1.cli.main generate --method random --n 1 --max-pieces 8
```

Options:
- `--max-pieces NUMBER`: Maximum pieces on board (default: 10)
- `--allow-multiple`: Allow multiple mate moves (default: requires unique)
- `--seed NUMBER`: Random seed

**Note:** Random generation can take time and may not always find valid positions.

## Creating Custom Puzzles

### Interactive Mode

Create a puzzle interactively:

```bash
python -m shogi_mate1.cli.main create
```

You'll be prompted for:
1. SFEN string
2. Puzzle name
3. Description
4. Author name
5. Tags (space-separated)

The system will:
- Validate the SFEN format
- Display the position
- Check if it's a valid mate-in-1
- Ask for confirmation to save

### Batch Mode

Create puzzles with all parameters specified:

```bash
python -m shogi_mate1.cli.main create \
  --sfen "8k/9/7GG/9/9/9/9/9/K8 b - 1" \
  --name "Corner Gold Mate" \
  --description "Two golds deliver mate" \
  --author "YourName" \
  --tags beginner corner \
  --batch
```

Options:
- `--force`: Save even if verification fails (for templates)
- `--batch`: Non-interactive mode

### Managing Saved Puzzles

List all saved puzzles:
```bash
python -m shogi_mate1.cli.main list
```

List with detailed info:
```bash
python -m shogi_mate1.cli.main list --verbose
```

Test saved puzzles:
```bash
python -m shogi_mate1.cli.main test
```

Test specific puzzle by index:
```bash
python -m shogi_mate1.cli.main test --index 0
```

## Using the API

You can use itte-shogi programmatically in your Python scripts:

### Basic Example

```python
from shogi_mate1.core.board import Board
from shogi_mate1.solver.mate1 import verify_mate_position

# Create a board from SFEN
sfen = "8k/9/7GG/9/9/9/9/9/K8 b - 1"
board = Board.from_sfen(sfen)

# Display the board
print(board)

# Verify if it's mate-in-1
result = verify_mate_position(board)

print(f"Is mate: {result['is_mate']}")
print(f"Unique: {result['is_unique']}")
print(f"Mate count: {result['mate_count']}")

if result['mate_moves']:
    print("\nMate moves:")
    for move in result['mate_moves']:
        print(f"  {move}")
```

### Creating a Board Programmatically

```python
from shogi_mate1.core.board import Board
from shogi_mate1.core.pieces import PieceType

# Create an empty board
board = Board()

# Place pieces
board.set_piece(1, 1, -PieceType.KING)  # Gote king at 1a
board.set_piece(9, 9, PieceType.KING)   # Sente king at 9i

# Add pieces to hand
board.hand_sente[PieceType.GOLD] = 2

# Set side to move (1 = Sente, -1 = Gote)
board.side_to_move = 1

# Convert to SFEN
sfen = board.to_sfen()
print(f"SFEN: {sfen}")
```

### Generating Puzzles

```python
from shogi_mate1.gen.reverse_gen import generate_reverse
from shogi_mate1.gen.random_gen import generate_random

# Generate using reverse method
puzzles = generate_reverse(n_problems=3, seed=42)

for i, board in enumerate(puzzles, 1):
    print(f"\nPuzzle {i}:")
    print(board)
    print(f"SFEN: {board.to_sfen()}")

# Generate using random method (may take time)
random_puzzles = generate_random(
    n_problems=1,
    max_pieces=8,
    require_unique=True,
    seed=123,
    max_attempts=100
)
```

### Calculating Difficulty

```python
from shogi_mate1.core.board import Board
from shogi_mate1.gen.quality import calculate_difficulty

sfen = "8k/9/7GG/9/9/9/9/9/K8 b - 1"
board = Board.from_sfen(sfen)

difficulty = calculate_difficulty(board)

print(f"Difficulty score: {difficulty.difficulty_score:.1f}")
print(f"Total pieces: {difficulty.total_pieces}")
print(f"Legal moves: {difficulty.legal_moves}")
print(f"Checking moves: {difficulty.checking_moves}")
print(f"Mate moves: {difficulty.mate_moves}")
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error

```
ModuleNotFoundError: No module named 'shogi_mate1'
```

**Solution:** Install the package in editable mode:
```bash
pip install -e .
```

#### 2. Invalid SFEN Format

```
Error parsing SFEN: ...
```

**Solution:** Check your SFEN string:
- Must have 4 parts separated by spaces
- Board must have 9 rows separated by `/`
- Each row must account for all 9 squares
- Side to move must be `b` or `w`

Example of valid SFEN:
```
4k4/9/9/9/9/9/9/9/4K4 b - 1
```

#### 3. Position Not Mate-in-1

```
Is mate-in-1: False
```

**Possible reasons:**
- The king can escape
- The checking piece can be captured
- Another piece can block the check
- The position is not in check

**Solution:** Use the `render` command to visualize and verify your position:
```bash
python -m shogi_mate1.cli.main render --sfen "YOUR_SFEN_HERE"
```

#### 4. Random Generation Takes Too Long

Random generation can be slow because it needs to find valid mate positions by chance.

**Solutions:**
- Reduce `--max-pieces` (fewer pieces = faster)
- Use `--method reverse` instead
- Increase timeout if needed
- Use `--seed` for reproducibility

#### 5. Japanese Characters Not Displaying

If you see garbled text instead of Japanese characters:

**Solutions:**
- Ensure your terminal supports UTF-8
- On Windows, use Windows Terminal or set console to UTF-8
- The SFEN format will still work correctly even if display has issues

### Getting Help

- View command-specific help:
  ```bash
  python -m shogi_mate1.cli.main <command> --help
  ```

- Check the main README:
  ```bash
  cat README.md
  ```

- View examples README:
  ```bash
  cat examples/README.md
  ```

- Run demos to see expected behavior:
  ```bash
  python examples/demo.py
  ```

### Performance Tips

1. **Use reverse generation** for reliable puzzle creation
2. **Limit max_pieces** in random generation (8 or fewer)
3. **Use seeds** for reproducible results
4. **Verify positions** before saving as puzzles
5. **Start simple** with corner mate patterns

## Next Steps

Now that you've completed the tutorial:

1. **Create your first puzzle:**
   ```bash
   python -m shogi_mate1.cli.main create
   ```

2. **Generate a set of puzzles:**
   ```bash
   python -m shogi_mate1.cli.main generate --method reverse --n 10 --seed 100
   ```

3. **Explore the API** by writing your own Python scripts

4. **Study tsume patterns** to understand one-move mates better

5. **Contribute** by creating interesting puzzles or improving the codebase

## Additional Resources

- [Main README](../README.md) - Project overview and features
- [Examples README](README.md) - Example file formats
- [SFEN Format Specification](https://web.archive.org/web/20080131070731/http://www.glaurungchess.com/shogi/usi.html)
- [Tsume Shogi Basics](https://en.wikipedia.org/wiki/Tsume_shogi) - Understanding checkmate puzzles

Happy puzzle solving! 詰将棋を楽しんでください！
