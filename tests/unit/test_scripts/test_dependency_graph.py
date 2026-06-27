"""Tests for dependency_graph.py"""
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/dependency_graph.py")


def _write_tasks(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_simple_dag(tmp_path):
    """Simple DAG with no cycles."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] [high] [simple] [feature] — Root task
  - Depends on: none | Blocks: T-002 [hard]
  - Packet: V1 | Builder: standard
- [ ] T-002 [P0] [high] [simple] [feature] — Child of T-001
  - Depends on: T-001 [hard] | Blocks: T-003 [hard]
  - Packet: V1 | Builder: standard
- [ ] T-003 [P1] [medium] [moderate] [feature] — Leaf task
  - Depends on: T-002 [hard] | Blocks: none
  - Packet: V2 | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "T-001" in result.stdout


def test_cycle_detection(tmp_path):
    """Circular dependency → detected."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] — Task A
  - Depends on: T-002 [hard] | Blocks: none
  - Packet: V1 | Builder: standard
- [ ] T-002 [P0] — Task B
  - Depends on: T-001 [hard] | Blocks: none
  - Packet: V1 | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should detect cycle
    assert "CIRCULAR" in result.stdout or result.returncode == 1


def test_dot_output(tmp_path):
    """DOT format output."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] — Root
  - Depends on: none | Blocks: T-002
  - Packet: V1 | Builder: standard
- [ ] T-002 [P1] — Child
  - Depends on: T-001 [hard] | Blocks: none
  - Packet: V1 | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks), "--format", "dot"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "digraph" in result.stdout
    assert "T-001" in result.stdout


def test_json_output(tmp_path):
    """JSON format output."""
    tasks = tmp_path / "TASKS.md"
    _write_tasks(tasks, """# Tasks
- [ ] T-001 [P0] — Root
  - Depends on: none | Blocks: T-002
  - Packet: V1 | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tasks), "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    import json
    data = json.loads(result.stdout)
    assert "tasks" in data


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
