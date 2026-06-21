"""Tests for the commit-message history audit & fix (F-012, Story 2).

Each test builds a throwaway git repo so the audit/fix run against real history
without touching this repo.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from aspis import commitaudit


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8"
    ).stdout


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "Tester")
    return tmp_path


def _commit(root: Path, name: str, body: str, message: str) -> None:
    (root / name).write_text(body, encoding="utf-8")
    _git(root, "add", name)
    subprocess.run(
        ["git", "-C", str(root), "commit", "--no-verify", "-q", "-F", "-"],
        input=message,
        text=True,
        encoding="utf-8",
        check=True,
    )


_CONV = commitaudit.load_convention(Path.cwd())  # the bundled/project convention


def test_audit_flags_a_bad_message(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "a.txt", "x", "feat(F-001/T-01): a clean one\n\n- note")
    _commit(repo, "b.txt", "y", "docs(F-001): leaked\n\nCo-Authored-By: A. Bot")
    findings = commitaudit.audit_history(repo, _CONV)
    assert len(findings) == 1
    assert findings[0].subject == "docs(F-001): leaked"
    assert findings[0].autofixable is True


def test_audit_clean_repo_is_empty(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "a.txt", "x", "feat(F-001/T-01): a clean subject\n\n- a real note")
    assert commitaudit.audit_history(repo, _CONV) == []


def test_commits_command_audit_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from aspis.cli import main

    repo = _repo(tmp_path)
    _commit(repo, "a.txt", "x", "feat(F-001/T-01): clean\n\n- note")
    assert main(["commits", "--path", str(repo)]) == 0
    assert "conform" in capsys.readouterr().out

    _commit(repo, "b.txt", "y", "docs(F-001): bad\n\nCo-Authored-By: A. Bot")
    assert main(["commits", "--path", str(repo), "--audit"]) == 1
    assert "violate" in capsys.readouterr().out


def test_fix_rewrites_attribution_and_keeps_content(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "a.txt", "x", "feat(F-001/T-01): clean\n\n- note")
    _commit(repo, "b.txt", "keepme", "docs(F-001): leaked\n\n- real note\nCo-Authored-By: A. Bot")

    tree_before = _git(repo, "rev-parse", "HEAD^{tree}").strip()
    findings = commitaudit.audit_history(repo, _CONV)
    assert commitaudit.fix_history(repo, _CONV, findings) == 0

    # backup ref exists and still carries the original attribution
    backups = [b.strip(" *") for b in _git(repo, "branch").splitlines() if "backup/" in b]
    assert backups, "a backup ref should have been created"
    assert "Co-Authored-By" in _git(repo, "log", backups[0], "--format=%B")

    # the rewritten HEAD message is clean; the file content is byte-identical
    assert "Co-Authored-By" not in _git(repo, "log", "HEAD", "--format=%B")
    assert "real note" in _git(repo, "log", "-1", "HEAD", "--format=%B")
    assert _git(repo, "rev-parse", "HEAD^{tree}").strip() == tree_before
    assert (repo / "b.txt").read_text(encoding="utf-8") == "keepme"
