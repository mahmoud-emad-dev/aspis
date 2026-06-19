"""``aspis commit`` — compose a conventional message and commit (F-007).

The tool the committer triggers: it stages the **explicitly named paths** (never
``-A``), composes the message via the shipped ``.aspis/scripts/git/compose.py`` (the
single rule source), and runs ``git commit`` so the F-006 hooks fire automatically
(pre-commit auto-fix/checks, commit-msg validation, post-commit refresh). It never
pushes and never amends.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from aspis import project


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``commit`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "commit",
        help="Stage explicit paths, compose a conventional message, and commit (no -A, no push).",
    )
    parser.add_argument("paths", nargs="+", help="Explicit paths to stage and commit.")
    parser.add_argument("--type", required=True, dest="type_", help="feat, fix, docs, chore, …")
    parser.add_argument("--title", required=True, help="imperative subject (no trailing period)")
    parser.add_argument("--task", default="", help="T-NN or a span T-NN..T-MM")
    parser.add_argument("--bullet", action="append", default=[], help="a body bullet (repeatable)")
    parser.add_argument("--tasks", default="", help="Tasks: trailer (auto-set from a span)")
    parser.add_argument("--no-scope", action="store_true", help="lifecycle commit (omit scope)")
    parser.add_argument("--path", default=".", help="project directory (default: current)")
    parser.set_defaults(func=_run)


def _compose(compose_script: Path, root: Path, args: argparse.Namespace) -> tuple[int, str, str]:
    """Run the shipped composer; return ``(returncode, message, errors)``."""
    cmd = [
        sys.executable,
        str(compose_script),
        "--type",
        args.type_,
        "--title",
        args.title,
        "--root",
        str(root),
    ]
    if args.task:
        cmd += ["--task", args.task]
    if args.tasks:
        cmd += ["--tasks", args.tasks]
    if args.no_scope:
        cmd += ["--no-scope"]
    for bullet in args.bullet:
        cmd += ["--bullet", bullet]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout, result.stderr


def _run(args: argparse.Namespace) -> int:
    """Compose the message, stage the explicit paths, and commit through git."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1
    compose_script = root / ".aspis" / "scripts" / "git" / "compose.py"
    if not compose_script.is_file():
        print("commit composer not found; re-run `aspis init` to ship the git scripts.")
        return 1

    # Compose + self-validate before touching the index, so a bad message stages nothing.
    code, message, errors = _compose(compose_script, root, args)
    if code != 0 or not message.strip():
        sys.stderr.write(errors or "[aspis commit] failed to compose a message\n")
        return code or 1

    # Stage exactly the named paths — never `git add -A`.
    subprocess.run(["git", "-C", str(root), "add", "--", *args.paths], check=False)

    # Commit via a message file so the full body (and the hooks) are honoured.
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
        handle.write(message)
        message_file = handle.name
    try:
        commit = subprocess.run(["git", "-C", str(root), "commit", "-F", message_file])
    finally:
        Path(message_file).unlink(missing_ok=True)
    return commit.returncode
