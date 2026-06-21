"""Tests for the F-010 resolver (T-08): precedence, hard limits, translation, fallback.

``resolve`` layers the F-010 behaviour on top of ``effective_model``: a machine-wide
``~/.aspis`` override rung below the project, hard-limit escalation (FR-007), and
translation of the canonical id into a runtime string via the adapter + inventory —
falling back to the canonical id (today's output) when nothing is detected.
"""

from __future__ import annotations

from aspis import models

_GLOBAL = {"cheap": "cheapM", "standard": "stdM", "deep": "deepM"}
_CATALOG = {
    "cheapM": {"limits": {"max_task_complexity": "low"}},
    "stdM": {"limits": {"max_task_complexity": "medium"}},
    "deepM": {"limits": {"max_task_complexity": "high"}},
}


def test_resolve_with_no_translate_is_canonical() -> None:
    # Bare resolve == effective_model precedence (the graceful, detection-free path).
    assert models.resolve("opencode", "x", "deep", global_map=_GLOBAL) == "deepM"


def test_project_override_beats_global_beats_tier_map() -> None:
    project = {"models": {"opencode": {"deep": "P"}}}
    glob = {"models": {"opencode": {"deep": "G"}}}
    # tier map only
    assert models.resolve("opencode", "x", "deep", global_map=_GLOBAL) == "deepM"
    # global ~/.aspis rung beats the tier map
    assert models.resolve("opencode", "x", "deep", global_map=_GLOBAL, global_config=glob) == "G"
    # project override beats the global rung
    got = models.resolve(
        "opencode", "x", "deep", global_map=_GLOBAL, project_config=project, global_config=glob
    )
    assert got == "P"


def test_per_runtime_agent_pin_routes_differently_per_runtime() -> None:
    # The headline flexibility: one agent, a different model on each runtime.
    cfg = {
        "runtimes": {
            "claude": {"agents": {"build-lead": "sonnet"}},
            "opencode": {"agents": {"build-lead": "deep"}},  # a tier here
        }
    }
    assert (
        models.resolve("claude", "build-lead", "deep", global_map=_GLOBAL, project_config=cfg)
        == "sonnet"  # model-id pin passes through
    )
    assert (
        models.resolve("opencode", "build-lead", "cheap", global_map=_GLOBAL, project_config=cfg)
        == "deepM"  # tier pin maps through the tier table
    )


def test_per_runtime_agent_pin_beats_per_agent_pin() -> None:
    cfg = {
        "agents": {"reviewer": "cheap"},  # all-runtime pin
        "runtimes": {"opencode": {"agents": {"reviewer": "glm-5.1"}}},  # more specific
    }
    assert (
        models.resolve("opencode", "reviewer", "deep", global_map=_GLOBAL, project_config=cfg)
        == "glm-5.1"  # the per-runtime-agent pin wins
    )
    assert (
        models.resolve("claude", "reviewer", "deep", global_map=_GLOBAL, project_config=cfg)
        == "cheapM"  # claude has no runtime-agent pin -> falls back to the per-agent pin
    )


def test_runtimes_block_can_override_a_tier() -> None:
    cfg = {"runtimes": {"opencode": {"models": {"deep": "X"}}}}
    assert models.resolve("opencode", "a", "deep", global_map=_GLOBAL, project_config=cfg) == "X"


def test_by_capability_routes_every_agent_of_that_capability() -> None:
    # The scalable middle layer: set review once, every review agent inherits it.
    cfg = {"by_capability": {"review": "rev-model"}}
    got = models.resolve(
        "opencode",
        "reviewer",
        "deep",
        global_map=_GLOBAL,
        project_config=cfg,
        agent_capability="review",
    )
    assert got == "rev-model"
    # an agent of a different capability is unaffected
    other = models.resolve(
        "opencode",
        "builder",
        "deep",
        global_map=_GLOBAL,
        project_config=cfg,
        agent_capability="implementation",
    )
    assert other == "deepM"


def test_per_agent_pin_beats_by_capability_beats_runtime_capability() -> None:
    cfg = {
        "by_capability": {"review": "global-cap"},
        "agents": {"reviewer": "agent-pin"},
        "runtimes": {"opencode": {"by_capability": {"review": "rt-cap"}}},
    }
    # per-agent pin wins
    assert (
        models.resolve(
            "opencode",
            "reviewer",
            "deep",
            global_map=_GLOBAL,
            project_config=cfg,
            agent_capability="review",
        )
        == "agent-pin"
    )
    # without an agent pin, the runtime capability beats the global capability
    cfg2 = {
        "by_capability": {"review": "global-cap"},
        "runtimes": {"opencode": {"by_capability": {"review": "rt-cap"}}},
    }
    assert (
        models.resolve(
            "opencode",
            "x",
            "deep",
            global_map=_GLOBAL,
            project_config=cfg2,
            agent_capability="review",
        )
        == "rt-cap"
    )


def test_agent_pin_in_project_wins_over_global_pin() -> None:
    project = {"agents": {"reviewer": "cheap"}}
    glob = {"agents": {"reviewer": "deep"}}
    got = models.resolve(
        "opencode",
        "reviewer",
        "standard",
        global_map=_GLOBAL,
        project_config=project,
        global_config=glob,
    )
    assert got == "cheapM"  # project pin wins


def test_translate_is_applied_with_inventory() -> None:
    captured: dict = {}

    def fake_translate(canonical_id, inventory):
        captured["canonical"] = canonical_id
        captured["inventory"] = inventory
        return f"opencode-go/{canonical_id}"

    sentinel = object()
    got = models.resolve(
        "opencode", "x", "deep", global_map=_GLOBAL, translate=fake_translate, inventory=sentinel
    )
    assert got == "opencode-go/deepM"
    assert captured == {"canonical": "deepM", "inventory": sentinel}


def test_within_limits() -> None:
    assert models.within_limits("cheapM", "low", _CATALOG) is True
    assert models.within_limits("cheapM", "high", _CATALOG) is False
    assert models.within_limits("deepM", "high", _CATALOG) is True
    # unknown model -> not blocked (graceful)
    assert models.within_limits("mystery", "high", _CATALOG) is True


def test_limits_escalate_to_cheapest_model_that_fits() -> None:
    # A cheap agent on a high-complexity task bumps up to the cheapest model that clears it.
    got = models.resolve(
        "opencode", "x", "cheap", global_map=_GLOBAL, catalog=_CATALOG, required_complexity="high"
    )
    assert got == "deepM"  # cheapM(low)->stdM(medium)->deepM(high) is the first that fits


def test_limits_leave_a_fitting_model_untouched() -> None:
    got = models.resolve(
        "opencode",
        "x",
        "standard",
        global_map=_GLOBAL,
        catalog=_CATALOG,
        required_complexity="medium",
    )
    assert got == "stdM"  # already clears medium -> no bump


# --- task sizing (FR-008 / SC-005) -------------------------------------------

_MODES = {
    "vibe": {"task_size": "large"},
    "mvp": {"task_size": "medium"},
    "production": {"task_size": "small"},
}
_SIZE_CATALOG = {"weak": {"cost_tier": "cheap"}, "strong": {"cost_tier": "frontier"}}
_ORDER = ("small", "medium", "large")


def test_cheap_model_gets_strictly_smaller_tasks_than_frontier() -> None:
    # SC-005: under the SAME mode, a cheap-capability model is sized smaller than a frontier one.
    for mode in ("vibe", "mvp", "production"):
        cheap = models.effective_task_size(mode, "weak", catalog=_SIZE_CATALOG, modes=_MODES)
        frontier = models.effective_task_size(mode, "strong", catalog=_SIZE_CATALOG, modes=_MODES)
        assert _ORDER.index(cheap) < _ORDER.index(frontier), mode


_CAP_CATALOG = {
    "flashM": {
        "cost_tier": "cheap",
        "pricing": {"in": 0.1},
        "scores": {"review": 7, "implementation": 8},
    },
    "proM": {
        "cost_tier": "standard",
        "pricing": {"in": 0.5},
        "scores": {"review": 9, "implementation": 9},
    },
    "opusM": {
        "cost_tier": "frontier",
        "pricing": {"in": 5.0},
        "scores": {"review": 10, "implementation": 10},
    },
}
_AVAIL = ["flashM", "proM", "opusM"]


def test_best_available_model_is_capability_aware_and_cost_conscious() -> None:
    # review, deep budget: opusM(10) is best but proM(9) is within tolerance and cheaper -> proM.
    assert (
        models.best_available_model("review", "deep", catalog=_CAP_CATALOG, available_ids=_AVAIL)
        == "proM"
    )
    # implementation, cheap budget: only the cheap-cost flashM qualifies.
    assert (
        models.best_available_model(
            "implementation", "cheap", catalog=_CAP_CATALOG, available_ids=_AVAIL
        )
        == "flashM"
    )
    # implementation, standard budget: flashM(8) is within 1 of proM(9) and cheaper -> flashM.
    assert (
        models.best_available_model(
            "implementation", "standard", catalog=_CAP_CATALOG, available_ids=_AVAIL
        )
        == "flashM"
    )


def test_best_available_model_falls_back_and_handles_empty() -> None:
    # Only a frontier model available but a cheap budget -> ignore the budget, don't return None.
    assert (
        models.best_available_model(
            "review", "cheap", catalog=_CAP_CATALOG, available_ids=["opusM"]
        )
        == "opusM"
    )
    assert models.best_available_model("review", "deep", catalog={}, available_ids=["x"]) is None


def test_effective_task_size_falls_back_safely() -> None:
    # Unknown mode -> medium baseline; unknown model -> no shift; never raises.
    assert models.effective_task_size("???", "weak", catalog=_SIZE_CATALOG, modes=_MODES) == "small"
    assert (
        models.effective_task_size("mvp", "mystery", catalog=_SIZE_CATALOG, modes=_MODES)
        == "medium"
    )
