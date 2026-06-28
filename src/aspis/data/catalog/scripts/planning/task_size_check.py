#!/usr/bin/env python3
"""Check task sizes against mode ceilings — packet size markers and thresholds.

Purpose: Parse a TASKS.md, extract each task's packet size marker
(V1-light, V2-standard, V3-deep, V4-complex), compute per-mode thresholds,
and flag over-size tasks with warnings.

Does Not: Estimate task effort — only checks declared sizes against mode limits.
Does not modify any files.

Used By: planning-lead (size audit), task-decomposer subagent.

Stdlib-only. Deterministic. --help shows usage.

Mode thresholds:
  vibe:       max 20 tasks, max 2 V3+, 0 V4
  mvp:        max 40 tasks, max 5 V3+, 1 V4
  production: max 60 tasks, max 10 V3+, 3 V4

Usage:
  python task_size_check.py <TASKS.md>
  python task_size_check.py <TASKS.md> --mode production
  python task_size_check.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SIZE_WEIGHTS = {"V1": 1, "V2": 2, "V3": 5, "V4": 8}

MODE_THRESHOLDS = {
    "vibe": {
        "max_tasks": 20,
        "max_v3": 2,
        "max_v4": 0,
        "max_weighted": 50,
    },
    "mvp": {
        "max_tasks": 40,
        "max_v3": 5,
        "max_v4": 1,
        "max_weighted": 100,
    },
    "production": {
        "max_tasks": 60,
        "max_v3": 10,
        "max_v4": 3,
        "max_weighted": 200,
    },
}


def parse_tasks(path: Path) -> list[dict]:
    """Parse TASKS.md and return list of task info dicts."""
    if not path.exists():
        raise FileNotFoundError(f"TASKS not found: {path}")

    text = path.read_text(encoding="utf-8")
    tasks = []

    # Split by task headers: "- [ ] T-XXX"
    blocks = re.split(r"\n(?=- \[ \] T-)", text)

    # Also handle first block before any task
    for block in blocks:
        task_match = re.search(r"T-(\d+[a-z]?)", block[:100])
        if not task_match:
            continue

        tid = f"T-{task_match.group(1)}"

        # Find priority
        priority = "P2"
        for p in ["P0", "P1", "P2"]:
            if re.search(rf"\[{p}\]", block[:200]):
                priority = p
                break

        # Find size marker
        size = "V2"  # default
        size_match = re.search(r"Packet:\s*(V\d)", block)
        if size_match:
            size = size_match.group(1)

        # Find builder
        builder = "standard"
        builder_match = re.search(r"Builder:\s*(\S+)", block)
        if builder_match:
            builder = builder_match.group(1)

        # Find description (first line after task ID)
        desc_match = re.search(
            r"T-\d+[a-z]?\s+.*?\[.*?\]\s*\[.*?\]\s*\[.*?\]\s*\[.*?\]\s*—\s*(.+?)(?:\n|$)",
            block[:300],
        )
        desc = desc_match.group(1).strip() if desc_match else tid

        tasks.append({
            "id": tid,
            "priority": priority,
            "size": size,
            "builder": builder,
            "description": desc,
        })

    return tasks


def check_sizes(tasks: list[dict], mode: str) -> dict:
    """Check task sizes against mode thresholds."""
    thresholds = MODE_THRESHOLDS.get(mode, MODE_THRESHOLDS["production"])

    total = len(tasks)
    v1 = sum(1 for t in tasks if t["size"] == "V1")
    v2 = sum(1 for t in tasks if t["size"] == "V2")
    v3 = sum(1 for t in tasks if t["size"] == "V3")
    v4 = sum(1 for t in tasks if t["size"] == "V4")
    unknown = sum(1 for t in tasks if t["size"] not in SIZE_WEIGHTS)

    weighted = sum(SIZE_WEIGHTS.get(t["size"], 2) for t in tasks)

    warnings = []
    if total > thresholds["max_tasks"]:
        warnings.append(f"Task count {total} exceeds mode ceiling {thresholds['max_tasks']}")
    if v3 > thresholds["max_v3"]:
        warnings.append(f"V3 tasks ({v3}) exceed mode limit ({thresholds['max_v3']})")
    if v4 > thresholds["max_v4"]:
        warnings.append(f"V4 tasks ({v4}) exceed mode limit ({thresholds['max_v4']})")
    if weighted > thresholds["max_weighted"]:
        warnings.append(
            f"Weighted total ({weighted}) exceeds mode ceiling ({thresholds['max_weighted']})"
        )

    over_threshold = len(warnings) > 0

    return {
        "mode": mode,
        "total_tasks": total,
        "v1_count": v1,
        "v2_count": v2,
        "v3_count": v3,
        "v4_count": v4,
        "unknown_size": unknown,
        "weighted_total": weighted,
        "thresholds": thresholds,
        "warnings": warnings,
        "over_threshold": over_threshold,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check task sizes against mode ceilings."
    )
    parser.add_argument(
        "tasks_path", nargs="?", default=None, help="path to TASKS.md"
    )
    parser.add_argument(
        "--mode", default="production",
        help="target mode: vibe, mvp, or production (default: production)"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.tasks_path:
        print("error: TASKS.md path required", file=sys.stderr)
        parser.print_help()
        return 1

    if args.mode not in MODE_THRESHOLDS:
        valid = ", ".join(MODE_THRESHOLDS)
        print(f"error: unknown mode '{args.mode}'. Valid: {valid}", file=sys.stderr)
        return 1

    try:
        tasks = parse_tasks(Path(args.tasks_path))
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    result = check_sizes(tasks, args.mode)

    if args.json:
        import json
        output = {
            "mode": result["mode"],
            "total_tasks": result["total_tasks"],
            "sizes": {
                "V1": result["v1_count"],
                "V2": result["v2_count"],
                "V3": result["v3_count"],
                "V4": result["v4_count"],
                "unknown": result["unknown_size"],
            },
            "weighted_total": result["weighted_total"],
            "thresholds": result["thresholds"],
            "over_threshold": result["over_threshold"],
            "warnings": result["warnings"],
        }
        print(json.dumps(output, indent=2))
        return 0

    # Pretty-print
    t = result["thresholds"]
    print(f"Mode: {result['mode']}")
    print(f"Total tasks: {result['total_tasks']} (limit: {t['max_tasks']})")
    print(f"  V1 (light):    {result['v1_count']}")
    print(f"  V2 (standard): {result['v2_count']}")
    print(f"  V3 (deep):     {result['v3_count']} (limit: {t['max_v3']})")
    print(f"  V4 (complex):  {result['v4_count']} (limit: {t['max_v4']})")
    if result["unknown_size"]:
        print(f"  Unknown size:  {result['unknown_size']}")
    print(f"Weighted total: {result['weighted_total']} (limit: {t['max_weighted']})")

    if result["warnings"]:
        print(f"\nWARNINGS ({len(result['warnings'])}):")
        for w in result["warnings"]:
            print(f"  [WARN] {w}")
        return 1
    else:
        print("\n[OK] All task sizes within mode thresholds.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
