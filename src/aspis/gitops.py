"""Shared git helpers for the lifecycle operations (init + bootstrap).

The one place that knows how init/bootstrap commit: only the ASPIS-owned paths are
staged, so a run on an existing repo never sweeps the user's own uncommitted code into
our commit. Stale ``.gitkeep`` is reaped before staging so a populated dir leaves no
dangling deletion. Both ``init`` (its own scaffold commit) and ``bootstrap`` (its fill
commit) call this, so the rule lives once.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

#: The paths init/bootstrap own — the only ones their commits may stage.
OWNED_PATHS = (".aspis", ".opencode", ".claude", "AGENTS.md", "CLAUDE.md", ".gitignore")


def git(root: Path, *args: str) -> str:
    """Run a git command in *root* (UTF-8, never raises); return stripped stdout."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip()


def has_git(root: Path) -> bool:
    """True when *root* is a git repository."""
    return (root / ".git").is_dir()


def reap_stale_gitkeeps(root: Path, owned: list[str]) -> None:
    """Delete ``.gitkeep`` from any owned dir that now holds git-trackable content (pre-stage).

    Runs before staging so the deletion lands in our commit and the tree stays clean,
    rather than the pre-commit hook reaping it post-stage and dangling the deletion.

    A ``.gitkeep`` is reaped only when its dir has a sibling git would actually track —
    NOT when the only other content is gitignored (e.g. ``index/`` holds just the
    generated, ignored ``FILE_REGISTRY.yaml``). Such a dir is git-empty, so its
    ``.gitkeep`` is still doing its job and must stay.
    """
    for name in owned:
        base = root / name
        if not base.is_dir():
            continue
        for keep in base.rglob(".gitkeep"):
            siblings = [p for p in keep.parent.iterdir() if p.name != ".gitkeep"]
            if not siblings:
                continue
            rels = [p.relative_to(root).as_posix() for p in siblings]
            ignored = set(git(root, "check-ignore", "--", *rels).splitlines())
            if any(rel not in ignored for rel in rels):  # some sibling is git-trackable
                keep.unlink()


def commit_owned(root: Path, message: str) -> bool:
    """Stage + commit only the ASPIS-owned paths; return True if a commit was made.

    init/bootstrap are authorized human setup: they ship the very R-009 protected paths
    (rules, constitution), so these commits carry the approval the pre-commit hook looks
    for. The commit pathspec guarantees unrelated user changes are never included; an
    empty owned-set or nothing-staged is a no-op (never an empty/foreign commit).
    """
    owned = [p for p in OWNED_PATHS if (root / p).exists()]
    if not owned:
        return False
    reap_stale_gitkeeps(root, owned)
    git(root, "add", "--", *owned)
    if not git(root, "diff", "--cached", "--name-only", "--", *owned):
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "commit", "-q", "-m", message, "--", *owned],
        capture_output=True,
        check=False,
        env={**os.environ, "ASPIS_ALLOW_PROTECTED": "1"},
    )
    return result.returncode == 0
