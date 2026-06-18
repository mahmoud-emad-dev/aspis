"""End-to-end tests for the `aspis bootstrap` CLI verb."""

from __future__ import annotations

from aspis.cli import main


def test_check_reports_not_bootstrapped(tmp_path, capsys) -> None:
    rc = main(["bootstrap", str(tmp_path), "--check"])
    assert rc == 1
    assert "NOT bootstrapped" in capsys.readouterr().out


def test_bootstrap_then_check_passes(tmp_path, capsys) -> None:
    main(["init", str(tmp_path), "--write", "--no-git"])
    capsys.readouterr()  # discard init output

    rc = main(["bootstrap", str(tmp_path), "--write", "--yes", "--goal", "A tool"])
    assert rc == 0
    assert "BOOTSTRAPPED" in capsys.readouterr().out

    assert main(["bootstrap", str(tmp_path), "--check"]) == 0  # gate now passes
