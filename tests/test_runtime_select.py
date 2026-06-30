"""F-020 — runtime detection + selection (pure logic) used by ``aspis init``."""

from __future__ import annotations

from aspis.operations import runtime_select as rs


def test_supported_includes_both_runtimes_sorted() -> None:
    sup = rs.supported()
    assert "opencode" in sup and "claude" in sup
    assert sup == sorted(sup)


def test_menu_marks_installed() -> None:
    rows = rs.menu(["claude", "opencode"], ["opencode"])
    assert rows == [(1, "claude", False), (2, "opencode", True)]


def test_render_menu_shows_install_tags() -> None:
    text = rs.render_menu(rs.menu(["claude", "opencode"], ["opencode"]))
    assert "claude" in text and "opencode" in text
    assert "installed" in text and "not installed" in text


def test_parse_selection_numbers_and_names_follow_supported_order() -> None:
    sup = ["claude", "opencode"]
    assert rs.parse_selection("1", sup) == ["claude"]
    assert rs.parse_selection("opencode", sup) == ["opencode"]
    assert rs.parse_selection("2, 1", sup) == ["claude", "opencode"]
    assert rs.parse_selection("opencode claude", sup) == ["claude", "opencode"]


def test_parse_selection_ignores_unknown_and_dedupes() -> None:
    sup = ["claude", "opencode"]
    assert rs.parse_selection("9 cursor opencode opencode", sup) == ["opencode"]
    assert rs.parse_selection("nonsense", sup) == []


def test_install_hint_mentions_url_and_command() -> None:
    hint = rs.install_hint()
    assert rs.OPENCODE_URL in hint and rs.OPENCODE_INSTALL in hint
