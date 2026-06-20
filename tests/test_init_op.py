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

    assert (tmp_path / ".aspis" / "context" / ".gitkeep").is_file()
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8").startswith("# demo")
    # base profile targets opencode only → no CLAUDE.md
    assert not (tmp_path / "CLAUDE.md").exists()


def test_reinit_does_not_replant_gitkeep_in_populated_dir(tmp_path) -> None:
    # A re-init over a brain whose directory already holds content must not drop a
    # stale .gitkeep next to that content.
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")
    features = tmp_path / ".aspis" / "features"
    (features / ".gitkeep").unlink()  # simulate the reaped state
    (features / "F-001-demo").mkdir()
    (features / "F-001-demo" / "SPEC.md").write_text("x", encoding="utf-8")

    _engine().run("init", tmp_path, write=True, force=True, no_git=True, name="demo")

    assert not (features / ".gitkeep").exists()


def test_init_writes_claude_md_only_for_claude_runtime(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])
    assert (tmp_path / "CLAUDE.md").is_file()


def test_init_ships_context_scripts(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)
    context = tmp_path / ".aspis" / "scripts" / "context"
    assert (context / "update.py").is_file()
    assert (context / "build_registry.py").is_file()


def test_init_seeds_as_built_architecture(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")

    arch = tmp_path / ".aspis" / "context" / "ARCHITECTURE.md"
    text = arch.read_text(encoding="utf-8")
    assert text.startswith("# demo — Architecture (as-built)")
    assert "docs/ARCHITECTURE.md" in text  # documents the intended/as-built split


def test_init_seeds_purposes_config(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")

    purposes = tmp_path / ".aspis" / "config" / "purposes.json"
    import json

    data = json.loads(purposes.read_text(encoding="utf-8"))
    assert set(data) >= {"files", "names", "patterns"}  # the three layers, one file


def test_init_does_not_clobber_existing_architecture(tmp_path) -> None:
    context = tmp_path / ".aspis" / "context"
    context.mkdir(parents=True)
    (context / "ARCHITECTURE.md").write_text("# hand-written, keep me\n", encoding="utf-8")

    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")

    assert (context / "ARCHITECTURE.md").read_text(encoding="utf-8") == "# hand-written, keep me\n"


def test_init_dry_run_writes_nothing(tmp_path) -> None:
    ctx = _engine().run("init", tmp_path, write=False, no_git=True)
    assert ctx.messages
    assert not (tmp_path / ".aspis").exists()
    assert not (tmp_path / "AGENTS.md").exists()
