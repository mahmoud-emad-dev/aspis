"""Catalog consistency guard — the machine-checked 'nothing is missing' rule.

Every asset a profile selects must exist; every skill and delegate an agent
references must ship in that profile; every command must bind to a shipped agent.
This turns the consistency rule from a prose promise into a failing test.
"""

from __future__ import annotations

from pathlib import Path

from aspis import resources
from aspis.catalog import parse_agent, parse_command
from aspis.profiles import load_profile, merge


def _profiles():
    """Return ``(name, resolved_profile)`` for every profile, merged under base."""
    profiles_dir = resources.data_dir() / "profiles"
    base = load_profile(profiles_dir / "base.yaml")
    resolved = [("base", base)]
    for path in sorted(profiles_dir.glob("*.yaml")):
        if path.stem != "base":
            resolved.append((path.stem, merge(base, load_profile(path))))
    return resolved


def test_every_selected_asset_exists() -> None:
    catalog = resources.catalog_dir()
    for name, profile in _profiles():
        for kind, rel in profile.assets():
            assert (catalog / rel).exists(), f"profile {name!r} selects missing {kind}: {rel}"


def test_agent_skills_and_delegates_are_shipped() -> None:
    catalog = resources.catalog_dir()
    for name, profile in _profiles():
        shipped_skills = {Path(s).name for s in profile.skills}
        shipped_agents = {Path(a).stem for a in profile.agents}
        for rel in profile.agents:
            agent = parse_agent((catalog / rel).read_text(encoding="utf-8"))
            for skill in agent.skills:
                assert skill in shipped_skills, f"{agent.name}: skill {skill!r} not in {name!r}"
            for delegate in agent.delegates:
                assert delegate in shipped_agents, (
                    f"{agent.name}: delegate {delegate!r} not in {name!r}"
                )


def test_commands_bind_to_a_shipped_agent() -> None:
    catalog = resources.catalog_dir()
    for name, profile in _profiles():
        shipped_agents = {Path(a).stem for a in profile.agents}
        for rel in profile.commands:
            command = parse_command((catalog / rel).read_text(encoding="utf-8"))
            if command.agent:
                assert command.agent in shipped_agents, (
                    f"command {command.name!r} binds {command.agent!r} not in {name!r}"
                )
