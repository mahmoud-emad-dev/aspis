"""``aspis validate-index`` — freshness check over the .aspis/index/ files.

Two machine-generated artifacts live under ``.aspis/index/`` and can drift
away from reality when someone adds or removes files without regenerating
them. This verb detects that drift in two passes:

1. ``FILE_REGISTRY.yaml`` — every entry's path must still exist on disk.
   A registered path that is missing is **stale** and means the registry
   needs regenerating (or the file was deleted without updating it).
2. ``CODE_MAP.md`` — every Python file listed must still exist, and its
   recorded line count must be within 10% of the actual line count. A
   drift greater than 10% means the code map needs regenerating (or
   someone added / removed a lot of code without re-running the builder).

Exits 0 when every check passes; 1 when any entry is stale. ``--dry-run``
runs the full check and prints the report, but always exits 0, so it is
safe to use for status-only display. Stdlib plus ``yaml`` (a project
dependency used everywhere under ``aspis/``).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Per-entry status labels. ASCII-safe for any console.
_LABEL_FRESH = "FRESH"
_LABEL_STALE_MISSING = "STALE-MISSING"
_LABEL_STALE_COUNT = "STALE-COUNT"

#: A line-count drift of more than 10% means the recorded value is no
#: longer accurate enough to be a useful skeleton summary, and the map
#: should be regenerated. The builder writes these counts on every regen
#: (see ``build_code_map.py:describe``), so a real divergence here is
#: almost always a sign that the map is stale, not that the file changed
#: by that much in a way that matters.
_COUNT_TOLERANCE = 0.10

#: How many parents to walk up looking for ``.aspis/`` before giving up
#: and falling back to CWD. Ten is plenty for a normal repo and stops
#: the loop on accidental root-relative paths.
_MAX_WALK_UP = 10

#: A file skeleton header in the code map. The builder's render output
#: is ``### `path/to/file.py`  (NNN lines)`` — exactly two spaces
#: between the closing backtick and the parenthesised count.
_FILE_HEADER_RE = re.compile(
    r"^###\s+`(?P<path>[^`]+)`\s+\((?P<count>\d+)\s+lines?\)"
)


# ---------------------------------------------------------------------------
# Project root + index loading
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    """The directory containing ``.aspis/`` — start at CWD, walk up.

    Walks up to ``_MAX_WALK_UP`` parents looking for ``.aspis/`` so the
    verb works from a subdirectory of the project (where IDEs and
    editors typically run a terminal) as well as from the project root
    itself. Falls back to CWD when not found — the caller will then get
    a clear "index directory not found" error.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents[:_MAX_WALK_UP]):
        if (candidate / ".aspis").is_dir():
            return candidate
    return cwd


def _load_registry(index_dir: Path) -> dict[str, dict]:
    """Read ``FILE_REGISTRY.yaml``; return the inner ``files:`` mapping.

    The contract is the ``files:`` dict — every other key in the YAML
    (the auto-generated header comment) is ignored. The mapping is
    dict-of-dict in YAML's natural shape: ``{path: {kind, purpose}}``.
    Quoted-key files (``".coverage"``) come back as plain strings.
    """
    registry_path = index_dir / "FILE_REGISTRY.yaml"
    with registry_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    files = data.get("files") or {}
    if not isinstance(files, dict):
        return {}
    # ``kind`` / ``purpose`` are not used by the freshness check itself;
    # we only need the keys. Normalise to ``str`` so YAML's mixed
    # scalar/sequence keys don't surprise us downstream.
    return {str(k): (v if isinstance(v, dict) else {}) for k, v in files.items()}


def _parse_code_map(code_map_path: Path) -> list[tuple[Path, int]]:
    """Extract ``(file_path, recorded_line_count)`` pairs from the code map.

    The builder (``build_code_map.render``) writes the **full** repo-relative
    path inside every ``### `path`  (N lines)`` entry; the ``## folder`` header
    is cosmetic grouping only and is never a path prefix. So each entry's path
    is taken verbatim.

    The regexes only match the builder's exact output, so a stray
    human-written ``## Section`` or ``### Heading`` in the file is
    silently ignored, which is the right behaviour for a generated
    artifact.
    """
    pairs: list[tuple[Path, int]] = []
    for line in code_map_path.read_text(encoding="utf-8").splitlines():
        file_match = _FILE_HEADER_RE.match(line)
        if file_match:
            rel = file_match.group("path")
            count = int(file_match.group("count"))
            pairs.append((Path(rel), count))
    return pairs


# ---------------------------------------------------------------------------
# Freshness checks
# ---------------------------------------------------------------------------


def _actual_line_count(path: Path) -> int:
    """Number of source lines in *path* — same formula the builder uses.

    ``text.count("\\n") + 1`` is the convention ``build_code_map.py``
    writes into the map. Matching it here means ``FRESH`` for a given
    file corresponds to "the builder's output would be unchanged" for
    that single number, so the tolerance check is meaningful.
    """
    return path.read_text(encoding="utf-8").count("\n") + 1


def _within_tolerance(recorded: int, actual: int) -> bool:
    """True when *actual* is within ``_COUNT_TOLERANCE`` of *recorded*.

    Treats a recorded value of 0 as a special case: any actual > 0 is
    drift, both 0 are fresh. A 0-line Python file in the registry is
    almost certainly a builder bug, but the validator should not mask
    that — it should report it.
    """
    if recorded == 0:
        return actual == 0
    return abs(actual - recorded) / recorded <= _COUNT_TOLERANCE


# ---------------------------------------------------------------------------
# CLI verb
# ---------------------------------------------------------------------------


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach the verb's options — shared between register() and __main__.

    Keeping the option wiring in one place means the module entry point
    (``python -m aspis.commands.validate_index``) and the parent CLI
    dispatch both see exactly the same flags.
    """
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Run the full check and print the report, but always exit 0 — "
            "use it for status-only display, not for gating."
        ),
    )


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``validate-index`` verb."""
    parser = subparsers.add_parser(
        "validate-index",
        help=(
            "Validate .aspis/index/: every FILE_REGISTRY entry exists on disk "
            "and every CODE_MAP line count is within 10%% of actual."
        ),
    )
    _add_arguments(parser)
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Walk both index files and print a per-entry pass/fail report.

    Returns 0 when every entry is fresh; 1 when any entry is stale. With
    ``--dry-run`` the full check still runs and prints, but the return
    is always 0.
    """
    root = _project_root()
    index_dir = root / ".aspis" / "index"

    if not index_dir.is_dir():
        print(f"index directory not found: {index_dir.as_posix()}")
        return 1

    registry = _load_registry(index_dir)
    code_map_path = index_dir / "CODE_MAP.md"
    code_map = _parse_code_map(code_map_path) if code_map_path.is_file() else []

    stale = 0
    total = 0

    # --- FILE_REGISTRY.yaml ---
    print(f"--- FILE_REGISTRY.yaml ({len(registry)} entries) ---")
    for rel_path in sorted(registry):
        total += 1
        if (root / rel_path).is_file():
            print(f"Registry: {rel_path} — {_LABEL_FRESH}")
        else:
            stale += 1
            print(f"Registry: {rel_path} — {_LABEL_STALE_MISSING}")

    # --- CODE_MAP.md ---
    print(f"\n--- CODE_MAP.md ({len(code_map)} Python files) ---")
    for rel, recorded in code_map:
        total += 1
        rel_posix = rel.as_posix()
        full = root / rel
        if not full.is_file():
            stale += 1
            print(f"Code-map: {rel_posix} — {_LABEL_STALE_MISSING}")
            continue
        try:
            actual = _actual_line_count(full)
        except OSError as exc:
            # File disappeared between is_file() and read_text() — race
            # with another process. Treat as missing rather than crashing
            # the whole sweep.
            stale += 1
            print(f"Code-map: {rel_posix} — {_LABEL_STALE_MISSING} (unreadable: {exc})")
            continue
        if _within_tolerance(recorded, actual):
            print(
                f"Code-map: {rel_posix} — {_LABEL_FRESH} "
                f"(recorded {recorded}, actual {actual})"
            )
        else:
            stale += 1
            print(
                f"Code-map: {rel_posix} — {_LABEL_STALE_COUNT} "
                f"(recorded {recorded}, actual {actual})"
            )

    print(f"\n{total - stale}/{total} entries fresh. {stale} stale.")

    if args.dry_run:
        return 0
    return 0 if stale == 0 else 1


if __name__ == "__main__":
    # Allow `python -m aspis.commands.validate_index [--dry-run]` for
    # ad-hoc runs in addition to the normal `aspis validate-index`
    # dispatch path. Use a fresh parser here (not register) so the user
    # gets `--help` and `--dry-run` without a subcommand prefix.
    _parser = argparse.ArgumentParser(description=__doc__)
    _add_arguments(_parser)
    raise SystemExit(_run(_parser.parse_args()))
