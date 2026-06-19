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

    #: Map a canonical tool token (read/bash/...) to this runtime's tool name.
    #: Unmapped tokens pass through unchanged.
    tools: dict[str, str] = {}

    #: Asset kinds this runtime accepts; ``None`` means it accepts every kind.
    #: A runtime opts out of a per-runtime kind by listing only what it supports.
    capabilities: frozenset[str] | None = None

    def supports(self, kind: str) -> bool:
        """Whether this runtime accepts assets of *kind* (``None`` ⇒ all kinds)."""
        return self.capabilities is None or kind in self.capabilities

    def __init__(self) -> None:
        from aspis import resources

        #: tier->concrete model id, loaded from the global models.yaml (data, not code).
        self.models: dict[str, str] = resources.model_map(self.name)

    def model_for(self, tier: str) -> str:
        """Resolve a model tier to a concrete id, falling back to ``standard``."""
        return self.models.get(tier, self.models.get("standard", tier))

    def tools_for(self, tokens: tuple[str, ...]) -> list[str]:
        """Map canonical tool tokens to this runtime's tool names (order preserved)."""
        return [self.tools.get(token, token) for token in tokens]

    @abstractmethod
    def render_agent(self, agent: CatalogAgent, *, project_config: dict | None = None) -> str:
        """Return the runtime's on-disk agent file (frontmatter + body)."""

    def _resolve_model(self, agent: CatalogAgent, project_config: dict | None) -> str:
        """Resolve an agent's concrete model id, honouring project overrides/pins."""
        if not project_config:
            return self.model_for(agent.model)
        from aspis import models

        return models.effective_model(
            self.name,
            agent.name,
            agent.model,
            global_map=self.models,
            project_config=project_config,
        )

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
