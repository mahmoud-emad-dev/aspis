"""End-to-end tests for the `aspis init` CLI verb."""

from __future__ import annotations

from aspis.cli import main


def test_init_cli_dry_run_writes_nothing(tmp_path, capsys) -> None:
    rc = main(["init", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DRY-RUN" in out
    assert not (tmp_path / ".aspis").exists()


def test_init_cli_write_scaffolds_project(tmp_path) -> None:
    rc = main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    assert rc == 0
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / ".aspis" / "context" / ".gitkeep").is_file()
