"""``aspis heal`` — deterministically restore the brain floor (F-020).

The safety net for when an agent was weak, offline, or failed during bootstrap: it re-runs
the project's own context generators (FILE_REGISTRY, CODE_MAP, CURRENT_STATE, RECENT_CHANGES)
and re-applies the ``.gitignore`` for the recorded stack, then reports readiness. It is a
**deterministic restore of expected files** — it never invents content — and is idempotent,
so it is safe to run any time the project looks half-filled. ``--check`` only reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aspis import manifest, project
from aspis.constants import BRAIN_DIR
from aspis.operations import bootstrap
from aspis.operations._proc import run_quiet


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``heal`` verb."""
    parser = subparsers.add_parser(
        "heal", help="Deterministically refill the brain (context/registry/gitignore)."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.add_argument(
        "--check", action="store_true", help="Only report readiness; don't run generators."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    if not args.check:
        update = root / BRAIN_DIR / "scripts" / "context" / "update.py"
        if update.is_file():
            run_quiet([sys.executable, str(update), str(root)])
            print("refreshed context (registry, code map, current state, recent changes)")
        stack = (manifest.load(root).get("stack") or "").strip()
        gitignore = root / BRAIN_DIR / "scripts" / "hooks" / "gitignore.py"
        if stack and stack != "unknown" and gitignore.is_file():
            run_quiet([sys.executable, str(gitignore), stack], cwd=root)
            print(f"re-applied .gitignore for stack: {stack}")

    missing = bootstrap.readiness(root)
    if missing:
        print("readiness: still missing/empty —")
        for item in missing:
            print(f"  - {item}")
        return 1
    print("readiness: ok (brain floor present)")
    return 0
