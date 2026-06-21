"""Runtime inventory — the per-machine record of what each runtime can actually run.

Detection is per-runtime (each adapter's ``detect()``); this module is the
orchestrator that asks every installed runtime and persists the combined answer to
a single generated file, ``.aspis/state/runtime_inventory.json``. The file is a
derived artifact (Constitution #8): gitignored, never hand-edited, rebuilt on demand
by ``aspis doctor``. The resolver reads it to emit only model strings the machine
can run, and degrades gracefully (to today's tier map) when it is absent.

Responsibilities: build the inventory from ``detect_all()`` and write it; load it
back. Does NOT: detect (that is each adapter), route models (that is ``models.py``).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.runtimes import detect_all
from aspis.runtimes.base import RuntimeInventory

#: Generated inventory path, relative to a project root.
INVENTORY_REL = f"{BRAIN_DIR}/state/runtime_inventory.json"


def _inventory_path(root: Path) -> Path:
    return Path(root) / INVENTORY_REL


def build_inventory(root: Path, *, write: bool = True) -> dict[str, RuntimeInventory]:
    """Detect every installed runtime and (optionally) persist the combined inventory.

    Returns the ``{runtime: RuntimeInventory}`` map for installed runtimes. When
    *write* is set, also writes the generated JSON, creating ``.aspis/state/`` as needed.
    """
    found = detect_all()
    if write:
        path = _inventory_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_to_json(found), encoding="utf-8")
    return found


def load_inventory(root: Path) -> dict[str, RuntimeInventory] | None:
    """Read the generated inventory back, or ``None`` when it is absent/unreadable.

    ``None`` means "detection has not run here" — callers fall back to the tier map,
    so a fresh checkout works before ``aspis doctor`` is ever run (FR-006).
    """
    path = _inventory_path(root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError, ValueError):
        return None
    result: dict[str, RuntimeInventory] = {}
    for name, entry in (data.get("runtimes") or {}).items():
        result[name] = RuntimeInventory(
            runtime=name,
            installed=bool(entry.get("installed")),
            providers=tuple(entry.get("providers") or ()),
            models=tuple(entry.get("models") or ()),
        )
    return result


def _to_json(found: dict[str, RuntimeInventory]) -> str:
    payload = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "runtimes": {
            name: {
                "installed": inv.installed,
                "providers": list(inv.providers),
                "models": list(inv.models),
            }
            for name, inv in found.items()
        },
    }
    return json.dumps(payload, indent=2) + "\n"
