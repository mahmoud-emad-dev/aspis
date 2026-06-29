"""Tests for the ``aspis artifact`` command — template-driven, mode-gated artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from aspis.cli import main


def _project(tmp_path: Path, *, mode: str = "production") -> Path:
    """Init a project and point it at a feature folder in the given mode."""
    main(["init", str(tmp_path), "--write", "--no-git", "--name", "demo"])
    feature_dir = tmp_path / ".aspis" / "features" / "F-001-demo"
    feature_dir.mkdir(parents=True)
    pointer = tmp_path / ".aspis" / "current" / "active_feature.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)  # current/ is on-demand now
    pointer.write_text(
        json.dumps(
            {
                "id": "F-001",
                "title": "Demo feature",
                "path": ".aspis/features/F-001-demo",
                "mode": mode,
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_artifact_creates_filled_report(tmp_path) -> None:
    root = _project(tmp_path)
    rc = main(["artifact", "build", "--task", "T-01", "--path", str(root)])
    assert rc == 0

    report = root / ".aspis" / "features" / "F-001-demo" / "reports" / "T-01-build.md"
    text = report.read_text(encoding="utf-8")
    assert "F-001" in text and "Demo feature" in text and "T-01" in text
    assert "<date>" not in text and "<feature-id>" not in text  # placeholders stamped


def test_artifact_acceptance_is_never_gated(tmp_path) -> None:
    root = _project(tmp_path, mode="vibe")
    rc = main(["artifact", "acceptance", "--path", str(root)])
    assert rc == 0
    assert (root / ".aspis" / "features" / "F-001-demo" / "ACCEPTANCE.md").is_file()


def test_artifact_is_mode_gated(tmp_path) -> None:
    # vibe mode (docs: none) does not earn a build report — skipped, no file written.
    root = _project(tmp_path, mode="vibe")
    rc = main(["artifact", "build", "--task", "T-01", "--path", str(root)])
    assert rc == 0
    assert not (root / ".aspis" / "features" / "F-001-demo" / "reports").exists()

    # --force overrides the gate.
    rc = main(["artifact", "build", "--task", "T-01", "--path", str(root), "--force"])
    assert rc == 0
    assert (root / ".aspis" / "features" / "F-001-demo" / "reports" / "T-01-build.md").is_file()


def test_architecture_impact_created_in_production(tmp_path) -> None:
    root = _project(tmp_path)
    rc = main(["artifact", "architecture-impact", "--path", str(root)])
    assert rc == 0
    report = root / ".aspis" / "features" / "F-001-demo" / "ARCHITECTURE_IMPACT.md"
    assert report.is_file()
    assert "F-001" in report.read_text(encoding="utf-8")


def test_architecture_impact_skipped_in_vibe(tmp_path) -> None:
    # vibe (architecture: skip) does not earn an impact report — matches the loop gating.
    root = _project(tmp_path, mode="vibe")
    rc = main(["artifact", "architecture-impact", "--path", str(root)])
    assert rc == 0
    assert not (root / ".aspis" / "features" / "F-001-demo" / "ARCHITECTURE_IMPACT.md").exists()


def test_artifact_does_not_overwrite_without_force(tmp_path) -> None:
    root = _project(tmp_path)
    main(["artifact", "review", "--task", "T-02", "--path", str(root)])
    review = root / ".aspis" / "features" / "F-001-demo" / "reviews" / "T-02-review.md"
    review.write_text("EDITED BY REVIEWER\n", encoding="utf-8")

    main(["artifact", "review", "--task", "T-02", "--path", str(root)])  # no --force
    assert review.read_text(encoding="utf-8") == "EDITED BY REVIEWER\n"
