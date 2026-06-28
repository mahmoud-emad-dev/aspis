"""Tests for cross_ref.py"""
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/research/cross_ref.py")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_all_refs_resolve(tmp_path):
    """When references resolve, should not crash."""
    # Create catalog structure
    agents_dir = tmp_path / "agents"
    skills_dir = tmp_path / "skills" / "test-skill"
    _write_file(agents_dir / "test-agent.md", """---
name: test-agent
skills: [test-skill]
delegates: []
runtimes: [opencode]
---
# Test Agent
""")
    _write_file(skills_dir / "SKILL.md", "# Test Skill\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path), "--root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should complete without exception
    out = result.stdout
    assert "References:" in out or "Agents:" in out or "total_refs" in out.lower()


def test_broken_ref(tmp_path):
    """Broken skill reference should be flagged."""
    agents_dir = tmp_path / "agents"
    _write_file(agents_dir / "test-agent.md", """---
name: test-agent
skills: [nonexistent-skill]
delegates: []
runtimes: [opencode]
---
# Test Agent
""")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "nonexistent-skill" in result.stdout or result.returncode != 0


def test_json_output(tmp_path):
    """JSON output mode."""
    agents_dir = tmp_path / "agents"
    _write_file(agents_dir / "test-agent.md", """---
name: test-agent
skills: []
delegates: []
runtimes: [opencode]
---
# Test
""")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(tmp_path), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    import json
    data = json.loads(result.stdout)
    assert "total_refs" in data


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
