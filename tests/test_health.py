"""Tests for ``aspis doctor`` health checks (F-014: the runtime-hook interpreter safety-net)."""

from __future__ import annotations

import sys
from pathlib import Path

from aspis.engine import build_engine
from aspis.health import check_runtime_hooks
from aspis.operations import register_all


def _init(root: Path) -> None:
    engine = build_engine()
    register_all(engine)
    engine.run("init", root, write=True, no_git=True)  # base -> opencode (ships the scope-guard)


def test_runtime_hook_interpreter_present_after_init(tmp_path) -> None:
    _init(tmp_path)
    check = check_runtime_hooks(tmp_path)
    assert check.status == "ok"
    assert Path(sys.executable).as_posix() in check.detail  # the baked, resolvable interpreter


def test_runtime_hook_interpreter_missing_warns(tmp_path) -> None:
    # Simulates a Windows<->WSL move: the baked path no longer resolves -> doctor must flag it,
    # never silently no-op the guard.
    _init(tmp_path)
    plugin = tmp_path / ".opencode" / "plugins" / "session-notice.ts"
    text = plugin.read_text(encoding="utf-8")
    plugin.write_text(
        text.replace(Path(sys.executable).as_posix(), "/no/such/python"), encoding="utf-8"
    )
    check = check_runtime_hooks(tmp_path)
    assert check.status == "warn"
    assert "missing" in check.detail


def test_no_runtime_hooks_is_ok(tmp_path) -> None:
    assert check_runtime_hooks(tmp_path).status == "ok"  # nothing to verify, not a failure
