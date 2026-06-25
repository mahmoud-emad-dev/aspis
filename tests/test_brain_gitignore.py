"""Tests for the brain .gitignore scaffold (F-015).

Verifies that the scaffolded brain .gitignore ignores the export snapshot
and audit log files, so generated export state is not tracked in git.
"""

from __future__ import annotations

from aspis import resources
from aspis.cli import main


def test_scaffold_brain_gitignore_contains_export_entries() -> None:
    """The scaffold brain.gitignore ignores export-snapshot.json and export-log.jsonl."""
    content = resources.scaffold("brain.gitignore")
    assert "current/export-snapshot.json" in content
    assert "current/export-log.jsonl" in content


def test_generated_project_gitignore_ignores_export_state(tmp_path) -> None:
    """A scaffolded project's .aspis/.gitignore ignores export state files."""
    assert main(["init", str(tmp_path), "--write", "--no-git"]) == 0
    gitignore = (tmp_path / ".aspis" / ".gitignore").read_text(encoding="utf-8")
    assert "current/export-snapshot.json" in gitignore
    assert "current/export-log.jsonl" in gitignore
