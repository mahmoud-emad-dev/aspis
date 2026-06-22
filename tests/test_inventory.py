"""Tests for the F-010 detection orchestrator (T-07).

``build_inventory`` asks every installed runtime (``detect_all``) and writes a single
generated ``.aspis/config/.runtime-inventory.json``; ``load_inventory`` reads it back and
returns ``None`` when it is absent — the graceful-degradation path (FR-006). Detection
itself is stubbed so these tests are deterministic and never touch a live runtime.
"""

from __future__ import annotations

import json

from aspis import inventory
from aspis.runtimes.base import RuntimeInventory

_FIXTURE = {
    "opencode": RuntimeInventory(
        runtime="opencode",
        installed=True,
        providers=("opencode-go", "minimax"),
        models=("opencode-go/minimax-m3", "minimax/MiniMax-M3"),
    ),
    "claude": RuntimeInventory(
        runtime="claude", installed=True, providers=("anthropic",), models=("opus", "haiku")
    ),
}


def test_build_inventory_writes_generated_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(inventory, "detect_all", lambda: _FIXTURE)
    result = inventory.build_inventory(tmp_path)

    assert set(result) == {"opencode", "claude"}
    path = tmp_path / inventory.INVENTORY_REL
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "generated" in data
    assert data["runtimes"]["opencode"]["providers"] == ["opencode-go", "minimax"]
    assert data["runtimes"]["claude"]["models"] == ["opus", "haiku"]


def test_build_inventory_can_skip_writing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(inventory, "detect_all", lambda: _FIXTURE)
    inventory.build_inventory(tmp_path, write=False)
    assert not (tmp_path / inventory.INVENTORY_REL).exists()


def test_load_inventory_round_trips(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(inventory, "detect_all", lambda: _FIXTURE)
    inventory.build_inventory(tmp_path)

    loaded = inventory.load_inventory(tmp_path)
    assert loaded is not None
    assert loaded["opencode"] == _FIXTURE["opencode"]  # frozen dataclass equality
    assert loaded["claude"].providers == ("anthropic",)


def test_load_inventory_absent_is_none(tmp_path) -> None:
    assert inventory.load_inventory(tmp_path) is None


def test_load_inventory_malformed_is_none(tmp_path) -> None:
    path = tmp_path / inventory.INVENTORY_REL
    path.parent.mkdir(parents=True)
    path.write_text("{ not valid json", encoding="utf-8")
    assert inventory.load_inventory(tmp_path) is None
