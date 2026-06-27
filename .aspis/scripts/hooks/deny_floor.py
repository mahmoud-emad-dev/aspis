#!/usr/bin/env python3
"""Deny-floor check — PreToolUse scope guard (R-008 surface, F-018 T-044).

Reads an agent's catalog frontmatter (``deny_floor`` if present, otherwise the
legacy ``permissions`` block) and decides whether a tool call would violate the
agent's scope. The runtime guard invokes this hook before a tool fires; the
verdict is one of:

- ``ALLOW`` — an explicit allow rule matches, or a more specific rule is allow.
- ``DENY``  — an explicit deny rule matches, or the default ``*`` rule is deny.
- ``WARN``  — no rule matches; the floor is silent on this tool, so the caller
  should consult the broader permissions elsewhere.

Stdlib (plus PyYAML for the frontmatter, as listed in the F-018 SPEC).
"""
from __future__ import annotations

import argparse
import sys
from fnmatch import fnmatch
from pathlib import Path

import yaml

# Resolved at import time from __file__; the hook always lives at
# .aspis/scripts/hooks/deny_floor.py, so parents[3] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_DIR = REPO_ROOT / "src" / "aspis" / "data" / "catalog" / "agents"


def load_agent(agent: str) -> dict:
    """Load and parse the YAML frontmatter of ``src/aspis/data/catalog/agents/<agent>.md``.

    Returns the parsed frontmatter dict. Raises ``FileNotFoundError`` if the
    agent file is missing, ``ValueError`` if the frontmatter is malformed.
    """
    path = CATALOG_DIR / f"{agent}.md"
    if not path.exists():
        raise FileNotFoundError(f"agent '{agent}' not found at {path}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"agent '{agent}' has no YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"agent '{agent}' frontmatter is not closed")
    block = text[4:end]
    data = yaml.safe_load(block)
    return data if isinstance(data, dict) else {}


def get_floor(agent_data: dict) -> tuple[dict, str]:
    """Return ``(floor_dict, source_name)``.

    Prefers the explicit ``deny_floor`` field; falls back to the legacy
    ``permissions`` block (used by older agents such as ``committer``); reports
    ``"none"`` if neither is present.
    """
    if "deny_floor" in agent_data and agent_data["deny_floor"]:
        return agent_data["deny_floor"], "deny_floor"
    if "permissions" in agent_data and agent_data["permissions"]:
        return agent_data["permissions"], "permissions"
    return {}, "none"


def _check_bash(pattern: str, rules: dict, agent: str, source: str) -> tuple[str, str]:
    """Match ``pattern`` against the bash submap; the most specific rule wins.

    Specificity = ``len(rule_pattern)``; longer = more specific. This matches
    how runtime guards reason about the same data: a specific allow beats the
    default ``*`` deny, and vice-versa.
    """
    if not pattern:
        return "WARN", "empty bash command"
    matches: list[tuple[int, str, str]] = []
    for rule_pat, value in rules.items():
        rule_pat_s = str(rule_pat)
        if fnmatch(pattern, rule_pat_s):
            matches.append((len(rule_pat_s), rule_pat_s, str(value).strip().lower()))
    if not matches:
        return "WARN", f"no rule matches '{pattern}' in {source}.bash"
    matches.sort(key=lambda m: -m[0])
    best_specificity, best_pat, best_value = matches[0]
    if best_value == "deny":
        return "DENY", f"'{pattern}' matches '{best_pat}' (deny) in {source}.bash"
    if best_value == "allow":
        return "ALLOW", f"'{pattern}' matches '{best_pat}' (allow) in {source}.bash"
    return (
        "WARN",
        f"'{pattern}' matches '{best_pat}' with non-boolean value '{best_value}'",
    )


def _check_simple(key: str, floor: dict, source: str) -> tuple[str, str]:
    """Look up a top-level scalar permission (``webfetch``/``websearch``/``file_write``)."""
    if key in floor:
        verdict = str(floor[key]).strip().lower()
        if verdict == "deny":
            return "DENY", f"{source}.{key} = deny"
        if verdict == "allow":
            return "ALLOW", f"{source}.{key} = allow"
        return "WARN", f"{source}.{key} has non-boolean value '{verdict}'"
    return "WARN", f"{source}.{key} is not set"


def check_deny_floor(agent: str, tool: str) -> tuple[str, str]:
    """Return ``(verdict, reason)`` for ``tool`` against ``agent``'s floor.

    Tool format: ``"<category>: <pattern>"`` (e.g. ``"bash: git push"``) or a
    bare category name (e.g. ``"webfetch"``). Recognised categories:
    ``bash``, ``webfetch``, ``websearch``, ``edit``, ``write``, ``file_write``.
    """
    data = load_agent(agent)
    floor, source = get_floor(data)
    if not floor:
        return "WARN", f"agent '{agent}' has no deny_floor or permissions"

    if ":" in tool:
        category, _, pattern = tool.partition(":")
        category = category.strip().lower()
        pattern = pattern.strip()
    else:
        category, pattern = tool.strip().lower(), ""

    if category == "bash":
        rules = floor.get("bash")
        if not isinstance(rules, dict) or not rules:
            return "WARN", f"{source}.bash is not a map for agent '{agent}'"
        return _check_bash(pattern, rules, agent, source)
    if category in ("webfetch", "websearch"):
        return _check_simple(category, floor, source)
    if category in ("edit", "write"):
        # Legacy permissions blocks use "edit" / "write" at the top level;
        # newer deny_floor blocks fold both under "file_write". Prefer the
        # legacy key when present so older agents are checked faithfully.
        if category in floor:
            return _check_simple(category, floor, source)
        return _check_simple("file_write", floor, source)
    if category == "file_write":
        return _check_simple("file_write", floor, source)
    return "WARN", f"unknown tool category '{category}'"


def main() -> int:
    """CLI entry point: parse args, run the check, print ``VERDICT — reason``."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether a tool call would violate an agent's deny_floor. "
            "Reads .aspis/data/catalog/agents/<agent>.md and returns "
            "ALLOW / DENY / WARN."
        ),
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (looks up src/aspis/data/catalog/agents/<agent>.md).",
    )
    parser.add_argument(
        "--tool",
        required=True,
        help="Tool call to check, e.g. 'bash: git push' or 'webfetch'.",
    )
    args = parser.parse_args()

    try:
        verdict, reason = check_deny_floor(args.agent, args.tool)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 0
    except (ValueError, yaml.YAMLError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 0

    print(f"{verdict} — {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
