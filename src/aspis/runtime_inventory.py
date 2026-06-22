"""Detect which agent-runtime CLIs are available on this machine (F-013, P1).

Presence only — which executables are on ``PATH``. No session access, no chat
access, no project scanning, no tracing. The set of runtimes and how to detect each
is **discovered** from ``data/runtimes/*.yaml`` (see :func:`aspis.resources.runtime_defs`),
never a hardcoded list — drop a runtime definition and it is detected automatically.
The result is cached to the data home as ``runtime-inventory.yaml`` so
``aspis doctor --verbose`` (and the installer summary) can answer "what can this
machine actually run", with each runtime's declared capabilities (mode, subagent
depth, exportable).
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from aspis import paths, resources


def _detect_exe(definition: dict, name: str) -> str:
    """The executable to look up for a runtime (its ``detect.exe``, default = name)."""
    return (definition.get("detect") or {}).get("exe", name)


def detect_runtimes() -> dict[str, str | None]:
    """Map each discovered runtime to its resolved executable path, or ``None`` if absent."""
    return {
        name: shutil.which(_detect_exe(definition, name))
        for name, definition in resources.runtime_defs().items()
    }


def available(detected: dict[str, str | None] | None = None) -> list[str]:
    """The names of the runtimes that are present, sorted."""
    found = detect_runtimes() if detected is None else detected
    return sorted(name for name, path in found.items() if path)


def capabilities(name: str) -> dict:
    """The declared capabilities for a runtime (mode, subagents, depth, exportable)."""
    return resources.runtime_def(name).get("capabilities") or {}


def inventory_path() -> Path:
    """Where the cached inventory lives (under the data home)."""
    return paths.data_home() / "runtime-inventory.yaml"


def save_inventory(detected: dict[str, str | None] | None = None) -> Path:
    """Write the detected inventory (path + declared capabilities) to the data home."""
    found = detect_runtimes() if detected is None else detected
    path = inventory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "runtimes": {
            name: {"available": bool(p), "path": p, "capabilities": capabilities(name)}
            for name, p in sorted(found.items())
        },
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
    return path
