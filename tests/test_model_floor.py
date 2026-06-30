"""F-020 — runtime-aware lead model floor seeded at init (before bootstrap)."""

from __future__ import annotations

import yaml

from aspis import project
from aspis.cli import main
from aspis.operations import model_defaults as md


def test_plan_floors_leads_per_runtime() -> None:
    opencode = md.plan(["opencode"])["opencode"]
    assert opencode["project-lead"] == "opencode-go/deepseek-v4-pro"
    assert opencode["build-lead"] == "opencode-go/deepseek-v4-pro"  # all leads on opencode
    claude = md.plan(["claude"])["claude"]
    assert claude == {"project-lead": "claude-sonnet-4-6", "bootstrap": "claude-sonnet-4-6"}
    assert "build-lead" not in claude  # deep-tier leads are not downgraded on claude
    assert md.plan(["cursor"]) == {}  # a runtime with no floor yet → nothing


def test_seed_floor_writes_project_yaml_pins(tmp_path) -> None:
    lines = md.seed_floor(tmp_path, ["opencode", "claude"], write=True)
    assert lines
    data = yaml.safe_load(project.config_path(tmp_path).read_text(encoding="utf-8"))
    opencode = data["runtimes"]["opencode"]["agents"]
    assert opencode["project-lead"] == "opencode-go/deepseek-v4-pro"
    assert opencode["bootstrap"] == "opencode-go/deepseek-v4-pro"
    assert data["runtimes"]["claude"]["agents"]["project-lead"] == "claude-sonnet-4-6"


def test_seed_floor_leaves_existing_project_yaml_untouched(tmp_path) -> None:
    path = project.config_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("mode: vibe\n", encoding="utf-8")
    lines = md.seed_floor(tmp_path, ["opencode"], write=True)
    assert "left as-is" in lines[0]
    assert path.read_text(encoding="utf-8") == "mode: vibe\n"


def test_seed_floor_dry_run_writes_nothing(tmp_path) -> None:
    md.seed_floor(tmp_path, ["opencode"], write=False)
    assert not project.config_path(tmp_path).is_file()


def test_init_bakes_floor_into_opencode_leads(tmp_path) -> None:
    main(["init", str(tmp_path), "--write", "--no-git", "--runtime", "opencode", "--name", "demo"])
    matches = list((tmp_path / ".opencode").rglob("project-lead.md"))
    assert matches, "project-lead agent should be exported for opencode"
    assert "opencode-go/deepseek-v4-pro" in matches[0].read_text(encoding="utf-8")
