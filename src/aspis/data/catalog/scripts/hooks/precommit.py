#!/usr/bin/env python3
"""pre-commit — fix things before the real commit, then check (FR-002).

Philosophy (ship-safe): in the default ``warn`` mode this NEVER blocks. It first
applies safe auto-fixes — clean junk, format/lint-fix staged Python and re-stage —
so the commit lands correct, then runs the checks (scope, R-009 protected paths,
secrets) and only *reports* them. Flip ``enforcement: block`` in hooks.yaml to turn
the reported issues into a hard stop. No LLM, never pytest.
"""

from __future__ import annotations

import os
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _config  # noqa: E402
import _git  # noqa: E402
import cleanup  # noqa: E402
import scope  # noqa: E402
import secret_scan  # noqa: E402

# Set this in the environment to approve an R-009 protected-path change (block mode).
_APPROVE_ENV = "ASPIS_ALLOW_PROTECTED"


def _ruff() -> str | None:
    """Locate ruff next to the active interpreter, then on PATH; None if absent."""
    sibling = Path(sys.executable).parent / "ruff"
    if sibling.is_file():
        return str(sibling)
    from shutil import which

    return which("ruff")


def _ruff_configured(root: Path) -> bool:
    """True when the project declares ruff config (so we fix to its rules, not defaults)."""
    if (root / "ruff.toml").is_file() or (root / ".ruff.toml").is_file():
        return True
    pyproject = root / "pyproject.toml"
    return pyproject.is_file() and "[tool.ruff]" in pyproject.read_text(encoding="utf-8")


def _autofix(root: Path, staged: list[str]) -> list[str]:
    """Format + lint-fix staged Python and re-stage it. Returns the files touched."""
    py = [f for f in staged if f.endswith(".py") and (root / f).is_file()]
    ruff = _ruff()
    if not py or not ruff or not _ruff_configured(root):
        return []
    for args in ([ruff, "format", *py], [ruff, "check", "--fix", *py]):
        subprocess.run(
            args,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    _git.add(py)  # capture any in-place fixes in this commit
    return py


def main() -> int:
    """Auto-fix, then check. Exit non-zero only in ``block`` mode with open issues."""
    _config.force_utf8_stdio()
    root = _git.repo_root()
    staged = _git.staged_files()

    # 1) Fix what we safely can, before the commit is taken.
    cleaned = cleanup.clean(root, staged)
    fixed = _autofix(root, staged)
    for rel in cleaned.junk:
        print(f"[aspis] removed junk: {rel}")
    if fixed:
        print(f"[aspis] auto-formatted {len(fixed)} staged file(s)")

    # 2) Check (report; only blocks in block mode).
    issues: list[str] = []
    issues += [f"out of scope: {p} — {why}" for p, why in scope.violations(staged, root)]

    protected = list(_config.hooks_config(root).get("protected_paths") or [])
    if protected and not os.environ.get(_APPROVE_ENV):
        issues += [
            f"protected path (R-009): {p} — set {_APPROVE_ENV}=1 to approve"
            for p in staged
            if any(fnmatch(p, pat) for pat in protected)
        ]
    if secret_scan.main() != 0:
        issues.append("possible secret in staged changes")

    blocking = _config.blocks(root)
    label = "BLOCKED" if blocking else "warning"
    for message in issues:
        print(f"[aspis] {label}: {message}", file=sys.stderr)
    return 1 if (blocking and issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
