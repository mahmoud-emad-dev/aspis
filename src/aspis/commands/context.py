"""``aspis context`` — refresh the project brain and print the L1 "hot" context in one call.

Mid-task (before any commit) the generated brain can be stale, and reading it otherwise means
several tool calls. This refreshes it — the same updaters the post-commit hook runs
(`.aspis/scripts/context/update.py`) — then prints the context an agent almost always needs:
current state, recent changes, and the active feature. One call yields fresh, token-efficient
hot context. This is L1 of the `context-ladder` skill.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from aspis.project import is_project

#: How many lines of RECENT_CHANGES to show (newest first) — keep it token-cheap.
_RECENT_LINES = 20


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``context`` verb."""
    parser = subparsers.add_parser(
        "context",
        help="Refresh the brain and print L1 hot context (state, recent changes, active feature).",
    )
    parser.add_argument("path", nargs="?", default=".", help="Project dir (default: current).")
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="Print the existing brain without regenerating it first.",
    )
    parser.set_defaults(func=_run)


def _refresh(root: Path) -> None:
    """Run the project's context updaters (best-effort; never raises)."""
    update_py = root / ".aspis" / "scripts" / "context" / "update.py"
    if not update_py.is_file():
        return
    subprocess.run(
        [sys.executable, str(update_py), str(root)],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _section(title: str, body: str) -> None:
    print(f"\n# {title}\n")
    print(body.rstrip() or "(none)")


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if not is_project(root):
        print("not an ASPIS project — run `aspis init` first.")
        return 1

    if not args.no_refresh:
        _refresh(root)

    context_dir = root / ".aspis" / "context"
    state = context_dir / "CURRENT_STATE.md"
    changes = context_dir / "RECENT_CHANGES.md"
    feature = root / ".aspis" / "current" / "active_feature.json"

    if state.is_file():
        _section("Current state", state.read_text(encoding="utf-8"))
    if changes.is_file():
        lines = changes.read_text(encoding="utf-8").splitlines()
        _section(f"Recent changes (top {_RECENT_LINES} lines)", "\n".join(lines[:_RECENT_LINES]))
    if feature.is_file():
        try:
            data = json.loads(feature.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            data = {}
        if data:
            phase, mode = data.get("phase", "?"), data.get("mode", "?")
            line = f"{data.get('id', '?')} — {data.get('title', '?')} ({phase}, {mode})"
            print(f"\n# Active feature\n\n{line} on '{data.get('branch', '?')}'")
    return 0
