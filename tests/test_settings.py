"""Tests for ASPIS settings (defaults + environment override)."""

from __future__ import annotations

from aspis.settings import Settings


def test_defaults() -> None:
    settings = Settings()
    assert settings.brain_dir == ".aspis"
    assert "opencode" in settings.runtimes


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("ASPIS_BRAIN_DIR", ".brain")
    assert Settings().brain_dir == ".brain"
