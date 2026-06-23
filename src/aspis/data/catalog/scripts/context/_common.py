"""Shared helpers for the self-contained context-update scripts.

Standard library only. These scripts ship into a project's
``.aspis/scripts/context/`` and run with the project's own Python — no global
``aspis`` dependency. A sibling script imports this module directly, because
Python puts the running script's directory on ``sys.path``.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (mirrors ``aspis.cli``).

    Best-effort: streams without ``reconfigure`` (e.g. a test capture buffer) are
    left untouched. Keeps these standalone scripts from crashing when they print a
    non-ASCII character (an arrow, a check mark) under a cp1252 console (Windows).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


# Markers bounding the regenerated block; anything outside them is preserved.
AUTO_START = "<!-- ASPIS:auto START -->"
AUTO_END = "<!-- ASPIS:auto END -->"

# Marker files that identify a project's stack (first match wins).
_STACK_MARKERS = [
    ("pyproject.toml", "python"),
    ("package.json", "node"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
]


def git(root: Path, *args: str) -> str:
    """Run a read-only git command in *root*; return stripped stdout ('' on failure)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def detect_stack(root: Path) -> str:
    """Return the project's stack from marker files, or 'unknown'."""
    for marker, stack in _STACK_MARKERS:
        if (root / marker).exists():
            return stack
    return "unknown"


def active_feature(root: Path) -> dict[str, str]:
    """Return the active feature record, or {} if none/unreadable."""
    path = root / ".aspis" / "current" / "active_feature.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


# A conventional-commit subject: ``type(scope): summary`` (scope optional).
_SUBJECT = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<summary>.*)$")
_FEATURE_ID = re.compile(r"F-\d+", re.IGNORECASE)


def parse_subject(subject: str) -> tuple[str, str | None, str]:
    """Split a commit subject into (type, scope-or-None, summary).

    Falls back to ('other', None, subject) when it is not a conventional commit.
    """
    match = _SUBJECT.match(subject)
    if not match:
        return "other", None, subject
    return match["type"], match["scope"], match["summary"]


def feature_id(scope: str | None) -> str | None:
    """Return the ``F-NNN`` id embedded in a commit scope, or None."""
    if not scope:
        return None
    found = _FEATURE_ID.search(scope)
    return found.group(0).upper() if found else None


def top_dir(path: str) -> str:
    """Return a file's leading path segment as a folder label (root → '(root)')."""
    head = path.split("/", 1)
    return f"{head[0]}/" if len(head) > 1 else "(root)"


def recent_commits(root: Path, limit: int) -> list[dict[str, object]]:
    """Return the newest *limit* commits with parsed metadata + touched files.

    Each entry: ``{hash, date, subject, type, scope, summary, feature, files,
    dirs}``. One ``git log`` call; stdlib parsing — no per-commit shell-out.
    """
    sentinel = "@@@"
    fmt = f"{sentinel}%h|%ad|%s"
    out = git(root, "log", f"-{limit}", "--date=short", f"--pretty=format:{fmt}", "--name-only")
    commits: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in out.splitlines():
        if line.startswith(sentinel):
            short, date, subject = (line[len(sentinel) :].split("|", 2) + ["", ""])[:3]
            ctype, scope, summary = parse_subject(subject)
            current = {
                "hash": short,
                "date": date,
                "subject": subject,
                "type": ctype,
                "scope": scope,
                "summary": summary,
                "feature": feature_id(scope),
                "files": [],
            }
            commits.append(current)
        elif line.strip() and current is not None:
            current["files"].append(line.strip())  # type: ignore[union-attr]
    for commit in commits:
        files = commit["files"]  # type: ignore[index]
        commit["dirs"] = _ordered_dirs(files)  # type: ignore[index]
    return commits


def _ordered_dirs(files: list[str]) -> list[str]:
    """Distinct top-level folders touched, most-frequent first."""
    counts: dict[str, int] = {}
    for path in files:
        counts[top_dir(path)] = counts.get(top_dir(path), 0) + 1
    return sorted(counts, key=lambda d: (-counts[d], d))


def render_auto_block(path: Path, body: str) -> str:
    """Return *path*'s content with the ASPIS auto block set to *body*.

    If the markers are present, only the block between them is replaced (manual
    content is preserved). If the file exists without markers, the block is
    prepended above the existing content. Otherwise a new block is created.
    """
    block = f"{AUTO_START}\n{body}\n{AUTO_END}"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            before = text.split(AUTO_START)[0]
            after = text.split(AUTO_END, 1)[1]
            return f"{before}{block}{after}"
        return f"{block}\n\n{text}"
    return f"{block}\n"
