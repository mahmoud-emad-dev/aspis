"""Tests for machine-wide path resolution.

Focused on the one contract that must hold on every platform: ``ASPIS_HOME``
overrides everything (the hook tests and relocation rely on it), and the three
locations are always resolved together.
"""

from __future__ import annotations

from aspis import paths


def test_aspis_home_override_wins(tmp_path, monkeypatch) -> None:
    # ASPIS_HOME is checked before the legacy/OS-standard branches, so it wins
    # regardless of what exists on the host — which is what keeps tests stable.
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert paths.config_home() == tmp_path / "config"
    assert paths.data_home() == tmp_path / "data"
    assert paths.cache_home() == tmp_path / "cache"


def test_all_locations_resolves_the_three(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert set(paths.all_locations()) == {"config", "data", "cache"}
