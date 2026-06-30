"""``aspis runtime status`` — the runtime-integrity lane (F-022 / D-023).

The runtime dirs (``.opencode``/``.claude``) are catalog-rendered and tracked by **no git**.
Their change record is the export snapshot (a content hash per file) plus the append-only
change-log the export writer keeps. This verb reads that record and reports it — so the user
can see what ASPIS changed in the runtimes, when, without a git history. Read-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.runtimes import runtime_dirs

_LOG = Path("current") / "export-log.jsonl"
_SNAPSHOT = Path("current") / "export-snapshot.json"


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``runtime`` verb (``status`` action)."""
    parser = subparsers.add_parser(
        "runtime",
        help="Inspect the runtime-integrity record (.opencode/.claude change-log + hashes).",
    )
    sub = parser.add_subparsers(dest="runtime_action")
    s = sub.add_parser("status", help="Show recorded runtime changes (no git; from the log).")
    s.add_argument("path", nargs="?", default=".", help="Project directory (default: current).")
    s.add_argument("-n", "--number", type=int, default=10, help="Recent changes to show.")
    parser.set_defaults(func=_run)


def _is_runtime_path(path: str) -> bool:
    """True when *path* lives under a runtime dir (the no-git, hash-tracked lane)."""
    return any(path.startswith(f"{d}/") for d in runtime_dirs())


def _run(args: argparse.Namespace) -> int:
    """Report the runtime integrity record: tracked file count + recent system-made changes."""
    root = Path(getattr(args, "path", ".") or ".").resolve()
    brain = root / BRAIN_DIR
    if not brain.is_dir():
        print("not an ASPIS project (no .aspis/) -- run `aspis init` first.")
        return 1

    snapshot = brain / _SNAPSHOT
    tracked = 0
    if snapshot.is_file():
        try:
            paths = json.loads(snapshot.read_text(encoding="utf-8")).get("paths", {})
            tracked = sum(1 for p in paths if _is_runtime_path(p))
        except (OSError, json.JSONDecodeError):
            tracked = 0

    log = brain / _LOG
    writes: list[dict] = []
    if log.is_file():
        for line in log.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if _is_runtime_path(entry.get("path", "")) and entry.get("action") == "wrote":
                writes.append(entry)

    dirs = ", ".join(runtime_dirs())
    print(f"runtime integrity ({dirs}) — tracked by hashes + change-log, no git")
    print(f"  files under integrity: {tracked}")
    print(f"  recorded changes:      {len(writes)}")
    number = getattr(args, "number", 10) or 10
    if writes:
        print(f"  last change:           {writes[-1]['timestamp']}")
        print(f"  recent (last {number}):")
        for entry in writes[-number:]:
            print(f"    {entry['timestamp']}  {entry['kind']:<9} {entry['path']}")
    else:
        print("  (no runtime changes recorded yet)")
    print(f"  record: {(_SNAPSHOT.as_posix())} + {(_LOG.as_posix())} under .aspis/")
    return 0
