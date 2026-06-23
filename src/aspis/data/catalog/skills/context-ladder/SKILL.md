---
name: context-ladder
description: How much project context to load and in what order — the minimum for the task, level by level, stopping as soon as you can act. Hot context (what you almost always need) is read directly; deeper context is pulled on demand via tools; the deepest analysis is delegated to a helper. Used by every role that reads project context.
---

# Context ladder

Load context in levels, cheapest first, and **stop as soon as you have enough to act**. Never load
the whole repo "just in case." Read only what your role and this task need — leave the rest to the
agents whose role it is. Use the generated brain files and tools to *decide where to look*; don't
scan the tree.

## L1 — Hot context (always; read directly)

What almost every task needs — read these three short, generated files first, no searching:

- `.aspis/context/CURRENT_STATE.md` — where the project stands now.
- `.aspis/context/RECENT_CHANGES.md` — what changed, newest first.
- `.aspis/current/active_feature.json` — the active feature, its branch, phase, and mode.

If they may be stale (work happened since the last commit), refresh first:
`python .aspis/scripts/context/update.py`. For most simple tasks, L1 is enough — act, don't dig deeper.

## L2 — The active feature (only when working on it)

The feature folder named by `active_feature.json` (`path`), e.g. `.aspis/features/<id>/`:
`SPEC.md`, `PLAN.md`, `TASKS.md`, `ACCEPTANCE.md` — the goal, approach, tasks, and acceptance.

## L3 — Locate & understand without reading bodies (only when you need code)

Use the index, never a tree scan:

- `.aspis/index/FILE_REGISTRY.yaml` — every file and its purpose; find *where* a thing lives.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports); understand a file
  without reading it. For a fresher or narrower view:
  `python .aspis/scripts/context/build_code_map.py --scope <path>`.

## L4 — Source (only the files this task touches)

Open the actual source/tests only for the specific files L3 pointed you to. Never more than the task needs.

## Deeper analysis → delegate, don't carry

For repo-wide usages, relationships, or analysis beyond the map, **delegate to `project-explorer`**
(it owns the search tools) and consume its compact summary. A lead does not carry every context tool —
it asks the helper whose role that is, and keeps its own context lean.

## Rules

- Stop at the lowest level that lets you act; when the task is unclear, ask before loading deeper.
- Read the generated registry/map to decide where to look — don't grep the whole tree.
- Pull deeper context only when the case needs it; not every task reaches L3 or L4.
