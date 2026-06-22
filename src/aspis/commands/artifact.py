"""``aspis artifact`` — create a feature artifact from a template, ready to fill.

The tool the build/review agents trigger so they never hand-author (and never
invent the *shape* of) a report, review, or acceptance file. It copies the project's
own template into the active feature's folder, stamping the deterministic fields
(feature id + title, task, date), and leaves the body for the agent to fill with real
results. Running it is one command — cheaper than re-deriving the format each time.

Creation is **mode-gated** (D-013): a lean mode skips the artifacts it does not earn
(e.g. ``vibe`` writes no reports) unless ``--force`` is passed — so artifacts are
created lazily, only when the mode warrants them.
"""

from __future__ import annotations

import argparse
import json
from datetime import date as _date
from pathlib import Path

from aspis import project, resources

#: kind -> (template path under .aspis/templates, target sub-path, (mode knob, skip-values)).
#: ``{task}`` in the target is replaced by the task id (or ``feature`` when none).
#: A ``None`` knob means the artifact is never mode-gated.
_KINDS: dict[str, tuple[str, str, tuple[str | None, frozenset[str]]]] = {
    "build": ("report/build.md", "reports/{task}-build.md", ("docs", frozenset({"none"}))),
    "feature": ("report/feature.md", "reports/feature-report.md", ("docs", frozenset({"none"}))),
    "review": (
        "review/review.md",
        "reviews/{task}-review.md",
        ("build_review", frozenset({"light"})),
    ),
    "test": ("review/test.md", "reviews/{task}-test.md", ("test_depth", frozenset({"gate"}))),
    "acceptance": ("planning/ACCEPTANCE.md", "ACCEPTANCE.md", (None, frozenset())),
}


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``artifact`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "artifact",
        help="Create a feature artifact (build/feature/review/test/acceptance) from its template.",
    )
    parser.add_argument("kind", choices=sorted(_KINDS), help="Which artifact to create.")
    parser.add_argument("--task", help="Task id (e.g. T-03); omit for a feature-level artifact.")
    parser.add_argument("--path", default=".", help="Project directory (default: current).")
    parser.add_argument("--force", action="store_true", help="Ignore mode gating and overwrite.")
    parser.set_defaults(func=_run)


def _active_feature(root: Path) -> dict:
    """Return the active-feature pointer, or ``{}`` when absent/unreadable."""
    pointer = root / ".aspis" / "current" / "active_feature.json"
    try:
        data = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _mode_knob(root: Path, mode: str, knob: str) -> str:
    """Return ``modes.yaml[mode][knob]`` for the project (empty string when absent).

    Tier-agnostic: ``resources.config`` finds ``modes.yaml`` whether it sits flat or
    under ``config/policy``.
    """
    data = resources.config("modes.yaml", root)
    return str(((data.get("modes") or {}).get(mode) or {}).get(knob, ""))


def _fill(text: str, *, feature_id: str, title: str, task: str) -> str:
    """Substitute the deterministic placeholders the agent should not have to type."""
    return (
        text.replace("<feature-id>", feature_id)
        .replace("<Feature Title>", title)
        .replace("<task-id>", task)
        .replace("<date>", _date.today().isoformat())
    )


def _run(args: argparse.Namespace) -> int:
    """Stamp the chosen template into the active feature's folder."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    feature = _active_feature(root)
    feature_path = feature.get("path")
    if not feature_path:
        print("No active feature — set .aspis/current/active_feature.json first.")
        return 1

    template_rel, target_tmpl, (knob, skip) = _KINDS[args.kind]
    mode = str(feature.get("mode", ""))
    if not args.force and knob and _mode_knob(root, mode, knob) in skip:
        print(f"skip: '{args.kind}' is not created in '{mode}' mode (--force to override).")
        return 0

    template = root / ".aspis" / "templates" / template_rel
    if not template.is_file():
        print(f"template not found: {template_rel}; re-run `aspis init` to ship templates.")
        return 1

    task = args.task or "feature"
    destination = root / feature_path / target_tmpl.format(task=task)
    if destination.exists() and not args.force:
        print(f"exists: {destination.relative_to(root).as_posix()} (--force to overwrite).")
        return 0

    body = _fill(
        template.read_text(encoding="utf-8"),
        feature_id=str(feature.get("id", "")),
        title=str(feature.get("title", "")),
        task=task if args.task else "",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8", newline="\n")
    print(f"created {destination.relative_to(root).as_posix()} — fill it with real results.")
    return 0
