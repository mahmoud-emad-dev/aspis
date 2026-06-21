"""``aspis models`` — show, per runtime, how each agent resolves to a model here.

Refreshes the runtime inventory (detection) and prints, per runtime: the tier defaults,
any per-agent override pins (flagging any model that is NOT actually available on that
runtime), and — with ``--available`` — the full menu of models the connected providers
expose, so a user can copy a real model id into ``project.yaml`` for any agent.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import project, resources
from aspis.constants import BRAIN_DIR
from aspis.inventory import build_inventory
from aspis.runtimes import available_runtimes, get_adapter

_TIERS = ("cheap", "standard", "deep")


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``models`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "models", help="Show how each agent resolves to a model per runtime on this machine."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.add_argument(
        "--available",
        action="store_true",
        help="Also list every model the connected providers expose (the menu to pin from).",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Detect runtimes and print tier defaults, override pins (validated), and the menu."""
    root = Path(args.path).resolve()
    # Persist the refreshed inventory only inside a project; elsewhere just detect.
    inventory = build_inventory(root, write=(root / BRAIN_DIR).is_dir())
    configs = (project.load_project_config(root), project.load_global_config())

    for runtime in available_runtimes():
        adapter = get_adapter(runtime)
        inv = inventory.get(runtime)
        tier_map = resources.model_map(runtime)
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
            canonical = tier_map.get(value, value)  # a tier maps through; else it's a model id
            resolved = adapter.model_string(canonical, inv)
            flag = "" if _is_available(resolved, inv) else "   [!] not available on this runtime"
            print(f"  pin {name:<16} {value}  ->  {resolved}{flag}")

        if args.available and inv and inv.models:
            print("  available (copy any into project.yaml):")
            for provider, models in _group_by_provider(inv.models):
                print(f"    {provider}: {', '.join(models)}")
    return 0


def _pins_for(runtime: str, configs: tuple[dict, ...]) -> dict[str, str]:
    """Effective per-agent override pins for *runtime* (runtime-agent beats agent; project wins)."""
    result: dict[str, str] = {}
    for config in reversed(configs):  # global then project, so project wins
        result.update(config.get("agents") or {})
    for config in reversed(configs):  # then the more-specific per-runtime pins
        runtime_block = (config.get("runtimes") or {}).get(runtime) or {}
        result.update(runtime_block.get("agents") or {})
    return result


def _is_available(resolved: str, inv) -> bool:
    """Whether *resolved* is runnable here — true when detection cannot judge (no inventory)."""
    if inv is None or not inv.models:
        return True  # can't detect -> don't cry wolf
    return resolved in inv.models


def _group_by_provider(models: tuple[str, ...]) -> list[tuple[str, list[str]]]:
    """Group ``provider/model`` strings by provider for the available-models menu."""
    groups: dict[str, list[str]] = {}
    for model in models:
        provider, _, rest = model.partition("/")
        groups.setdefault(provider, []).append(rest or model)
    return sorted(groups.items())
