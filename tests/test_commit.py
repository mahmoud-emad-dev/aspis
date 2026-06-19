"""Tests for the F-007 git subsystem — message composition and the ``aspis commit`` tool.

The composer ships as a self-contained catalog script; it is added to ``sys.path`` and
imported by name, the same way the installed tool runs it. ``aspis commit`` is exercised
end-to-end against a real, freshly-initialised project.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from aspis import resources

_CATALOG = resources.catalog_dir()
for _d in (_CATALOG / "scripts" / "git", _CATALOG / "scripts" / "hooks"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import commitmsg  # noqa: E402  (sibling catalog script)
import compose  # noqa: E402  (sibling catalog script)


def _convention() -> dict:
    path = _CATALOG / "config" / "commit-convention.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _mini_project(root: Path, feature_id: str = "F-007") -> Path:
    """A minimal project carrying just the convention + active-feature pointer."""
    (root / ".aspis" / "config").mkdir(parents=True, exist_ok=True)
    (root / ".aspis" / "current").mkdir(parents=True, exist_ok=True)
    convention = (_CATALOG / "config" / "commit-convention.yaml").read_text(encoding="utf-8")
    (root / ".aspis" / "config" / "commit-convention.yaml").write_text(convention, encoding="utf-8")
    (root / ".aspis" / "current" / "active_feature.json").write_text(
        f'{{"id": "{feature_id}"}}', encoding="utf-8"
    )
    return root


# --- composition (unit) -----------------------------------------------------------------


def test_compose_formats_scope_bullets_and_validates() -> None:
    message = compose.compose(
        type_="feat",
        title="add the committer",
        scope="F-007/T-02",
        bullets=["single git writer", "reuses the F-006 validator"],
    )
    assert message.splitlines()[0] == "feat(F-007/T-02): add the committer"
    assert "- single git writer" in message
    assert commitmsg.validate(message, _convention()) == []  # convention-valid


def test_build_scope_uses_active_feature_and_spans(tmp_path) -> None:
    _mini_project(tmp_path, "F-042")
    assert compose.build_scope(tmp_path, "", "T-03") == "F-042/T-03"
    assert compose.build_scope(tmp_path, "", "") == "F-042"
    assert compose.build_scope(tmp_path, "F-099", "T-01..T-05") == "F-099/T-01..T-05"


def test_main_span_adds_tasks_trailer(tmp_path, capsys) -> None:
    _mini_project(tmp_path)
    code = compose.main(
        [
            "--type",
            "feat",
            "--task",
            "T-01..T-05",
            "--title",
            "the core fix",
            "--bullet",
            "x",
            "--root",
            str(tmp_path),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert out.splitlines()[0] == "feat(F-007/T-01..T-05): the core fix"
    assert "Tasks: T-01..T-05" in out


def test_main_rejects_attribution(tmp_path, capsys) -> None:
    _mini_project(tmp_path)
    code = compose.main(["--type", "feat", "--title", "done with claude", "--root", str(tmp_path)])
    assert code == 1
    assert "attribution" in capsys.readouterr().err.lower()


def test_main_scopeless_lifecycle_validates(tmp_path, capsys) -> None:
    _mini_project(tmp_path)
    code = compose.main(
        [
            "--type",
            "chore",
            "--title",
            "initialize the project",
            "--no-scope",
            "--bullet",
            "seed",
            "--root",
            str(tmp_path),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert out.splitlines()[0] == "chore: initialize the project"
    assert commitmsg.validate(out, _convention()) == []


# --- aspis commit (integration) ---------------------------------------------------------


def test_aspis_commit_stages_only_named_paths(tmp_path) -> None:
    from aspis.cli import main as cli_main
    from aspis.engine import build_engine
    from aspis.operations import register_all

    engine = build_engine()
    register_all(engine)
    engine.run("init", tmp_path, write=True)  # git init + ship scripts + arm hooks

    (tmp_path / "wanted.txt").write_text("keep\n", encoding="utf-8")
    (tmp_path / "other.txt").write_text("later\n", encoding="utf-8")

    code = cli_main(
        [
            "commit",
            "wanted.txt",
            "--type",
            "chore",
            "--no-scope",
            "--title",
            "add the wanted file",
            "--bullet",
            "just this one",
            "--path",
            str(tmp_path),
        ]
    )
    assert code == 0

    subject = subprocess.run(
        ["git", "-C", str(tmp_path), "log", "-1", "--pretty=%s"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    assert "add the wanted file" in subject

    # The unnamed file was never staged — explicit paths only, no `git add -A`.
    untracked = subprocess.run(
        ["git", "-C", str(tmp_path), "status", "--porcelain", "other.txt"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    assert "other.txt" in untracked


def test_aspis_commit_requires_explicit_paths() -> None:
    from aspis.cli import main as cli_main

    with pytest.raises(SystemExit):  # argparse nargs="+" refuses an empty path set
        cli_main(["commit", "--type", "chore", "--title", "nothing staged"])
