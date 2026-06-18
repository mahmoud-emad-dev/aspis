# {project_name}

<!-- one-line project definition — filled at bootstrap -->

This project is managed with **ASPIS**. Durable project state lives in plain
files under `.asps/` (the project "brain"), so any AI runtime reads and writes
the same source of truth.

## Rules for any AI agent

1. **Scope** — only modify what the active task allows; never touch files outside it.
2. **Gates first** — run the project's checks before calling work done; never weaken a test to pass.
3. **Trace** — record what you changed and why; no silent edits.

<!-- Stack: <stack> — filled at bootstrap -->
