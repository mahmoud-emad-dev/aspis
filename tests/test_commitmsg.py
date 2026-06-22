"""Tests for the commit-message attribution rule.

Real attribution (Co-Authored-By, "generated with", a credited model, 🤖) is blocked,
but a bare mention of the `.claude` / `.opencode` runtime directories is valid domain
vocabulary — the check is phrase/context-aware, not a bare-token substring match.
"""

from __future__ import annotations

import sys

import yaml

from aspis import resources

_CATALOG = resources.catalog_dir()
if str(_CATALOG / "scripts" / "hooks") not in sys.path:
    sys.path.insert(0, str(_CATALOG / "scripts" / "hooks"))

import commitmsg  # noqa: E402  (sibling catalog script)


def _convention() -> dict:
    path = _CATALOG / "config" / "policy" / "commit-convention.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _attribution_flagged(message: str) -> bool:
    return any("attribution" in error for error in commitmsg.validate(message, _convention()))


def test_blocks_real_attribution() -> None:
    assert _attribution_flagged("feat(F-008/T-01): x\n\nCo-Authored-By: A. Person")
    assert _attribution_flagged("feat(F-008/T-01): x\n\n- generated with claude")
    assert _attribution_flagged("feat(F-008/T-01): x\n\n- written by claude")
    assert _attribution_flagged("feat(F-008/T-01): x\n\n- a claude-generated change")
    assert _attribution_flagged("feat(F-008/T-01): x\n\n- 🤖 assisted this")


def test_allows_runtime_directory_mentions() -> None:
    assert not _attribution_flagged(
        "feat(F-008/T-01): ship to the .claude and .opencode dirs\n\n"
        "- regenerate the claude runtime adapter"
    )
    assert not _attribution_flagged("chore: refresh .claude/settings.json and the opencode plugin")
    assert not _attribution_flagged("fix(F-008): build with .claude config present")


# --- F-012: the shared detector finds the offending lines ---------------------


def test_find_attribution_returns_the_offending_lines() -> None:
    msg = "feat(F-008/T-01): x\n\nbody line\nCo-Authored-By: A. Person\n"
    found = commitmsg.find_attribution(msg, _convention())
    assert len(found) == 1
    index, line, reason = found[0]
    assert index == 3
    assert line == "Co-Authored-By: A. Person"
    assert "attribution" in reason


def test_find_attribution_empty_for_clean_message() -> None:
    clean = "feat(F-008/T-01): clean subject\n\n- a note"
    assert commitmsg.find_attribution(clean, _convention()) == []


# --- F-012 / Story 1: non-blocking auto-fix strips attribution ----------------


def test_strip_attribution_removes_the_lines() -> None:
    msg = (
        "docs(F-010): document the model system\n\n"
        "- real change note\n\n"
        "Co-Authored-By: A. Person\n"
        "Claude-Session: https://example/x\n"
    )
    cleaned, removed = commitmsg.strip_attribution(msg, _convention())
    assert len(removed) == 2
    assert "Co-Authored-By" not in cleaned
    assert "Claude-Session" not in cleaned
    assert "real change note" in cleaned
    assert not commitmsg.find_attribution(cleaned, _convention())


def test_strip_attribution_is_byte_stable_when_clean() -> None:
    msg = "feat(F-008/T-01): a clean subject\n\n- only real notes here\n"
    cleaned, removed = commitmsg.strip_attribution(msg, _convention())
    assert removed == []
    assert cleaned == msg


def test_strip_attribution_preserves_runtime_directory_mentions() -> None:
    msg = "feat(F-008): build with .claude config present\n\n- touch the opencode plugin\n"
    cleaned, removed = commitmsg.strip_attribution(msg, _convention())
    assert removed == []
    assert cleaned == msg


# --- F-012 / Story 3: configurable policy + escape hatch ----------------------


def test_autofix_enabled_defaults_on_and_honours_policy() -> None:
    assert commitmsg.autofix_enabled({}, "attribution") is True
    assert commitmsg.autofix_enabled({"autofix": {"attribution": False}}, "attribution") is False
    assert commitmsg.autofix_enabled({"autofix": {"attribution": True}}, "attribution") is True


def test_skip_marker_strips_an_exact_trailer_line() -> None:
    marker = commitmsg.skip_marker(_convention())
    assert marker == "Commit-Style: skip"
    msg = f"wip: messy subject\n\n- note\n{marker}\n"
    cleaned, present = commitmsg.strip_skip_marker(msg, marker)
    assert present is True
    assert marker not in cleaned
    assert "note" in cleaned


def test_skip_marker_absent_leaves_message_unchanged() -> None:
    msg = "feat(F-008/T-01): subject\n\n- note\n"
    cleaned, present = commitmsg.strip_skip_marker(msg, "Commit-Style: skip")
    assert present is False
    assert cleaned == msg


def test_skip_marker_ignores_a_prose_mention() -> None:
    # The marker text inside a longer line must NOT trigger the bypass.
    msg = "feat(F-012): add a Commit-Style: skip escape hatch\n\n- note"
    cleaned, present = commitmsg.strip_skip_marker(msg, "Commit-Style: skip")
    assert present is False
    assert cleaned == msg
