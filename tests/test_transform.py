"""Tests for catalog parsing and per-runtime transformation."""

from __future__ import annotations

import pytest

from aspis.catalog import parse_agent
from aspis.transform import render_agent, render_command

AGENT = """---
name: project-lead
description: The lead you talk to.
mode: primary
model: deep
tools: [read, edit]
---

You are the lead.
"""

COMMAND = """---
name: build
description: Run the build.
agent: project-lead
---

Build the feature.
"""


def test_parse_agent_reads_abstraction() -> None:
    agent = parse_agent(AGENT)
    assert agent.name == "project-lead"
    assert agent.mode == "primary"
    assert agent.tools == ("read", "edit")
    assert agent.body == "You are the lead."


def test_opencode_agent_has_mode() -> None:
    out = render_agent(AGENT, "opencode")
    assert "mode: primary" in out
    assert "You are the lead." in out


def test_claude_agent_maps_model_and_keys_on_name() -> None:
    out = render_agent(AGENT, "claude")
    assert "name: project-lead" in out
    assert "claude-opus-4-8" in out  # deep tier → opus


def test_command_binding_differs_per_runtime() -> None:
    assert "agent: project-lead" in render_command(COMMAND, "opencode")
    assert "agent:" not in render_command(COMMAND, "claude")


def test_unknown_runtime_raises() -> None:
    with pytest.raises(KeyError):
        render_agent(AGENT, "nope")
