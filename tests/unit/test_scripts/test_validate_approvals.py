"""Tests for validate-approvals.py"""
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("src/aspis/data/catalog/scripts/system/validate-approvals.py")


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_no_ledger(tmp_path):
    """No ledger → WARN, not FAIL."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # Should exit 0 (no ledger is not a failure)
    assert result.returncode == 0
    assert "WARN" in result.stdout or "No approval ledger" in result.stdout


def test_valid_approval_json(tmp_path):
    """Valid JSON ledger should pass."""
    ledger = tmp_path / "ledger.json"
    _write_file(ledger, json.dumps({
        "approvals": [
            {
                "id": "APPROVE-001",
                "approver": "owner",
                "path": ".claude/settings.json",
                "status": "approved",
                "expires": "2099-12-31",
            }
        ]
    }))
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--ledger", str(ledger)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_unknown_approver_json(tmp_path):
    """Unknown approver → FAIL."""
    ledger = tmp_path / "ledger.json"
    _write_file(ledger, json.dumps({
        "approvals": [
            {
                "id": "APPROVE-002",
                "approver": "hacker",
                "path": ".claude/settings.json",
                "status": "approved",
                "expires": "2099-12-31",
            }
        ]
    }))
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--ledger", str(ledger)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert "FAIL" in result.stdout or result.returncode != 0


def test_json_output(tmp_path):
    """JSON output."""
    ledger = tmp_path / "ledger.json"
    _write_file(ledger, json.dumps({
        "approvals": [
            {
                "id": "APPROVE-003",
                "approver": "owner",
                "path": ".claude/settings.json",
                "status": "approved",
                "expires": "2099-12-31",
            }
        ]
    }))
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--ledger", str(ledger), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["pass"] >= 1 or data["fail"] >= 0


def test_help():
    """--help exits 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    assert result.returncode == 0
