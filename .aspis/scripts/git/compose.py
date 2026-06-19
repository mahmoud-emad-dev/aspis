#!/usr/bin/env python3
"""compose.py — build a convention-valid commit message (F-007).

Purpose:
    Compose ``type(F-NNN[/T-NN | /T-NN..T-MM]): title`` plus a bullet body and an
    optional ``Tasks:`` trailer, so the committer never hand-formats a message. The
    feature id is read from ``.aspis/current/active_feature.json``; the type, task,
    title, bullets, and trailer come from argv.

Does Not:
    Stage or commit anything (that is ``aspis commit``), and it does not define the
    message rules — it self-validates against the single source (F-006's
    ``commitmsg.validate`` + ``commit-convention.yaml``) when those ship alongside.

Used By:
    src/aspis/commands/commit.py (the ``aspis commit`` tool), the committer agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reuse the F-006 hook validator + convention loader so the message rules live in
# exactly one place. Best-effort: if the hooks are not shipped, composition still
# works and the commit-msg hook validates at commit time.
_HOOKS = Path(__file__).resolve().parent.parent / "hooks"
if _HOOKS.is_dir() and str(_HOOKS) not in sys.path:
    sys.path.insert(0, str(_HOOKS))
try:
    import _config  # type: ignore  # noqa: E402
    import commitmsg  # type: ignore  # noqa: E402
except ImportError:  # pragma: no cover - hooks not shipped
    _config = None  # type: ignore[assignment]
    commitmsg = None  # type: ignore[assignment]


def force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (Windows cp1252)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def active_feature_id(root: Path) -> str:
    """The active feature id (e.g. ``F-007``), or ``""`` when none is set."""
    pointer = root / ".aspis" / "current" / "active_feature.json"
    if not pointer.is_file():
        return ""
    try:
        return str(json.loads(pointer.read_text(encoding="utf-8")).get("id", ""))
    except json.JSONDecodeError:
        return ""


def build_scope(root: Path, feature: str, task: str) -> str:
    """Resolve the scope: ``F-NNN`` or ``F-NNN/T-NN[..T-MM]`` (empty ⇒ lifecycle)."""
    fid = feature or active_feature_id(root)
    if not fid:
        return ""
    return f"{fid}/{task}" if task else fid


def compose(
    *,
    type_: str,
    title: str,
    scope: str = "",
    bullets: list[str] | None = None,
    tasks: str = "",
) -> str:
    """Render the full commit message from its parts."""
    head = f"{type_}({scope}): {title}" if scope else f"{type_}: {title}"
    lines = [head]
    body = [f"- {b}" for b in (bullets or [])]
    if body:
        lines += ["", *body]
    if tasks:
        lines += ["", f"Tasks: {tasks}"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Print the composed message to stdout; exit non-zero if it fails self-validation."""
    force_utf8_stdio()
    parser = argparse.ArgumentParser(description="Compose a convention-valid commit message.")
    parser.add_argument("--type", required=True, dest="type_", help="feat, fix, docs, chore, …")
    parser.add_argument("--title", required=True, help="imperative subject (no trailing period)")
    parser.add_argument("--task", default="", help="T-NN or a span T-NN..T-MM")
    parser.add_argument("--feature", default="", help="override the active feature id")
    parser.add_argument("--bullet", action="append", default=[], help="a body bullet (repeatable)")
    parser.add_argument("--tasks", default="", help="Tasks: trailer (auto-set from a span)")
    parser.add_argument("--no-scope", action="store_true", help="lifecycle commit (omit scope)")
    parser.add_argument("--root", default=".", help="project root (default: current dir)")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    root = Path(args.root).resolve()
    scope = "" if args.no_scope else build_scope(root, args.feature, args.task)
    # A multi-task commit auto-carries the span as its Tasks: trailer.
    tasks = args.tasks or (args.task if ".." in args.task else "")
    message = compose(
        type_=args.type_, title=args.title, scope=scope, bullets=args.bullet, tasks=tasks
    )

    if commitmsg is not None and _config is not None:
        errors = commitmsg.validate(message, _config.commit_convention(root))
        if errors:
            for error in errors:
                print(f"[compose] {error}", file=sys.stderr)
            return 1

    sys.stdout.write(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
