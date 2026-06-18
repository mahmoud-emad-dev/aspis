# ASPIS

The file-first agentic software production factory that builds and ships agent runtimes

This project is managed with **ASPIS**. Durable project state lives in plain
files under `.aspis/` (the project "brain"), so any AI runtime reads and writes
the same source of truth.

## Durable governance — read first

The *why* behind ASPIS; read once before scoped work.

- `.aspis/context/IDENTITY.md` — what ASPIS is and is not.
- `.aspis/context/ARCHITECTURE.md` — the target architecture (the contract).
- `.aspis/context/DECISIONS.md` — durable, dated decisions (D-001…).
- `.aspis/context/ROADMAP.md` — where the system is going and where it is now.
- `.aspis/rules/system-rules.md` — the non-negotiable system rules (R-001…).

## Live state — read at the start of every session

Kept current automatically. Read the live state first; open source files only once
you know which the task needs.

- `.aspis/context/CURRENT_STATE.md` — where the project is right now.
- `.aspis/context/RECENT_CHANGES.md` — what changed recently, newest first.
- `.aspis/index/FILE_REGISTRY.yaml` — every file and its purpose; use it to locate
  code without scanning the tree.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports);
  use it to understand a file without reading its body.

**Stack:** python
