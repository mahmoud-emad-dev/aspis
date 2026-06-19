#!/usr/bin/env python3
"""Compile TASKS.md into one self-contained packet per task.

Self-contained (stdlib only). Ships into ``.aspis/scripts/planning/``. Reads the
active (or named) feature's ``TASKS.md``, parses each task line, and renders a
packet from ``.aspis/templates/TASK_PACKET.md`` into the feature's ``tasks/``
folder — filling the *deterministic* fields (feature id, task id, title, the
allowed-files list from the task's paths) and leaving the rich fields (context,
skeleton, acceptance, review routing) as guidance for the Build Lead to enrich
from its whole-feature context.

Task line format (see TASKS.md):
  ``- [ ] T-NN [P?] [US?] <description> (`path/one`, `path/two`)``

Usage:
  python3 task_compile.py [root] [--feature F-001] [--force] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_TASK_RE = re.compile(r"^- \[[ xX]\]\s+(T-\d+)\b(.*)$")
_MARKER_RE = re.compile(r"\[(?:P|US\d+|US\?)\]", re.IGNORECASE)
_PATH_SUFFIXES = (".py", ".md", ".yaml", ".yml", ".toml", ".json", ".txt", ".sh", ".cfg", ".ini")


@dataclass
class TaskRef:
    """One parsed task line."""

    task_id: str
    title: str
    paths: list[str] = field(default_factory=list)


@dataclass
class CompileResult:
    """What the compile produced (or would, with ``write=False``)."""

    feature_id: str
    feature_dir: str
    packets: dict[str, str] = field(default_factory=dict)  # task_id -> rel path
    skipped: list[str] = field(default_factory=list)


def _looks_like_path(token: str) -> bool:
    return "/" in token or token.endswith(_PATH_SUFFIXES)


def parse_tasks(text: str) -> list[TaskRef]:
    """Parse every task line out of a TASKS.md body."""
    tasks: list[TaskRef] = []
    for line in text.splitlines():
        match = _TASK_RE.match(line.strip())
        if not match:
            continue
        task_id, rest = match.group(1), match.group(2)
        paths = [t for t in re.findall(r"`([^`]+)`", rest) if _looks_like_path(t)]
        title = _MARKER_RE.sub("", rest)
        title = re.sub(r"`[^`]+`", "", title)  # drop backticked paths
        title = re.sub(r"\(\s*[,\s]*\)", "", title)  # drop emptied parens
        title = title.strip(" .()-")
        tasks.append(TaskRef(task_id=task_id, title=title or task_id, paths=paths))
    return tasks


def _resolve_feature(root: Path, feature: str | None) -> tuple[str, Path, str]:
    """Return ``(feature_id, feature_dir, feature_title)`` for the target feature."""
    features = root / ".aspis" / "features"
    if feature:
        matches = sorted(features.glob(f"{feature}*"))
        if not matches:
            raise SystemExit(f"no feature directory matches {feature!r}")
        feature_dir = matches[0]
        feature_id = feature_dir.name.split("-", 1)[0] if "-" in feature_dir.name else feature
        return feature_id, feature_dir, feature_dir.name
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        raise SystemExit("no active feature; pass --feature F-NNN")
    data = json.loads(pointer.read_text(encoding="utf-8"))
    return data["id"], root / data["path"], data.get("title", data["id"])


def _render_packet(template: str, feature_id: str, feature_title: str, task: TaskRef) -> str:
    """Fill the deterministic packet fields; leave the rest as guidance."""
    text = template.replace("<feature-id>", feature_id)
    text = text.replace("<feature title>", feature_title)
    text = text.replace("T-NN", task.task_id)
    text = text.replace("<Short Title>", task.title)
    if task.paths:
        bullets = "\n".join(f"- `{p}`" for p in task.paths)
        text = text.replace("- `<exact/path/one>`\n- `<exact/path/two>`", bullets)
    return text


def compile_tasks(
    root: Path, *, feature: str | None = None, force: bool = False, write: bool = False
) -> CompileResult:
    """Render a packet per task in the feature's TASKS.md."""
    feature_id, feature_dir, feature_title = _resolve_feature(root, feature)
    result = CompileResult(
        feature_id=feature_id, feature_dir=feature_dir.relative_to(root).as_posix()
    )

    tasks_md = feature_dir / "TASKS.md"
    if not tasks_md.is_file():
        raise SystemExit(f"no TASKS.md in {result.feature_dir}")
    template = (root / ".aspis" / "templates" / "TASK_PACKET.md").read_text(encoding="utf-8")

    out_dir = feature_dir / "tasks"
    for task in parse_tasks(tasks_md.read_text(encoding="utf-8")):
        target = out_dir / f"{task.task_id}.md"
        rel = target.relative_to(root).as_posix()
        if target.exists() and not force:
            result.skipped.append(rel)
            continue
        result.packets[task.task_id] = rel
        if write:
            out_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(
                _render_packet(template, feature_id, feature_title, task), encoding="utf-8"
            )
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Compile TASKS.md into task packets.")
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument("--feature", default=None, help="feature id/prefix (default: active)")
    parser.add_argument("--force", action="store_true", help="overwrite existing packets")
    parser.add_argument("--dry-run", action="store_true", help="show what would be written")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    result = compile_tasks(
        Path(args.root).resolve(),
        feature=args.feature,
        force=args.force,
        write=not args.dry_run,
    )
    verb = "would write" if args.dry_run else "wrote"
    print(f"{result.feature_id}: {len(result.packets)} packet(s)")
    for task_id, rel in result.packets.items():
        print(f"  {verb}: {task_id} → {rel}")
    for rel in result.skipped:
        print(f"  skip (exists): {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
