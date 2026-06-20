"""Tests for the ``aspis tests`` ledger — cache a pass, skip re-running unchanged files."""

from __future__ import annotations

from pathlib import Path

from aspis.cli import main


def _project(tmp_path: Path) -> Path:
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "src" / "test_app.py").write_text(
        "def test_x():\n    assert True\n", encoding="utf-8"
    )
    return tmp_path


def test_check_is_stale_with_no_record(tmp_path) -> None:
    root = _project(tmp_path)
    rc = main(
        ["tests", "check", "src/app.py", "src/test_app.py", "--scope", "F-001", "--path", str(root)]
    )
    assert rc == 1  # nothing recorded yet → must run


def test_record_then_check_is_cached(tmp_path) -> None:
    root = _project(tmp_path)
    files = ["src/app.py", "src/test_app.py"]
    assert (
        main(
            ["tests", "record", *files, "--result", "pass", "--scope", "F-001", "--path", str(root)]
        )
        == 0
    )
    # Unchanged → cached pass → skip re-running.
    assert main(["tests", "check", *files, "--scope", "F-001", "--path", str(root)]) == 0
    assert (root / ".aspis" / "index" / "test-ledger.json").is_file()


def test_change_invalidates_the_cache(tmp_path) -> None:
    root = _project(tmp_path)
    files = ["src/app.py", "src/test_app.py"]
    main(["tests", "record", *files, "--result", "pass", "--scope", "F-001", "--path", str(root)])

    (root / "src" / "app.py").write_text("x = 2  # changed\n", encoding="utf-8")
    rc = main(["tests", "check", *files, "--scope", "F-001", "--path", str(root)])
    assert rc == 1  # a covered file changed → stale


def test_recorded_fail_is_not_treated_as_cached_pass(tmp_path) -> None:
    root = _project(tmp_path)
    files = ["src/app.py"]
    main(["tests", "record", *files, "--result", "fail", "--scope", "F-001", "--path", str(root)])
    assert main(["tests", "check", *files, "--scope", "F-001", "--path", str(root)]) == 1
