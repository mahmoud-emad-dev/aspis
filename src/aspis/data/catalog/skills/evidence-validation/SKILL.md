---
name: evidence-validation
description: Codify "verify, don't trust" — what counts as valid evidence per review dimension, and how to judge it.
---

# evidence-validation

## Purpose
Every review finding must be backed by observable, specific evidence — never
opinion, never "feels wrong." This skill defines what counts as valid evidence
for each review dimension, so the reviewer never issues an unsupported verdict.

## When to use
- During the reviewer's Evaluate step, before recording any finding.
- When a sub-reviewer or peer reviewer submits findings — validate their evidence
  before folding into the verdict.
- On any `changes-required` or `rejected` verdict — every HIGH+ finding must have
  evidence.

## Hard rule: no evidence, no verdict
A finding without file:line or observable-trace evidence is NOT a finding — it's
an impression. Drop it or downgrade it to LOW with a note. A verdict cannot rest
on un-evidenced findings.

## What counts as evidence per dimension

| Dimension | Valid evidence |
|---|---|
| **Correctness** | Failing test output, counterexample input/output, logic error at specific line |
| **Scope** | File change outside the packet's allowed-files list, diff showing forbidden path touched |
| **Architecture** | Constitution rule violated at specific file:line, cost-of-change count |
| **Maintainability** | Concrete readability issue (e.g. 100+ line function, 5+ nesting levels), missing self-documentation |
| **Reliability** | Race condition trace, missing error handling at specific line, non-idempotent operation |
| **Security** | OWASP-catalogued vulnerability at specific line, secret in diff, missing input sanitization |
| **Performance** | N+1 query visible in code, O(n²) loop without bounds, missing cache on repeated computation |
| **Standards** | Violation of a named convention at file:line (e.g. missing docstring, non-standard import order) |
| **Documentation** | Missing Purpose/Does Not/Used By block, undocumented public API, stale comment contradicting code |

## Procedure
1. **Observe before judging.** Read the change; don't form a conclusion first and
   then look for evidence to support it.
2. **For each potential finding**, identify the specific file and line (or
   observable output) that demonstrates the issue.
3. **Classify the evidence**:
   - **Direct**: the issue is visible at the cited location (e.g. a missing null
     check on line 42).
   - **Inferred**: the issue follows from the code but requires reasoning (e.g.
     "this loop has no bound, and input size is unbounded").
   - **Insufficient**: the evidence points to a general area but not a specific
     problem — not a valid finding; investigate further or drop.
4. **Record the finding** in the standard format: `file:line — what's wrong —
   why — severity — fix — evidence`.
5. **Sanity-check**: could another reviewer, given the same evidence, reach the
   same conclusion? If not, the evidence is too weak.

## Outputs
- Validated findings with specific file:line evidence.
- Dropped or downgraded impressions that lacked sufficient evidence.
- A verdict that rests on evidence, not opinion.

## Anti-patterns
- "This feels wrong" or "this is bad practice" without pointing to a specific
  line and rule.
- Citing a rule the reviewer doesn't own — the reviewer's domain is the 9
  dimensions, not every rule in the system.
- Treating style preference as a finding — if no named standard is violated,
  it's not a defect.
- Accepting "the tests pass" as sole correctness evidence — tests passing doesn't
  mean the right thing was built (check against SPEC FR-###/SC-###).
