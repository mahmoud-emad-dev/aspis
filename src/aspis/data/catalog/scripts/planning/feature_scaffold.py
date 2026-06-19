#!/usr/bin/env python3
"""Scaffold a new feature: directory, planning artifacts, and active pointer.

Self-contained (stdlib only). Ships into ``.aspis/scripts/planning/`` and runs
with the project's own Python. Deterministic mechanics so the Planning Lead spends
its judgement on content, not bookkeeping:

  - allocate the next ``F-NNN`` id and a slug from the name,
  - create ``.aspis/features/F-NNN-slug/`` with a ``tasks/`` packet folder,
  - copy SPEC/PLAN/TASKS from ``.aspis/templates/`` with the id/title filled in,
  - record ``.aspis/current/active_feature.json``,
  - create+checkout the ``feature/F-NNN-slug`` branch when git is present.

Mode does not change which artifacts are created — every feature gets all three
templates and their inline mode hints tell the lead what to compress or skip.

Usage:
  python3 feature_scaffold.py [root] --name "Add export retries" [--slug retries]
                              [--mode production] [--no-branch]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_TEMPLATES = ("SPEC.md", "PLAN.md", "TASKS.md")
_STOP = {"a", "an", "the", "to", "for", "of", "and", "add", "make", "in", "on"}


@dataclass
class ScaffoldResult:
    """What the scaffold produced (or would produce, with ``write=False``)."""

    feature_id: str
    slug: str
    title: str
    feature_dir: str
    branch: str
    mode: str
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def _slugify(name: str) -> str:
    """Derive a short kebab-case slug from a feature name."""
    words = [w for w in re.sub(r"[^a-z0-9]+", " ", name.lower()).split() if w not in _STOP]
    slug = "-".join(words)[:50].strip("-")
    return slug or "feature"


def _next_id(features_dir: Path) -> str:
    """Return the next ``F-NNN`` id by scanning existing feature folders."""
    highest = 0
    if features_dir.is_dir():
        for child in features_dir.iterdir():
            match = re.match(r"F-(\d+)", child.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"F-{highest + 1:03d}"


def _fill(text: str, feature_id: str, title: str) -> str:
    """Substitute the template placeholders for this feature."""
    return text.replace("<feature-id>", feature_id).replace("<Feature Title>", title)


def prepare_feature(
    root: Path,
    name: str,
    *,
    slug: str | None = None,
    mode: str = "production",
    create_branch: bool = True,
    write: bool = False,
) -> ScaffoldResult:
    """Plan (and optionally perform) the scaffold for a new feature."""
    brain = root / ".aspis"
    features_dir = brain / "features"
    feature_id = _next_id(features_dir)
    slug = _slugify(slug or name)
    title = name.strip()
    feature_dir = features_dir / f"{feature_id}-{slug}"
    branch = f"feature/{feature_id}-{slug}"

    result = ScaffoldResult(
        feature_id=feature_id,
        slug=slug,
        title=title,
        feature_dir=feature_dir.relative_to(root).as_posix(),
        branch=branch,
        mode=mode,
    )

    templates_dir = brain / "templates"
    for template in _TEMPLATES:
        source = templates_dir / template
        target = feature_dir / template
        if not source.is_file():
            result.skipped.append(f"missing template: {template}")
            continue
        result.created.append(target.relative_to(root).as_posix())
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                _fill(source.read_text(encoding="utf-8"), feature_id, title), encoding="utf-8"
            )

    tasks_dir = feature_dir / "tasks"
    result.created.append(tasks_dir.relative_to(root).as_posix() + "/")
    if write:
        tasks_dir.mkdir(parents=True, exist_ok=True)
        (tasks_dir / ".gitkeep").write_text("", encoding="utf-8")

    pointer = brain / "current" / "active_feature.json"
    result.created.append(pointer.relative_to(root).as_posix())
    if write:
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text(
            json.dumps(
                {
                    "id": feature_id,
                    "slug": slug,
                    "title": title,
                    "path": result.feature_dir,
                    "branch": branch,
                    "mode": mode,
                    "phase": "plan",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if create_branch and write and (root / ".git").is_dir():
        subprocess.run(
            ["git", "-C", str(root), "checkout", "-q", "-b", branch],
            capture_output=True,
            check=False,
        )
        result.created.append(f"branch: {branch}")

    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Scaffold a new ASPIS feature.")
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument("--name", required=True, help="feature name / one-line goal")
    parser.add_argument("--slug", default=None, help="override the derived slug")
    parser.add_argument("--mode", default="production", help="vibe | mvp | production")
    parser.add_argument("--no-branch", action="store_true", help="do not create a git branch")
    parser.add_argument(
        "--dry-run", action="store_true", help="show what would be created, write nothing"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    result = prepare_feature(
        Path(args.root).resolve(),
        args.name,
        slug=args.slug,
        mode=args.mode,
        create_branch=not args.no_branch,
        write=not args.dry_run,
    )
    verb = "would create" if args.dry_run else "created"
    print(f"{result.feature_id} ({result.mode}) → {result.feature_dir}")
    for item in result.created:
        print(f"  {verb}: {item}")
    for item in result.skipped:
        print(f"  skipped: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
