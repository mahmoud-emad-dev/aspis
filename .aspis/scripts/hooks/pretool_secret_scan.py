#!/usr/bin/env python3
"""Pre-tool secret scan — PreToolUse hook (R-008 surface, F-018 T-044).

Scans text (or a file) for likely secrets *before* a tool writes or commits
it, and reports one of three verdicts:

- ``BLOCK`` — a definite secret pattern matched (cloud creds, private keys,
  GitHub / OpenAI tokens). The runtime should refuse the tool call.
- ``WARN``  — a possible secret pattern matched (e.g. ``password=…`` which
  might be config or might be a leak). The runtime should surface it.
- ``CLEAN`` — nothing matched.

The pattern set lives in code (not config) because a hook that silently
drops a rule because the config file is wrong is worse than one that misses
a rarely-used key. Adding a rule is one line in the ``PATTERNS`` list.

Stdlib only (``re``, ``sys``, ``argparse``, ``pathlib``).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# (severity, name, compiled regex)
# - BLOCK: a leaked value of these classes is always a defect.
# - WARN : likely but not certain; the caller surfaces it for a human look.
PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    # GitHub personal access / OAuth / user / server / refresh tokens.
    # New format since 2021: ghp_, gho_, ghu_, ghs_, ghr_ prefix + 36+ alnum.
    (
        "BLOCK",
        "github_token",
        re.compile(r"\bgh[psour]_[A-Za-z0-9]{36,255}\b"),
    ),
    # OpenAI API keys. Legacy: sk-<48 alnum>. Project-scoped: sk-proj-<...>.
    (
        "BLOCK",
        "openai_key",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,}\b"),
    ),
    # AWS access key ID (20 chars, AKIA / ASIA prefix + 16 uppercase alnum).
    (
        "BLOCK",
        "aws_access_key",
        re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    # PEM private key headers — RSA, EC, DSA, OpenSSH, PGP, and the
    # ``ENCRYPTED`` variant. The header alone is enough to flag the block.
    (
        "BLOCK",
        "private_key_header",
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----"
        ),
    ),
    # ``password=...`` assignments in code / config. The catch is broad on
    # purpose; the verdict is WARN (not BLOCK) so legitimate config like
    # ``password=changeme`` in a docs example doesn't hard-stop the tool.
    (
        "WARN",
        "password_assignment",
        re.compile(r"""(?i)\bpassword\s*[:=]\s*['"]?[^\s'"]+"""),
    ),
]


def scan(text: str) -> list[tuple[str, str, str]]:
    """Return ``[(severity, name, snippet), ...]`` for matches in *text*."""
    hits: list[tuple[str, str, str]] = []
    for severity, name, rx in PATTERNS:
        for match in rx.finditer(text):
            snippet = match.group(0)
            if len(snippet) > 60:
                snippet = snippet[:57] + "..."
            hits.append((severity, name, snippet))
    return hits


def _read(path: str) -> str:
    """Read *path* as UTF-8 (replacing undecodable bytes)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"file not found: {path}")
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    """CLI entry point: scan text or a file and print the verdict."""
    parser = argparse.ArgumentParser(
        description=(
            "Scan content for likely secrets. Returns one of "
            "CLEAN / WARN / BLOCK plus any matched snippets."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--content", help="Inline text to scan.")
    group.add_argument("--file", help="Path to a file to scan.")
    args = parser.parse_args()

    try:
        text = args.content if args.content is not None else _read(args.file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 0

    hits = scan(text)
    if not hits:
        print("CLEAN — no secret patterns matched")
        return 0

    severities = {h[0] for h in hits}
    if "BLOCK" in severities:
        verdict = "BLOCK"
    elif "WARN" in severities:
        verdict = "WARN"
    else:
        verdict = "CLEAN"  # unreachable when hits is non-empty; defensive.

    for severity, name, snippet in hits:
        print(f"{verdict} — {severity}/{name}: {snippet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
