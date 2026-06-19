#!/usr/bin/env python3
"""Validate a feature's phase prerequisites — the gate before plan/tasks/build.

Self-contained (stdlib only). Ships into ``.aspis/scripts/planning/``. Enforces the
loop's ordering — no plan without a spec, no tasks without a plan, no build without
tasks — relaxed by mode: a mode that skips architecture (e.g. vibe) does not require
PLAN.md. The mode's knobs are read from ``.aspis/config/modes.yaml`` (the single
source), via a minimal reader for our own flat file shape so no YAML dependency is
needed in the target project.

Exit code is 0 when prerequisites are met, 1 when something is missing — so this can
be used directly as a gate.

Usage:
  python3 prereq_validate.py [root] --phase build [--feature F-001] [--mode mvp]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import _console

# Standard ordering: each phase needs the artifacts of the phases before it.
_PHASE_REQUIRES = {
    "plan": ["SPEC.md"],
    "tasks": ["SPEC.md", "PLAN.md"],
    "build": ["SPEC.md", "PLAN.md", "TASKS.md"],
}


@dataclass
class ValidationResult:
    """The outcome of a prerequisite check for one phase."""

    feature_id: str
    phase: str
    mode: str
    required: list[str] = field(default_factory=list)
    present: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing


def _read_mode_knob(modes_file: Path, mode: str, knob: str) -> str | None:
    """Read one scalar knob for *mode* from our flat 2-space modes.yaml.

    Deliberately minimal — it understands only the shape this project writes
    (``modes:`` → 2-space mode key → 4-space ``knob: value``), so target projects
    need no YAML library. Returns None if not found.
    """
    if not modes_file.is_file():
        return None
    in_modes = False
    current = None
    for raw in modes_file.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0:
            in_modes = line.startswith("modes:")
            continue
        if not in_modes:
            continue
        if indent == 2 and line.endswith(":"):
            current = line[:-1].strip()
        elif indent >= 4 and current == mode and line.split(":", 1)[0].strip() == knob:
            value = line.split(":", 1)[1]
            return value.split("#", 1)[0].strip()
    return None


def _resolve(root: Path, feature: str | None, mode: str | None) -> tuple[str, Path, str]:
    """Return ``(feature_id, feature_dir, mode)`` from args or the active pointer."""
    features = root / ".aspis" / "features"
    if feature:
        matches = sorted(features.glob(f"{feature}*"))
        if not matches:
            raise SystemExit(f"no feature directory matches {feature!r}")
        return matches[0].name.split("-", 1)[0], matches[0], (mode or "production")
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        raise SystemExit("no active feature; pass --feature F-NNN")
    data = json.loads(pointer.read_text(encoding="utf-8"))
    return data["id"], root / data["path"], (mode or data.get("mode", "production"))


def validate(
    root: Path, phase: str, *, feature: str | None = None, mode: str | None = None
) -> ValidationResult:
    """Check that *phase*'s prerequisite artifacts exist for the feature."""
    if phase not in _PHASE_REQUIRES:
        raise SystemExit(f"unknown phase {phase!r}; expected one of {list(_PHASE_REQUIRES)}")
    feature_id, feature_dir, mode = _resolve(root, feature, mode)

    required = list(_PHASE_REQUIRES[phase])
    # Mode relaxation: a mode that skips architecture does not require a PLAN.md.
    if _read_mode_knob(root / ".aspis" / "config" / "modes.yaml", mode, "architecture") == "skip":
        required = [r for r in required if r != "PLAN.md"]

    result = ValidationResult(feature_id=feature_id, phase=phase, mode=mode, required=required)
    for artifact in required:
        if (feature_dir / artifact).is_file():
            result.present.append(artifact)
        else:
            result.missing.append(artifact)
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Exit 1 when a prerequisite is missing."""
    _console.force_utf8_stdio()
    parser = argparse.ArgumentParser(description="Validate feature phase prerequisites.")
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument(
        "--phase", required=True, choices=sorted(_PHASE_REQUIRES), help="target phase"
    )
    parser.add_argument("--feature", default=None, help="feature id/prefix (default: active)")
    parser.add_argument(
        "--mode", default=None, help="override the mode (default: active/production)"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    result = validate(Path(args.root).resolve(), args.phase, feature=args.feature, mode=args.mode)
    status = "OK" if result.ok else "BLOCKED"
    print(f"[{status}] {result.feature_id} → {result.phase} ({result.mode})")
    for artifact in result.present:
        print(f"  present: {artifact}")
    for artifact in result.missing:
        print(f"  MISSING: {artifact}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
