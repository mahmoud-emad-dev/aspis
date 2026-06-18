"""Tests for the self-contained CODE_MAP builder script.

Runs the shipped script via subprocess, exactly as a project would, so the test
covers the real artifact (whole-project write + scoped stdout).
"""

from __future__ import annotations

import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "build_code_map.py"

SAMPLE = '''\
"""The app module."""

from pathlib import Path

MAX_SIZE = 10


def run(target: Path) -> int:
    """Do the thing."""
    return 0


def _private() -> None:
    """Hidden helper."""


class Engine:
    """Runs work."""

    def start(self) -> None:
        """Begin."""
'''


def _project(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(SAMPLE, encoding="utf-8")
    return tmp_path


def test_whole_project_writes_code_map(tmp_path) -> None:
    _project(tmp_path)
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    code_map = (tmp_path / ".aspis" / "index" / "CODE_MAP.md").read_text(encoding="utf-8")
    assert "The app module." in code_map
    assert "from pathlib import Path" in code_map  # imports captured
    assert "def run(target: Path) -> int" in code_map  # public signature
    assert "constants: `MAX_SIZE`" in code_map
    assert "class Engine" in code_map and "def start(self) -> None" in code_map
    assert "_private" not in code_map  # private helpers skipped


def test_scope_prints_single_file_to_stdout(tmp_path) -> None:
    _project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--scope", "src/app.py", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "def run(target: Path) -> int" in result.stdout
    assert not (tmp_path / ".aspis" / "index" / "CODE_MAP.md").exists()  # scope = print, no write
