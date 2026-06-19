"""Tests for project default-mode settings and the ``aspis mode`` verb."""

from __future__ import annotations

from aspis import project
from aspis.cli import main


def _init(tmp_path):
    from aspis.engine import build_engine
    from aspis.operations import register_all

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True, no_git=True)


def test_default_mode_falls_back_then_persists(tmp_path) -> None:
    _init(tmp_path)
    assert project.default_mode(tmp_path) == "production"  # fallback when unset

    project.set_mode(tmp_path, "vibe")
    assert project.default_mode(tmp_path) == "vibe"  # persisted and read back


def test_mode_cli_shows_and_sets(tmp_path, capsys) -> None:
    _init(tmp_path)

    assert main(["mode", "mvp", "--path", str(tmp_path)]) == 0
    assert "→ mvp" in capsys.readouterr().out
    assert project.default_mode(tmp_path) == "mvp"

    assert main(["mode", "--path", str(tmp_path)]) == 0
    assert "mvp" in capsys.readouterr().out  # shows the current default
