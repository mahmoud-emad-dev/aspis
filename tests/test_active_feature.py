"""Tests for the active-feature pointer guard.

Covers the pure validate/set-phase helpers (imported directly) and the switch-guard
wired into the feature scaffold (exercised via subprocess, as a project runs it).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from aspis import resources

_PLANNING = resources.catalog_dir() / "scripts" / "planning"
if str(_PLANNING) not in sys.path:
    sys.path.insert(0, str(_PLANNING))

import active_feature  # noqa: E402  (sibling catalog script)

SCAFFOLD = _PLANNING / "feature_scaffold.py"


def _write_pointer(root: Path, **overrides: str) -> dict:
    """Write an active_feature.json with sensible defaults; return the written dict."""
    data = {
        "id": "F-001",
        "slug": "demo",
        "title": "Demo feature",
        "path": ".aspis/features/F-001-demo",
        "branch": "feature/F-001-demo",
        "mode": "mvp",
        "phase": "build",
    }
    data.update(overrides)
    pointer = root / ".aspis" / "current" / "active_feature.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def _seed_existing_feature(root: Path, *, phase: str) -> None:
    """Write a pointer at F-001 plus its feature dir, so the next scaffold id is F-002."""
    data = _write_pointer(root, phase=phase)
    (root / data["path"]).mkdir(parents=True, exist_ok=True)


def _seed_templates(root: Path) -> None:
    templates = root / ".aspis" / "templates"
    templates.mkdir(parents=True, exist_ok=True)
    for name in ("SPEC.md", "PLAN.md", "TASKS.md"):
        (templates / name).write_text(resources.template(name), encoding="utf-8")


def _run_scaffold(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), str(root), "--name", "Next thing", "--no-branch", *extra],
        capture_output=True,
        text=True,
    )


# --- validate -------------------------------------------------------------------


def test_validate_clean_pointer_has_no_problems(tmp_path) -> None:
    data = _write_pointer(tmp_path)
    (tmp_path / data["path"]).mkdir(parents=True, exist_ok=True)
    assert active_feature.validate(tmp_path, check_branch=False) == []


def test_validate_flags_missing_file(tmp_path) -> None:
    assert active_feature.validate(tmp_path) == ["active_feature.json is missing or malformed"]


def test_validate_flags_bad_field_path_and_phase(tmp_path) -> None:
    _write_pointer(tmp_path, title="", phase="cooking", path=".aspis/features/F-404-gone")
    problems = active_feature.validate(tmp_path, check_branch=False)
    assert any("title" in p for p in problems)
    assert any("does not exist" in p for p in problems)
    assert any("unknown phase" in p for p in problems)


# --- set_phase ------------------------------------------------------------------


def test_set_phase_updates_pointer(tmp_path) -> None:
    _write_pointer(tmp_path, phase="build")
    active_feature.set_phase(tmp_path, "merged")
    assert active_feature.read_pointer(tmp_path)["phase"] == "merged"


def test_set_phase_rejects_unknown_phase(tmp_path) -> None:
    _write_pointer(tmp_path)
    with pytest.raises(ValueError):
        active_feature.set_phase(tmp_path, "frozen")


# --- scaffold switch-guard ------------------------------------------------------


def test_scaffold_refuses_switch_while_feature_unfinished(tmp_path) -> None:
    _seed_templates(tmp_path)
    _seed_existing_feature(tmp_path, phase="build")
    result = _run_scaffold(tmp_path)
    assert result.returncode == 2
    assert "refused" in result.stdout.lower()
    assert active_feature.read_pointer(tmp_path)["id"] == "F-001"  # pointer untouched


def test_scaffold_allows_switch_when_previous_terminal(tmp_path) -> None:
    _seed_templates(tmp_path)
    _seed_existing_feature(tmp_path, phase="merged")
    result = _run_scaffold(tmp_path)
    assert result.returncode == 0
    assert active_feature.read_pointer(tmp_path)["id"] == "F-002"


def test_scaffold_force_overrides_the_guard(tmp_path) -> None:
    _seed_templates(tmp_path)
    _seed_existing_feature(tmp_path, phase="build")
    result = _run_scaffold(tmp_path, "--force")
    assert result.returncode == 0
    assert active_feature.read_pointer(tmp_path)["id"] == "F-002"
