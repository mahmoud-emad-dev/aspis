#!/usr/bin/env python3
"""Shared config + path access for the hook scripts.

All hook rules are data: ``.aspis/config/hooks.yaml`` (secrets, junk, protected
paths) and ``.aspis/config/commit-convention.yaml`` (commit style). This module is
the one place that locates the brain and loads those files, so each hook stays a
thin consumer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:  # PyYAML ships with aspis; the installed hook wrapper runs that interpreter.
    import yaml
except ImportError:  # pragma: no cover - degraded mode
    yaml = None  # type: ignore[assignment]


def load_yaml(path: Path) -> dict[str, Any]:
    """Parse a YAML file, returning ``{}`` when it is missing or unparseable."""
    if yaml is None or not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def hooks_config(root: Path) -> dict[str, Any]:
    """The hook rule data (secrets, junk, protected paths)."""
    return load_yaml(root / ".aspis" / "config" / "hooks.yaml")


def commit_convention(root: Path) -> dict[str, Any]:
    """The commit-message convention (the single source for commit style)."""
    return load_yaml(root / ".aspis" / "config" / "commit-convention.yaml")


def active_feature(root: Path) -> dict[str, Any]:
    """The active-feature pointer, or ``{}`` when none is set."""
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        return {}
    try:
        return json.loads(pointer.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
