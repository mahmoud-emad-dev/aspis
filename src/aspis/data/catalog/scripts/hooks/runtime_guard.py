#!/usr/bin/env python3
"""Runtime scope-guard — block an out-of-scope Edit/Write at the tool boundary (FR-008/9).

Wired by both runtimes and reusing the one ``scope`` decision:
  - Claude `PreToolUse` passes the tool input as JSON on stdin; exit code 2 blocks.
  - OpenCode's plugin passes the path(s) as argv and throws on a non-zero exit.

Only needs ``active_feature.json`` (stdlib JSON), so it runs under a bare ``python3``
with no third-party dependency.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git  # noqa: E402
import scope  # noqa: E402


def _paths_from_stdin() -> list[str]:
    """Extract the edited path from a Claude PreToolUse payload on stdin."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return []
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("filePath") or tool_input.get("path")
    return [path] if path else []


def _relative(path: str, root: Path) -> str:
    """Best-effort repo-relative form of *path* for glob matching."""
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except (ValueError, OSError):
        return path


def main() -> int:
    """Exit 2 (block) if any target path is outside the active feature's scope."""
    root = _git.repo_root()
    paths = list(sys.argv[1:]) or _paths_from_stdin()
    blocked = [p for p in paths if p and not scope.in_scope(_relative(p, root), root)]
    for path in blocked:
        print(f"[aspis] blocked out-of-scope edit: {path}", file=sys.stderr)
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
