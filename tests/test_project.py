"""Tests for project-layer helpers: build-mode read/write and the modes single source.

Behaviour-focused — these cover the real logic (a fallback when unset, an
in-place file edit that preserves the rest of the file, rejection of an unknown
mode) and the one cross-file invariant: the accepted mode names must match
``modes.yaml``, the single source of the rigor dial.
"""

from __future__ import annotations

import pytest

from aspis import project, resources


def test_default_mode_falls_back_when_unset(tmp_path) -> None:
    # No project.yaml → the documented fallback, not a crash.
    assert project.default_mode(tmp_path) == "production"
    assert project.default_mode(tmp_path, fallback="mvp") == "mvp"


def test_set_mode_updates_in_place_and_preserves_the_rest(tmp_path) -> None:
    cfg = project.config_path(tmp_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("# project settings\nmode: vibe\nother: keep\n", encoding="utf-8")

    project.set_mode(tmp_path, "production")

    text = cfg.read_text(encoding="utf-8")
    assert "mode: production" in text
    assert "# project settings" in text  # comment preserved
    assert "other: keep" in text  # unrelated keys preserved
    assert project.default_mode(tmp_path) == "production"


def test_set_mode_rejects_unknown_mode(tmp_path) -> None:
    with pytest.raises(ValueError):
        project.set_mode(tmp_path, "turbo")


def test_valid_modes_match_modes_yaml() -> None:
    # The accepted mode names (code) must stay in lock-step with modes.yaml so
    # the two can't silently drift — single source enforced by test, not by a
    # runtime read that would complicate a stable constant.
    shipped = set(resources.config("modes.yaml").get("modes", {}))
    assert set(project.VALID_MODES) == shipped
