"""Temporary runtime-aware model floor for the leads, seeded at init (F-020).

The agents that drive first-contact quality — project discovery, onboarding,
planning — must not start on a weak free model. Until the full model-decision
engine (F-021) detects each runtime's subscription and picks the best available
model per agent against a quality threshold, ``aspis init`` seeds a small, explicit
*floor*: the lead agents are pinned to a capable model per runtime.

It is written to the project's ``project.yaml`` (the override layer **below**
``agent-models.yaml``) **before** the export renders the agent files, so the floor is
baked into the on-disk agents — in place before the user ever opens the runtime TUI or
runs bootstrap (the timing the owner requires). Writing to ``project.yaml`` (not
``agent-models.yaml``) is deliberate: it introduces no file that would shadow the user's
own ``project.yaml`` routing, and bootstrap's ``aspis models --sync`` (which writes
``agent-models.yaml``) then takes over lead selection with detected, best-available models.

A floor only ever *raises* quality. On OpenCode every tier currently defaults to a free
model, so all leads are floored to a capable paid model. On Claude only ``project-lead``
and ``bootstrap`` are floored (to ``sonnet``) — the other leads run a ``deep`` tier that
already maps to a stronger model, and a floor must never downgrade them. The catalog model
map is never touched (it stays frozen until F-021).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from aspis import project

#: Which leads are floored, per runtime. OpenCode: all leads (free → capable = an upgrade).
#: Claude: only the two the owner named, so a ``deep``-tier lead is never downgraded.
LEADS_BY_RUNTIME: dict[str, tuple[str, ...]] = {
    "opencode": (
        "project-lead",
        "bootstrap",
        "planning-lead",
        "build-lead",
        "research-lead",
        "fix-lead",
        "test-lead",
        "system-lead",
    ),
    "claude": ("project-lead", "bootstrap"),
}

#: Temporary per-runtime floor model. F-021 replaces this with detection-driven,
#: subscription-aware "best available within budget" selection.
FLOOR_MODEL: dict[str, str] = {
    "claude": "claude-sonnet-4-6",
    "opencode": "opencode-go/deepseek-v4-pro",
}


def plan(runtimes: list[str]) -> dict[str, dict[str, str]]:
    """The ``{runtime: {agent: floor-model}}`` pins that apply to the chosen *runtimes*."""
    return {
        runtime: {agent: FLOOR_MODEL[runtime] for agent in LEADS_BY_RUNTIME[runtime]}
        for runtime in runtimes
        if runtime in FLOOR_MODEL
    }


def seed_floor(root: Path, runtimes: list[str], *, write: bool) -> list[str]:
    """Seed the lead model floor into ``project.yaml`` for the chosen *runtimes*.

    Only writes a fresh file: if ``project.yaml`` already exists (a re-init, or the user/
    bootstrap has set the mode/overrides) it is left untouched so we never clobber it.
    Returns log lines.
    """
    floor = plan(runtimes)
    if not floor:
        return []
    path = project.config_path(root)
    if path.is_file():
        return ["model floor: project.yaml exists — left as-is"]

    lines = [f"model floor: {runtime} leads -> {FLOOR_MODEL[runtime]}" for runtime in floor]
    if write:
        data = {"runtimes": {runtime: {"agents": agents} for runtime, agents in floor.items()}}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump(data), encoding="utf-8", newline="\n")
    return lines


def _dump(data: dict) -> str:
    """Serialize the seed file with a short header explaining where it came from."""
    header = (
        "# project.yaml — project defaults (build mode, model overrides).\n"
        "# Seeded by `aspis init` with a temporary lead model floor so project-lead/bootstrap\n"
        "# start on a capable model. (F-021 picks the best model your subscription exposes;\n"
        "# bootstrap's `aspis models --sync` writes agent-models.yaml, which then takes over.)\n"
    )
    return header + yaml.safe_dump(data, sort_keys=True)
