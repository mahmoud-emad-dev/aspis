"""Lightweight, deterministic project detection used by init and bootstrap.

Distinguishes a fresh/empty target from an existing-code project (they follow
different workflows) and identifies the stack from marker files.
"""

from __future__ import annotations

from pathlib import Path

from aspis.constants import BRAIN_DIR

# Ignored when deciding whether a directory is "empty" for ASPIS purposes.
_IGNORED = {".git", BRAIN_DIR, ".opencode", ".claude"}

# Marker files that identify a project's stack (first match wins).
_STACK_MARKERS = [
    ("pyproject.toml", "python"),
    ("package.json", "node"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
]


def project_mode(root: Path) -> str:
    """Return 'empty' if *root* has no project content yet, else 'existing'."""
    if not root.is_dir():
        return "empty"
    for child in root.iterdir():
        if child.name not in _IGNORED:
            return "existing"
    return "empty"


def detect_stack(root: Path) -> str:
    """Return the project's stack from marker files, or 'unknown'."""
    for marker, stack in _STACK_MARKERS:
        if (root / marker).exists():
            return stack
    return "unknown"
