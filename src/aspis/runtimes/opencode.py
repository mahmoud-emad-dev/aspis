"""OpenCode runtime adapter.

OpenCode agents carry a ``mode``, a ``temperature``, and a single ``permission``
block that folds together tool access, bash policy, delegation (``task``), and
skill access. This adapter translates the catalog superset into that shape; model
ids are data and can be edited without touching logic.
"""

from __future__ import annotations

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, to_frontmatter

# Canonical tool tokens that map straight to an allow/ask/deny permission key.
_SIMPLE_TOOLS = ("read", "list", "glob", "grep", "edit", "write")
# Tokens that default to deny when the agent does not list them.
_GATED_TOOLS = ("webfetch", "websearch")


class OpenCodeAdapter(RuntimeAdapter):
    """Renders catalog assets for the OpenCode runtime."""

    name = "opencode"
    models = {
        "cheap": "deepseek-v4-flash",
        "standard": "minimax-m3",
        "deep": "minimax-m2-pro",
    }

    def render_agent(self, agent: CatalogAgent) -> str:
        data: dict = {
            "description": agent.description,
            "mode": agent.mode,
            "model": self.model_for(agent.model),
        }
        if agent.temperature is not None:
            data["temperature"] = agent.temperature
        data["permission"] = self._permission(agent)
        return f"{to_frontmatter(data)}\n{agent.body}\n"

    def _permission(self, agent: CatalogAgent) -> dict:
        """Fold tools, bash policy, delegation, and skills into one permission block."""
        perm: dict = {}
        for token in agent.tools:
            if token in _SIMPLE_TOOLS:
                perm[token] = "allow"
        # bash policy may be a plain allow or a pattern map; explicit wins.
        if "bash" in agent.permissions:
            perm["bash"] = agent.permissions["bash"]
        elif "bash" in agent.tools:
            perm["bash"] = "allow"
        # Delegation and skill access become allow-lists (deny everything else).
        if agent.delegates:
            perm["task"] = {"*": "deny", **{name: "allow" for name in agent.delegates}}
        if agent.skills:
            perm["skill"] = {"*": "deny", **{name: "allow" for name in agent.skills}}
        # Network tools default to deny unless granted.
        for token in _GATED_TOOLS:
            perm[token] = agent.permissions.get(token, "allow" if token in agent.tools else "deny")
        return perm

    def render_command(self, command: CatalogCommand) -> str:
        data = {"description": command.description}
        if command.agent:
            data["agent"] = command.agent  # OpenCode binds the command to an agent
        return f"{to_frontmatter(data)}\n{command.body}\n"
