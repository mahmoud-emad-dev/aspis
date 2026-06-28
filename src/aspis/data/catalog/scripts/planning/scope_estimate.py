#!/usr/bin/env python3
"""Estimate scope from a feature SPEC.md — story-point range and risk level.

Purpose: Parse a SPEC.md, count functional requirements (FR-XXX), success
criteria (SC-XXX), detect complexity markers, and output an estimated
story-point range (1/2/3/5/8/13 Fibonacci) plus a risk level.

Does Not: Guarantee accuracy — this is a deterministic heuristic, not an
oracle. Does not read TASKS.md or PLAN.md.

Used By: planning-lead (scope estimation), scope-estimator subagent (L3).

Stdlib-only. Deterministic. --help shows usage.

Usage:
  python scope_estimate.py <SPEC.md path>
  python scope_estimate.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Story-point scale (Fibonacci)
STORY_POINTS = [1, 2, 3, 5, 8, 13]

# Complexity markers and their weights
COMPLEXITY_PATTERNS = [
    (r"subprocess|subprocess\.run|Popen", 3, "subprocess usage"),
    (r"cross-runtime|multi-runtime|claude.*opencode", 3, "cross-runtime"),
    (r"governance|R-008|human.gate|approval", 2, "governance gate"),
    (r"permission.*change|settings\.json|\.claude/settings", 2, "permission change"),
    (r"database|migration|schema", 2, "database"),
    (r"concurrency|async|threading|parallel", 2, "concurrency"),
    (r"security|encrypt|secret|vulnerabilit", 2, "security"),
    (r"api.*integration|external.*service|webhook", 2, "external integration"),
    (r"breaking.*change|backward.*compat", 2, "breaking change"),
    (r"regex|parsing|lexer|parser|grammar", 1, "parsing"),
]


def parse_spec(path: Path) -> dict:
    """Parse SPEC.md and return counts and markers."""
    if not path.exists():
        raise FileNotFoundError(f"SPEC not found: {path}")

    text = path.read_text(encoding="utf-8")

    fr_count = len(re.findall(r"\bFR-[A-Z]+\d+-\d+\b", text))
    sc_count = len(re.findall(r"\bSC-[A-Z]+\d+-\d+\b", text))

    # Detect complexity markers
    markers = []
    complexity_score = 0
    for pattern, weight, label in COMPLEXITY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            markers.append(label)
            complexity_score += weight

    # Estimate file count from scope section mentions
    file_count = len(re.findall(r"Files?:.*`[^`]+`", text))
    # Also count "new" mentions near file paths
    new_files = len(
        re.findall(r"\(new\)|\(new file\)|create.*\.py|create.*\.md", text, re.IGNORECASE)
    )

    return {
        "fr_count": fr_count,
        "sc_count": sc_count,
        "markers": markers,
        "complexity_score": complexity_score,
        "file_count": file_count,
        "new_files": new_files,
    }


def estimate_story_points(parsed: dict) -> tuple[int, int, str]:
    """Return (low, high, risk_level) estimate."""
    fr = parsed["fr_count"]
    sc = parsed["sc_count"]
    cx = parsed["complexity_score"]
    nf = parsed["new_files"]

    # Base: FRs are work units, SCs are verification effort
    base = max(1, (fr * 0.7 + sc * 0.3 + nf * 0.5))

    # Complexity multiplier
    multiplier = 1.0 + (cx * 0.15)
    adjusted = base * multiplier

    # Map to Fibonacci
    low = 1
    high = 2
    for sp in STORY_POINTS:
        if adjusted <= sp * 0.7:
            high = sp
            if sp > 2:
                low = STORY_POINTS[STORY_POINTS.index(sp) - 1]
            break
    else:
        low = 13
        high = 13

    # Risk level
    if cx >= 8:
        risk = "HIGH"
    elif cx >= 4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return low, high, risk


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Estimate scope from a feature SPEC.md — story-point range and risk level."
    )
    parser.add_argument(
        "spec_path", nargs="?", default=None, help="path to SPEC.md (reads from stdin if omitted)"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.spec_path:
        spec_path = Path(args.spec_path)
    else:
        # Read from stdin
        spec_path = None

    try:
        if spec_path:
            parsed = parse_spec(spec_path)
        else:
            # Read from stdin
            text = sys.stdin.read()
            tmp = Path(".aspis/cache/_scope_estimate_tmp.md")
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(text, encoding="utf-8")
            parsed = parse_spec(tmp)
            tmp.unlink(missing_ok=True)

        low, high, risk = estimate_story_points(parsed)

        if args.json:
            import json
            output = {
                "story_points": f"{low}-{high}" if low != high else str(low),
                "low": low,
                "high": high,
                "risk": risk,
                "fr_count": parsed["fr_count"],
                "sc_count": parsed["sc_count"],
                "complexity_score": parsed["complexity_score"],
                "markers": parsed["markers"],
                "file_count": parsed["file_count"],
                "new_files": parsed["new_files"],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"FR count:         {parsed['fr_count']}")
            print(f"SC count:         {parsed['sc_count']}")
            print(f"Complexity score: {parsed['complexity_score']}")
            markers = ", ".join(parsed["markers"]) if parsed["markers"] else "none"
            print(f"Markers:          {markers}")
            print(f"Estimated files:  {parsed['file_count']} (new: {parsed['new_files']})")
            print(f"Story points:     {low}-{high}" if low != high else f"Story points:     {low}")
            print(f"Risk level:       {risk}")

        return 0

    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
