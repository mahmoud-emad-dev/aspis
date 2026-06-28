---
name: finding-format
description: Required fields and severity rubric (CRITICAL/HIGH/MEDIUM/LOW) for review findings, with file:line evidence convention. Owned by the reviewer.
---

# finding-format

## Purpose

Standardize every reviewer's finding so it is machine-parseable, actionable, and
carries enough evidence for the builder to fix the issue without re-investigation.
Eliminates vague output like "this looks wrong" and grounds every severity call in
the rubric defined in the F-016 reviewer reference spec §6 (the canonical verdict
system — cited, not restated, in this skill).

## When to use

Every time the reviewer produces a finding — plan review (`plan-critic`),
change review (`quality-review`, `security-review`), scope-compliance check, or
acceptance verdict (`acceptance-decision`). If the agent is the reviewer, the
finding runs through this format.

## Procedure

For every issue found, capture the six required fields in this order:

1. **Location** — the exact `file:line` reference (repo-relative path, line
   number; use `path:start-end` for a range).
2. **What** — one sentence stating what is wrong, no hedge.
3. **Why** — which FR / SC / system rule (R-###) it violates, or what concrete
   harm it causes. Name the rule ID, do not restate it.
4. **Severity** — assign per the rubric in the F-016 reviewer ref spec §6:
   `CRITICAL` → always REJECTED · `HIGH` → always CHANGES-REQUIRED ·
   `MEDIUM` → blocking by default, deferrable only with an explicit note ·
   `LOW` → never blocking, always a note.
5. **Fix** — the specific correction (function name, regex change, test to
   add), not "fix it" or "consider improving."
6. **Evidence** — test output, diff line range (`git diff HEAD~1:L138-L150`),
   gate failure message, or rule ID. **"No evidence = no verdict"** — if any
   field cannot be filled, withhold the verdict and request the missing
   evidence from the delegating lead.

## Outputs

A finding with all six fields above, ready to fold into the review report and
route to the build lead (HIGH / MEDIUM-blocking) or committer (LOW notes).

## Anti-patterns

- Vague findings without `file:line` — the builder cannot locate the issue.
- Severity inflation — marking everything CRITICAL to force a reject.
- Severity deflation — downgrading a HIGH to MEDIUM to avoid blocking.
- Findings without evidence ("trust me, this is broken") — withhold verdict.
- Generic fix suggestions ("refactor", "improve naming") — name the actual
  change.
- Restating the rubric in the skill body — cite the F-016 reviewer ref spec §6
  once and link it; do not duplicate the table here.
