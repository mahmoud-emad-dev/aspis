"""``aspis doctor`` — report on the local environment and project health."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.health import run_checks

#: Label shown per status. ASCII-safe so it renders on any console.
_LABELS = {"ok": "ok  ", "warn": "warn", "fail": "FAIL"}


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``doctor`` verb on the given subparsers action."""
    parser = subparsers.add_parser("doctor", help="Check the local environment and project health.")
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run all health checks and print a small report.

    Returns a non-zero exit code only when a check fails; warnings pass.
    """
    root = Path(args.path).resolve()
    checks = run_checks(root)

    for check in checks:
        label = _LABELS.get(check.status, check.status)
        print(f"  [{label}] {check.name:<8} {check.detail}")

    failed = [c for c in checks if c.status == "fail"]
    if failed:
        print(f"\n{len(failed)} check(s) failed.")
        return 1
    print("\nAll checks passed.")
    return 0
