# {project_name} — Claude Code guide

<!-- one-line project definition — filled at bootstrap -->

This project is built with **ASPIS**, a file-first software-production system.
All durable project state lives in plain files under `.asps/` (the project
"brain") so any AI runtime reads and writes the same source of truth.

## How to work here

- **Read first.** Start from `.asps/context/` to learn current state before changing code.
- **Scope.** Only modify what the active task allows; never touch files outside it.
- **Gates first.** Run the project's checks (lint, types, tests) before declaring work
  done. Never weaken or delete a test just to make a gate pass.
- **Trace.** Record what you changed and why — no silent edits.

## Where things live

- `.asps/context/` — durable project context and current state.
- `.asps/features/` — per-feature plans and tasks.
- `src/`, `tests/` — the product being built.

<!-- Stack: <stack> — filled at bootstrap -->
