"""Tests for ``aspis models`` (F-010): tier view, override validation, and the menu.

Detection is stubbed so the command is deterministic and never touches a live runtime.
``ASPIS_HOME`` is isolated so the machine's real ~/.aspis config never leaks in.
"""

from __future__ import annotations

import argparse

from aspis import resources
from aspis.commands import models as models_cmd
from aspis.runtimes.base import RuntimeInventory


def _ns(tmp_path, **kw):
    kw.setdefault("available", False)
    kw.setdefault("sync", False)
    return argparse.Namespace(path=str(tmp_path), **kw)


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path / "no-home"))  # no global config


def test_models_lists_tiers_and_resolved_strings(monkeypatch, capsys, tmp_path) -> None:
    _isolate(monkeypatch, tmp_path)
    deep = resources.model_map("opencode")["deep"]
    fake = {
        "opencode": RuntimeInventory(
            runtime="opencode",
            installed=True,
            providers=("opencode-go",),
            models=(f"opencode-go/{deep}",),
        )
    }
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: fake)

    rc = models_cmd._run(_ns(tmp_path))
    out = capsys.readouterr().out

    assert rc == 0
    assert "opencode  (detected: opencode-go)" in out
    assert f"opencode-go/{deep}" in out  # deep tier translated to a connected string
    assert "claude  (not detected)" in out
    assert resources.model_map("claude")["deep"] in out  # claude undetected -> canonical id


def test_models_flags_a_pin_that_is_not_available(monkeypatch, capsys, tmp_path) -> None:
    _isolate(monkeypatch, tmp_path)
    fake = {
        "opencode": RuntimeInventory(
            runtime="opencode",
            installed=True,
            providers=("opencode-go",),
            models=("opencode-go/deepseek-v4-pro",),
        )
    }
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: fake)
    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      reviewer: glm-9.9\n", encoding="utf-8"
    )

    models_cmd._run(_ns(tmp_path))
    out = capsys.readouterr().out

    assert "pin reviewer" in out
    assert "[!] not available on this runtime" in out  # glm-9.9 is not in the inventory


def test_sync_generates_an_editable_agent_models_file(monkeypatch, tmp_path) -> None:
    import yaml

    _isolate(monkeypatch, tmp_path)
    fake = {
        "opencode": RuntimeInventory(
            runtime="opencode",
            installed=True,
            providers=("opencode-go",),
            models=(
                "opencode-go/deepseek-v4-pro",
                "opencode-go/deepseek-v4-flash",
                "opencode-go/minimax-m3",
            ),
        )
    }
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: fake)

    rc = models_cmd._run(_ns(tmp_path, sync=True))
    text = (tmp_path / ".aspis" / "config" / "agent-models.yaml").read_text(encoding="utf-8")

    assert rc == 0
    assert "AVAILABLE MODELS, ranked per capability" in text  # the menu header
    assert "review (reviewers)" in text  # per-capability ranking
    data = yaml.safe_load(text)
    agents = data["runtimes"]["opencode"]["agents"]
    available = {"deepseek-v4-pro", "deepseek-v4-flash", "minimax-m3"}
    # every agent is auto-assigned a model drawn only from the connected provider's catalog.
    assert agents["reviewer"] in available
    assert agents["committer"] in available
    assert set(agents.values()) <= available


def test_models_available_lists_the_menu_by_provider(monkeypatch, capsys, tmp_path) -> None:
    _isolate(monkeypatch, tmp_path)
    fake = {
        "opencode": RuntimeInventory(
            runtime="opencode",
            installed=True,
            providers=("opencode-go",),
            models=("opencode-go/deepseek-v4-pro", "opencode-go/minimax-m3"),
        )
    }
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: fake)

    models_cmd._run(_ns(tmp_path, available=True))
    out = capsys.readouterr().out

    assert "available (copy any into agent-models.yaml):" in out
    assert "opencode-go: deepseek-v4-pro, minimax-m3" in out
