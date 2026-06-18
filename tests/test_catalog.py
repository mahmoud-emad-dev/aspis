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


def test_project_explorer_is_a_cheap_readonly_subagent(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])

    text = (tmp_path / ".claude" / "agents" / "project-explorer.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["model"] == "claude-haiku-4-5-20251001"  # cheap tier
    assert fm["tools"] == ["Read", "Grep", "Glob", "Bash"]  # bash is guarded to context tools


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
