"""Tests for the F-020 pre-bootstrap resolution layer (read-only decision state)."""

from __future__ import annotations

from pathlib import Path

from aspis import manifest
from aspis.cli import main
from aspis.operations import pre_bootstrap as pb


def _init(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_empty_dir_is_empty_and_not_written(tmp_path) -> None:
    state = pb.resolve(tmp_path)
    assert state["project_state"] == pb.EMPTY
    # No brain → nothing written (stays read-only).
    assert not pb.state_path(tmp_path).exists()


def test_existing_code_without_aspis(tmp_path) -> None:
    (tmp_path / "main.py").write_text("print('hi')\n", encoding="utf-8")
    assert pb.resolve(tmp_path)["project_state"] == pb.EXISTING_CODE


def test_initialized_project_writes_state(tmp_path) -> None:
    root = _init(tmp_path)
    state = pb.resolve(root)
    assert state["project_state"] == pb.INITIALIZED
    assert pb.state_path(root).is_file()
    assert state["rules"]["system"] is True  # system-rules ship at init
    assert "user_path" in state["rules"]


def test_bootstrapped_state(tmp_path) -> None:
    root = _init(tmp_path)
    manifest.save(root, {"bootstrapped": True})
    assert pb.resolve(root)["project_state"] == pb.BOOTSTRAPPED


def test_stack_confidence_high_for_single_marker(tmp_path) -> None:
    root = _init(tmp_path)
    (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    stack = pb.resolve(root)["stack"]
    assert stack["confidence"] == "high"
    assert "python" in stack["value"]


def test_stack_unknown_when_no_markers(tmp_path) -> None:
    root = _init(tmp_path)
    stack = pb.resolve(root)["stack"]
    assert stack["confidence"] == "unknown" and stack["value"] == "unknown"


def test_plan_file_detection_root_and_docs(tmp_path) -> None:
    root = _init(tmp_path)
    (root / "PLAN.md").write_text("# plan\n", encoding="utf-8")
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "architecture.md").write_text("# arch\n", encoding="utf-8")
    (root / "notes.md").write_text("# unrelated\n", encoding="utf-8")
    plans = pb.resolve(root)["plan_files"]
    assert "PLAN.md" in plans and "docs/architecture.md" in plans
    assert "notes.md" not in plans  # name doesn't match a plan pattern


def test_onboarding_block_is_preserved_for_resume(tmp_path) -> None:
    root = _init(tmp_path)
    pb.resolve(root)
    state = pb.load_state(root)
    state["onboarding"] = {"status": "in_progress", "answered": ["mode"]}
    pb.save_state(root, state)
    # A re-resolve must not clobber onboarding progress.
    again = pb.resolve(root)
    assert again["onboarding"]["status"] == "in_progress"
    assert again["onboarding"]["answered"] == ["mode"]


def test_runtimes_block_shape(tmp_path) -> None:
    root = _init(tmp_path)
    rt = pb.resolve(root)["runtimes"]
    assert set(rt) >= {"available", "detected", "capabilities", "subscriptions"}
    assert isinstance(rt["available"], list)
