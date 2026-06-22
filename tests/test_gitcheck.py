"""Tests for the git-subsystem self-test (gitcheck.verify)."""

from __future__ import annotations

import subprocess

from aspis import gitcheck
from aspis.engine import build_engine
from aspis.operations import register_all


def _bootstrapped(tmp_path):
    engine = build_engine()
    register_all(engine)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    engine.run("init", tmp_path, write=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="demo", stack="python")
    return tmp_path


def test_verify_passes_on_a_bootstrapped_project(tmp_path) -> None:
    root = _bootstrapped(tmp_path)
    results = gitcheck.verify(root)
    by_name = {c.name: c for c in results}
    # Hooks wired + all four end-to-end jobs proven.
    for name in ("hook:pre-commit", "hooks-fire", "junk-clean", "gitkeep-reap", "commit-msg"):
        assert by_name[name].ok, f"{name}: {by_name[name].detail}"


def test_verify_is_side_effect_free(tmp_path) -> None:
    """The probe must leave history and the working tree exactly as they were."""
    root = _bootstrapped(tmp_path)
    head_before = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    gitcheck.verify(root)

    head_after = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert head_after == head_before  # probe commit rolled back
    assert status == ""  # tree clean
    assert not (root / ".aspis" / "_selftest_").exists()  # probe files cleaned


def test_hooks_armed_flags_missing_hooks(tmp_path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    checks = gitcheck.hooks_armed(tmp_path)
    assert all(not c.ok for c in checks)  # no aspis hooks installed yet
