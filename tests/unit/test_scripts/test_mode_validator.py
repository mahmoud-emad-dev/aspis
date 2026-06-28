"""Tests for mode_validator.py"""
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/mode_validator.py")


def test_valid_mode():
    """Passing a valid mode should return PASS."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--mode", "production"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_invalid_mode():
    """Invalid mode should return FAIL."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--mode", "invalid_mode"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode != 0
    assert "FAIL" in result.stdout


def test_mvp_mode():
    """MVP mode should validate."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--mode", "mvp"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_vibe_mode():
    """Vibe mode should validate."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--mode", "vibe"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0


def test_json_output():
    """JSON output mode."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--mode", "production", "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    import json
    data = json.loads(result.stdout)
    assert data["verdict"] == "PASS"
    assert data["mode"] == "production"


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
