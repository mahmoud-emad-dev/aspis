"""``aspis doctor`` — report on the local environment and project health."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.health import run_checks
from aspis.inventory import build_inventory, load_sync_snapshot, provider_signature

#: Label shown per status. ASCII-safe so it renders on any console.
_LABELS = {"ok": "ok  ", "warn": "warn", "fail": "FAIL"}


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``doctor`` verb on the given subparsers action."""
    parser = subparsers.add_parser("doctor", help="Check the local environment and project health.")
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run all health checks and print a small report.

    Returns a non-zero exit code only when a check fails; warnings pass.
    """
    root = Path(args.path).resolve()
    checks = run_checks(root)

    for check in checks:
        label = _LABELS.get(check.status, check.status)
        print(f"  [{label}] {check.name:<8} {check.detail}")

    # Refresh detection and flag when the connected plans changed since the last
    # `aspis models --sync` — the moment to re-sync. Best-effort; never fails a check.
    if (root / BRAIN_DIR).is_dir():
        try:
            _report_model_drift(root)
        except Exception:
            pass
        try:
            _report_commit_health(root)
        except Exception:
            pass

    failed = [c for c in checks if c.status == "fail"]
    if failed:
        print(f"\n{len(failed)} check(s) failed.")
        return 1
    print("\nAll checks passed.")
    return 0


def _report_model_drift(root: Path) -> None:
    """Detect runtimes and compare the connected providers to the last sync snapshot."""
    current = provider_signature(build_inventory(root))
    names = ", ".join(sorted(current)) or "none"
    snapshot = load_sync_snapshot(root)

    if snapshot is None:
        print(f"  [info] models   detected: {names} — run `aspis models --sync` to assign models")
        return
    if current != snapshot:
        added = _flatten(current) - _flatten(snapshot)
        removed = _flatten(snapshot) - _flatten(current)
        change = ", ".join([*(f"+{p}" for p in sorted(added)), *(f"-{p}" for p in sorted(removed))])
        print(f"  [warn] models   connected plans changed ({change}) — run `aspis models --sync`")
        return
    print(f"  [info] models   detected: {names} (in sync)")


def _report_commit_health(root: Path) -> None:
    """Read-only: flag when any commit message violates the convention (never fails)."""
    from aspis import commitaudit

    findings = commitaudit.audit_history(root, commitaudit.load_convention(root))
    if not findings:
        print("  [ok  ] commits  all messages conform to the convention")
        return
    fixable = sum(1 for f in findings if f.autofixable)
    hint = " — run `aspis commits --fix`" if fixable else " — run `aspis commits` for detail"
    print(f"  [warn] commits  {len(findings)} message(s) break the convention{hint}")


def _flatten(signature: dict[str, list[str]]) -> set[str]:
    """The set of ``runtime/provider`` pairs in a provider signature, for diffing."""
    return {
        f"{runtime}/{provider}"
        for runtime, providers in signature.items()
        for provider in providers
    }
