---
name: commit-splitting
description: Keep commits atomic — split a mixed change set into scoped, reviewable commits.
---

# Commit splitting

One commit = one logical change. A change that mixes concerns (source + tests + docs +
config) is hard to review and to revert. Split it.

## When to split

- The change touches more than one concern (e.g. a feature plus unrelated docs).
- The diff is large enough that a reviewer cannot hold it in their head.
- Parts of the change belong to different tasks.

## Flow

1. See what changed and group it by concern:
   ```
   git status --short
   ```
   Bucket the files (source area / tests / docs / config), and decide if the set is
   already one logical change. If it is, commit it as one unit.
2. For each group, make one commit with the named paths only — `aspis commit` stages
   exactly those paths (never `-A`):
   ```
   aspis commit <paths-for-this-group> --type <type> --task <T-NN> \
     --title "<scoped title>" --bullet "<what>"
   ```
3. Repeat until the tree is clean.

## Rules

- Never `git add -A` across concerns; name the paths for each commit.
- Each commit should build and pass its own gate where practical.
- Prefer several small, clearly-scoped commits over one large mixed one.
- A commit spanning several planned tasks uses the span scope `T-NN..T-MM` (see the
  `commit-message` skill); never label a multi-task commit with only its first task.
