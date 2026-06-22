"""Tests for the F-013 install & first-run UX: paths, runtime inventory, uninstall.

``ASPIS_HOME`` relocates the machine-wide dirs, so every test points it at a
temp dir and never touches the real home.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from aspis import paths, runtime_inventory
from aspis.cli import main


def test_aspis_home_overrides_all_locations(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert paths.config_home() == tmp_path / "config"
    assert paths.data_home() == tmp_path / "data"
    assert paths.cache_home() == tmp_path / "cache"


def test_global_config_path_uses_config_home(monkeypatch, tmp_path: Path) -> None:
    from aspis import project

    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert project.global_config_path() == tmp_path / "config" / "project.yaml"


def test_detect_runtimes_reports_discovered_names(monkeypatch) -> None:
    """The runtime set is discovered from data/runtimes/*.yaml — no hardcoded list."""
    from aspis import resources

    monkeypatch.setattr(runtime_inventory.shutil, "which", lambda exe: "/bin/" + exe)
    detected = runtime_inventory.detect_runtimes()
    discovered = set(resources.runtime_defs())
    assert discovered  # at least the bundled runtimes exist
    assert set(detected) == discovered
    assert runtime_inventory.available(detected) == sorted(discovered)


def test_available_filters_absent_runtimes() -> None:
    detected = {"claude": "/bin/claude", "opencode": None, "cursor": "/bin/cursor"}
    assert runtime_inventory.available(detected) == ["claude", "cursor"]


def test_save_inventory_writes_to_data_home(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    detected = {"claude": "/bin/claude", "opencode": None}
    path = runtime_inventory.save_inventory(detected)
    assert path == tmp_path / "data" / "runtime-inventory.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert payload["runtimes"]["claude"]["available"] is True
    assert payload["runtimes"]["claude"]["path"] == "/bin/claude"
    assert "capabilities" in payload["runtimes"]["claude"]  # declared caps travel with detection
    assert payload["runtimes"]["opencode"]["available"] is False


def test_doctor_verbose_shows_locations(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    assert main(["doctor", str(tmp_path), "--verbose"]) == 0
    out = capsys.readouterr().out
    assert "Installation:" in out
    assert str(tmp_path / "config") in out
    assert "Runtimes" in out


def test_uninstall_dry_run_removes_nothing(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    (tmp_path / "data").mkdir(parents=True)
    assert main(["uninstall"]) == 0
    assert (tmp_path / "data").exists(), "dry-run must not delete"
    assert "Nothing was removed" in capsys.readouterr().out


def test_uninstall_write_removes_state_but_can_keep_config(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path))
    for sub in ("config", "data", "cache"):
        (tmp_path / sub).mkdir(parents=True)
    assert main(["uninstall", "--write", "--keep-config"]) == 0
    assert (tmp_path / "config").exists(), "--keep-config must preserve config"
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "cache").exists()


def test_uninstall_handles_missing_state(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("ASPIS_HOME", str(tmp_path / "absent"))
    assert main(["uninstall", "--write"]) == 0
    assert "nothing to remove" in capsys.readouterr().out
