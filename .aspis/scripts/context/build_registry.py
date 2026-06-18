#!/usr/bin/env python3
"""Build ``.aspis/index/FILE_REGISTRY.yaml`` for a project.

Self-contained: standard library only, so it runs in any project that has
Python, with no dependency on a global ``aspis`` install. It scans the project,
classifies each file, derives a one-line purpose, and writes a YAML registry. It
regenerates the whole file from a fresh scan (idempotent), so there is no fragile
merge step.

A file's purpose comes from, in order:
  1. an explicit entry in ``.aspis/index/PURPOSES.json`` (a ``{path: purpose}``
     map agents maintain) — for files that cannot carry a top docstring/comment
     (JSON, data, binaries) or to override a weak auto-extracted line;
  2. the file's own module docstring / first heading / leading comment;
  3. otherwise blank.

Usage:
    python3 build_registry.py [project_root]   # default: current directory
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

# Directories never scanned: VCS, envs, caches, generated runtimes, the brain.
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".aspis",
    ".opencode",
    ".claude",
    "dist",
    "build",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
}

# File kind by extension (deterministic). Unlisted suffixes fall back to "file".
_KIND_BY_SUFFIX = {
    ".py": "python",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".sh": "shell",
    ".ps1": "powershell",
    ".txt": "text",
    ".cfg": "config",
    ".ini": "config",
}


# ---------------------------------------------------------------------------
# Classification + purpose extraction
# ---------------------------------------------------------------------------


def classify(rel_path: Path) -> str:
    """Return a coarse 'kind' for a file from its location and extension."""
    if "tests" in rel_path.parts or rel_path.name.startswith("test_"):
        return "test"
    return _KIND_BY_SUFFIX.get(rel_path.suffix.lower(), "file")


def load_purposes(root: Path) -> dict[str, str]:
    """Load the agent-maintained ``{path: purpose}`` override map (keys with ``_`` skipped).

    Lives at ``.aspis/index/PURPOSES.json``; absent or malformed → empty map. JSON
    so it parses with the standard library (no pyyaml dependency).
    """
    path = root / ".aspis" / "index" / "PURPOSES.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: str(v) for k, v in data.items() if not k.startswith("_") and isinstance(v, str)}


def purpose_of(path: Path) -> str:
    """Derive a one-line purpose from the file itself (docstring / first comment)."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    suffix = path.suffix.lower()
    if suffix == ".py":
        return _python_purpose(text)
    if suffix == ".md":
        return _markdown_purpose(text)
    return _comment_purpose(text)


def _first_line(text: str) -> str:
    """Return the first non-empty, stripped line of *text*."""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _python_purpose(text: str) -> str:
    """First line of the module docstring, via the stdlib ast parser."""
    try:
        doc = ast.get_docstring(ast.parse(text))
    except SyntaxError:
        return ""
    return _first_line(doc) if doc else ""


def _markdown_purpose(text: str) -> str:
    """First heading/line of a markdown file, with leading '#' removed."""
    return _first_line(text).lstrip("#").strip()


def _comment_purpose(text: str) -> str:
    """First leading '#' comment line (yaml/toml/shell), '#' removed."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return stripped.lstrip("#").strip() if stripped.startswith("#") else ""
    return ""


# ---------------------------------------------------------------------------
# Scan + emit
# ---------------------------------------------------------------------------


def scan(root: Path) -> list[tuple[str, str, str]]:
    """Walk *root* and return sorted (relpath, kind, purpose) for each file."""
    purposes = load_purposes(root)
    entries: list[tuple[str, str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        # Explicit override wins; otherwise extract from the file itself.
        purpose = purposes.get(rel.as_posix()) or purpose_of(path)
        entries.append((rel.as_posix(), classify(rel), purpose))
    return entries


def _quote(value: str) -> str:
    """Quote a string as a safe double-quoted YAML scalar."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def to_yaml(entries: list[tuple[str, str, str]]) -> str:
    """Render the registry entries as a YAML document."""
    lines = ["# Generated by build_registry.py — do not edit by hand.", "files:"]
    for rel, kind, purpose in entries:
        lines.append(f"  {_quote(rel)}:")
        lines.append(f"    kind: {kind}")
        lines.append(f"    purpose: {_quote(purpose)}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Scan the project root and write the file registry."""
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path.cwd()

    entries = scan(root)
    registry = root / ".aspis" / "index" / "FILE_REGISTRY.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(to_yaml(entries), encoding="utf-8")

    print(f"wrote {registry.relative_to(root).as_posix()} ({len(entries)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
