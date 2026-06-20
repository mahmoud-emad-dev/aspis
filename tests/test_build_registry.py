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
    (tmp_path / "notes.md").write_text("# Design notes\n\nstuff\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "noise").write_text("ignore me", encoding="utf-8")

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    registry = tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml"
    files = yaml.safe_load(registry.read_text(encoding="utf-8"))["files"]

    assert files["src/app.py"] == {"kind": "python", "purpose": "The app entrypoint."}
    assert files["notes.md"]["purpose"] == "Design notes"  # plain markdown: heading extracted
    assert not any(".git" in key for key in files)  # skipped dirs excluded


def test_common_map_is_authoritative_for_known_meta_files(tmp_path) -> None:
    # Known meta-files whose own first line is a title/section, not a purpose:
    # the curated common purpose wins over whatever the file content would yield.
    (tmp_path / "README.md").write_text("# My Project\n\nstuff\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("# Python\n__pycache__/\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT License\n\n...\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_text("# generated\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "gate.yml").write_text("name: gate\non: [push]\n", encoding="utf-8")

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    files = yaml.safe_load(
        (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").read_text(encoding="utf-8")
    )["files"]
    assert files["README.md"]["purpose"] == "Project overview and entry point"
    assert files[".gitignore"]["purpose"] == "Git ignore rules"  # not the stray "# Python"
    assert files["LICENSE"]["purpose"] == "Project license"
    assert files["pyproject.toml"]["purpose"] == "Python project metadata and tooling config"
    assert files["uv.lock"]["purpose"] == "Dependency lockfile (generated)"  # *.lock pattern
    assert files[".github/workflows/gate.yml"]["purpose"] == "CI workflow"  # workflow pattern


def test_common_map_is_fallback_when_file_has_no_purpose(tmp_path) -> None:
    # A non-authoritative file with no extractable purpose: common map fills it,
    # but a real docstring still wins over a generic common entry.
    (tmp_path / "data.json").write_text('{"k": 1}\n', encoding="utf-8")  # no common entry → blank
    (tmp_path / "Makefile").write_text("all:\n\techo hi\n", encoding="utf-8")  # common fills it

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    files = yaml.safe_load(
        (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").read_text(encoding="utf-8")
    )["files"]
    assert files["data.json"]["purpose"] == ""  # nothing matched
    assert files["Makefile"]["purpose"] == "Build/automation targets"


def test_common_purposes_json_extends_and_overrides_defaults(tmp_path) -> None:
    import json

    (tmp_path / "weird.xyz").write_text("binary-ish\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    index = tmp_path / ".aspis" / "index"
    index.mkdir(parents=True)
    (index / "COMMON_PURPOSES.json").write_text(
        json.dumps(
            {
                "exact": {"LICENSE": "Custom license terms"},  # override a built-in default
                "patterns": {"*.xyz": "Project widget file"},  # extend with a new pattern
            }
        ),
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    files = yaml.safe_load((index / "FILE_REGISTRY.yaml").read_text(encoding="utf-8"))["files"]
    assert files["LICENSE"]["purpose"] == "Custom license terms"  # project override wins
    assert files["weird.xyz"]["purpose"] == "Project widget file"  # user-added pattern


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
