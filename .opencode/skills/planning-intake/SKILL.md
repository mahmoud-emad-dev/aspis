---
name: planning-intake
description: Use at the start of any planning request to classify the work and size it — what kind of request this is, its complexity and risk, the right mode, and therefore how much planning it needs. Sets the planning depth so effort matches the work.
---

# Planning Intake

## Purpose

Decide *how* to plan before planning. The intake decision sets the depth of every
downstream step, so a one-line fix doesn't get an epic's ceremony and a risky
feature doesn't get under-planned.

## When to use

First, on every planning request, before gathering deep context or writing anything.

## Procedure

1. **Classify the request.** Question · small fix · task · feature · epic · new
   project · architecture change · research request. The class sets the path.
2. **Assess complexity.** Scope, risk, dependencies, unknowns, and blast radius on
   the existing project.
3. **Pick the mode.** Production (max rigor), MVP (balanced), or Vibe (speed) —
   from the request, the project's default, or a quick confirmation.
4. **Set the planning depth.** Map class + complexity + mode to which artifacts are
   needed (spec only, spec+plan, or full spec+architecture+tasks) and how granular.
5. State the plan-of-plan in one or two lines before proceeding.

## Outputs

- A classification, complexity read, mode, and the set of artifacts to produce.

## Anti-patterns

- Full planning ceremony for a trivial change.
- Skipping classification and planning everything the same way.
- Choosing a mode the project or user didn't ask for.
