"""Tests for rank_source.py"""
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/research/rank_source.py")


def test_ranking():
    """Sources should be ranked by authority × freshness."""
    sources = json.dumps([
        {"url": "https://docs.python.org/3/", "authority_score": 10, "freshness_days": 30},
        {"url": "https://example.com/blog", "authority_score": 3, "freshness_days": 5},
        {"url": "https://old-docs.example.com", "authority_score": 8, "freshness_days": 500},
    ])
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--sources", sources],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    # The high-authority source should be first
    assert "docs.python.org" in result.stdout


def test_json_output():
    """JSON output should be parseable."""
    sources = json.dumps([
        {"url": "https://example.com", "authority_score": 5, "freshness_days": 10},
    ])
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--sources", sources, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert "composite_score" in data[0]
    assert "tier" in data[0]


def test_stdin_input():
    """Should read from stdin when no --sources."""
    sources = json.dumps([
        {"url": "https://test.com", "authority_score": 7, "freshness_days": 20},
    ])
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--json"],
        input=sources, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
