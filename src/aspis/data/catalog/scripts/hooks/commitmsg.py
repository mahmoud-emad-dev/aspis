#!/usr/bin/env python3
"""Commit-message validation against ``commit-convention.yaml`` (FR-003).

The convention file is the single source of style: allowed types, the
``F-NNN[/T-NN | /T-NN..T-MM]`` scope grammar, the subject length, and the
forbidden-attribution blocklist (history must read as human-authored). This hook
adds no inline rules of its own.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _config  # noqa: E402
import _git  # noqa: E402

# Scope is optional: feature work carries F-NNN[/T-NN | /T-NN..T-MM]; repo-lifecycle
# commits (init, bootstrap, release) may omit it.
_SUBJECT = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?: (?P<title>.+)$")
_SCOPE = re.compile(r"^F-\d{3}(/T-\d{2}(\.\.T-\d{2})?)?$")


def _subject_line(message: str) -> str:
    """First non-blank, non-comment line of the message."""
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def validate(message: str, convention: dict[str, Any]) -> list[str]:
    """Return a list of human-readable violations (empty ⇒ the message is valid)."""
    subject = _subject_line(message)
    if subject.startswith("Merge "):  # merge commits are git-generated; let them pass
        return []

    errors: list[str] = []
    lowered = message.lower()
    # Unambiguous attribution phrases — substring match.
    for token in (t.lower() for t in convention.get("forbid_attribution") or []):
        if token in lowered:
            errors.append(f"forbidden attribution: '{token}' (history must read as human-authored)")
    # Model/tool names only when credited (e.g. "by claude", "claude-generated"); a bare
    # mention of the `.claude` / `.opencode` runtime dirs is fine domain vocabulary.
    for model in (m.lower() for m in convention.get("attribution_models") or []):
        name = re.escape(model)
        credited = re.search(rf"\b(?:by|with|from)\s+{name}\b", lowered) or re.search(
            rf"\b{name}[-\s](?:generated|authored|assisted|wrote|co-authored)\b", lowered
        )
        if credited:
            errors.append(
                f"forbidden attribution: '{model}' credited (history must read as human-authored)"
            )

    match = _SUBJECT.match(subject)
    if not match:
        errors.append("subject must be '<type>(F-NNN[/T-NN | /T-NN..T-MM]): <title>'")
        return errors

    types = convention.get("types") or []
    if types and match["type"] not in types:
        errors.append(f"type '{match['type']}' is not one of {types}")
    if match["scope"] is not None and not _SCOPE.match(match["scope"]):
        errors.append(f"scope '{match['scope']}' must be F-NNN, F-NNN/T-NN, or F-NNN/T-NN..T-MM")

    max_len = int((convention.get("subject") or {}).get("max_length") or 72)
    if len(subject) > max_len:
        errors.append(f"subject is {len(subject)} chars (max {max_len})")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Read the message file (git passes its path as $1); exit 1 on any violation."""
    _config.force_utf8_stdio()
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        return 0
    root = _git.repo_root()
    message = Path(args[0]).read_text(encoding="utf-8")
    errors = validate(message, _config.commit_convention(root))
    blocking = _config.blocks(root)  # "warn" (default) reports without blocking
    label = "commit-msg BLOCKED" if blocking else "commit-msg warning"
    for error in errors:
        print(f"[aspis] {label}: {error}", file=sys.stderr)
    return 1 if (blocking and errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
