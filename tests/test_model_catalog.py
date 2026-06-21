"""Tests for the F-010 model data files: catalog, capability taxonomy, provider registry.

These are the single source of truth the resolver builds on, so the schema is pinned:
canonical ids carry no provider prefix, scores cover the four capabilities, tiers are
valid, and every capability's preferred tier and every provider entry is well-formed.
"""

from __future__ import annotations

import yaml

from aspis import resources

_TIERS = {"cheap", "standard", "deep"}
_COST_TIERS = _TIERS | {"frontier"}
_CAPS = {"planning", "implementation", "review", "reasoning"}
_CONFIDENCE = {"low", "medium", "high"}


def _config(name: str) -> dict:
    return yaml.safe_load((resources.catalog_dir() / "config" / name).read_text(encoding="utf-8"))


def test_model_catalog_schema() -> None:
    models = _config("model_catalog.yaml")["models"]
    assert models, "catalog must list models"
    for model_id, m in models.items():
        # Canonical id: provider-neutral, never a runtime/provider-prefixed string.
        assert "/" not in model_id, f"{model_id} looks runtime-specific (has '/')"
        assert m["provider"] and m["family"]
        assert isinstance(m["context_window"], int) and m["context_window"] > 0
        assert _CAPS <= set(m["scores"]), f"{model_id} missing capability scores"
        assert all(1 <= m["scores"][c] <= 10 for c in _CAPS)
        assert m["cost_tier"] in _COST_TIERS
        assert {"in", "out"} <= set(m["pricing"])
        assert m["limits"]["max_task_complexity"] in {"low", "medium", "high"}
        assert m["confidence"] in _CONFIDENCE


def test_capabilities_schema() -> None:
    caps = _config("capabilities.yaml")["capabilities"]
    assert caps
    for name, c in caps.items():
        assert c["preferred_tier"] in _TIERS, f"{name} preferred_tier not a real tier"


def test_providers_schema() -> None:
    provs = _config("providers.yaml")["providers"]
    assert provs
    for pid, p in provs.items():
        assert p["runtimes"], f"{pid} names no runtime"
        assert p["detect"] in {"auth_json", "claude_settings"}
        assert isinstance(p["prefer"], int)
        assert p["naming"]


def test_tier_map_references_catalog() -> None:
    # Single source of truth: every runtime/tier value in models.yaml MUST be a
    # canonical id defined in the catalog (so the map never drifts from the catalog).
    catalog = set(_config("model_catalog.yaml")["models"])
    tier_map = _config("models.yaml")
    for runtime, tiers in tier_map.items():
        for tier, model_id in tiers.items():
            assert model_id in catalog, f"{runtime}.{tier} -> {model_id} not in catalog"


def test_free_to_test_default_exists() -> None:
    # A brand-new user must have a $0 default to run end-to-end (FR-011).
    free = _config("model_catalog.yaml")["free_to_test"]
    assert free["overall_default"]
    assert _TIERS <= set(free) | {"overall_default"}
