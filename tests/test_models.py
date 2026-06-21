"""Tests for data-driven model routing: global map, project override, per-agent pin."""

from __future__ import annotations

import yaml

from aspis import models, resources
from aspis.engine import build_engine
from aspis.operations import register_all

_GLOBAL = {"cheap": "c", "standard": "s", "deep": "d"}


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def _model(text: str) -> str:
    return yaml.safe_load(text.split("---", 2)[1])["model"]


def test_effective_model_resolution_order() -> None:
    # plain tier → global map
    assert (
        models.effective_model("opencode", "x", "deep", global_map=_GLOBAL, project_config={})
        == "d"
    )
    # per-project tier override wins over the global map
    cfg = {"models": {"opencode": {"deep": "D2"}}}
    assert (
        models.effective_model("opencode", "x", "deep", global_map=_GLOBAL, project_config=cfg)
        == "D2"
    )
    # per-agent pin to another tier
    cfg = {"agents": {"reviewer": "cheap"}}
    got = models.effective_model(
        "opencode", "reviewer", "deep", global_map=_GLOBAL, project_config=cfg
    )
    assert got == "c"
    # per-agent pin to a concrete model id (not a tier) passes through
    cfg = {"agents": {"reviewer": "my-model"}}
    got = models.effective_model(
        "opencode", "reviewer", "deep", global_map=_GLOBAL, project_config=cfg
    )
    assert got == "my-model"


def test_model_map_is_data_driven() -> None:
    assert resources.model_map("claude")["deep"] == "claude-opus-4-8"
    assert resources.model_map("opencode")["standard"] == "minimax-m2.7"


def test_project_override_and_pin_apply_on_export(tmp_path) -> None:
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)  # base → opencode, defaults

    build_lead = tmp_path / ".opencode" / "agents" / "build-lead.md"
    assert _model(build_lead.read_text(encoding="utf-8")) == "minimax-m3"  # deep default

    (tmp_path / ".aspis" / "config" / "project.yaml").write_text(
        "mode: production\n"
        "models:\n  opencode:\n    deep: custom-deep\n"
        "agents:\n  reviewer: cheap\n",
        encoding="utf-8",
    )
    engine.run("init", tmp_path, write=True, no_git=True, force=True)  # re-export

    assert _model(build_lead.read_text(encoding="utf-8")) == "custom-deep"  # tier override
    reviewer = tmp_path / ".opencode" / "agents" / "reviewer.md"
    assert _model(reviewer.read_text(encoding="utf-8")) == "deepseek-v4-flash"  # pinned to cheap
