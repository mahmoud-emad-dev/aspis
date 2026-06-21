"""Commit-message history audit & fix (F-012).

Reuses the commit-msg hook's ``validate`` — the single source of commit style —
to scan existing history and report every commit whose message violates the
convention. Read-only by default; ``fix_history`` rewrites the auto-fixable
messages (forbidden attribution) after stamping a backup ref, leaving commit
*content* byte-identical (only messages change). The ``aspis commits`` verb is a
thin wrapper over this module.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from aspis import resources


@lru_cache(maxsize=1)
def _commitmsg() -> ModuleType:
    """Load the catalog commit-msg hook module (the SSoT for message validation)."""
    path = resources.catalog_dir() / "scripts" / "hooks" / "commitmsg.py"
    spec = importlib.util.spec_from_file_location("aspis_hook_commitmsg", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import wiring
        raise RuntimeError(f"cannot load commit-msg hook at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_convention(root: Path) -> dict[str, Any]:
    """The project's commit convention, falling back to the bundled catalog copy."""
    path = root / ".aspis" / "config" / "commit-convention.yaml"
    if not path.is_file():
        path = resources.catalog_dir() / "config" / "commit-convention.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def clean_message(message: str, convention: dict[str, Any]) -> str:
    """Apply the auto-fixable repairs (escape-hatch + attribution) to one message."""
    hook = _commitmsg()
    message, _ = hook.strip_skip_marker(message, hook.skip_marker(convention))
    message, _ = hook.strip_attribution(message, convention)
    return message


@dataclass
class Finding:
    """One commit whose message violates the convention."""

    sha: str
    subject: str
    violations: list[str]

    @property
    def autofixable(self) -> bool:
        """True when every violation is the attribution class (safe to auto-rewrite)."""
        return bool(self.violations) and all("attribution" in v for v in self.violations)


def _git(root: Path, *args: str) -> str:
    """Run a git command in *root* and return stdout (UTF-8)."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def audit_history(
    root: Path, convention: dict[str, Any], *, limit: int | None = None
) -> list[Finding]:
    """Every commit whose message violates *convention*, newest first.

    One ``git log`` call: ``-z`` NUL-separates commits, ``%H%n%B`` gives each
    commit's hash then its full raw message, so the scan stays cheap on big repos.
    """
    hook = _commitmsg()
    rng = ["-n", str(limit)] if limit else []
    raw = _git(root, "log", "-z", "--format=%H%n%B", *rng)
    findings: list[Finding] = []
    for record in raw.split("\0"):
        record = record.strip("\n")
        if not record:
            continue
        sha, _, message = record.partition("\n")
        subject = message.splitlines()[0].strip() if message else ""
        violations = hook.validate(message, convention)
        if violations:
            findings.append(Finding(sha=sha, subject=subject, violations=violations))
    return findings


def clean_message_stdin() -> None:
    """Filter entry: read a message on stdin, write the cleaned message to stdout.

    Used by ``git filter-branch --msg-filter``; the convention is loaded from the
    repository the filter runs in (cwd), falling back to the bundled catalog.
    """
    convention = load_convention(Path.cwd())
    sys.stdout.write(clean_message(sys.stdin.read(), convention))


def fix_history(root: Path, convention: dict[str, Any], findings: list[Finding]) -> int:
    """Rewrite the auto-fixable messages across history; stamp a backup ref first.

    Returns 0 on success. Advisory-only findings (scope/length) are reported but
    never auto-rewritten — a subject's intent must not be machine-guessed.
    """
    auto = [f for f in findings if f.autofixable]
    manual = [f for f in findings if not f.autofixable]
    if not auto:
        print("commits: nothing auto-fixable.")
        if manual:
            print(f"  ({len(manual)} advisory finding(s) need a manual reword.)")
        return 0

    backup = f"backup/commits-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    subprocess.run(["git", "-C", str(root), "branch", backup], check=True)

    # Rewrite only the current branch (HEAD); the backup ref keeps the originals.
    cleaner = f'"{sys.executable}" -c "import aspis.commitaudit as a; a.clean_message_stdin()"'
    env = {**os.environ, "FILTER_BRANCH_SQUELCH_WARNING": "1"}
    subprocess.run(
        ["git", "-C", str(root), "filter-branch", "-f", "--msg-filter", cleaner, "HEAD"],
        check=True,
        env=env,
    )
    print(f"commits: rewrote {len(auto)} message(s); backup ref at '{backup}'.")
    if manual:
        print(f"  ({len(manual)} advisory finding(s) still need a manual reword.)")
    return 0
