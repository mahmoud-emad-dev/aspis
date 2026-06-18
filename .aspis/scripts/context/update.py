#!/usr/bin/env python3
"""Run all context updaters — the single entry hooks/agents/bootstrap call.

Self-contained (stdlib only). This is pure orchestration: it invokes each
updater in turn so the project's brain is refreshed in one call. Add an updater
to ``_UPDATERS`` to include it.

Usage: python3 update.py [project_root]
"""

from __future__ import annotations

import sys
from pathlib import Path

import build_code_map
import build_registry
import build_state
import record_changes

# Updaters run in order; each exposes ``main(argv)``.
_UPDATERS = (build_registry, build_state, record_changes, build_code_map)


def main(argv: list[str] | None = None) -> int:
    """Refresh every context file for the given (or current) project root."""
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path.cwd()
    for updater in _UPDATERS:
        updater.main([str(root)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
