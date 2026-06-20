#!/usr/bin/env python3
"""Active-feature pointer — read, validate, and guard the single source of truth.

``.aspis/current/active_feature.json`` names the feature work is happening on right
now. It is a source of truth, so it must stay correct: name a real feature, agree
with the git branch, and never be silently overwritten while a previous feature is
still unfinished. This module is the deterministic guard around it — the scaffold
uses it to refuse an unsafe switch, and ``--check`` validates the pointer (usable as
a gate so drift cannot go unnoticed, the way F-008 sat stale on a merged feature).

Self-contained (stdlib only). Ships into ``.aspis/scripts/planning/`` and runs with
the project's own Python.

Usage:
  python3 active_feature.py [root]                 # print the current pointer
  python3 active_feature.py [root] --check         # validate; exit nonzero on problems
  python3 active_feature.py [root] --set-phase done # move the pointer's phase
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import _console

REQUIRED_KEYS = ("id", "slug", "title", "path", "branch", "mode", "phase")
WORK_PHASES = ("plan", "build", "review")
TERMINAL_PHASES = ("done", "merged", "abandoned")
KNOWN_PHASES = WORK_PHASES + TERMINAL_PHASES


def pointer_path(root: Path) -> Path:
    """Path to the active-feature pointer under *root*."""
    return root / ".aspis" / "current" / "active_feature.json"


def read_pointer(root: Path) -> dict | None:
    """Return the pointer as a dict, or ``None`` if missing/malformed."""
    try:
        data = json.loads(pointer_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def current_branch(root: Path) -> str:
    """Return the current git branch name ('' when unavailable or detached lookup fails)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def is_unfinished(data: dict | None) -> bool:
    """True when *data* names a feature still in a working (non-terminal) phase."""
    return bool(data) and data.get("phase") not in TERMINAL_PHASES


def validate(root: Path, *, check_branch: bool = True) -> list[str]:
    """Return a list of problems with the pointer (empty ⇒ valid)."""
    data = read_pointer(root)
    if data is None:
        return ["active_feature.json is missing or malformed"]
    problems = [f"missing or empty field: {key}" for key in REQUIRED_KEYS if not data.get(key)]
    feat_path = data.get("path")
    if feat_path and not (root / feat_path).is_dir():
        problems.append(f"feature path does not exist: {feat_path}")
    phase = data.get("phase")
    if phase and phase not in KNOWN_PHASES:
        problems.append(f"unknown phase: {phase!r} (expected one of {', '.join(KNOWN_PHASES)})")
    if check_branch:
        branch = current_branch(root)
        pointer_branch = data.get("branch")
        if branch and pointer_branch and branch not in (pointer_branch, "HEAD"):
            problems.append(f"branch mismatch: on '{branch}' but pointer says '{pointer_branch}'")
    return problems


def set_phase(root: Path, phase: str, *, write: bool = True) -> dict:
    """Set the pointer's phase (validated), returning the updated pointer."""
    if phase not in KNOWN_PHASES:
        raise ValueError(f"unknown phase: {phase!r} (expected one of {', '.join(KNOWN_PHASES)})")
    data = read_pointer(root)
    if data is None:
        raise ValueError("no active feature to update")
    data["phase"] = phase
    if write:
        pointer_path(root).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    _console.force_utf8_stdio()
    parser = argparse.ArgumentParser(
        description="Read, validate, or update the active-feature pointer."
    )
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument(
        "--check", action="store_true", help="validate the pointer; exit nonzero on problems"
    )
    parser.add_argument(
        "--set-phase", metavar="PHASE", help=f"set phase: {' | '.join(KNOWN_PHASES)}"
    )
    parser.add_argument(
        "--no-branch-check", action="store_true", help="skip the git-branch agreement check"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).resolve()

    if args.set_phase:
        try:
            data = set_phase(root, args.set_phase)
        except ValueError as exc:
            print(f"error: {exc}")
            return 2
        print(f"{data['id']} phase -> {data['phase']}")
        return 0

    if args.check:
        problems = validate(root, check_branch=not args.no_branch_check)
        if problems:
            print("active-feature pointer has problems:")
            for problem in problems:
                print(f"  - {problem}")
            return 1
        data = read_pointer(root)
        print(f"OK: {data['id']} ({data['phase']}) on {data['branch']}")
        return 0

    data = read_pointer(root)
    if data is None:
        print("no active feature")
        return 0
    print(f"{data['id']} ({data['phase']}) — {data['title']}  [{data['branch']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
