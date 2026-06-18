---
name: test-execution
description: Use to run tests and turn the outcome into objective, reusable evidence — pass/fail, coverage, and a clear reproduction of any failure. Reports what the results mean for confidence, without rendering an approval verdict.
---

# Test Execution

## Purpose

Produce trustworthy evidence of how software behaves. The value is in results that
others can rely on and reuse — not in a thumbs-up, which is the Reviewer's call.

## When to use

After tests exist (new or existing), to validate behavior or a fix and record the
outcome.

## Procedure

1. **Run the right set.** Execute the relevant tests for what's under validation;
   widen to the full suite when impact is broad or at feature completion.
2. **Capture results.** Record pass/fail counts, which tests ran, and coverage where
   it's meaningful.
3. **Reproduce failures.** For any failure, capture the exact command and output so
   it can be reproduced and handed to a fix — a failing test is a finding, not noise.
4. **Read confidence.** State plainly what the results do and don't establish, and
   what remains unvalidated.
5. **Make it reusable.** Record the evidence so build, fix, and review can consume it
   without re-running.

## Outputs

- Recorded results (pass/fail, coverage), reproductions for failures, and a
  confidence summary.

## Anti-patterns

- Reporting "tests pass" without saying which ran or what they cover.
- Hiding or rerunning-away a flaky failure instead of capturing it.
- Turning evidence into an approval decision — that's the Reviewer's role.
