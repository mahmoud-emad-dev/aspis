"""Runtime adapter interface + shared rendering helpers.

Purpose:
    Define the RuntimeAdapter contract every runtime implements, plus the
    shared behaviour (model resolution, capability checks, runtime-hook
    placement, frontmatter rendering) so each concrete adapter writes only
    what genuinely differs. The transformer dispatches to the right adapter,
    so adding a runtime is one module — no change to the transformer.

Responsibilities:
    - The RuntimeAdapter ABC: render_agent / render_command (abstract),
      supports(kind), detect(), model_string(), and the declarative facts
      loaded from data/runtimes/<name>.yaml.
    - RuntimeInventory: the per-machine record of a runtime's provider/model
      presence.
    - to_frontmatter: the one YAML-frontmatter renderer every adapter shares.

Does Not:
    - Name or special-case any concrete runtime — capabilities decide
      behaviour, not names.
    - Read profiles or write exports (that is aspis.export's job).

Used By:
    aspis.transform, aspis.export, aspis.runtimes.{opencode,claude}, and the
    models / detection layer.
"""

from __future__ import annotations

import shutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from aspis.catalog import CatalogAgent, CatalogCommand

# Placeholder in runtime-hook source files, replaced at emit with the resolved interpreter
# (``sys.executable``, posix-form so one spelling works on Windows + Linux). This bakes the
# interpreter at install — the same approach the git-hook installer uses — so a hook never
# guesses ``python3`` (absent on Windows) and silently no-ops.
_PY_PLACEHOLDER = "__ASPIS_PY__"


def _emit_hook_file(source: Path, destination: Path) -> None:
    """Place a runtime-hook file, baking the interpreter path if it carries the placeholder."""
    text = source.read_text(encoding="utf-8")
    if _PY_PLACEHOLDER not in text:
        shutil.copy2(source, destination)
        return
    interpreter = Path(sys.executable).as_posix()
    destination.write_text(text.replace(_PY_PLACEHOLDER, interpreter), encoding="utf-8")


@dataclass(frozen=True)
class RuntimeInventory:
    """What a runtime offers on the current machine — provider *presence*, not plan/quota.

    Produced by :meth:`RuntimeAdapter.detect` and persisted (per machine) as generated
    state. ``providers`` are the connected provider ids; ``models`` are the concrete
    runtime model strings actually available (e.g. ``"opencode-go/minimax-m3"``), which
    :meth:`RuntimeAdapter.model_string` matches a canonical id against.
    """

    runtime: str
    installed: bool = False
    providers: tuple[str, ...] = ()
    models: tuple[str, ...] = field(default_factory=tuple)


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

    #: Scope-guard wiring as (catalog-relative source, project-relative target) pairs.
    #: Empty ⇒ this runtime emits no runtime hooks (the capability is opt-in by data).
    runtime_hooks: tuple[tuple[str, str], ...] = ()

    #: This runtime's own root-guide filename written at the project root (e.g.
    #: ``"CLAUDE.md"``). ``None`` ⇒ the runtime relies on the universal ``AGENTS.md``
    #: and gets no extra guide. Lets init emit guides without naming a runtime.
    root_guide: str | None = None

    #: Whether this runtime expresses an agent ``mode`` field in frontmatter. Only
    #: such a runtime can have its leads promoted from subagent to primary, so lead
    #: promotion targets the runtime that sets this rather than a hardcoded name.
    supports_mode: bool = False

    @property
    def runtime_dir(self) -> str:
        """This runtime's on-disk project dir (e.g. ``.claude``), from its definition.

        Sourced from ``data/runtimes/<name>.yaml`` (``dir:``), defaulting to the
        ``.<runtime>`` convention, so callers ask the adapter rather than rebuilding it.
        """
        return self._runtime_dir

    def supports(self, kind: str) -> bool:
        """Whether this runtime accepts assets of *kind* (``None`` ⇒ all kinds)."""
        return self.capabilities is None or kind in self.capabilities

    def emit_runtime_hooks(
        self, catalog_root: Path, target_root: Path, *, force: bool = False, write: bool = False
    ) -> list[str]:
        """Place this runtime's scope-guard wiring; honours force/write like the exporter.

        Runtime hooks are runtime-specific files at fixed locations (Claude's
        ``settings.json``, OpenCode's plugin), so the adapter owns the placement
        rather than the uniform per-kind target rule.
        """
        performed: list[str] = []
        for src_rel, dst_rel in self.runtime_hooks:
            source = catalog_root / src_rel
            destination = target_root / dst_rel
            if not source.is_file():
                continue
            if destination.exists() and not force:
                performed.append(f"skip (exists): {dst_rel}")
                continue
            performed.append(f"copy: {dst_rel}")
            if write:
                destination.parent.mkdir(parents=True, exist_ok=True)
                _emit_hook_file(source, destination)
        return performed

    def __init__(self) -> None:
        from aspis import resources

        #: tier->concrete model id, loaded from the global models.yaml (data, not code).
        self.models: dict[str, str] = resources.model_map(self.name)

        # Declarative facts come from the runtime definition (data SSoT); class-attr
        # defaults are the fallback when no definition file exists for this runtime.
        spec = resources.runtime_def(self.name)
        caps = spec.get("capabilities") or {}
        self.supports_mode = bool(caps.get("mode", type(self).supports_mode))
        self.subagent_depth: int = int(caps.get("subagent_depth", 0))
        self.exportable: bool = bool(caps.get("exportable", True))
        self.run_command: str = spec.get("run") or self.name
        self._runtime_dir: str = spec.get("dir") or f".{self.name}"
        if "root_guide" in spec:
            self.root_guide = spec.get("root_guide")

    def model_for(self, tier: str) -> str:
        """Resolve a model tier to a concrete id, falling back to ``standard``."""
        return self.models.get(tier, self.models.get("standard", tier))

    def detect(self) -> RuntimeInventory | None:
        """Detect what this runtime offers on the current machine.

        Returns ``None`` when the runtime is not installed/usable here, so detection
        is a per-runtime plugin and the orchestrator never name-checks a runtime. The
        base default is "not installed"; each adapter overrides with its own probe.
        Implementations MUST be cross-platform and MUST never raise — any failure
        means "not detected" (return ``None``), never a crash (FR-004/FR-006).
        """
        return None

    def model_string(self, canonical_id: str, inventory: RuntimeInventory | None = None) -> str:
        """Translate a canonical model id into the exact string this runtime expects.

        The canonical id (e.g. ``"minimax-m3"``) is provider-neutral; a runtime spells
        it differently per connected provider. When an *inventory* is given, adapters
        match the canonical id against the real available strings; with no inventory the
        base default is the identity (the canonical id is already a usable string), which
        preserves today's behaviour and keeps the resolver working for any user.
        """
        return canonical_id

    def tools_for(self, tokens: tuple[str, ...]) -> list[str]:
        """Map canonical tool tokens to this runtime's tool names (order preserved)."""
        return [self.tools.get(token, token) for token in tokens]

    @abstractmethod
    def render_agent(
        self,
        agent: CatalogAgent,
        *,
        project_config: dict | None = None,
        inventory: RuntimeInventory | None = None,
    ) -> str:
        """Return the runtime's on-disk agent file (frontmatter + body)."""

    def _resolve_model(
        self,
        agent: CatalogAgent,
        project_config: dict | None,
        inventory: RuntimeInventory | None = None,
    ) -> str:
        """Resolve an agent's model and translate it to this runtime's string.

        Runs the full resolver: tier/pin/override precedence to a canonical id, then
        ``model_string()`` against the detected *inventory*. With no inventory the
        translation is the identity, so rendered output is unchanged for any user who
        has not run detection (and the committed dogfood stays canonical).
        """
        from aspis import models, project, resources

        agent_caps = resources.config("agent-capabilities.yaml").get("agents", {})
        return models.resolve(
            self.name,
            agent.name,
            agent.model,
            global_map=self.models,
            project_config=project_config or {},
            global_config=project.load_global_config(),
            translate=self.model_string,
            inventory=inventory,
            agent_capability=agent_caps.get(agent.name),
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
