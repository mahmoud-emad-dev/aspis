"""ASPIS command-line interface.

Thin shell: this module only parses arguments and dispatches to a handler.
All real behaviour lives in dedicated modules so the CLI stays small and the
core stays independently testable.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import __version__

TAGLINE = "the shield for autonomous software production"

# A directory is an ASPIS project when it carries the brain folder.
BRAIN_DIR = ".asps"


def _cmd_status(args: argparse.Namespace) -> int:
    """Report whether ``path`` is an ASPIS project."""
    root = Path(args.path).resolve()
    if (root / BRAIN_DIR).is_dir():
        print(f"ASPIS project detected at {root}")
    else:
        print(f"No ASPIS project here ({root}).")
        print("Run `aspis init` to create one.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser."""
    parser = argparse.ArgumentParser(prog="aspis", description=f"ASPIS — {TAGLINE}.")
    parser.add_argument(
        "-V", "--version", action="version", version=f"aspis {__version__}"
    )

    subcommands = parser.add_subparsers(dest="command", metavar="<command>")

    status = subcommands.add_parser(
        "status", help="Report whether the current directory is an ASPIS project."
    )
    status.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    status.set_defaults(func=_cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
