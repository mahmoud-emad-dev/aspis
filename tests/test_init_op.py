"""Tests for the init operation (scaffold + root files + dry-run)."""

from __future__ import annotations

from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def test_init_does_not_scaffold_on_demand_dirs(tmp_path) -> None:
    """On-demand dirs are not scaffolded with .gitkeep at init.

    ``features`` and ``research`` are truly absent (no writer has run yet).
    ``current`` may be created by ``write_export`` for export state (F-015),
    but it is never scaffolded empty — it only exists when it has content.
    """
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")
    # features and research: no writer has created them yet.
    assert not (tmp_path / ".aspis" / "features").exists()
    assert not (tmp_path / ".aspis" / "research").exists()
    # current: not scaffolded with .gitkeep (the empty-dir scaffold mechanism).
    current = tmp_path / ".aspis" / "current"
    assert not (current / ".gitkeep").exists()
    # If current exists (created by write_export for export state), it has content.
    if current.exists():
        assert any(current.iterdir()), "current should not be empty if it exists"
    # The filled scaffold dirs are present.
    for name in ("config", "context", "index", "rules", "scripts", "templates", "workflows"):
        assert (tmp_path / ".aspis" / name).is_dir()


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
    context = tmp_path / ".aspis" / "context"  # a scaffold dir (features is on-demand now)
    (context / ".gitkeep").unlink()  # simulate the reaped state
    (context / "NOTE.md").write_text("x", encoding="utf-8")

    _engine().run("init", tmp_path, write=True, force=True, no_git=True, name="demo")

    assert not (context / ".gitkeep").exists()


def test_init_root_gitignore_has_universal_baseline(tmp_path) -> None:
    """The root .gitignore ships the always-correct baseline (OS noise + secrets)."""
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text  # secrets never committed
    assert "!.env.example" in text  # but an example is kept
    assert ".DS_Store" in text  # OS noise


def test_init_seeds_brain_gitignore(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, name="demo")

    brain_ignore = tmp_path / ".aspis" / ".gitignore"
    text = brain_ignore.read_text(encoding="utf-8")
    # The brain owns its generated-index + cache hygiene (paths relative to .aspis/).
    assert "index/FILE_REGISTRY.yaml" in text
    assert "index/test-ledger.json" in text
    assert "context/CURRENT_STATE.md" in text


def test_init_writes_claude_md_only_for_claude_runtime(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True, runtimes=["claude"])
    # The adapter declares CLAUDE.md as Claude's root guide; AGENTS.md is universal.
    assert (tmp_path / "CLAUDE.md").is_file()
    assert (tmp_path / "AGENTS.md").is_file()


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
