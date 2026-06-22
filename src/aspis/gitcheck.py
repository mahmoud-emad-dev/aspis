"""Git-subsystem self-test — prove the armed hooks actually work (bootstrap, gap C).

Bootstrap does not *trust* that the git hooks are wired; it *proves* it by exercising
them on a throwaway probe and rolling it back. It checks the jobs of the git subsystem
end-to-end against the real ``.git/hooks``:

* **wiring** — the pre-commit / commit-msg / post-commit wrappers exist and call aspis;
* **junk cleanup** — a ghost file (``=…``) is removed by pre-commit;
* **stale .gitkeep** — a ``.gitkeep`` beside real content is reaped by pre-commit;
* **commit-message** — an attribution line is auto-stripped by commit-msg.

The probe never survives: the temporary commit is reset away and the probe files
cleaned, so history and the working tree are exactly as they were. Untracked user
files are never touched (``reset --hard`` preserves them; the clean cleanup is scoped).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

_PROBE_DIR = Path(".aspis") / "_selftest_"
_JUNK = "=aspis_selftest"
_HOOKS = ("pre-commit", "commit-msg", "post-commit")


@dataclass
class Check:
    """One self-test result line."""

    name: str
    ok: bool
    detail: str


def _git(root: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run a git command in *root* (UTF-8, never raises), with the bootstrap approval env."""
    return subprocess.run(
        ["git", "-C", str(root), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env={**os.environ, "ASPIS_ALLOW_PROTECTED": "1"},
    )


def hooks_armed(root: Path) -> list[Check]:
    """Check the three hook wrappers exist and reference aspis (wiring only, no commit)."""
    checks = []
    for hook in _HOOKS:
        path = root / ".git" / "hooks" / hook
        wired = (
            path.is_file() and "aspis" in path.read_text(encoding="utf-8", errors="replace").lower()
        )
        checks.append(Check(f"hook:{hook}", wired, "armed" if wired else "missing or not aspis"))
    return checks


def verify(root: Path) -> list[Check]:
    """Run the full git-subsystem self-test; safe and side-effect-free (rolls back the probe)."""
    checks = hooks_armed(root)
    if not (root / ".git").is_dir():
        return [*checks, Check("probe", False, "no git repo — skipped")]
    # Require a clean tracked tree so `reset --hard` cannot lose real work.
    if _git(root, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        return [*checks, Check("probe", False, "tracked tree not clean — skipped probe")]
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    if not head:
        return [*checks, Check("probe", False, "no commit yet — skipped probe")]

    probe_dir = root / _PROBE_DIR
    junk = root / _JUNK
    try:
        probe_dir.mkdir(parents=True, exist_ok=True)
        (probe_dir / ".gitkeep").write_text("", encoding="utf-8")
        (probe_dir / "real.txt").write_text("real\n", encoding="utf-8")
        junk.write_text("junk\n", encoding="utf-8")
        # Stage ONLY the probe paths — never `add -A`, which would sweep the user's
        # own untracked code into the probe commit and lose it on the reset --hard.
        _git(root, "add", "--", _PROBE_DIR.as_posix(), _JUNK)
        _git(
            root,
            "commit",
            "-q",
            "-F",
            "-",
            stdin="chore: aspis git self-test\n\nCo-Authored-By: Probe <p@p>\n",
        )

        committed = _git(root, "rev-parse", "HEAD").stdout.strip() != head
        junk_gone = not junk.exists()
        gitkeep_reaped = not (probe_dir / ".gitkeep").exists()
        last_msg = _git(root, "log", "-1", "--format=%B").stdout if committed else ""
        attr_stripped = committed and "Co-Authored-By" not in last_msg
        checks += [
            Check(
                "hooks-fire", committed, "probe commit created" if committed else "no commit made"
            ),
            Check("junk-clean", junk_gone, "ghost removed" if junk_gone else "ghost survived"),
            Check(
                "gitkeep-reap",
                gitkeep_reaped,
                "stale .gitkeep reaped" if gitkeep_reaped else "survived",
            ),
            Check(
                "commit-msg",
                attr_stripped,
                "attribution stripped" if attr_stripped else "not stripped",
            ),
        ]
    finally:
        _git(root, "reset", "--hard", head)
        shutil.rmtree(probe_dir, ignore_errors=True)
        if junk.exists():
            junk.unlink()
    return checks
