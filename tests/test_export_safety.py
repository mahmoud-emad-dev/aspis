"""Export-safety guarantees (F-021).

Two invariants a re-export must never violate on an already-live project:

1. **Models are frozen.** ``aspis export`` (``preserve_models=True``) keeps each live
   agent's already-baked ``model:`` line, even when current config would resolve a
   different model. ``aspis models --apply`` (``preserve_models=False``) is the one path
   that may re-bake.
2. **Bootstrap leaves no trace.** Once the manifest says the project is bootstrapped, a
   re-export strips the first-run gate + ``bootstrap`` delegate from the rendered
   project-lead, skips the transient onboarding package, and removes any package residue.
"""

from __future__ import annotations

import re
from pathlib import Path

from aspis import manifest
from aspis.export import plan_export, write_export
from aspis.profiles import Profile

_GATE = (
    "<!-- ASPIS:BOOTSTRAP-GATE:START -->\n"
    "First action: if NOT bootstrapped, delegate to the `bootstrap` agent.\n"
    "<!-- ASPIS:BOOTSTRAP-GATE:END -->\n"
)
PROJECT_LEAD = (
    "---\n"
    "name: project-lead\n"
    "description: entry point\n"
    "mode: primary\n"
    "model: standard\n"
    "delegates:\n"
    "  - bootstrap\n"
    "  - planning-lead\n"
    "---\n\n"
    "## How you work\n\n" + _GATE + "\nClassify intent then delegate.\n"
)
BOOTSTRAP_AGENT = (
    "---\nname: bootstrap\ndescription: onboarding\nmode: primary\nmodel: standard\n---\n\nbody\n"
)
PLANNING_LEAD = (
    "---\nname: planning-lead\ndescription: planner\nmode: primary\nmodel: deep\n---\n\nbody\n"
)


def _catalog(tmp_path: Path) -> Path:
    """A catalog with the bootstrap package: project-lead (gated), bootstrap, onboarding."""
    root = tmp_path / "catalog"
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "project-lead.md").write_text(PROJECT_LEAD, encoding="utf-8")
    (root / "agents" / "bootstrap.md").write_text(BOOTSTRAP_AGENT, encoding="utf-8")
    (root / "agents" / "planning-lead.md").write_text(PLANNING_LEAD, encoding="utf-8")
    skill = root / "skills" / "project-onboarding"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# onboarding\n", encoding="utf-8")
    (root / "workflows").mkdir()
    (root / "workflows" / "bootstrap.md").write_text("# bootstrap workflow\n", encoding="utf-8")
    return root


def _profile() -> Profile:
    return Profile(
        name="p",
        runtimes=["opencode"],
        agents=["agents/project-lead.md", "agents/bootstrap.md", "agents/planning-lead.md"],
        skills=["skills/project-onboarding"],
        workflows=["workflows/bootstrap.md"],
    )


def _model_line(text: str) -> str:
    return next(line for line in text.splitlines() if line.startswith("model:"))


# --- 1. model preservation ----------------------------------------------------


def _freeze_model(live: Path, model: str) -> None:
    """Rewrite *live*'s ``model:`` line to *model* — stands in for ``models --apply``."""
    text = re.sub(r"^model:.*$", f"model: {model}", live.read_text(encoding="utf-8"), flags=re.M)
    live.write_text(text, encoding="utf-8")


def test_export_preserves_a_live_baked_model(tmp_path) -> None:
    cat, target = _catalog(tmp_path), tmp_path / "proj"
    write_export(plan_export(cat, _profile()), target, write=True)
    live = target / ".opencode/agents/planning-lead.md"
    _freeze_model(live, "my-frozen-model")

    # A forced re-export with preserve_models must keep the frozen model, not re-resolve.
    write_export(
        plan_export(cat, _profile()), target, force=True, write=True, preserve_models=True
    )
    assert _model_line(live.read_text(encoding="utf-8")) == "model: my-frozen-model"


def test_models_apply_path_rebakes_when_not_preserving(tmp_path) -> None:
    cat, target = _catalog(tmp_path), tmp_path / "proj"
    write_export(plan_export(cat, _profile()), target, write=True)
    live = target / ".opencode/agents/planning-lead.md"
    resolved = _model_line(live.read_text(encoding="utf-8"))
    _freeze_model(live, "my-frozen-model")

    # Without preserve_models (the `models --apply` path), the model is re-resolved.
    write_export(
        plan_export(cat, _profile()), target, force=True, write=True, preserve_models=False
    )
    assert _model_line(live.read_text(encoding="utf-8")) == resolved


# --- 2. bootstrap-aware export -------------------------------------------------


def test_pre_bootstrap_export_ships_the_gate_and_package(tmp_path) -> None:
    cat, target = _catalog(tmp_path), tmp_path / "proj"
    write_export(plan_export(cat, _profile()), target, write=True)

    lead = (target / ".opencode/agents/project-lead.md").read_text(encoding="utf-8")
    assert "BOOTSTRAP-GATE" in lead
    assert "bootstrap: allow" in lead  # the delegate rendered as a task permission
    assert (target / ".opencode/agents/bootstrap.md").is_file()
    assert (target / ".opencode/skills/project-onboarding").is_dir()
    assert (target / ".aspis/workflows/bootstrap.md").is_file()


def test_live_export_strips_gate_skips_and_removes_package(tmp_path) -> None:
    cat, target = _catalog(tmp_path), tmp_path / "proj"
    write_export(plan_export(cat, _profile()), target, write=True)
    manifest.save(target, {"bootstrapped": True})

    performed = write_export(
        plan_export(cat, _profile()), target, force=True, write=True, preserve_models=True
    )

    lead = (target / ".opencode/agents/project-lead.md").read_text(encoding="utf-8")
    assert "BOOTSTRAP-GATE" not in lead  # gate prose stripped
    assert "bootstrap" not in lead  # delegate task-perm AND prose mention both gone
    # The transient package is skipped (not re-written) and any residue is removed.
    assert any("skip (bootstrap done)" in line for line in performed)
    assert any("remove (bootstrap done)" in line for line in performed)
    assert not (target / ".opencode/agents/bootstrap.md").exists()
    assert not (target / ".opencode/skills/project-onboarding").exists()
    assert not (target / ".aspis/workflows/bootstrap.md").exists()


def test_live_export_keeps_non_bootstrap_agents(tmp_path) -> None:
    cat, target = _catalog(tmp_path), tmp_path / "proj"
    write_export(plan_export(cat, _profile()), target, write=True)
    manifest.save(target, {"bootstrapped": True})

    write_export(plan_export(cat, _profile()), target, force=True, write=True, preserve_models=True)
    # A normal lead is untouched by the bootstrap machinery.
    assert (target / ".opencode/agents/planning-lead.md").is_file()
