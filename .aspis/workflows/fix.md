# Workflow: Fix an issue

The Fix Lead's spine — the recovery authority for defects, regressions, and red gates.

## When to use
A bug report, a failing gate, or a review rejection with a concrete defect.

## Prerequisites
The failure signal: the error, the failing test/gate output, or the rejection notes.

## Steps

1. **Reproduce & root-cause** — skill `root-cause-analysis`. Reproduce the failure,
   isolate the smallest cause; do not patch symptoms.
2. **Scope the fix** — skill `scope-control`. Identify the minimal set of files; treat
   it as a one-task packet (`TASK_PACKET.md`) if it is more than a line.
3. **Correct** — skill `corrective-fix`. Apply the smallest change that fixes the root
   cause. Add or strengthen a test that fails before and passes after (R-005); never
   weaken a test to go green.
4. **Verify** — skill `selective-testing`, then the full gate.
5. **Commit & report** — hand the approved fix to the `committer`; report the root
   cause and the guard added.

## Mode overlays
Fixes default to production rigor regardless of the feature's mode — a defect that
escaped is evidence the bar was too low. Vibe may skip the extra regression test only
for throwaway work.

## Outputs
Root cause fixed, a regression guard in place, gate green.
