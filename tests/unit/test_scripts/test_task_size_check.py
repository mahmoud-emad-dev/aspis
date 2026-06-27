"""Tests for task_size_check.py"""
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/task_size_check.py")


def _write_tasks(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_small_task_list(tmp_path):
    """Small task list within thresholds."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] [high] [simple] [feature] — Task one
  - Packet: V1 (light) | Builder: standard
- [ ] T-002 [P0] [high] [simple] [feature] — Task two
  - Packet: V2 (standard) | Builder: standard
- [ ] T-003 [P1] [medium] [moderate] [feature] — Task three
  - Packet: V2 (standard) | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "Total tasks:" in result.stdout


def test_over_threshold(tmp_path):
    """Many V3 tasks → over threshold for vibe mode."""
    tasks = tmp_path / "TASKS.md"
    task_lines = []
    for i in range(1, 25):
        task_lines.append(f"- [ ] T-{i:03d} [P1] [medium] [moderate] [feature] — Task {i}")
        task_lines.append(f"  - Packet: V3 (deep) | Builder: standard")
    _write_tasks(tasks, "# Tasks\n" + "\n".join(task_lines))
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks), "--mode", "vibe"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should warn
    assert "WARNINGS" in result.stdout or result.returncode != 0


def test_json_output(tmp_path):
    """JSON output."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] — Task one
  - Packet: V1 (light) | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    import json
    data = json.loads(result.stdout)
    assert data["total_tasks"] == 1


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
