#!/usr/bin/env python3
"""Check if a cached research file is stale — compare mtime against type-specific windows.

Purpose: Given a file path and optional reference type, check the file's
modification time against a staleness threshold and output FRESH/STALE/WARN
with age in days.

Does Not: Update or delete stale files — this is a check-only tool.
Does not fetch fresh content.

Used By: research-lead (staleness checks), cache management.

Stdlib-only. Deterministic. --help shows usage.

Staleness windows by type:
  security    — 7 days
  api         — 30 days
  framework   — 90 days
  library     — 90 days
  language    — 180 days (6 months)
  stable      — 365 days (12 months)
  default     — 90 days

Usage:
  python check_staleness.py <file_path>
  python check_staleness.py <file_path> --type security
  python check_staleness.py <file_path> --threshold 30
  python check_staleness.py --help
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Type -> max age in days
STALENESS_WINDOWS = {
    "security": 7,
    "api": 30,
    "framework": 90,
    "library": 90,
    "language": 180,
    "stable": 365,
    "default": 90,
}


def check_staleness(file_path: Path, ref_type: str = "default", custom_threshold: int | None = None) -> dict:
    """Check file staleness. Returns verdict dict."""
    if not file_path.exists():
        return {
            "verdict": "ERROR",
            "reason": f"File not found: {file_path}",
            "age_days": None,
            "threshold_days": None,
        }

    threshold = custom_threshold if custom_threshold is not None else STALENESS_WINDOWS.get(ref_type, 90)
    mtime = file_path.stat().st_mtime
    now = time.time()
    age_seconds = now - mtime
    age_days = age_seconds / 86400.0

    if age_days <= threshold * 0.5:
        verdict = "FRESH"
    elif age_days <= threshold:
        verdict = "WARN"
    else:
        verdict = "STALE"

    return {
        "verdict": verdict,
        "reason": f"Age {age_days:.1f}d vs threshold {threshold}d (type: {ref_type})",
        "age_days": round(age_days, 1),
        "threshold_days": threshold,
        "file": str(file_path),
        "type": ref_type,
        "mtime": mtime,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check if a cached research file is stale."
    )
    parser.add_argument(
        "file_path", nargs="?", default=None, help="path to the cached research file"
    )
    parser.add_argument(
        "--type", default="default",
        choices=list(STALENESS_WINDOWS.keys()),
        help="reference type for staleness window (default: default=90d)"
    )
    parser.add_argument(
        "--threshold", type=int, default=None,
        help="custom staleness threshold in days (overrides --type)"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.file_path:
        print("error: file path required", file=sys.stderr)
        parser.print_help()
        return 1

    result = check_staleness(
        Path(args.file_path),
        ref_type=args.type,
        custom_threshold=args.threshold,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"File:      {result['file']}")
        print(f"Type:      {result['type']}")
        print(f"Age:       {result['age_days']} days")
        print(f"Threshold: {result['threshold_days']} days")
        print(f"Verdict:   {result['verdict']}")
        if result['verdict'] == 'ERROR':
            print(f"Reason:    {result['reason']}")

    if result["verdict"] == "ERROR":
        return 2
    elif result["verdict"] == "STALE":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
