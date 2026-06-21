"""Claude Code runtime adapter.

Claude agents key on ``name`` and a ``tools`` list. Claude expresses access only
through ``tools``, auto-discovers skills, and has implicit subagent access — so
this adapter deliberately drops the superset fields it cannot express (``mode``,
``temperature``, ``permissions``, ``delegates``, ``skills``). Claude commands do
NOT bind to an agent (the binding is dropped). Model ids are data and editable.
"""

from __future__ import annotations

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, to_frontmatter


class ClaudeAdapter(RuntimeAdapter):
    """Renders catalog assets for the Claude Code runtime."""

    name = "claude"
    # Claude reads a CLAUDE.md root guide in addition to the universal AGENTS.md.
    root_guide = "CLAUDE.md"
    # Scope-guard wiring: a PreToolUse hook in Claude's settings.json.
    runtime_hooks = (("runtime-hooks/claude/settings.json", ".claude/settings.json"),)
    # Claude Code uses capitalised tool names.
    tools = {
        "read": "Read",
        "grep": "Grep",
        "glob": "Glob",
        "bash": "Bash",
        "edit": "Edit",
        "write": "Write",
        "webfetch": "WebFetch",
        "websearch": "WebSearch",
    }

    def render_agent(self, agent: CatalogAgent, *, project_config: dict | None = None) -> str:
        frontmatter = to_frontmatter(
            {
                "name": agent.name,
                "description": agent.description,
                "tools": self.tools_for(agent.tools),
                "model": self._resolve_model(agent, project_config),
            }
        )
        return f"{frontmatter}\n{agent.body}\n"

    def render_command(self, command: CatalogCommand) -> str:
        # Claude commands are not bound to an agent — drop the binding.
        return f"{to_frontmatter({'description': command.description})}\n{command.body}\n"
