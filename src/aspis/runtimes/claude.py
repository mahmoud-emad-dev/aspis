"""Claude Code runtime adapter.

Claude agents key on ``name`` and a ``tools`` list. Claude expresses tool access
through ``tools`` and auto-discovers skills, so this adapter drops the fields
Claude consumes natively in another way (``mode``, ``temperature``,
``delegates``, ``skills``). It DOES preserve the catalog ``permissions`` block
(FR-010): the deny floor and the R-008 protected-path set are load-bearing
safety, so they ride along in the rendered frontmatter for capability-equivalence
with OpenCode and for a PreToolUse guard to enforce. (Native Claude enforcement of
that block additionally requires the settings.json PreToolUse hook — a follow-up;
preserving the block is the prerequisite and what FR-010 requires.) Claude commands
do NOT bind to an agent (the binding is dropped). Model ids are data and editable.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, RuntimeInventory, to_frontmatter

# Durable aliases Claude Code accepts for --model / frontmatter (verified, more
# stable than dated ids). A canonical ``claude-<family>-*`` id maps to its alias.
_CLAUDE_ALIASES = ("opus", "sonnet", "haiku", "fable")


class ClaudeAdapter(RuntimeAdapter):
    """Renders catalog assets for the Claude Code runtime."""

    name = "claude"
    # root_guide (CLAUDE.md) / mode / dir come from data/runtimes/claude.yaml (data SSoT).
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

    def render_agent(
        self,
        agent: CatalogAgent,
        *,
        project_config: dict | None = None,
        inventory: RuntimeInventory | None = None,
    ) -> str:
        data: dict = {
            "name": agent.name,
            "description": agent.description,
            "tools": self.tools_for(agent.tools),
            "model": self._resolve_model(agent, project_config, inventory),
        }
        # FR-010: preserve the permission block (deny floor + R-008 protected
        # paths) so the runtime can enforce capability-equivalence with OpenCode.
        if agent.permissions:
            data["permissions"] = dict(agent.permissions)
        return f"{to_frontmatter(data)}\n{agent.body}\n"

    def render_command(self, command: CatalogCommand) -> str:
        # Claude commands are not bound to an agent — drop the binding.
        return f"{to_frontmatter({'description': command.description})}\n{command.body}\n"

    # --- detection (D-018) -------------------------------------------------
    # Claude Code keeps a readable settings.json (no secrets) under ~/.claude
    # (or %USERPROFILE%\.claude); its presence — or the `claude` binary on PATH —
    # means the runtime is usable here. Available models are the durable alias set;
    # plan/quota is not scriptable, so we record provider presence only.

    def detect(self) -> RuntimeInventory | None:
        """Report Claude presence (settings.json or binary) + the durable alias set."""
        try:
            installed = self._settings_path().is_file() or shutil.which("claude") is not None
            if not installed:
                return None
            return RuntimeInventory(
                runtime=self.name,
                installed=True,
                providers=("anthropic",),
                models=_CLAUDE_ALIASES,
            )
        except Exception:
            return None

    def model_string(self, canonical_id: str, inventory: RuntimeInventory | None = None) -> str:
        """Translate a canonical ``claude-<family>-*`` id to its durable alias when detected.

        Only translates when an *inventory* offers the alias — so with no detection the
        rendered output is the canonical id, identical to today (SC-004, dogfood parity).
        """
        if inventory and inventory.models:
            cid = canonical_id.lower()
            if cid.startswith("claude-"):
                family = cid[len("claude-") :]
                for alias in _CLAUDE_ALIASES:
                    if family.startswith(alias) and alias in inventory.models:
                        return alias
        return canonical_id

    @staticmethod
    def _settings_path() -> Path:
        """Resolve ~/.claude/settings.json cross-platform (``CLAUDE_CONFIG_DIR`` overrides)."""
        base = os.environ.get("CLAUDE_CONFIG_DIR")
        root = Path(base) if base else Path.home() / ".claude"
        return root / "settings.json"
