#!/usr/bin/env python3
"""Repo housekeeping — the one junk handler (FR-005).

Two idempotent jobs, both no-ops on an already-clean tree:

1. **Junk files** — shell-redirect ghosts (names beginning ``=``/``*``/``-`` or
   ending ``:``/``,``) and bare extensionless root words that are not on the keep
   list. Removed from disk (and unstaged if they were staged).
2. **Stale ``.gitkeep``** — once a folder holds a real file, its ``.gitkeep`` has
   done its job and is deleted.

Rules (prefixes, suffixes, keep list, skip dirs) are data in ``hooks.yaml``.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git  # noqa: E402
from _config import hooks_config  # noqa: E402

_BARE_WORD = re.compile(r"^[A-Za-z][A-Za-z-]*$")


@dataclass
class CleanResult:
    """What cleanup removed (empty lists ⇒ the tree was already clean)."""

    junk: list[str] = field(default_factory=list)
    gitkeep: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.junk or self.gitkeep)


def is_junk(path: str, rules: dict[str, Any]) -> bool:
    """True when *path*'s basename looks like a shell-redirect ghost."""
    base = Path(path).name
    if base in set(rules.get("keep") or []):
        return False
    prefixes = tuple(rules.get("ghost_prefixes") or [])
    suffixes = tuple(rules.get("ghost_suffixes") or [])
    if prefixes and base.startswith(prefixes):
        return True
    if suffixes and base.endswith(suffixes):
        return True
    # A bare extensionless word at the repo root is almost always a redirect ghost.
    return "/" not in path and "." not in base and bool(_BARE_WORD.match(base))


def clean(root: Path, files: list[str] | None = None) -> CleanResult:
    """Remove junk among *files* (default: staged) and stale ``.gitkeep`` tree-wide."""
    rules = hooks_config(root).get("junk") or {}
    result = CleanResult()

    for rel in files if files is not None else _git.staged_files():
        if is_junk(rel, rules):
            target = root / rel
            if target.is_file():
                target.unlink()
            result.junk.append(rel)
    _git.unstage(result.junk)

    skip = set(rules.get("skip_dirs") or [])
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        if ".gitkeep" in filenames and any(f != ".gitkeep" for f in filenames):
            keep = Path(dirpath) / ".gitkeep"
            keep.unlink()
            result.gitkeep.append(keep.relative_to(root).as_posix())
    return result


def main() -> int:
    """Clean the tree; always exit 0 (housekeeping never blocks)."""
    root = _git.repo_root()
    result = clean(root)
    for rel in result.junk:
        print(f"[aspis] removed junk file: {rel}")
    for rel in result.gitkeep:
        print(f"[aspis] removed stale .gitkeep: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
