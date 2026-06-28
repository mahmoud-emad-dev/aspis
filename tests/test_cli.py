"""Smoke tests for the ASPIS CLI.

Kept deliberately small: one check per real behaviour. These assert the
command runs and dispatches correctly, not internal implementation detail.
"""

from __future__ import annotations

import pkgutil

import pytest

import aspis.commands as commands_pkg
from aspis.cli import main
from aspis.commands import COMMAND_MODULES


def test_every_command_module_is_registered() -> None:
    # COMMAND_MODULES is hand-ordered on purpose (it sets --help order), so guard
    # against a verb file that ships but is never wired in (or vice versa).
    on_disk = {info.name for info in pkgutil.iter_modules(commands_pkg.__path__)}
    registered = {m.__name__.rsplit(".", 1)[1] for m in COMMAND_MODULES}
    assert on_disk == registered


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


def test_doctor_runs_and_reports(tmp_path, capsys) -> None:
    rc = main(["doctor", str(tmp_path)])
    out = capsys.readouterr().out
    # Python is current, so doctor should pass overall (warnings do not fail).
    assert rc == 0
    assert "python" in out
