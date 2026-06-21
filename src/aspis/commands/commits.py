"""``aspis commits`` — audit (and optionally fix) commit-message history (F-012).

- ``aspis commits`` / ``--audit``  report every commit whose message violates the
  convention (exit 1 when any are found), read-only.
- ``aspis commits --fix``          rewrite the auto-fixable messages (forbidden
  attribution) after stamping a backup ref; commit *content* is left unchanged.

Validation reuses the commit-msg hook's rules — the single source of commit style.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import commitaudit


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``commits`` verb."""
    parser = subparsers.add_parser(
        "commits",
        help="Audit (and optionally fix) commit-message history against the convention.",
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Report commits whose message violates the convention (the default).",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Rewrite auto-fixable messages (backup ref first; content unchanged).",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Only scan the most recent N commits."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    convention = commitaudit.load_convention(root)
    findings = commitaudit.audit_history(root, convention, limit=args.limit)

    if args.fix:
        return commitaudit.fix_history(root, convention, findings)

    if not findings:
        print("commits: all messages conform to the convention.")
        return 0

    print(f"commits: {len(findings)} message(s) violate the convention:\n")
    for finding in findings:
        print(f"  {finding.sha[:9]}  {finding.subject}")
        for violation in finding.violations:
            print(f"       - {violation}")
    fixable = sum(1 for f in findings if f.autofixable)
    if fixable:
        print(f"\n{fixable} auto-fixable — run `aspis commits --fix` (a backup ref is made first).")
    return 1
