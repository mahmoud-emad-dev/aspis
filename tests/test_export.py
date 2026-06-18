"""Tests for the export planner and writer."""

from __future__ import annotations

from pathlib import Path

from aspis.export import plan_export, write_export
from aspis.profiles import Profile

AGENT = "---\nname: lead\ndescription: d\nmode: primary\nmodel: standard\n---\n\nbody\n"
PROJECT_ONLY = "---\nname: gov\ndescription: d\nexport_scope: project-only\n---\n\nbody\n"
CLAUDE_ONLY = "---\nname: cc\ndescription: d\nruntimes:\n  - claude\n---\n\nbody\n"


def test_runtime_lock_skips_other_runtimes(tmp_path) -> None:
    root = tmp_path / "catalog"
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "cc.md").write_text(CLAUDE_ONLY, encoding="utf-8")
    profile = Profile(name="p", runtimes=["opencode", "claude"], agents=["agents/cc.md"])

    plan = plan_export(root, profile)

    runtimes = {a.runtime for a in plan.actions if a.kind == "agents"}
    assert runtimes == {"claude"}  # opencode skipped by the lock
    assert "agents/cc.md (opencode)" in plan.skipped_by_scope


def _catalog(tmp_path: Path) -> Path:
    root = tmp_path / "catalog"
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "lead.md").write_text(AGENT, encoding="utf-8")
    (root / "agents" / "gov.md").write_text(PROJECT_ONLY, encoding="utf-8")
    (root / "templates").mkdir()
    (root / "templates" / "report.md").write_text("# report", encoding="utf-8")
    return root


def test_plan_marks_missing_and_scope(tmp_path) -> None:
    profile = Profile(
        name="p",
        runtimes=["opencode", "claude"],
        agents=["agents/lead.md", "agents/gov.md", "agents/ghost.md"],
        templates=["templates/report.md"],
    )
    plan = plan_export(_catalog(tmp_path), profile)

    assert "agents/ghost.md" in plan.missing
    assert "agents/gov.md" in plan.skipped_by_scope
    agent_targets = [a.target for a in plan.actions if a.kind == "agents"]
    assert ".opencode/agents/lead.md" in agent_targets
    assert ".claude/agents/lead.md" in agent_targets  # per runtime
    assert any(a.target == ".asps/templates/report.md" for a in plan.actions)  # once


def test_write_renders_agents_and_copies_files(tmp_path) -> None:
    target = tmp_path / "proj"
    profile = Profile(
        name="p",
        runtimes=["opencode"],
        agents=["agents/lead.md"],
        templates=["templates/report.md"],
    )
    write_export(plan_export(_catalog(tmp_path), profile), target, write=True)

    assert "mode: primary" in (target / ".opencode/agents/lead.md").read_text(encoding="utf-8")
    assert (target / ".asps/templates/report.md").read_text(encoding="utf-8") == "# report"


def test_dry_run_writes_nothing(tmp_path) -> None:
    target = tmp_path / "proj"
    profile = Profile(name="p", agents=["agents/lead.md"])
    performed = write_export(plan_export(_catalog(tmp_path), profile), target, write=False)

    assert performed
    assert not target.exists()
