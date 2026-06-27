#!/usr/bin/env python3
"""Check a PLAN.md or TASKS.md against the 12 architecture-constitution rules.

Purpose: Read a plan or task file, evaluate it against the 12 rules from the
architecture constitution, and produce a per-rule pass/warn/fail table with
evidence and suggested fixes.

Does Not: Modify files. Does not guarantee correctness — this is a heuristic
check based on text patterns, not a semantic analysis.

Used By: planning-lead (constitution audit), constitution-checker subagent (L3).

Stdlib-only. Deterministic. --help shows usage.

The 12 rules (from architecture-constitution.md):
  1. Local Change — add by creating files, not editing many
  2. Plugin First — growable things are plugins
  3. Single Source of Truth — every fact has one owner
  4. Configuration over Code — data over if-chains
  5. Core is Stable — most work in plugins/assets
  6. Dependency Direction — plugins -> core
  7. Discovery over Registration — convention over hand-maintained lists
  8. Generated Artifacts — humans edit source, machines generate
  9. No Special Cases — never if-runtime==claude
  10. Consistency over Cleverness — boring, predictable, repeatable
  11. Architecture before Features — extension mechanism before feature
  12. Portable by Default — Windows + Linux, UTF-8, pathlib

Usage:
  python constitution_check.py <PLAN.md or TASKS.md path>
  python constitution_check.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The 12 rules with their descriptions and check functions
RULES = [
    {
        "id": 1,
        "name": "Local Change",
        "description": "Add features by creating files, not editing many",
        "check_patterns": [r"(?i)new file|create.*file|add.*file|Files.*new"],
        "anti_patterns": [r"(?i)modify.*many|edit.*existing|change.*core"],
    },
    {
        "id": 2,
        "name": "Plugin First",
        "description": "Growable things are plugins; core never names a concrete one",
        "check_patterns": [r"(?i)plugin|extension|convention|discovery|catalog"],
        "anti_patterns": [r"(?i)hard.?coded|REGISTRY\s*=\s*\[|built.?in.*list"],
    },
    {
        "id": 3,
        "name": "Single Source of Truth",
        "description": "Every fact has exactly one owner; everything else is generated",
        "check_patterns": [r"(?i)single source|catalog is truth|generated from|derive"],
        "anti_patterns": [r"(?i)duplicate|copied from|hand.?maintain.*generated"],
    },
    {
        "id": 4,
        "name": "Configuration over Code",
        "description": "Describe behaviour with data, not if-chains",
        "check_patterns": [r"(?i)config\.yaml|\.yaml|\.json|data.?driven|configure"],
        "anti_patterns": [r"if\s+mode\s*==|if\s+runtime\s*=="],
    },
    {
        "id": 5,
        "name": "Core is Stable",
        "description": "Most work happens in plugins/assets; core changes rarely",
        "check_patterns": [r"(?i)plugin|asset|catalog|extension"],
        "anti_patterns": [r"(?i)edit.*core|modify.*core|change.*core.*module"],
    },
    {
        "id": 6,
        "name": "Dependency Direction",
        "description": "Dependencies flow inward: plugins -> core, never reverse",
        "check_patterns": [r"(?i)dependenc.*inward|import.*core|plugin.*import"],
        "anti_patterns": [r"(?i)core.*import.*plugin|core.*depends.*plugin"],
    },
    {
        "id": 7,
        "name": "Discovery over Registration",
        "description": "Load by convention; no hand-maintained REGISTRY lists",
        "check_patterns": [r"(?i)convention|discover|glob|scan|auto.?detect"],
        "anti_patterns": [r"REGISTRY\s*=\s*\[|hand.?maintain|manual.*register"],
    },
    {
        "id": 8,
        "name": "Generated Artifacts",
        "description": "Humans edit source; machines generate catalogs, indexes, docs",
        "check_patterns": [r"(?i)generated|auto.?generated|machine.?generated|build.*script"],
        "anti_patterns": [r"(?i)hand.?edit.*generated|manual.*update.*index"],
    },
    {
        "id": 9,
        "name": "No Special Cases",
        "description": "Never if-runtime==claude; use abstractions and capability checks",
        "check_patterns": [r"(?i)capability|abstraction|runtime\.supports|generic"],
        "anti_patterns": [r"if\s+runtime\s*==\s*[\"']claude|if\s+profile\s*==\s*[\"']"],
    },
    {
        "id": 10,
        "name": "Consistency over Cleverness",
        "description": "Boring, predictable, repeatable wins",
        "check_patterns": [r"(?i)consistent|predictable|repeatable|standard"],
        "anti_patterns": [r"(?i)clever|hack|trick|optimiz.*premature"],
    },
    {
        "id": 11,
        "name": "Architecture before Features",
        "description": "Build the extension mechanism first, then the feature",
        "check_patterns": [r"(?i)extension mechanism|plugin system|framework|before.*feature"],
        "anti_patterns": [r"(?i)one.?off|single.?use|hard.?coded.*feature"],
    },
    {
        "id": 12,
        "name": "Portable by Default",
        "description": "Windows + Linux, UTF-8, pathlib over string paths",
        "check_patterns": [r"(?i)utf-8|pathlib|Path\(|cross.?platform|Windows.*Linux|Linux.*Windows"],
        "anti_patterns": [r"\\\\|os\.path\.join|'utf-8'|encode\(.*\)|decode\(.*\)"],
    },
]


def check_document(path: Path) -> list[dict]:
    """Check a document against all 12 rules and return results."""
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    text = path.read_text(encoding="utf-8")
    results = []

    for rule in RULES:
        evidence_for = []
        evidence_against = []

        for pat in rule["check_patterns"]:
            matches = re.findall(pat, text)
            evidence_for.extend(matches[:3])  # up to 3 matches

        for pat in rule["anti_patterns"]:
            matches = re.findall(pat, text)
            evidence_against.extend(matches[:3])

        # Determine verdict
        if evidence_against and not evidence_for:
            verdict = "FAIL"
        elif evidence_against and evidence_for:
            verdict = "WARN"
        elif evidence_for:
            verdict = "PASS"
        else:
            verdict = "WARN"  # no evidence either way -> can't confirm

        fix = ""
        if verdict == "FAIL":
            fix = f"Remove anti-patterns: {', '.join(evidence_against[:2])}"
        elif verdict == "WARN" and not evidence_for:
            fix = f"No evidence found for rule {rule['id']}. Consider documenting adherence."

        results.append({
            "id": rule["id"],
            "name": rule["name"],
            "verdict": verdict,
            "evidence_for": evidence_for,
            "evidence_against": evidence_against,
            "fix": fix,
        })

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a PLAN.md or TASKS.md against the 12 architecture-constitution rules."
    )
    parser.add_argument(
        "doc_path", nargs="?", default=None, help="path to PLAN.md or TASKS.md"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.doc_path:
        print("error: document path required", file=sys.stderr)
        parser.print_help()
        return 1

    try:
        results = check_document(Path(args.doc_path))
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.json:
        import json
        print(json.dumps(results, indent=2))
        return 0

    # Pretty-print table
    print(f"{'#':>2}  {'Rule':<30} {'Verdict':<6} Evidence")
    print("-" * 80)
    for r in results:
        ev = ", ".join(r["evidence_for"][:2]) if r["evidence_for"] else "—"
        print(f"{r['id']:>2}  {r['name']:<30} {r['verdict']:<6} {ev[:45]}")

    print("-" * 80)
    fails = sum(1 for r in results if r["verdict"] == "FAIL")
    warns = sum(1 for r in results if r["verdict"] == "WARN")
    passes = sum(1 for r in results if r["verdict"] == "PASS")
    print(f"Summary: {passes} PASS, {warns} WARN, {fails} FAIL")

    # Print fix suggestions for FAILs
    for r in results:
        if r["verdict"] == "FAIL" and r["fix"]:
            print(f"  Rule {r['id']}: {r['fix']}")

    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
