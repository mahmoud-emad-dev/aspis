#!/usr/bin/env python3
"""Shared config + path access for the hook scripts.

All hook rules are data: ``.aspis/config/hooks.yaml`` (secrets, junk, protected
paths) and ``.aspis/config/commit-convention.yaml`` (commit style). This module is
the one place that locates the brain and loads those files, so each hook stays a
thin consumer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:  # PyYAML ships with aspis; the installed hook wrapper runs that interpreter.
    import yaml
except ImportError:  # pragma: no cover - degraded mode
    yaml = None  # type: ignore[assignment]


def force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (mirrors ``aspis.cli``).

    Best-effort: streams without ``reconfigure`` are left untouched. Keeps a hook
    from crashing when it prints a non-ASCII character under a cp1252 console.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def load_yaml(path: Path) -> dict[str, Any]:
    """Parse a YAML file, returning ``{}`` when it is missing or unparseable."""
    if yaml is None or not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


#: Config is tiered: a few files sit flat in ``config/``; policy files live in
#: ``config/policy/``. Search flat first (legacy/tier-1), then the tier subfolders —
#: so a hook finds its rule file by bare name regardless of layout.
_CONFIG_SUBDIRS = ("", "policy", "reference")


def config_yaml(root: Path, name: str) -> dict[str, Any]:
    """Load ``.aspis/config/<name>`` (or its tier subfolder), ``{}`` if absent."""
    base = root / ".aspis" / "config"
    for sub in _CONFIG_SUBDIRS:
        candidate = base / sub / name if sub else base / name
        if candidate.is_file():
            return load_yaml(candidate)
    return {}


def hooks_config(root: Path) -> dict[str, Any]:
    """The hook rule data (secrets, junk, protected paths)."""
    return config_yaml(root, "hooks.yaml")


def enforcement(root: Path) -> str:
    """Enforcement mode: ``"warn"`` (never blocks, the default) or ``"block"``."""
    return str(hooks_config(root).get("enforcement") or "warn").lower()


def blocks(root: Path) -> bool:
    """True only when the project has opted into hard blocking."""
    return enforcement(root) == "block"


def commit_convention(root: Path) -> dict[str, Any]:
    """The commit-message convention (the single source for commit style)."""
    return config_yaml(root, "commit-convention.yaml")


def active_feature(root: Path) -> dict[str, Any]:
    """The active-feature pointer, or ``{}`` when none is set."""
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        return {}
    try:
        return json.loads(pointer.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
