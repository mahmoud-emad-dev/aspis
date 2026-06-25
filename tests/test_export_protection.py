"""Tests for the hash-protected write_export decide flow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aspis.export import ExportAction, ExportPlan, ProtectionError, write_export
from aspis.protect import sha256_text


def _plan(tmp_path: Path, files: dict[str, str]) -> tuple[ExportPlan, Path]:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    actions = []
    for name, content in files.items():
        src = catalog / name
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text(content, encoding="utf-8")
        actions.append(
            ExportAction(
                kind="templates",
                runtime="",
                source=src,
                target=f".aspis/templates/{name}",
                op="copy",
            )
        )
    return ExportPlan(actions=actions, catalog_root=None), tmp_path / "proj"


def _snapshot(target_root: Path) -> dict:
    path = target_root / ".aspis" / "current" / "export-snapshot.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _log_lines(target_root: Path) -> list[dict]:
    path = target_root / ".aspis" / "current" / "export-log.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").strip().split("\n")]


def test_first_export_adds_all_files(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha", "b.md": "beta"})
    performed = write_export(plan, target, write=True)

    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "alpha"
    assert (target / ".aspis" / "templates" / "b.md").read_text(encoding="utf-8") == "beta"
    assert len(performed) == 2
    snapshot = _snapshot(target)
    assert snapshot["paths"][".aspis/templates/a.md"] == sha256_text("alpha")
    assert snapshot["paths"][".aspis/templates/b.md"] == sha256_text("beta")


def test_second_export_unchanged_skips_writes(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    write_export(plan, target, write=True)
    first_hash = (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8")

    performed = write_export(plan, target, write=True, apply=True)

    assert "UNCHANGED" in performed[0]
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == first_hash


def test_user_edit_is_protected(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    write_export(plan, target, write=True)
    live = target / ".aspis" / "templates" / "a.md"
    live.write_text("user edited", encoding="utf-8")

    performed = write_export(plan, target, write=True, apply=True)

    assert "PROTECT" in performed[0]
    assert live.read_text(encoding="utf-8") == "user edited"


def test_catalog_update_is_applied(tmp_path: Path) -> None:
    files = {"a.md": "alpha"}
    plan, target = _plan(tmp_path, files)
    write_export(plan, target, write=True)

    # Mutate the source (catalog) file in place.
    plan.actions[0].source.write_text("updated alpha", encoding="utf-8")
    performed = write_export(plan, target, write=True, apply=True)

    assert performed[0].startswith("copy:")
    live = target / ".aspis" / "templates" / "a.md"
    assert live.read_text(encoding="utf-8") == "updated alpha"
    assert _snapshot(target)["paths"][".aspis/templates/a.md"] == sha256_text("updated alpha")


def test_both_changed_is_conflict(tmp_path: Path) -> None:
    files = {"a.md": "alpha"}
    plan, target = _plan(tmp_path, files)
    write_export(plan, target, write=True)
    live = target / ".aspis" / "templates" / "a.md"
    live.write_text("user edited", encoding="utf-8")
    plan.actions[0].source.write_text("catalog edited", encoding="utf-8")

    performed = write_export(plan, target, write=True, apply=True)

    assert "CONFLICT" in performed[0]
    assert live.read_text(encoding="utf-8") == "user edited"


def test_force_overwrites_everything(tmp_path: Path) -> None:
    files = {"a.md": "alpha"}
    plan, target = _plan(tmp_path, files)
    write_export(plan, target, write=True)
    live = target / ".aspis" / "templates" / "a.md"
    live.write_text("user edited", encoding="utf-8")

    performed = write_export(plan, target, force=True, write=True)

    assert performed[0].startswith("copy:")
    assert live.read_text(encoding="utf-8") == "alpha"


def test_force_conflicts_overwrites_conflict_but_not_protect(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "a", "b.md": "b"})
    write_export(plan, target, write=True)

    # a.md: CONFLICT (both user and catalog changed)
    (target / ".aspis" / "templates" / "a.md").write_text("a user", encoding="utf-8")
    plan.actions[0].source.write_text("a catalog", encoding="utf-8")

    # b.md: PROTECT (only user changed)
    (target / ".aspis" / "templates" / "b.md").write_text("b user", encoding="utf-8")

    performed = write_export(plan, target, write=True, apply=True, force_conflicts=True)

    performed_by_target = {p.split(": ", 1)[1]: p for p in performed}
    assert performed_by_target[".aspis/templates/a.md"].startswith("copy:")
    assert "PROTECT" in performed_by_target[".aspis/templates/b.md"]
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "a catalog"
    assert (target / ".aspis" / "templates" / "b.md").read_text(encoding="utf-8") == "b user"


def test_strict_raises_on_conflict(tmp_path: Path) -> None:
    files = {"a.md": "alpha"}
    plan, target = _plan(tmp_path, files)
    write_export(plan, target, write=True)
    (target / ".aspis" / "templates" / "a.md").write_text("user edited", encoding="utf-8")
    plan.actions[0].source.write_text("catalog edited", encoding="utf-8")

    with pytest.raises(ProtectionError, match="conflict on .aspis/templates/a.md"):
        write_export(plan, target, write=True, apply=True, strict=True)

    # Lock must be released even after the exception.
    assert not (target / ".aspis" / "current" / "export.lock").exists()


def test_scope_filters_actions(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "a", "b.md": "b"})
    performed = write_export(
        plan, target, write=True, apply=True, scope=".aspis/templates/a.md"
    )

    assert len(performed) == 1
    assert ".aspis/templates/a.md" in performed[0]
    assert (target / ".aspis" / "templates" / "a.md").exists()
    assert not (target / ".aspis" / "templates" / "b.md").exists()


def test_apply_implies_write(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    performed = write_export(plan, target, apply=True)

    assert performed[0].startswith("copy:")
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "alpha"


def test_audit_log_appended(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha", "b.md": "beta"})
    write_export(plan, target, write=True)

    lines = _log_lines(target)
    assert len(lines) == 2
    assert {line["path"] for line in lines} == {
        ".aspis/templates/a.md",
        ".aspis/templates/b.md",
    }


def test_plain_write_backward_compatible_skips_existing(tmp_path: Path) -> None:
    files = {"a.md": "alpha"}
    plan, target = _plan(tmp_path, files)
    write_export(plan, target, write=True)

    plan.actions[0].source.write_text("updated alpha", encoding="utf-8")
    performed = write_export(plan, target, write=True)

    assert "UPDATE" in performed[0]
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "alpha"


def test_lockfile_created_and_released(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    write_export(plan, target, write=True)
    assert not (target / ".aspis" / "current" / "export.lock").exists()


def test_stale_lock_with_dead_pid_is_taken_over(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    lock_path = target / ".aspis" / "current" / "export.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("99999999", encoding="utf-8")

    performed = write_export(plan, target, write=True)

    assert performed[0].startswith("copy:")
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "alpha"
    assert not lock_path.exists()


# --------------------------------------------------------------------------- #
# Reviewer-requested coverage (Unit-2 review F-005)
# --------------------------------------------------------------------------- #


def test_strict_raises_on_protect(tmp_path: Path) -> None:
    # FR-010: --strict must fail on LIVE-CUSTOMIZED (PROTECT), not just CONFLICT.
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    write_export(plan, target, write=True)
    (target / ".aspis" / "templates" / "a.md").write_text("user edited", encoding="utf-8")

    with pytest.raises(ProtectionError, match="protected on .aspis/templates/a.md"):
        write_export(plan, target, write=True, apply=True, strict=True)

    # The lock must be released even after the strict exception.
    assert not (target / ".aspis" / "current" / "export.lock").exists()


def test_reset_snapshot_recovers_from_corruption(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    write_export(plan, target, write=True)
    snap = target / ".aspis" / "current" / "export-snapshot.json"

    # Corrupt the snapshot; without reset_snapshot this would raise.
    snap.write_text("not json at all", encoding="utf-8")
    with pytest.raises(ProtectionError):
        write_export(plan, target, write=True)

    # With reset_snapshot, the export recovers and rewrites a valid snapshot.
    performed = write_export(plan, target, write=True, reset_snapshot=True)
    assert "UNCHANGED" in performed[0]  # live == regen -> UNCHANGED
    assert (target / ".aspis" / "templates" / "a.md").read_text(encoding="utf-8") == "alpha"
    assert json.loads(snap.read_text(encoding="utf-8"))["paths"] == {}


def test_unknown_records_live_hash_in_snapshot(tmp_path: Path) -> None:
    # A pre-existing live file with no snapshot entry -> UNKNOWN -> preserved,
    # and its live hash is recorded so a future run can detect changes.
    plan, target = _plan(tmp_path, {"a.md": "alpha"})
    live = target / ".aspis" / "templates" / "a.md"
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_text("pre-existing", encoding="utf-8")

    write_export(plan, target, write=True, apply=True)

    assert live.read_text(encoding="utf-8") == "pre-existing"  # preserved
    assert _snapshot(target)["paths"][".aspis/templates/a.md"] == sha256_text("pre-existing")


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    plan, target = _plan(tmp_path, {"a.md": "alpha", "b.md": "beta"})

    performed = write_export(plan, target, write=False, apply=False)

    assert performed  # describes the decisions
    assert not target.exists()  # no files, no .aspis/current/, no lockfile


_AGENT_SRC = (
    "---\nname: lead\ndescription: d\nmode: primary\nmodel: standard\n---\n\nbody\n"
)


def test_render_op_hash_parity_is_unchanged(tmp_path: Path) -> None:
    # _regen_hash for a render op must equal the hash of what _apply writes,
    # otherwise a second export would falsely PROTECT/CONFLICT. A render-agent
    # action is exported twice; the second run must classify it UNCHANGED.
    catalog = tmp_path / "catalog"
    (catalog / "agents").mkdir(parents=True)
    src = catalog / "agents" / "lead.md"
    src.write_text(_AGENT_SRC, encoding="utf-8")
    action = ExportAction(
        kind="agents",
        runtime="opencode",
        source=src,
        target=".opencode/agents/lead.md",
        op="render-agent",
    )
    plan = ExportPlan(actions=[action], catalog_root=None)
    target = tmp_path / "proj"

    write_export(plan, target, write=True)  # first export -> ADD, renders
    live = target / ".opencode" / "agents" / "lead.md"
    first = live.read_text(encoding="utf-8")

    performed = write_export(plan, target, write=True, apply=True)  # second -> UNCHANGED

    assert "UNCHANGED" in performed[0]
    assert live.read_text(encoding="utf-8") == first  # not rewritten
