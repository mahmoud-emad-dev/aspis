"""Tests for package-data resolution: the config tier search and project-first override.

Small and behaviour-focused — these pin the two non-obvious contracts of
``resources``: a config file resolves by *bare* name regardless of which tier
folder it sits in, and a project's own copy wins over the bundled package data.
"""

from __future__ import annotations

from aspis import resources


def test_config_resolves_bundled_by_bare_name() -> None:
    # modes.yaml lives under config/policy/, but callers never spell the tier.
    assert "modes" in resources.config("modes.yaml")


def test_project_config_overrides_bundled(tmp_path) -> None:
    local = tmp_path / ".aspis" / "config" / "policy"
    local.mkdir(parents=True)
    (local / "modes.yaml").write_text("modes: {solo: {}}\n", encoding="utf-8")

    # The project's own copy wins over the bundled default.
    assert resources.config("modes.yaml", tmp_path) == {"modes": {"solo": {}}}


def test_runtime_defs_are_discovered_not_hardcoded() -> None:
    # Runtimes come from data/runtimes/*.yaml (Discovery over Registration).
    assert {"opencode", "claude"} <= set(resources.runtime_defs())
