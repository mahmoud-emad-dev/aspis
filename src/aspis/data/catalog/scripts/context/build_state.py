#!/usr/bin/env python3
"""Write ``.aspis/context/CURRENT_STATE.md`` — a snapshot of the project now.

Self-contained (stdlib only). The auto block (project, stack, branch, last
commit) is regenerated; any manual notes outside the markers are preserved.

Usage: python3 build_state.py [project_root]
"""

from __future__ import annotations

import sys
from pathlib import Path

import _common


def _feature_line(root: Path, branch: str) -> str:
    """One-line active-feature summary, with commits-on-this-feature count."""
    feature = _common.active_feature(root)
    if not feature:
        return "- **Active feature:** none"
    fid = feature.get("id", "?")
    title = feature.get("title", feature.get("slug", "?"))
    phase = feature.get("phase", "?")
    mode = feature.get("mode", "?")
    # How many commits on this branch carry this feature's scope (0 → no code yet).
    count = 0
    for commit in _common.recent_commits(root, 50):
        if commit["feature"] == fid.upper():
            count += 1
    body = f"{fid} {title} — phase {phase}, mode {mode}"
    tail = "no commits yet" if count == 0 else f"{count} commit(s)"
    return f"- **Active feature:** {body} · {tail}"


def _tree_line(root: Path) -> str:
    """Working-tree status: clean, or a count of changed paths."""
    status = _common.git(root, "status", "--porcelain")
    changed = [ln for ln in status.splitlines() if ln.strip()]
    if not changed:
        return "- **Working tree:** clean"
    return f"- **Working tree:** {len(changed)} changed"


def run(root: Path) -> Path:
    """Regenerate CURRENT_STATE.md's auto block; return the file path."""
    stack = _common.detect_stack(root)
    branch = _common.git(root, "rev-parse", "--abbrev-ref", "HEAD") or "(no git)"
    last = _common.git(root, "log", "-1", "--pretty=%h %s — %ad", "--date=short") or "(no commits)"

    body = "\n".join(
        [
            "## Current state",
            "",
            f"- **Project:** {root.name} · **Stack:** {stack}",
            f"- **Branch:** {branch}",
            _feature_line(root, branch),
            _tree_line(root),
            f"- **Last commit:** {last}",
        ]
    )

    target = root / ".aspis" / "context" / "CURRENT_STATE.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_common.render_auto_block(target, body), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    """Run the updater against the given (or current) project root."""
    _common.force_utf8_stdio()
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path.cwd()
    target = run(root)
    print(f"wrote {target.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
