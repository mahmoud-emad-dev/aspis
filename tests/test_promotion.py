"""Tests for lead promotion — every agent ships as a subagent; bootstrap promotes
the post-bootstrap leads to ``primary`` (only ``project-lead`` is primary from the
start). Promotion edits OpenCode agent frontmatter and is idempotent.
"""

from __future__ import annotations

import yaml

from aspis import promotion
from aspis.constants import PROMOTE_TO_PRIMARY
from aspis.engine import build_engine
from aspis.operations import register_all


def _engine():
    engine = build_engine()
    register_all(engine)
    return engine


def _mode(path) -> str:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])["mode"]


def _agent(root, name):
    return root / ".opencode" / "agents" / f"{name}.md"


def test_promote_flips_system_lead_to_primary(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)  # base → opencode
    agent = _agent(tmp_path, "system-lead")
    assert _mode(agent) == "subagent"  # ships as a subagent

    result = promotion.promote_leads(tmp_path, write=True)

    assert "system-lead" in result.promoted
    assert _mode(agent) == "primary"


def test_promote_is_idempotent(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)
    promotion.promote_leads(tmp_path, write=True)

    result = promotion.promote_leads(tmp_path, write=True)

    assert result.promoted == []
    assert "system-lead" in result.already


def test_promote_dry_run_does_not_write(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)
    agent = _agent(tmp_path, "system-lead")

    result = promotion.promote_leads(tmp_path, write=False)

    assert "system-lead" in result.promoted  # would promote
    assert _mode(agent) == "subagent"  # but the file is untouched


def test_all_promote_leads_are_present_and_flipped(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)

    result = promotion.promote_leads(tmp_path, write=True)

    # All four post-bootstrap leads now exist in the catalog: each is promoted,
    # none are missing. (Promotion still tolerates a missing lead — see the dry-run
    # path — but the shipped base profile carries the full set.)
    assert set(result.promoted) == set(PROMOTE_TO_PRIMARY)
    assert result.missing == []


def test_project_lead_is_always_primary(tmp_path) -> None:
    _engine().run("init", tmp_path, write=True, no_git=True)

    assert _mode(_agent(tmp_path, "project-lead")) == "primary"  # never a subagent
    assert "project-lead" not in PROMOTE_TO_PRIMARY  # and not in the flip list


def test_bootstrap_promotes_leads(tmp_path) -> None:
    engine = _engine()
    engine.run("init", tmp_path, write=True, no_git=True)
    engine.run("bootstrap", tmp_path, write=True, yes=True, goal="x", stack="python")

    assert _mode(_agent(tmp_path, "system-lead")) == "primary"  # promoted by bootstrap
