# {project_name}

<!-- one-line project definition — filled at bootstrap -->

This project is managed with **ASPIS**. Durable project state lives in plain
files under `.asps/` (the project "brain"), so any AI runtime reads and writes
the same source of truth.

## Start here — project context

These are the canonical entry points, kept current automatically. Read the live
state first; open source files only once you know which the task needs.

- `.asps/context/CURRENT_STATE.md` — where the project is right now.
- `.asps/context/RECENT_CHANGES.md` — what changed recently, newest first.
- `.asps/index/FILE_REGISTRY.yaml` — every source file and its purpose; use it to
  locate code without scanning the tree.

## Rules for any AI agent

1. **Scope** — only modify what the active task allows; never touch files outside it.
2. **Gates first** — run the project's checks before calling work done; never weaken a test to pass.
3. **Trace** — record what you changed and why; no silent edits.

<!-- Stack: <stack> — filled at bootstrap -->
