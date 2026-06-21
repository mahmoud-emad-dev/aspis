"""Standard per-user install locations for ASPIS (F-013).

Resolves the OS-appropriate **config**, **data**, and **cache** directories so
ASPIS stores machine-wide state where users expect it — not in an arbitrary
folder. Resolution order, high to low:

1. ``ASPIS_HOME`` — overrides everything (used by tests and for relocation); all
   three dirs live under it.
2. The legacy ``~/.aspis`` — used when it already exists, so existing installs
   keep working after an upgrade.
3. The OS standard:
   * Linux/BSD: ``$XDG_CONFIG_HOME`` or ``~/.config/aspis``, ``$XDG_DATA_HOME`` or
     ``~/.local/share/aspis``, ``$XDG_CACHE_HOME`` or ``~/.cache/aspis``.
   * macOS: the same XDG dirs (developer-friendly and script-stable).
   * Windows: ``%APPDATA%\\ASPIS`` (config), ``%LOCALAPPDATA%\\ASPIS`` (data),
     ``%LOCALAPPDATA%\\ASPIS\\cache`` (cache).

The per-project brain (``<project>/.aspis``) is unrelated — that is project
state and always lives with the project.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP = "aspis"

#: The legacy machine-wide base used before F-013 adopted OS-standard dirs.
LEGACY_HOME = Path.home() / ".aspis"


def _override_home() -> Path | None:
    """``ASPIS_HOME`` when set — the single base for config/data/cache."""
    base = os.environ.get("ASPIS_HOME")
    return Path(base) if base else None


def _is_windows() -> bool:
    return sys.platform == "win32"


def config_home() -> Path:
    """The machine-wide config directory (where ``project.yaml`` lives)."""
    override = _override_home()
    if override is not None:
        return override / "config"
    if LEGACY_HOME.is_dir():
        return LEGACY_HOME / "config"
    if _is_windows():
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "ASPIS"
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / APP


def data_home() -> Path:
    """The machine-wide data directory (runtime inventory, persistent state)."""
    override = _override_home()
    if override is not None:
        return override / "data"
    if LEGACY_HOME.is_dir():
        return LEGACY_HOME / "data"
    if _is_windows():
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "ASPIS"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / APP


def cache_home() -> Path:
    """The machine-wide cache directory (regenerable, safe to delete)."""
    override = _override_home()
    if override is not None:
        return override / "cache"
    if LEGACY_HOME.is_dir():
        return LEGACY_HOME / "cache"
    if _is_windows():
        return data_home() / "cache"
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / APP


def all_locations() -> dict[str, Path]:
    """The resolved machine-wide locations, for display by ``aspis doctor --verbose``."""
    return {"config": config_home(), "data": data_home(), "cache": cache_home()}
