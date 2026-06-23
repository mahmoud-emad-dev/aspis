"""F-014 T-06 — golden test: every command an agent's instructions name is in its allowlist.

Parses each catalog agent. For every ``aspis <sub>`` and ``python[3] .aspis/scripts/<dir>/...``
the body tells the agent to run, an allow pattern in its bash permission must cover it. This
turns the "told to do X, blocked from X" bug class (the committer / build-lead / reviewer
findings) from prose into a machine-checked invariant, so it cannot rot back in.
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path

import pytest
import yaml

from aspis import resources

_AGENTS = sorted((resources.catalog_dir() / "agents").glob("*.md"))

# The real `aspis` CLI verbs — only these are treated as commands when found after "aspis"
# in prose (so phrases like "the aspis system" are not mistaken for a command).
_ASPIS_VERBS = {
    "init",
    "bootstrap",
    "status",
    "mode",
    "models",
    "doctor",
    "gitignore",
    "commit",
    "commits",
    "artifact",
    "testledger",
    "preflight",
    "context",
}


def _split(md: str) -> tuple[dict, str]:
    parts = md.split("---", 2)
    front = (yaml.safe_load(parts[1]) or {}) if len(parts) >= 3 else {}
    body = parts[2] if len(parts) >= 3 else md
    return front, body


def _allow_patterns(front: dict) -> tuple[dict, list[str]]:
    bash = (front.get("permissions") or {}).get("bash")
    bash = bash if isinstance(bash, dict) else {}
    return bash, [k for k, v in bash.items() if v == "allow"]


def _referenced_skill_text(front: dict) -> str:
    """The body text of every skill the agent references — its instructions extend the agent's."""
    chunks: list[str] = []
    for name in front.get("skills") or []:
        skill_file = resources.catalog_dir() / "skills" / name / "SKILL.md"
        if skill_file.is_file():
            chunks.append(skill_file.read_text(encoding="utf-8"))
    return "\n".join(chunks)


@pytest.mark.parametrize("agent_path", _AGENTS, ids=lambda p: p.stem)
def test_agent_named_commands_are_in_its_allowlist(agent_path: Path) -> None:
    front, body = _split(agent_path.read_text(encoding="utf-8"))
    bash, allows = _allow_patterns(front)

    # A read-only agent (no bash capability) runs no commands — it reads files; skill command
    # steps simply don't apply to it. A broad allow-all bash can run anything. Either way: nothing
    # to check.
    if not bash or bash.get("*") == "allow":
        return

    # Commands the agent is told to run — by its own body AND by the skills it references (a
    # referenced skill's instructions extend the agent's, so its commands must be permitted too).
    text = body + "\n" + _referenced_skill_text(front)

    # `aspis <verb>` (only real CLI verbs).
    found = {v for v in re.findall(r"\baspis\s+([a-z][a-z-]*)", text) if v in _ASPIS_VERBS}
    for verb in sorted(found):
        covered = any(p == "aspis *" or p.startswith(f"aspis {verb}") for p in allows)
        assert covered, f"{agent_path.stem}: named `aspis {verb}` but no bash allow covers it"

    # `python .aspis/scripts/<dir>/...` (and python3).
    for interp, sdir in sorted(set(re.findall(r"\b(python3?)\s+(\.aspis/scripts/[a-z_]+)", text))):
        sample = f"{interp} {sdir}/x.py"
        covered = any(fnmatch(sample, p) for p in allows)
        assert covered, f"{agent_path.stem}: named `{interp} {sdir}/...` but no allow covers it"
