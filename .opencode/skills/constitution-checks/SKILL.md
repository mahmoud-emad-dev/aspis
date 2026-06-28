---
name: constitution-checks
description: Audit a PLAN against the architecture-constitution checks (system-of-record YAML) and emit a pass/fail report with file:line evidence.
---

# constitution-checks

## Purpose
Before a plan is approved, audit it against the architecture-constitution checks
the planning-lead owns — catch architecture violations at planning time when
they're cheapest to fix, not at review time when code is already written.

The system of record for the rules is
**`src/aspis/data/catalog/config/policy/constitution-checks.yaml`** — load the
rule list from it, never re-derive it from the prose constitution document. R-006
single-source: one fact, one owner; this skill **walks the YAML**, not its own
hard-coded list.

## When to use
- At P5 (Architecture) of the planning lifecycle, after the PLAN.md is drafted.
- Before handing a plan to the reviewer for the plan-critic pass (P7).
- Whenever a plan is revised after a rejection.

## Procedure
1. **Load the rule list** from
   `src/aspis/data/catalog/config/policy/constitution-checks.yaml`. Walk every
   `checks[]` entry — the YAML defines `id`, `statement`, `enforced_by`, and
   `review_question`. The set evolves; do not hand-maintain a separate list.
2. **Filter to the rules you own.** The planning-lead's `constitution-checks` skill
   evaluates the checks where `enforced_by` includes `planning` (currently:
   C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-TESTABLE,
   C-ARCH-BEFORE-FEATURES). Skip rules the planning-lead does not own — the
   reviewer enforces those at review time.
3. **For each planning-owned check, ask its `review_question` against the PLAN.**
   Record the verdict, the file:line in the PLAN where the concern is visible,
   and any suggested fix. Cost-of-change test (from C-COST): count the existing
   files the plan would change. 1–3 = healthy, 5–10 = warning, 10+ = problem,
   20+ = critical.
4. **Emit the report** as one row per rule:
   `CONSTITUTION_CHECK: C-<ID> — <verdict> — <finding> — in <plan section> —
   fix: <suggestion>`. Group by verdict at the end (PASS / WARN / FAIL).
5. **Verdict**: PASS (0 FAIL), PASS-WITH-NOTES (only WARN), or FAIL (any FAIL).
   A FAIL must be resolved before the plan advances.

## Outputs
- A `CONSTITUTION_CHECK` report with per-rule findings, verdict, and cost-of-change
  score.
- If FAIL: specific, actionable fixes for each violation.

## Anti-patterns
- Hand-maintaining a separate rule list — the YAML is the source of truth;
  walking a hand-written list creates silent drift (R-006 violation).
- Skipping the constitution check because "it's just a plan" — architecture
  mistakes caught later cost 10x more.
- Applying rules mechanically without judgment — a rule that doesn't improve the
  work for this specific plan is not a violation to flag (per `system-rules.md`
  "Applying these rules").
- Flagging a rule the planning-lead doesn't own — only the rules whose
  `enforced_by` includes `planning` apply to this skill.
- Approving a FAIL just to move forward — unresolved violations cascade into
  build problems.
