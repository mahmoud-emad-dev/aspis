---
name: acceptance-decision
description: Use to turn review findings into a clear verdict — approved, approved with notes, changes required, or rejected — backed by evidence, with rejections routed to the right fix. The decision that gates work moving forward.
---

# Acceptance Decision

## Purpose

Convert findings into an unambiguous, defensible decision. A review that ends in a
vague "looks mostly fine" helps no one; the verdict must be clear and the path
forward obvious.

## When to use

After `quality-review`, to close the review.

## Procedure

1. **Weigh the findings.** Separate blocking issues (correctness, security, scope,
   failed acceptance) from non-blocking notes.
2. **Render the verdict:**
   - **Approved** — meets the bar; no blocking issues.
   - **Approved with notes** — acceptable now; minor items recorded as follow-ups.
   - **Changes required** — specific blocking issues must be fixed and re-reviewed.
   - **Rejected** — the approach itself is wrong; send back to planning or build.
3. **Justify it.** Tie the verdict to the evidence and the acceptance criteria.
4. **Route rejections.** Send "changes required" to a builder or fix worker with the
   exact issues; escalate genuine disagreement rather than overriding silently.
5. **Record** the verdict and findings as review evidence.

## Outputs

- A verdict with justification, the blocking-issue list, and the routing for any fix.

## Anti-patterns

- Ambiguous verdicts that don't say whether work can proceed.
- Approving despite unresolved blocking issues to avoid friction.
- Rejecting without telling the author exactly what must change.
