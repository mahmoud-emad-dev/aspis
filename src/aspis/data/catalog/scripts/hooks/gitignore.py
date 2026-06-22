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


def ensure(root: Path, stack: str | None = None) -> bool:
    """Write/refresh the stack's ignore block. Returns True if `.gitignore` changed."""
    stack = stack or detect_stack(root)
    if stack == "unknown":
        return False
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


def main(argv: list[str] | None = None) -> int:
    """`aspis gitignore [stack]` core: ensure the block; exit 0 always."""
    args = argv if argv is not None else sys.argv[1:]
    root = _git.repo_root()
    stack = args[0] if args else detect_stack(root)
    changed = ensure(root, stack)
    state = "updated" if changed else "already current"
    print(f"[aspis] .gitignore {state} ({stack})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
