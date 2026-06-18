"""Tests for the bundled catalog: the Project Lead agent and its skills export.

These exercise the superset → per-runtime translation: the same catalog YAML
renders as a Claude ``tools`` list and as an OpenCode ``permission`` block.
"""

from __future__ import annotations

import yaml

from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def _frontmatter(text: str) -> dict:
    return yaml.safe_load(text.split("---", 2)[1])


def test_project_lead_renders_for_claude(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "project-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["name"] == "project-lead"
    assert fm["model"] == "claude-sonnet-4-6"  # standard tier resolved
    assert fm["tools"] == ["Read", "Grep", "Glob", "Bash"]  # Claude capitalises
    # Claude cannot express these superset fields, so they are dropped.
    assert "mode" not in fm
    assert "permission" not in fm
    assert "delegates" not in fm


def test_project_lead_renders_for_opencode(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "project-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["mode"] == "primary"
    assert fm["temperature"] == 0.1
    perm = fm["permission"]
    assert perm["read"] == "allow" and perm["grep"] == "allow"
    assert perm["bash"]["git status*"] == "allow" and perm["bash"]["*"] == "deny"
    assert perm["bash"]["python3 .asps/scripts/context/*"] == "allow"  # guarded refresh
    assert perm["webfetch"] == "deny"  # not granted → denied
    # delegates → task allow-list (leads + the project-explorer helper)
    assert perm["task"]["planning-lead"] == "allow" and perm["task"]["*"] == "deny"
    assert perm["task"]["project-explorer"] == "allow"
    # skills → skill allow-list
    assert perm["skill"]["context-packaging"] == "allow"


def test_system_lead_is_a_deep_authoring_primary(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "system-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "claude-opus-4-8"  # deep tier — authoring/governance
    assert "Edit" in fm["tools"] and "Write" in fm["tools"]  # it modifies the runtime

    skills = tmp_path / ".claude" / "skills"
    for skill in (
        "system-awareness",
        "deterministic-first",
        "asset-authoring",
        "system-validation",
        "system-repair",
    ):
        assert (skills / skill / "SKILL.md").is_file()


def test_system_lead_opencode_reserves_commits(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "system-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["mode"] == "subagent"  # ships as subagent; promoted at bootstrap
    perm = fm["permission"]
    assert perm["edit"] == "allow"  # authors assets
    assert perm["bash"]["git commit*"] == "deny"  # commits go through the committer


def test_project_explorer_is_a_cheap_readonly_subagent(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "project-explorer.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "claude-haiku-4-5-20251001"  # cheap tier
    assert fm["tools"] == ["Read", "Grep", "Glob", "Bash"]  # bash is guarded to context tools


def test_planning_lead_is_a_deep_planning_subagent(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "planning-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "claude-opus-4-8"  # deep tier — planning is reasoning-heavy
    assert "Edit" in fm["tools"] and "Write" in fm["tools"]  # it authors plan artifacts


def test_planning_lead_opencode_plans_only(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "planning-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["mode"] == "subagent"  # promoted at bootstrap
    perm = fm["permission"]
    assert perm["webfetch"] == "deny"  # research goes through the Research Lead
    assert perm["bash"]["git commit*"] == "deny"  # commits go through the committer
    assert perm["skill"]["task-decomposition"] == "allow"


def test_planning_lead_skills_and_templates_are_shipped(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    skills = tmp_path / ".claude" / "skills"
    for skill in (
        "planning-intake",
        "requirement-clarification",
        "feature-planning",
        "architecture-planning",
        "task-decomposition",
    ):
        assert (skills / skill / "SKILL.md").is_file()

    templates = tmp_path / ".asps" / "templates"
    for template in ("SPEC.md", "PLAN.md", "TASKS.md", "TASK_PACKET.md"):
        assert (templates / template).is_file()


def test_build_lead_is_a_deep_orchestrator(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "build-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "minimax-m2-pro"  # deep tier — the reasoning orchestrator
    assert fm["mode"] == "subagent"  # promoted at bootstrap
    perm = fm["permission"]
    assert perm["bash"]["git commit*"] == "deny"  # commits go through the committer
    # delegates its execution arm
    assert perm["task"]["general-builder"] == "allow"
    assert perm["task"]["committer"] == "allow"
    assert perm["skill"]["task-orchestration"] == "allow"


def test_build_workers_are_scoped(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    builder = _frontmatter(
        (tmp_path / ".opencode" / "agents" / "general-builder.md").read_text(encoding="utf-8")
    )
    assert builder["model"] == "minimax-m3"  # standard tier — executes packets
    assert builder["permission"]["edit"] == "allow"  # it writes code
    assert builder["permission"]["bash"]["git commit*"] == "deny"  # but never commits

    committer = _frontmatter(
        (tmp_path / ".opencode" / "agents" / "committer.md").read_text(encoding="utf-8")
    )
    assert committer["model"] == "deepseek-v4-flash"  # cheap tier — mechanical
    assert committer["permission"]["bash"]["git commit*"] == "allow"  # the only committer
    assert committer["permission"]["bash"]["git push*"] == "deny"  # never pushes
    assert "edit" not in committer["permission"]  # never edits files


def test_build_lead_skills_are_copied(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    skills = tmp_path / ".claude" / "skills"
    for skill in ("build-readiness", "task-orchestration", "scope-control", "selective-testing"):
        assert (skills / skill / "SKILL.md").is_file()


def test_reviewer_is_a_deep_readonly_authority(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "reviewer.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "claude-opus-4-8"  # deep tier — quality judgment
    assert fm["tools"] == ["Read", "Grep", "Glob", "Bash"]  # read-only: never edits


def test_reviewer_opencode_is_read_only(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "reviewer.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["mode"] == "subagent"  # promoted at bootstrap
    perm = fm["permission"]
    assert "edit" not in perm and "write" not in perm  # never modifies the work
    assert perm["bash"]["git commit*"] == "deny"
    assert perm["skill"]["quality-review"] == "allow"


def test_reviewer_skills_are_copied(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    skills = tmp_path / ".claude" / "skills"
    for skill in ("review-strategy", "quality-review", "acceptance-decision"):
        assert (skills / skill / "SKILL.md").is_file()


def test_research_lead_is_the_web_enabled_knowledge_layer(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode

    text = (tmp_path / ".opencode" / "agents" / "research-lead.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["mode"] == "subagent"  # a support lead — never promoted
    perm = fm["permission"]
    assert perm["webfetch"] == "allow" and perm["websearch"] == "allow"  # the one researcher
    assert "edit" not in perm  # packages references via write, doesn't edit code
    assert perm["skill"]["knowledge-packaging"] == "allow"

    skills = tmp_path / ".opencode" / "skills"
    for skill in ("knowledge-research", "knowledge-packaging"):
        assert (skills / skill / "SKILL.md").is_file()


def test_project_lead_skills_are_copied(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    skills = tmp_path / ".claude" / "skills"
    for skill in (
        "project-awareness",
        "request-classification",
        "lead-routing",
        "context-packaging",
        "project-question-answering",
        "project-guidance",
    ):
        assert (skills / skill / "SKILL.md").is_file()
