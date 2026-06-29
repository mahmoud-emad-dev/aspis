"""Tests for ``aspis subsystem`` — Architecture Memory file scaffolding + indexing (F-019)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from aspis.cli import main

_SUBSYS = Path(".aspis") / "architecture" / "subsystems"


def _project(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    return tmp_path


def test_new_creates_conformant_file_and_indexes_it(tmp_path) -> None:
    root = _project(tmp_path)
    rc = main(["subsystem", "new", "payments", "--path", str(root)])
    assert rc == 0

    created = root / _SUBSYS / "payments.md"
    text = created.read_text(encoding="utf-8")
    assert text.startswith("# Subsystem: payments")
    # Placeholders are stamped, dates filled.
    assert "<name>" not in text and "<date>" not in text
    assert date.today().isoformat() in text
    # The lean required sections are present.
    for heading in (
        "## Why it exists",
        "## Responsibilities & boundaries",
        "## Current behaviour",
        "## Integrations",
        "## System contracts",
        "## Changelog",
    ):
        assert heading in text

    index = (root / _SUBSYS / "INDEX.md").read_text(encoding="utf-8")
    assert "[payments](payments.md)" in index


def test_name_is_slugified(tmp_path) -> None:
    root = _project(tmp_path)
    rc = main(["subsystem", "new", "Models Intelligence", "--path", str(root)])
    assert rc == 0
    assert (root / _SUBSYS / "models-intelligence.md").is_file()


def test_new_does_not_overwrite_without_force(tmp_path) -> None:
    root = _project(tmp_path)
    main(["subsystem", "new", "auth", "--path", str(root)])
    target = root / _SUBSYS / "auth.md"
    target.write_text("EDITED INTENT\n", encoding="utf-8")

    main(["subsystem", "new", "auth", "--path", str(root)])  # no --force
    assert target.read_text(encoding="utf-8") == "EDITED INTENT\n"

    main(["subsystem", "new", "auth", "--path", str(root), "--force"])
    assert target.read_text(encoding="utf-8").startswith("# Subsystem: auth")


def test_index_rebuilds_from_headers(tmp_path) -> None:
    root = _project(tmp_path)
    main(["subsystem", "new", "alpha", "--path", str(root)])
    main(["subsystem", "new", "beta", "--path", str(root)])
    # Remove the index, then rebuild it from the files.
    (root / _SUBSYS / "INDEX.md").unlink()
    rc = main(["subsystem", "index", "--path", str(root)])
    assert rc == 0
    index = (root / _SUBSYS / "INDEX.md").read_text(encoding="utf-8")
    assert "[alpha](alpha.md)" in index and "[beta](beta.md)" in index


def test_no_project_is_reported(tmp_path, capsys) -> None:
    rc = main(["subsystem", "new", "x", "--path", str(tmp_path)])
    assert rc == 1
    assert "No ASPIS project" in capsys.readouterr().out
