---
name: packet-validation
description: Validate a task packet on 4 dimensions (scope, feasibility, completeness, acceptance) scaled by V0–V4 maturity.
---

# packet-validation

## Purpose
Before the build-lead delegates a task packet to a builder, validate that the
packet is well-formed — its scope is correct, its steps are feasible, its
acceptance is measurable, and it's complete enough for a context-isolated builder
to execute. Catch bad packets at delegation time, not after a builder fails.

## When to use
- At step 3 of the build workflow (`.aspis/workflows/build.md`), before ordering
  and delegating tasks.
- When a packet is returned from planning with gaps.
- When a rejected task is revised and re-submitted.

## The four checks

### 1. Scope check
- Are the allowed files listed exactly? No wildcards, no "the usual places."
- Are any forbidden paths touched? Check against the universal deny list.
- Does the packet's scope match the task's type? A "docs" task shouldn't list
  `src/` files; a "fix" task shouldn't touch feature artifacts.
- **V0–V1 (vibe/mvp)**: light check — just confirm no protected paths.
- **V2–V4 (standard/production)**: full check — every file justified against the
  task description.

### 2. Feasibility check
- Can a context-isolated builder with the listed tools actually execute the steps?
- Are the steps concrete ("add a `validate()` function to `check.py`") or vague
  ("improve the validation")?
- Does the packet assume knowledge the builder won't have from the packet alone?
- **V0–V1**: can a builder figure it out from context? If yes, proceed.
- **V2–V4**: every step must be executable from the packet alone.

### 3. Completeness check
- All packet sections filled? Identity, Context, Scope, Steps, Skeleton,
  Dependencies, Outputs, Acceptance, Tests, Review routing, Verify.
- Fields the mode doesn't need are marked `N/A` — never left blank.
- No `TODO` markers, no `TBD` placeholders in critical fields.
- **V0–V1**: may skip Skeleton and Test sections if the builder is trusted.
- **V2–V4**: all sections filled or explicitly marked N/A.

### 4. Acceptance check
- Are the acceptance criteria measurable? ("the test passes" vs "it works better")
- Are they traced to SPEC requirements (FR-### / SC-###)?
- Can the builder verify them independently?
- **V0–V1**: one or two clear conditions.
- **V2–V4**: every acceptance row traced to a SPEC requirement.

## V0–V4 maturity scaling

| Version | Mode | Checks | Enrichment needed |
|---|---|---|---|
| V0 | vibe | Light scope + basic feasibility | Minimal |
| V1 | mvp | Scope + feasibility | Light context |
| V2 | production (small) | All 4 checks | Full enrichment |
| V3 | production (cross-cutting) | All 4 + cross-ref | Full enrichment + impact analysis |
| V4 | production (critical/security) | All 4 + cross-ref + security | Full + security review routing |

## Procedure
1. **Read the packet** against the task's entry in TASKS.md.
2. **Apply all 4 checks** at the depth matching the packet's maturity (V0–V4).
3. **Record results**: PASS (all checks green), ENRICH (gaps fillable from feature
   context), or RETURN (gaps require planning-lead input — send back).
4. **Enrich if needed**: fill thin context fields, add missing refs, set review
   routing, set builder tier — from the build-lead's whole-feature context.
5. **Set the builder tier** using `builder-selection` based on the packet's
   version and risk.

## Outputs
- A validation verdict: PASS, ENRICH (with specific gaps filled), or RETURN
  (with specific gaps the planning-lead must fix).
- An enriched packet ready for delegation (if ENRICH).

## Anti-patterns
- Delegating a RETURN-level packet — if it has gaps the planning-lead must fix,
  don't try to fill them at the build-lead level.
- Over-validating V0 packets — a vibe-mode one-liner doesn't need the full 4-check
  rigor; the overhead costs more than the validation saves.
- Under-validating V4 packets — a security-critical task with a thin packet is a
  time bomb. Return it.
- Skipping the scope check because "the builder will figure it out" — scope
  violations are the #1 cause of rejected builds.
