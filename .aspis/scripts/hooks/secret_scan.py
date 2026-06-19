#!/usr/bin/env python3
"""Secret detection over the staged diff.

Patterns are data (``hooks.yaml: secrets``), so adding a rule never touches code.
Only added lines are scanned (a unified diff with zero context), keeping it fast.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _config  # noqa: E402
import _git  # noqa: E402


def find(diff_text: str, patterns: list[str]) -> list[str]:
    """Return the added lines that match any secret pattern."""
    compiled = [re.compile(p) for p in patterns]
    hits: list[str] = []
    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added = line[1:]
        if any(rx.search(added) for rx in compiled):
            hits.append(added.strip())
    return hits


def main() -> int:
    """Scan the staged diff; exit 1 if a secret-shaped line was added."""
    root = _git.repo_root()
    patterns = list(_config.hooks_config(root).get("secrets") or [])
    if not patterns:
        return 0
    hits = find(_git.staged_diff(), patterns)
    for line in hits:
        print(f"[aspis] possible secret in staged change: {line[:80]}", file=sys.stderr)
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
