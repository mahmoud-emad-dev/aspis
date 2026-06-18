---
name: system-awareness
description: Use to understand the current ASPIS system before changing it — which agents, skills, commands, profiles, and runtime assets exist, how they are wired, and what a change would affect — so system work never duplicates or breaks what is already there.
---

# System Awareness

## Purpose

Know the system you are about to change. System work fails when it duplicates an
existing asset, breaks a reference, or ignores how export/runtime wiring works.
This skill builds that picture fast, from deterministic sources.

## When to use

At the start of any system change, before deciding what to build.

## Procedure

1. **Inventory the catalog.** Read the catalog under `data/catalog/` (agents,
   skills, commands, templates, hooks, scripts) — what already exists by name.
2. **Understand wiring.** Read the profiles (which assets each project gets) and
   the runtime adapters (how an asset renders per runtime). Use
   `.asps/index/CODE_MAP.md` to grasp the engine without reading every file.
3. **Trace impact.** For a change, find what references the asset — profiles,
   other agents' `skills`/`delegates`, the entrypoint files — so you know the full
   blast radius before editing.
4. Stop once you can name what exists, how it is wired, and what your change touches.

## Outputs

- What already exists (by name) in the relevant category.
- How it is wired (profile, runtime, references).
- The blast radius of the proposed change.

## Anti-patterns

- Authoring a new asset without checking for an existing one (duplication).
- Changing an asset without finding everything that references it.
- Reading every source file instead of using the index and code map.
