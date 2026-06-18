#!/usr/bin/env python3
"""Write ``.asps/context/CURRENT_STATE.md`` — a snapshot of the project now.

Self-contained (stdlib only). The auto block (project, stack, branch, last
commit) is regenerated; any manual notes outside the markers are preserved.

Usage: python3 build_state.py [project_root]
"""

from __future__ import annotations

import sys
from pathlib import Path

import _common


def run(root: Path) -> Path:
    """Regenerate CURRENT_STATE.md's auto block; return the file path."""
    stack = _common.detect_stack(root)
    branch = _common.git(root, "rev-parse", "--abbrev-ref", "HEAD") or "(no git)"
    last_commit = _common.git(root, "log", "-1", "--pretty=%h %s") or "(no commits)"

    body = "\n".join(
        [
            "## Current state",
            "",
            f"- **Project:** {root.name}",
            f"- **Stack:** {stack}",
            f"- **Branch:** {branch}",
            f"- **Last commit:** {last_commit}",
        ]
    )

    target = root / ".asps" / "context" / "CURRENT_STATE.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_common.render_auto_block(target, body), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    """Run the updater against the given (or current) project root."""
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path.cwd()
    target = run(root)
    print(f"wrote {target.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
