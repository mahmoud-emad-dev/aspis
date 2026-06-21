"""Model routing — resolve an agent's model from its tier, with overrides.

Agents declare a *tier* (cheap/standard/deep). The global tier->model map lives in
``catalog/config/models.yaml`` (data, per runtime) and now points at **canonical**
model ids (F-010). A project can override that map or pin an agent in
``.aspis/config/project.yaml``; a machine-wide ``~/.aspis/config`` sits one rung below
the project. Full resolution order (high -> low):

  per-(runtime, agent) pin  >  per-agent pin  >  per-(runtime, capability)  >
  per-capability  >  project/global tier override  >  tier map

The per-(runtime, agent) pin (``runtimes.<runtime>.agents.<name>``) is what makes the
system fully flexible: the *same* agent can use a different model on each runtime — e.g.
``build-lead`` on ``sonnet`` under Claude but ``deepseek-v4-pro`` under OpenCode. The
``by_capability`` rung is the scalable layer: set a model once per kind of work (review,
implementation, …) and every agent of that capability inherits it.

``effective_model`` keeps the original two-layer behaviour (its callers and tests are
unchanged). ``resolve`` adds the F-010 layers on top and translates the canonical id into
the runtime's exact string via the adapter + detected inventory — falling back to the
canonical id (today's output) when nothing is detected, so it works for any user. Hard
limits + task sizing are a run-time/dispatch concern, not render (deferred — see D-017).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # annotation only — avoids a runtimes->models->runtimes import cycle
    from aspis.runtimes.base import RuntimeInventory


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


def _agent_pin(
    runtime: str, agent_name: str, capability: str | None, configs: tuple[dict, ...]
) -> str | None:
    """The most specific override for *agent_name* on *runtime* — tier or concrete model id.

    Precedence, highest first, project config before global within each rung:
      1. per-(runtime, agent)   ``runtimes.<rt>.agents.<name>``
      2. per-agent (all rt)     ``agents.<name>``
      3. per-(runtime, capability) ``runtimes.<rt>.by_capability.<cap>``
      4. per-capability (all rt)   ``by_capability.<cap>``
    The capability rungs are the scalable middle layer: set a model once per kind of work
    (review/implementation/…) and every agent of that capability inherits it, so a 50-agent
    roster is configured by ~10 lines, not 50. The per-(runtime, agent) rung still lets one
    agent differ per runtime (``sonnet`` on Claude, ``deepseek-v4-pro`` on OpenCode).
    """
    lookups = (
        lambda c: (c.get("runtimes", {}).get(runtime, {}).get("agents") or {}).get(agent_name),
        lambda c: (c.get("agents") or {}).get(agent_name),
    )
    if capability:
        lookups += (
            lambda c: (c.get("runtimes", {}).get(runtime, {}).get("by_capability") or {}).get(
                capability
            ),
            lambda c: (c.get("by_capability") or {}).get(capability),
        )
    for lookup in lookups:
        for config in configs:  # project before global
            value = lookup(config)
            if value:
                return value
    return None


def _canonical_id(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    configs: tuple[dict, ...],
    capability: str | None = None,
) -> str:
    """Apply the full precedence (agent pin > capability override > tier override > tier map)."""
    pin = _agent_pin(runtime, agent_name, capability, configs)
    if pin:
        tier = pin  # a tier name maps through the table; a model id passes through
    table = _resolved_table(runtime, global_map, *configs)
    return table[tier] if tier in table else tier


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
    agent_capability: str | None = None,
) -> str:
    """Resolve an agent's model to the runtime string it should render with.

    Precedence (high->low): per-(runtime,agent) pin, per-agent pin, per-(runtime,capability)
    override, per-capability override, tier map. The resolved canonical id is translated into
    the runtime's exact string via *translate* against the detected *inventory*. With no
    translate/inventory it returns the canonical id — exactly today's output — so detection is
    optional (FR-006/FR-009). Hard limits and task sizing are NOT applied here: render does not
    know the task, so those are a run-time/dispatch concern (deferred — see D-017).
    """
    configs = tuple(c for c in (project_config, global_config) if c)
    canonical = _canonical_id(
        runtime,
        agent_name,
        tier,
        global_map=global_map,
        configs=configs,
        capability=agent_capability,
    )
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


def affordable(available_ids: list[str], budget_tier: str, catalog: dict) -> list[str]:
    """Known model ids within *budget_tier*'s cost cap (all known, if none qualify)."""
    cap = _COST_RANK.get(_TIER_MAX_COST.get(budget_tier, "frontier"), 3)
    known = [mid for mid in available_ids if mid in catalog]
    within = [mid for mid in known if _COST_RANK.get(catalog[mid].get("cost_tier"), 3) <= cap]
    return within or known


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
