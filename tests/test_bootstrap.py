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

    data = json.loads((tmp_path / ".asps" / "manifest.json").read_text(encoding="utf-8"))
    assert data["bootstrapped"] is True
    assert data["goal"] == "A tiny tool"
    assert data["stack"] == "python"

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "A tiny tool" in agents
    assert "filled at bootstrap" not in agents  # both slots replaced

    # The brain fill ran (context files produced by the shipped scripts).
    assert (tmp_path / ".asps" / "index" / "FILE_REGISTRY.yaml").is_file()
    assert (tmp_path / ".asps" / "context" / "CURRENT_STATE.md").is_file()
