---
name: architecture-planning
description: Use to design the technical approach for a spec — the strategy, components, data flow, dependencies, and integration points, with the steps and gates that make it buildable. Produces the implementation plan, from the PLAN template, consistent with the project's existing architecture.
---

# Architecture Planning

## Purpose

Turn *what* (the spec) into *how* — a technical approach that fits the existing
system, names its risks, and is concrete enough to decompose into tasks.

## When to use

After the spec is settled, for any work that touches code or system structure.

## Procedure

1. **Choose the approach.** The strategy in a few sentences, tied to the spec's
   slices and consistent with existing patterns.
2. **Design the structure.** Components, data flow, interfaces, dependencies, and
   integration points; say where new files live and why.
3. **State technical context.** Language, key dependencies, storage/interfaces.
4. **Lay out steps and gates.** Ordered steps, each with the files it touches and
   the deterministic check that proves it.
5. **Name risks and rollback.** What could go wrong, mitigations, and how to undo.

Fill the `.aspis/templates/PLAN.md` template. Keep architecture decisions that need
human approval flagged, not silently made.

## Outputs

- A completed implementation plan: approach, structure, steps+gates, risks.

## Anti-patterns

- Designing against the spec's intent or ignoring existing patterns.
- Steps with no deterministic gate to verify them.
- Hiding a load-bearing architecture decision instead of surfacing it.
