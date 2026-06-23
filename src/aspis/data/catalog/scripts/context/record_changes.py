#!/usr/bin/env python3
"""Write ``.aspis/context/RECENT_CHANGES.md`` — a digest, not a ``git log`` dump.

Self-contained (stdlib only). The auto block synthesises what an agent would
otherwise have to compute itself: a header (branch · active feature · cadence),
recent commits grouped by feature/area with the folders they touched, and the
latest few annotated with file-count + top folder. Manual notes outside the
markers are preserved.

Usage: python3 record_changes.py [project_root]
"""

from __future__ import annotations

import sys
from pathlib import Path

import _common

# How many recent commits to digest, and how many to list individually.
LIMIT = 15
LATEST = 8


def _header(root: Path, branch: str, commits: list[dict[str, object]]) -> str:
    """One orientation line: branch, active feature + phase, last date."""
    feature = _common.active_feature(root)
    parts = [f"branch `{branch}`"]
    if feature:
        parts.append(f"active {feature.get('id', '?')} ({feature.get('phase', '?')})")
    if commits:
        parts.append(f"updated {commits[0]['date']}")
    parts.append(f"last {len(commits)} commits")
    return "_" + " · ".join(parts) + "_"


def _group_label(commit: dict[str, object]) -> str:
    """Group a commit under its feature id, else its conventional-commit type."""
    return str(commit["feature"] or commit["type"])


def _by_feature(commits: list[dict[str, object]], active: str | None) -> str:
    """Render the 'By feature / area' section: count + touched folders per group.

    The active feature's group is listed first; the rest follow newest-first.
    """
    order: list[str] = []
    groups: dict[str, list[dict[str, object]]] = {}
    for commit in commits:
        key = _group_label(commit)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(commit)

    if active and active in order:
        order.remove(active)
        order.insert(0, active)

    lines = ["**By feature / area**"]
    for key in order:
        members = groups[key]
        dirs: list[str] = []
        for commit in members:
            for folder in commit["dirs"]:  # type: ignore[union-attr]
                if folder not in dirs:
                    dirs.append(folder)
        touched = " ".join(f"`{d}`" for d in dirs[:3]) if dirs else ""
        bold = f"**{key}**" if key.upper().startswith("F-") else key
        lines.append(f"- {bold} — {len(members)} commit(s) · {touched}".rstrip(" ·"))
    return "\n".join(lines)


def _latest(commits: list[dict[str, object]]) -> str:
    """Render the newest commits, each with file-count + top folder."""
    lines = ["**Latest**"]
    for commit in commits[:LATEST]:
        files = commit["files"]  # type: ignore[index]
        dirs = commit["dirs"]  # type: ignore[index]
        where = f" · {len(files)} file(s) `{dirs[0]}`" if files else ""
        summary = commit["summary"] or commit["subject"]
        lines.append(f"- `{commit['hash']}` {summary} — {commit['date']}{where}")
    return "\n".join(lines)


def run(root: Path) -> Path:
    """Regenerate RECENT_CHANGES.md's auto block; return the file path."""
    branch = _common.git(root, "rev-parse", "--abbrev-ref", "HEAD") or "(no git)"
    commits = _common.recent_commits(root, LIMIT)

    if not commits:
        body = "## Recent changes\n\n_no commits yet_"
    else:
        active = _common.active_feature(root).get("id")
        active = active.upper() if active else None
        body = "\n\n".join(
            [
                "## Recent changes",
                _header(root, branch, commits),
                _by_feature(commits, active),
                _latest(commits),
            ]
        )

    target = root / ".aspis" / "context" / "RECENT_CHANGES.md"
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
