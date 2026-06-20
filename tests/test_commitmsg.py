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
    path = _CATALOG / "config" / "commit-convention.yaml"
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
