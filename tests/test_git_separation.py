"""Git separation (F-022) — the two-lane storage model.

A freshly initialized project must keep three artifact kinds apart:
- **Product** git (`root/.git`) tracks source + the small root guides only.
- **Brain** shadow git (`.aspis/.git`) versions the brain on its own history.
- **Runtime** dirs (`.opencode`/`.claude`) are committed to neither — they are
  catalog-rendered and tracked by the export snapshot/log lane.

These tests drive the real `init` operation with git enabled (env-provided identity so
commits work without global config) and assert what each lane tracks.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from aspis import gitops
from aspis.lifecycle import Engine
from aspis.operations import init as initop


@pytest.fixture(autouse=True)
def _git_identity(monkeypatch) -> None:
    """Provide a git author/committer via env so init's commits succeed headless."""
    for var in ("NAME", "EMAIL"):
        monkeypatch.setenv(f"GIT_AUTHOR_{var}", "Tester" if var == "NAME" else "t@t")
        monkeypatch.setenv(f"GIT_COMMITTER_{var}", "Tester" if var == "NAME" else "t@t")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "")  # ignore the machine's global git config


def _init(root: Path, runtimes=("opencode", "claude")) -> None:
    root.mkdir(parents=True, exist_ok=True)
    engine = Engine()
    initop.register(engine)
    engine.run("init", root, write=True, name="demo", runtimes=list(runtimes))


def _tracked(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=False
    )
    return out.stdout.splitlines()


def _log(repo: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--oneline"], capture_output=True, text=True, check=False
    )
    return out.stdout.strip()


def test_product_gitignore_shields_brain_and_runtimes(tmp_path) -> None:
    root = tmp_path / "proj"
    _init(root)
    ignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".aspis/" in ignore
    assert ".opencode/" in ignore
    assert ".claude/" in ignore


def test_product_repo_excludes_brain_and_runtime(tmp_path) -> None:
    root = tmp_path / "proj"
    _init(root)
    tracked = _tracked(root)
    assert "AGENTS.md" in tracked  # root guide stays in the product repo
    assert not any(p.startswith(".aspis/") for p in tracked)
    assert not any(p.startswith((".opencode/", ".claude/")) for p in tracked)


def test_brain_shadow_repo_tracks_brain_but_not_generated(tmp_path) -> None:
    root = tmp_path / "proj"
    _init(root)
    assert (root / ".aspis" / ".git").is_dir()
    brain = _tracked(root / ".aspis")
    assert brain, "shadow repo should track the scaffolded brain"
    # Generated/local artifacts are excluded by the brain's own .gitignore.
    assert not any("FILE_REGISTRY" in p for p in brain)
    assert not any("CURRENT_STATE" in p for p in brain)
    assert not any(p.startswith("current/export-") for p in brain)


def test_commit_routing_two_independent_histories(tmp_path) -> None:
    root = tmp_path / "proj"
    _init(root)
    assert _log(root), "product repo should have its own commit"
    assert _log(root / ".aspis"), "brain shadow repo should have its own commit"
    # The brain commit is NOT in the product history.
    assert ".aspis" not in subprocess.run(
        ["git", "-C", str(root), "log", "--name-only"], capture_output=True, text=True
    ).stdout


def test_brain_verb_commits_on_event(tmp_path, capsys) -> None:
    """`aspis brain commit` records an on-demand brain event in the shadow repo."""
    from argparse import Namespace

    from aspis.commands import brain

    root = tmp_path / "proj"
    _init(root)
    before = _log(root / ".aspis")
    (root / ".aspis" / "context" / "note.md").write_text("a brain change\n", encoding="utf-8")

    rc = brain._run(Namespace(brain_action="commit", path=str(root), message="chore(brain): note"))
    assert rc == 0
    after = _log(root / ".aspis")
    assert after != before and "chore(brain): note" in after
    # The brain event never reaches the product history.
    assert "chore(brain): note" not in _log(root)


def test_brain_verb_errors_without_shadow_repo(tmp_path, capsys) -> None:
    """On a project with no shadow repo, the verb explains rather than crashing."""
    from argparse import Namespace

    from aspis.commands import brain

    root = tmp_path / "legacy"
    (root / ".aspis").mkdir(parents=True)
    rc = brain._run(Namespace(brain_action="status", path=str(root)))
    assert rc == 1
    assert "no brain shadow repo" in capsys.readouterr().out


def test_runtime_status_reports_the_integrity_record(tmp_path, capsys) -> None:
    """`aspis runtime status` surfaces the runtime change-log counts (no git)."""
    from argparse import Namespace

    from aspis.commands import runtime

    root = tmp_path / "proj"
    _init(root)
    rc = runtime._run(Namespace(runtime_action="status", path=str(root), number=10))
    assert rc == 0
    out = capsys.readouterr().out
    assert "runtime integrity" in out
    assert "files under integrity:" in out


def test_build_loop_routes_each_change_to_its_lane(tmp_path) -> None:
    """A feature that changes product source AND the brain lands one commit in each repo."""
    from argparse import Namespace

    from aspis.commands import brain

    root = tmp_path / "proj"
    _init(root)
    # Product source change → product repo (explicit path, like `aspis commit`).
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "src/app.py"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "feat: add app"], check=True)
    # Brain change → shadow repo (the committer's `aspis brain commit` path).
    (root / ".aspis" / "context" / "note.md").write_text("design note\n", encoding="utf-8")
    brain._run(
        Namespace(brain_action="commit", path=str(root), message="chore(brain): design note")
    )

    product_log = _log(root)
    brain_log = _log(root / ".aspis")
    assert "feat: add app" in product_log and "chore(brain): design note" not in product_log
    assert "chore(brain): design note" in brain_log and "feat: add app" not in brain_log
    # Source never leaked into the brain repo; brain never leaked into product.
    assert "src/app.py" not in subprocess.run(
        ["git", "-C", str(root / ".aspis"), "ls-files"], capture_output=True, text=True
    ).stdout


def test_committer_catalog_routes_both_lanes() -> None:
    """The single writer (R-004) must be allowed to commit the brain lane too (F-022)."""
    from aspis import resources

    body = (resources.catalog_dir() / "agents" / "committer.md").read_text(encoding="utf-8")
    assert "aspis brain commit*" in body  # brain shadow-repo commit permission
    assert "aspis commit*" in body  # product commit path still present
    # The committer is told to never commit the runtime dirs.
    assert "never commit" in body.lower()


def test_legacy_project_is_not_auto_shadowed(tmp_path) -> None:
    """A product repo that already tracks .aspis must not be auto-converted (needs migration)."""
    root = tmp_path / "legacy"
    (root / ".aspis").mkdir(parents=True)
    (root / ".aspis" / "keep.md").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "legacy"], check=True)

    created = gitops.init_brain_repo(root, write=True)
    assert created is False
    assert not (root / ".aspis" / ".git").is_dir()
