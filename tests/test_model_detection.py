"""Tests for the F-010 runtime detection + model-string contract (D-016/D-018).

The adapter owns two new members: ``detect()`` (what the runtime offers on this machine,
or ``None`` when not installed) and ``model_string()`` (canonical id -> the runtime's
exact string). Both have safe defaults so the resolver works for any user; the registry's
``detect_all()`` is plugin-based and keeps only installed runtimes.
"""

from __future__ import annotations

from aspis import runtimes
from aspis.runtimes.base import RuntimeAdapter, RuntimeInventory


class _Dummy(RuntimeAdapter):
    name = "dummy"

    def render_agent(self, agent, *, project_config=None):  # pragma: no cover - unused
        return ""

    def render_command(self, command):  # pragma: no cover - unused
        return ""


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


def test_detect_all_is_plugin_based_and_keeps_installed() -> None:
    found = runtimes.detect_all()
    assert isinstance(found, dict)
    # Whatever a machine reports, every entry is an installed inventory for its runtime.
    for name, inv in found.items():
        assert isinstance(inv, RuntimeInventory)
        assert inv.installed and inv.runtime == name
