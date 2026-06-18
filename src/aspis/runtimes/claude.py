"""Claude Code runtime adapter.

Claude agents key on ``name`` and a ``tools`` list, and Claude commands do NOT
bind to an agent (the binding is dropped). Model ids are data and editable.
"""

from __future__ import annotations

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, to_frontmatter


class ClaudeAdapter(RuntimeAdapter):
    """Renders catalog assets for the Claude Code runtime."""

    name = "claude"
    models = {
        "cheap": "claude-haiku-4-5-20251001",
        "standard": "claude-sonnet-4-6",
        "deep": "claude-opus-4-8",
    }

    def render_agent(self, agent: CatalogAgent) -> str:
        frontmatter = to_frontmatter(
            {
                "name": agent.name,
                "description": agent.description,
                "tools": list(agent.tools),
                "model": self.model_for(agent.model),
            }
        )
        return f"{frontmatter}\n{agent.body}\n"

    def render_command(self, command: CatalogCommand) -> str:
        # Claude commands are not bound to an agent — drop the binding.
        return f"{to_frontmatter({'description': command.description})}\n{command.body}\n"
