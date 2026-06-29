"""``aspis subsystem`` — create and index Architecture Memory subsystem files.

Architecture Memory (F-019) keeps one living markdown file per subsystem under
``.aspis/architecture/subsystems/``, recording *intent* — why a subsystem exists,
what it owns, what it must never own, how it integrates, and what it guarantees —
so no future session has to reconstruct the design from code, git, or lost chats.

These instance files are **project brain content**, not catalog assets (only the
*template* is cataloged), so this verb owns their creation rather than ``aspis
artifact`` (which is feature-scoped). ``new`` stamps the template into a new file;
``index`` rebuilds the advisory ``INDEX.md`` from each file's header. Updating a
subsystem file's body is an agent/human act, gated by explicit user confirmation —
this tool only scaffolds and indexes, it never edits intent.
"""

from __future__ import annotations

import argparse
import re
from datetime import date as _date
from pathlib import Path

from aspis import project

#: Where subsystem files live, relative to the project root.
_SUBSYS_REL = ".aspis/architecture/subsystems"
#: Template shipped to the brain by ``aspis init`` (see profiles/base.yaml).
_TEMPLATE_REL = ".aspis/templates/context/subsystem.md"

_STATUS_RE = re.compile(r"^- \*\*Status:\*\*\s*(.+?)\s*$", re.MULTILINE)
_ONELINER_RE = re.compile(r"^- \*\*One-liner:\*\*\s*(.+?)\s*$", re.MULTILINE)
_REVIEWED_RE = re.compile(r"\*\*Last reviewed:\*\*\s*(.+?)\s*$", re.MULTILINE)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``subsystem`` verb and its ``new`` / ``index`` actions."""
    parser = subparsers.add_parser(
        "subsystem",
        help="Create or index Architecture Memory subsystem files.",
    )
    parser.set_defaults(func=lambda _a: parser.print_help() or 0)
    actions = parser.add_subparsers(dest="action", metavar="<action>")

    new = actions.add_parser("new", help="Scaffold a new subsystem intent file from the template.")
    new.add_argument("name", help="Subsystem name (e.g. 'models-intelligence').")
    new.add_argument("--path", default=".", help="Project directory (default: current).")
    new.add_argument("--force", action="store_true", help="Overwrite if the file exists.")
    new.set_defaults(func=_new)

    index = actions.add_parser("index", help="Rebuild the subsystems INDEX.md from file headers.")
    index.add_argument("--path", default=".", help="Project directory (default: current).")
    index.set_defaults(func=_index)


def _slug(name: str) -> str:
    """Normalise a subsystem name to a file-safe slug (lowercase, hyphens)."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "subsystem"


def _meta(text: str) -> tuple[str, str, str]:
    """Pull (status, one-liner, last-reviewed) from a subsystem file's header."""
    status = m.group(1) if (m := _STATUS_RE.search(text)) else "?"
    one_liner = m.group(1) if (m := _ONELINER_RE.search(text)) else ""
    reviewed = m.group(1) if (m := _REVIEWED_RE.search(text)) else ""
    return status, one_liner, reviewed


def _build_index(directory: Path) -> str:
    """Render INDEX.md from every ``<name>.md`` (except INDEX.md) in *directory*."""
    rows = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        status, one_liner, reviewed = _meta(path.read_text(encoding="utf-8"))
        rows.append(f"| [{path.stem}]({path.name}) | {status} | {one_liner} | {reviewed} |")
    table = "\n".join(rows) if rows else "| _(none yet)_ |  |  |  |"
    return (
        "# Architecture Memory — Subsystems Index\n\n"
        "Living per-subsystem intent (why it exists, what it owns, what it guarantees, how it\n"
        "evolved). One file per subsystem. This index is advisory and rebuilt from each file's\n"
        "header by `aspis subsystem index`.\n\n"
        "> Only **architectural** change updates a subsystem file (intent/responsibility/"
        "boundary/contract/integration, or add/remove) — never bug fixes, refactors, renames.\n"
        "> No file changes without explicit user confirmation. Trigger is the planning phase.\n\n"
        "| Subsystem | Status | One-liner | Last reviewed |\n"
        "|---|---|---|---|\n"
        f"{table}\n"
    )


def _write_index(directory: Path) -> Path:
    """(Re)write INDEX.md for *directory* and return its path."""
    index_path = directory / "INDEX.md"
    index_path.write_text(_build_index(directory), encoding="utf-8", newline="\n")
    return index_path


def _new(args: argparse.Namespace) -> int:
    """Scaffold ``.aspis/architecture/subsystems/<slug>.md`` from the template."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    template = root / _TEMPLATE_REL
    if not template.is_file():
        print(f"template not found: {_TEMPLATE_REL}; re-run `aspis init` to ship templates.")
        return 1

    slug = _slug(args.name)
    directory = root / _SUBSYS_REL
    destination = directory / f"{slug}.md"
    if destination.exists() and not args.force:
        print(f"exists: {destination.relative_to(root).as_posix()} (--force to overwrite).")
        return 0

    today = _date.today().isoformat()
    body = template.read_text(encoding="utf-8").replace("<name>", slug).replace("<date>", today)
    directory.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8", newline="\n")
    _write_index(directory)
    print(f"created {destination.relative_to(root).as_posix()} — fill it with the real intent.")
    return 0


def _index(args: argparse.Namespace) -> int:
    """Rebuild INDEX.md from the subsystem files' headers."""
    root = Path(args.path).resolve()
    if not project.is_project(root):
        print(f"No ASPIS project here ({root}). Run `aspis init` first.")
        return 1

    directory = root / _SUBSYS_REL
    if not directory.is_dir():
        print(f"no subsystems yet ({_SUBSYS_REL}); create one with `aspis subsystem new <name>`.")
        return 0
    index_path = _write_index(directory)
    print(f"rebuilt {index_path.relative_to(root).as_posix()}")
    return 0
