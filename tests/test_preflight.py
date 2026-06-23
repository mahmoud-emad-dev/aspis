"""Tests for ``aspis preflight`` — the deterministic pre-task gate (F-014 T-07)."""

from __future__ import annotations

import json
from pathlib import Path

from aspis.cli import main as cli_main
from aspis.engine import build_engine
from aspis.operations import register_all


def _init(root: Path) -> None:
    engine = build_engine()
    register_all(engine)
    engine.run("init", root, write=True)  # real git repo + auto-commit of the scaffold


def test_preflight_ready_on_clean_repo(tmp_path, capsys) -> None:
    _init(tmp_path)
    code = cli_main(["preflight", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Ready" in out
    assert "clean" in out


def test_preflight_blocks_on_dirty_tree(tmp_path, capsys) -> None:
    _init(tmp_path)
    (tmp_path / "loose.txt").write_text("uncommitted\n", encoding="utf-8")
    code = cli_main(["preflight", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "loose.txt" in out  # the blocker names the offending path
    assert "committer" in out  # and the next action


def test_preflight_ignores_generated_brain_churn(tmp_path, capsys) -> None:
    _init(tmp_path)
    # Generated brain files churn after every commit — they must not block a prestart check.
    (tmp_path / ".aspis" / "index").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").write_text("changed\n", encoding="utf-8")
    code = cli_main(["preflight", str(tmp_path)])
    assert code == 0  # brain churn is expected, not a blocker


def _add_finding(root: Path) -> None:
    store = root / ".aspis" / "current" / "findings.json"
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(
        '[{"kind": "scope", "detail": "out-of-scope edit: x.py", "source": "scope-guard"}]',
        encoding="utf-8",
    )


def test_preflight_findings_advisory_in_warn_mode(tmp_path, capsys) -> None:
    # Default warn mode: findings are surfaced but NEVER block real work (fire-and-forget).
    _init(tmp_path)
    _add_finding(tmp_path)
    code = cli_main(["preflight", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0  # advisory, not a blocker
    assert "x.py" in out  # still surfaced for the agent to route
    assert "warn" in out


def test_preflight_findings_block_only_in_block_mode(tmp_path, capsys) -> None:
    _init(tmp_path)
    _add_finding(tmp_path)
    hooks = tmp_path / ".aspis" / "config" / "policy" / "hooks.yaml"
    hooks.write_text("enforcement: block\n", encoding="utf-8")
    code = cli_main(["preflight", str(tmp_path)])
    assert code == 1  # only an opt-in block-mode project gates on findings
    assert "x.py" in capsys.readouterr().out


def test_preflight_blocks_on_branch_mismatch(tmp_path, capsys) -> None:
    _init(tmp_path)
    pointer = tmp_path / ".aspis" / "current" / "active_feature.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(
        json.dumps({"id": "F-099", "branch": "feat/F-099-elsewhere"}), encoding="utf-8"
    )
    code = cli_main(["preflight", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "F-099" in out
    assert "checkout" in out
