---
name: build-readiness
description: Use before starting implementation to confirm the work can safely begin — the repository, branch, and feature state are clean and known. Prevents building from an unknown or conflicting state.
---

# Build Readiness

## Purpose

Never start implementation from an unknown state. A quick, disciplined pre-work
check catches uncommitted changes, the wrong branch, or unfinished work before
they corrupt a build.

## When to use

First, when taking ownership of a feature for implementation, before delegating
any task.

## Procedure

1. **Repository state.** `git status` is clean (or expected changes are accounted
   for); no stray uncommitted or conflicting work.
2. **Branch.** On the correct feature branch, up to date with its base.
3. **Feature state.** The plan, task list, and packets exist and are approved;
   the feature is actually ready to build.
4. **Confirm or stop.** If anything is unclear or conflicting, resolve or stop and
   report — do not build over an unknown state.

## Outputs

- A go/no-go readiness verdict, with the specific blocker if not ready.

## Anti-patterns

- Building on a dirty tree or the wrong branch.
- Starting before the plan and packets are approved.
- Treating readiness as a formality and skipping the actual checks.
