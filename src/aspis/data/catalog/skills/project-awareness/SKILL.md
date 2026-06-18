---
name: project-awareness
description: The Project Lead's project-intelligence skill — build a fast, accurate picture of the project (state, active feature, progress, changes, code locations, risks) by retrieving from deterministic sources on demand, never by loading the whole repo.
---

# Project Awareness

## Purpose

Know the project well enough to decide and delegate correctly — its current state
and where things live — by retrieving knowledge on demand. This is the Project
Lead's defining capability; every later step (classify, route, answer, guide)
rests on it.

## When to use

At the start of handling any request, and whenever you need current project facts.

## Procedure

1. **Live state.** Read `.asps/context/CURRENT_STATE.md` (where things stand) and
   `.asps/context/RECENT_CHANGES.md` (what changed, newest first).
2. **The map.** Query `.asps/index/FILE_REGISTRY.yaml` to locate files and
   understand what each does — read the registry, not the files, to decide where
   to look.
3. **Working state.** Confirm with read-only checks: `git status`, `git log`.
4. **Deeper exploration.** When you need more than a lookup (find usages, trace a
   relationship, map an area), delegate to `project-explorer` and consume its
   compact findings instead of reading widely yourself.
5. Stop as soon as you have enough for the task — never load the whole project.

## Outputs

- Current status and active feature
- Progress and open work
- Where the relevant code lives
- Recent changes and risks that matter to the request

## Anti-patterns

- Scanning or globbing the tree instead of using the registry and the explorer.
- Re-deriving state you can read directly from the generated files.
- Loading more than the request needs "just in case".

## Growing into it

Semantic search and dependency analysis belong here too; until that tooling
lands, the registry plus `project-explorer` cover location and relationships.
