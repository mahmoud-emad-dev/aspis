"""``aspis uninstall`` — remove ASPIS's machine-wide state (F-013, P1).

Removes the global config / data / cache directories and the runtime inventory.
It never touches a project's ``.aspis`` brain. Removing the CLI binary itself is
left to ``uv`` (printed at the end) because a tool cannot reliably delete its own
running executable — especially on Windows. Dry-run by default, like the rest of
ASPIS; pass ``--write`` to actually delete.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from aspis import paths


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``uninstall`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "uninstall", help="Remove ASPIS's machine-wide state (keeps project brains)."
    )
    parser.add_argument("--write", action="store_true", help="Actually delete (default: dry-run).")
    parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Keep the global config dir (remove only data + cache).",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    locations = paths.all_locations()
    targets: list[tuple[str, Path]] = [
        (name, path)
        for name, path in locations.items()
        if not (args.keep_config and name == "config")
    ]
    existing = [(name, path) for name, path in targets if path.exists()]

    verb = "Removing" if args.write else "Would remove"
    print(f"{verb} ASPIS machine-wide state (project brains are left untouched):")
    if not existing:
        print("  (nothing to remove — no global state dirs exist)")
    for name, path in existing:
        print(f"  {name:<8} {path}")
        if args.write:
            shutil.rmtree(path, ignore_errors=True)

    if not args.write:
        print("\nNothing was removed (dry-run). Re-run with --write to delete.")
    else:
        print("\nRemoved. To uninstall the CLI itself, run:")
        print("  uv tool uninstall aspis")
    return 0
