"""F-020 T-08 — state recovery + resume: re-init never destroys, onboarding resumes."""

from __future__ import annotations

from pathlib import Path

from aspis.cli import main
from aspis.operations import pre_bootstrap as pb
from aspis.operations import setup_workflow as sw


def _init(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_reinit_preserves_brain_and_user_code(tmp_path) -> None:
    root = _init(tmp_path)
    user = root / "app.py"
    user.write_text("print('mine')\n", encoding="utf-8")
    # Re-running init (an upgrade-style re-export) must not destroy the brain or user code.
    rc = main(["init", str(root), "--write", "--no-git", "--name", "demo"])
    assert rc == 0
    assert (root / ".aspis").is_dir()
    assert user.read_text(encoding="utf-8") == "print('mine')\n"


def test_resume_point_follows_recorded_status(tmp_path) -> None:
    root = _init(tmp_path)
    pb.resolve(root)
    # pending → state-derived step (onboard for a fresh init)
    assert sw.resume_point(pb.load_state(root)) == "onboard"
    # skipped → skipped (don't re-ask)
    sw.mark(root, sw.SKIPPED)
    assert sw.resume_point(pb.load_state(root)) == "skipped"
    # complete → done
    sw.mark(root, sw.COMPLETE)
    assert sw.resume_point(pb.load_state(root)) == "done"


def test_incomplete_aspis_state_detected(tmp_path) -> None:
    # A brain that is missing context/ + index/ is incomplete (needs recover, not bootstrap).
    brain = tmp_path / ".aspis"
    (brain / "rules").mkdir(parents=True)
    assert pb.project_state(tmp_path) == pb.INCOMPLETE
    assert sw.next_step({"project_state": pb.INCOMPLETE}) == "recover"
