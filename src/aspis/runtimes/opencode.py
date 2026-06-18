"""OpenCode runtime adapter.

OpenCode agents carry a ``mode`` field and bind commands to an ``agent``. Model
ids are data here and can be edited without touching logic.
"""

from __future__ import annotations

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, to_frontmatter


class OpenCodeAdapter(RuntimeAdapter):
    """Renders catalog assets for the OpenCode runtime."""

    name = "opencode"
    models = {
        "cheap": "deepseek-v4-flash",
        "standard": "minimax-m3",
        "deep": "minimax-m2-pro",
    }

    def render_agent(self, agent: CatalogAgent) -> str:
        frontmatter = to_frontmatter(
            {
                "description": agent.description,
                "mode": agent.mode,
                "model": self.model_for(agent.model),
                "tools": list(agent.tools),
            }
        )
        return f"{frontmatter}\n{agent.body}\n"

    def render_command(self, command: CatalogCommand) -> str:
        data = {"description": command.description}
        if command.agent:
            data["agent"] = command.agent  # OpenCode binds the command to an agent
        return f"{to_frontmatter(data)}\n{command.body}\n"
