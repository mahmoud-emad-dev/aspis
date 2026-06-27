---
name: prestart-checks
description: Run before creating or editing any file — confirm the repo is in a safe state to start (clean tree, right branch) with one deterministic command, and resolve or route any blocker before working. Keeps an agent from building on top of someone else's uncommitted changes or on the wrong branch.
---

# Prestart checks

Before you create or edit files, confirm the project is safe to start on — so your work never
lands on top of someone else's uncommitted changes or on the wrong branch.

## Run the gate first

```
aspis preflight
```

- **Ready (exit 0):** the tree is clean and the branch matches the active feature — start working.
- **Blocker (non-zero):** do **not** edit. Resolve first, then re-run until it is Ready:
  - finished, reviewed work in the tree → hand it to the `committer` (see the `commit-message` skill);
  - unrelated uncommitted work → stash it deliberately (never edit on top of it);
  - wrong branch → `git checkout <the active feature's branch>`;
  - **open findings** (a guard flagged a wrong state) → inspect with `aspis findings`, fix or route
    the cause, then `aspis findings --resolve <n>`.

Generated brain churn (`.aspis/index/`, `.aspis/context/`) is expected and never blocks — `aspis
preflight` already ignores it. This is the active form of the `clean-tree-precondition` rule.

## Bootstrap exception

The one-time `bootstrap` agent is exempt: it runs on a not-yet-live project whose tree carries the
fresh export it is about to commit, so the clean-tree gate does not apply. It uses its own first-step
check instead of `aspis preflight`. Preflight applies once the project is live (an active feature exists).
