"""Tests for the feature-scaffold planning script.

Runs the shipped script exactly as a project would (via subprocess), so the test
covers the real artifact, not an in-process import.
"""

from __future__ import annotations

import json
import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "planning" / "feature_scaffold.py"


def _seed_templates(root) -> None:
    """Give the tmp project the planning templates the scaffold copies."""
    templates = root / ".aspis" / "templates"
    templates.mkdir(parents=True)
    for name in ("SPEC.md", "PLAN.md", "TASKS.md"):
        (templates / name).write_text(resources.template(name), encoding="utf-8")


def test_scaffold_creates_feature_and_pointer(tmp_path) -> None:
    _seed_templates(tmp_path)

    subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--name", "Add export retries", "--no-branch"],
        check=True,
        capture_output=True,
    )

    feature = tmp_path / ".aspis" / "features" / "F-001-export-retries"
    assert (feature / "SPEC.md").is_file()
    assert (feature / "PLAN.md").is_file()
    assert (feature / "tasks").is_dir()  # packets land here
    assert "F-001" in (feature / "SPEC.md").read_text(encoding="utf-8")  # placeholder filled

    pointer = json.loads(
        (tmp_path / ".aspis" / "current" / "active_feature.json").read_text(encoding="utf-8")
    )
    assert pointer["id"] == "F-001"
    assert pointer["slug"] == "export-retries"  # stop words ("add") dropped
    assert pointer["mode"] == "production"
    assert pointer["phase"] == "plan"


def test_scaffold_increments_id(tmp_path) -> None:
    _seed_templates(tmp_path)
    (tmp_path / ".aspis" / "features" / "F-007-old").mkdir(parents=True)

    subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--name", "Next thing", "--no-branch"],
        check=True,
        capture_output=True,
    )

    assert (tmp_path / ".aspis" / "features" / "F-008-next-thing").is_dir()
