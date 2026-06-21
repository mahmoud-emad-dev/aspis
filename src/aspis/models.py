"""Model routing — resolve an agent's model from its tier, with overrides.

Agents declare a *tier* (cheap/standard/deep). The global tier->model map lives in
``catalog/config/models.yaml`` (data, per runtime) and now points at **canonical**
model ids (F-010). A project can override that map or pin an individual agent in
``.aspis/config/project.yaml``; a machine-wide ``~/.aspis/config`` sits one rung below
the project. Full resolution order (high -> low):

  per-agent pin  >  project tier override  >  global ``~/.aspis`` override  >  tier map

``effective_model`` keeps the original two-layer behaviour (its callers and tests are
unchanged). ``resolve`` adds the F-010 layers on top: the global config rung, hard-limit
enforcement (FR-007), and translation of the canonical id into the runtime's exact string
via the adapter + detected inventory — falling back to the canonical id (today's output)
when nothing is detected, so it works for any user.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # annotation only — avoids a runtimes->models->runtimes import cycle
    from aspis.runtimes.base import RuntimeInventory

# Ordered task-complexity ceilings; a model may take any task at or below its ceiling.
_COMPLEXITY = {"low": 0, "medium": 1, "high": 2}
# Tiers from cheapest to deepest — the order limit-escalation walks to find the
# cheapest model that still clears a task's required ceiling.
_TIERS = ("cheap", "standard", "deep")


def effective_model(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    project_config: dict,
) -> str:
    """Resolve the concrete model id for *agent_name* on *runtime* (pin > project > map)."""
    pin = (project_config.get("agents") or {}).get(agent_name)
    if pin:
        tier = pin  # may be a tier name or a concrete model id
    overrides = (project_config.get("models") or {}).get(runtime) or {}
    table = {**global_map, **overrides}
    # A known tier maps through the table; anything else is already a model id.
    return table[tier] if tier in table else tier


def _resolved_table(runtime: str, global_map: dict[str, str], *configs: dict) -> dict[str, str]:
    """Merge the tier map with each config's per-runtime override (later configs lose)."""
    table = dict(global_map)
    for config in reversed(configs):  # apply low->high priority so earlier configs win
        table.update((config.get("models") or {}).get(runtime) or {})
    return table


def _canonical_id(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    configs: tuple[dict, ...],
) -> str:
    """Apply the full precedence (pin > each config tier override > tier map) to a canonical id."""
    for config in configs:  # configs are highest-priority first (project, then global)
        pin = (config.get("agents") or {}).get(agent_name)
        if pin:
            tier = pin
            break
    table = _resolved_table(runtime, global_map, *configs)
    return table[tier] if tier in table else tier


def within_limits(canonical_id: str, required: str, catalog: dict) -> bool:
    """Whether *canonical_id* may take a task of *required* complexity (unknown -> allowed)."""
    model = catalog.get(canonical_id)
    if not model:
        return True  # not in the catalog -> don't block routing (graceful)
    ceiling = (model.get("limits") or {}).get("max_task_complexity") or "high"
    return _COMPLEXITY.get(ceiling, 2) >= _COMPLEXITY.get(required, 0)


def _enforce_limits(canonical_id: str, required: str, table: dict[str, str], catalog: dict) -> str:
    """Bump to the cheapest tier whose model clears *required*; keep current if none do."""
    if within_limits(canonical_id, required, catalog):
        return canonical_id
    for tier in _TIERS:
        candidate = table.get(tier)
        if candidate and within_limits(candidate, required, catalog):
            return candidate
    return canonical_id  # nothing clears the bar -> best effort, caller may warn


def resolve(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    project_config: dict | None = None,
    global_config: dict | None = None,
    translate: Callable[[str, RuntimeInventory | None], str] | None = None,
    inventory: RuntimeInventory | None = None,
    catalog: dict | None = None,
    required_complexity: str | None = None,
) -> str:
    """Resolve an agent's model to the runtime string it should render with.

    Precedence (high->low): per-agent pin, project override, global ``~/.aspis`` override,
    tier map. The resulting canonical id is bounded by hard limits when a *catalog* and a
    *required_complexity* are supplied (FR-007), then translated into the runtime's exact
    string via *translate* against the detected *inventory*. With no translate/inventory it
    returns the canonical id — exactly today's output — so detection is optional (FR-006/FR-009).
    """
    configs = tuple(c for c in (project_config, global_config) if c)
    canonical = _canonical_id(runtime, agent_name, tier, global_map=global_map, configs=configs)
    if catalog and required_complexity:
        table = _resolved_table(runtime, global_map, *configs)
        canonical = _enforce_limits(canonical, required_complexity, table, catalog)
    if translate is None:
        return canonical
    return translate(canonical, inventory)
