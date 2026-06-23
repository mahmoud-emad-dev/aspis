"""Tests for ``aspis context`` — refresh + one-call L1 hot context (F-014 T-10)."""

from __future__ import annotations

import json
from pathlib import Path

from aspis.cli import main as cli_main
from aspis.engine import build_engine
from aspis.operations import register_all


def _init(root: Path) -> None:
    engine = build_engine()
    register_all(engine)
    engine.run("init", root, write=True, no_git=True)


def test_context_prints_hot_context(tmp_path, capsys) -> None:
    _init(tmp_path)
    code = cli_main(["context", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Current state" in out  # the L1 hot section is shown


def test_context_shows_active_feature(tmp_path, capsys) -> None:
    _init(tmp_path)
    pointer = tmp_path / ".aspis" / "current" / "active_feature.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(
        json.dumps({"id": "F-042", "title": "demo", "phase": "build", "branch": "feat/x"}),
        encoding="utf-8",
    )
    code = cli_main(["context", str(tmp_path), "--no-refresh"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Active feature" in out
    assert "F-042" in out


def test_context_rejects_non_project(tmp_path, capsys) -> None:
    code = cli_main(["context", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "not an ASPIS project" in out
