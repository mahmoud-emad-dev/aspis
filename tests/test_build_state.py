"""Tests for the CURRENT_STATE builder script."""

from __future__ import annotations

import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "build_state.py"


def _run(root) -> None:
    subprocess.run([sys.executable, str(SCRIPT), str(root)], check=True, capture_output=True)


def test_state_reports_stack_and_branch(git_repo) -> None:
    (git_repo / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    _run(git_repo)

    text = (git_repo / ".aspis" / "context" / "CURRENT_STATE.md").read_text(encoding="utf-8")
    assert "ASPIS:auto START" in text
    assert "**Stack:** python" in text
    assert "**Branch:**" in text


def test_state_reports_active_feature(git_repo) -> None:
    current = git_repo / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text(
        '{"id": "F-009", "title": "widgets", "phase": "build", "mode": "mvp"}',
        encoding="utf-8",
    )
    _run(git_repo)

    text = (git_repo / ".aspis" / "context" / "CURRENT_STATE.md").read_text(encoding="utf-8")
    assert "**Active feature:** F-009 widgets" in text
    assert "phase build" in text
    assert "no commits yet" in text  # seed commit carries no F-009 scope


def test_state_reports_no_active_feature(git_repo) -> None:
    _run(git_repo)
    text = (git_repo / ".aspis" / "context" / "CURRENT_STATE.md").read_text(encoding="utf-8")
    assert "**Active feature:** none" in text


def test_manual_content_is_preserved(git_repo) -> None:
    target = git_repo / ".aspis" / "context" / "CURRENT_STATE.md"
    target.parent.mkdir(parents=True)
    target.write_text(
        "<!-- ASPIS:auto START -->\nold\n<!-- ASPIS:auto END -->\n\n## My notes\nkeep me\n",
        encoding="utf-8",
    )
    _run(git_repo)

    text = target.read_text(encoding="utf-8")
    assert "## My notes" in text and "keep me" in text  # manual section survived
    assert "old" not in text  # auto block was regenerated
