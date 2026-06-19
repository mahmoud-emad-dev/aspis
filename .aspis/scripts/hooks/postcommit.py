#!/usr/bin/env python3
"""post-commit auto-run — light, fast, never blocks (FR-004, FR-007).

After a successful commit it tidies up and refreshes the brain: clean junk and
stale ``.gitkeep``, maintain ``.gitignore`` for the stack, and run the existing
context scripts. Every step is best-effort; the hook always exits 0.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git  # noqa: E402
import cleanup  # noqa: E402
import gitignore  # noqa: E402


def _refresh_context(root: Path) -> None:
    """Run the existing context updater if present (reused, not reimplemented)."""
    updater = root / ".aspis" / "scripts" / "context" / "update.py"
    if updater.is_file():
        subprocess.run([sys.executable, str(updater), str(root)], cwd=str(root), check=False)


def main() -> int:
    """Run the auto-run steps; swallow errors so a commit is never undone."""
    root = _git.repo_root()
    for step in (
        lambda: cleanup.clean(root),
        lambda: gitignore.ensure(root),
        lambda: _refresh_context(root),
    ):
        try:
            step()
        except Exception as error:  # noqa: BLE001 - post-commit must never fail
            print(f"[aspis] post-commit step skipped: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
