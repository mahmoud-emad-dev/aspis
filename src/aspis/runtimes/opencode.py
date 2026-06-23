"""OpenCode runtime adapter.

OpenCode agents carry a ``mode``, a ``temperature``, and a single ``permission``
block that folds together tool access, bash policy, delegation (``task``), and
skill access. This adapter translates the catalog superset into that shape; model
ids are data and can be edited without touching logic.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from aspis.catalog import CatalogAgent, CatalogCommand
from aspis.runtimes.base import RuntimeAdapter, RuntimeInventory, to_frontmatter

# Canonical tool tokens that map straight to an allow/ask/deny permission key.
_SIMPLE_TOOLS = ("read", "list", "glob", "grep", "edit", "write")
# Tokens that default to deny when the agent does not list them.
_GATED_TOOLS = ("webfetch", "websearch")


class OpenCodeAdapter(RuntimeAdapter):
    """Renders catalog assets for the OpenCode runtime."""

    name = "opencode"
    # supports_mode / root_guide / dir come from data/runtimes/opencode.yaml (data SSoT).
    # Lite, fire-and-forget runtime plugin: a session.created notice that surfaces open
    # findings. No per-tool-call hook — scope is checked at the git boundary (pre-commit),
    # so the runtime never gates or slows an individual edit.
    runtime_hooks = (
        ("runtime-hooks/opencode/session-notice.ts", ".opencode/plugins/session-notice.ts"),
    )

    def render_agent(
        self,
        agent: CatalogAgent,
        *,
        project_config: dict | None = None,
        inventory: RuntimeInventory | None = None,
    ) -> str:
        data: dict = {
            "description": agent.description,
            "mode": agent.mode,
            "model": self._resolve_model(agent, project_config, inventory),
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

    # --- detection (D-018) -------------------------------------------------
    # OpenCode stores connected providers in auth.json (an XDG path, not %APPDATA%
    # — verified landmine) and lists every available `provider/model` string via
    # `opencode models`. We read provider PRESENCE (the auth.json keys, never the
    # secret values) and the available strings, so translation matches a canonical
    # id against what the machine can actually run. Any failure means "not detected".

    def detect(self) -> RuntimeInventory | None:
        """Read connected providers (auth.json keys) + available model strings."""
        try:
            providers = self._auth_providers()
            installed = bool(providers) or shutil.which("opencode") is not None
            if not installed:
                return None
            return RuntimeInventory(
                runtime=self.name,
                installed=True,
                providers=providers,
                models=self._available_models(),
            )
        except Exception:
            return None

    def model_string(self, canonical_id: str, inventory: RuntimeInventory | None = None) -> str:
        """Match a canonical id to an available `provider/model` string for a connected provider.

        Picks the lowest-`prefer`-rank connected provider that actually lists the model
        (per `providers.yaml`), matching on the model id's final path segment. With no
        inventory (or no match), returns the canonical id unchanged — preserving today's
        rendered output so the resolver still works for a user with no detection.
        """
        if inventory and inventory.models:
            connected = set(inventory.providers)
            ranks = _provider_ranks()
            target = canonical_id.lower()
            candidates = []
            for available in inventory.models:
                provider = available.split("/", 1)[0]
                if connected and provider not in connected:
                    continue
                if available.rsplit("/", 1)[-1].lower() == target:
                    candidates.append((ranks.get(provider, 99), available))
            if candidates:
                return min(candidates)[1]
        return canonical_id

    @staticmethod
    def _auth_path() -> Path:
        """Resolve auth.json cross-platform (XDG; Windows native = %USERPROFILE%\\.local\\share)."""
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
        return base / "opencode" / "auth.json"

    def _auth_providers(self) -> tuple[str, ...]:
        """The connected provider ids — auth.json keys only, never the secret values."""
        content = os.environ.get("OPENCODE_AUTH_CONTENT")
        if content is None:
            path = self._auth_path()
            if not path.is_file():
                return ()
            content = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(content)
        return tuple(data) if isinstance(data, dict) else ()

    def _available_models(self) -> tuple[str, ...]:
        """Parse `opencode models` for available `provider/model` strings (empty if it fails).

        Self-contained and never raises: a missing binary, a Windows ``.CMD`` shim that
        won't exec, a non-zero exit, or a timeout all degrade to ``()`` so detection still
        returns the connected providers it already read. Uses the path resolved by
        ``shutil.which`` (which carries the ``.CMD``/``.EXE`` suffix Windows needs).
        """
        executable = shutil.which("opencode")
        if executable is None:
            return ()
        # Windows `.CMD`/`.BAT` shims (how npm installs `opencode`) cannot be exec'd
        # argv-style via CreateProcess — they must go through the shell. Everywhere
        # else, run the resolved path directly (no shell).
        if os.name == "nt" and executable.lower().endswith((".cmd", ".bat")):
            command: str | list[str] = f'"{executable}" models'
            shell = True
        else:
            command = [executable, "models"]
            shell = False
        try:
            proc = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            return ()
        if proc.returncode != 0:
            return ()
        return _parse_models(proc.stdout)


def _parse_models(text: str) -> tuple[str, ...]:
    """Keep the `provider/model` lines from `opencode models` output (drop blanks/noise)."""
    return tuple(
        line.strip()
        for line in text.splitlines()
        if "/" in line and not line.strip().startswith("─")
    )


def _provider_ranks() -> dict[str, int]:
    """Provider -> preference rank (lower = preferred) from `providers.yaml` data."""
    from aspis import resources

    providers = resources.config("providers.yaml").get("providers", {})
    return {pid: info.get("prefer", 99) for pid, info in providers.items()}
