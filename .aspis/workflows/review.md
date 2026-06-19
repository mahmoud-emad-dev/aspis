# Workflow: Review a change

The Reviewer's spine — the independent quality authority. Used per-task on escalation
from the Build Lead, and for the feature-level acceptance decision.

## When to use
A change, branch, or completed feature needs an independent quality verdict.

## Prerequisites
The diff/branch, the SPEC (acceptance criteria), and the active mode.

## Steps

1. **Strategy** — skill `review-strategy`. Set the depth from risk + mode: which
   dimensions to check (correctness, scope, tests, security, clarity) and how hard.
2. **Evaluate** — skill `quality-review`. Check the in-scope dimensions against the
   SPEC's `FR-###`/`SC-###` and the project rules. Stay read-only; cite file:line.
3. **Decide** — skill `acceptance-decision`. Verdict: approve / approve-with-notes /
   changes-required / rejected.
4. **Route** — approve → committer/done; changes-required → back to a builder;
   rejected with a defect → **Fix Lead** (`fix.md`).

## Mode overlays
- **vibe** — one light pass: does it run, is it in scope, anything obviously broken.
  Not the full multi-dimension review.
- **mvp** — standard depth on the changed surface.
- **production** — full multi-lens review; every acceptance criterion checked.

## Outputs
A written verdict with reasons and routed follow-ups.
