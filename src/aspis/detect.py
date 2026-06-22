"""Lightweight, deterministic project detection used by init and bootstrap.

Distinguishes a fresh/empty target from an existing-code project (they follow
different workflows) and identifies the stack from marker files.
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.runtimes import runtime_dirs

# Ignored when deciding whether a directory is "empty" for ASPIS purposes:
# version control, the brain, and every runtime's generated dir (asked of the
# adapters, never hardcoded).
_IGNORED = {".git", BRAIN_DIR, *runtime_dirs()}

# Marker files that identify a project's stack (first match wins).
_STACK_MARKERS = [
    ("pyproject.toml", "python"),
    ("requirements.txt", "python"),
    ("setup.py", "python"),
    ("package.json", "node"),
    ("tsconfig.json", "node"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
    ("pom.xml", "java"),
    ("build.gradle", "java"),
    ("Gemfile", "ruby"),
    ("composer.json", "php"),
]

# Spelling fixes / abbreviations for the *display* form (kept in the manifest as the
# user means it — frameworks and databases stay, only the spelling is canonicalised).
_DISPLAY_ALIASES = {
    "py": "python",
    "python3": "python",
    "ts": "typescript",
    "js": "javascript",
    "nodejs": "node",
    "node.js": "node",
    "rs": "rust",
    "golang": "go",
    "c++": "cpp",
    "c#": "dotnet",
    "csharp": "dotnet",
    "postgres": "postgresql",
    "psql": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "nextjs": "next",
    "reactjs": "react",
}
# The vocabulary used to forgive small typos (fuzzy match) on free-typed input.
_VOCAB = [
    "python",
    "node",
    "typescript",
    "javascript",
    "rust",
    "go",
    "java",
    "c",
    "cpp",
    "ruby",
    "php",
    "dotnet",
    "fastapi",
    "django",
    "flask",
    "react",
    "next",
    "vue",
    "svelte",
    "express",
    "nestjs",
    "rails",
    "laravel",
    "postgresql",
    "mysql",
    "sqlite",
    "redis",
    "mongodb",
    "docker",
    "kubernetes",
    "graphql",
    "tailwind",
]
# Framework / database -> the base stack whose .gitignore actually applies ("" = none).
_GITIGNORE_BASE = {
    "fastapi": "python",
    "django": "python",
    "flask": "python",
    "pandas": "python",
    "typescript": "node",
    "javascript": "node",
    "react": "node",
    "next": "node",
    "vue": "node",
    "svelte": "node",
    "express": "node",
    "nestjs": "node",
    "tailwind": "node",
    "rails": "ruby",
    "laravel": "php",
    "postgresql": "",
    "mysql": "",
    "sqlite": "",
    "redis": "",
    "mongodb": "",
    "docker": "",
    "kubernetes": "",
    "graphql": "",
}
# Stacks we have a real .gitignore for (offline cache or the Toptal API keyword).
_GITIGNORE_KNOWN = {"python", "node", "rust", "go", "java", "c", "cpp", "ruby", "php"}


def _stack_tokens(raw: str) -> list[str]:
    """Split a free-typed stack into lowercase tokens (space/comma/slash/+ separated)."""
    return [t for t in re.split(r"[\s,+/|]+", (raw or "").strip().lower()) if t]


def normalize_stack(raw: str) -> str:
    """Clean user-typed stack into a readable, de-typo'd list (for the manifest).

    ``"py fastapi postgres"`` -> ``"python, fastapi, postgresql"``; fixes near typos
    (``"pyton"`` -> ``"python"``). Frameworks/databases are kept (they describe the
    project); only spelling is canonicalised. Returns ``""`` for empty/unknown input.
    """
    out: list[str] = []
    seen: set[str] = set()
    for token in _stack_tokens(raw):
        word = _DISPLAY_ALIASES.get(token, token)
        if word not in _VOCAB:
            match = difflib.get_close_matches(word, _VOCAB, n=1, cutoff=0.8)
            word = match[0] if match else word
        if word and word not in seen:
            seen.add(word)
            out.append(word)
    return ", ".join(out)


def gitignore_stacks(raw: str) -> list[str]:
    """The base stacks a ``.gitignore`` actually applies to, from free-typed input.

    ``"python fastapi postgres"`` -> ``["python"]`` (fastapi folds into python,
    postgres has no standard ignore). Used by the gitignore hook to write one ignore
    block per real stack.
    """
    out: list[str] = []
    seen: set[str] = set()
    for word in normalize_stack(raw).split(", "):
        base = _GITIGNORE_BASE.get(word, word)
        if base in _GITIGNORE_KNOWN and base not in seen:
            seen.add(base)
            out.append(base)
    return out


def project_mode(root: Path) -> str:
    """Return 'empty' if *root* has no project content yet, else 'existing'."""
    if not root.is_dir():
        return "empty"
    for child in root.iterdir():
        if child.name not in _IGNORED:
            return "existing"
    return "empty"


def detect_stack(root: Path) -> str:
    """Return the project's stack from marker files, or 'unknown'."""
    for marker, stack in _STACK_MARKERS:
        if (root / marker).exists():
            return stack
    return "unknown"
