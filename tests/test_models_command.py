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
    kw.setdefault("apply", False)
    kw.setdefault("force", False)
    return argparse.Namespace(path=str(tmp_path), **kw)


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path / "no-home"))  # no global config


def test_models_lists_tiers_and_resolved_strings(monkeypatch, capsys, tmp_path) -> None:
    _isolate(monkeypatch, tmp_path)
    deep = resources.model_map("opencode")["deep"]  # provider-prefixed canonical id
    fake = {
        "opencode": RuntimeInventory(
            runtime="opencode",
            installed=True,
            providers=("opencode-go",),
            models=(deep,),
        )
    }
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: fake)

    rc = models_cmd._run(_ns(tmp_path))
    out = capsys.readouterr().out

    assert rc == 0
    assert "opencode  (detected: opencode-go)" in out
    # A provider-prefixed tier id is already a runnable `provider/model`: shown as-is.
    assert deep in out
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
    available = {"deepseek-v4-pro", "deepseek-v4-flash", "minimax-m3"}
    by_capability = data["runtimes"]["opencode"]["by_capability"]
    # the scalable layer: a model per capability, drawn only from the connected provider.
    assert by_capability["review"] in available
    assert set(by_capability.values()) <= available
    # per-agent overrides ship commented out (by_capability drives by default).
    assert (data["runtimes"]["opencode"].get("agents") or {}) == {}
    assert "# Override a single agent" in text


def test_apply_rerenders_live_agents_from_config(monkeypatch, tmp_path) -> None:
    """`models --apply` re-renders the live agents so a config edit becomes active.

    The model is baked into each agent file at export; --apply force-renders the live
    agents against the current project.yaml / agent-models.yaml. A per-agent pin to a
    concrete id must land in the on-disk agent frontmatter.
    """
    from aspis.engine import build_engine
    from aspis.operations import register_all

    _isolate(monkeypatch, tmp_path)
    # No live detection: --apply reads the file-based inventory (absent here -> canonical).
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True, no_git=True)

    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    assert "opencode/zzz-test-pin" not in agent.read_text(encoding="utf-8")  # not pinned yet

    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      committer: opencode/zzz-test-pin\n",
        encoding="utf-8",
    )
    rc = models_cmd._run(_ns(tmp_path, apply=True))

    assert rc == 0
    assert "model: opencode/zzz-test-pin" in agent.read_text(encoding="utf-8")  # edit is live


def test_apply_without_project_is_a_clean_error(monkeypatch, tmp_path) -> None:
    """--apply on a non-project reports cleanly instead of rendering nothing."""
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})
    rc = models_cmd._run(_ns(tmp_path, apply=True))
    assert rc == 1


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


# --------------------------------------------------------------------------- #
# F-015 Unit 3: models --apply hash-protection behavior
# --------------------------------------------------------------------------- #


def test_apply_protects_user_edited_agent(monkeypatch, tmp_path) -> None:
    """`models --apply` protects a user-edited agent (PROTECT, not overwritten)."""
    from aspis.engine import build_engine
    from aspis.operations import register_all

    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True, no_git=True)

    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    original = agent.read_text(encoding="utf-8")
    agent.write_text(original + "\n<!-- user edit -->\n", encoding="utf-8")

    rc = models_cmd._run(_ns(tmp_path, apply=True))

    assert rc == 0
    # PROTECT: the user edit is preserved, not overwritten.
    assert "<!-- user edit -->" in agent.read_text(encoding="utf-8")


def test_apply_conflicts_on_both_changed_agent(monkeypatch, tmp_path) -> None:
    """`models --apply` reports CONFLICT when both user and catalog changed an agent."""
    from aspis.engine import build_engine
    from aspis.operations import register_all

    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True, no_git=True)

    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    original = agent.read_text(encoding="utf-8")
    agent.write_text(original + "\n<!-- user edit -->\n", encoding="utf-8")

    # Simultaneously change the model routing (catalog-side change).
    cfg = tmp_path / ".aspis" / "config" / "project.yaml"
    cfg.write_text(
        "runtimes:\n  opencode:\n    agents:\n      committer: opencode/zzz-test-pin\n",
        encoding="utf-8",
    )

    rc = models_cmd._run(_ns(tmp_path, apply=True))

    assert rc == 0
    # CONFLICT: user edit preserved, new model NOT applied.
    assert "<!-- user edit -->" in agent.read_text(encoding="utf-8")
    assert "opencode/zzz-test-pin" not in agent.read_text(encoding="utf-8")


def test_apply_force_overwrites_user_edited_agent(monkeypatch, tmp_path) -> None:
    """`models --apply --force` overwrites user-edited agents (escape hatch)."""
    from aspis.engine import build_engine
    from aspis.operations import register_all

    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(models_cmd, "build_inventory", lambda root, write=False: {})

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True, no_git=True)

    agent = tmp_path / ".opencode" / "agents" / "committer.md"
    original = agent.read_text(encoding="utf-8")
    agent.write_text(original + "\n<!-- user edit -->\n", encoding="utf-8")

    rc = models_cmd._run(_ns(tmp_path, apply=True, force=True))

    assert rc == 0
    # Force overwrites: user edit is gone.
    assert "<!-- user edit -->" not in agent.read_text(encoding="utf-8")
