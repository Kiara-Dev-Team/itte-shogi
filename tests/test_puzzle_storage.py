"""Tests for puzzle storage."""

import os
import json
import tempfile
import pytest
from pathlib import Path
from shogi_mate1.puzzles.storage import PuzzleStorage


def test_puzzle_storage_init():
    """Test puzzle storage initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        assert storage.storage_dir == Path(tmpdir)
        assert storage.storage_dir.exists()


def test_save_and_load_puzzle():
    """Test saving and loading puzzles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        # Save a puzzle
        sfen = "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
        puzzle = storage.save_puzzle(
            sfen=sfen,
            name="Test Puzzle",
            description="A test puzzle",
            author="Test Author",
            tags=["test", "example"]
        )
        
        assert puzzle["sfen"] == sfen
        assert puzzle["name"] == "Test Puzzle"
        assert puzzle["author"] == "Test Author"
        assert "test" in puzzle["tags"]
        
        # Load all puzzles
        puzzles = storage.load_all_puzzles()
        assert len(puzzles) == 1
        assert puzzles[0]["sfen"] == sfen


def test_save_invalid_sfen():
    """Test that saving invalid SFEN raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        with pytest.raises(ValueError):
            storage.save_puzzle(sfen="invalid sfen format")


def test_get_puzzle():
    """Test getting a specific puzzle by index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        # Save multiple puzzles
        storage.save_puzzle("7gk/7pg/8R/9/9/9/9/9/4K4 b - 1", "Puzzle 1")
        storage.save_puzzle("3gkg3/3sps3/4R4/9/9/9/9/9/4K4 b - 1", "Puzzle 2")
        
        # Get specific puzzle
        puzzle = storage.get_puzzle(0)
        assert puzzle["name"] == "Puzzle 1"
        
        puzzle = storage.get_puzzle(1)
        assert puzzle["name"] == "Puzzle 2"
        
        # Get non-existent puzzle
        puzzle = storage.get_puzzle(999)
        assert puzzle is None


def test_delete_puzzle():
    """Test deleting a puzzle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        # Save puzzles
        storage.save_puzzle("7gk/7pg/8R/9/9/9/9/9/4K4 b - 1", "Puzzle 1")
        storage.save_puzzle("3gkg3/3sps3/4R4/9/9/9/9/9/4K4 b - 1", "Puzzle 2")
        
        assert storage.count_puzzles() == 2
        
        # Delete first puzzle
        result = storage.delete_puzzle(0)
        assert result is True
        assert storage.count_puzzles() == 1
        
        # Remaining puzzle should be "Puzzle 2"
        puzzle = storage.get_puzzle(0)
        assert puzzle["name"] == "Puzzle 2"
        
        # Try to delete non-existent puzzle
        result = storage.delete_puzzle(999)
        assert result is False


def test_count_puzzles():
    """Test counting puzzles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        assert storage.count_puzzles() == 0
        
        storage.save_puzzle("7gk/7pg/8R/9/9/9/9/9/4K4 b - 1")
        assert storage.count_puzzles() == 1
        
        storage.save_puzzle("3gkg3/3sps3/4R4/9/9/9/9/9/4K4 b - 1")
        assert storage.count_puzzles() == 2


def test_search_puzzles():
    """Test searching puzzles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        # Save puzzles with different attributes
        storage.save_puzzle(
            "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1",
            name="Corner Mate",
            author="Alice",
            tags=["beginner", "corner"]
        )
        storage.save_puzzle(
            "3gkg3/3sps3/4R4/9/9/9/9/9/4K4 b - 1",
            name="Template Position",
            author="Bob",
            tags=["advanced", "template"]
        )
        storage.save_puzzle(
            "4k4/9/9/9/9/9/9/9/4K4 b R 1",
            name="Corner Drop",
            author="Alice",
            tags=["beginner", "drop"]
        )
        
        # Search by name
        results = storage.search_puzzles(query="corner")
        assert len(results) == 2
        assert all("corner" in r["name"].lower() or "corner" in r.get("tags", []) for r in results)
        
        # Search by author
        results = storage.search_puzzles(query="bob")
        assert len(results) == 1
        assert results[0]["author"] == "Bob"
        
        # Search by tag only
        results = storage.search_puzzles(tags=["beginner"])
        assert len(results) == 2
        assert all("beginner" in r.get("tags", []) for r in results)
        
        # Search with both query and tags (AND logic)
        results = storage.search_puzzles(query="corner", tags=["beginner"])
        assert len(results) == 2  # Both "Corner Mate" and "Corner Drop" match
        
        # Search with query that doesn't match any beginner tags
        results = storage.search_puzzles(query="template", tags=["beginner"])
        assert len(results) == 0  # Template Position is advanced, not beginner
        
        # Get all (no filters)
        results = storage.search_puzzles()
        assert len(results) == 3


def test_puzzle_default_name():
    """Test that puzzles get default names if not provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = PuzzleStorage(tmpdir)
        
        puzzle = storage.save_puzzle("7gk/7pg/8R/9/9/9/9/9/4K4 b - 1")
        
        # Should have auto-generated name with timestamp
        assert "Puzzle" in puzzle["name"]
        assert puzzle["name"] != ""


def test_puzzle_persistence():
    """Test that puzzles persist across storage instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and save with first instance
        storage1 = PuzzleStorage(tmpdir)
        storage1.save_puzzle("7gk/7pg/8R/9/9/9/9/9/4K4 b - 1", "Test")
        
        # Load with second instance
        storage2 = PuzzleStorage(tmpdir)
        puzzles = storage2.load_all_puzzles()
        
        assert len(puzzles) == 1
        assert puzzles[0]["name"] == "Test"
