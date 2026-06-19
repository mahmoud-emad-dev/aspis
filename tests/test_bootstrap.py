"""Tests for the bootstrap operation (wizard defaults, slot fill, manifest, brain fill)."""

from __future__ import annotations

import json

from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def test_bootstrap_fills_slots_and_writes_manifest(tmp_path) -> None:
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    # Non-interactive: --yes + flags drive the values (no prompts).
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="A tiny tool", stack="python")

    data = json.loads((tmp_path / ".aspis" / "manifest.json").read_text(encoding="utf-8"))
    assert data["bootstrapped"] is True
    assert data["goal"] == "A tiny tool"
    assert data["stack"] == "python"

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "A tiny tool" in agents
    assert "filled at bootstrap" not in agents  # both slots replaced

    # The brain fill ran (context files produced by the shipped scripts).
    assert (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").is_file()
    assert (tmp_path / ".aspis" / "context" / "CURRENT_STATE.md").is_file()


def test_bootstrap_writes_project_config_with_mode(tmp_path) -> None:
    from aspis import project

    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, mode="mvp")

    assert (tmp_path / ".aspis" / "config" / "project.yaml").is_file()
    assert project.default_mode(tmp_path) == "mvp"  # the chosen default is readable


def test_bootstrap_makes_init_then_bootstrap_commits(tmp_path) -> None:
    import subprocess

    engine = _engine()
    engine.run("init", tmp_path, write=True)  # git init, scaffolding left uncommitted
    engine.run("bootstrap", tmp_path, write=True, yes=True)

    log = subprocess.run(
        ["git", "-C", str(tmp_path), "log", "--oneline"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "initialize ASPIS project" in log  # 1st commit (auto-committed init)
    assert "bootstrap ASPIS project" in log  # 2nd commit (bootstrap fill)

    data = json.loads((tmp_path / ".aspis" / "manifest.json").read_text(encoding="utf-8"))
    assert "bootstrapped_at" in data  # done stamp recorded


def test_bootstrap_requires_init(tmp_path) -> None:
    import pytest

    with pytest.raises(RuntimeError, match="aspis init"):
        _engine().run("bootstrap", tmp_path, write=True, yes=True)
