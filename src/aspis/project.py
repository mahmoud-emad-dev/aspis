"""Project-layer helpers: identifying an ASPIS project.

A directory is an ASPIS project when it contains the brain folder (``.asps/``) —
the durable, tool-neutral memory for that project. Keeping this in one place
means every command agrees on what "a project" means.
"""

from __future__ import annotations

from pathlib import Path

from aspis.constants import BRAIN_DIR


def is_project(root: Path) -> bool:
    """Return True if ``root`` contains an ASPIS brain folder."""
    return (root / BRAIN_DIR).is_dir()
