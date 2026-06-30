"""``aspis brain`` — interact with the brain shadow repo (``.aspis/.git``).

The brain versions itself in its own git history (F-022 / D-023), separate from the product
repo, so the build loop commits brain changes here on brain events rather than polluting the
product's history. This verb is the thin, scriptable surface the committer / system-lead use:

- ``aspis brain status`` — what changed in the brain since its last commit.
- ``aspis brain commit -m "..."`` — commit the brain (its own ``.gitignore`` filters
  generated/local/secret state). The one write the build loop calls on a brain event.
- ``aspis brain log`` — recent brain history.

A no-op with a clear message on a project that has no shadow repo (legacy / pre-F-022).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import gitops
from aspis.constants import BRAIN_DIR


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``brain`` verb and its sub-actions."""
    parser = subparsers.add_parser(
        "brain",
        help="Interact with the brain shadow repo (.aspis/.git): status / commit / log.",
    )
    sub = parser.add_subparsers(dest="brain_action")
    for name, helptext in (
        ("status", "Show what changed in the brain since its last commit."),
        ("commit", "Commit the brain to its shadow repo."),
        ("log", "Show recent brain history."),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("path", nargs="?", default=".", help="Project directory (default: current).")
        if name == "commit":
            p.add_argument("-m", "--message", help="Commit message (default if omitted).")
        if name == "log":
            p.add_argument("-n", "--number", type=int, default=10, help="Commits to show.")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Dispatch the chosen brain action against the project's shadow repo."""
    root = Path(getattr(args, "path", ".") or ".").resolve()
    if not (root / BRAIN_DIR).is_dir():
        print("not an ASPIS project (no .aspis/) -- run `aspis init` first.")
        return 1
    if not gitops.has_brain_repo(root):
        print(
            "no brain shadow repo (.aspis/.git) here.\n"
            "  Fresh `aspis init` projects get one automatically; a legacy project that "
            "tracks .aspis in its product repo needs the explicit migration first."
        )
        return 1

    action = getattr(args, "brain_action", None) or "status"
    brain = gitops.brain_repo_dir(root)
    if action == "status":
        out = gitops.git(brain, "status", "--short")
        print(out or "brain clean (nothing to commit).")
        return 0
    if action == "log":
        print(gitops.git(brain, "log", f"-n{args.number}", "--oneline") or "(no brain history yet)")
        return 0
    # commit
    message = args.message or "chore(brain): record workspace changes"
    if gitops.commit_brain(root, message):
        print(f"brain committed: {message}")
    else:
        print("brain clean (nothing to commit).")
    return 0
