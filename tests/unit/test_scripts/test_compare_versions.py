"""Tests for compare_versions.py"""
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/research/compare_versions.py")


def test_major_diff():
    """2.0.0 is newer than 1.0.0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0", "2.0.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "2.0.0" in result.stdout  # newer
    assert "major" in result.stdout.lower()


def test_minor_diff():
    """1.2.0 is newer than 1.0.0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0", "1.2.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "minor" in result.stdout.lower()


def test_patch_diff():
    """1.0.2 is newer than 1.0.0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0", "1.0.2"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "patch" in result.stdout.lower()


def test_equal():
    """Same versions are equal."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0", "1.0.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "equal" in result.stdout.lower()


def test_prerelease():
    """1.0.0-rc1 vs 1.0.0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0-rc.1", "1.0.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    # 1.0.0 (release) is newer than 1.0.0-rc.1
    assert "1.0.0" in result.stdout


def test_invalid():
    """Invalid version should report error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "not.a.version", "1.0.0"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode != 0 or "Error" in result.stdout


def test_json_output():
    """JSON output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "1.0.0", "2.0.0", "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["newer"] == "2.0.0"
    assert data["diff_type"] == "major"


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
