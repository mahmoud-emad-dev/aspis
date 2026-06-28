# Workflow: Bootstrap a project (first-run onboarding)

The one-time path that turns an **exported** project (files materialized by
`aspis init`) into a **live** one: brain seeded, leads promoted, first commit made,
the project self-explaining — so every agent that runs afterward finds a complete,
filled, ready system. This package **removes itself** once the project is live.

## When to use

- The very first user message in a project that is not yet bootstrapped
  (`aspis bootstrap --check` exits non-zero).
- `project-lead` detects an un-bootstrapped project and routes here before any
  feature work (the first-message gate).

Never run feature work (plan/build/review) on an un-bootstrapped project — route
through this workflow first.

## Agent sequence

```
project-lead → runs `aspis bootstrap --check`; if NOT live, routes to bootstrap
bootstrap    → loads project-onboarding skill, drives the run:
                 1. detect (stack, git, runtimes, emptiness)
                 2. confirm or skip (never blocks; --yes = non-interactive)
                 3. draft ARCHITECTURE.md from the real layout (existing code; before the spine)
                 4. aspis bootstrap --write   (deterministic spine; self-cleans once ready)
                 5. finish enrichment: AGENTS.md definition + file purposes (bounded)
                 6. verify: doctor 0-FAIL, brain seeded, architecture real, 5 primaries
bootstrap    → hands a one-line readiness summary back to project-lead
project-lead → continues with the user's original request
```

## What is deterministic vs. agent-driven

The CLI does everything that can be done without judgment; the agent does only what
needs reasoning, and only from facts the detector produced.

| Step | Owner |
|---|---|
| Detect stack / git / runtimes / emptiness | script (`detect`) |
| Fill AGENTS.md / CLAUDE.md slots, write `project.yaml` + manifest | script (`bootstrap_core`) |
| Seed the brain (FILE_REGISTRY, CODE_MAP, CURRENT_STATE) | script (`context/update.py`) |
| Promote the 4 leads to primary (→ 5 total) | script (`promote_leads`) |
| Draft `ARCHITECTURE.md` (before the spine); enrich AGENTS.md definition + file purposes | **agent** (`project-onboarding`) |
| First + bootstrap commits, doctor + readiness gate, self-clean | script (pre/post stages) |

## Bounded autonomy (D-B6)

The bootstrap agent enriches **only** from detected facts and templates, and writes
**only** under: `.aspis/`, `.opencode/`, `.claude/`, `AGENTS.md`, `.gitignore`. It
never touches the user's own namespace (`src/`, `tests/`, app code) and never edits
rules, permissions, or model routing.

## Exit criteria

- `aspis bootstrap --check` exits 0 (manifest `bootstrapped: true`).
- `aspis doctor` shows no FAIL; the working tree is clean (auto-committed).
- The brain is filled: `.aspis/index/FILE_REGISTRY.yaml`, `CODE_MAP.md`, and
  `.aspis/context/CURRENT_STATE.md` exist and are non-empty.
- For an existing-code project, `.aspis/context/ARCHITECTURE.md` is real (past the
  seeded skeleton); a greenfield project may leave it for the first feature.
- Exactly five `mode: primary` agents (project-lead + planning-lead + build-lead +
  reviewer + system-lead).
- `bootstrap.done` recorded; the bootstrap package (agent + skill + this workflow)
  is removed from the project runtime.
- Re-running is idempotent: no duplicate commits, no re-prompting, the package stays
  gone.

## Idempotency

After a green run the manifest carries the bootstrapped flag, so `--check`
short-circuits and the entry agent never mentions bootstrap again. Re-running
`aspis bootstrap --write` is a safe RESUME: it re-seeds the brain and re-runs the
health gate without re-committing unchanged files.
