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

from aspis import assetkinds, project, transform
from aspis.catalog import split_frontmatter
from aspis.profiles import Profile
from aspis.runtimes import get_adapter


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
    catalog_root: Path | None = None  # carried so the writer can emit runtime hooks


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
    plan = ExportPlan(catalog_root=catalog_root)
    for kind, rel in profile.assets():
        source = catalog_root / rel
        if not source.exists():
            plan.missing.append(rel)
            continue
        scope, runtime_lock = _asset_meta(source, kind)
        if scope == "project-only":
            plan.skipped_by_scope.append(rel)
            continue

        per_runtime = assetkinds.is_per_runtime(kind)
        runtimes = profile.runtimes if per_runtime else ("",)
        for runtime in runtimes:
            # Honour runtime-lock: a locked asset skips runtimes outside its set.
            if runtime_lock and runtime not in runtime_lock:
                plan.skipped_by_scope.append(f"{rel} ({runtime})")
                continue
            # Honour the runtime capability model: drop a kind a runtime can't accept.
            if per_runtime and not get_adapter(runtime).supports(kind):
                plan.skipped_by_scope.append(f"{rel} ({runtime}: unsupported)")
                continue
            target = assetkinds.target(kind, runtime, rel)
            plan.actions.append(ExportAction(kind, runtime, source, target, assetkinds.op(kind)))
    return plan


def write_export(
    plan: ExportPlan, target_root: Path, *, force: bool = False, write: bool = False
) -> list[str]:
    """Perform (or, with ``write=False``, just describe) the planned actions."""
    # The target's own settings override model routing (tier maps, per-agent pins).
    project_config = project.load_project_config(target_root)
    performed: list[str] = []
    for action in plan.actions:
        destination = target_root / action.target
        if destination.exists() and not force:
            performed.append(f"skip (exists): {action.target}")
            continue

        performed.append(f"{action.op}: {action.target}")
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _apply(action, destination, project_config)

    # Each runtime emits its own scope-guard wiring (adapter-owned placement).
    if plan.catalog_root is not None:
        for runtime in sorted({action.runtime for action in plan.actions if action.runtime}):
            performed.extend(
                get_adapter(runtime).emit_runtime_hooks(
                    plan.catalog_root, target_root, force=force, write=write
                )
            )
    return performed


def _apply(action: ExportAction, destination: Path, project_config: dict) -> None:
    """Execute a single export action against *destination*."""
    if action.op == "render-agent":
        text = transform.render_agent(
            action.source.read_text(encoding="utf-8"),
            action.runtime,
            project_config=project_config,
        )
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.op == "render-command":
        text = transform.render_command(action.source.read_text(encoding="utf-8"), action.runtime)
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.source.is_dir():
        shutil.copytree(action.source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(action.source, destination)
