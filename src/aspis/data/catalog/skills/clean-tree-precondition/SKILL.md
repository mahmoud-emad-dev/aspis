---
name: clean-tree-precondition
description: Every editing agent should start on a clean working tree so parallel work never collides.
---

# Clean-tree precondition

Before an agent creates or edits files, the working tree should be clean — no
uncommitted changes from a previous task. Otherwise two pieces of work edit over each
other and produce a tangled, unreviewable diff.

## Check

```
git status --porcelain     # empty output = clean
```

## If the tree is dirty

1. Identify the uncommitted work (`git status --short` lists staged/untracked).
2. If it is finished, reviewed work, hand it to the committer to commit (the
   `commit-message` skill). If it is unrelated, stash it deliberately — never
   edit on top of it.
3. Re-check; only start editing once `git status --porcelain` is empty.

## Note on generated brain files

The post-commit hook refreshes the generated context/index (CURRENT_STATE,
RECENT_CHANGES, FILE_REGISTRY, CODE_MAP) after each commit, so they may show as dirty.
That churn is expected — fold it into the next commit; it is not a reason to stop work.

## Rule

Do not begin a task on a dirty tree of *unrelated* work. A clean start is what makes
sequential delegation (and later, worktrees) safe.
