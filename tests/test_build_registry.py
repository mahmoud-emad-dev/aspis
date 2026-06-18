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
