"""Locate files bundled inside the aspis package (templates, profiles, catalog).

One place resolves package data, so callers never hardcode paths. Uses
importlib.resources so it works both from a source checkout and an installed
wheel.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def data_dir() -> Path:
    """Return the path to the package's bundled ``data/`` directory."""
    return Path(str(files("aspis"))) / "data"


def template(name: str) -> str:
    """Return the text of a bundled template under ``data/templates/``."""
    return (data_dir() / "templates" / name).read_text(encoding="utf-8")
