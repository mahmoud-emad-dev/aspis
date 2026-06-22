"""Locate files bundled inside the aspis package (templates, profiles, catalog).

One place resolves package data, so callers never hardcode paths. Uses
importlib.resources so it works both from a source checkout and an installed
wheel.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import yaml


def data_dir() -> Path:
    """Return the path to the package's bundled ``data/`` directory (config)."""
    return Path(str(files("aspis"))) / "data"


def catalog_dir() -> Path:
    """Return the catalog root — the single home for every target-bound asset.

    Agents, skills, commands, templates, hooks, and scripts all live under here,
    one folder per category, so init/export have one place to resolve from.
    """
    return data_dir() / "catalog"


def template(name: str) -> str:
    """Return the text of a bundled output-shape template under ``catalog/templates/``.

    Templates are the shapes agents and scripts fill so an output's format is never
    invented (planning artifacts, task/feature reports, review/test results). *name*
    may include a category sub-path, e.g. ``planning/SPEC.md`` or ``report/task.md``.
    """
    return (catalog_dir() / "templates" / name).read_text(encoding="utf-8")


def scaffold(name: str) -> str:
    """Return the text of a bundled scaffold file under ``catalog/scaffold/``.

    Scaffold files are generated once by the system at init/bootstrap (the runtime
    root guides ``AGENTS.md``/``CLAUDE.md``, ``gitignore``, the ``purposes.json`` seed)
    — project agents never author them, so they are kept apart from agent templates.
    """
    return (catalog_dir() / "scaffold" / name).read_text(encoding="utf-8")


def _brain_spec() -> dict:
    """Parsed ``data/brain.yaml`` — the canonical .aspis/ structure."""
    return yaml.safe_load((data_dir() / "brain.yaml").read_text(encoding="utf-8")) or {}


def brain_dirs() -> list[str]:
    """Brain dirs scaffolded AND filled at init — the ``scaffold`` set in brain.yaml.

    Excludes the on-demand dirs (features/current/research): those are created by
    their own writer when the first file lands, so the brain never carries an empty
    ``.gitkeep``-only folder. (``dirs`` is honoured for backward compatibility.)
    """
    spec = _brain_spec()
    return list(spec.get("scaffold") or spec.get("dirs", []))


def on_demand_dirs() -> list[str]:
    """Brain dirs created lazily by their writer (features, current, research)."""
    return list(_brain_spec().get("on_demand", []))


def canonical_brain_subdirs() -> set[str]:
    """Every legitimate ``.aspis/`` subfolder name (scaffold + on-demand).

    The allow-list the bootstrap structure check uses to reject any invented or
    stray folder, so the brain layout stays consistent across every project.
    """
    return {d.split("/", 1)[1] for d in (*brain_dirs(), *on_demand_dirs()) if "/" in d}


def config(name: str, root: Path | None = None) -> dict:
    """Load a ``config/<name>`` YAML file as a dict (``{}`` if empty), project-first.

    One resolver for every config file (``models.yaml``, ``providers.yaml``,
    ``model_catalog.yaml``, ``capabilities.yaml``). When *root* is an ASPIS project and
    it carries its own ``.aspis/config/<name>``, that copy wins — so a project can edit
    its exported model config and have it honoured; otherwise the bundled package copy
    (the global install's reference data) is used.
    """
    if root is not None:
        local = root / ".aspis" / "config" / name
        if local.is_file():
            return yaml.safe_load(local.read_text(encoding="utf-8")) or {}
    data = yaml.safe_load((catalog_dir() / "config" / name).read_text(encoding="utf-8"))
    return data or {}


def model_map(runtime: str, root: Path | None = None) -> dict[str, str]:
    """Return the tier->model map for *runtime* (project ``models.yaml`` first, else bundled)."""
    return dict(config("models.yaml", root).get(runtime, {}))


def runtime_defs() -> dict[str, dict]:
    """Discover every runtime definition under ``data/runtimes/*.yaml``.

    The single source of truth for *what runtimes exist* and their declarative facts
    (detect exe, run command, dir, root_guide, capabilities). Adding a runtime is
    dropping a YAML file here — no hardcoded list anywhere (Discovery over Registration).
    """
    directory = data_dir() / "runtimes"
    defs: dict[str, dict] = {}
    if directory.is_dir():
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            name = data.get("name", path.stem)
            defs[name] = data
    return defs


def runtime_def(name: str) -> dict:
    """Return one runtime's definition (``{}`` if there is no file for it)."""
    return runtime_defs().get(name, {})
