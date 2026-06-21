"""Asset-kind registry — the single source of how each catalog kind is placed.

Purpose:
    Describe every asset kind once: where its exported copy lands (the portable
    ``.aspis/`` brain vs. each runtime dir) and how it is written (a verbatim
    copy vs. rendered through a runtime adapter). ``export.py`` reads from here,
    so adding a new brain-copied kind is just dropping a ``catalog/<kind>/`` dir
    and listing it in a profile — no code change anywhere (Local Change rule).

Responsibilities:
    - Define the AssetKind contract (name, placement, write op).
    - Resolve a kind's target path and write op for a given runtime.
    - Tell callers which kinds are placed per-runtime.

Does Not:
    - Read profiles or touch the filesystem (export.py owns planning + writes).
    - Know any concrete runtime (whether a runtime accepts a kind is the
      adapter's ``supports`` capability, not the registry's concern).

Used By:
    export.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aspis.constants import BRAIN_DIR
from aspis.runtimes import get_adapter

#: Placement: the durable brain (once) vs. each target runtime dir.
BRAIN = "brain"
PER_RUNTIME = "per_runtime"

#: Write ops — kept identical to the strings ``export._apply`` dispatches on.
COPY = "copy"
RENDER_AGENT = "render-agent"
RENDER_COMMAND = "render-command"


@dataclass(frozen=True)
class AssetKind:
    """How one catalog kind is exported."""

    name: str
    placement: str = BRAIN
    op: str = COPY

    @property
    def per_runtime(self) -> bool:
        return self.placement == PER_RUNTIME


# The only kinds that need special handling: rendered and/or placed per-runtime.
# Every other name a profile references defaults to a brain copy — so a new
# brain kind (e.g. ``knowledge``) is purely additive, no entry required here.
_OVERRIDES: dict[str, AssetKind] = {
    k.name: k
    for k in (
        AssetKind("agents", PER_RUNTIME, RENDER_AGENT),
        AssetKind("commands", PER_RUNTIME, RENDER_COMMAND),
        AssetKind("skills", PER_RUNTIME, COPY),
    )
}


def kind(name: str) -> AssetKind:
    """Return the AssetKind for *name*, defaulting to a brain copy."""
    return _OVERRIDES.get(name, AssetKind(name))


def target(name: str, runtime: str, rel: str) -> str:
    """Project-relative destination for one asset of *name* under *runtime*.

    Per-runtime kinds land under ``.<runtime>/<kind>/``; brain kinds land once
    under ``.aspis/<kind>/``. Any category sub-path *under* the kind dir is kept,
    so a categorised source like ``templates/planning/SPEC.md`` lands at
    ``.aspis/templates/planning/SPEC.md`` — for a flat source it is just the leaf.
    """
    parts = Path(rel).parts
    sub = Path(*parts[1:]).as_posix() if parts and parts[0] == name else Path(rel).name
    if kind(name).per_runtime:
        prefix = f"{get_adapter(runtime).runtime_dir}/{name}"
    else:
        prefix = f"{BRAIN_DIR}/{name}"
    return f"{prefix}/{sub}"


def op(name: str) -> str:
    """Write op for *name* (``copy`` | ``render-agent`` | ``render-command``)."""
    return kind(name).op


def is_per_runtime(name: str) -> bool:
    """True when *name* is exported once per target runtime."""
    return kind(name).per_runtime
