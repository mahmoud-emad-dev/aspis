"""``aspis models`` — see and assign the models each agent uses, per runtime.

- ``aspis models``              show each runtime's tier defaults + override pins (validated).
- ``aspis models --available``  also list every model the connected providers expose.
- ``aspis models --sync``       (re)generate ``.aspis/config/agent-models.yaml`` — the one
  editable file with the available models ranked per capability and every agent pre-assigned
  the best available model for its job. Open it, change any agent to any available model.

Everything is built from real detection (``opencode auth list`` + ``opencode models`` /
``~/.claude``), so only models your plan/subscription actually provides are ever shown.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from aspis import models as routing
from aspis import project, resources
from aspis.constants import BRAIN_DIR
from aspis.inventory import build_inventory, save_sync_snapshot
from aspis.runtimes import available_runtimes, get_adapter

_TIERS = ("cheap", "standard", "deep")
# Catalog score dimensions, with the agent role each ranks — shown in the menu.
_DIMENSIONS = (
    ("planning", "planning (planners)"),
    ("implementation", "implementation (builders)"),
    ("review", "review (reviewers)"),
    ("reasoning", "reasoning (research/fix)"),
)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``models`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "models", help="Show or assign the model each agent uses, per runtime, on this machine."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.add_argument(
        "--available",
        action="store_true",
        help="Also list every model the connected providers expose.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="(Re)generate .aspis/config/agent-models.yaml — the editable per-agent model file.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Re-render the live runtime agents from agent-models.yaml + project.yaml "
        "(makes your edits active). Combine with --sync to refresh then apply.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --apply: overwrite all agents, ignoring protection (escape hatch).",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    inventory = build_inventory(root, write=(root / BRAIN_DIR).is_dir())
    if args.sync:
        rc = _sync(root, inventory)
        if rc or not args.apply:
            return rc
    if args.apply:
        return _apply(root, force=bool(args.force))
    return _show(root, inventory, available=args.available)


# --- aspis models / --available ----------------------------------------------


def _show(root: Path, inventory: dict, *, available: bool) -> int:
    """Print tier defaults, the effective per-agent pins (validated), and (opt) the menu."""
    configs = (project.load_effective_config(root), project.load_global_config())
    for runtime in available_runtimes():
        adapter = get_adapter(runtime)
        inv = inventory.get(runtime)
        tier_map = resources.model_map(runtime, root)
        detail = f"detected: {', '.join(inv.providers)}" if inv else "not detected"
        print(f"{runtime}  ({detail})")

        for tier in _TIERS:
            canonical = tier_map.get(tier)
            if not canonical:
                continue
            resolved = adapter.model_string(canonical, inv)
            arrow = f"  ->  {resolved}" if resolved != canonical else ""
            print(f"  {tier:<9} {canonical}{arrow}")

        for name, value in sorted(_pins_for(runtime, configs).items()):
            canonical = tier_map.get(value, value)
            resolved = adapter.model_string(canonical, inv)
            flag = "" if _is_available(resolved, inv) else "   [!] not available on this runtime"
            print(f"  pin {name:<16} {value}  ->  {resolved}{flag}")

        if available and inv and inv.models:
            print("  available (copy any into agent-models.yaml):")
            for provider, group in _group_by_provider(inv.models):
                print(f"    {provider}: {', '.join(group)}")
    return 0


# --- aspis models --sync -----------------------------------------------------


def _sync(root: Path, inventory: dict) -> int:
    """Generate the editable agent-models.yaml: per-capability menu + best-fit assignments."""
    catalog = resources.config("model_catalog.yaml", root).get("models", {})
    capabilities = resources.config("capabilities.yaml", root).get("capabilities", {})
    agent_caps = resources.config("agent-capabilities.yaml", root).get("agents", {})
    agent_tiers = _catalog_agent_tiers()
    existing = project.load_agent_models(root).get("runtimes") or {}

    out: list[str] = [
        "# agent-models.yaml — assign a model to each agent, per runtime. EDIT FREELY.",
        "# Generated by `aspis models --sync` from the models your connected runtimes expose;",
        "# re-run after connecting a new plan/provider to refresh. Each agent is pre-set to the",
        "# best AVAILABLE model for its capability within its cost budget — change any to another",
        "# model from the ranked menu below, or to a tier (cheap/standard/deep). Scores are seeds,",
        "# refined later by tracing.",
        "#",
        "# AFTER EDITING, run `aspis models --apply` to re-render the live agents with your",
        "# choices (the model is baked into each agent file, so edits here are inert until then).",
        "#",
        "# ---- AVAILABLE MODELS, ranked per capability (score 1-10, best first) ----",
    ]
    runtime_ids: dict[str, list[str]] = {}
    for runtime in available_runtimes():
        adapter = get_adapter(runtime)
        inv = inventory.get(runtime)
        ids = _available_catalog_ids(runtime, catalog, inv, adapter)
        runtime_ids[runtime] = ids
        det = f"detected: {', '.join(inv.providers)}" if inv else "not detected — showing all known"
        out.append("#")
        out.append(f"# {runtime}  ({det}):")
        if not ids:
            out.append("#   (no known models)")
            continue
        for dimension, label in _DIMENSIONS:
            ranked = _rank(dimension, ids, catalog)
            shown = " > ".join(f"{mid}({score})" for score, mid in ranked[:12])
            out.append(f"#   {label:<26}: {shown}")

    used_capabilities = sorted(set(agent_caps.values()))
    out += [
        "",
        "# Set a model per CAPABILITY — covers every agent of that kind, so a roster of any",
        "# size is configured by a handful of lines. Pre-filled with the best-value available",
        "# model; change any. The per-agent section below overrides this for individual agents.",
        "runtimes:",
    ]
    for runtime in available_runtimes():
        ids = runtime_ids[runtime]
        existing_runtime = existing.get(runtime) or {}
        out.append(f"  {runtime}:")
        out.append("    by_capability:")
        existing_caps = existing_runtime.get("by_capability") or {}
        for capability in used_capabilities:
            spec = capabilities.get(capability) or {}
            dimension = spec.get("scored_by", "implementation")
            budget = spec.get("preferred_tier", "standard")
            value = existing_caps.get(capability) or (
                routing.best_available_model(dimension, budget, catalog=catalog, available_ids=ids)
                or budget
            )
            ranked = _rank(dimension, routing.affordable(ids, budget, catalog), catalog)[:3]
            hint = " > ".join(f"{mid}({score})" for score, mid in ranked) or "(none)"
            out.append(_yaml_line(f"      {capability}: {value}", f"options: {hint}"))
        out.append("    # Override a single agent here (uncomment a line):")
        out.append("    agents:")
        existing_agents = existing_runtime.get("agents") or {}
        for agent, tier in agent_tiers.items():
            capability = agent_caps.get(agent, "implementation")
            if agent in existing_agents:  # a real, active override the user added
                out.append(_yaml_line(f"      {agent}: {existing_agents[agent]}", capability))
            else:
                dimension = (capabilities.get(capability) or {}).get("scored_by", "implementation")
                best = routing.best_available_model(
                    dimension, tier, catalog=catalog, available_ids=ids
                )
                out.append(_yaml_line(f"      # {agent}: {best or tier}", capability))

    path = root / project.AGENT_MODELS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    # Record what we synced against so `aspis doctor` can flag when the connected plans change.
    save_sync_snapshot(root, inventory)
    print(f"wrote {path.relative_to(root)} — open it to assign a model to each agent.")
    return 0


# --- aspis models --apply ----------------------------------------------------


def _apply(root: Path, *, force: bool = False) -> int:
    """Re-render live runtime agents so edits to agent-models.yaml/project.yaml take effect.

    The model is baked into each runtime agent file at export time; ``--sync`` only refreshes
    the editable ``agent-models.yaml``. This re-runs the same render path over the agents
    that are *already live* -- so a model change becomes active without a re-init.
    Only existing agent files are touched: self-cleaned transient agents are not resurrected,
    and skills/scripts/root files (e.g. a bootstrap-stripped AGENTS.md) are left untouched.

    By default (``--apply`` without ``--force``) the hash-protection engine decides per
    agent: pristine agents whose model routing changed are UPDATEd, user-edited agents are
    PROTECTed (skipped), and agents changed by both sides are CONFLICTed (skipped, reported).
    ``--force`` bypasses protection and overwrites every live agent (the legacy behavior).
    """
    from aspis.export import ExportPlan, plan_export, write_export
    from aspis.profiles import load_merged

    if not (root / BRAIN_DIR).is_dir():
        print("not an ASPIS project (no .aspis/) -- run `aspis init` first.")
        return 1

    profile = load_merged("base", resources.data_dir() / "profiles")
    present = [r for r in profile.runtimes if (root / get_adapter(r).runtime_dir).is_dir()]
    if present:
        profile = profile.model_copy(update={"runtimes": present})

    plan = plan_export(resources.catalog_dir(), profile)
    live = [
        action
        for action in plan.actions
        if action.op == "render-agent" and (root / action.target).exists()
    ]
    if not live:
        print("no live runtime agents to apply to -- run `aspis init` first.")
        return 1

    performed = write_export(
        ExportPlan(actions=live, catalog_root=None), root,
        force=force, apply=not force, write=True,
        # This command exists to (re-)bake models, so it must NOT preserve the live
        # model line — unlike `aspis export`, which keeps frozen models intact.
        preserve_models=False,
    )
    runtimes = ", ".join(sorted({a.runtime for a in live}))
    _skip_kinds = {"ADD", "UNCHANGED", "UNKNOWN", "UPDATE", "PROTECT", "CONFLICT"}
    skipped = [p for p in performed if p.split(":")[0].strip() in _skip_kinds]
    written_count = len(performed) - len(skipped)
    print(f"applied: {written_count} re-rendered, {len(skipped)} skipped ({runtimes}).")
    for s in skipped:
        print(f"  {s}")
    return 0


# --- helpers -----------------------------------------------------------------


def _pins_for(runtime: str, configs: tuple[dict, ...]) -> dict[str, str]:
    """Effective per-agent override pins for *runtime* (runtime-agent beats agent; project wins)."""
    result: dict[str, str] = {}
    for config in reversed(configs):
        result.update(config.get("agents") or {})
    for config in reversed(configs):
        runtime_block = (config.get("runtimes") or {}).get(runtime) or {}
        result.update(runtime_block.get("agents") or {})
    return result


def _is_available(resolved: str, inv) -> bool:
    """Whether *resolved* is runnable here — true when detection cannot judge."""
    if inv is None or not inv.models:
        return True
    return resolved in inv.models


def _group_by_provider(models: tuple[str, ...]) -> list[tuple[str, list[str]]]:
    """Group ``provider/model`` strings by provider for the available-models menu."""
    groups: dict[str, list[str]] = {}
    for model in models:
        provider, _, rest = model.partition("/")
        groups.setdefault(provider, []).append(rest or model)
    return sorted(groups.items())


def _available_catalog_ids(runtime: str, catalog: dict, inv, adapter) -> list[str]:
    """Catalog model ids actually runnable on *runtime* (all known, if detection is blind)."""
    if inv and inv.models:
        return [mid for mid in catalog if adapter.model_string(mid, inv) in inv.models]
    return list(catalog)


def _yaml_line(text: str, comment: str) -> str:
    """A YAML line with its inline comment, padded so there is always a space before ``#``."""
    pad = " " * max(1, 44 - len(text))
    return f"{text}{pad}# {comment}".rstrip()


def _rank(dimension: str, ids: list[str], catalog: dict) -> list[tuple[int, str]]:
    """Available model ids ranked by their *dimension* score, best first."""
    scored = [((catalog[mid].get("scores") or {}).get(dimension, 0), mid) for mid in ids]
    return sorted(scored, key=lambda pair: (-pair[0], pair[1]))


def _catalog_agent_tiers() -> dict[str, str]:
    """Each catalog agent's declared tier (its cost budget), by agent name."""
    tiers: dict[str, str] = {}
    for path in sorted((resources.catalog_dir() / "agents").glob("*.md")):
        frontmatter = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1]) or {}
        tiers[path.stem] = frontmatter.get("model", "standard")
    return tiers
