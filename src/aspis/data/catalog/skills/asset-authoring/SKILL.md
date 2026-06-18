---
name: asset-authoring
description: Use to author a catalog asset correctly — a runtime-neutral agent, skill, command, or template that is thin, single-sourced, professionally named, and renders correctly for every runtime through the adapters.
---

# Asset Authoring

## Purpose

Author catalog assets that are correct, lean, and runtime-neutral, so the adapters
can translate them to every runtime and the system stays consistent.

## When to use

When `deterministic-first` decides an agent, skill, command, or template is the
right mechanism.

## Procedure

1. **Author runtime-neutral.** Write one catalog asset in the superset format
   (frontmatter + body). Never hand-write per-runtime files — the adapters render
   `.claude/`, `.opencode/`, etc., and drop what a runtime can't use.
2. **Keep agents thin.** An agent instruction holds identity, rules,
   responsibilities, and skill references — the intelligence lives in its skills.
   Put procedures in skills, structured output in templates.
3. **Name professionally.** Role-specific, lowercase, no tool prefixes; one clear
   responsibility per asset.
4. **Single-source.** Reuse existing skills/helpers instead of duplicating; if two
   assets share logic, extract it rather than copy it.
5. **Wire it.** Add the asset to the right profile so `init` exports it, and to the
   owning agent's `skills`/`delegates` as needed.
6. Hand off to `system-validation` before calling it done.

## Outputs

- One runtime-neutral catalog asset, wired into a profile and its owner.

## Anti-patterns

- Hand-writing runtime-specific files instead of one neutral source.
- Fat agent instructions with inlined procedures that belong in skills.
- Duplicating an existing skill instead of reusing it.
- Authoring an asset but forgetting to wire it into a profile.
