# Your first ASPIS build — a worked example

The clearest worked example of ASPIS is **ASPIS itself**: this repository is a live
ASPIS project that builds its own catalog and CLI through the same `plan → build →
review → commit` loop it ships to you. Every feature lives as plain files you can read.
This page walks one real, completed feature end-to-end, then shows how to do the same on
your project.

## The case study — F-007, the git subsystem

A real feature, built and merged through the loop. Its artifacts are in the repo:

```
.aspis/features/F-007-git/
  SPEC.md     # the goal, scope, user stories, success criteria
  PLAN.md     # the approach + build order
  TASKS.md    # the task list, checked off as built
```

### 1. Plan — clarity before code
`SPEC.md` fixes *what* and *why*: the committer becomes the single commit authority; the
agent composes, a tool builds the message, the hooks enforce. `scope.allowed` /
`scope.forbidden` bound the change so nothing drifts. `TASKS.md` breaks it into small,
ordered tasks (T-00…T-05).

### 2. Build — one task, gates-first
Each task is implemented and **proven by the deterministic gate** before it counts:

```bash
uv run ruff format --check .   &&   uv run ruff check .   &&   uv run pytest -q
```

Nothing is "done" on a model's say-so — it's done when the gate is green. F-007 added
`scripts/git/compose.py` and the `aspis commit` tool, each landing green.

### 3. Review — independent check
A reviewer checks the change against the SPEC's scope, the gates, and the acceptance
criteria — separately from whoever built it.

### 4. Commit — one authority, one convention
Every F-007 commit was made with the very tool it introduced — `aspis commit` —
which stages explicit paths, composes a conventional message, and lets the hooks
enforce it. The history reads as one clean, in-order line:

```
feat(F-007/T-01): compose tool + the aspis commit verb
feat(F-007/T-02): committer uses aspis commit; ship commit skills
test(F-007/T-03): cover compose + aspis commit
docs(F-007/T-04): record the why - D-011, architecture, roadmap
Merge feature F-007: git subsystem
```

## What ASPIS adds over a bare runtime

| Without ASPIS | With ASPIS |
| --- | --- |
| "Looks done" — trust the model | **Gate-green or it isn't done** (ruff + pytest) |
| Scope drifts across files | **Scope is declared** and the hooks flag out-of-scope edits |
| Ad-hoc commit messages, `git add -A` | **One commit authority**, a data-driven convention, explicit paths |
| Rules live in a prompt and rot | Rules are **files** — system rules + an architecture constitution agents enforce |
| State lives in a chat session | State lives in **`.aspis/` files**, in Git, readable by any runtime |
| Each model/runtime reinvents the setup | One **brain**, exported to Claude Code *and* OpenCode |

The bet, made concrete: *clarity × tests × review* let the cheapest sufficient model
produce production-grade work — repeatably.

## Do it on your project

```bash
aspis init . --write       # scaffold the brain + runtime
aspis bootstrap            # goal, stack, default mode
# open the project in Claude Code or OpenCode, then run the loop:
#   plan  → SPEC / PLAN / TASKS
#   build → one task at a time, gate-green
#   review→ independent check
aspis commit <paths…> --type feat --task T-01 --title "…" --bullet "…"
```

See the **[Quickstart](QUICKSTART.md)** for the full first-run walkthrough.
