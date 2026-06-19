"""Model routing — resolve an agent's model from its tier, with overrides.

Agents declare a *tier* (cheap/standard/deep). The global tier->model map lives in
``catalog/config/models.yaml`` (data, per runtime). A project can override that map
or pin an individual agent in ``.aspis/config/project.yaml``. Resolution order:

  per-agent pin  >  per-project tier override  >  global tier map

A pin (or any value) that is not a known tier is treated as a concrete model id and
returned unchanged, so a project can pin an agent straight to a specific model.
"""

from __future__ import annotations


def effective_model(
    runtime: str,
    agent_name: str,
    tier: str,
    *,
    global_map: dict[str, str],
    project_config: dict,
) -> str:
    """Resolve the concrete model id for *agent_name* on *runtime*."""
    pin = (project_config.get("agents") or {}).get(agent_name)
    if pin:
        tier = pin  # may be a tier name or a concrete model id
    overrides = (project_config.get("models") or {}).get(runtime) or {}
    table = {**global_map, **overrides}
    # A known tier maps through the table; anything else is already a model id.
    return table[tier] if tier in table else tier
