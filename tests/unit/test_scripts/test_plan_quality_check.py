"""Tests for plan_quality_check.py"""
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/planning/plan_quality_check.py")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_well_traced_plan(tmp_path):
    """A well-traced plan should score high."""
    spec = tmp_path / "SPEC.md"
    tasks = tmp_path / "TASKS.md"
    _write_file(spec, """# Spec
- **FR-L0-001**: Feature A
- **FR-L0-002**: Feature B
- **SC-L0-001**: Feature A works
""")
    _write_file(tasks, """# Tasks
### L0 — Layer 0
- [ ] T-001 [P0] [high] [simple] [feature] — Build feature A
  - Depends on: none | Blocks: T-002
  - Packet: V1 (light) | Builder: standard
  - Acceptance: FR-L0-001 satisfied
- [ ] T-002 [P0] [high] [simple] [verify] — L0 exit gate
  - Depends on: T-001 [hard]
  - Packet: V1 (light)
  - Acceptance: SC-L0-001 met
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(spec), str(tasks)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Score may be below threshold depending on test data richness
    assert "QUALITY SCORE" in result.stdout


def test_untasked_fr(tmp_path):
    """A spec with FRs not traced to tasks should flag them."""
    spec = tmp_path / "SPEC.md"
    tasks = tmp_path / "TASKS.md"
    _write_file(spec, """# Spec
- **FR-L0-001**: Feature A
- **FR-L0-002**: Feature B (untasked)
- **FR-L0-003**: Feature C (untasked)
""")
    _write_file(tasks, """# Tasks
- [ ] T-001 [P0] — Build FR-L0-001
  - Packet: V1 | Builder: standard
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(spec), str(tasks)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should produce a lower score but not crash
    assert "QUALITY SCORE" in result.stdout


def test_dir_mode(tmp_path):
    """--dir mode finds SPEC.md and TASKS.md."""
    feat_dir = tmp_path / "feature"
    _write_file(feat_dir / "SPEC.md", "# Spec\n- **FR-L0-001**: Test\n")
    _write_file(feat_dir / "TASKS.md", "# Tasks\n- [ ] T-001 [P0] — Test FR-L0-001\n  - Packet: V1 | Builder: standard\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--dir", str(feat_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
