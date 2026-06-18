"""Tests for the data-driven profile model, loader, and base merge."""

from __future__ import annotations

from aspis.profiles import Profile, load_profile, merge


def test_assets_returns_kind_path_pairs() -> None:
    profile = Profile(name="x", agents=["agents/lead.md"], skills=["skills/scope"])
    assets = profile.assets()
    assert ("agents", "agents/lead.md") in assets
    assert ("skills", "skills/scope") in assets


def test_load_profile(tmp_path) -> None:
    path = tmp_path / "p.yaml"
    path.write_text("name: x\nagents: [a.md]\n", encoding="utf-8")
    profile = load_profile(path)
    assert profile.name == "x"
    assert profile.agents == ["a.md"]


def test_merge_concatenates_and_dedupes() -> None:
    base = Profile(name="base", agents=["agents/lead.md"], skills=["skills/scope"])
    overlay = Profile(name="py", runtimes=["opencode", "claude"], agents=["agents/py.md"])
    result = merge(base, overlay)
    assert result.name == "py"
    assert result.runtimes == ["opencode", "claude"]
    assert result.agents == ["agents/lead.md", "agents/py.md"]
    assert result.skills == ["skills/scope"]
