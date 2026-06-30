# {project_name}

<!-- one-line project definition — filled at bootstrap -->

<!-- ASPIS:BOOTSTRAP-GATE:START -->
> **First run — one-time setup.** This project is exported but not yet *live* (its
> brain is empty, its leads are not active). It must be onboarded once before any work.
> Either **switch to the `bootstrap` agent** (the onboarding agent — pick it in your
> runtime's agent picker and tell it what you want to build) **or** run `aspis bootstrap
> --write` in a terminal. Bootstrap confirms the project's name, goal, and stack *with
> you*, then makes it live. The entry agent (`project-lead`) starts no other work until
> this is done. This notice and the bootstrap agent are removed automatically once the
> project is live.
<!-- ASPIS:BOOTSTRAP-GATE:END -->

This project is managed with **ASPIS**. Durable project state lives in plain
files under `.aspis/` (the project "brain"), so any AI runtime reads and writes
the same source of truth.

## Start here — project context

These are the canonical entry points, kept current automatically. Read the live
state first; open source files only once you know which the task needs.

- `.aspis/context/CURRENT_STATE.md` — where the project is right now.
- `.aspis/context/RECENT_CHANGES.md` — what changed recently, newest first.
- `.aspis/index/FILE_REGISTRY.yaml` — every file and its purpose; use it to locate
  code without scanning the tree. A file's purpose is derived in three layers, all
  configured in one file, `.aspis/config/purposes.json`: its own top docstring/comment;
  a common-purpose map for well-known files (`names`/`patterns`); and explicit per-file
  purposes (`files`: `{"path": "purpose"}`). When you create a file that can't carry a
  docstring (JSON, data) and is not a known type, register it under `files`. No file
  should have a blank purpose — `build_registry.py --check` lists the gaps.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports);
  use it to understand a file without reading its body.

## Rules

The non-negotiable system rules (R-001…) live in `.aspis/rules/system-rules.md` —
read them, follow them by ID, don't restate them. Project-specific rules, when
present, live in `.aspis/rules/project-rules.md`.

<!-- Stack: <stack> — filled at bootstrap -->
