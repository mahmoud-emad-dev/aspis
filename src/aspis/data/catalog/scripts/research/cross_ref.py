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


# Reference patterns in agent body text
REF_PATTERNS = {
    "skill": re.compile(r"(?i)(?:skills?|skill):\s*\[?([^\],\n]+)\]?"),
    "workflow": re.compile(r"(?i)(?:workflows?|workflow):\s*\[?([^\],\n]+)\]?"),
    "delegate": re.compile(r"(?i)(?:delegates?|delegate):\s*\[?([^\],\n]+)\]?"),
    "runtime": re.compile(r"(?i)(?:runtimes?|runtime):\s*\[?([^\],\n]+)\]?"),
}

# Known runtime names
KNOWN_RUNTIMES = {"opencode", "claude", "all"}


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


def extract_references(text: str) -> dict[str, set[str]]:
    """Extract all references from agent body text."""
    refs = {}
    for ref_type, pattern in REF_PATTERNS.items():
        found = set()
        for match in pattern.finditer(text):
            ref_text = match.group(1).strip()
            # Skip empty brackets like "[]"
            if ref_text in ("", "[", "]", "[]"):
                continue
            # Split on commas and clean
            for item in re.split(r"[,|]\s*", ref_text):
                item = item.strip().strip('"').strip("'").strip("[").strip("]")
                if item and item not in ("", "none"):
                    found.add(item)
        refs[ref_type] = found
    return refs


def resolve_references(
    agent_refs: dict[str, dict[str, set[str]]],
    known_skills: set[str],
    known_workflows: set[str],
    known_agents: set[str],
) -> list[dict]:
    """Resolve all references and return results."""
    results = []

    for agent_name, refs in agent_refs.items():
        for ref_type, ref_set in refs.items():
            for ref in ref_set:
                if ref_type == "skill":
                    resolved = ref in known_skills
                    source_set = known_skills
                elif ref_type == "workflow":
                    resolved = ref in known_workflows
                    source_set = known_workflows
                elif ref_type == "delegate":
                    resolved = ref in known_agents
                    source_set = known_agents
                elif ref_type == "runtime":
                    resolved = ref in KNOWN_RUNTIMES or ref in known_agents
                    source_set = KNOWN_RUNTIMES
                else:
                    resolved = False
                    source_set = set()

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
    for agent_name, refs in agent_refs.items():
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

    # Extract references from each agent
    agent_refs = {}
    for agent_file in agent_files:
        agent_name = agent_file.stem
        try:
            text = agent_file.read_text(encoding="utf-8")
        except OSError:
            continue
        agent_refs[agent_name] = extract_references(text)

    # Resolve
    results = resolve_references(agent_refs, known_skills, known_workflows, known_agents)

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
    print(f"Agents: {len(agent_files)} | Skills: {len(known_skills)} | Workflows: {len(known_workflows)}")
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
