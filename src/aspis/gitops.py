"""Shared git helpers for the lifecycle operations (init + bootstrap).

The one place that knows how init/bootstrap commit: only the ASPIS-owned paths are
staged, so a run on an existing repo never sweeps the user's own uncommitted code into
our commit. Stale ``.gitkeep`` is reaped before staging so a populated dir leaves no
dangling deletion. Both ``init`` (its own scaffold commit) and ``bootstrap`` (its fill
commit) call this, so the rule lives once.

**Two git lanes (F-022 — the `git` subsystem).** The product repo (``root/.git``) tracks
the user's source and the small root guides; the **brain shadow repo** (``.aspis/.git``)
versions the brain on its own history. ``commit_owned`` routes to the right lane when a
shadow repo exists, so the product history never carries brain noise. Runtime dirs
(``.opencode``/``.claude``) are committed to **neither** — they are catalog-rendered and
tracked by the export snapshot + change-log (the runtime-integrity lane). A project with
no shadow repo (legacy, pre-F-022) keeps the original single-repo behaviour.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from aspis.constants import BRAIN_DIR

#: Root guides the *product* repo tracks (small, orienting; not brain, not runtime).
PRODUCT_OWNED = ("AGENTS.md", "CLAUDE.md", ".gitignore")

#: The paths init/bootstrap own in the legacy single-repo path — the only ones it stages.
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


def brain_repo_dir(root: Path) -> Path:
    """The directory that holds the brain shadow repo (``<root>/.aspis``)."""
    return root / BRAIN_DIR


def has_brain_repo(root: Path) -> bool:
    """True when the brain shadow repo (``.aspis/.git``) exists."""
    return (brain_repo_dir(root) / ".git").is_dir()


def init_brain_repo(root: Path, *, write: bool = True) -> bool:
    """Create the brain shadow repo at ``.aspis/`` if absent; return True if created.

    Refuses on a **legacy** project whose product repo already tracks ``.aspis`` — turning
    a tracked dir into a nested repo would make the product see it as a gitlink. Such a
    project needs the explicit, reviewed migration, not an automatic shadow init. A fresh
    project (``.aspis`` ignored by the product repo) initialises cleanly.
    """
    bdir = brain_repo_dir(root)
    if not bdir.is_dir() or (bdir / ".git").is_dir():
        return False
    if has_git(root) and git(root, "ls-files", "--", BRAIN_DIR):
        return False  # legacy: product already tracks the brain — leave it for migration
    if write:
        git(bdir, "init", "-q")
    return True


def _commit_in(repo: Path, message: str, pathspec: list[str]) -> bool:
    """Stage *pathspec* in *repo* and commit if anything is staged; return True if committed.

    Carries ``ASPIS_ALLOW_PROTECTED`` so an authorized setup/brain commit clears the
    protected-path pre-commit hook. A no-op (returns False) when nothing is staged.
    """
    git(repo, "add", "--", *pathspec)
    if not git(repo, "diff", "--cached", "--name-only", "--", *pathspec):
        return False
    result = subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", message, "--", *pathspec],
        capture_output=True,
        check=False,
        env={**os.environ, "ASPIS_ALLOW_PROTECTED": "1"},
    )
    return result.returncode == 0


def commit_brain(root: Path, message: str) -> bool:
    """Commit the whole brain to the shadow repo (``.aspis/.git``); True if a commit was made.

    Stages everything under ``.aspis`` (its own ``.gitignore`` filters generated/local/secret
    state). Runtime dirs live outside ``.aspis`` and are never staged here. A no-op when no
    shadow repo exists.
    """
    bdir = brain_repo_dir(root)
    if not has_brain_repo(root):
        return False
    reap_stale_gitkeeps(bdir, ["."])
    return _commit_in(bdir, message, ["."])


def commit_product(root: Path, message: str) -> bool:
    """Commit only the product-owned root guides to the product repo; True if committed."""
    owned = [p for p in PRODUCT_OWNED if (root / p).exists()]
    if not owned or not has_git(root):
        return False
    reap_stale_gitkeeps(root, owned)
    return _commit_in(root, message, owned)


def commit_owned(root: Path, message: str) -> bool:
    """Commit the ASPIS-owned paths to their correct lane(s); True if any commit was made.

    With a brain shadow repo present (F-022), the brain commits to ``.aspis/.git`` and the
    root guides to the product repo — so the product history never carries brain noise.
    Without one (legacy single-repo), the original behaviour applies: stage all owned paths
    into the product repo in one commit.

    init/bootstrap are authorized human setup: they ship the very R-009 protected paths
    (rules, constitution), so these commits carry the approval the pre-commit hook looks
    for. The commit pathspec guarantees unrelated user changes are never included.
    """
    if has_brain_repo(root):
        brain = commit_brain(root, message)
        product = commit_product(root, message)
        return brain or product

    owned = [p for p in OWNED_PATHS if (root / p).exists()]
    if not owned:
        return False
    reap_stale_gitkeeps(root, owned)
    return _commit_in(root, message, owned)
