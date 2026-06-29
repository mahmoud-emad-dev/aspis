"""F-020 T-09/T-10 — init export completeness + the guided end-to-end acceptance."""

from __future__ import annotations

from pathlib import Path

import yaml

from aspis import resources
from aspis.cli import main
from aspis.operations import pre_bootstrap as pb
from aspis.operations import setup_workflow as sw


def _init(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_init_exports_every_base_agent(tmp_path) -> None:
    # T-09: init ships the complete current asset set — no base agent is missing.
    root = _init(tmp_path)
    base = yaml.safe_load((resources.data_dir() / "profiles" / "base.yaml").read_text("utf-8"))
    expected = {Path(a).stem for a in base["agents"]}
    for runtime_dir in (".opencode", ".claude"):
        deployed = {p.stem for p in (root / runtime_dir / "agents").glob("*.md")}
        assert expected <= deployed, f"{runtime_dir} missing: {expected - deployed}"


def test_e2e_empty_to_initialized_then_onboard(tmp_path) -> None:
    # T-10: empty dir → init → state is initialized-not-onboarded → guidance says onboard.
    root = _init(tmp_path)
    state, text = sw.guide(root)
    assert state["project_state"] == pb.INITIALIZED
    assert sw.next_step(state) == "onboard"
    assert "Next: onboard" in text


def test_e2e_skip_leaves_valid_project(tmp_path) -> None:
    # Skipping onboarding leaves a structurally valid project (brain + runtime present).
    root = _init(tmp_path)
    sw.mark(root, sw.SKIPPED)
    assert (root / ".aspis").is_dir() and (root / ".opencode").is_dir()
    assert sw.resume_point(pb.load_state(root)) == "skipped"
