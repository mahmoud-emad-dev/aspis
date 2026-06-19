#!/usr/bin/env python3
"""Write ``.aspis/context/RECENT_CHANGES.md`` — recent commits, newest first.

Self-contained (stdlib only). The auto block is a short reverse-chronological
list pulled from ``git log``; manual notes outside the markers are preserved.

Usage: python3 record_changes.py [project_root]
"""

from __future__ import annotations

import sys
from pathlib import Path

import _common

# How many recent commits to list.
LIMIT = 15


def run(root: Path) -> Path:
    """Regenerate RECENT_CHANGES.md's auto block; return the file path."""
    log = _common.git(root, "log", f"-{LIMIT}", "--pretty=- `%h` %s — %ad", "--date=short")
    body = "## Recent changes\n\n" + (log if log else "_no commits yet_")

    target = root / ".aspis" / "context" / "RECENT_CHANGES.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_common.render_auto_block(target, body), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    """Run the updater against the given (or current) project root."""
    _common.force_utf8_stdio()
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path.cwd()
    target = run(root)
    print(f"wrote {target.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
