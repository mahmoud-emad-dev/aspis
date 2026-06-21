"""``aspis models`` — show, per runtime, how each tier resolves on this machine.

Refreshes the runtime inventory (detection) and prints, for every registered runtime,
the canonical model each tier maps to and the exact string it renders to here. When a
runtime is detected, that string is a connected-provider/alias form; otherwise it is the
canonical id — so the output makes the routing visible to the user (US1).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import resources
from aspis.constants import BRAIN_DIR
from aspis.inventory import build_inventory
from aspis.runtimes import available_runtimes, get_adapter

_TIERS = ("cheap", "standard", "deep")


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``models`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "models", help="Show how each tier resolves to a model per runtime on this machine."
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Detect runtimes and print each runtime's tier -> canonical -> resolved string."""
    root = Path(args.path).resolve()
    # Persist the refreshed inventory only inside a project; elsewhere just detect.
    inventory = build_inventory(root, write=(root / BRAIN_DIR).is_dir())

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
    return 0
