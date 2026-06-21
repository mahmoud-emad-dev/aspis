"""Tests for F-010 T-09: agent render routed through the resolver + detected inventory.

With an inventory, a rendered agent carries the model string the machine can actually run
(OpenCode: a connected-provider string; Claude: the durable alias). With no inventory, the
rendered model is the canonical tier id — byte-identical to today, which keeps the committed
dogfood reproducible (SC-001/SC-004).
"""

from __future__ import annotations

import yaml

from aspis import resources
from aspis.runtimes.base import RuntimeInventory
from aspis.transform import render_agent

_DEEP_AGENT = """---
name: build-lead
description: The build orchestrator.
mode: subagent
model: deep
tools: [read, edit]
---

You orchestrate the build.
"""


def _model(rendered: str) -> str:
    return yaml.safe_load(rendered.split("---", 2)[1])["model"]


def test_opencode_without_inventory_renders_canonical_tier() -> None:
    # SC-004: no detection -> today's tier map value (the deep canonical id).
    assert _model(render_agent(_DEEP_AGENT, "opencode")) == resources.model_map("opencode")["deep"]


def test_opencode_with_inventory_renders_connected_provider_string() -> None:
    deep = resources.model_map("opencode")["deep"]
    inv = RuntimeInventory(
        runtime="opencode",
        installed=True,
        providers=("opencode-go",),
        models=(f"opencode-go/{deep}",),
    )
    out = _model(render_agent(_DEEP_AGENT, "opencode", inventory=inv))
    assert out == f"opencode-go/{deep}"  # SC-001: a real, runnable string


def test_claude_without_inventory_renders_canonical_id() -> None:
    assert _model(render_agent(_DEEP_AGENT, "claude")) == "claude-opus-4-8"


def test_claude_with_inventory_renders_alias() -> None:
    inv = RuntimeInventory(
        runtime="claude", installed=True, providers=("anthropic",), models=("opus", "haiku")
    )
    assert _model(render_agent(_DEEP_AGENT, "claude", inventory=inv)) == "opus"
