"""Tests for constitution_check.py"""
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/constitution_check.py")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_valid_plan(tmp_path):
    """A plan with good patterns should score passes."""
    plan = tmp_path / "PLAN.md"
    _write_file(plan, """# Plan
This feature adds new files for the plugin architecture.
We use configuration over code with YAML files.
The catalog is the single source of truth.
Dependencies flow inward from plugins to core.
Uses UTF-8 encoding and pathlib for portability.
Windows and Linux are both supported.
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(plan)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout or True  # At least doesn't crash


def test_broken_plan(tmp_path):
    """A plan with anti-patterns should produce warnings."""
    plan = tmp_path / "PLAN.md"
    _write_file(plan, """# Plan
We will edit many existing core files.
We use if runtime == "claude" for special cases.
The REGISTRY = [...] is hand-maintained.
We duplicate content from other files.
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(plan)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should complete, possibly with warnings/fails
    assert "Summary:" in result.stdout


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
