---
name: constitution-check
description: Apply the 9 reviewer-owned constitution checks before issuing a review verdict.
---

# constitution-check

## Purpose
During review, verify that the built change honours the architecture constitution
— specifically the 9 checks the reviewer owns per the constitution's
`constitution-checks.yaml`. This is the review-time counterpart to the planning-
lead's `constitution-checks` (which audits the PLAN); this skill audits the
**built artifact** against the constitution.

## When to use
- During the reviewer's Evaluate step (review.md step 2), under the Architecture
  dimension.
- After a build-lead hands a completed task for review.
- At feature-level acceptance review, before the final verdict.

## Procedure
1. **Load the reviewer's constitution checks** from the project's
   `constitution-checks.yaml` (or the global default). The reviewer owns 9 checks:
   the 12 extension rules minus the 3 that only the planning-lead evaluates
   (Local Change, Architecture before Features, Portable by Default — those are
   plan-time checks).
2. **Walk each check against the diff:**
   - **Plugin First**: is new capability in a plugin or did it require core edits?
   - **Single Source of Truth**: is any fact now duplicated across files?
   - **Configuration over Code**: is new behaviour controlled by config or by
     conditional logic?
   - **Core is Stable**: did the change touch core modules? If yes, is it justified?
   - **Dependency Direction**: do imports flow inward?
   - **Discovery over Registration**: are new assets discovered by convention?
   - **Generated Artifacts**: are generated files hand-edited?
   - **No Special Cases**: are there runtime-specific branches?
   - **Consistency over Cleverness**: is the implementation predictable?
3. **For each violation**, record: the rule, the file:line where it's visible,
   severity (per the review severity rubric), and a suggested fix.
4. **Fold into the review verdict**: a FAIL on any constitution check is at least
   a HIGH finding → changes-required. A pattern of violations is a CRITICAL finding
   → rejected.

## Outputs
- Constitution findings with file:line evidence, folded into the review report.
- Each finding uses the standard review finding format: `file:line — what's wrong
  — why — severity — fix — evidence`.

## Anti-patterns
- Applying constitution checks to work the reviewer doesn't own — stay within the
  9 reviewer-owned checks; the planning-lead handles the other 3.
- Treating every deviation as a violation — a rule that doesn't improve the work
  is not a defect to flag (per system-rules.md "Applying these rules").
- Skipping constitution check on small changes — even a one-file edit can
  introduce a special case or duplicate a fact.
