"""Tests for the RECENT_CHANGES builder script."""

from __future__ import annotations

import subprocess
import sys

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "record_changes.py"


def _run(root) -> None:
    subprocess.run([sys.executable, str(SCRIPT), str(root)], check=True, capture_output=True)


def _commit(root, name: str, message: str) -> None:
    (root / name).write_text(name, encoding="utf-8")
    for args in (("add", "-A"), ("commit", "-q", "-m", message)):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def test_lists_recent_commits(git_repo) -> None:
    _run(git_repo)

    text = (git_repo / ".aspis" / "context" / "RECENT_CHANGES.md").read_text(encoding="utf-8")
    assert "ASPIS:auto START" in text
    assert "seed commit" in text  # the fixture's commit subject


def test_digest_groups_by_feature_and_annotates(git_repo) -> None:
    _commit(git_repo, "a.py", "feat(F-007): add a thing")
    _commit(git_repo, "b.py", "fix(F-007): correct it")
    _run(git_repo)

    text = (git_repo / ".aspis" / "context" / "RECENT_CHANGES.md").read_text(encoding="utf-8")
    assert "**By feature / area**" in text
    assert "**F-007** — 2 commit(s)" in text  # scopes grouped under the feature id
    assert "**Latest**" in text
    assert "file(s)" in text  # each commit annotated with a file count


def test_active_feature_group_is_listed_first(git_repo) -> None:
    current = git_repo / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text('{"id": "F-007", "phase": "build"}', "utf-8")
    _commit(git_repo, "a.py", "chore: housekeeping")
    _commit(git_repo, "b.py", "feat(F-007): the active work")
    _run(git_repo)

    text = (git_repo / ".aspis" / "context" / "RECENT_CHANGES.md").read_text(encoding="utf-8")
    by_feature = text.split("**By feature / area**", 1)[1]
    assert by_feature.index("F-007") < by_feature.index("chore")  # active group floats up
