"""Tests for the prereq-validate gate script (run as shipped, via subprocess)."""

from __future__ import annotations

import json
import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "planning" / "prereq_validate.py"
MODES = resources.catalog_dir() / "config" / "policy" / "modes.yaml"


def _seed(root, *, mode, artifacts):
    """Create a feature with the given artifacts, the active pointer, and modes.yaml."""
    config = root / ".aspis" / "config"
    config.mkdir(parents=True)
    (config / "modes.yaml").write_text(MODES.read_text(encoding="utf-8"), encoding="utf-8")

    feature = root / ".aspis" / "features" / "F-001-thing"
    feature.mkdir(parents=True)
    for name in artifacts:
        (feature / name).write_text("x", encoding="utf-8")

    current = root / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text(
        json.dumps({"id": "F-001", "path": ".aspis/features/F-001-thing", "mode": mode}),
        encoding="utf-8",
    )


def _run(root, phase):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), "--phase", phase],
        capture_output=True,
        text=True,
    )


def test_build_blocked_when_plan_and_tasks_missing(tmp_path) -> None:
    _seed(tmp_path, mode="production", artifacts=["SPEC.md"])

    proc = _run(tmp_path, "build")

    assert proc.returncode == 1  # usable as a gate
    assert "MISSING: PLAN.md" in proc.stdout
    assert "MISSING: TASKS.md" in proc.stdout


def test_vibe_relaxes_the_plan_requirement(tmp_path) -> None:
    # vibe skips architecture, so PLAN.md is not required to build.
    _seed(tmp_path, mode="vibe", artifacts=["SPEC.md", "TASKS.md"])

    proc = _run(tmp_path, "build")

    assert proc.returncode == 0  # OK despite no PLAN.md
    assert "PLAN.md" not in proc.stdout
