---
name: scope-control
description: Use throughout implementation to keep the work inside its planned boundaries — only the allowed files change, no unrelated edits, no architecture drift, no gold-plating. Keeps the feature aligned with planned intent.
---

# Scope Control

## Purpose

Protect the boundary between what was planned and what gets built. Scope creep,
drift, and unrequested "improvements" are how a clean plan turns into a risky,
unreviewable change.

## When to use

Continuously during implementation — when validating packets, reviewing worker
reports, and before accepting a task as done.

## Procedure

1. **Hold the allowed files.** Each task changes only the files its packet allows;
   anything else is out of scope.
2. **Reject unrelated edits.** Drive-by refactors and cleanups outside the task go
   back out — capture them as future work, don't smuggle them in.
3. **Guard the architecture.** Implementation follows the approved design; a needed
   deviation is escalated, not made silently.
4. **No gold-plating.** Build what the plan calls for, not extra complexity beyond it.
5. **Check the diff.** Confirm `git diff` touches only in-scope paths before a task
   is accepted.

## Outputs

- Changes confined to planned scope; out-of-scope work surfaced as new items.

## Anti-patterns

- "While I was in here, I also changed…" outside the task.
- Silent architecture deviations.
- Expanding scope to make a task feel more complete.
