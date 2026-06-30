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
    assert resources.model_map("claude")["deep"] == "claude-opus-4-8"  # claude map is stable
    # The opencode map is user-tuned data; assert it is keyed by tier with catalog ids,
    # not a specific model, so editing models.yaml never breaks this test.
    assert set(resources.model_map("opencode")) == {"cheap", "standard", "deep"}


def test_project_override_and_pin_apply_on_export(tmp_path) -> None:
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)  # base → opencode, defaults

    build_lead = tmp_path / ".opencode" / "agents" / "build-lead.md"
    # Leads are floored to a capable model at init (D-021); build-lead is a lead, so a fresh
    # init renders it at the opencode floor rather than the bare tier default.
    from aspis.operations import model_defaults as md

    assert _model(build_lead.read_text(encoding="utf-8")) == md.FLOOR_MODEL["opencode"]

    (tmp_path / ".aspis" / "config" / "project.yaml").write_text(
        "mode: production\n"
        "models:\n  opencode:\n    deep: custom-deep\n"
        "agents:\n  reviewer: cheap\n",
        encoding="utf-8",
    )
    engine.run("init", tmp_path, write=True, no_git=True, force=True)  # re-export

    assert _model(build_lead.read_text(encoding="utf-8")) == "custom-deep"  # tier override
    reviewer = tmp_path / ".opencode" / "agents" / "reviewer.md"
    # reviewer pinned to the cheap tier → the cheap default (free Zen model), runnable as-is.
    assert _model(reviewer.read_text(encoding="utf-8")) == resources.model_map("opencode")["cheap"]
