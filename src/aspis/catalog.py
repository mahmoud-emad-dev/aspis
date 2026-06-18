"""Catalog asset format + parsing.

Catalog assets are runtime-neutral markdown with a small YAML frontmatter (the
"abstraction") and a body. Parsing lives here so the whole engine agrees on what
an agent or command looks like; per-runtime rendering lives in the runtime
adapters. The real asset files are authored later (catalog feature) — this
module only defines and reads the format.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import yaml

# Split a markdown file into (frontmatter, body) when it opens with a --- block.
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


@dataclass(frozen=True)
class CatalogAgent:
    """A runtime-neutral agent definition — the superset every runtime renders from.

    The catalog format is deliberately richer than any single runtime: it holds
    every property *some* runtime can use, plus our own control fields. Each
    runtime adapter reads this and emits only the fields it understands, in its
    own format — anything it cannot use is skipped, never an error. Field notes:

    - ``mode`` — primary vs subagent. OpenCode renders it; Claude has no such
      field and drops it.
    - ``model`` — a tier (cheap/standard/deep); each adapter maps it to a concrete
      model id, so the catalog never pins a vendor model.
    - ``temperature`` — sampling temperature; OpenCode renders it, Claude drops it.
    - ``tools`` — canonical capability tokens (read/grep/bash/...); each adapter
      maps them to its own tool names (Claude ``tools`` list, OpenCode permission).
    - ``permissions`` — policy per capability (allow/ask/deny, bash patterns).
      OpenCode renders a ``permission`` block; Claude expresses access via ``tools``
      only, so it drops this.
    - ``delegates`` — which agents this one may hand work to. OpenCode renders it
      as a ``permission.task`` allow-list; Claude has implicit subagent access and
      drops it. Also machine-readable for routing validation.
    - ``skills`` — which skills this agent may use. OpenCode renders a
      ``permission.skill`` allow-list; Claude auto-discovers skills and drops it.
    - ``runtimes`` — runtime-lock: the runtimes this asset is valid for. Empty
      means all; otherwise export skips runtimes outside the list.
    - ``export_scope`` — all | export-only | project-only (factory-only assets).
    """

    name: str
    description: str = ""
    mode: str = "subagent"  # primary | subagent
    model: str = "standard"  # cheap | standard | deep
    temperature: float | None = None
    tools: tuple[str, ...] = ()
    permissions: dict = field(default_factory=dict)
    delegates: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    runtimes: tuple[str, ...] = ()
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
        temperature=data.get("temperature"),
        tools=tuple(data.get("tools", [])),
        permissions=dict(data.get("permissions", {})),
        delegates=tuple(data.get("delegates", [])),
        skills=tuple(data.get("skills", [])),
        runtimes=tuple(data.get("runtimes", [])),
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
