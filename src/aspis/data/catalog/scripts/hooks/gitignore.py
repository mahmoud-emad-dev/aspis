#!/usr/bin/env python3
"""`.gitignore` maintainer — canonical patterns by stack (FR-006).

Detects the project stack (reusing ``aspis.detect`` when importable, else local
marker files), then fetches the canonical ignore body from the Toptal gitignore
API. The API needs a valid stack keyword (``python``, ``node``, …). When the
network is unavailable it falls back to a bundled offline cache under ``ignore/``;
a successful fetch refreshes that cache. The body is written into a single marked
block in ``.gitignore``, so re-running is a no-op once current.
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
    """Canonical ignore body for *stack*: Toptal API, else the offline cache."""
    try:
        with urllib.request.urlopen(_API.format(stack=stack), timeout=5) as response:
            body = response.read().decode("utf-8")
        _CACHE.mkdir(parents=True, exist_ok=True)
        (_CACHE / f"{stack}.gitignore").write_text(body, encoding="utf-8")
        return body
    except Exception:
        cached = _CACHE / f"{stack}.gitignore"
        return cached.read_text(encoding="utf-8") if cached.is_file() else None


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
