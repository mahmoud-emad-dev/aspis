"""Tests for the three enforcement-hook gates that previously shipped untested (R-005).

`secret_scan` (the secret-leak blocker), `precommit` (the R-009 protected-paths gate),
and `runtime_guard` (the tool-use veto) are run exactly as the installed hooks run them:
the self-contained scripts are added to ``sys.path`` and imported by name. The gates
shell out to real git, so each test builds a throwaway repo and runs from inside it.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

from aspis import resources

_HOOKS = resources.catalog_dir() / "scripts" / "hooks"
sys.path.insert(0, str(_HOOKS))

import precommit  # noqa: E402
import runtime_guard  # noqa: E402
import secret_scan  # noqa: E402

_JUNK = "junk:\n  ghost_prefixes: ['=']\n  keep: ['LICENSE']\n  skip_dirs: ['.git']\n"


def _repo(root: Path, *, hooks_yaml: str, feature: dict | None = None) -> Path:
    """Init a git repo with the brain config the hooks read."""
    root.mkdir(parents=True, exist_ok=True)
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    cfg = root / ".aspis" / "config"
    cfg.mkdir(parents=True)
    (cfg / "hooks.yaml").write_text(hooks_yaml, encoding="utf-8")
    current = root / ".aspis" / "current"
    current.mkdir(parents=True)
    (current / "active_feature.json").write_text(
        json.dumps(feature or {"id": "F-006", "slug": "hooks"}), encoding="utf-8"
    )
    return root


def _stage(root: Path, rel: str, content: str) -> None:
    """Write *rel* under *root* and stage it."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "--", rel], check=True)


# --- T-08: secret_scan -------------------------------------------------------


def test_secret_scan_find_matches_added_lines_only() -> None:
    diff = (
        "diff --git a/app.py b/app.py\n"
        "+++ b/app.py\n"  # a header that itself starts with '+' must be ignored
        "+aws = 'AKIAIOSFODNN7EXAMPLE'\n"  # an added secret
        "-aws = 'OLD'\n"  # a removed line is not scanned
        " context = 1\n"  # unchanged context is not scanned
    )
    hits = secret_scan.find(diff, [r"AKIA[0-9A-Z]{16}"])
    assert hits == ["aws = 'AKIAIOSFODNN7EXAMPLE'"]


def test_secret_scan_main_exits_nonzero_on_staged_secret(tmp_path, monkeypatch) -> None:
    root = _repo(tmp_path, hooks_yaml="secrets:\n  - 'AKIA[0-9A-Z]{16}'\n" + _JUNK)
    monkeypatch.chdir(root)

    _stage(root, "clean.py", "x = 1\n")
    assert secret_scan.main() == 0  # nothing secret-shaped staged

    _stage(root, "leak.py", "key = 'AKIAIOSFODNN7EXAMPLE'\n")
    assert secret_scan.main() == 1  # the staged secret trips the gate


# --- T-09: precommit R-009 protected-paths gate ------------------------------


def test_precommit_blocks_protected_path_unless_approved(tmp_path, monkeypatch) -> None:
    root = _repo(
        tmp_path,
        hooks_yaml="enforcement: block\nprotected_paths:\n  - 'rules/**'\n" + _JUNK,
    )
    monkeypatch.chdir(root)
    monkeypatch.delenv("ASPIS_ALLOW_PROTECTED", raising=False)
    _stage(root, "rules/system.md", "do not touch\n")

    # Block mode + an unapproved protected path → the gate fails the commit.
    assert precommit.main() == 1

    # The documented escape hatch approves the change.
    monkeypatch.setenv("ASPIS_ALLOW_PROTECTED", "1")
    assert precommit.main() == 0


def test_precommit_warn_mode_never_blocks(tmp_path, monkeypatch) -> None:
    root = _repo(
        tmp_path,
        hooks_yaml="enforcement: warn\nprotected_paths:\n  - 'rules/**'\n" + _JUNK,
    )
    monkeypatch.chdir(root)
    monkeypatch.delenv("ASPIS_ALLOW_PROTECTED", raising=False)
    _stage(root, "rules/system.md", "touched\n")

    # Default warn mode reports but never vetoes — safe to ship to others.
    assert precommit.main() == 0


# --- T-10: runtime_guard tool-use veto ---------------------------------------


def test_runtime_guard_parses_claude_pretooluse_stdin(monkeypatch) -> None:
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "/abs/src/app.py"}}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert runtime_guard._paths_from_stdin() == ["/abs/src/app.py"]


def test_runtime_guard_vetoes_out_of_scope_only_in_block_mode(tmp_path, monkeypatch) -> None:
    feature = {"id": "F-006", "slug": "hooks", "scope": {"allowed": ["src/**"]}}
    root = _repo(tmp_path, hooks_yaml="enforcement: block\n" + _JUNK, feature=feature)
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["runtime_guard.py", "docs/out.md"])

    # docs/ is outside the allowed src/** → exit 2 vetoes the edit in block mode.
    assert runtime_guard.main() == 2

    # The same edit only warns (exit 0) under the default warn mode.
    (root / ".aspis" / "config" / "hooks.yaml").write_text("enforcement: warn\n" + _JUNK, "utf-8")
    assert runtime_guard.main() == 0
