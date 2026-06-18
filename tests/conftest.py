"""Shared pytest fixtures."""

from __future__ import annotations

import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    """A temporary git repository with one seed commit."""

    def _git(*args: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)

    _git("init", "-q")
    _git("config", "user.email", "tester@example.com")
    _git("config", "user.name", "Tester")
    (tmp_path / "seed.txt").write_text("seed", encoding="utf-8")
    _git("add", "-A")
    _git("commit", "-q", "-m", "seed commit")
    return tmp_path
