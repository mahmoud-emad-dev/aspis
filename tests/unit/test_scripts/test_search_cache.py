"""Tests for search_cache.py"""
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/research/search_cache.py")


def test_add_and_lookup(tmp_path):
    """Add an entry, then look it up."""
    cache = tmp_path / "cache.json"
    # Add
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache),
         "--add", "test query", "test result"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0

    # Lookup
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache),
         "--lookup", "test query"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "HIT" in result.stdout
    assert "test result" in result.stdout


def test_lookup_miss(tmp_path):
    """Look up non-existent entry."""
    cache = tmp_path / "cache.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache),
         "--lookup", "nonexistent"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "MISS" in result.stdout or result.returncode != 0


def test_stats(tmp_path):
    """Get cache stats."""
    cache = tmp_path / "cache.json"
    # Add some entries first
    subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache),
         "--add", "q1", "r1"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache), "--stats"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "Total entries:" in result.stdout


def test_clear(tmp_path):
    """Clear cache."""
    cache = tmp_path / "cache.json"
    # Add then clear
    subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache),
         "--add", "q1", "r1"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache), "--clear"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    # Verify it's cleared
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--cache", str(cache), "--stats"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "Total entries:       0" in result.stdout


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
