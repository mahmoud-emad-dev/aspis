"""Tests for the self-contained FILE_REGISTRY builder script.

Runs the shipped script exactly as a project would (via subprocess), so the test
covers the real artifact, not an in-process import.
"""

from __future__ import annotations

import subprocess
import sys

import yaml

from aspis import resources

SCRIPT = resources.catalog_dir() / "scripts" / "context" / "build_registry.py"


def test_builds_registry_with_docstring_purpose(tmp_path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        '"""The app entrypoint."""\n\nx = 1\n', encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# My Project\n\nstuff\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "noise").write_text("ignore me", encoding="utf-8")

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    registry = tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml"
    files = yaml.safe_load(registry.read_text(encoding="utf-8"))["files"]

    assert files["src/app.py"] == {"kind": "python", "purpose": "The app entrypoint."}
    assert files["README.md"]["purpose"] == "My Project"
    assert not any(".git" in key for key in files)  # skipped dirs excluded


def test_purposes_json_overrides_and_fills(tmp_path) -> None:
    import json

    # A data file that cannot carry a docstring, and a .py whose docstring we override.
    (tmp_path / "data.json").write_text('{"k": 1}\n', encoding="utf-8")
    (tmp_path / "app.py").write_text('"""Weak line."""\n', encoding="utf-8")
    index = tmp_path / ".aspis" / "index"
    index.mkdir(parents=True)
    (index / "PURPOSES.json").write_text(
        json.dumps(
            {
                "_note": "agent-maintained purposes for non-self-documenting files",
                "data.json": "Seed config for the demo",
                "app.py": "The real entrypoint",
            }
        ),
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    files = yaml.safe_load((index / "FILE_REGISTRY.yaml").read_text(encoding="utf-8"))["files"]
    assert files["data.json"]["purpose"] == "Seed config for the demo"  # filled from JSON
    assert files["app.py"]["purpose"] == "The real entrypoint"  # override wins over docstring
