#!/usr/bin/env python3
"""Validate the governance approval ledger — R-008 enforcement.

Purpose: Read the approval ledger (default: .aspis/state/approval-ledger.yaml
or .aspis/approvals/), check that every protected-path write has a valid,
non-expired approval from a known approver, and output per-approval
PASS/WARN/FAIL with reasoning.

Does Not: Create or modify approvals — this is a read-only validator.
Does not enforce at runtime — that's the hook's job. This validates the ledger.

Used By: system-lead (governance enforcement), governance subagent.

Stdlib-only (yaml via PyYAML if available, with JSON fallback).
Deterministic. --help shows usage.

Checks performed:
  1. Every approval has a valid approver in known_approvers list
  2. Every approval is not expired (expires_at in the future)
  3. Every approval references a real protected path
  4. No duplicate approvals for the same path

Usage:
  python validate-approvals.py
  python validate-approvals.py --ledger .aspis/state/approval-ledger.yaml
  python validate-approvals.py --help
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Default known approvers (project-specific, overridable via config)
KNOWN_APPROVERS = {"owner", "project-lead", "system-lead"}

# Protected paths that require approval.
#
# MUST mirror the canonical set in ``aspis.commands.governance.PROTECTED_PATHS``
# (whose own source is governance.md §3). This script prefix-matches, so the
# glob patterns there are expressed here as directory/file prefixes. Until F-019
# extracts a shared data source both sides load, keep these two lists in step.
PROTECTED_PATHS = [
    "rules/",
    ".aspis/rules/",
    ".aspis/config/",
    "profiles/defaults.yaml",
    ".opencode/agents/",
    ".claude/agents/",
    ".claude/settings.json",
    ".aspis/current/active_feature.json",
]

DEFAULT_LEDGER_PATH = ".aspis/state/approval-ledger.yaml"


def try_load_yaml_or_json(path: Path) -> dict | list | None:
    """Try loading YAML (PyYAML) or JSON from path."""
    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8")

    # Try PyYAML
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        pass
    except Exception:
        pass

    # Try JSON
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        pass

    # Minimal YAML parser for approval-ledger structure
    try:
        entries = []
        current = {}
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                if current:
                    entries.append(current)
                current = {}
                # Parse "- key: value"
                kv = stripped[2:].split(":", 1)
                if len(kv) == 2:
                    current[kv[0].strip()] = kv[1].strip().strip('"').strip("'")
            elif ":" in stripped and not stripped.startswith("#"):
                kv = stripped.split(":", 1)
                current[kv[0].strip()] = kv[1].strip().strip('"').strip("'")

        if current:
            entries.append(current)

        if entries:
            return {"approvals": entries}
    except Exception:
        pass

    return None


def find_ledger(root: Path) -> Path | None:
    """Find approval ledger file."""
    candidates = [
        root / ".aspis" / "state" / "approval-ledger.yaml",
        root / ".aspis" / "state" / "approval-ledger.yml",
        root / ".aspis" / "state" / "approval-ledger.json",
        root / ".aspis" / "approvals" / "ledger.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def validate_approvals(
    ledger_data: dict | list, known_approvers: set[str], protected_paths: list[str]
) -> list[dict]:
    """Validate each approval entry. Returns list of result dicts."""
    results = []

    # Normalize to list of entries
    if isinstance(ledger_data, list):
        entries = ledger_data
    elif isinstance(ledger_data, dict):
        entries = ledger_data.get("approvals", [])
    else:
        return [{"approval_id": "N/A", "verdict": "FAIL", "reason": "Invalid ledger format"}]

    if not entries:
        return [
            {"approval_id": "N/A", "verdict": "WARN",
             "reason": "Ledger is empty — no approvals on file"}
        ]

    seen_paths = {}
    now = time.time()

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            results.append({
                "approval_id": f"entry-{i}",
                "verdict": "FAIL",
                "reason": f"Entry {i} is not a mapping",
            })
            continue

        approval_id = entry.get("id", entry.get("approval_id", f"entry-{i}"))
        approver = entry.get("approver", entry.get("approved_by", ""))
        path = entry.get("path", entry.get("protected_path", ""))
        expires_str = entry.get("expires", entry.get("expires_at", ""))
        status = entry.get("status", entry.get("state", "pending"))

        issues = []

        # Check 1: Valid approver
        if not approver:
            issues.append("Missing approver")
        elif approver not in known_approvers:
            known = ", ".join(sorted(known_approvers))
            issues.append(f"Unknown approver '{approver}' (known: {known})")

        # Check 2: Protected path
        if not path:
            issues.append("Missing protected path")
        else:
            is_protected = any(path.startswith(p) or p.startswith(path) for p in protected_paths)
            if not is_protected:
                issues.append(f"Path '{path}' is not a recognized protected path")

            # Check duplicates
            if path in seen_paths:
                issues.append(f"Duplicate approval for path '{path}' (first: {seen_paths[path]})")
            seen_paths[path] = approval_id

        # Check 3: Expiration
        if expires_str:
            expires_ts = None
            try:
                # Try ISO format
                from datetime import datetime
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                    try:
                        expires_ts = datetime.strptime(str(expires_str), fmt).timestamp()
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

            if expires_ts is not None and expires_ts < now:
                issues.append(f"Approval expired at {expires_str}")
        else:
            issues.append("No expiration date set — approval is perpetual (WARN)")

        # Check 4: Status
        if status and status not in ("approved", "active", "granted"):
            issues.append(f"Status is '{status}' (expected: approved/active/granted)")

        # Determine verdict
        if not issues:
            verdict = "PASS"
        elif any("Missing" in i or "Unknown" in i or "expired" in i.lower() for i in issues):
            verdict = "FAIL"
        else:
            verdict = "WARN"

        results.append({
            "approval_id": str(approval_id),
            "approver": approver,
            "path": path,
            "verdict": verdict,
            "issues": issues,
        })

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the governance approval ledger (R-008 enforcement)."
    )
    parser.add_argument(
        "--ledger", default=None, help="path to approval ledger file"
    )
    parser.add_argument(
        "--root", default=".", help="project root directory"
    )
    parser.add_argument(
        "--approvers", default=None,
        help="comma-separated list of known approvers (default: owner,project-lead,system-lead)"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    root = Path(args.root)
    ledger_path = Path(args.ledger) if args.ledger else find_ledger(root)

    known_approvers = KNOWN_APPROVERS
    if args.approvers:
        known_approvers = set(a.strip() for a in args.approvers.split(","))

    if not ledger_path:
        if args.json:
            print(json.dumps({"verdict": "WARN", "reason": "No approval ledger found"}, indent=2))
        else:
            print("WARN: No approval ledger found.")
            print("  No governance approvals on file — protected paths are honor-system only.")
        return 0  # Not a failure — just no ledger yet

    ledger_data = try_load_yaml_or_json(ledger_path)

    if ledger_data is None:
        print(f"error: could not parse ledger: {ledger_path}", file=sys.stderr)
        return 1

    results = validate_approvals(ledger_data, known_approvers, PROTECTED_PATHS)

    if args.json:
        summary = {
            "ledger_path": str(ledger_path),
            "total_approvals": len(results),
            "pass": sum(1 for r in results if r["verdict"] == "PASS"),
            "warn": sum(1 for r in results if r["verdict"] == "WARN"),
            "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
            "results": results,
        }
        print(json.dumps(summary, indent=2))
    else:
        print(f"Ledger: {ledger_path}")
        print(f"Approvals: {len(results)}")
        print()
        print(f"{'ID':<20} {'Approver':<16} {'Path':<30} {'Verdict':<6} Issues")
        print("-" * 100)
        for r in results:
            issues_str = "; ".join(r["issues"]) if r["issues"] else "[OK]"
            print(
                f"{r['approval_id']:<20} {r['approver']:<16} {r['path']:<30} "
                f"{r['verdict']:<6} {issues_str[:45]}"
            )

        passes = sum(1 for r in results if r["verdict"] == "PASS")
        warns = sum(1 for r in results if r["verdict"] == "WARN")
        fails = sum(1 for r in results if r["verdict"] == "FAIL")
        print("-" * 100)
        print(f"Summary: {passes} PASS, {warns} WARN, {fails} FAIL")

    exit_code = 0
    if any(r["verdict"] == "FAIL" for r in results):
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
