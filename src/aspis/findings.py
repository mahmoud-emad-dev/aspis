"""Read and resolve the project findings store (``.aspis/current/findings.json``).

The package side of the findings flow: deterministic guards (e.g. the runtime scope-guard, see
``data/catalog/scripts/hooks/findings.py``) emit findings; ``aspis preflight`` surfaces them and
``aspis findings`` lists/resolves them. The JSON-list shape is the shared contract.
"""

from __future__ import annotations

import json
from pathlib import Path


def store_path(root: Path) -> Path:
    return root / ".aspis" / "current" / "findings.json"


def load(root: Path) -> list[dict]:
    """Open findings (empty list if none, missing, or unreadable)."""
    path = store_path(root)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write(root: Path, items: list[dict]) -> None:
    store_path(root).write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")


def clear(root: Path) -> int:
    """Resolve every finding; return how many were cleared."""
    items = load(root)
    if store_path(root).is_file():
        _write(root, [])
    return len(items)


def resolve(root: Path, index: int) -> dict | None:
    """Resolve the finding at 1-based *index*; return it, or None if out of range."""
    items = load(root)
    if not 1 <= index <= len(items):
        return None
    removed = items.pop(index - 1)
    _write(root, items)
    return removed
