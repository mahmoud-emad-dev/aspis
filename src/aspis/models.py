"""Model routing — resolve an agent's model from its tier, with overrides.

Agents declare a *tier* (cheap/standard/deep). The global tier->model map lives in
``catalog/config/models.yaml`` (data, per runtime) and now points at **canonical**
model ids (F-010). A project can override that map or pin an agent in
``.aspis/config/project.yaml``; a machine-wide ``~/.aspis/config`` sits one rung below
the project. Full resolution order (high -> low):

  per-(runtime, agent) pin  >  per-agent pin  >  project/global tier override  >  tier map

The per-(runtime, agent) pin (``runtimes.<runtime>.agents.<name>``) is what makes the
system fully flexible: the *same* agent can use a different model on each runtime — e.g.
``build-lead`` on ``sonnet`` under Claude but ``deepseek-v4-pro`` under OpenCode — and any
agent can be pinned to any model (a tier or a concrete id) without touching code.

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

# Task-packet granularity, smallest (finest, most rigor) to largest (coarsest).
_TASK_SIZES = ("small", "medium", "large")
# How a model's cost tier shifts the mode's base task size: a weaker (cheaper) model
# gets finer tasks to compensate; a frontier model can take coarser ones (FR-008).
_CAPABILITY_SHIFT = {"cheap": -1, "standard": 0, "deep": 1, "frontier": 1}


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
    """Merge the tier map with each config's per-runtime tier override (earlier configs win).

    A config may override a tier two ways: the flat ``models.<runtime>.<tier>`` or, under
    the unified ``runtimes.<runtime>.models.<tier>`` block. Both feed the same table.
    """
    table = dict(global_map)
    for config in reversed(configs):  # apply low->high priority so earlier configs win
        table.update((config.get("models") or {}).get(runtime) or {})
        runtime_block = (config.get("runtimes") or {}).get(runtime) or {}
        table.update(runtime_block.get("models") or {})
    return table


def _agent_pin(runtime: str, agent_name: str, configs: tuple[dict, ...]) -> str | None:
    """The most specific override for *agent_name* on *runtime* — tier or concrete model id.

    Precedence, highest first: a per-(runtime, agent) pin
    (``runtimes.<runtime>.agents.<name>``) beats a per-agent pin that applies to every
    runtime (``agents.<name>``); within each, an earlier config (project) beats a later
    one (global). This is what lets one agent use a different model per runtime — e.g.
    ``sonnet`` on Claude but ``deepseek-v4-pro`` on OpenCode.
    """
    for config in configs:  # per-(runtime, agent) — the most specific
        runtime_block = (config.get("runtimes") or {}).get(runtime) or {}
        pin = (runtime_block.get("agents") or {}).get(agent_name)
        if pin:
            return pin
    for config in configs:  # per-agent across all runtimes
        pin = (config.get("agents") or {}).get(agent_name)
        if pin:
            return pin
    return None


def _canonical_id(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    configs: tuple[dict, ...],
) -> str:
    """Apply the full precedence (per-runtime-agent / agent pin > tier override > tier map)."""
    pin = _agent_pin(runtime, agent_name, configs)
    if pin:
        tier = pin  # a tier name maps through the table; a model id passes through
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


# Cost ordering and how a tier (the agent's budget) caps the models it may pick from.
_COST_RANK = {"cheap": 0, "standard": 1, "deep": 2, "frontier": 3}
_TIER_MAX_COST = {"cheap": "cheap", "standard": "standard", "deep": "frontier"}


def _price(model: dict) -> tuple[float, float, int]:
    """Cost sort key (input $/Mtok, output $/Mtok, cost-tier rank); cheaper sorts first."""
    pricing = model.get("pricing") or {}
    return (
        pricing.get("in", 999.0),
        pricing.get("out", 999.0),
        _COST_RANK.get(model.get("cost_tier"), 3),
    )


def best_available_model(
    dimension: str,
    budget_tier: str,
    *,
    catalog: dict,
    available_ids: list[str],
    tolerance: int = 1,
) -> str | None:
    """Pick the *cheapest* available model that is near-best at *dimension* within the budget.

    Capability-based and cost-conscious: among the runnable models within the agent's cost
    budget, take those scoring within *tolerance* of the best score for the capability, then
    choose the cheapest. So a reviewer gets a strong *reviewer* and a builder a strong
    *implementer*, but a budget plan lands on its affordable workhorse (e.g. deepseek-v4-pro)
    rather than an expensive frontier model that happens to also be connected. Falls back to
    ignoring the budget when nothing fits it; ``None`` only when nothing is known.
    """
    max_cost = _COST_RANK.get(_TIER_MAX_COST.get(budget_tier, "frontier"), 3)
    known = [(mid, catalog[mid]) for mid in available_ids if mid in catalog]
    pool = [(mid, m) for mid, m in known if _COST_RANK.get(m.get("cost_tier"), 3) <= max_cost]
    pool = pool or known
    if not pool:
        return None

    def _score(model: dict) -> int:
        return (model.get("scores") or {}).get(dimension, 0)

    best = max(_score(m) for _, m in pool)
    near_best = [(mid, m) for mid, m in pool if _score(m) >= best - tolerance]
    return min(near_best, key=lambda pair: _price(pair[1]))[0]


def effective_task_size(
    mode: str,
    canonical_id: str,
    *,
    catalog: dict | None = None,
    modes: dict | None = None,
) -> str:
    """Combine a mode's base ``task_size`` with the model's capability (FR-008).

    The mode sets the baseline granularity (``modes.yaml``); the model's cost tier
    shifts it — a weaker model gets finer tasks to compensate, a frontier model can
    take coarser ones. Returns one of ``small``/``medium``/``large``. Unknown mode or
    model falls back to the mode's base size (or ``medium``), never raising.
    """
    from aspis import resources

    modes = modes if modes is not None else resources.config("modes.yaml").get("modes", {})
    catalog = (
        catalog if catalog is not None else resources.config("model_catalog.yaml").get("models", {})
    )

    base = (modes.get(mode) or {}).get("task_size", "medium")
    base_index = _TASK_SIZES.index(base) if base in _TASK_SIZES else 1
    cost_tier = (catalog.get(canonical_id) or {}).get("cost_tier")
    shifted = base_index + _CAPABILITY_SHIFT.get(cost_tier, 0)
    shifted = max(0, min(len(_TASK_SIZES) - 1, shifted))
    return _TASK_SIZES[shifted]
