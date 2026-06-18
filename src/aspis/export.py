"""Export — plan and write a project's runtime assets from a profile.

Given a resolved profile and the bundled catalog, the planner computes what to
copy or render per runtime (dry-run, no writes); the writer performs it. Agents
and commands are rendered through the runtime adapters; skills/templates/hooks/
scripts are copied. Runtime-independent assets (templates/hooks/scripts) land
once under ``.aspis/``; runtime assets land under each ``.<runtime>/``.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from aspis import transform
from aspis.catalog import split_frontmatter
from aspis.constants import BRAIN_DIR
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
        "templates": (f"{BRAIN_DIR}/templates/{name}", "copy"),
        "hooks": (f"{BRAIN_DIR}/hooks/{name}", "copy"),
        "scripts": (f"{BRAIN_DIR}/scripts/{name}", "copy"),
        "rules": (f"{BRAIN_DIR}/rules/{name}", "copy"),
    }
    return mapping[kind]


def _asset_meta(source: Path, kind: str) -> tuple[str, set[str]]:
    """Return ``(export_scope, runtime_lock)`` from an agent/command's frontmatter.

    ``runtime_lock`` is the set of runtimes the asset is restricted to; an empty
    set means "all runtimes". Non-renderable kinds carry no scope metadata.
    """
    if kind not in ("agents", "commands") or not source.is_file():
        return "all", set()
    frontmatter, _ = split_frontmatter(source.read_text(encoding="utf-8"))
    scope = frontmatter.get("export_scope", "all")
    return scope, set(frontmatter.get("runtimes", []))


def plan_export(catalog_root: Path, profile: Profile) -> ExportPlan:
    """Compute the export actions for *profile* against *catalog_root* (no writes)."""
    plan = ExportPlan()
    for kind, rel in profile.assets():
        source = catalog_root / rel
        if not source.exists():
            plan.missing.append(rel)
            continue
        scope, runtime_lock = _asset_meta(source, kind)
        if scope == "project-only":
            plan.skipped_by_scope.append(rel)
            continue

        runtimes = profile.runtimes if kind in _RUNTIME_KINDS else ("",)
        for runtime in runtimes:
            # Honour runtime-lock: a locked asset skips runtimes outside its set.
            if runtime_lock and runtime not in runtime_lock:
                plan.skipped_by_scope.append(f"{rel} ({runtime})")
                continue
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
