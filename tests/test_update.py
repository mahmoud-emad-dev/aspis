"""Test the context-update dispatcher runs every updater."""

from __future__ import annotations

import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "update.py"


def test_update_refreshes_all_context_files(git_repo) -> None:
    subprocess.run([sys.executable, str(SCRIPT), str(git_repo)], check=True, capture_output=True)

    assert (git_repo / ".aspis" / "index" / "FILE_REGISTRY.yaml").is_file()
    assert (git_repo / ".aspis" / "context" / "CURRENT_STATE.md").is_file()
    assert (git_repo / ".aspis" / "context" / "RECENT_CHANGES.md").is_file()
    assert (git_repo / ".aspis" / "index" / "CODE_MAP.md").is_file()
