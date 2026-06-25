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


# --------------------------------------------------------------------------- #
# F-015 Unit 3: init CLI flags (apply, strict, scope, force-conflicts, reset)
# --------------------------------------------------------------------------- #


def test_init_cli_apply_flag_scaffolds_project(tmp_path) -> None:
    """--apply works like --write for a fresh init (all files are ADD)."""
    rc = main(["init", str(tmp_path), "--apply", "--no-git", "--name", "demo"])
    assert rc == 0
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / ".aspis" / "context" / ".gitkeep").is_file()


def test_init_cli_reapply_with_apply_updates_changed_agent(tmp_path) -> None:
    """--write --apply re-renders agents whose model routing changed (UPDATE)."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    assert "opencode/zzz-test-pin" not in agent.read_text(encoding="utf-8")

    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      committer: opencode/zzz-test-pin\n",
        encoding="utf-8",
    )

    rc = main(["init", str(tmp_path), "--write", "--apply", "--no-git"])
    assert rc == 0
    assert "opencode/zzz-test-pin" in agent.read_text(encoding="utf-8")


def test_init_cli_reapply_protects_user_edited_agent(tmp_path) -> None:
    """--write --apply skips user-edited agents (PROTECT)."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )

    rc = main(["init", str(tmp_path), "--write", "--apply", "--no-git"])
    assert rc == 0
    assert "<!-- user edit -->" in agent.read_text(encoding="utf-8")


def test_init_cli_strict_exits_nonzero_on_conflict(tmp_path, capsys) -> None:
    """--strict exits non-zero when a CONFLICT is detected."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )
    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      committer: opencode/zzz-test-pin\n",
        encoding="utf-8",
    )

    rc = main(["init", str(tmp_path), "--write", "--apply", "--strict", "--no-git"])
    assert rc != 0
    out = capsys.readouterr().out
    assert "conflict" in out.lower()


def test_init_cli_scope_limits_to_matching_files(tmp_path) -> None:
    """--scope limits export to files whose target path starts with the prefix."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    agent_a = tmp_path / ".opencode" / "agents" / "committer.md"
    agent_b = tmp_path / ".opencode" / "agents" / "build-lead.md"
    agent_a.unlink()
    agent_b.unlink()
    assert not agent_a.exists()
    assert not agent_b.exists()

    rc = main([
        "init", str(tmp_path), "--write",
        "--scope=.opencode/agents/committer.md", "--no-git",
    ])
    assert rc == 0
    assert agent_a.exists()
    assert not agent_b.exists()


def test_init_cli_force_conflicts_overwrites_conflict(tmp_path) -> None:
    """--force-conflicts overwrites a CONFLICT file during --apply."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )
    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      committer: opencode/zzz-test-pin\n",
        encoding="utf-8",
    )

    rc = main(["init", str(tmp_path), "--write", "--apply", "--force-conflicts", "--no-git"])
    assert rc == 0
    assert "<!-- user edit -->" not in agent.read_text(encoding="utf-8")
    assert "opencode/zzz-test-pin" in agent.read_text(encoding="utf-8")


def test_init_cli_reset_snapshot_recovers_from_corruption(tmp_path) -> None:
    """--reset-snapshot recovers from a corrupted snapshot."""
    import json

    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    snap = tmp_path / ".aspis" / "current" / "export-snapshot.json"
    snap.write_text("not valid json {{{", encoding="utf-8")

    rc = main(["init", str(tmp_path), "--write", "--reset-snapshot", "--no-git"])
    assert rc == 0
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert "paths" in data


def test_init_cli_force_conflicts_with_strict_rejected(tmp_path, capsys) -> None:
    """--force-conflicts --strict is a contradictory combination."""
    rc = main([
        "init", str(tmp_path), "--write", "--apply",
        "--force-conflicts", "--strict", "--no-git",
    ])
    assert rc != 0
    out = capsys.readouterr().out
    assert "contradictory" in out.lower()
