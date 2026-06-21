"""Detect which agent-runtime CLIs are available on this machine (F-013, P1).

Presence only — which executables are on ``PATH``. No session access, no chat
access, no project scanning, no tracing. The result is cached to the data home
as ``runtime-inventory.yaml`` so ``aspis doctor --verbose`` (and, later, the
installer summary) can answer "what can this machine actually run".
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from aspis import paths

#: Known agent-runtime CLIs: display name -> the executable looked up on PATH.
KNOWN_RUNTIMES: dict[str, str] = {
    "claude": "claude",
    "opencode": "opencode",
    "cursor": "cursor",
    "gemini": "gemini",
    "codex": "codex",
}


def detect_runtimes() -> dict[str, str | None]:
    """Map each known runtime to its resolved executable path, or ``None`` if absent."""
    return {name: shutil.which(exe) for name, exe in KNOWN_RUNTIMES.items()}


def available(detected: dict[str, str | None] | None = None) -> list[str]:
    """The names of the runtimes that are present, sorted."""
    found = detect_runtimes() if detected is None else detected
    return sorted(name for name, path in found.items() if path)


def inventory_path() -> Path:
    """Where the cached inventory lives (under the data home)."""
    return paths.data_home() / "runtime-inventory.yaml"


def save_inventory(detected: dict[str, str | None] | None = None) -> Path:
    """Write the detected inventory to the data home; return the file path."""
    found = detect_runtimes() if detected is None else detected
    path = inventory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "runtimes": {name: {"available": bool(p), "path": p} for name, p in sorted(found.items())},
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
    return path
