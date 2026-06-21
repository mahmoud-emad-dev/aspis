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
# A model name counts as *credited* only next to one of these — covers authorship
# claims ("claude-generated", "by claude") and tool trailers ("Claude-Session").
_CREDIT = r"generated|authored|assisted|wrote|co-authored|session|assistant"


def _subject_line(message: str) -> str:
    """First non-blank, non-comment line of the message."""
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def find_attribution(message: str, convention: dict[str, Any]) -> list[tuple[int, str, str]]:
    """Lines carrying forbidden attribution: ``(line_index, line_text, reason)``.

    One detector shared by :func:`validate` (which reports) and
    :func:`strip_attribution` (which repairs), so report and fix never drift. The
    check is line-based and context-aware: an unambiguous phrase from
    ``forbid_attribution`` anywhere on a line, or a model name only when *credited*
    (``by claude``, ``claude-generated``) — a bare ``.claude``/``.opencode`` mention
    stays valid domain vocabulary.
    """
    tokens = [t.lower() for t in convention.get("forbid_attribution") or []]
    models = [m.lower() for m in convention.get("attribution_models") or []]
    human = "(history must read as human-authored)"
    found: list[tuple[int, str, str]] = []
    for index, line in enumerate(message.splitlines()):
        low = line.lower()
        reason = ""
        for token in tokens:
            if token in low:
                reason = f"forbidden attribution: '{token}' {human}"
                break
        if not reason:
            for model in models:
                name = re.escape(model)
                credited = re.search(rf"\b(?:by|with|from)\s+{name}\b", low) or re.search(
                    rf"\b{name}[-\s](?:{_CREDIT})\b", low
                )
                if credited:
                    reason = f"forbidden attribution: '{model}' credited {human}"
                    break
        if reason:
            found.append((index, line, reason))
    return found


def validate(message: str, convention: dict[str, Any]) -> list[str]:
    """Return a list of human-readable violations (empty ⇒ the message is valid)."""
    subject = _subject_line(message)
    if subject.startswith("Merge "):  # merge commits are git-generated; let them pass
        return []

    errors: list[str] = [reason for _, _, reason in find_attribution(message, convention)]

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


def strip_attribution(message: str, convention: dict[str, Any]) -> tuple[str, list[str]]:
    """Drop the lines carrying forbidden attribution; return ``(cleaned, removed)``.

    The non-blocking guard: rather than reject the commit, the hook removes the
    offending lines so history stays human-authored without interrupting the flow.
    Byte-stable when nothing matches; trailing blank lines left behind are collapsed.
    """
    found = find_attribution(message, convention)
    if not found:
        return message, []
    drop = {index for index, _, _ in found}
    kept = [line for i, line in enumerate(message.splitlines()) if i not in drop]
    cleaned = "\n".join(kept).rstrip("\n")
    if cleaned:
        cleaned += "\n"
    return cleaned, [line for _, line, _ in found]


def autofix_enabled(convention: dict[str, Any], kind: str) -> bool:
    """Whether the project lets the hook auto-fix *kind* (default on for safe repairs)."""
    policy = convention.get("autofix")
    if not isinstance(policy, dict) or kind not in policy:
        return True
    return bool(policy[kind])


def skip_marker(convention: dict[str, Any]) -> str:
    """The per-commit escape-hatch trailer (rare; bypasses checks)."""
    return str(convention.get("skip_marker") or "Commit-Style: skip")


def strip_skip_marker(message: str, marker: str) -> tuple[str, bool]:
    """Remove an *exact* escape-hatch trailer line; return ``(cleaned, was_present)``.

    Only a line that *is* the marker (a deliberate trailer) triggers the bypass, so
    merely mentioning the marker text in the body never bypasses the checks.
    """
    target = marker.strip().lower()
    lines = message.splitlines()
    kept = [line for line in lines if line.strip().lower() != target]
    if len(kept) == len(lines):
        return message, False
    cleaned = "\n".join(kept).rstrip("\n")
    if cleaned:
        cleaned += "\n"
    return cleaned, True


def main(argv: list[str] | None = None) -> int:
    """Read the message file (git passes its path as $1); auto-fix, then validate.

    Auto-fix is non-blocking: unambiguous violations (forbidden attribution) are
    removed and the commit proceeds. A ``Commit-Style: skip`` trailer bypasses the
    checks for that one commit. Remaining advisory issues are reported under the
    project's enforcement mode (``warn`` by default, so they never block).
    """
    _config.force_utf8_stdio()
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        return 0
    root = _git.repo_root()
    convention = _config.commit_convention(root)
    path = Path(args[0])
    message = path.read_text(encoding="utf-8")

    marker = skip_marker(convention)
    cleaned, skipped = strip_skip_marker(message, marker)
    if skipped:
        path.write_text(cleaned, encoding="utf-8")
        print(f"[aspis] commit-msg: '{marker}' — checks bypassed for this commit", file=sys.stderr)
        return 0

    if autofix_enabled(convention, "attribution"):
        cleaned, removed = strip_attribution(message, convention)
        if removed:
            path.write_text(cleaned, encoding="utf-8")
            for line in removed:
                note = f"removed attribution — {line.strip()}"
                print(f"[aspis] commit-msg auto-fix: {note}", file=sys.stderr)
            message = cleaned

    errors = validate(message, convention)
    blocking = _config.blocks(root)  # "warn" (default) reports without blocking
    label = "commit-msg BLOCKED" if blocking else "commit-msg warning"
    for error in errors:
        print(f"[aspis] {label}: {error}", file=sys.stderr)
    return 1 if (blocking and errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
