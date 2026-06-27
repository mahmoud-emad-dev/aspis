# Workflow: Fix an issue

The Fix Lead's spine — the recovery authority for defects, regressions, and red gates.

## When to use
A bug report, a failing gate, or a review rejection with a concrete defect.

## Prerequisites
The failure signal: the error, the failing test/gate output, or the rejection notes.

## Steps

1. **Verify readiness** — skill `prestart-checks`. Run `aspis preflight` to confirm
   the repo is in a safe state (clean tree, right branch). Resolve or route any
   blocker before working.
2. **Reproduce** — skill `root-cause-analysis`. Trigger the failure reliably and
   capture the evidence (error output, failing test, gate log). If the failure cannot
   be reproduced, request environment details from the delegating lead — do not guess.
3. **Root cause** — skill `root-cause-analysis` + `context-ladder`. Isolate the
   smallest cause (not the symptom), backed by evidence. Load only the files the
   cause touches.
4. **Minimal fix** — skill `corrective-fix` + `scope-control`. Apply the smallest
   change that fixes the root cause. Add or strengthen a test that fails before and
   passes after (R-005); never weaken a test to go green. If the fix grows beyond
   minimal (requires architecture change), promote to a feature and route to the
   project-lead.
5. **Verify** — skill `selective-testing`, then the full gate. Reproduce-then-pass:
   the original failure signal must now pass. Confirm no regression in related tests.
6. **Report & commit** — hand the approved fix to the `committer` (the only git
   writer). Write a FIX_REPORT with: Symptom, Root cause, Fix (minimal change),
   Regression guard (test added), Gate result (before/after), Residual risk, Attempts
   used (1/3, 2/3, 3/3).

## Attempt cap
Hard 3-attempt cap with tier cascade:
1. standard model → full RCA + fix + verify
2. standard (focused) → narrower hypothesis
3. deep model → escalated model, broader investigation
Cap hit → write REVIEW_NEEDED (3 attempts × hypothesis/action/result) → escalate to
project-lead.

## Escalation triggers
- Fix touches protected paths (`.opencode/`, `.claude/`, `rules/**`) → system-lead
- Fix grows beyond minimal → promote to feature, route to project-lead
- Cannot reproduce → request environment details from delegating lead
- Pre-existing failure not caused by current change → log + file follow-up, do NOT
  fix in current scope

## Mode overlays
Fixes default to production rigor regardless of the feature's mode — a defect that
escaped is evidence the bar was too low. Vibe may skip the extra regression test only
for throwaway work.

## Outputs
Root cause fixed, a regression guard in place, gate green.
