"""Tests for the init operation (scaffold + root files + dry-run)."""

from __future__ import annotations

from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def test_init_scaffolds_brain_and_root_files(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")

    assert (tmp_path / ".asps" / "context" / ".gitkeep").is_file()
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8").startswith("# demo")
    # base profile targets opencode only → no CLAUDE.md
    assert not (tmp_path / "CLAUDE.md").exists()


def test_init_writes_claude_md_only_for_claude_runtime(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])
    assert (tmp_path / "CLAUDE.md").is_file()


def test_init_ships_context_scripts(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)
    context = tmp_path / ".asps" / "scripts" / "context"
    assert (context / "update.py").is_file()
    assert (context / "build_registry.py").is_file()


def test_init_dry_run_writes_nothing(tmp_path) -> None:
    ctx = _engine().run("init", tmp_path, write=False, no_git=True)
    assert ctx.messages
    assert not (tmp_path / ".asps").exists()
    assert not (tmp_path / "AGENTS.md").exists()
