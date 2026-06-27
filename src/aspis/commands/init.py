"""``aspis init`` — scaffold an ASPIS project and export its runtime assets."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.engine import build_engine
from aspis.operations import register_all
from aspis.export import ProtectionError


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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Show what would happen without writing (default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes with protection (synonym for --write that also updates pristine files).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Refuse on CONFLICT or PROTECT (exit non-zero).",
    )
    parser.add_argument(
        "--scope",
        default=None,
        help="Export only assets whose target path starts with this prefix.",
    )
    parser.add_argument(
        "--force-conflicts",
        action="store_true",
        dest="force_conflicts",
        help="Overwrite files even when both catalog and user changed (CONFLICT).",
    )
    parser.add_argument(
        "--reset-snapshot",
        action="store_true",
        dest="reset_snapshot",
        help="Discard a corrupt snapshot and rebuild it.",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run the init operation through the lifecycle engine and print its report."""
    # --force-conflicts and --strict are contradictory: one permits conflicts,
    # the other forbids them. Reject with a clear error before doing any work.
    if args.force_conflicts and args.strict:
        print("error: --force-conflicts and --strict are contradictory "
              "(one permits conflicts, one forbids them).")
        return 2

    effective_write = bool(args.write or args.apply)

    engine = build_engine()
    register_all(engine)

    try:
        ctx = engine.run(
            "init",
            Path(args.path).resolve(),
            profile=args.profile,
            runtimes=args.runtimes,
            name=args.name,
            write=effective_write,
            force=bool(args.force),
            no_git=bool(args.no_git),
            apply=bool(args.apply),
            strict=bool(args.strict),
            scope=args.scope,
            force_conflicts=bool(args.force_conflicts),
            reset_snapshot=bool(args.reset_snapshot),
        )
    except ProtectionError as exc:
        print(f"error: {exc}")
        return 1

    header = "WROTE" if effective_write else "DRY-RUN (pass --write to apply)"
    print(f"{header} — init {ctx.root}")
    for message in ctx.messages:
        print(f"  {message}")
    if not effective_write:
        print("\nNothing was written (dry-run). Re-run with --write to apply:")
        print(f"  aspis init {args.path} --write")
        return 0

    print("\nInitialized. Next:")
    print("  1. aspis bootstrap --write   # make the project live (sets goal, promotes leads)")
    print("  2. aspis models --sync       # assign a model to each agent for this machine")
    print("  3. open AGENTS.md            # the project's entry point")
    print("  4. start your runtime        # OpenCode, or add --runtime claude for Claude Code")
    return 0
