"""``aspis mode`` — show or set the project's default build mode."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import project


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``mode`` verb on the given subparsers action."""
    parser = subparsers.add_parser("mode", help="Show or set the project's default build mode.")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=project.VALID_MODES,
        help="New default mode (omit to show the current one).",
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Show or set the default mode for the project at ``args.path``."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1
    if args.mode:
        project.set_mode(root, args.mode)
        print(f"default build mode → {args.mode}")
    else:
        print(f"default build mode: {project.default_mode(root)}")
    return 0
