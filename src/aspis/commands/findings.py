"""``aspis findings`` — list and resolve open project findings (F-014).

Deterministic guards (e.g. the runtime scope-guard) emit a finding when they detect a wrong state;
``aspis preflight`` surfaces them as blockers. This verb lets a lead inspect and resolve them —
after the underlying problem is actually fixed or routed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import findings as store


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``findings`` verb."""
    parser = subparsers.add_parser("findings", help="List and resolve open project findings.")
    parser.add_argument("path", nargs="?", default=".", help="Project dir (default: current).")
    parser.add_argument(
        "--resolve", type=int, metavar="N", help="Resolve finding N (1-based) after fixing it."
    )
    parser.add_argument("--clear", action="store_true", help="Resolve all findings.")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()

    if args.clear:
        print(f"cleared {store.clear(root)} finding(s).")
        return 0
    if args.resolve is not None:
        removed = store.resolve(root, args.resolve)
        if removed is None:
            print("no such finding.")
            return 1
        print(f"resolved: [{removed.get('kind', '?')}] {removed.get('detail', '')}")
        return 0

    items = store.load(root)
    if not items:
        print("no open findings.")
        return 0
    for i, finding in enumerate(items, 1):
        kind = finding.get("kind", "?")
        print(f"  {i}. [{kind}] {finding.get('detail', '')}  ({finding.get('source', '?')})")
    return 0
