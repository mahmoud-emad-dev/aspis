"""Profiles — data-driven selection of which catalog assets a project receives.

A profile is a YAML file listing assets by kind plus the target runtimes. The
shared ``base`` profile is merged under every profile, so a profile only lists
its extras. Selection is pure data — adding or removing assets never touches
code.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import yaml
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """A named selection of catalog assets for export."""

    name: str
    runtimes: list[str] = Field(default_factory=lambda: ["opencode"])
    include_all: bool = False
    agents: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    templates: list[str] = Field(default_factory=list)
    hooks: list[str] = Field(default_factory=list)
    scripts: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    config: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)

    #: The asset list fields, in stable export order.
    ASSET_KINDS: ClassVar[tuple[str, ...]] = (
        "agents",
        "skills",
        "commands",
        "templates",
        "hooks",
        "scripts",
        "rules",
        "config",
        "workflows",
    )

    def assets(self) -> list[tuple[str, str]]:
        """Return ``(kind, path)`` for every selected asset, in a stable order."""
        return [(kind, path) for kind in self.ASSET_KINDS for path in getattr(self, kind)]


def load_profile(path: Path) -> Profile:
    """Load and validate a profile from a YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Profile(**data)


def merge(base: Profile, overlay: Profile) -> Profile:
    """Combine *base* assets with *overlay* (overlay wins for name/runtimes/flags).

    Asset lists are concatenated base-first and de-duplicated, so a profile only
    needs to list what it adds on top of the shared base.
    """
    merged: dict = {
        "name": overlay.name,
        "runtimes": overlay.runtimes,
        "include_all": overlay.include_all,
    }
    for kind in Profile.ASSET_KINDS:
        combined = [*getattr(base, kind), *getattr(overlay, kind)]
        merged[kind] = list(dict.fromkeys(combined))  # dedup, preserve order
    return Profile(**merged)
