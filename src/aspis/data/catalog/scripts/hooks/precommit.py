#!/usr/bin/env python3
"""pre-commit orchestrator — the commit-boundary wall (FR-002).

Deterministic, fast, no LLM, and never the test suite. In order: auto-clean junk
(block if any staged junk was removed so the cleaned set is re-staged), then block
on out-of-scope files, R-009 protected paths, secrets, and a fast ruff lint/format
of the staged Python.
"""

from __future__ import annotations

import os
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git  # noqa: E402
import cleanup  # noqa: E402
import scope  # noqa: E402
import secret_scan  # noqa: E402
from _config import hooks_config  # noqa: E402

# Set this in the environment to approve an R-009 protected-path change.
_APPROVE_ENV = "ASPIS_ALLOW_PROTECTED"


def _ruff() -> str | None:
    """Locate ruff next to the active interpreter, then on PATH; None if absent."""
    sibling = Path(sys.executable).parent / "ruff"
    if sibling.is_file():
        return str(sibling)
    from shutil import which

    return which("ruff")


def _fast_lint(root: Path, staged: list[str], fails: list[str]) -> None:
    """Run ruff format-check + lint on staged Python (best-effort, never pytest)."""
    py = [f for f in staged if f.endswith(".py") and (root / f).is_file()]
    ruff = _ruff()
    if not py or not ruff:
        return
    for args, label in (
        ([ruff, "format", "--check", *py], "ruff format"),
        ([ruff, "check", *py], "ruff check"),
    ):
        result = subprocess.run(args, cwd=str(root), capture_output=True, text=True, check=False)
        if result.returncode != 0:
            fails.append(f"{label} failed:\n{(result.stdout or result.stderr).strip()}")


def main() -> int:
    """Run every wall; exit 1 with all reasons if any blocks the commit."""
    root = _git.repo_root()
    staged = _git.staged_files()
    fails: list[str] = []

    cleaned = cleanup.clean(root, staged)
    if cleaned.junk:
        fails.append(f"removed junk files (re-commit without them): {', '.join(cleaned.junk)}")

    for path, reason in scope.violations(staged, root):
        fails.append(f"out of scope: {path} — {reason}")

    protected = list(hooks_config(root).get("protected_paths") or [])
    if protected and not os.environ.get(_APPROVE_ENV):
        for path in staged:
            if any(fnmatch(path, pat) for pat in protected):
                fails.append(f"protected path (R-009): {path} — set {_APPROVE_ENV}=1 to approve")

    if secret_scan.main() != 0:
        fails.append("possible secret in staged changes")

    _fast_lint(root, staged, fails)

    for message in fails:
        print(f"[aspis] BLOCKED: {message}", file=sys.stderr)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
