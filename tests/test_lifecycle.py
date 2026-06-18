"""Tests for the lifecycle engine: registration and pre/core/post run order."""

from __future__ import annotations

import pytest

from aspis.lifecycle import Context, Engine


def test_run_executes_core_and_flows_context(tmp_path) -> None:
    order: list[str] = []

    def core(ctx: Context) -> None:
        order.append("core")
        ctx.results["done"] = True

    # A stub hook runner records the events so we can assert ordering.
    engine = Engine(run_hooks=lambda event, ctx: order.append(event))
    engine.register("init", core)
    ctx = engine.run("init", tmp_path, name="demo")

    assert order == ["pre-init", "core", "post-init"]
    assert ctx.results["done"] is True
    assert ctx.options["name"] == "demo"


def test_builtin_pre_post_steps_run_around_core(tmp_path) -> None:
    order: list[str] = []

    engine = Engine(run_hooks=lambda event, ctx: order.append(event))
    engine.register(
        "init",
        lambda ctx: order.append("core"),
        pre=(lambda ctx: order.append("pre-step"),),
        post=(lambda ctx: order.append("post-step"),),
    )
    engine.run("init", tmp_path)

    assert order == ["pre-init", "pre-step", "core", "post-step", "post-init"]


def test_unknown_operation_raises(tmp_path) -> None:
    with pytest.raises(KeyError):
        Engine().run("nope", tmp_path)


def test_duplicate_registration_raises() -> None:
    engine = Engine()
    engine.register("init", lambda ctx: None)
    with pytest.raises(ValueError):
        engine.register("init", lambda ctx: None)
