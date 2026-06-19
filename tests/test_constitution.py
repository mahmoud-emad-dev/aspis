"""Tests for the architecture-constitution rule asset + machine checklist."""

from __future__ import annotations

import yaml

from aspis import resources
from aspis.profiles import load_profile

_ROLES = {"planning", "build", "review"}


def test_checklist_is_well_formed() -> None:
    path = resources.catalog_dir() / "config" / "constitution-checks.yaml"
    checks = yaml.safe_load(path.read_text(encoding="utf-8"))["checks"]
    assert checks
    seen: set[str] = set()
    for check in checks:
        assert check["id"] and check["id"] not in seen
        seen.add(check["id"])
        assert check["statement"].strip()
        assert check["review_question"].strip()
        roles = set(check["enforced_by"])
        assert roles and roles <= _ROLES, f"{check['id']} has bad roles: {roles}"


def test_base_profile_ships_the_constitution() -> None:
    base = load_profile(resources.data_dir() / "profiles" / "base.yaml")
    assert "rules/architecture-constitution.md" in base.rules
    assert "config/constitution-checks.yaml" in base.config

    catalog = resources.catalog_dir()
    assert (catalog / "rules" / "architecture-constitution.md").exists()
    assert (catalog / "config" / "constitution-checks.yaml").exists()
