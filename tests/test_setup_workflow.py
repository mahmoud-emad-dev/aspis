"""Tests for the F-020 setup-workflow orchestration (deterministic decision/UX layer)."""

from __future__ import annotations

from pathlib import Path

from aspis.cli import main
from aspis.operations import pre_bootstrap as pb
from aspis.operations import setup_workflow as sw


def _init(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_next_step_per_state() -> None:
    assert sw.next_step({"project_state": pb.EMPTY}) == "init"
    assert sw.next_step({"project_state": pb.EXISTING_CODE}) == "init"
    assert sw.next_step({"project_state": pb.INCOMPLETE}) == "recover"
    assert sw.next_step({"project_state": pb.LEGACY}) == "recover"
    assert sw.next_step({"project_state": pb.INITIALIZED}) == "onboard"
    assert sw.next_step({"project_state": pb.BOOTSTRAPPED}) == "done"


def test_options_for_onboard_state() -> None:
    keys = [k for k, _ in sw.options({"project_state": pb.INITIALIZED})]
    assert keys == ["continue", "skip", "runtime", "stop"]


def test_launch_commands_from_available_runtimes() -> None:
    state = {"runtimes": {"available": ["opencode", "claude"]}}
    cmds = sw.launch_commands(state)
    assert cmds["opencode"] and cmds["claude"]


def test_render_mentions_state_and_next() -> None:
    state = {
        "project_state": pb.INITIALIZED,
        "stack": {"value": "python", "confidence": "high"},
        "runtimes": {"available": ["opencode"]},
        "rules": {"system": True, "project": False, "user_present": False},
        "plan_files": ["docs/plan.md"],
    }
    text = sw.render(state)
    assert pb.INITIALIZED in text and "python" in text and "docs/plan.md" in text
    assert "Next: onboard" in text


def test_mark_records_onboarding_status_for_resume(tmp_path) -> None:
    root = _init(tmp_path)
    pb.resolve(root)  # write the state file
    sw.mark(root, sw.SKIPPED)
    assert pb.load_state(root)["onboarding"]["status"] == sw.SKIPPED


def test_guide_on_initialized_project(tmp_path) -> None:
    root = _init(tmp_path)
    state, text = sw.guide(root)
    assert state["project_state"] == pb.INITIALIZED
    assert "Next: onboard" in text
