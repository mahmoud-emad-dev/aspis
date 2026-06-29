"""``aspis stack`` — show or correct the project's stack (F-020).

Stack is not one-shot. Detection guesses it at bootstrap, but the user can confirm or
correct it any time (and later, as files reveal it). Setting normalises the value, records
it in the manifest with ``source: user``, and re-applies the project's ``.gitignore`` for
the new stack. With no value it shows the current stack and how it was determined.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aspis import detect, manifest, project
from aspis.constants import BRAIN_DIR
from aspis.operations._proc import run_quiet


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``stack`` verb."""
    parser = subparsers.add_parser("stack", help="Show or correct the project's stack.")
    parser.add_argument(
        "value", nargs="?", help="New stack (e.g. 'python, fastapi'); omit to show."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    data = manifest.load(root)
    if not args.value:
        current = data.get("stack") or detect.detect_stack(root)
        source = data.get("stack_source", "detected")
        print(f"stack: {current} ({source})")
        return 0

    normalized = detect.normalize_stack(args.value) or "unknown"
    data["stack"] = normalized
    data["stack_source"] = "user"
    manifest.save(root, data)
    print(f"stack set: {normalized}")

    gitignore = root / BRAIN_DIR / "scripts" / "hooks" / "gitignore.py"
    if normalized != "unknown" and gitignore.is_file():
        run_quiet([sys.executable, str(gitignore), normalized], cwd=root)
        print("re-applied .gitignore for the new stack")
    return 0
