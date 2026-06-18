# ASPIS — Claude Code guide

The file-first agentic software production factory that builds and ships agent runtimes

This project is built with **ASPIS**, a file-first software-production system.
All durable project state lives in plain files under `.aspis/` (the project
"brain") so any AI runtime reads and writes the same source of truth.

## How to work here

- **Understand the why first.** Read `.aspis/context/IDENTITY.md`,
  `ARCHITECTURE.md`, `DECISIONS.md`, and `ROADMAP.md` before scoped work.
- **Read the live state.** Then read `.aspis/context/CURRENT_STATE.md` and
  `RECENT_CHANGES.md`, and use `.aspis/index/FILE_REGISTRY.yaml` to locate files.
  These are kept current automatically.
- **Follow the rules.** The system rules (R-001…) live in
  `.aspis/rules/system-rules.md` — follow them by ID; don't restate them.

## Where things live

- `.aspis/context/` — identity, architecture, decisions, roadmap, and live state.
- `.aspis/rules/system-rules.md` — the non-negotiable system rules.
- `.aspis/index/FILE_REGISTRY.yaml` — the map of every file and its purpose.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports).
- `.aspis/features/` — per-feature plans and tasks.

**Stack:** python
