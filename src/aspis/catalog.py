"""Catalog asset format + parsing.

Catalog assets are runtime-neutral markdown with a small YAML frontmatter (the
"abstraction") and a body. Parsing lives here so the whole engine agrees on what
an agent or command looks like; per-runtime rendering lives in the runtime
adapters. The real asset files are authored later (catalog feature) — this
module only defines and reads the format.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

# Split a markdown file into (frontmatter, body) when it opens with a --- block.
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


@dataclass(frozen=True)
class CatalogAgent:
    """A runtime-neutral agent definition parsed from a catalog file."""

    name: str
    description: str = ""
    mode: str = "subagent"  # primary | subagent
    model: str = "standard"  # cheap | standard | deep
    skills: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    export_scope: str = "all"  # all | export-only | project-only
    body: str = ""


@dataclass(frozen=True)
class CatalogCommand:
    """A runtime-neutral command definition parsed from a catalog file."""

    name: str
    description: str = ""
    agent: str = ""  # the agent this command runs as (dropped on runtimes that don't bind)
    export_scope: str = "all"
    body: str = ""


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return ``(frontmatter, body)``; frontmatter is ``{}`` when absent."""
    match = _FRONTMATTER.match(text)
    if not match:
        return {}, text.strip()
    return yaml.safe_load(match.group(1)) or {}, match.group(2).strip()


def parse_agent(text: str) -> CatalogAgent:
    """Parse a catalog agent markdown file into a :class:`CatalogAgent`."""
    data, body = split_frontmatter(text)
    return CatalogAgent(
        name=data["name"],
        description=data.get("description", ""),
        mode=data.get("mode", "subagent"),
        model=data.get("model", "standard"),
        skills=tuple(data.get("skills", [])),
        tools=tuple(data.get("tools", [])),
        export_scope=data.get("export_scope", "all"),
        body=body,
    )


def parse_command(text: str) -> CatalogCommand:
    """Parse a catalog command markdown file into a :class:`CatalogCommand`."""
    data, body = split_frontmatter(text)
    return CatalogCommand(
        name=data["name"],
        description=data.get("description", ""),
        agent=data.get("agent", ""),
        export_scope=data.get("export_scope", "all"),
        body=body,
    )
