---
name: root-cause-analysis
description: Use to find the true cause of a failure rather than its symptom — reproduce it reliably, then trace from the observed behavior back to the underlying defect using evidence. The diagnosis a correct fix depends on.
---

# Root Cause Analysis

## Purpose

A fix is only as good as the diagnosis behind it. This skill establishes *why*
something fails — reproducibly and from evidence — so the correction targets the
cause, not a surface symptom.

## When to use

At the start of any fix, before changing code.

## Procedure

1. **Reproduce reliably.** Find the minimal, repeatable way to trigger the failure
   and capture the exact error, output, or wrong behavior. If you can't reproduce
   it, you can't confirm a fix.
2. **Gather evidence.** Logs, stack traces, the failing test, recent diffs, and git
   history around when it broke.
3. **Trace to the cause.** Follow the symptom inward — narrow to the specific line,
   state, or assumption that is actually wrong. Distinguish the cause from its
   downstream effects.
4. **Confirm the hypothesis.** Verify the suspected cause actually produces the
   failure (and explains all of it), not just a plausible-looking candidate.

## Outputs

- A reliable reproduction, the confirmed root cause, and the affected area.

## Anti-patterns

- "Fixing" what you can't reproduce.
- Stopping at the first plausible cause without confirming it.
- Treating a downstream symptom as the cause.
