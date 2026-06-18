---
name: selective-testing
description: Use to test implementation proportional to impact — from changed files to affected components to the relevant tests — instead of running the whole suite after every task. Records the test evidence later stages can reuse.
---

# Selective Testing

## Purpose

Make testing fast and meaningful during implementation by focusing effort where
the change actually lands, while still proving each task works.

## When to use

After a task is implemented, before accepting it — and when deciding how much to
test at feature completion.

## Procedure

1. **Trace the impact.** Changed files → affected components → the tests that cover
   them. Test that set first.
2. **Run task-level tests.** Unit and targeted tests for the change, plus the
   integration or smoke tests its components touch.
3. **Scale to risk.** Higher-risk or cross-cutting changes widen the net; small,
   isolated changes stay narrow.
4. **Run the full gate at the right moments.** Reserve the whole-suite run for
   feature completion or when impact is broad — not after every task.
5. **Record evidence.** Capture what ran and the pass/fail result so review and
   feature completion can reuse it.

## Outputs

- Targeted test results per task and recorded evidence for later stages.

## Anti-patterns

- Running the entire suite after every trivial change.
- Skipping tests for "obvious" changes.
- Testing only the changed file while ignoring the components it affects.
- Discarding results that later stages would have reused.
