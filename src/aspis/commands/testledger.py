"""``aspis tests`` — a file-first test ledger so a passing test is not re-run for nothing.

The problem: a reviewer or a later task re-runs tests that already passed and have not
changed — wasted time and tokens. The ledger records a test result against a *fingerprint*
of the files that were tested (their content), keyed by a scope (default: the active
feature). Before running, an agent asks ``aspis tests check <paths>``: if the fingerprint
still matches a recorded pass, the cached verdict is returned (exit 0) and the run is
skipped; if anything relevant changed — or nothing is recorded — it reports stale (exit 1)
and the tests must run, after which ``aspis tests record`` updates the ledger.

The ledger lives at ``.aspis/index/test-ledger.json`` (a local cache — gitignored). It is
deliberately simple and file-first; richer per-run history belongs to the future tracing
spine, not here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date as _date
from pathlib import Path

from aspis import project

_LEDGER = (".aspis", "index", "test-ledger.json")


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``tests`` verb (with ``check`` / ``record`` actions)."""
    parser = subparsers.add_parser(
        "tests",
        help="Test ledger: skip re-running tests whose files have not changed since they passed.",
    )
    parser.add_argument(
        "action", choices=("check", "record"), help="check a cache or record a run."
    )
    parser.add_argument("paths", nargs="+", help="The code/test files this run covers.")
    parser.add_argument(
        "--scope", help="Ledger key (default: the active feature id, else 'default')."
    )
    parser.add_argument(
        "--result", choices=("pass", "fail"), help="Result to record (record only)."
    )
    parser.add_argument("--detail", default="", help="Optional note stored with a recorded run.")
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.set_defaults(func=_run)


def _files(root: Path, paths: list[str]) -> list[Path]:
    """Expand the given paths to a sorted list of existing files (dirs are walked)."""
    found: set[Path] = set()
    for raw in paths:
        target = (root / raw).resolve()
        if target.is_file():
            found.add(target)
        elif target.is_dir():
            found.update(p for p in target.rglob("*") if p.is_file())
    return sorted(found)


def fingerprint(root: Path, paths: list[str]) -> str:
    """Content fingerprint of the covered files — changes iff a covered file's bytes change."""
    digest = hashlib.sha256()
    for path in _files(root, paths):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _scope(root: Path, explicit: str | None) -> str:
    """Resolve the ledger key: explicit, else the active feature id, else 'default'."""
    if explicit:
        return explicit
    pointer = root / ".aspis" / "current" / "active_feature.json"
    try:
        data = json.loads(pointer.read_text(encoding="utf-8"))
        return str(data.get("id") or "default")
    except (OSError, ValueError):
        return "default"


def _load(root: Path) -> dict:
    """Read the ledger, returning ``{}`` when absent or unreadable."""
    try:
        data = json.loads((root.joinpath(*_LEDGER)).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _run(args: argparse.Namespace) -> int:
    """Check or record a scope's test result against the covered files' fingerprint."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    scope = _scope(root, args.scope)
    current = fingerprint(root, args.paths)
    ledger = _load(root)
    entry = ledger.get(scope) if isinstance(ledger.get(scope), dict) else None

    if args.action == "check":
        if entry and entry.get("fingerprint") == current and entry.get("result") == "pass":
            print(f"cached: pass — '{scope}' unchanged since {entry.get('date')}; skip re-running.")
            return 0
        reason = "no record" if not entry else "files changed or last run failed"
        print(f"stale: '{scope}' must be tested ({reason}).")
        return 1

    # record
    if not args.result:
        print("record needs --result pass|fail.")
        return 1
    ledger[scope] = {
        "result": args.result,
        "fingerprint": current,
        "date": _date.today().isoformat(),
        "files": [str(p.relative_to(root).as_posix()) for p in _files(root, args.paths)],
        "detail": args.detail,
    }
    target = root.joinpath(*_LEDGER)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"recorded: {args.result} for '{scope}' ({len(ledger[scope]['files'])} file(s)).")
    return 0
