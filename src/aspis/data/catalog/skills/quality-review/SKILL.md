---
name: quality-review
description: Use to evaluate a change against the quality dimensions in scope — correctness, scope compliance, architecture, maintainability, security, standards, and more — by verifying against real evidence rather than trusting the author's claims. Produces specific, located findings.
---

# Quality Review

## Purpose

Find what's actually wrong. The reviewer assumes gaps and issues exist and proves
quality by inspecting evidence — the diff, the tests, the behavior — not by reading
a summary and trusting it.

## When to use

After `review-strategy` sets the dimensions and depth, for each artifact under review.

## Procedure

1. **Gather the evidence.** Read the actual diff, the spec/acceptance criteria, and
   the test results; run the tests yourself when correctness is in question.
2. **Evaluate each in-scope dimension:**
   - **Correctness** — does it do the right thing, including edge cases?
   - **Scope** — was the requested work done, and nothing extra?
   - **Architecture** — does it follow the planned design and existing patterns?
   - **Maintainability** — is it clear, not needlessly complex, low future cost?
   - **Reliability / performance** — does it behave consistently, no new bottlenecks?
   - **Security** — input handling, secrets, access; any new attack surface?
   - **Standards / docs** — project conventions followed, docs sufficient.
3. **Locate each finding.** File and line, what's wrong, why it matters, and its
   severity (blocking vs note).
4. **Confirm acceptance.** Check the change against the spec's acceptance criteria
   one by one.

## Outputs

- A list of findings — each located, explained, and severity-rated — plus an
  acceptance-criteria checklist.

## Anti-patterns

- Approving from the description without reading the diff or running tests.
- Vague findings ("could be cleaner") with no location or reason.
- Treating style nits as blockers, or waving through real correctness/security issues.
