"""Tests for ASPIS settings (defaults + environment override)."""

from __future__ import annotations

from aspis.runtimes import available_runtimes
from aspis.settings import Settings


def test_defaults() -> None:
    settings = Settings()
    assert settings.brain_dir == ".aspis"


def test_available_runtimes_is_the_single_source() -> None:
    # "Which runtimes exist" comes from adapter discovery, not a settings duplicate.
    assert "opencode" in available_runtimes()


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("ASPIS_BRAIN_DIR", ".brain")
    assert Settings().brain_dir == ".brain"
