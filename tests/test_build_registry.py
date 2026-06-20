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


def _write_config(root, payload: dict) -> None:
    import json

    config = root / ".aspis" / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "purposes.json").write_text(json.dumps(payload), encoding="utf-8")


def test_purposes_config_one_file_covers_all_three_layers(tmp_path) -> None:
    # One .aspis/config/purposes.json holds explicit files, common names, and patterns.
    (tmp_path / "data.json").write_text('{"k": 1}\n', encoding="utf-8")  # no docstring
    (tmp_path / "app.py").write_text('"""Weak line."""\n', encoding="utf-8")  # docstring overridden
    (tmp_path / "weird.xyz").write_text("binary-ish\n", encoding="utf-8")  # via pattern
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")  # override a built-in name

    _write_config(
        tmp_path,
        {
            "_note": "agent/human-maintained file purposes",
            "files": {"data.json": "Seed config for the demo", "app.py": "The real entrypoint"},
            "names": {"LICENSE": "Custom license terms"},
            "patterns": {"*.xyz": "Project widget file"},
        },
    )

    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True)

    files = yaml.safe_load(
        (tmp_path / ".aspis" / "index" / "FILE_REGISTRY.yaml").read_text(encoding="utf-8")
    )["files"]
    assert files["data.json"]["purpose"] == "Seed config for the demo"  # files: filled
    assert files["app.py"]["purpose"] == "The real entrypoint"  # files: wins over docstring
    assert files["LICENSE"]["purpose"] == "Custom license terms"  # names: override built-in
    assert files["weird.xyz"]["purpose"] == "Project widget file"  # patterns: user-added


def test_check_reports_files_without_a_purpose(tmp_path) -> None:
    (tmp_path / "app.py").write_text('"""Has a purpose."""\n', encoding="utf-8")
    (tmp_path / "mystery.dat").write_text("opaque\n", encoding="utf-8")  # no purpose anywhere

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "mystery.dat" in result.stdout
    assert "app.py" not in result.stdout  # covered files are not reported

    # Register it, and --check passes.
    _write_config(tmp_path, {"files": {"mystery.dat": "Opaque fixture for the parser test"}})
    ok = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--check"], capture_output=True, text=True
    )
    assert ok.returncode == 0
