"""Tests for the export snapshot/log/hash helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aspis.export import ProtectionError, _append_log, _hash_file, _load_snapshot, _save_snapshot
from aspis.protect import sha256_text


def test_load_snapshot_returns_default_when_absent(tmp_path: Path) -> None:
    snapshot = _load_snapshot(tmp_path)
    assert snapshot == {"version": 1, "paths": {}}


def test_load_snapshot_round_trips_saved_snapshot(tmp_path: Path) -> None:
    original = {"version": 1, "paths": {"a/b.md": "abc123", "c/d.md": "def456"}}
    _save_snapshot(tmp_path, original)
    loaded = _load_snapshot(tmp_path)
    assert loaded == original


def test_load_snapshot_raises_on_corrupted_json(tmp_path: Path) -> None:
    path = tmp_path / ".aspis" / "current" / "export-snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json at all", encoding="utf-8")
    with pytest.raises(ProtectionError):
        _load_snapshot(tmp_path)


def test_load_snapshot_reset_discards_corruption(tmp_path: Path) -> None:
    path = tmp_path / ".aspis" / "current" / "export-snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json at all", encoding="utf-8")
    snapshot = _load_snapshot(tmp_path, reset=True)
    assert snapshot == {"version": 1, "paths": {}}


def test_save_snapshot_writes_atomic_file(tmp_path: Path) -> None:
    snapshot = {"version": 1, "paths": {"x.md": "hash"}}
    _save_snapshot(tmp_path, snapshot)
    dest = tmp_path / ".aspis" / "current" / "export-snapshot.json"
    assert dest.exists()
    assert json.loads(dest.read_text(encoding="utf-8")) == snapshot
    assert list(dest.parent.glob("*.tmp")) == []


def test_save_snapshot_creates_parent_directory(tmp_path: Path) -> None:
    snapshot = {"version": 1, "paths": {}}
    _save_snapshot(tmp_path, snapshot)
    assert (tmp_path / ".aspis" / "current").is_dir()
    assert (tmp_path / ".aspis" / "current" / "export-snapshot.json").exists()


def test_append_log_writes_json_lines(tmp_path: Path) -> None:
    entries = [{"kind": "ADD", "path": "a.md"}, {"kind": "UPDATE", "path": "b.md"}]
    _append_log(tmp_path, entries)
    log_path = tmp_path / ".aspis" / "current" / "export-log.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == entries[0]
    assert json.loads(lines[1]) == entries[1]


def test_append_log_is_append_only(tmp_path: Path) -> None:
    _append_log(tmp_path, [{"n": 1}])
    _append_log(tmp_path, [{"n": 2}])
    log_path = tmp_path / ".aspis" / "current" / "export-log.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"n": 1}
    assert json.loads(lines[1]) == {"n": 2}


def test_hash_file_missing_returns_none(tmp_path: Path) -> None:
    assert _hash_file(tmp_path / "missing.txt") is None


def test_hash_file_existing_matches_sha256_text(tmp_path: Path) -> None:
    path = tmp_path / "file.md"
    text = "hello world\r\nsecond line\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    assert _hash_file(path) == sha256_text(text)
