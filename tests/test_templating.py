"""Tests for the placeholder rendering helper."""

from __future__ import annotations

from aspis.templating import render


def test_fills_known_and_keeps_unknown() -> None:
    out = render("hi {name}, stack={stack}", name="ASPIS")
    assert out == "hi ASPIS, stack={stack}"


def test_leaves_non_placeholder_braces_untouched() -> None:
    assert render('{"a": 1}', name="x") == '{"a": 1}'
