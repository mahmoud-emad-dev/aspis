---
name: scope-compliance
description: Cross-check a diff against the task packet's allowed/forbidden file lists; enforce R-001 scope boundaries with file:line evidence. Owned by the reviewer.
---

# scope-compliance

## Purpose

Before approving any change, verify every modified file is within the task
packet's allowed scope and no forbidden files were touched. A single
out-of-scope edit can corrupt the architecture or open a security hole. This
is the deterministic half of the scope dimension: scripts check the file list,
the reviewer interprets and judges. Reviewer is read-only (R-004) — it
verifies, never edits.

## When to use

Every change review, before any verdict. Also during plan review: does the
plan's stated file list plausibly cover the scope it claims? Run alongside
other reviewer skills (constitution-check, evidence-validation).

## Procedure

1. Get the diff file list: `git diff --name-only HEAD~1` (or the appropriate
   base — the last reviewed commit).
2. Get the allowed file list from the task packet (`TASK_PACKET.md` /
   `TASKS.md` / `feature.yaml`).
3. Get the forbidden file list: protected paths per R-008
   (`.aspis/rules/**`, `profiles/defaults.yaml`, `.opencode/agents/**`,
   `.claude/agents/**`, secrets).
4. Cross-check: every changed file must be in allowed AND not in forbidden.
   Report each violation with `file:line` evidence.
5. Scope creep (outside allowed, not forbidden): HIGH if it changes
   architecture or adds capability; MEDIUM if a harmless adjacent cleanup.
6. Protected-path violation: CRITICAL — requires R-008 human governance
   approval; reject the change outright.
7. All files in scope → **CLEAN**. Any violation → **CHANGES-REQUIRED** with
   the violating `file:line` list as evidence.

## Outputs

A scope compliance report:

- Changed files list (from `git diff --name-only`).
- Per-file status: `ALLOWED` | `FORBIDDEN` | `OUT-OF-SCOPE`.
- Verdict: `CLEAN` or `CHANGES-REQUIRED`.
- Each finding carries `file:line` evidence and a severity (CRITICAL / HIGH /
  MEDIUM).

## Anti-patterns

- Trusting the builder's claim about which files changed — always run
  `git diff --name-only` yourself.
- Allowing "quick cleanup" edits that fall outside the allowed list.
- Skipping forbidden-path checks because "it's just a documentation file."
- Approving a change with scope violations because the rest of the diff
  looks good.
- Confusing scope-control (builder-side discipline) with scope-compliance
  (reviewer-side verification) — this skill is the reviewer half (R-001).
