# Example Puzzles for Itte Tsume Shogi

This directory contains example puzzles that demonstrate how to create and test Itte Tsume Shogi (one-move checkmate) puzzles.

## Example Puzzle File Format

Puzzles are stored in JSON format with the following structure:

```json
{
  "sfen": "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1",
  "name": "Corner Position Example",
  "description": "Example puzzle showing how to store a position",
  "author": "Example",
  "tags": ["example", "corner"],
  "created_at": "2026-01-06T00:00:00"
}
```

### Fields:

- **sfen**: The position in SFEN (Shogi Forsyth-Edwards Notation) format
- **name**: A descriptive name for the puzzle
- **description**: Detailed explanation of the puzzle
- **author**: Name of the puzzle creator
- **tags**: Array of tags for categorization
- **created_at**: ISO timestamp of when the puzzle was created

## Using Example Puzzles

### Test the examples:
```bash
# First, copy examples to your puzzle storage
cp examples/example_puzzles.json puzzles/user_puzzles.json

# Then test them
python -m shogi_mate1.cli.main test
```

### Test with verbose output:
```bash
python -m shogi_mate1.cli.main test --verbose
```

### View a position:
```bash
python -m shogi_mate1.cli.main render --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
```

### Verify a position is a valid mate-in-1:
```bash
python -m shogi_mate1.cli.main verify --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
```

## Creating Your Own Puzzles

### Interactive mode:
```bash
python -m shogi_mate1.cli.main create
```

You'll be prompted to enter a SFEN string and metadata for your puzzle. The system will:
1. Validate the SFEN format
2. Display the position
3. Verify if it's a valid mate-in-1
4. Ask for puzzle metadata (name, description, author, tags)
5. Save the puzzle to storage

### Batch mode with all parameters:
```bash
python -m shogi_mate1.cli.main create \
  --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1" \
  --name "My Puzzle" \
  --description "A challenging mate" \
  --author "YourName" \
  --tags challenge advanced \
  --batch
```

### Generate and save puzzles:
```bash
# Generate a puzzle using reverse method
python -m shogi_mate1.cli.main generate --method reverse --n 1

# Copy the SFEN and create a puzzle from it
python -m shogi_mate1.cli.main create --sfen "PASTE_SFEN_HERE" --batch --force
```

## SFEN Format

SFEN (Shogi Forsyth-Edwards Notation) is the standard way to represent Shogi positions:

```
BOARD_POSITION SIDE_TO_MOVE HAND_PIECES MOVE_NUMBER
```

Example: `7gk/7pg/8R/9/9/9/9/9/4K4 b - 1`

- **Board**: Rows separated by `/`, pieces denoted by letters (uppercase=Sente, lowercase=Gote)
- **Side**: `b` for black (Sente), `w` for white (Gote)
- **Hand**: Pieces in hand (e.g., `R` for Rook, `2P` for 2 Pawns), or `-` for none
- **Move**: Move number (usually `1` for puzzles)

### Piece notation:
- K/k: King (王/玉)
- R/r: Rook (飛)
- B/b: Bishop (角)
- G/g: Gold (金)
- S/s: Silver (銀)
- N/n: Knight (桂)
- L/l: Lance (香)
- P/p: Pawn (歩)
- +R/+r: Promoted Rook (竜)
- +B/+b: Promoted Bishop (馬)
- +S/+s: Promoted Silver (成銀)
- +N/+n: Promoted Knight (成桂)
- +L/+l: Promoted Lance (成香)
- +P/+p: Promoted Pawn (と)

## Tips for Creating Good Puzzles

1. **Use the verify command** to check your position before saving
2. **Start with simple positions** - clear mate-in-1 scenarios
3. **Ensure uniqueness** - ideally there's only one mating move
4. **Use meaningful names and descriptions** to help others understand the puzzle
5. **Tag appropriately** for easy searching and categorization

See the main README.md for more commands and options.
