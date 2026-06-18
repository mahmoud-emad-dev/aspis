# {project_name} — Claude Code guide

<!-- one-line project definition — filled at bootstrap -->

This project is built with **ASPIS**, a file-first software-production system.
All durable project state lives in plain files under `.asps/` (the project
"brain") so any AI runtime reads and writes the same source of truth.

## How to work here

- **Read first.** Before changing code, read `.asps/context/CURRENT_STATE.md` and
  `.asps/context/RECENT_CHANGES.md`, then use `.asps/index/FILE_REGISTRY.yaml` to
  locate the files a task touches. These are kept current automatically.
- **Scope.** Only modify what the active task allows; never touch files outside it.
- **Gates first.** Run the project's checks (lint, types, tests) before declaring work
  done. Never weaken or delete a test just to make a gate pass.
- **Trace.** Record what you changed and why — no silent edits.

## Where things live

- `.asps/context/` — current state and recent changes (the live snapshot).
- `.asps/index/FILE_REGISTRY.yaml` — the map of every file and its purpose.
- `.asps/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports).
- `.asps/features/` — per-feature plans and tasks.

<!-- Stack: <stack> — filled at bootstrap -->
