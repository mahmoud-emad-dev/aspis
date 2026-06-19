"""Shared helpers for the self-contained context-update scripts.

Standard library only. These scripts ship into a project's
``.aspis/scripts/context/`` and run with the project's own Python — no global
``aspis`` dependency. A sibling script imports this module directly, because
Python puts the running script's directory on ``sys.path``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (mirrors ``aspis.cli``).

    Best-effort: streams without ``reconfigure`` (e.g. a test capture buffer) are
    left untouched. Keeps these standalone scripts from crashing when they print a
    non-ASCII character (an arrow, a check mark) under a cp1252 console (Windows).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


# Markers bounding the regenerated block; anything outside them is preserved.
AUTO_START = "<!-- ASPIS:auto START -->"
AUTO_END = "<!-- ASPIS:auto END -->"

# Marker files that identify a project's stack (first match wins).
_STACK_MARKERS = [
    ("pyproject.toml", "python"),
    ("package.json", "node"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
]


def git(root: Path, *args: str) -> str:
    """Run a read-only git command in *root*; return stripped stdout ('' on failure)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def detect_stack(root: Path) -> str:
    """Return the project's stack from marker files, or 'unknown'."""
    for marker, stack in _STACK_MARKERS:
        if (root / marker).exists():
            return stack
    return "unknown"


def render_auto_block(path: Path, body: str) -> str:
    """Return *path*'s content with the ASPIS auto block set to *body*.

    If the markers are present, only the block between them is replaced (manual
    content is preserved). If the file exists without markers, the block is
    prepended above the existing content. Otherwise a new block is created.
    """
    block = f"{AUTO_START}\n{body}\n{AUTO_END}"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            before = text.split(AUTO_START)[0]
            after = text.split(AUTO_END, 1)[1]
            return f"{before}{block}{after}"
        return f"{block}\n\n{text}"
    return f"{block}\n"
