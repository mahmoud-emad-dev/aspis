#!/usr/bin/env python3
"""Thin wrappers over the ``git`` CLI shared by every hook script.

Stdlib only. Each function shells out once and returns plain Python values, so the
hook logic never parses git output inline.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run(args: list[str]) -> str:
    """Run ``git <args>`` and return stripped stdout (empty string on failure)."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def repo_root() -> Path:
    """Absolute path of the repository root (cwd if git is unavailable)."""
    root = _run(["rev-parse", "--show-toplevel"])
    return Path(root) if root else Path.cwd()


def staged_files() -> list[str]:
    """Repo-relative paths staged for the pending commit."""
    out = _run(["diff", "--cached", "--name-only"])
    return [line for line in out.splitlines() if line]


def deleted_files() -> list[str]:
    """Repo-relative paths staged for deletion."""
    out = _run(["diff", "--cached", "--name-only", "--diff-filter=D"])
    return [line for line in out.splitlines() if line]


def staged_diff() -> str:
    """Unified staged diff with zero context (just the added/removed lines)."""
    return _run(["diff", "--cached", "-U0"])


def unstage(paths: list[str]) -> None:
    """Remove *paths* from the index (used after auto-cleaning staged junk)."""
    if paths:
        subprocess.run(["git", "reset", "-q", "HEAD", "--", *paths], check=False)
