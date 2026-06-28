#!/usr/bin/env python3
"""Compare two semantic version strings — determine which is newer and compute diff.

Purpose: Parse two semver strings (MAJOR.MINOR.PATCH with optional pre-release),
compare them, and output which is newer plus the magnitude of difference
(major, minor, or patch-level change).

Does Not: Fetch changelogs or release notes — this is a pure version comparator.
Does not handle non-semver version schemes.

Used By: research-lead (version comparison), dependency analysis.

Stdlib-only. Deterministic. --help shows usage.

Usage:
  python compare_versions.py 1.2.3 2.0.0
  python compare_versions.py --a 1.0.0 --b 1.0.1
  python compare_versions.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# Semver regex: MAJOR.MINOR.PATCH[-prerelease][+build]
SEMVER_RE = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


def parse_semver(version: str) -> tuple[int, int, int, str, str] | None:
    """Parse semver string. Returns (major, minor, patch, prerelease, build) or None."""
    match = SEMVER_RE.match(version.strip())
    if not match:
        return None
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        match.group(4) or "",
        match.group(5) or "",
    )


def compare_prerelease(a_pre: str, b_pre: str) -> int:
    """Compare two pre-release identifiers. Returns -1, 0, or 1."""
    if not a_pre and not b_pre:
        return 0
    if not a_pre:
        return 1  # no pre-release > has pre-release
    if not b_pre:
        return -1

    a_parts = a_pre.split(".")
    b_parts = b_pre.split(".")

    for a_part, b_part in zip(a_parts, b_parts, strict=False):
        a_is_int = a_part.isdigit()
        b_is_int = b_part.isdigit()
        if a_is_int and b_is_int:
            a_num, b_num = int(a_part), int(b_part)
            if a_num != b_num:
                return -1 if a_num < b_num else 1
        elif a_is_int:
            return -1  # numeric < alphanumeric
        elif b_is_int:
            return 1
        else:
            if a_part < b_part:
                return -1
            elif a_part > b_part:
                return 1

    return -1 if len(a_parts) < len(b_parts) else (1 if len(a_parts) > len(b_parts) else 0)


def compare_versions(a: str, b: str) -> dict:
    """Compare two version strings. Returns comparison result dict."""
    parsed_a = parse_semver(a)
    parsed_b = parse_semver(b)

    result = {
        "version_a": a,
        "version_b": b,
        "valid_a": parsed_a is not None,
        "valid_b": parsed_b is not None,
    }

    if parsed_a is None or parsed_b is None:
        result["newer"] = None
        result["diff_type"] = None
        result["error"] = "Invalid semver: " + (
            a if parsed_a is None else b
        )
        return result

    maj_a, min_a, pat_a, pre_a, _ = parsed_a
    maj_b, min_b, pat_b, pre_b, _ = parsed_b

    # Compare major -> minor -> patch -> prerelease
    if maj_a != maj_b:
        diff_type = "major"
        direction = "a" if maj_a > maj_b else "b"
    elif min_a != min_b:
        diff_type = "minor"
        direction = "a" if min_a > min_b else "b"
    elif pat_a != pat_b:
        diff_type = "patch"
        direction = "a" if pat_a > pat_b else "b"
    else:
        pre_cmp = compare_prerelease(pre_a, pre_b)
        if pre_cmp == 0:
            diff_type = "equal"
            direction = "equal"
        elif pre_cmp > 0:
            diff_type = "prerelease"
            direction = "a"
        else:
            diff_type = "prerelease"
            direction = "b"

    if direction == "a":
        newer = a
    elif direction == "b":
        newer = b
    else:
        newer = "equal"

    result.update({
        "newer": newer,
        "diff_type": diff_type,
        "a": {"major": maj_a, "minor": min_a, "patch": pat_a, "prerelease": pre_a},
        "b": {"major": maj_b, "minor": min_b, "patch": pat_b, "prerelease": pre_b},
        "diff": {
            "major": abs(maj_a - maj_b),
            "minor": abs(min_a - min_b) if maj_a == maj_b else None,
            "patch": abs(pat_a - pat_b) if maj_a == maj_b and min_a == min_b else None,
        },
    })

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two semantic version strings."
    )
    parser.add_argument(
        "version_a", nargs="?", default=None, help="first version string"
    )
    parser.add_argument(
        "version_b", nargs="?", default=None, help="second version string"
    )
    parser.add_argument("--a", dest="ver_a", default=None, help="first version (named)")
    parser.add_argument("--b", dest="ver_b", default=None, help="second version (named)")
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    ver_a = args.ver_a or args.version_a
    ver_b = args.ver_b or args.version_b

    if not ver_a or not ver_b:
        print("error: two version strings required", file=sys.stderr)
        parser.print_help()
        return 1

    result = compare_versions(ver_a, ver_b)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"Version A: {ver_a}")
    print(f"Version B: {ver_b}")

    if result.get("error"):
        print(f"Error: {result['error']}")
        return 1

    valid_a = "[OK]" if result["valid_a"] else "[FAIL]"
    valid_b = "[OK]" if result["valid_b"] else "[FAIL]"
    print(f"Valid:    A={valid_a}, B={valid_b}")
    print(f"Newer:    {result['newer']}")
    print(f"Diff:     {result['diff_type']}")
    if result["diff"]["major"]:
        print(f"  Major:  {result['diff']['major']}")
    if result["diff"]["minor"] is not None:
        print(f"  Minor:  {result['diff']['minor']}")
    if result["diff"]["patch"] is not None:
        print(f"  Patch:  {result['diff']['patch']}")

    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
