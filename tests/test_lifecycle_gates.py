"""Tests for the lifecycle gates that previously shipped untested (R-005).

Covers the git-hook installer (wrapper creation + idempotency), the post-commit
hook's never-fail guarantee, and ``aspis doctor``'s failing exit path.
"""

from __future__ import annotations

import argparse
import sys

from aspis import resources
from aspis.commands import doctor
from aspis.health import Check

_HOOKS = resources.catalog_dir() / "scripts" / "hooks"
sys.path.insert(0, str(_HOOKS))

import install  # noqa: E402
import postcommit  # noqa: E402

# --- install.py --------------------------------------------------------------


def test_install_writes_a_wrapper_per_hook(tmp_path) -> None:
    (tmp_path / ".git").mkdir()

    written = install.install(tmp_path)

    assert set(written) == {"pre-commit", "commit-msg", "post-commit"}
    for hook in written:
        body = (tmp_path / ".git" / "hooks" / hook).read_text(encoding="utf-8")
        assert sys.executable in body  # runs the interpreter that has aspis
        assert hook.replace("-", "") in body.replace("-", "")  # points at its entry script


def test_install_is_idempotent(tmp_path) -> None:
    (tmp_path / ".git").mkdir()
    install.install(tmp_path)
    first = (tmp_path / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")

    install.install(tmp_path)  # re-run
    second = (tmp_path / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")

    assert first == second


def test_install_no_git_writes_nothing(tmp_path) -> None:
    assert install.install(tmp_path) == []  # no .git → no wrappers


# --- postcommit.py never-fail guarantee --------------------------------------


def test_postcommit_exits_zero_even_when_a_step_raises(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    def _boom(*_args, **_kwargs):
        raise RuntimeError("step blew up")

    # Make the first step raise and neutralise the network/context steps.
    monkeypatch.setattr(postcommit.cleanup, "clean", _boom)
    monkeypatch.setattr(postcommit.gitignore, "ensure", lambda *a, **k: None)

    # A post-commit hook must never undo a commit by exiting non-zero.
    assert postcommit.main() == 0


# --- doctor failing exit path ------------------------------------------------


def test_doctor_exits_nonzero_when_a_check_fails(monkeypatch) -> None:
    monkeypatch.setattr(doctor, "run_checks", lambda root: [Check("python", "fail", "too old")])
    monkeypatch.setattr(doctor, "build_inventory", lambda root: {})  # no live detection
    assert doctor._run(argparse.Namespace(path=".")) == 1


def test_doctor_exits_zero_when_only_warnings(monkeypatch) -> None:
    monkeypatch.setattr(
        doctor,
        "run_checks",
        lambda root: [Check("git", "warn", "missing"), Check("python", "ok", "3.12")],
    )
    monkeypatch.setattr(doctor, "build_inventory", lambda root: {})  # no live detection
    assert doctor._run(argparse.Namespace(path=".")) == 0  # warnings pass


# --- doctor model-drift warning ----------------------------------------------


def test_doctor_warns_when_connected_plans_changed(monkeypatch, capsys, tmp_path) -> None:
    from aspis import inventory
    from aspis.runtimes.base import RuntimeInventory

    (tmp_path / ".aspis").mkdir()
    # last sync saw only opencode-go; now minimax is also connected -> drift.
    inventory.save_sync_snapshot(
        tmp_path, {"opencode": RuntimeInventory("opencode", True, ("opencode-go",))}
    )
    monkeypatch.setattr(doctor, "run_checks", lambda root: [])
    monkeypatch.setattr(
        doctor,
        "build_inventory",
        lambda root: {"opencode": RuntimeInventory("opencode", True, ("opencode-go", "minimax"))},
    )

    doctor._run(argparse.Namespace(path=str(tmp_path)))
    out = capsys.readouterr().out
    assert "connected plans changed" in out
    assert "+opencode/minimax" in out
    assert "aspis models --sync" in out


def test_doctor_prompts_sync_when_never_synced(monkeypatch, capsys, tmp_path) -> None:
    from aspis.runtimes.base import RuntimeInventory

    (tmp_path / ".aspis").mkdir()  # a project, but no last-sync snapshot
    monkeypatch.setattr(doctor, "run_checks", lambda root: [])
    monkeypatch.setattr(
        doctor, "build_inventory", lambda root: {"opencode": RuntimeInventory("opencode", True, ())}
    )

    doctor._run(argparse.Namespace(path=str(tmp_path)))
    out = capsys.readouterr().out
    assert "run `aspis models --sync`" in out
