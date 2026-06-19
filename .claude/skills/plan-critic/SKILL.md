---
name: plan-critic
description: Use before any build to check a feature's plan for cross-artifact consistency — that SPEC, PLAN, and TASKS agree and nothing is orphaned or unverifiable. Catches planning defects while they are still cheap to fix.
---

# Plan Critic

## Purpose

Find the gaps in a plan before they become expensive in code. A build inherits every
weakness of its plan, so the cheapest place to catch a missing requirement, an
untestable criterion, or an orphan task is here — between planning and building.

## When to use

At P5, after SPEC/PLAN/TASKS exist and before the build gate. Skip in vibe; a
self-check in mvp; an independent Reviewer pass in production (see `modes.yaml`).

## Procedure

1. **Traceability — SPEC → TASKS.** Every `FR-###` and user story maps to at least
   one task. Flag requirements with no task (under-built) and tasks that serve no
   requirement (scope creep).
2. **Measurability — SC-### .** Every success criterion is observable and has a task
   or test that proves it. Flag any criterion nothing verifies.
3. **Coherence — SPEC ↔ PLAN.** The plan's approach actually delivers the spec's
   scope; technical-context choices don't contradict the requirements.
4. **Ordering — TASKS.** Phases respect dependencies (Setup → Foundational → stories →
   Polish); `[P]` tasks truly touch different files; tests precede their implementation.
5. **Resolved unknowns.** No `[NEEDS CLARIFICATION]` markers survive into a production
   build; open questions are answered or explicitly deferred.
6. **Rules & gate.** The PLAN's gate-check is honest; any rule exception is justified
   in Complexity tracking and flagged for the human gate (R-009) where needed.

## Outputs

- A short findings list (each tied to the artifact and line), and a verdict: ready to
  build, or changes-required with the specific fixes.

## Anti-patterns

- Reviewing prose quality instead of cross-artifact consistency.
- Passing a plan with an unverifiable success criterion or an orphan requirement.
- Re-doing the planning work — name the gap and route it back to the Planning Lead.
