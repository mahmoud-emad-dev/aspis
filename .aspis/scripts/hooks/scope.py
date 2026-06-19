#!/usr/bin/env python3
"""Scope decision — is a path allowed for the active feature? (FR-008)

One source of truth, reused by both the git ``pre-commit`` and the runtime
scope-guard. Scope is optional data on ``active_feature.json``::

    "scope": {"allowed": ["src/aspis/**", "tests/**"], "forbidden": ["rules/**"]}

Rules: a ``forbidden`` match always loses; an ``allowed`` list is enforced only
when it is non-empty (no list declared ⇒ everything is allowed, so the guard never
blocks a feature that has not opted in). Patterns are globs (``fnmatch``).
"""

from __future__ import annotations

import sys
from fnmatch import fnmatch
from pathlib import Path

if __package__ in (None, ""):  # run as a script: import siblings from this dir
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _config  # noqa: E402
import _git  # noqa: E402


def _scope(root: Path) -> tuple[list[str], list[str]]:
    """Return ``(allowed, forbidden)`` glob lists for the active feature."""
    scope = _config.active_feature(root).get("scope") or {}
    return list(scope.get("allowed") or []), list(scope.get("forbidden") or [])


def violations(files: list[str], root: Path) -> list[tuple[str, str]]:
    """Return ``(path, reason)`` for each file that is out of scope."""
    allowed, forbidden = _scope(root)
    out: list[tuple[str, str]] = []
    for path in files:
        hit = next((pat for pat in forbidden if fnmatch(path, pat)), None)
        if hit:
            out.append((path, f"matches forbidden pattern '{hit}'"))
            continue
        if allowed and not any(fnmatch(path, pat) for pat in allowed):
            out.append((path, "outside the feature's allowed paths"))
    return out


def in_scope(path: str, root: Path) -> bool:
    """True when a single *path* is within the active feature's scope."""
    return not violations([path], root)


if __name__ == "__main__":  # `python scope.py <path>...` → exit 1 if any out of scope
    root = _git.repo_root()
    bad = violations(sys.argv[1:] or _git.staged_files(), root)
    for path, reason in bad:
        print(f"[aspis] out of scope: {path} — {reason}", file=sys.stderr)
    raise SystemExit(1 if bad else 0)
