"""Tests for project detection (mode + stack)."""

from __future__ import annotations

from aspis.detect import detect_stack, project_mode


def test_project_mode_empty_then_existing(tmp_path) -> None:
    assert project_mode(tmp_path) == "empty"
    (tmp_path / ".git").mkdir()  # ignored — still empty
    assert project_mode(tmp_path) == "empty"
    (tmp_path / "main.py").write_text("x", encoding="utf-8")
    assert project_mode(tmp_path) == "existing"


def test_detect_stack(tmp_path) -> None:
    assert detect_stack(tmp_path) == "unknown"
    (tmp_path / "pyproject.toml").write_text("[project]", encoding="utf-8")
    assert detect_stack(tmp_path) == "python"
