"""Tests for the bootstrap operation (wizard defaults, slot fill, manifest, brain fill)."""

from __future__ import annotations

import json

from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def test_bootstrap_fills_slots_and_writes_manifest(tmp_path) -> None:
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    # Non-interactive: --yes + flags drive the values (no prompts).
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="A tiny tool", stack="python")

    data = json.loads((tmp_path / ".aspis" / "manifest.json").read_text(encoding="utf-8"))
    assert data["bootstrapped"] is True
    assert data["goal"] == "A tiny tool"
    assert data["stack"] == "python"

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "A tiny tool" in agents
    assert "filled at bootstrap" not in agents  # both slots replaced

    # The brain fill ran (context files produced by the shipped scripts).
    assert (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").is_file()
    assert (tmp_path / ".aspis" / "context" / "CURRENT_STATE.md").is_file()


def test_bootstrap_writes_project_config_with_mode(tmp_path) -> None:
    from aspis import project

    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, mode="mvp")

    assert (tmp_path / ".aspis" / "config" / "project.yaml").is_file()
    assert project.default_mode(tmp_path) == "mvp"  # the chosen default is readable


def test_bootstrap_makes_init_then_bootstrap_commits(tmp_path) -> None:
    import subprocess

    engine = _engine()
    engine.run("init", tmp_path, write=True)  # git init, scaffolding left uncommitted
    engine.run("bootstrap", tmp_path, write=True, yes=True)

    log = subprocess.run(
        ["git", "-C", str(tmp_path), "log", "--oneline"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "initialize ASPIS project" in log  # 1st commit (auto-committed init)
    assert "bootstrap ASPIS project" in log  # 2nd commit (bootstrap fill)

    data = json.loads((tmp_path / ".aspis" / "manifest.json").read_text(encoding="utf-8"))
    assert "bootstrapped_at" in data  # done stamp recorded


def test_bootstrap_requires_init(tmp_path) -> None:
    import pytest

    with pytest.raises(RuntimeError, match="aspis init"):
        _engine().run("bootstrap", tmp_path, write=True, yes=True)


def test_init_exports_the_bootstrap_package(tmp_path) -> None:
    """Init ships the transient onboarding package; bootstrap removes it."""
    from aspis.operations.bootstrap import bootstrap_package

    _engine().run("init", tmp_path, write=True, no_git=True)
    assert (tmp_path / ".opencode" / "agents" / "bootstrap.md").is_file()
    assert (tmp_path / ".opencode" / "skills" / "project-onboarding").is_dir()
    assert (tmp_path / ".aspis" / "workflows" / "bootstrap.md").is_file()
    assert len(bootstrap_package(tmp_path)) == 3


def test_bootstrap_self_cleans_the_package_and_stamps_version(tmp_path) -> None:
    """A green bootstrap removes the onboarding package and records the engine version."""
    from aspis import __version__
    from aspis.operations.bootstrap import bootstrap_package

    engine = _engine()
    engine.run("init", tmp_path, write=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="t", stack="python")

    assert bootstrap_package(tmp_path) == []  # package gone
    assert not (tmp_path / ".opencode" / "agents" / "bootstrap.md").exists()
    assert not (tmp_path / ".opencode" / "skills" / "project-onboarding").exists()
    assert not (tmp_path / ".aspis" / "workflows" / "bootstrap.md").exists()

    data = json.loads((tmp_path / ".aspis" / "manifest.json").read_text(encoding="utf-8"))
    assert data["bootstrap_engine_version"] == __version__


def test_bootstrap_keeps_package_when_doctor_fails(tmp_path, monkeypatch) -> None:
    """If the health gate fails, the onboarding package is kept for a re-run."""
    from types import SimpleNamespace

    from aspis.operations import bootstrap as bootstrap_op
    from aspis.operations.bootstrap import bootstrap_package

    monkeypatch.setattr(bootstrap_op, "run_checks", lambda root: [SimpleNamespace(status="fail")])
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True)

    assert len(bootstrap_package(tmp_path)) == 3  # nothing was cleaned


def test_bootstrap_keeps_package_when_brain_not_ready(tmp_path, monkeypatch) -> None:
    """Readiness gate: if required brain files are missing/empty, keep the package."""
    from aspis.operations import bootstrap as bootstrap_op
    from aspis.operations.bootstrap import bootstrap_package

    # Doctor passes, but the brain fill is skipped → required files absent → not ready.
    monkeypatch.setattr(bootstrap_op, "run_checks", lambda root: [])
    monkeypatch.setattr(bootstrap_op, "_run_brain_fill", lambda ctx, *, write: None)
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True)

    assert len(bootstrap_package(tmp_path)) == 3  # not ready → package kept


def test_bootstrap_keeps_package_when_config_invalid(tmp_path, monkeypatch) -> None:
    """Validation gate: malformed exported config keeps the package (project not ready)."""
    from aspis.operations import bootstrap as bootstrap_op
    from aspis.operations.bootstrap import bootstrap_package

    monkeypatch.setattr(bootstrap_op, "run_checks", lambda root: [])
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    # Corrupt an exported config YAML after init, before bootstrap's gate runs.
    (tmp_path / ".aspis" / "config" / "modes.yaml").write_text("mode: : : bad\n", encoding="utf-8")
    engine.run("bootstrap", tmp_path, write=True, yes=True)

    assert len(bootstrap_package(tmp_path)) == 3  # invalid config → package kept


def test_bootstrap_syncs_agent_models(tmp_path) -> None:
    """Bootstrap runs `models --sync` so the project has a per-agent model config."""
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, stack="python")

    agent_models = tmp_path / ".aspis" / "config" / "agent-models.yaml"
    assert agent_models.is_file()
    assert "by_capability" in agent_models.read_text(encoding="utf-8")


def test_bootstrap_enriches_gitignore_for_stack(tmp_path) -> None:
    """Bootstrap expands .gitignore from the detected stack (offline cache)."""
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, stack="python")

    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "aspis gitignore (python)" in gitignore
    assert "__pycache__" in gitignore


def test_bootstrap_never_commits_user_code(tmp_path) -> None:
    """On an existing repo, bootstrap commits only ASPIS paths — never user code."""
    import subprocess

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)

    engine = _engine()
    engine.run("init", tmp_path, write=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="demo", stack="python")

    tracked = subprocess.run(
        ["git", "-C", str(tmp_path), "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    assert "src/app.py" not in tracked  # user code never swept into the bootstrap commit
    assert (tmp_path / "src" / "app.py").is_file()  # and still on disk, untouched


def test_bootstrap_leaves_clean_tree_no_stale_gitkeep(tmp_path) -> None:
    """After a greenfield bootstrap the ASPIS tree is clean — no dangling .gitkeep."""
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)

    engine = _engine()
    engine.run("init", tmp_path, write=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="demo", stack="python")

    status = subprocess.run(
        ["git", "-C", str(tmp_path), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert status.strip() == ""  # clean tree (no pending .gitkeep deletion)
    # A populated brain dir carries no stale .gitkeep.
    assert not (tmp_path / ".aspis" / "index" / ".gitkeep").exists()
