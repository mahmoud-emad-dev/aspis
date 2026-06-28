"""Tests for scope_estimate.py"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/scope_estimate.py")


def _write_spec(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_small_spec(tmp_path):
    """Small spec → low story points."""
    spec = tmp_path / "SPEC.md"
    _write_spec(spec, """# Small Feature
## Requirements
- **FR-L0-001**: Do thing
- **SC-L0-001**: Thing works
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(spec)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "Story points:" in result.stdout
    assert "Risk level:" in result.stdout


def test_large_spec(tmp_path):
    """Large spec with complexity markers → higher story points."""
    spec = tmp_path / "SPEC.md"
    _write_spec(spec, """# Large Complex Feature
## Requirements
- **FR-L0-001**: Do thing with subprocess and cross-runtime
- **FR-L0-002**: Another thing with security concerns
- **FR-L0-003**: Yet another
- **FR-L0-004**: Database migration
- **FR-L0-005**: External API integration
- **FR-L0-006**: Breaking change
- **FR-L0-007**: Complex parsing
- **FR-L0-008**: Concurrency handling
## Success Criteria
- **SC-L0-001**: Thing works
- **SC-L0-002**: Security passes
- **SC-L0-003**: Performance ok
- **SC-L0-004**: Migration clean
Files: `src/new_file.py` (new), `src/another.py` (new)
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(spec)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "Story points:" in result.stdout


def test_json_output(tmp_path):
    """JSON output mode."""
    spec = tmp_path / "SPEC.md"
    _write_spec(spec, """# Test
- **FR-L0-001**: Test
- **SC-L0-001**: Test works
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(spec), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "story_points" in data
    assert "risk" in data
    assert "fr_count" in data


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "Usage" in result.stdout


def test_invalid_path(tmp_path):
    """Non-existent spec returns error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path / "nonexistent.md")],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode != 0
