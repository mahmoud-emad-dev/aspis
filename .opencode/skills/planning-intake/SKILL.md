---
name: planning-intake
description: Use at the start of any planning request to classify the work and size it — what kind of request this is, its complexity and risk, the right mode, and therefore how much planning it needs. Reads .aspis/config/modes.yaml so effort matches the work.
---

# Planning Intake

## Purpose

Decide *how* to plan before planning. The intake decision sets the depth of every
downstream step, so a one-line fix doesn't get an epic's ceremony and a risky
feature doesn't get under-planned.

## When to use

First, on every planning request, before gathering deep context or writing anything.

## Procedure

1. **Classify the request — the track.** Question · trivial · small task / bug ·
   feature · project plan. The track sets the path:
   - *Question* → answer from project intelligence; no plan, no branch.
   - *Trivial* → no plan; readiness → change → gate → commit.
   - *Small task / bug* → one task packet only (no spec/architecture).
   - *Feature* → the full lifecycle (P1–P5), sized by mode.
   - *Project plan* → project-level planning, then decompose into features.
2. **Assess complexity.** Scope, risk, dependencies, unknowns, and blast radius on
   the existing project — this nudges the mode (high risk resists vibe).
3. **Pick the mode.** Resolve in this order, highest first: the mode named in the
   request (`/plan --mode vibe`, "build this MVP-style") → the active feature's mode →
   the **project default** (`.aspis/config/project.yaml`) → `modes.yaml`'s `default`.
   You may infer a mode from the request's risk and scope and confirm it with the
   user, rather than always asking. Read the chosen mode's knobs from
   `.aspis/config/modes.yaml` — do not invent them.
4. **Apply the mode's knobs.** The file gives, per mode: `spec`, `architecture`,
   `task_size`, `plan_review`, `build_review`, `test_depth`, `docs`, `promotable`.
   These decide which artifacts P2–P5 produce and how deep each goes (e.g.
   `architecture: skip` drops P3; `plan_review: skip` drops P5). `task_size` is the
   *base* granularity — the model in use shifts it: a weaker (cheaper) model earns
   finer task packets, a frontier model can take coarser ones. Run `aspis models` to
   see what each tier resolves to here; the effective size is `task_size` adjusted by
   that model's capability (see `effective_task_size`).
5. **State the plan-of-plan** in one or two lines before proceeding: track, mode, and
   the artifacts to produce.

## Mode is a ceiling, not a floor

The **track** (set by size and complexity) chooses the path; the **mode** only tunes
how much rigor that path gets. So a genuinely small change in production mode still
takes the small-task path — production raises the bar *on that path* (require a test,
require the review) but never forces a full spec + architecture onto a one-file edit.
Let real simplicity collapse phases even under production; let real risk resist vibe.
Mode sets the maximum ceremony, not a minimum.

## Outputs

- A classification (track), complexity read, the chosen mode, and the resolved knob
  set that sizes every downstream phase.

## Anti-patterns

- Full planning ceremony for a trivial change.
- Skipping classification and planning everything the same way.
- Hard-coding mode behaviour instead of reading `modes.yaml`.
- Choosing a mode the project or user didn't ask for.
