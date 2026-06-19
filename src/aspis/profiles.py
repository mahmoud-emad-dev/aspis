"""Profiles — data-driven selection of which catalog assets a project receives.

Purpose:
    A profile is a YAML file listing assets by kind plus the target runtimes.
    The shared ``base`` profile is merged under every profile, so a profile only
    lists its extras. Selection is pure data — adding or removing assets, and
    even adding a brand-new asset *kind*, never touches code: any top-level list
    key in the YAML becomes a selected kind.

Responsibilities:
    - Parse a profile (any kind key) into a kind→paths mapping.
    - Expose the selected assets as ``(kind, path)`` pairs and per-kind lists.
    - Merge a base profile under an overlay (concatenate + dedupe per kind).

Does Not:
    - Decide where an asset is placed or how it is written — that is the asset-kind
      registry's job (:mod:`aspis.assetkinds`), read by :mod:`aspis.export`.

Used By:
    export.py, operations/init.py
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

#: Top-level profile keys that are settings, not asset-kind lists.
_RESERVED = {"name", "runtimes", "include_all", "selected"}


class Profile(BaseModel):
    """A named selection of catalog assets for export."""

    name: str
    runtimes: list[str] = Field(default_factory=lambda: ["opencode"])
    include_all: bool = False
    #: Selected assets keyed by kind, e.g. ``{"agents": [...], "skills": [...]}``.
    selected: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _gather_kinds(cls, data: object) -> object:
        """Fold every top-level list key (any kind) into ``selected``.

        Keeps the natural YAML/kwarg form (``agents: [...]``) while letting the
        kind set stay open — a new kind needs no new field here.
        """
        if not isinstance(data, dict):
            return data
        data = dict(data)
        selected: dict[str, list[str]] = dict(data.get("selected") or {})
        for key in [k for k in data if k not in _RESERVED and isinstance(data[k], list)]:
            selected[key] = data.pop(key)
        data["selected"] = selected
        return data

    def __getattr__(self, item: str) -> list[str]:
        """Per-kind convenience: ``profile.agents`` → ``selected["agents"]``.

        Only fires for names pydantic didn't resolve (i.e. asset kinds); private
        and model attributes fall through to pydantic's own handling.
        """
        if not item.startswith("_") and "selected" in self.__dict__:
            return self.__dict__["selected"].get(item, [])
        return super().__getattr__(item)

    def assets(self) -> list[tuple[str, str]]:
        """Return ``(kind, path)`` for every selected asset, in declared order."""
        return [(kind, path) for kind, paths in self.selected.items() for path in paths]


def load_profile(path: Path) -> Profile:
    """Load and validate a profile from a YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Profile(**data)


def merge(base: Profile, overlay: Profile) -> Profile:
    """Combine *base* assets with *overlay* (overlay wins for name/runtimes/flags).

    Asset lists are concatenated base-first and de-duplicated per kind, so a
    profile only needs to list what it adds on top of the shared base.
    """
    selected: dict[str, list[str]] = {}
    for kind in [*base.selected, *overlay.selected]:
        combined = [*base.selected.get(kind, []), *overlay.selected.get(kind, [])]
        selected[kind] = list(dict.fromkeys(combined))  # dedup, preserve order
    return Profile(
        name=overlay.name,
        runtimes=overlay.runtimes,
        include_all=overlay.include_all,
        selected=selected,
    )
