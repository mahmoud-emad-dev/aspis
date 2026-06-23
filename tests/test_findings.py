"""Tests for the findings flow (F-014 T-11): catalog emit -> store -> `aspis findings`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from aspis import findings, resources
from aspis.cli import main as cli_main
from aspis.engine import build_engine
from aspis.operations import register_all


def _init(root: Path) -> None:
    engine = build_engine()
    register_all(engine)
    engine.run("init", root, write=True, no_git=True)


def _catalog_findings():
    """Load the stdlib catalog emitter the runtime guard uses (by path, to avoid a name clash)."""
    path = resources.catalog_dir() / "scripts" / "hooks" / "findings.py"
    spec = importlib.util.spec_from_file_location("catalog_findings", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_emit_is_read_by_the_package(tmp_path) -> None:
    # The guard emits with the stdlib catalog module; the package reads the same file.
    catalog = _catalog_findings()
    catalog.emit(tmp_path, "scope", "out-of-scope edit attempted: foo.py", "scope-guard")
    items = findings.load(tmp_path)
    assert len(items) == 1
    assert items[0]["detail"] == "out-of-scope edit attempted: foo.py"
    catalog.emit(tmp_path, "scope", "out-of-scope edit attempted: foo.py", "scope-guard")
    assert len(findings.load(tmp_path)) == 1  # deduped on kind+detail


def test_findings_list_empty(tmp_path, capsys) -> None:
    _init(tmp_path)
    assert cli_main(["findings", str(tmp_path)]) == 0
    assert "no open findings" in capsys.readouterr().out


def test_findings_list_and_resolve(tmp_path, capsys) -> None:
    _init(tmp_path)
    _catalog_findings().emit(tmp_path, "scope", "out-of-scope edit attempted: bar.py")
    assert cli_main(["findings", str(tmp_path)]) == 0
    assert "bar.py" in capsys.readouterr().out
    assert cli_main(["findings", str(tmp_path), "--resolve", "1"]) == 0
    assert findings.load(tmp_path) == []


def test_findings_clear(tmp_path) -> None:
    _init(tmp_path)
    catalog = _catalog_findings()
    catalog.emit(tmp_path, "scope", "a")
    catalog.emit(tmp_path, "scope", "b")
    assert cli_main(["findings", str(tmp_path), "--clear"]) == 0
    assert findings.load(tmp_path) == []
