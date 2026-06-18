"""Tests for the RECENT_CHANGES builder script."""

from __future__ import annotations

import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "record_changes.py"


def test_lists_recent_commits(git_repo) -> None:
    subprocess.run([sys.executable, str(SCRIPT), str(git_repo)], check=True, capture_output=True)

    text = (git_repo / ".aspis" / "context" / "RECENT_CHANGES.md").read_text(encoding="utf-8")
    assert "ASPIS:auto START" in text
    assert "seed commit" in text  # the fixture's commit subject
