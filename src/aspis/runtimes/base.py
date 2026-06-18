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

    #: Map a canonical tool token (read/bash/...) to this runtime's tool name.
    #: Unmapped tokens pass through unchanged.
    tools: dict[str, str] = {}

    def model_for(self, tier: str) -> str:
        """Resolve a model tier to a concrete id, falling back to ``standard``."""
        return self.models.get(tier, self.models["standard"])

    def tools_for(self, tokens: tuple[str, ...]) -> list[str]:
        """Map canonical tool tokens to this runtime's tool names (order preserved)."""
        return [self.tools.get(token, token) for token in tokens]

    @abstractmethod
    def render_agent(self, agent: CatalogAgent) -> str:
        """Return the runtime's on-disk agent file (frontmatter + body)."""

    @abstractmethod
    def render_command(self, command: CatalogCommand) -> str:
        """Return the runtime's on-disk command file (frontmatter + body)."""


def to_frontmatter(data: dict) -> str:
    """Render *data* as a YAML frontmatter block (key order preserved)."""
    # allow_unicode keeps em-dashes readable; the wide width stops long
    # descriptions from being backslash-wrapped into noise.
    body = yaml.safe_dump(
        data, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000
    ).strip()
    return f"---\n{body}\n---\n"
