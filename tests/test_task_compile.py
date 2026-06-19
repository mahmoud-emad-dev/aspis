"""Tests for the task-compile planning script (run as shipped, via subprocess)."""

from __future__ import annotations

import json
import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "planning" / "task_compile.py"

TASKS = """# F-001 — Tasks

## Phase 1 — Setup
- [ ] T-01 [P] [US1] Add the retry helper in `src/aspis/retry.py`.
- [ ] T-02 Wire it in `src/aspis/export.py` (depends on T-01).
"""


def _seed_feature(root):
    """Create a feature with a TASKS.md, the packet template, and an active pointer."""
    templates = root / ".aspis" / "templates"
    templates.mkdir(parents=True)
    (templates / "TASK_PACKET.md").write_text(
        resources.template("TASK_PACKET.md"), encoding="utf-8"
    )

    feature = root / ".aspis" / "features" / "F-001-retries"
    feature.mkdir(parents=True)
    (feature / "TASKS.md").write_text(TASKS, encoding="utf-8")

    current = root / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text(
        json.dumps(
            {
                "id": "F-001",
                "slug": "retries",
                "title": "Add retries",
                "path": ".aspis/features/F-001-retries",
            }
        ),
        encoding="utf-8",
    )
    return feature


def test_compile_emits_a_packet_per_task(tmp_path) -> None:
    feature = _seed_feature(tmp_path)

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    t01 = feature / "tasks" / "T-01.md"
    t02 = feature / "tasks" / "T-02.md"
    assert t01.is_file() and t02.is_file()

    body = t01.read_text(encoding="utf-8")
    assert "F-001 / T-01" in body  # identity filled
    assert "src/aspis/retry.py" in body  # allowed files filled from the task path
    assert "<exact/path/one>" not in body  # placeholder replaced


def test_compile_skips_existing_without_force(tmp_path) -> None:
    feature = _seed_feature(tmp_path)
    (feature / "tasks").mkdir()
    (feature / "tasks" / "T-01.md").write_text("hand-edited", encoding="utf-8")

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    assert (feature / "tasks" / "T-01.md").read_text(encoding="utf-8") == "hand-edited"  # preserved
    assert (feature / "tasks" / "T-02.md").is_file()  # the new one still written
