"""ASPIS command-line interface.

Thin shell: this module builds the parser by letting each command module
register its own verb, then dispatches. No business logic lives here — command
handlers call into the core modules (``aspis.health``, ``aspis.project``, ...).

To add a command, create a module under ``aspis.commands`` and list it in that
package's ``COMMAND_MODULES``. This file never changes when a verb is added.
"""

from __future__ import annotations

import argparse
import sys

from aspis import __version__
from aspis.commands import COMMAND_MODULES

TAGLINE = "the shield for autonomous software production"


# ---------------------------------------------------------------------------
# Console compatibility
# ---------------------------------------------------------------------------


def _force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (e.g. Windows cp1252).

    Best-effort: streams without ``reconfigure`` (such as test capture buffers)
    are left untouched.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


# ---------------------------------------------------------------------------
# Parser assembly & dispatch
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Assemble the top-level parser from the registered command modules."""
    parser = argparse.ArgumentParser(prog="aspis", description=f"ASPIS — {TAGLINE}.")
    parser.add_argument("-V", "--version", action="version", version=f"aspis {__version__}")

    subcommands = parser.add_subparsers(dest="command", metavar="<command>")
    for module in COMMAND_MODULES:
        module.register(subcommands)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    _force_utf8_stdio()

    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
