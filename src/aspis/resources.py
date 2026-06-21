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


def brain_dirs() -> list[str]:
    """Return the brain skeleton directories from ``data/brain.yaml``."""
    data = yaml.safe_load((data_dir() / "brain.yaml").read_text(encoding="utf-8")) or {}
    return list(data.get("dirs", []))


def config(name: str) -> dict:
    """Load a catalog ``config/<name>`` YAML file as a dict (``{}`` if empty).

    One resolver for every bundled config file (``models.yaml``, ``providers.yaml``,
    ``model_catalog.yaml``, ``capabilities.yaml``), so callers never rebuild the path.
    """
    data = yaml.safe_load((catalog_dir() / "config" / name).read_text(encoding="utf-8"))
    return data or {}


def model_map(runtime: str) -> dict[str, str]:
    """Return the global tier->model map for *runtime* from ``config/models.yaml``."""
    return dict(config("models.yaml").get(runtime, {}))
