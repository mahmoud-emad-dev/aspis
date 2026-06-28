---
name: mode-decision
description: Infer the build mode from risk and scope, with auto-escalation and downgrade rules.
---

# mode-decision

## Purpose
Determine the correct mode (`vibe`, `mvp`, `production`) for a piece of work from
risk signals, scope, and explicit overrides — so the planning-lead and project-lead
apply consistent mode logic without re-deriving it every time.

## When to use
- At the start of planning (P0 intake), before scaffolding.
- When a task's scope or risk profile changes mid-cycle.
- When the project-lead re-evaluates the active feature's mode.

## Procedure
1. **Read the base mode** from the most specific source available:
   - User-specified mode override (command / config)
   - Active feature's `mode` field (set by planning-lead)
   - Project default from `.aspis/config/project.yaml`
   - Global fallback: `production`
2. **Check auto-escalation triggers.** If any apply, escalate to at least the
   minimum mode listed:
   - **E1 — protected paths** in scope (`.opencode/`, `.claude/`, `rules/**`,
     `**/permissions*.yaml`) → at least `mvp`
   - **E2 — architecture/security** change (new component, new permission surface,
     new rule) → at least `production`
   - **E3 — 10+ files** in scope → at least `production`
3. **Check auto-downgrade eligibility.** Downgrade is safe only if ALL of:
   - Current mode is `production` or `mvp`
   - No auto-escalation trigger is active
   - Work is explicitly classified as Trivial or Small-task (not Feature)
   - Risk level is `low`
4. **Resolve conflicts**: if both escalation and downgrade triggers fire,
   escalation wins. Never downgrade below `vibe`. Never escalate above `production`.
5. **Record the decision**: write the chosen mode and the reason (base source,
   triggers, overrides) into the plan-of-plan or the active feature pointer.

## Outputs
- The resolved mode string (`vibe` / `mvp` / `production`).
- The reason it was chosen (base source + any triggers).
- Optionally, a `MODE_DECISION` note in the planning artifact if the decision was
  non-trivial.

## Anti-patterns
- Always defaulting to `production` without checking if the work warrants it.
- Downgrading mode because the model is cheap — model tier and mode are different
  dials (see DYNAMIC_READINESS.md). A cheap model in production mode still gets
  full process; it just gets more scaffolding.
- Escalating mode because of uncertainty — clarify first, escalate only on actual
  risk signals.
- Using mode as a quality shortcut — `vibe` is still correct; it just skips
  ceremony.
