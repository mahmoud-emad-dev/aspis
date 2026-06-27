---
name: catalog-validator
description: Validate the catalog's structural integrity — all references resolve, no broken links, schemas valid, no orphan assets.
---

# catalog-validator

## Purpose
Before any system change is declared done, validate that the catalog is
structurally sound: every skill reference in every agent frontmatter resolves
to a `SKILL.md` file, every delegate reference resolves to a catalog agent,
every template and workflow reference points to an existing file, and no
asset is orphaned (referenced by nothing and owned by no one).

## When to use
- At step 5 of the system-lead's 6-step workflow (VALIDATE).
- After any change to an agent body's `skills:` or `delegates:` list.
- After authoring, renaming, or deleting a skill, template, or workflow.
- As part of the post-change validation sequence (`aspis validate-runtime`).

## Procedure
1. **Check skill references** — for every agent in `catalog/agents/`:
   - Parse the frontmatter `skills:` list.
   - For each skill name, verify `catalog/skills/<name>/SKILL.md` exists.
   - Flag any skill referenced but not found → BROKEN_REF.
2. **Check delegate references** — for every agent:
   - Parse the frontmatter `delegates:` list.
   - For each delegate name, verify `catalog/agents/<name>.md` exists.
   - Flag any delegate referenced but not found → ORPHAN_DELEGATE.
3. **Check workflow/template references** — scan agent bodies for references to
   `.aspis/workflows/<name>.md` or `catalog/templates/<path>`:
   - Verify each referenced file exists.
   - Flag any broken path reference → BROKEN_PATH.
4. **Check orphans** — for every skill in `catalog/skills/`:
   - Search all agent frontmatters for a reference to that skill name.
   - If no agent references the skill → ORPHAN_SKILL (warn, not error — a
     skill may be newly authored and not yet wired).
5. **Check frontmatter schema** — for every agent:
   - Verify all 11 required fields per the agent body standard are present.
   - Verify `mode` is one of: `vibe`, `mvp`, `production` (or `primary`/`subagent`
     for legacy compatibility).
   - Verify `model` is one of: `cheap`, `standard`, `deep`.
6. **Emit the report** — per-agent pass/fail with file:line evidence for every
   failure. Exit 0 when all agents pass; exit 1 when any agent has a BROKEN_REF
   or ORPHAN_DELEGATE.

## Outputs
- A validation report: per-agent status (PASS / FAIL with specific failures).
- For each failure: `file:line — type — what's broken — fix`.
- Exit code: 0 (all clean) or 1 (failures found).

## Anti-patterns
- Skipping catalog validation because "I just changed one field" — a single
  typo in a skill name breaks the entire agent.
- Flagging ORPHAN_SKILL as a hard error — a skill may be new and not yet
  referenced; this is a warning, not a blocker.
- Validating only agents and not cross-referencing skills — a skill with no
  consumer is a maintenance liability even if not a hard error.
