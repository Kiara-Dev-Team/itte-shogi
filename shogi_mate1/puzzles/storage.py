"""
Puzzle storage and management module.

This module handles:
- Saving user-created puzzles
- Loading puzzles from storage
- Managing puzzle collections
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from shogi_mate1.core.board import Board


class PuzzleStorage:
    """Manages storage of user-created puzzles."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize puzzle storage.
        
        Args:
            storage_dir: Directory to store puzzles. Defaults to ./puzzles/
        """
        if storage_dir is None:
            storage_dir = os.path.join(os.getcwd(), "puzzles")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.puzzle_file = self.storage_dir / "user_puzzles.json"
    
    def save_puzzle(self, sfen: str, name: str = "", description: str = "", 
                   author: str = "", tags: List[str] = None) -> Dict[str, Any]:
        """
        Save a puzzle to storage.
        
        Args:
            sfen: SFEN string of the puzzle
            name: Optional name for the puzzle
            description: Optional description
            author: Optional author name
            tags: Optional list of tags
            
        Returns:
            Dict with puzzle information
        """
        # Validate SFEN
        try:
            board = Board.from_sfen(sfen)
        except Exception as e:
            raise ValueError(f"Invalid SFEN: {e}")
        
        # Create puzzle entry
        puzzle = {
            "sfen": sfen,
            "name": name or f"Puzzle {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": description,
            "author": author,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
        }
        
        # Load existing puzzles
        puzzles = self.load_all_puzzles()
        
        # Add new puzzle
        puzzles.append(puzzle)
        
        # Save to file
        with open(self.puzzle_file, 'w', encoding='utf-8') as f:
            json.dump(puzzles, f, indent=2, ensure_ascii=False)
        
        return puzzle
    
    def load_all_puzzles(self) -> List[Dict[str, Any]]:
        """
        Load all puzzles from storage.
        
        Returns:
            List of puzzle dictionaries
        """
        if not self.puzzle_file.exists():
            return []
        
        try:
            with open(self.puzzle_file, 'r', encoding='utf-8') as f:
                puzzles = json.load(f)
                return puzzles if isinstance(puzzles, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_puzzle(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific puzzle by index.
        
        Args:
            index: Puzzle index (0-based)
            
        Returns:
            Puzzle dictionary or None if not found
        """
        puzzles = self.load_all_puzzles()
        if 0 <= index < len(puzzles):
            return puzzles[index]
        return None
    
    def delete_puzzle(self, index: int) -> bool:
        """
        Delete a puzzle by index.
        
        Args:
            index: Puzzle index (0-based)
            
        Returns:
            True if deleted, False if not found
        """
        puzzles = self.load_all_puzzles()
        if 0 <= index < len(puzzles):
            puzzles.pop(index)
            with open(self.puzzle_file, 'w', encoding='utf-8') as f:
                json.dump(puzzles, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def count_puzzles(self) -> int:
        """
        Get the number of stored puzzles.
        
        Returns:
            Number of puzzles
        """
        return len(self.load_all_puzzles())
    
    def search_puzzles(self, query: str = "", tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search puzzles by name, description, author, or tags.
        
        Args:
            query: Search query string
            tags: List of tags to filter by
            
        Returns:
            List of matching puzzles
        """
        puzzles = self.load_all_puzzles()
        results = []
        
        query_lower = query.lower()
        
        for puzzle in puzzles:
            # Check query match
            if query:
                if (query_lower in puzzle.get('name', '').lower() or
                    query_lower in puzzle.get('description', '').lower() or
                    query_lower in puzzle.get('author', '').lower()):
                    results.append(puzzle)
                    continue
            
            # Check tag match
            if tags:
                puzzle_tags = puzzle.get('tags', [])
                if any(tag in puzzle_tags for tag in tags):
                    results.append(puzzle)
                    continue
            
            # If no filters, include all
            if not query and not tags:
                results.append(puzzle)
        
        return results
