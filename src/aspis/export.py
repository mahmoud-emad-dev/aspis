"""Export — plan and write a project's runtime assets from a profile.

Given a resolved profile and the bundled catalog, the planner computes what to
copy or render per runtime (dry-run, no writes); the writer performs it. Agents
and commands are rendered through the runtime adapters; skills/templates/hooks/
scripts are copied. Runtime-independent assets (templates/hooks/scripts) land
once under ``.asps/``; runtime assets land under each ``.<runtime>/``.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from aspis import transform
from aspis.catalog import split_frontmatter
from aspis.profiles import Profile

# Asset kinds placed per runtime; everything else lands once under the brain.
_RUNTIME_KINDS = ("agents", "skills", "commands")


@dataclass(frozen=True)
class ExportAction:
    """One planned copy/render step."""

    kind: str
    runtime: str
    source: Path
    target: str
    op: str  # render-agent | render-command | copy


@dataclass
class ExportPlan:
    """The full set of actions plus anything that could not be exported."""

    actions: list[ExportAction] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    skipped_by_scope: list[str] = field(default_factory=list)


def _target_and_op(kind: str, runtime: str, rel: str) -> tuple[str, str]:
    """Map an asset kind to its project-relative target path and write op."""
    name = Path(rel).name
    mapping = {
        "agents": (f".{runtime}/agents/{name}", "render-agent"),
        "commands": (f".{runtime}/commands/{name}", "render-command"),
        "skills": (f".{runtime}/skills/{name}", "copy"),
        "templates": (f".asps/templates/{name}", "copy"),
        "hooks": (f".asps/hooks/{name}", "copy"),
        "scripts": (f".asps/scripts/{name}", "copy"),
    }
    return mapping[kind]


def _is_project_only(source: Path, kind: str) -> bool:
    """True if an agent/command is scoped to the factory only (never exported)."""
    if kind not in ("agents", "commands") or not source.is_file():
        return False
    frontmatter, _ = split_frontmatter(source.read_text(encoding="utf-8"))
    return frontmatter.get("export_scope") == "project-only"


def plan_export(catalog_root: Path, profile: Profile) -> ExportPlan:
    """Compute the export actions for *profile* against *catalog_root* (no writes)."""
    plan = ExportPlan()
    for kind, rel in profile.assets():
        source = catalog_root / rel
        if not source.exists():
            plan.missing.append(rel)
            continue
        if _is_project_only(source, kind):
            plan.skipped_by_scope.append(rel)
            continue

        runtimes = profile.runtimes if kind in _RUNTIME_KINDS else ("",)
        for runtime in runtimes:
            target, op = _target_and_op(kind, runtime, rel)
            plan.actions.append(ExportAction(kind, runtime, source, target, op))
    return plan


def write_export(
    plan: ExportPlan, target_root: Path, *, force: bool = False, write: bool = False
) -> list[str]:
    """Perform (or, with ``write=False``, just describe) the planned actions."""
    performed: list[str] = []
    for action in plan.actions:
        destination = target_root / action.target
        if destination.exists() and not force:
            performed.append(f"skip (exists): {action.target}")
            continue

        performed.append(f"{action.op}: {action.target}")
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _apply(action, destination)
    return performed


def _apply(action: ExportAction, destination: Path) -> None:
    """Execute a single export action against *destination*."""
    if action.op == "render-agent":
        text = transform.render_agent(action.source.read_text(encoding="utf-8"), action.runtime)
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.op == "render-command":
        text = transform.render_command(action.source.read_text(encoding="utf-8"), action.runtime)
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.source.is_dir():
        shutil.copytree(action.source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(action.source, destination)
