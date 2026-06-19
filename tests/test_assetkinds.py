"""Tests for the asset-kind registry and its two export consumers.

The headline guarantees: a brand-new brain kind exports with zero core edits
(Local Change), and per-runtime placement is gated by a runtime's capability,
not by a name check.
"""

from __future__ import annotations

from aspis import assetkinds, export
from aspis.export import plan_export
from aspis.profiles import Profile

# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #


def test_unknown_kind_defaults_to_brain_copy() -> None:
    k = assetkinds.kind("knowledge")
    assert k.placement == assetkinds.BRAIN
    assert k.op == assetkinds.COPY
    assert not k.per_runtime


def test_overridden_kinds_render_per_runtime() -> None:
    assert assetkinds.kind("agents").op == assetkinds.RENDER_AGENT
    assert assetkinds.kind("commands").op == assetkinds.RENDER_COMMAND
    assert assetkinds.is_per_runtime("agents")
    assert assetkinds.is_per_runtime("skills")
    assert not assetkinds.is_per_runtime("templates")


def test_target_paths() -> None:
    assert assetkinds.target("agents", "claude", "agents/lead.md") == ".claude/agents/lead.md"
    assert assetkinds.target("knowledge", "", "knowledge/python.md") == ".aspis/knowledge/python.md"


# --------------------------------------------------------------------------- #
# Story 1 — a new brain kind exports with no core change
# --------------------------------------------------------------------------- #


def test_new_brain_kind_exports_without_core_change(tmp_path) -> None:
    root = tmp_path / "catalog"
    (root / "knowledge").mkdir(parents=True)
    (root / "knowledge" / "python.md").write_text("# py", encoding="utf-8")
    profile = Profile(name="p", runtimes=["opencode"], knowledge=["knowledge/python.md"])

    plan = plan_export(root, profile)

    actions = [a for a in plan.actions if a.kind == "knowledge"]
    assert len(actions) == 1
    assert actions[0].target == ".aspis/knowledge/python.md"
    assert actions[0].op == "copy"


# --------------------------------------------------------------------------- #
# Story 2 — per-runtime placement is capability-gated
# --------------------------------------------------------------------------- #


def test_capability_gating_drops_unsupported_kind(tmp_path, monkeypatch) -> None:
    root = tmp_path / "catalog"
    (root / "skills" / "scope").mkdir(parents=True)
    (root / "skills" / "scope" / "SKILL.md").write_text("x", encoding="utf-8")
    profile = Profile(name="p", runtimes=["opencode", "claude"], skills=["skills/scope"])

    class _NoSkills:
        def supports(self, kind: str) -> bool:
            return kind != "skills"

    monkeypatch.setattr(export, "get_adapter", lambda runtime: _NoSkills())

    plan = plan_export(root, profile)

    assert not [a for a in plan.actions if a.kind == "skills"]
    assert any("unsupported" in s for s in plan.skipped_by_scope)
