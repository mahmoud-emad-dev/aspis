#!/usr/bin/env python3
"""Build ``.aspis/index/FILE_REGISTRY.yaml`` for a project.

Self-contained: standard library only, so it runs in any project that has
Python, with no dependency on a global ``aspis`` install. It scans the project,
classifies each file, derives a one-line purpose, and writes a YAML registry. It
regenerates the whole file from a fresh scan (idempotent), so there is no fragile
merge step.

A file's purpose comes from three layers, resolved per file. All project-supplied
purposes live in ONE file, ``.aspis/config/purposes.json`` (agents and humans edit
it), with shape ``{"files": {...}, "names": {...}, "patterns": {...}}``:
  1. ``files`` — explicit per-path purposes (``{relpath: purpose}``), highest
     priority; where an agent/human registers a file that cannot carry a docstring
     or whose extracted line is weak;
  2. ``names`` + ``patterns`` — the common-purpose map (by basename, then glob),
     extending/overriding the built-in defaults. For well-known meta-files whose own
     first line is a title/section rather than a purpose (README, LICENSE,
     .gitignore, lockfiles, CI workflows, ...) this map is *authoritative* and beats
     layer 3; for everything else it is the fallback when layer 3 is empty;
  3. the file's own module docstring / first heading / leading comment.
Nothing matched ⇒ blank. ``--check`` reports every such file so an agent/human (or a
background cheap-model helper) registers it in ``files``; no file should stay blank.

Usage:
    python3 build_registry.py [project_root]            # write the registry
    python3 build_registry.py [project_root] --check    # list files with no purpose; exit 1 if any
"""

from __future__ import annotations

import ast
import fnmatch
import json
import sys
from pathlib import Path

import _common

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


# Static common-purpose map (layer 2). Built-in defaults for well-known files,
# project-overridable via the "names" section of .aspis/config/purposes.json. Keys are basenames.
_COMMON_EXACT = {
    "README.md": "Project overview and entry point",
    "AGENTS.md": "Agent runtime guide — entry context for coding agents",
    "CLAUDE.md": "Claude Code runtime guide",
    "CHANGELOG.md": "Project changelog",
    "CONTRIBUTING.md": "Contribution guide",
    "LICENSE": "Project license",
    ".gitignore": "Git ignore rules",
    ".gitattributes": "Git attributes",
    ".editorconfig": "Editor formatting rules",
    "pyproject.toml": "Python project metadata and tooling config",
    "setup.cfg": "Python packaging/tooling config",
    "package.json": "Node project metadata and dependencies",
    "tsconfig.json": "TypeScript compiler config",
    "Makefile": "Build/automation targets",
    "Dockerfile": "Container image definition",
    ".env.example": "Example environment variables",
}
# Glob patterns (matched against the basename, then the posix relpath); first wins.
_COMMON_PATTERNS = {
    "*.lock": "Dependency lockfile (generated)",
    "LICENSE*": "Project license",
    "docker-compose*.yml": "Container orchestration config",
    "docker-compose*.yaml": "Container orchestration config",
    ".github/workflows/*.yml": "CI workflow",
    ".github/workflows/*.yaml": "CI workflow",
}
# Known meta-files whose own first line is a title/section, not a purpose: for
# these the common map is authoritative (beats the file's extracted line).
_AUTHORITATIVE_NAMES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    "pyproject.toml",
    "setup.cfg",
    "package.json",
    "tsconfig.json",
    "Makefile",
    "Dockerfile",
}
_AUTHORITATIVE_PATTERNS = ("*.lock", "LICENSE*", ".github/workflows/*")


# ---------------------------------------------------------------------------
# Classification + purpose extraction
# ---------------------------------------------------------------------------


def classify(rel_path: Path) -> str:
    """Return a coarse 'kind' for a file from its location and extension."""
    if "tests" in rel_path.parts or rel_path.name.startswith("test_"):
        return "test"
    return _KIND_BY_SUFFIX.get(rel_path.suffix.lower(), "file")


def _str_map(section: object) -> dict[str, str]:
    """Coerce a JSON object into a ``{str: str}`` map, skipping ``_`` comment keys."""
    if not isinstance(section, dict):
        return {}
    return {k: str(v) for k, v in section.items() if not k.startswith("_")}


def load_purpose_config(root: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Return (files, names, patterns) purpose maps: built-in defaults + project config.

    One file holds all three: ``.aspis/config/purposes.json`` with shape
    ``{"files": {relpath: purpose}, "names": {basename: purpose}, "patterns": {glob: purpose}}``.
    ``files`` are explicit per-path purposes (agents register non-self-documenting files
    here); ``names``/``patterns`` are the common map and extend/override the built-in
    defaults. Absent or malformed → defaults only. JSON so it parses with the standard
    library (no pyyaml dependency).
    """
    names = dict(_COMMON_EXACT)
    patterns = dict(_COMMON_PATTERNS)
    files: dict[str, str] = {}
    path = root / ".aspis" / "config" / "purposes.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return files, names, patterns
    if isinstance(data, dict):
        files.update(_str_map(data.get("files")))
        names.update(_str_map(data.get("names")))
        patterns.update(_str_map(data.get("patterns")))
    return files, names, patterns


def common_purpose(rel: str, name: str, exact: dict[str, str], patterns: dict[str, str]) -> str:
    """Look up a file's purpose in the common map: exact basename, then glob (first wins)."""
    if name in exact:
        return exact[name]
    for pattern, purpose in patterns.items():
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern):
            return purpose
    return ""


def is_authoritative(rel: str, name: str) -> bool:
    """Whether the common map should win over the file's own extracted line."""
    if name in _AUTHORITATIVE_NAMES:
        return True
    return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel, p) for p in _AUTHORITATIVE_PATTERNS)


def resolve_purpose(
    rel: str,
    path: Path,
    files: dict[str, str],
    names: dict[str, str],
    patterns: dict[str, str],
) -> str:
    """Resolve a file's purpose across the three layers (see the module docstring)."""
    if rel in files:  # layer 1: explicit per-path purpose
        return files[rel]
    name = path.name
    common = common_purpose(rel, name, names, patterns)
    if common and is_authoritative(rel, name):  # layer 2 wins for known meta-files
        return common
    extracted = purpose_of(path)  # layer 3: the file's own docstring/heading/comment
    return extracted or common  # else fall back to the common map (or blank)


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
    files, names, patterns = load_purpose_config(root)
    entries: list[tuple[str, str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        purpose = resolve_purpose(rel.as_posix(), path, files, names, patterns)
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


def missing_purpose(entries: list[tuple[str, str, str]]) -> list[str]:
    """Relative paths of files that resolved to no purpose (coverage gap)."""
    return [rel for rel, _kind, purpose in entries if not purpose]


def main(argv: list[str] | None = None) -> int:
    """Scan the project root and write the file registry, or check purpose coverage."""
    _common.force_utf8_stdio()
    args = list(argv if argv is not None else sys.argv[1:])
    check = "--check" in args
    if check:
        args.remove("--check")
    root = Path(args[0]).resolve() if args else Path.cwd()

    entries = scan(root)
    gaps = missing_purpose(entries)

    if check:
        if gaps:
            print(f"{len(gaps)} file(s) have no purpose — register in .aspis/config/purposes.json:")
            for rel in gaps:
                print(f"  - {rel}")
            return 1
        print(f"OK: all {len(entries)} files have a purpose")
        return 0

    registry = root / ".aspis" / "index" / "FILE_REGISTRY.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(to_yaml(entries), encoding="utf-8")

    print(f"wrote {registry.relative_to(root).as_posix()} ({len(entries)} files)")
    if gaps:
        print(f"  note: {len(gaps)} file(s) have no purpose; run --check to list them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
