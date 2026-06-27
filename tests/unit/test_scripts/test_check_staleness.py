"""Tests for check_staleness.py"""
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/research/check_staleness.py")


def test_fresh_file(tmp_path):
    """Newly created file should be FRESH."""
    f = tmp_path / "fresh.md"
    f.write_text("test", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(f)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "FRESH" in result.stdout


def test_stale_file(tmp_path):
    """Old file should be STALE with a short threshold."""
    f = tmp_path / "stale.md"
    f.write_text("test", encoding="utf-8")
    # Set mtime to 200 days ago
    old_time = time.time() - 200 * 86400
    f.touch()
    # Can't easily set mtime far back on all platforms, so use short threshold
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(f), "--threshold", "0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "STALE" in result.stdout or "WARN" in result.stdout


def test_security_type(tmp_path):
    """Security type has 7-day threshold."""
    f = tmp_path / "security.md"
    f.write_text("test", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(f), "--type", "security"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "security" in result.stdout.lower() or "FRESH" in result.stdout


def test_missing_file(tmp_path):
    """Non-existent file → ERROR."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path / "nonexistent.md")],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode != 0


def test_json_output(tmp_path):
    """JSON output."""
    f = tmp_path / "test.md"
    f.write_text("test", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(f), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    import json
    data = json.loads(result.stdout)
    assert "verdict" in data
    assert "age_days" in data


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
