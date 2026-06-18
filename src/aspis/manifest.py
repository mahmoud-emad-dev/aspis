"""The project manifest — ``.aspis/manifest.json``.

The durable signal that a project has been bootstrapped, plus the recorded
project state. JSON (stdlib) so it is trivially read/written anywhere.
"""

from __future__ import annotations

import json
from pathlib import Path

from aspis.constants import BRAIN_DIR

#: Manifest location relative to a project root.
MANIFEST_REL = Path(BRAIN_DIR) / "manifest.json"


def manifest_path(root: Path) -> Path:
    """Return the manifest path for *root*."""
    return root / MANIFEST_REL


def load(root: Path) -> dict:
    """Return the manifest dict, or ``{}`` if absent/unreadable."""
    path = manifest_path(root)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save(root: Path, data: dict) -> Path:
    """Write *data* as the project manifest; return its path."""
    path = manifest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def is_bootstrapped(root: Path) -> bool:
    """Return True if the project has been bootstrapped."""
    return bool(load(root).get("bootstrapped"))
