"""Tests for the F-020 ``aspis stack`` (correctable stack) and ``aspis heal`` (floor) verbs."""

from __future__ import annotations

from pathlib import Path

from aspis import manifest
from aspis.cli import main


def _init(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_stack_show_and_set(tmp_path, capsys) -> None:
    root = _init(tmp_path)
    rc = main(["stack", "--path", str(root)])  # show (none yet)
    assert rc == 0

    rc = main(["stack", "python, fastapi", "--path", str(root)])
    assert rc == 0
    data = manifest.load(root)
    assert "python" in data["stack"] and data["stack_source"] == "user"

    capsys.readouterr()
    main(["stack", "--path", str(root)])  # show again → reflects the set value + source
    out = capsys.readouterr().out
    assert "python" in out and "user" in out


def test_stack_requires_project(tmp_path, capsys) -> None:
    rc = main(["stack", "python", "--path", str(tmp_path)])
    assert rc == 1
    assert "No ASPIS project" in capsys.readouterr().out


def test_heal_check_reports_readiness(tmp_path, capsys) -> None:
    root = _init(tmp_path)
    # A freshly-initialized project has skeleton brain files → not yet ready.
    rc = main(["heal", "--check", "--path", str(root)])
    out = capsys.readouterr().out
    assert "readiness:" in out
    assert rc in (0, 1)  # 1 if floor not yet filled, 0 if init already filled it


def test_heal_requires_project(tmp_path, capsys) -> None:
    rc = main(["heal", "--path", str(tmp_path)])
    assert rc == 1
    assert "No ASPIS project" in capsys.readouterr().out
