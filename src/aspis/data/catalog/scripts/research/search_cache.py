#!/usr/bin/env python3
"""Manage a JSON search cache — add, lookup, clear, and stats.

Purpose: Maintain a persistent JSON cache at .aspis/cache/search-cache.json
for research queries. Supports subcommands: --add, --lookup, --clear, --stats.
Each cache entry stores: query, result, timestamp, hit count.

Does Not: Perform actual web searches — this is a local cache manager.
Does not expire entries automatically (use check_staleness.py for that).

Used By: research-lead (cache management), search_cache users.

Stdlib-only. Deterministic. --help shows usage.

Usage:
  python search_cache.py --add <query> <result>
  python search_cache.py --lookup <query>
  python search_cache.py --clear
  python search_cache.py --stats
  python search_cache.py --help
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_CACHE_PATH = ".aspis/cache/search-cache.json"


def load_cache(cache_path: Path) -> dict:
    """Load cache from JSON file. Returns {'entries': [...]}."""
    if not cache_path.exists():
        return {"entries": [], "_meta": {"created": time.time()}}

    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "entries" in data:
            return data
    except (ValueError, OSError):
        pass

    return {"entries": [], "_meta": {"created": time.time(), "corrupted_previous": True}}


def save_cache(cache_path: Path, cache: dict) -> None:
    """Save cache to JSON file."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, default=str) + "\n", encoding="utf-8")


def add_entry(cache: dict, query: str, result: str) -> dict:
    """Add or update a cache entry. Returns updated cache."""
    now = time.time()
    for entry in cache["entries"]:
        if entry["query"] == query:
            entry["result"] = result
            entry["updated"] = now
            entry["hit_count"] = entry.get("hit_count", 0)
            return cache

    cache["entries"].append({
        "query": query,
        "result": result,
        "created": now,
        "updated": now,
        "hit_count": 0,
    })
    cache["_meta"]["last_updated"] = now
    return cache


def lookup_entry(cache: dict, query: str) -> dict | None:
    """Look up a query. Updates hit count. Returns entry or None."""
    for entry in cache["entries"]:
        if entry["query"] == query:
            entry["hit_count"] = entry.get("hit_count", 0) + 1
            entry["last_hit"] = time.time()
            return entry
    return None


def clear_cache(cache_path: Path) -> None:
    """Remove all entries but keep meta."""
    cache = {"entries": [], "_meta": {"created": time.time(), "cleared": time.time()}}
    save_cache(cache_path, cache)


def compute_stats(cache: dict) -> dict:
    """Compute cache statistics."""
    entries = cache.get("entries", [])
    total = len(entries)
    total_hits = sum(e.get("hit_count", 0) for e in entries)
    now = time.time()

    oldest = None
    newest = None
    for e in entries:
        created = e.get("created", 0)
        if oldest is None or created < oldest:
            oldest = created
        if newest is None or created > newest:
            newest = created

    return {
        "total_entries": total,
        "total_hits": total_hits,
        "avg_hits": total_hits / max(total, 1),
        "oldest_entry_age_days": round((now - oldest) / 86400, 1) if oldest else None,
        "newest_entry_age_days": round((now - newest) / 86400, 1) if newest else None,
        "cache_created": cache.get("_meta", {}).get("created"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage a JSON search cache for research queries."
    )
    parser.add_argument(
        "--cache", default=DEFAULT_CACHE_PATH,
        help=f"path to cache file (default: {DEFAULT_CACHE_PATH})"
    )
    parser.add_argument(
        "--add", nargs=2, metavar=("QUERY", "RESULT"),
        help="add or update a cache entry"
    )
    parser.add_argument(
        "--lookup", metavar="QUERY", help="look up a cached query"
    )
    parser.add_argument(
        "--clear", action="store_true", help="clear all cache entries"
    )
    parser.add_argument(
        "--stats", action="store_true", help="show cache statistics"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    cache_path = Path(args.cache)

    if args.add:
        query, result = args.add
        cache = load_cache(cache_path)
        cache = add_entry(cache, query, result)
        save_cache(cache_path, cache)
        print(f"Cached: {query}")
        return 0

    if args.lookup:
        cache = load_cache(cache_path)
        entry = lookup_entry(cache, query=args.lookup)
        save_cache(cache_path, cache)  # save updated hit count

        if entry:
            if args.json:
                print(json.dumps(
                    {"hit": True, "result": entry["result"], "query": entry["query"]}, indent=2
                ))
            else:
                print(f"HIT: {entry['query']}")
                print(f"  Result: {entry['result']}")
                print(f"  Hits: {entry.get('hit_count', 0)}")
            return 0
        else:
            if args.json:
                print(json.dumps({"hit": False, "query": args.lookup}))
            else:
                print(f"MISS: {args.lookup}")
            return 1

    if args.clear:
        clear_cache(cache_path)
        print("Cache cleared.")
        return 0

    if args.stats:
        cache = load_cache(cache_path)
        stats = compute_stats(cache)
        if args.json:
            print(json.dumps(stats, indent=2, default=str))
        else:
            print(f"Total entries:       {stats['total_entries']}")
            print(f"Total hits:          {stats['total_hits']}")
            print(f"Avg hits per entry:  {stats['avg_hits']:.2f}")
            if stats.get("oldest_entry_age_days") is not None:
                print(f"Oldest entry:        {stats['oldest_entry_age_days']} days ago")
            if stats.get("newest_entry_age_days") is not None:
                print(f"Newest entry:        {stats['newest_entry_age_days']} days ago")
        return 0

    # No subcommand — show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
