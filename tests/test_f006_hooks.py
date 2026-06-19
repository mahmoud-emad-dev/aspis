"""Tests for the F-006 deterministic hooks — logic, enforcement modes, emission.

The hook scripts ship as self-contained modules under the catalog; they are added
to ``sys.path`` and imported by name, the same way the installed git hooks run them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from aspis import resources
from aspis.runtimes.claude import ClaudeAdapter
from aspis.runtimes.opencode import OpenCodeAdapter

_HOOKS = resources.catalog_dir() / "scripts" / "hooks"
sys.path.insert(0, str(_HOOKS))

import _config  # noqa: E402
import cleanup  # noqa: E402
import commitmsg  # noqa: E402
import gitignore  # noqa: E402
import scope  # noqa: E402

_CONVENTION = {
    "types": ["feat", "fix", "chore", "docs"],
    "subject": {"max_length": 72},
    "forbid_attribution": ["co-authored-by", "claude", "🤖"],
}


def _project(tmp_path: Path, *, scope_data: dict | None = None, enforcement: str = "warn") -> Path:
    """Build a minimal project brain with an active feature + hooks config."""
    cfg = tmp_path / ".aspis" / "config"
    cfg.mkdir(parents=True)
    (cfg / "hooks.yaml").write_text(
        f"enforcement: {enforcement}\n"
        "junk:\n  ghost_prefixes: ['=']\n  keep: ['LICENSE']\n  skip_dirs: ['.git']\n",
        encoding="utf-8",
    )
    feature: dict = {"id": "F-006", "slug": "hooks"}
    if scope_data is not None:
        feature["scope"] = scope_data
    current = tmp_path / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text(json.dumps(feature), encoding="utf-8")
    return tmp_path


# --- commit-message validation (pure) ---------------------------------------


@pytest.mark.parametrize(
    "message, ok",
    [
        ("feat(F-006/T-01..T-05): add core", True),
        ("chore: initialize project", True),  # scope optional for lifecycle commits
        ("Merge feature F-005: x", True),
        ("wip random text", False),
        ("feat(hooks): bad scope", False),
        ("feat(F-006): x\n\nCo-Authored-By: Claude", False),
    ],
)
def test_commitmsg_validation(message: str, ok: bool) -> None:
    assert (commitmsg.validate(message, _CONVENTION) == []) is ok


# --- scope decision ----------------------------------------------------------


def test_scope_permissive_without_declaration(tmp_path: Path) -> None:
    root = _project(tmp_path)  # no scope declared
    assert scope.violations(["anything/at/all.py"], root) == []


def test_scope_allowed_and_forbidden(tmp_path: Path) -> None:
    root = _project(tmp_path, scope_data={"allowed": ["src/**"], "forbidden": ["src/secret/**"]})
    assert scope.violations(["src/ok.py"], root) == []
    assert scope.violations(["docs/x.md"], root)  # outside allowed
    assert scope.violations(["src/secret/x.py"], root)  # forbidden wins


# --- housekeeping (junk + .gitkeep) ------------------------------------------


def test_cleanup_junk_and_gitkeep(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "=junk").write_text("x", encoding="utf-8")
    (root / "LICENSE").write_text("x", encoding="utf-8")
    pkg = root / "pkg"
    pkg.mkdir()
    (pkg / ".gitkeep").write_text("", encoding="utf-8")
    (pkg / "real.py").write_text("x", encoding="utf-8")

    result = cleanup.clean(root, ["=junk", "LICENSE"])
    assert "=junk" in result.junk and "LICENSE" not in result.junk
    assert not (root / "=junk").exists()
    assert "pkg/.gitkeep" in result.gitkeep and not (pkg / ".gitkeep").exists()
    assert not cleanup.clean(root, [])  # idempotent: nothing left to do


# --- gitignore maintainer (offline) ------------------------------------------


def test_gitignore_writes_block_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gitignore, "fetch", lambda stack: "__pycache__/\n*.pyc\n")
    assert gitignore.ensure(tmp_path, "python") is True
    body = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "aspis gitignore (python)" in body and "__pycache__/" in body
    assert gitignore.ensure(tmp_path, "python") is False  # no-op once current


# --- enforcement switch ------------------------------------------------------


def test_enforcement_modes(tmp_path: Path) -> None:
    assert _config.enforcement(tmp_path) == "warn"  # no config present
    assert _config.blocks(_project(tmp_path, enforcement="block")) is True
    assert _config.blocks(_project(tmp_path / "b", enforcement="warn")) is False


# --- runtime-hook emission (capability gating) -------------------------------


def test_runtime_hooks_emitted_per_runtime(tmp_path: Path) -> None:
    catalog = resources.catalog_dir()
    assert ClaudeAdapter().emit_runtime_hooks(catalog, tmp_path, write=True)
    assert (tmp_path / ".claude" / "settings.json").is_file()

    other = tmp_path / "oc"
    assert OpenCodeAdapter().emit_runtime_hooks(catalog, other, write=True)
    assert (other / ".opencode" / "plugins" / "scope-guard.ts").is_file()


def test_runtime_without_wiring_emits_nothing(tmp_path: Path) -> None:
    class Bare(OpenCodeAdapter):
        runtime_hooks = ()

    assert Bare().emit_runtime_hooks(resources.catalog_dir(), tmp_path, write=True) == []
