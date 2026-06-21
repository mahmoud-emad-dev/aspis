"""Tests for the RuntimeAdapter identity contract (F-011).

The adapter is the single source of a runtime's on-disk dir, its root guide, and
whether it expresses an agent ``mode`` — so callers never hardcode a runtime name.
"""

from __future__ import annotations

from aspis import runtimes
from aspis.runtimes.claude import ClaudeAdapter
from aspis.runtimes.opencode import OpenCodeAdapter


def test_runtime_dir_is_derived_from_name() -> None:
    assert ClaudeAdapter().runtime_dir == ".claude"
    assert OpenCodeAdapter().runtime_dir == ".opencode"


def test_root_guide_is_per_runtime() -> None:
    # Claude reads CLAUDE.md; OpenCode relies on the universal AGENTS.md (no extra guide).
    assert ClaudeAdapter().root_guide == "CLAUDE.md"
    assert OpenCodeAdapter().root_guide is None


def test_supports_mode_marks_the_promotable_runtime() -> None:
    assert OpenCodeAdapter().supports_mode is True
    assert ClaudeAdapter().supports_mode is False


def test_registry_helpers_expose_dirs_and_mode_runtime() -> None:
    dirs = runtimes.runtime_dirs()
    assert ".claude" in dirs
    assert ".opencode" in dirs
    # Exactly the runtime that expresses ``mode``.
    assert runtimes.mode_runtime() == "opencode"
