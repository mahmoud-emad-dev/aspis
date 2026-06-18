"""``aspis status`` — report whether a directory is an ASPIS project."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.project import is_project


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``status`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "status", help="Report whether the current directory is an ASPIS project."
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Print project detection for ``args.path``."""
    root = Path(args.path).resolve()
    if is_project(root):
        print(f"ASPIS project detected at {root}")
    else:
        print(f"No ASPIS project here ({root}).")
        print("Run `aspis init` to create one.")
    return 0
