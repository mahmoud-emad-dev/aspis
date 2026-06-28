---
name: constitution-check
description: Apply the reviewer-owned architecture-constitution checks (from the system-of-record YAML) before issuing a review verdict.
---

# constitution-check

## Purpose
During review, verify that the built change honours the architecture constitution
— specifically the checks the reviewer owns per the constitution's
`constitution-checks.yaml`. This is the review-time counterpart to the planning-
lead's `constitution-checks` (which audits the PLAN); this skill audits the
**built artifact** against the constitution.

The system of record for the rules is
**`src/aspis/data/catalog/config/policy/constitution-checks.yaml`** — load the
rule list from it, never re-derive it from the prose constitution document.
R-006 single-source: one fact, one owner; this skill **walks the YAML**, not its
own hard-coded list.

## When to use
- During the reviewer's Evaluate step (review.md step 2), under the Architecture
  dimension.
- After a build-lead hands a completed task for review.
- At feature-level acceptance review, before the final verdict.

## Procedure
1. **Load the rule list** from
   `src/aspis/data/catalog/config/policy/constitution-checks.yaml`. Walk every
   `checks[]` entry — the YAML defines `id`, `statement`, `enforced_by`, and
   `review_question`. The set evolves; do not hand-maintain a separate list.
2. **Filter to the rules you own.** The reviewer's `constitution-check` skill
   evaluates the checks where `enforced_by` includes `review` (currently:
   C-COST, C-LOCAL-CHANGE, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE,
   C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE). Skip rules the
   reviewer does not own — the planning-lead evaluates those at plan time.
3. **For each reviewer-owned check, ask its `review_question` against the diff.**
   Record: the rule, the file:line where the violation is visible, severity (per
   the review severity rubric), and a suggested fix.
4. **Fold into the review verdict**: a FAIL on any constitution check is at least
   a HIGH finding → changes-required. A pattern of violations is a CRITICAL
   finding → rejected.

## Outputs
- Constitution findings with file:line evidence, folded into the review report.
- Each finding uses the standard review finding format: `file:line — what's wrong
  — why — severity — fix — evidence`.

## Anti-patterns
- Hand-maintaining a separate rule list — the YAML is the source of truth;
  walking a hand-written list creates silent drift (R-006 violation).
- Applying constitution checks to work the reviewer doesn't own — stay within
  the rules whose `enforced_by` includes `review`; planning-lead handles the rest.
- Treating every deviation as a violation — a rule that doesn't improve the work
  is not a defect to flag (per system-rules.md "Applying these rules").
- Skipping constitution check on small changes — even a one-file edit can
  introduce a special case or duplicate a fact.
