#!/usr/bin/env python3
"""Rank research sources by authority × freshness — T1-T6 tier hierarchy.

Purpose: Given a JSON list of sources (each with url, date, authority_score,
freshness_days), rank them by a composite score: authority_score × freshness_weight.
Output the ranked list with tier classification.

Does Not: Fetch source content or validate URLs — this is a ranking algorithm only.
Does not modify any files.

Used By: research-lead (source ranking), source evaluation.

Stdlib-only. Deterministic. --help shows usage.

Tier hierarchy:
  T1 (10): Official vendor documentation, language specs
  T2 (8):  Major framework docs, established references
  T3 (6):  Recognized community authority, curated knowledge bases
  T4 (4):  Blog posts from recognized experts, tutorial sites
  T5 (2):  Forum posts (StackOverflow, Reddit), general blogs
  T6 (1):  General web, unknown source

Freshness weight: 1.0 -> 0.1 as freshness_days increases (exponential decay).

Usage:
  python rank_source.py <sources.json
  python rank_source.py --sources '[{"url":"...", "date":"...", "authority_score":8}]'
  python rank_source.py --help
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone


TIER_THRESHOLDS = [
    (10, "T1", "Official vendor documentation"),
    (8, "T2", "Major framework docs"),
    (6, "T3", "Recognized community authority"),
    (4, "T4", "Expert blogs, tutorials"),
    (2, "T5", "Forum posts, general blogs"),
    (1, "T6", "General web"),
]


def classify_tier(authority_score: float) -> tuple[str, str]:
    """Classify authority score into T1-T6 tier."""
    for threshold, tier, label in TIER_THRESHOLDS:
        if authority_score >= threshold:
            return tier, label
    return "T6", "General web"


def freshness_weight(freshness_days: float) -> float:
    """Compute freshness weight: exponential decay from 1.0 to 0.1."""
    if freshness_days <= 0:
        return 1.0
    # Half-life of 90 days
    weight = math.exp(-freshness_days / 90.0 * math.log(2))
    return max(weight, 0.1)


def parse_date(date_str: str) -> datetime | None:
    """Parse ISO date string. Returns datetime or None."""
    for fmt in [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        pass
    return None


def rank_sources(sources: list[dict]) -> list[dict]:
    """Rank sources by composite score. Returns sorted list with scores added."""
    now = datetime.now(timezone.utc)
    ranked = []

    for src in sources:
        authority = float(src.get("authority_score", 1))
        authority = max(1, min(10, authority))

        # Compute freshness
        freshness_days = src.get("freshness_days")
        if freshness_days is None:
            date_str = src.get("date", "")
            dt = parse_date(date_str)
            if dt:
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                freshness_days = (now - dt).total_seconds() / 86400.0
            else:
                freshness_days = 365.0  # assume old if unparseable

        freshness_days = float(freshness_days)
        fw = freshness_weight(freshness_days)
        composite = round(authority * fw, 2)

        tier, tier_label = classify_tier(authority)

        entry = dict(src)
        entry["composite_score"] = composite
        entry["freshness_days"] = round(freshness_days, 1)
        entry["freshness_weight"] = round(fw, 3)
        entry["tier"] = tier
        entry["tier_label"] = tier_label
        ranked.append(entry)

    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return ranked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rank research sources by authority × freshness."
    )
    parser.add_argument(
        "--sources", default=None, help="JSON string of sources array"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON (default: table)"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.sources:
        try:
            sources = json.loads(args.sources)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON: {e}", file=sys.stderr)
            return 1
    else:
        # Read from stdin
        try:
            raw = sys.stdin.read()
            if not raw.strip():
                print("error: no input provided (use --sources or stdin)", file=sys.stderr)
                return 1
            sources = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON from stdin: {e}", file=sys.stderr)
            return 1

    if not isinstance(sources, list):
        print("error: input must be a JSON array of sources", file=sys.stderr)
        return 1

    ranked = rank_sources(sources)

    if args.json:
        print(json.dumps(ranked, indent=2))
        return 0

    # Pretty-print table
    print(f"{'Rank':<5} {'Tier':<4} {'Score':<8} {'Freshness':<10} {'URL'}")
    print("-" * 80)
    for i, src in enumerate(ranked, 1):
        url = src.get("url", src.get("source", "unknown"))[:50]
        print(f"{i:<5} {src['tier']:<4} {src['composite_score']:<8} {src['freshness_days']}d {'':<4} {url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
