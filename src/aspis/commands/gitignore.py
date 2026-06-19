"""``aspis gitignore`` — write/refresh the project's .gitignore for its stack.

Thin wrapper over the shipped ``.aspis/scripts/hooks/gitignore.py`` so the logic
lives in exactly one place (the same script the post-commit hook runs). Sources the
canonical body from the Toptal API with an offline cache.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from aspis import project


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``gitignore`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "gitignore",
        help="Write/refresh .gitignore for the project's stack (Toptal source + offline cache).",
    )
    parser.add_argument(
        "stack", nargs="?", help="Stack keyword (default: detected, e.g. python, node)."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run the shipped gitignore maintainer against the project at ``args.path``."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1
    script = root / ".aspis" / "scripts" / "hooks" / "gitignore.py"
    if not script.is_file():
        print("gitignore maintainer not found; re-run `aspis init` to ship the hooks.")
        return 1
    command = [sys.executable, str(script), *([args.stack] if args.stack else [])]
    return subprocess.run(command, cwd=str(root), check=False).returncode
