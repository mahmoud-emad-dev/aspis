#!/usr/bin/env python3
"""`.gitignore` maintainer — canonical patterns by stack (FR-006).

Detects the project stack (reusing ``aspis.detect`` when importable, else local
marker files), then resolves the canonical ignore body **offline-first**: the
bundled cache under ``ignore/`` (the common stacks ship with the catalog, so the
common case is instant and works with no network), and only when a stack is not
cached does it fetch from the Toptal gitignore API (a valid stack keyword like
``python``/``node``) and cache the result for next time. The body is written into a
single marked block in ``.gitignore``, so re-running is a no-op once current.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git  # noqa: E402

_API = "https://www.toptal.com/developers/gitignore/api/{stack}"
_CACHE = Path(__file__).resolve().parent / "ignore"
_MARKERS = {
    "pyproject.toml": "python",
    "package.json": "node",
    "Cargo.toml": "rust",
    "go.mod": "go",
}
_BEGIN = "# >>> aspis gitignore ({stack}) >>>"
_END = "# <<< aspis gitignore <<<"


def project_root() -> Path:
    """The project whose `.gitignore` we maintain.

    The nearest ancestor of the cwd that holds a `.aspis/` brain, else the enclosing
    git repo, else the cwd. Anchoring on `.aspis` keeps the ignore block in the
    project's own `.gitignore` even when the project is not its own git repo but sits
    inside a larger one (e.g. a home directory that is itself a repo) — otherwise the
    block would land in the wrong, outer `.gitignore`.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".aspis").is_dir():
            return candidate
    return _git.repo_root()


def detect_stack(root: Path) -> str:
    """Project stack, reusing the engine's detector when available."""
    try:
        from aspis.detect import detect_stack as _detect  # DRY when aspis is importable

        return _detect(root)
    except Exception:  # pragma: no cover - degraded mode (bare interpreter)
        return next((s for m, s in _MARKERS.items() if (root / m).exists()), "unknown")


def fetch(stack: str) -> str | None:
    """Canonical ignore body for *stack*, offline-first: cache, then the Toptal API.

    The bundled cache is authoritative for the stacks that ship with the catalog
    (instant, no network). Only an uncached stack reaches out to the API, and a
    successful fetch is cached so it is offline-fast thereafter.
    """
    cached = _CACHE / f"{stack}.gitignore"
    if cached.is_file():
        return cached.read_text(encoding="utf-8")
    try:
        with urllib.request.urlopen(_API.format(stack=stack), timeout=5) as response:
            body = response.read().decode("utf-8")
        _CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_text(body, encoding="utf-8")
        return body
    except Exception:
        return None


def resolve_stacks(raw: str, root: Path) -> list[str]:
    """Base stacks to write ignore blocks for, from free-typed input (or detection).

    Reuses the engine's normalizer (aliases + fuzzy match + multi-stack) when aspis is
    importable — so ``"py fastapi postgres"`` resolves to ``["python"]`` and ``"noed"``
    is forgiven to ``node``. Falls back to a small alias map for a bare interpreter.
    """
    raw = (raw or "").strip()
    try:
        from aspis.detect import gitignore_stacks  # DRY when aspis is importable

        return gitignore_stacks(raw or detect_stack(root))
    except Exception:  # pragma: no cover - degraded mode (bare interpreter)
        token = (raw.split() or [detect_stack(root)])[0].lower()
        token = {"py": "python", "ts": "node", "js": "node", "golang": "go"}.get(token, token)
        return [token] if token and token != "unknown" else []


def _ensure_one(root: Path, stack: str) -> bool:
    """Write/refresh ONE stack's ignore block. Returns True if `.gitignore` changed."""
    body = fetch(stack)
    if not body:
        return False
    block = f"{_BEGIN.format(stack=stack)}\n{body.strip()}\n{_END}\n"
    path = root / ".gitignore"
    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    pattern = re.compile(
        re.escape(_BEGIN.format(stack=stack)) + r".*?" + re.escape(_END) + r"\n?", re.DOTALL
    )
    updated = (
        pattern.sub(block, current)
        if pattern.search(current)
        else (current.rstrip() + "\n\n" + block if current else block)
    )
    if updated == current:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def ensure(root: Path, stack: str | None = None) -> bool:
    """Write/refresh an ignore block per resolved stack. Returns True if anything changed."""
    changed = False
    for one in resolve_stacks(stack or "", root):
        changed = _ensure_one(root, one) or changed
    return changed


def main(argv: list[str] | None = None) -> int:
    """`aspis gitignore [stack ...]` core: ensure a block per stack; exit 0 always.

    Accepts free-typed input, joined across args: ``aspis gitignore python fastapi``
    and ``aspis gitignore "py, fastapi"`` both resolve to the python block.
    """
    args = argv if argv is not None else sys.argv[1:]
    root = project_root()
    raw = " ".join(args) if args else detect_stack(root)
    stacks = resolve_stacks(raw, root)
    changed = ensure(root, raw)
    label = ", ".join(stacks) or "no known stack"
    state = "updated" if changed else "already current"
    print(f"[aspis] .gitignore {state} ({label})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
