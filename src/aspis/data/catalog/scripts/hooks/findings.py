#!/usr/bin/env python3
"""Project findings store — a small JSON list at ``.aspis/current/findings.json``.

A deterministic guard that detects a wrong state **emits** a finding here; the next agent's
``aspis preflight`` surfaces it so it is resolved or routed before work continues. Stdlib-only,
so catalog scripts (the runtime guard, the git hooks) can emit without the ``aspis`` package.
The JSON-list shape is the shared contract — the package side (``aspis findings`` / preflight)
reads the same file.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


def _store(root: Path) -> Path:
    return root / ".aspis" / "current" / "findings.json"


def load(root: Path) -> list[dict]:
    """Open findings (empty list if none, missing, or unreadable)."""
    path = _store(root)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return data if isinstance(data, list) else []


def emit(root: Path, kind: str, detail: str, source: str = "guard") -> None:
    """Record a finding (deduped on kind+detail). Best-effort — never raises."""
    try:
        items = load(root)
        if any(f.get("kind") == kind and f.get("detail") == detail for f in items):
            return
        items.append(
            {
                "kind": kind,
                "detail": detail,
                "source": source,
                "ts": datetime.now(UTC).isoformat(timespec="seconds"),
            }
        )
        path = _store(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return
