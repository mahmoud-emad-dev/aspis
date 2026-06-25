"""F-015 end-to-end acceptance tests — safe catalog export through the full CLI.

These tests exercise the complete init -> edit -> re-apply cycle through the real
CLI entry point (``aspis.cli.main``), verifying the hash-protection engine's
behavior in realistic scenarios. Agent files are used as the test substrate
because their rendered content changes when model routing changes — simulating
a "catalog update" — while skills (copied verbatim) cannot be catalog-changed
without modifying the bundled source. The protection behavior is identical for
all asset kinds (the decide flow is kind-agnostic).
"""

from __future__ import annotations

import json
from pathlib import Path

from aspis.cli import main
from aspis.commands import models as models_cmd


def _init(tmp_path: Path) -> int:
    """Scaffold a fresh project with --write --no-git."""
    return main(["init", str(tmp_path), "--write", "--no-git"])


def _agent(tmp_path: Path, name: str) -> Path:
    """Return the path to a live opencode agent file."""
    return tmp_path / ".opencode" / "agents" / f"{name}.md"


def _pin_agent(tmp_path: Path, name: str, model: str) -> None:
    """Write a project.yaml that pins *name* to *model* (simulates a catalog change)."""
    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        f"runtimes:\n  opencode:\n    agents:\n      {name}: {model}\n",
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# Story 1: user-edit protected, catalog-change updated
# --------------------------------------------------------------------------- #


def test_e2e_user_edit_protected_catalog_change_updated(tmp_path: Path) -> None:
    """Init -> user-edit agent A -> model-config-change agent B -> re-apply.

    Agent A (user-edited) is PROTECTED; agent B (catalog-changed) is UPDATED.
    """
    assert _init(tmp_path) == 0
    agent_a = _agent(tmp_path, "committer")
    agent_b = _agent(tmp_path, "build-lead")

    # User edits agent A.
    agent_a.write_text(
        agent_a.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )
    # Catalog "changes" agent B (model routing change).
    _pin_agent(tmp_path, "build-lead", "opencode/zzz-test-pin")

    rc = main(["init", str(tmp_path), "--write", "--apply", "--no-git"])
    assert rc == 0

    # Agent A: PROTECT -- user edit preserved.
    assert "<!-- user edit -->" in agent_a.read_text(encoding="utf-8")
    # Agent B: UPDATE -- re-rendered with the new model.
    assert "opencode/zzz-test-pin" in agent_b.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Story 2: conflict not overwritten, then --force-conflicts overwrites
# --------------------------------------------------------------------------- #


def test_e2e_conflict_not_overwritten_then_force_conflicts_overwrites(
    tmp_path: Path,
) -> None:
    """Init -> user-edit agent X -> catalog-change agent X -> re-apply: CONFLICT.

    The file is not overwritten. Then --force-conflicts overwrites it.
    """
    assert _init(tmp_path) == 0
    agent = _agent(tmp_path, "committer")
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )
    _pin_agent(tmp_path, "committer", "opencode/zzz-test-pin")

    # Re-apply: CONFLICT -- not overwritten.
    rc = main(["init", str(tmp_path), "--write", "--apply", "--no-git"])
    assert rc == 0
    assert "<!-- user edit -->" in agent.read_text(encoding="utf-8")
    assert "opencode/zzz-test-pin" not in agent.read_text(encoding="utf-8")

    # Re-apply with --force-conflicts: overwrites the CONFLICT.
    rc = main([
        "init", str(tmp_path), "--write", "--apply",
        "--force-conflicts", "--no-git",
    ])
    assert rc == 0
    assert "<!-- user edit -->" not in agent.read_text(encoding="utf-8")
    assert "opencode/zzz-test-pin" in agent.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Story 3: --scope limits to a single file
# --------------------------------------------------------------------------- #


def test_e2e_scope_limits_to_single_file(tmp_path: Path) -> None:
    """--scope limits export to files whose target path starts with the prefix."""
    assert _init(tmp_path) == 0
    agent_a = _agent(tmp_path, "committer")
    agent_b = _agent(tmp_path, "build-lead")
    agent_a.unlink()
    agent_b.unlink()

    rc = main([
        "init", str(tmp_path), "--write",
        "--scope=.opencode/agents/committer.md", "--no-git",
    ])
    assert rc == 0
    assert agent_a.exists()
    assert not agent_b.exists()


# --------------------------------------------------------------------------- #
# Story 4: conflict + --strict -> non-zero exit
# --------------------------------------------------------------------------- #


def test_e2e_strict_nonzero_exit_on_conflict(tmp_path: Path, capsys) -> None:
    """Conflict + --strict -> non-zero exit with a clear error message."""
    assert _init(tmp_path) == 0
    agent = _agent(tmp_path, "committer")
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )
    _pin_agent(tmp_path, "committer", "opencode/zzz-test-pin")

    rc = main(["init", str(tmp_path), "--write", "--apply", "--strict", "--no-git"])
    assert rc != 0
    out = capsys.readouterr().out
    assert "conflict" in out.lower()


# --------------------------------------------------------------------------- #
# Story 5: models --apply protects user-edited agents
# --------------------------------------------------------------------------- #


def test_e2e_models_apply_protects_user_edited_agents(monkeypatch, tmp_path: Path) -> None:
    """models --apply protects user-edited agents after a model routing change."""
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path / "no-home"))
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})

    assert _init(tmp_path) == 0
    agent = _agent(tmp_path, "committer")
    agent.write_text(
        agent.read_text(encoding="utf-8") + "\n<!-- user edit -->\n", encoding="utf-8"
    )

    rc = main(["models", "--path", str(tmp_path), "--apply"])
    assert rc == 0
    # PROTECT: user edit preserved.
    assert "<!-- user edit -->" in agent.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Story 6: corrupted snapshot + --reset-snapshot -> recovery
# --------------------------------------------------------------------------- #


def test_e2e_corrupted_snapshot_reset_recovery(tmp_path: Path) -> None:
    """Corrupted snapshot + --reset-snapshot -> recovery; export proceeds."""
    assert _init(tmp_path) == 0
    snap = tmp_path / ".aspis" / "current" / "export-snapshot.json"
    snap.write_text("not valid json {{{", encoding="utf-8")

    rc = main(["init", str(tmp_path), "--write", "--reset-snapshot", "--no-git"])
    assert rc == 0
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert "paths" in data
