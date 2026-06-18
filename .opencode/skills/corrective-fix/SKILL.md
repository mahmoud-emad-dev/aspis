---
name: corrective-fix
description: Use after the root cause is known to apply the smallest safe correction — fix the cause, not the symptom, without unrelated changes — then prove the failure is gone and nothing regressed. Produces a verified fix and a report.
---

# Corrective Fix

## Purpose

Turn a confirmed diagnosis into a minimal, safe repair. The goal is to correct the
cause cleanly and prove it, not to patch over the symptom or rewrite more than the
defect requires.

## When to use

After `root-cause-analysis` confirms the cause, to implement and verify the fix.

## Procedure

1. **Target the cause.** Change exactly what fixes the root cause — the smallest
   diff that resolves it, no opportunistic refactors.
2. **Avoid temporary patches.** No swallowing errors or masking behavior; if only a
   stopgap is possible, say so explicitly and flag the real fix as follow-up.
3. **Prove it.** Re-run the reproduction — it now passes — and add a regression test
   that would have caught the bug.
4. **Check for regressions.** Run the tests for the affected area; confirm nothing
   else broke.
5. **Report.** Root cause, the change made, files touched, tests run, and residual
   risk; hand the commit to the committer.

## Outputs

- A minimal verified fix, a regression test, and a fix report.

## Anti-patterns

- Masking the symptom instead of fixing the cause.
- A broad rewrite when a targeted change would do.
- Declaring it fixed without the reproduction passing and a regression test added.
