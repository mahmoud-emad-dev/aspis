# {project_name}

<!-- one-line project definition — filled at bootstrap -->

This project is managed with **ASPIS**. Durable project state lives in plain
files under `.aspis/` (the project "brain"), so any AI runtime reads and writes
the same source of truth.

## Start here — project context

These are the canonical entry points, kept current automatically. Read the live
state first; open source files only once you know which the task needs.

- `.aspis/context/CURRENT_STATE.md` — where the project is right now.
- `.aspis/context/RECENT_CHANGES.md` — what changed recently, newest first.
- `.aspis/index/FILE_REGISTRY.yaml` — every file and its purpose; use it to locate
  code without scanning the tree.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports);
  use it to understand a file without reading its body.

## Rules

The non-negotiable system rules (R-001…) live in `.aspis/rules/system-rules.md` —
read them, follow them by ID, don't restate them. Project-specific rules, when
present, live in `.aspis/rules/project-rules.md`.

<!-- Stack: <stack> — filled at bootstrap -->
