#!/usr/bin/env python3
"""Cross-reference validation — check that catalog references resolve correctly.

Purpose: Scan a catalog directory of agent bodies, extract references to
skills, workflows, delegates, and runtimes, then verify that each reference
resolves to an existing file or known entity. Output a table of
resolved/broken/orphan references.

Does Not: Modify any files. Does not validate reference *content*, only existence.
Does not handle runtime-generated files — only catalog source.

Used By: research-lead (cross-reference checks), system-lead (runtime validation).

Stdlib-only. Deterministic. --help shows usage.

Usage:
  python cross_ref.py <catalog_dir>
  python cross_ref.py --catalog src/aspis/data/catalog
  python cross_ref.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _frontmatter(text: str) -> str:
    """Return the YAML frontmatter block (between the first two ``---`` fences)."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def _list_field(frontmatter: str, key: str) -> set[str]:
    """Parse a YAML list field (flow ``[a, b]`` or block ``- a``) from the
    frontmatter, stripping inline ``#`` comments, quotes, and brackets.

    Deliberately a small stdlib parser, not a full YAML load — we only need the
    three list fields this tool checks. Parsing the structured frontmatter (not
    scraping the whole body) is what keeps references free of false positives.
    """
    items: set[str] = set()
    lines = frontmatter.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"\s*{key}:\s*(.*)$", line)
        if not m:
            continue
        rest = re.sub(r"\s+#.*$", "", m.group(1)).strip()
        if rest.startswith("["):  # flow list on the same line
            for it in rest.strip("[]").split(","):
                it = it.strip().strip("\"'")
                if it and it != "none":
                    items.add(it)
        else:  # block list on the following indented "- " lines
            for nxt in lines[i + 1:]:
                bm = re.match(r"\s*-\s+(.*)$", nxt)
                if not bm:
                    if nxt.strip():  # a non-list, non-blank line ends the block
                        break
                    continue
                it = re.sub(r"\s+#.*$", "", bm.group(1)).strip().strip("\"'")
                if it and it != "none":
                    items.add(it)
        break
    return items


def discover_runtimes(catalog_dir: Path) -> set[str]:
    """Discover runtime names from ``data/runtimes/*.yaml`` (sibling of the
    catalog) so the set is not hand-maintained. Falls back to the shipped two."""
    rt_dir = catalog_dir.parent / "runtimes"
    names = {p.stem for p in rt_dir.glob("*.yaml")} if rt_dir.exists() else set()
    return (names or {"opencode", "claude"}) | {"all"}


def find_catalog_files(catalog_dir: Path) -> list[Path]:
    """Find all agent body .md files in the catalog."""
    agents_dir = catalog_dir / "agents"
    if agents_dir.exists():
        return sorted(agents_dir.glob("*.md"))
    return []


def find_skill_files(catalog_dir: Path) -> set[str]:
    """Find all skill names from SKILL.md files."""
    skills = set()
    skills_dir = catalog_dir / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.add(skill_dir.name)
    return skills


def find_workflow_files(project_root: Path) -> set[str]:
    """Find all workflow names from .aspis/workflows/."""
    workflows = set()
    wf_dir = project_root / ".aspis" / "workflows"
    if wf_dir.exists():
        for wf in wf_dir.glob("*.md"):
            workflows.add(wf.stem)
    return workflows


def extract_references(text: str, known_workflows: set[str]) -> dict[str, set[str]]:
    """Extract structured references from one agent body.

    ``skills`` / ``delegates`` / ``runtimes`` come from the YAML frontmatter —
    the authoritative, structured source. Workflow references are detected by
    scanning the prose body for known workflow names as whole words, since
    agents cite workflows in prose, not in a frontmatter field. (Limiting
    workflow matches to *known* names means a workflow ref can never be a false
    "broken" — only orphan detection uses it.)
    """
    fm = _frontmatter(text)
    body = text[len(fm) + 3:] if fm else text
    return {
        "skill": _list_field(fm, "skills"),
        "delegate": _list_field(fm, "delegates"),
        "runtime": _list_field(fm, "runtimes"),
        "workflow": {w for w in known_workflows if re.search(rf"\b{re.escape(w)}\b", body)},
    }


def resolve_references(
    agent_refs: dict[str, dict[str, set[str]]],
    known_skills: set[str],
    known_workflows: set[str],
    known_agents: set[str],
    known_runtimes: set[str],
) -> list[dict]:
    """Resolve all references and return results."""
    results = []

    for agent_name, refs in agent_refs.items():
        for ref_type, ref_set in refs.items():
            for ref in ref_set:
                if ref_type == "skill":
                    resolved = ref in known_skills
                elif ref_type == "workflow":
                    resolved = ref in known_workflows
                elif ref_type == "delegate":
                    resolved = ref in known_agents
                elif ref_type == "runtime":
                    resolved = ref in known_runtimes or ref in known_agents
                else:
                    resolved = False

                results.append({
                    "agent": agent_name,
                    "ref_type": ref_type,
                    "reference": ref,
                    "resolved": resolved,
                    "status": "resolved" if resolved else "broken",
                })

    # Find orphans: known entities not referenced by any agent
    all_refd_skills = set()
    all_refd_workflows = set()
    all_refd_agents = set()
    for refs in agent_refs.values():
        all_refd_skills.update(refs.get("skill", set()))
        all_refd_workflows.update(refs.get("workflow", set()))
        all_refd_agents.update(refs.get("delegate", set()))

    orphan_skills = known_skills - all_refd_skills
    orphan_workflows = known_workflows - all_refd_workflows
    orphan_agents = known_agents - all_refd_agents - set(agent_refs.keys())  # Exclude self

    # Add orphan entries as "orphan" status
    for skill in orphan_skills:
        results.append({
            "agent": "—",
            "ref_type": "skill",
            "reference": skill,
            "resolved": True,
            "status": "orphan",
        })
    for wf in orphan_workflows:
        results.append({
            "agent": "—",
            "ref_type": "workflow",
            "reference": wf,
            "resolved": True,
            "status": "orphan",
        })
    for agent in orphan_agents:
        results.append({
            "agent": "—",
            "ref_type": "delegate",
            "reference": agent,
            "resolved": True,
            "status": "orphan",
        })

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-reference validation for catalog agent bodies."
    )
    parser.add_argument(
        "catalog_dir", nargs="?", default=None,
        help="path to catalog directory (e.g., src/aspis/data/catalog)"
    )
    parser.add_argument(
        "--catalog", default=None, help="named path to catalog directory"
    )
    parser.add_argument(
        "--root", default=".", help="project root (for workflow discovery)"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    catalog_dir = Path(args.catalog or args.catalog_dir or "src/aspis/data/catalog")
    project_root = Path(args.root)

    if not catalog_dir.exists():
        print(f"error: catalog directory not found: {catalog_dir}", file=sys.stderr)
        return 1

    # Discover known entities
    agent_files = find_catalog_files(catalog_dir)
    known_agents = {f.stem for f in agent_files}
    known_skills = find_skill_files(catalog_dir)
    known_workflows = find_workflow_files(project_root)
    known_runtimes = discover_runtimes(catalog_dir)

    # Extract references from each agent
    agent_refs = {}
    for agent_file in agent_files:
        agent_name = agent_file.stem
        try:
            text = agent_file.read_text(encoding="utf-8")
        except OSError:
            continue
        agent_refs[agent_name] = extract_references(text, known_workflows)

    # Resolve
    results = resolve_references(
        agent_refs, known_skills, known_workflows, known_agents, known_runtimes
    )

    if args.json:
        summary = {
            "total_refs": len([r for r in results if r["status"] != "orphan"]),
            "resolved": len([r for r in results if r["status"] == "resolved"]),
            "broken": len([r for r in results if r["status"] == "broken"]),
            "orphan": len([r for r in results if r["status"] == "orphan"]),
            "results": results,
        }
        print(json.dumps(summary, indent=2))
        return 0

    # Pretty-print table
    broken = [r for r in results if r["status"] == "broken"]
    orphans = [r for r in results if r["status"] == "orphan"]
    resolved = [r for r in results if r["status"] == "resolved"]

    print(f"Catalog: {catalog_dir}")
    print(
        f"Agents: {len(agent_files)} | Skills: {len(known_skills)} | "
        f"Workflows: {len(known_workflows)}"
    )
    print(f"References: {len(resolved)} resolved, {len(broken)} broken, {len(orphans)} orphan")
    print()

    if broken:
        print("BROKEN REFERENCES:")
        print(f"  {'Agent':<25} {'Type':<12} {'Reference'}")
        print("  " + "-" * 65)
        for r in broken:
            print(f"  {r['agent']:<25} {r['ref_type']:<12} {r['reference']}")

    if orphans:
        print("\nORPHAN ENTITIES (not referenced):")
        print(f"  {'Type':<12} {'Name'}")
        print("  " + "-" * 40)
        for r in orphans:
            print(f"  {r['ref_type']:<12} {r['reference']}")

    if not broken and not orphans:
        print("[OK] All references resolve. No orphans found.")

    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
