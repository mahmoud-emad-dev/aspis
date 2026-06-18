"""Smoke tests for the ASPIS CLI.

Kept deliberately small: one check per real behaviour. These assert the
command runs and dispatches correctly, not internal implementation detail.
"""

from __future__ import annotations

import pytest

from aspis.cli import main


def test_version_exits_clean() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_no_command_prints_help(capsys) -> None:
    rc = main([])
    assert rc == 0
    assert "usage:" in capsys.readouterr().out.lower()


def test_status_reports_no_project(tmp_path, capsys) -> None:
    rc = main(["status", str(tmp_path)])
    assert rc == 0
    assert "No ASPIS project" in capsys.readouterr().out
