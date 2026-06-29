"""Lightweight, deterministic project detection used by init and bootstrap.

Distinguishes a fresh/empty target from an existing-code project (they follow
different workflows) and identifies the stack from marker files.
"""

from __future__ import annotations

import difflib
import re
from functools import lru_cache
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.runtimes import runtime_dirs

# Ignored when deciding whether a directory is "empty" for ASPIS purposes:
# version control, the brain, and every runtime's generated dir (asked of the
# adapters, never hardcoded).
_IGNORED = {".git", BRAIN_DIR, *runtime_dirs()}

# Minimal built-in stack set — used ONLY if data/stacks.yaml is missing or corrupt, so
# detection never dies on a bad file. The real source of truth is data/stacks.yaml.
_FALLBACK_STACKS: dict[str, dict] = {
    "python": {
        "markers": ["pyproject.toml", "requirements.txt"],
        "aliases": ["py"],
        "gitignore": "python",
    },
    "node": {"markers": ["package.json"], "aliases": ["js", "ts", "node.js"], "gitignore": "node"},
    "rust": {"markers": ["Cargo.toml"], "gitignore": "rust"},
    "go": {"markers": ["go.mod"], "gitignore": "go"},
}


@lru_cache(maxsize=1)
def _stacks() -> dict[str, dict]:
    """Load the stack definitions from data/stacks.yaml; fall back when missing/corrupt."""
    try:
        import yaml

        from aspis import resources

        data = yaml.safe_load((resources.data_dir() / "stacks.yaml").read_text(encoding="utf-8"))
        stacks = data.get("stacks") if isinstance(data, dict) else None
        if isinstance(stacks, dict) and stacks:
            return {name: (spec or {}) for name, spec in stacks.items()}
    except Exception:  # pragma: no cover - degraded mode (missing/corrupt data file)
        pass
    return _FALLBACK_STACKS


@lru_cache(maxsize=1)
def _maps() -> tuple[list[tuple[str, str]], dict[str, str], list[str], dict[str, str]]:
    """Derive (markers, aliases, vocab, gitignore_of) from the stack definitions."""
    markers: list[tuple[str, str]] = []
    aliases: dict[str, str] = {}
    vocab: list[str] = []
    gitignore_of: dict[str, str] = {}
    for name, spec in _stacks().items():
        for marker in spec.get("markers", []):
            markers.append((marker, name))
        for alias in spec.get("aliases", []):
            aliases[alias] = name
        vocab.append(name)
        vocab.extend(spec.get("aliases", []))
        gitignore_of[name] = spec.get("gitignore", "")
    return markers, aliases, vocab, gitignore_of


def _stack_tokens(raw: str) -> list[str]:
    """Split a free-typed stack into lowercase tokens (space/comma/slash/+ separated)."""
    return [t for t in re.split(r"[\s,+/|]+", (raw or "").strip().lower()) if t]


def normalize_stack(raw: str) -> str:
    """Clean user-typed stack into a readable, de-typo'd list (for the manifest).

    ``"py fastapi postgres"`` -> ``"python, fastapi, postgresql"``; fixes near typos
    (``"pyton"`` -> ``"python"``). Frameworks/databases are kept (they describe the
    project); only spelling is canonicalised. Returns ``""`` for empty/unknown input.
    """
    _, aliases, vocab, _ = _maps()
    out: list[str] = []
    seen: set[str] = set()
    for token in _stack_tokens(raw):
        word = aliases.get(token, token)  # alias -> canonical name
        if word not in vocab:
            match = difflib.get_close_matches(word, vocab, n=1, cutoff=0.8)
            word = match[0] if match else word
        word = aliases.get(word, word)  # a fuzzy hit on an alias resolves to its name
        if word and word not in seen:
            seen.add(word)
            out.append(word)
    return ", ".join(out)


def gitignore_stacks(raw: str) -> list[str]:
    """The base stacks a ``.gitignore`` actually applies to, from free-typed input.

    ``"python fastapi postgres"`` -> ``["python"]`` (fastapi folds into python via its
    ``gitignore:`` key, postgres has none). Reads the fold from data/stacks.yaml; used
    by the gitignore hook to write one ignore block per real stack.
    """
    _, _, _, gitignore_of = _maps()
    out: list[str] = []
    seen: set[str] = set()
    for word in normalize_stack(raw).split(", "):
        base = gitignore_of.get(word, "")
        if base and base not in seen:
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


def detect_stacks(root: Path) -> list[str]:
    """Every stack with at least one marker file present, in definition order (may be empty).

    The basis for confidence: one match is a confident guess, several is ambiguous, none
    is unknown. ``detect_stack`` stays the single-value convenience over this.
    """
    markers, _, _, _ = _maps()
    found: list[str] = []
    for marker, stack in markers:
        if stack not in found and (root / marker).exists():
            found.append(stack)
    return found


def detect_stack(root: Path) -> str:
    """Return the project's stack from the marker files in data/stacks.yaml, or 'unknown'."""
    found = detect_stacks(root)
    return found[0] if found else "unknown"
