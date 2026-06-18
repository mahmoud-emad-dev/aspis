"""Runtime adapter interface + shared rendering helpers.

Each runtime tool (OpenCode, Claude Code, ...) gets one adapter module that
turns a parsed catalog asset into that runtime's on-disk format. The transformer
dispatches to the right adapter, so adding a runtime is adding a module and
registering it — no change to the transformer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import yaml

from aspis.catalog import CatalogAgent, CatalogCommand


class RuntimeAdapter(ABC):
    """Renders catalog assets for one runtime tool."""

    #: Runtime key used in profiles and the registry (e.g. "opencode").
    name: str

    #: Map a model tier (cheap/standard/deep) to this runtime's concrete model id.
    models: dict[str, str]

    def model_for(self, tier: str) -> str:
        """Resolve a model tier to a concrete id, falling back to ``standard``."""
        return self.models.get(tier, self.models["standard"])

    @abstractmethod
    def render_agent(self, agent: CatalogAgent) -> str:
        """Return the runtime's on-disk agent file (frontmatter + body)."""

    @abstractmethod
    def render_command(self, command: CatalogCommand) -> str:
        """Return the runtime's on-disk command file (frontmatter + body)."""


def to_frontmatter(data: dict) -> str:
    """Render *data* as a YAML frontmatter block (key order preserved)."""
    body = yaml.safe_dump(data, sort_keys=False, default_flow_style=False).strip()
    return f"---\n{body}\n---\n"
