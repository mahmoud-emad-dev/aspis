"""``aspis init`` — scaffold an ASPIS project and export its runtime assets."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.engine import build_engine
from aspis.operations import register_all


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``init`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "init", help="Initialize an ASPIS project in a directory (dry-run by default)."
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.add_argument("--profile", default="base", help="Profile to export (default: base).")
    parser.add_argument(
        "--runtime",
        action="append",
        dest="runtimes",
        help="Runtime to export (repeatable; default: the profile's runtimes).",
    )
    parser.add_argument("--name", default=None, help="Project name (default: directory name).")
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument(
        "--no-git", action="store_true", dest="no_git", help="Skip git initialization."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run the init operation through the lifecycle engine and print its report."""
    engine = build_engine()
    register_all(engine)

    ctx = engine.run(
        "init",
        Path(args.path).resolve(),
        profile=args.profile,
        runtimes=args.runtimes,
        name=args.name,
        write=bool(args.write),
        force=bool(args.force),
        no_git=bool(args.no_git),
    )

    header = "WROTE" if args.write else "DRY-RUN (pass --write to apply)"
    print(f"{header} — init {ctx.root}")
    for message in ctx.messages:
        print(f"  {message}")
    if not args.write:
        print("\nNothing was written (dry-run). Re-run with --write to apply:")
        print(f"  aspis init {args.path} --write")
        return 0

    print("\nInitialized. Next:")
    print("  1. aspis bootstrap --write   # make the project live (sets goal, promotes leads)")
    print("  2. aspis models --sync       # assign a model to each agent for this machine")
    print("  3. open AGENTS.md            # the project's entry point")
    print("  4. start your runtime        # OpenCode, or add --runtime claude for Claude Code")
    return 0
