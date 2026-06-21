"""Tests for ``aspis models`` (F-010 T-10): the per-runtime tier resolution view.

Detection is stubbed so the command is deterministic and never touches a live runtime.
"""

from __future__ import annotations

import argparse

from aspis import resources
from aspis.commands import models as models_cmd
from aspis.runtimes.base import RuntimeInventory


def test_models_lists_tiers_and_resolved_strings(monkeypatch, capsys, tmp_path) -> None:
    # A detected OpenCode with a connected provider; Claude undetected.
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

    rc = models_cmd._run(argparse.Namespace(path=str(tmp_path)))
    out = capsys.readouterr().out

    assert rc == 0
    assert "opencode  (detected: opencode-go)" in out
    assert f"opencode-go/{deep}" in out  # deep tier translated to a connected string
    assert "claude  (not detected)" in out
    assert resources.model_map("claude")["deep"] in out  # claude undetected -> canonical id
