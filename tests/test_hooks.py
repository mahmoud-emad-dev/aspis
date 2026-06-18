"""Tests for Type-1 lifecycle hook discovery and execution."""

from __future__ import annotations

from pathlib import Path

from aspis.engine import build_engine


def _write_hook(root: Path, event: str, name: str, body: str) -> None:
    """Drop a hook script under the project's hooks/<event>/ folder."""
    event_dir = root / ".asps" / "hooks" / event
    event_dir.mkdir(parents=True, exist_ok=True)
    (event_dir / name).write_text(body, encoding="utf-8")


def test_pre_hook_runs_before_core(tmp_path) -> None:
    # A pre-hook that writes a marker file proves discovery + execution + order.
    _write_hook(
        tmp_path,
        "pre-demo",
        "10_marker.py",
        "from pathlib import Path\nPath('pre.marker').write_text('ok')\n",
    )

    engine = build_engine()
    ran: list[str] = []
    engine.register("demo", lambda ctx: ran.append("core"))
    ctx = engine.run("demo", tmp_path)

    assert (tmp_path / "pre.marker").is_file()
    assert ran == ["core"]
    assert ctx.results["hooks"]["pre-demo"][0]["exit_code"] == 0


def test_no_hooks_dir_is_a_noop(tmp_path) -> None:
    engine = build_engine()
    engine.register("demo", lambda ctx: None)
    ctx = engine.run("demo", tmp_path)
    assert "hooks" not in ctx.results
