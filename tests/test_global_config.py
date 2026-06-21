"""Tests for F-010 T-12: the machine-wide ~/.aspis override layer (US4 / FR-005).

The global config sits below project config and above the catalog tier map. It is read
from ``~/.aspis/config/project.yaml`` (relocatable via ``ASPIS_HOME`` for tests).
"""

from __future__ import annotations

import yaml

from aspis import project, resources
from aspis.transform import render_agent

_DEEP_AGENT = """---
name: build-lead
description: The build orchestrator.
mode: subagent
model: deep
tools: [read, edit]
---

You orchestrate the build.
"""


def _model(rendered: str) -> str:
    return yaml.safe_load(rendered.split("---", 2)[1])["model"]


def _write_global(tmp_path, body: str, monkeypatch) -> None:
    cfg = tmp_path / "config" / "project.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(body, encoding="utf-8")
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))


def test_load_global_config_honours_aspis_home(monkeypatch, tmp_path) -> None:
    _write_global(tmp_path, "models:\n  opencode:\n    deep: glob-deep\n", monkeypatch)
    assert project.load_global_config()["models"]["opencode"]["deep"] == "glob-deep"


def test_global_override_applies_when_no_project_override(monkeypatch, tmp_path) -> None:
    _write_global(tmp_path, "models:\n  opencode:\n    deep: glob-deep\n", monkeypatch)
    assert _model(render_agent(_DEEP_AGENT, "opencode")) == "glob-deep"


def test_project_override_beats_global(monkeypatch, tmp_path) -> None:
    _write_global(tmp_path, "models:\n  opencode:\n    deep: glob-deep\n", monkeypatch)
    project_config = {"models": {"opencode": {"deep": "proj-deep"}}}
    out = _model(render_agent(_DEEP_AGENT, "opencode", project_config=project_config))
    assert out == "proj-deep"


def test_no_global_config_is_canonical(monkeypatch, tmp_path) -> None:
    # ASPIS_HOME pointing at an empty dir -> no override -> the tier-map canonical id.
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert _model(render_agent(_DEEP_AGENT, "opencode")) == resources.model_map("opencode")["deep"]
