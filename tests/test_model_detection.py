"""Tests for the F-010 runtime detection + model-string contract (D-016/D-018).

The adapter owns two members: ``detect()`` (what the runtime offers on this machine,
or ``None`` when not installed) and ``model_string()`` (canonical id -> the runtime's
exact string). Both have safe defaults so the resolver works for any user; the registry's
``detect_all()`` is plugin-based and keeps only installed runtimes.

Detection is exercised with FIXTURES (a sample auth.json / settings.json and a captured
``opencode models`` listing) and never the live runtime — ``shutil.which`` is stubbed to
``None`` so no subprocess fires, and env vars point path resolution at a tmp dir.
"""

from __future__ import annotations

import json

from aspis import runtimes
from aspis.runtimes import claude as claude_mod
from aspis.runtimes import opencode as opencode_mod
from aspis.runtimes.base import RuntimeAdapter, RuntimeInventory
from aspis.runtimes.claude import ClaudeAdapter
from aspis.runtimes.opencode import OpenCodeAdapter

# A trimmed, representative `opencode models` capture (the real list is ~350 lines).
_OPENCODE_MODELS = """opencode/claude-opus-4-8
opencode/deepseek-v4-flash
opencode-go/minimax-m3
minimax/MiniMax-M3
openrouter/anthropic/claude-opus-4.8
"""


class _Dummy(RuntimeAdapter):
    name = "dummy"

    def render_agent(self, agent, *, project_config=None):  # pragma: no cover - unused
        return ""

    def render_command(self, command):  # pragma: no cover - unused
        return ""


def _no_runtime_binary(monkeypatch) -> None:
    """Stub `shutil.which` in both adapters so detection never shells out in tests."""
    monkeypatch.setattr(opencode_mod.shutil, "which", lambda _name: None)
    monkeypatch.setattr(claude_mod.shutil, "which", lambda _name: None)


def test_inventory_is_a_value_object() -> None:
    inv = RuntimeInventory(runtime="opencode", installed=True, providers=("opencode-go",))
    assert inv.runtime == "opencode" and inv.installed
    assert inv.providers == ("opencode-go",) and inv.models == ()


def test_contract_defaults_are_safe() -> None:
    # A runtime that overrides nothing is "not installed" and translates by identity,
    # so the resolver degrades gracefully rather than crashing or guessing.
    dummy = _Dummy()
    assert dummy.detect() is None
    assert dummy.model_string("minimax-m3") == "minimax-m3"


# --- parsing -----------------------------------------------------------------


def test_parse_models_keeps_only_provider_slash_lines() -> None:
    parsed = opencode_mod._parse_models(_OPENCODE_MODELS + "\n─── hidden ───\nnot-a-model\n")
    assert "opencode-go/minimax-m3" in parsed
    assert "minimax/MiniMax-M3" in parsed
    assert "not-a-model" not in parsed  # no slash -> dropped
    assert all("/" in line for line in parsed)


# --- model_string translation ------------------------------------------------


def test_opencode_model_string_prefers_connected_provider_by_rank() -> None:
    inv = RuntimeInventory(
        runtime="opencode",
        installed=True,
        providers=("opencode-go", "minimax", "openrouter"),
        models=opencode_mod._parse_models(_OPENCODE_MODELS),
    )
    # minimax-m3 is offered by opencode-go (prefer 1) and minimax (prefer 3) -> go wins.
    assert OpenCodeAdapter().model_string("minimax-m3", inv) == "opencode-go/minimax-m3"


def test_opencode_model_string_skips_unconnected_providers() -> None:
    inv = RuntimeInventory(
        runtime="opencode",
        installed=True,
        providers=("minimax",),  # opencode-go NOT connected
        models=opencode_mod._parse_models(_OPENCODE_MODELS),
    )
    # Only the connected minimax string qualifies, even though go ranks higher.
    assert OpenCodeAdapter().model_string("minimax-m3", inv) == "minimax/MiniMax-M3"


def test_opencode_model_string_is_identity_without_inventory() -> None:
    # SC-004: no detection -> output equals today's bare canonical id.
    assert OpenCodeAdapter().model_string("minimax-m3") == "minimax-m3"
    empty = RuntimeInventory(runtime="opencode", installed=True, providers=(), models=())
    assert OpenCodeAdapter().model_string("minimax-m3", empty) == "minimax-m3"


def test_claude_model_string_maps_to_durable_alias() -> None:
    adapter = ClaudeAdapter()
    assert adapter.model_string("claude-opus-4-8") == "opus"
    assert adapter.model_string("claude-sonnet-4-6") == "sonnet"
    assert adapter.model_string("claude-haiku-4-5") == "haiku"
    assert adapter.model_string("minimax-m3") == "minimax-m3"  # non-claude -> identity


# --- detect() (env-driven, fixture-backed) -----------------------------------


def test_opencode_detect_reads_auth_content_env(monkeypatch) -> None:
    _no_runtime_binary(monkeypatch)
    monkeypatch.setenv(
        "OPENCODE_AUTH_CONTENT",
        json.dumps({"opencode-go": {"type": "api", "key": "secret"}, "minimax": {"type": "api"}}),
    )
    inv = OpenCodeAdapter().detect()
    assert inv is not None and inv.installed
    assert set(inv.providers) == {"opencode-go", "minimax"}  # keys only, never the secret
    assert inv.models == ()  # no binary -> no live listing


def test_opencode_detect_reads_auth_json_via_xdg(monkeypatch, tmp_path) -> None:
    _no_runtime_binary(monkeypatch)
    monkeypatch.delenv("OPENCODE_AUTH_CONTENT", raising=False)
    auth = tmp_path / "opencode" / "auth.json"
    auth.parent.mkdir(parents=True)
    auth.write_text(json.dumps({"openrouter": {"type": "api", "key": "x"}}), encoding="utf-8")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    inv = OpenCodeAdapter().detect()
    assert inv is not None and inv.providers == ("openrouter",)


def test_opencode_detect_is_none_when_absent(monkeypatch, tmp_path) -> None:
    _no_runtime_binary(monkeypatch)
    monkeypatch.delenv("OPENCODE_AUTH_CONTENT", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))  # empty -> no auth.json
    assert OpenCodeAdapter().detect() is None


def test_opencode_detect_never_raises_on_malformed_auth(monkeypatch) -> None:
    _no_runtime_binary(monkeypatch)
    monkeypatch.setenv("OPENCODE_AUTH_CONTENT", "{ this is not valid json")
    assert OpenCodeAdapter().detect() is None  # swallowed, never raised


def test_claude_detect_reads_settings_dir(monkeypatch, tmp_path) -> None:
    _no_runtime_binary(monkeypatch)
    (tmp_path / "settings.json").write_text('{"model": "opus"}', encoding="utf-8")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    inv = ClaudeAdapter().detect()
    assert inv is not None and inv.providers == ("anthropic",)
    assert "opus" in inv.models and "haiku" in inv.models


def test_claude_detect_is_none_when_absent(monkeypatch, tmp_path) -> None:
    _no_runtime_binary(monkeypatch)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))  # empty -> no settings.json
    assert ClaudeAdapter().detect() is None


# --- registry ----------------------------------------------------------------


def test_detect_all_is_plugin_based_and_keeps_installed(monkeypatch, tmp_path) -> None:
    # Deterministic across machines: stub the binaries and point OpenCode at a fixture
    # auth.json, Claude at an empty dir. Only OpenCode should be discovered.
    _no_runtime_binary(monkeypatch)
    monkeypatch.delenv("OPENCODE_AUTH_CONTENT", raising=False)
    data_home = tmp_path / "data"
    (data_home / "opencode").mkdir(parents=True)
    (data_home / "opencode" / "auth.json").write_text(
        json.dumps({"opencode-go": {"type": "api", "key": "x"}}), encoding="utf-8"
    )
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "noclaude"))

    found = runtimes.detect_all()
    assert isinstance(found, dict)
    assert "opencode" in found
    for name, inv in found.items():
        assert isinstance(inv, RuntimeInventory)
        assert inv.installed and inv.runtime == name
