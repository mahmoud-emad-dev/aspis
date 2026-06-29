# {project_name} — Claude Code guide

<!-- one-line project definition — filled at bootstrap -->

<!-- ASPIS:BOOTSTRAP-GATE:START -->
> **First run — one-time setup.** This project is exported but not yet *live*. The entry
> agent (`project-lead`) detects this on its first action and **delegates to the
> `bootstrap`** agent, which makes the project live before any other work — so just say
> what you want and let it route; no task runs on an un-bootstrapped project. (To
> bootstrap from a terminal yourself: `aspis bootstrap --write`.) This notice and the
> bootstrap agent are removed automatically once live.
<!-- ASPIS:BOOTSTRAP-GATE:END -->

This project is built with **ASPIS**, a file-first software-production system.
All durable project state lives in plain files under `.aspis/` (the project
"brain") so any AI runtime reads and writes the same source of truth.

## How to work here

- **Read first.** Before changing code, read `.aspis/context/CURRENT_STATE.md` and
  `.aspis/context/RECENT_CHANGES.md`, then use `.aspis/index/FILE_REGISTRY.yaml` to
  locate the files a task touches. These are kept current automatically.
- **Follow the rules.** The system rules (R-001…) live in
  `.aspis/rules/system-rules.md` — follow them by ID; don't restate them. Project
  rules, when present, live in `.aspis/rules/project-rules.md`.

## Where things live

- `.aspis/context/` — current state and recent changes (the live snapshot).
- `.aspis/rules/system-rules.md` — the non-negotiable system rules.
- `.aspis/index/FILE_REGISTRY.yaml` — the map of every file and its purpose.
- `.aspis/index/CODE_MAP.md` — each Python file's skeleton (signatures + imports).
- `.aspis/features/` — per-feature plans and tasks.

<!-- Stack: <stack> — filled at bootstrap -->
