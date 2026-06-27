"""``aspis validate-runtime`` — structural validity sweep over the agent catalog.

Walks every agent markdown file under the catalog, parses its YAML frontmatter,
and reports per-agent pass/fail with file:line evidence on any problem. Exits
non-zero when any check fails, so the cross-agent consistency claim
(``aspis validate-runtime`` shows 0 broken skill refs and 0 orphan delegates)
is machine-enforced, not just asserted in prose. Stdlib-only at the
algorithmic level — only the project's own ``aspis.catalog.split_frontmatter``
and ``aspis.resources.catalog_dir`` are imported, both already proven on the
catalog files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis.catalog import split_frontmatter
from aspis.resources import catalog_dir

#: Frontmatter fields every agent must declare (the agent-body standard).
#: Order is preserved in failure reports so the diff against an existing
#: agent reads top-to-bottom like the file itself.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "mode",
    "model",
    "temperature",
    "tools",
    "permissions",
    "delegates",
    "skills",
    "runtimes",
    "export_scope",
)

#: Status label, ASCII-safe for any console.
_LABEL_PASS = "PASS"
_LABEL_FAIL = "FAIL"

#: The opening ``---`` of a YAML frontmatter block is always line 1 of a valid
#: catalog file. Missing-field evidence points there so the user knows where to
#: add the field.
_FRONTMATTER_OPEN_LINE = 1


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``validate-runtime`` verb."""
    parser = subparsers.add_parser(
        "validate-runtime",
        help=(
            "Validate every catalog agent: required frontmatter fields present, "
            "skill refs resolve, delegate refs resolve (no orphans)."
        ),
    )
    parser.set_defaults(func=_run)


def _frontmatter_field_line(text: str, field: str) -> int | None:
    """Return the 1-indexed line of a top-level YAML field, or ``None`` if absent.

    Only matches at column 0 (no leading whitespace), so nested keys under
    ``permissions:`` or items under ``tools:``/``skills:``/``delegates:`` are not
    mistaken for the top-level field declaration. The scan stops at the closing
    ``---`` fence so a body that happens to contain ``name:`` does not match.
    """
    lines = text.splitlines()
    in_block = False
    for i, line in enumerate(lines, start=1):
        if line.strip() == "---":
            if in_block:
                break  # closing fence — frontmatter is over
            in_block = True
            continue
        if in_block and line.startswith(f"{field}:"):
            return i
    return None


def _check_agent(
    agent_path: Path,
    agents_dir: Path,
    skills_dir: Path,
) -> list[str]:
    """Return the list of failure messages for one agent file; ``[]`` if it passes."""
    failures: list[str] = []

    try:
        text = agent_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{agent_path.name}:{_FRONTMATTER_OPEN_LINE} unreadable: {exc}"]

    frontmatter, _body = split_frontmatter(text)

    # Required fields — presence only. Empty list/dict/None still counts as
    # declared; the field is the contract, not its value.
    for field in _REQUIRED_FIELDS:
        if field not in frontmatter:
            failures.append(
                f"{agent_path.name}:{_FRONTMATTER_OPEN_LINE} missing field: '{field}'"
            )

    # Skill refs — every name in ``skills`` must have a SKILL.md under its
    # own folder in the skills catalog.
    skills_line = _frontmatter_field_line(text, "skills")
    for skill in frontmatter.get("skills") or []:
        if not isinstance(skill, str):
            failures.append(
                f"{agent_path.name}:{skills_line or _FRONTMATTER_OPEN_LINE} "
                f"non-string skill ref: {skill!r}"
            )
            continue
        skill_path = skills_dir / skill / "SKILL.md"
        if not skill_path.is_file():
            failures.append(
                f"{agent_path.name}:{skills_line or _FRONTMATTER_OPEN_LINE} "
                f"missing skill ref: '{skill}' (expected {skill_path})"
            )

    # Delegate refs — every name in ``delegates`` must have a matching agent
    # .md in the agents catalog. This is the "no orphan delegates" check.
    delegates_line = _frontmatter_field_line(text, "delegates")
    for delegate in frontmatter.get("delegates") or []:
        if not isinstance(delegate, str):
            failures.append(
                f"{agent_path.name}:{delegates_line or _FRONTMATTER_OPEN_LINE} "
                f"non-string delegate ref: {delegate!r}"
            )
            continue
        delegate_path = agents_dir / f"{delegate}.md"
        if not delegate_path.is_file():
            failures.append(
                f"{agent_path.name}:{delegates_line or _FRONTMATTER_OPEN_LINE} "
                f"orphan delegate: '{delegate}' (expected {delegate_path})"
            )

    return failures


def _run(args: argparse.Namespace) -> int:
    """Walk every agent in the catalog and print a per-agent pass/fail report.

    Returns 0 when every agent passes every check; 1 if any agent has any
    finding. The summary line always prints so callers can parse it.
    """
    del args  # no CLI options yet

    catalog_root = catalog_dir()
    agents_dir = catalog_root / "agents"
    skills_dir = catalog_root / "skills"

    if not agents_dir.is_dir():
        print(f"agents directory not found: {agents_dir}")
        return 1

    agent_files = sorted(agents_dir.glob("*.md"))
    total = len(agent_files)
    passed = 0
    total_failures = 0

    for path in agent_files:
        failures = _check_agent(path, agents_dir, skills_dir)
        if failures:
            total_failures += len(failures)
            joined = "; ".join(failures)
            print(f"Agent: {path.stem} — {_LABEL_FAIL} ({joined})")
        else:
            passed += 1
            print(f"Agent: {path.stem} — {_LABEL_PASS}")

    print(f"\n{passed}/{total} agents passed. {total_failures} failures.")
    return 0 if total_failures == 0 else 1


if __name__ == "__main__":
    # Allow `python -m aspis.commands.validate_runtime` for ad-hoc runs in
    # addition to the normal `aspis validate-runtime` dispatch path.
    raise SystemExit(_run(argparse.Namespace()))
