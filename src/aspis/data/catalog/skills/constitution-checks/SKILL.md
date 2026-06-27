---
name: constitution-checks
description: Audit a PLAN against the 12 architecture-constitution rules and emit a pass/fail report with file:line evidence.
---

# constitution-checks

## Purpose
Before a plan is approved, audit it against all 12 rules of the architecture
constitution (`.aspis/rules/architecture-constitution.md`) — catch architecture
violations at planning time when they're cheapest to fix, not at review time when
code is already written.

## When to use
- At P5 (Architecture) of the planning lifecycle, after the PLAN.md is drafted.
- Before handing a plan to the reviewer for the plan-critic pass (P7).
- Whenever a plan is revised after a rejection.

## Procedure
1. **Load the constitution** from `.aspis/rules/architecture-constitution.md`.
   Focus on the 12 extension rules, the file rules, and the cost-of-change test.
2. **Walk each rule against the PLAN:**
   - **Rule 1 (Local Change)**: does the plan add files or edit many? Count planned
     file changes.
   - **Rule 2 (Plugin First)**: if the plan adds a new kind of thing (agent type,
     asset type), does it use the plugin mechanism or hardcode?
   - **Rule 3 (Single Source of Truth)**: is any fact planned to live in two places?
   - **Rule 4 (Configuration over Code)**: is behaviour controlled by config or
     by `if` chains?
   - **Rule 5 (Core is Stable)**: does the plan touch core modules? If yes, is it
     justified?
   - **Rule 6 (Dependency Direction)**: do dependencies flow inward?
   - **Rule 7 (Discovery over Registration)**: are new assets discovered by
     convention or hand-registered?
   - **Rule 8 (Generated Artifacts)**: are humans editing generated output?
   - **Rule 9 (No Special Cases)**: are there `if runtime == "x"` patterns?
   - **Rule 10 (Consistency over Cleverness)**: is the approach boring and
     predictable?
   - **Rule 11 (Architecture before Features)**: if more features of this shape are
     coming, is the extension mechanism built first?
   - **Rule 12 (Portable by Default)**: do scripts/tools run on Windows AND Linux?
3. **Run the cost-of-change test**: count how many existing files the plan would
   change. 1–3 = healthy, 5–10 = warning, 10+ = problem, 20+ = critical.
4. **Emit the report**: for each violation, note the rule number, the specific
   concern, the file:line in the PLAN where the violation is visible, and a
   suggested fix. Format: `CONSTITUTION_CHECK: R-<N> — <finding> — in <plan
   section> — fix: <suggestion>`.
5. **Verdict**: PASS (0 violations), PASS-WITH-NOTES (only WARN-level), or FAIL
   (any ERROR-level violation). A FAIL must be resolved before the plan advances.

## Outputs
- A `CONSTITUTION_CHECK` report with per-rule findings, verdict, and cost-of-change
  score.
- If FAIL: specific, actionable fixes for each violation.

## Anti-patterns
- Skipping the constitution check because "it's just a plan" — architecture
  mistakes caught later cost 10x more.
- Applying rules mechanically without judgment — a rule that doesn't improve the
  work for this specific plan is not a violation to flag.
- Flagging a rule the planning-lead doesn't own — only the rules the planning
  lead is responsible for apply (see `constitution-checks.yaml`).
- Approving a FAIL just to move forward — unresolved violations cascade into
  build problems.
