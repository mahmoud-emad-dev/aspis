"""``aspis preflight`` — the deterministic pre-task check every editing agent runs first.

Step 0 for an agent taking on work: confirm the working tree is clean (so parallel work never
collides), the current branch matches the active feature, and the feature pointer is valid. On a
problem it exits non-zero with a concrete next action, so the agent resolves or routes it before
editing — rather than starting on a dirty or mismatched state (the demo_win2 failure mode).

Generated brain churn (``.aspis/index/`` + ``.aspis/context/``, refreshed by the post-commit
hook) is expected and never counts as "dirty" — it folds into the next commit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aspis import findings, gitops, resources
from aspis.project import is_project

#: Status label, ASCII-safe for any console.
_LABELS = {"ok": "ok  ", "warn": "warn", "fail": "FAIL"}

#: Generated, post-commit-refreshed brain dirs — churn here is expected, not a blocker.
_GENERATED_PREFIXES = (".aspis/index/", ".aspis/context/")


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``preflight`` verb."""
    parser = subparsers.add_parser(
        "preflight", help="Pre-task check: clean tree, branch matches the active feature."
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.set_defaults(func=_run)


def _active_feature(root: Path) -> dict:
    """Read ``.aspis/current/active_feature.json`` (empty dict if absent or malformed)."""
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        return {}
    try:
        data = json.loads(pointer.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _dirty_paths(root: Path) -> list[str]:
    """Uncommitted paths, excluding the generated brain churn.

    Splits each porcelain line on its status code rather than slicing a fixed column —
    ``gitops.git`` strips the output, which can eat the leading space of the first line.
    """
    dirty: list[str] = []
    for line in gitops.git(root, "status", "--porcelain").splitlines():
        parts = line.split(maxsplit=1)  # ['XY', 'path'] — status code, then the path
        if len(parts) < 2:
            continue
        path = parts[1].strip().strip('"')
        if path and not path.startswith(_GENERATED_PREFIXES):
            dirty.append(path)
    return dirty


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    checks: list[tuple[str, str, str]] = []

    if not is_project(root):
        print("  [FAIL] project  not an ASPIS project — run `aspis init` first.")
        return 1
    if not gitops.has_git(root):
        print("  [FAIL] git      no git repository here — run `git init` first.")
        return 1

    # Clean tree (generated brain churn excluded).
    dirty = _dirty_paths(root)
    if dirty:
        shown = ", ".join(dirty[:5]) + (" …" if len(dirty) > 5 else "")
        checks.append(
            (
                "tree",
                "fail",
                f"{len(dirty)} uncommitted path(s): {shown} — commit finished work via the "
                "committer, or stash unrelated work, then re-run.",
            )
        )
    else:
        checks.append(("tree", "ok", "clean"))

    # Branch matches the active feature pointer.
    feature = _active_feature(root)
    current = gitops.git(root, "rev-parse", "--abbrev-ref", "HEAD")
    expected = feature.get("branch")
    fid = feature.get("id", "?")
    if not feature:
        checks.append(("feature", "ok", "no active feature pointer (nothing to match)"))
    elif expected and current and expected != current:
        checks.append(
            (
                "branch",
                "fail",
                f"on '{current}' but active feature {fid} is '{expected}' — "
                f"`git checkout {expected}` before working.",
            )
        )
    else:
        phase = feature.get("phase", "?")
        checks.append(("feature", "ok", f"{fid} ({phase}) on '{current}'"))

    # Open findings emitted by the deterministic guards. Fire-and-forget: in the default
    # `warn` mode they are advisory (surfaced, never blocking) so real work is never stopped —
    # the agent routes them to a fix on its next turn. Only `enforcement: block` makes them gate.
    open_findings = findings.load(root)
    if open_findings:
        enforcement = (resources.config("hooks.yaml", root) or {}).get("enforcement", "warn")
        severity = "fail" if enforcement == "block" else "warn"
        shown = "; ".join(f.get("detail", "") for f in open_findings[:3])
        checks.append(
            (
                "findings",
                severity,
                f"{len(open_findings)} open: {shown} — route to a fix, then "
                "`aspis findings --resolve <n>`.",
            )
        )
    else:
        checks.append(("findings", "ok", "none"))

    for name, status, detail in checks:
        print(f"  [{_LABELS.get(status, status)}] {name:<8} {detail}")

    failed = [c for c in checks if c[1] == "fail"]
    if failed:
        print(f"\n{len(failed)} blocker(s) — resolve before editing.")
        return 1
    print("\nReady.")
    return 0
