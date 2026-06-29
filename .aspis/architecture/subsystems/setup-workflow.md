# Subsystem: setup-workflow

- **Status:** active
- **Created:** 2026-06-29   **Last reviewed:** 2026-06-29
- **One-liner:** The orchestration layer that turns first-run into ONE guided command — sequencing init → pre-bootstrap → onboarding → bootstrap → post-heal → ready, with skip and resume — so the user never has to remember separate commands.

## Why it exists (problem)
The operations (initialization, bootstrapping, the pre-bootstrap resolution, the post-heal) are
each independent and own only themselves. Something has to **sequence** them into a single, smooth,
friendly experience — handle transitions, the post-init decision screen, onboarding flow, progress,
skip, and resume — without the user invoking `init`, `bootstrap`, `models sync`, `apply` by hand.
That orchestration is a distinct concern from any one operation; keeping it separate is what lets
each operation stay simple and testable while the user sees one command.

## Responsibilities & boundaries
- **Owns:** the guided CLI flow after `aspis init` (decision screen: continue / skip / open a
  runtime / stop); the order of stages (init → pre-bootstrap → onboarding → bootstrap → post-heal →
  ready); transitions, progress display, colors/installer-feel; **skip** (leave a valid project) and
  **resume** (continue from `.aspis/current/bootstrap_state.json`, never restart); surfacing runtime
  continuation (exact launch command) and multi-runtime options.
- **Does NOT own:** the internals of any operation (each operation is Before→Core→After and owns
  itself); AI decisions, stack/mode confirmation (bootstrap agent + user), or model resolution
  (models-intelligence). The workflow sequences and presents; it does not do the work itself.

## Current behaviour (FIXED vs OPEN)
- **Today (as-built):** there is **no** formal workflow layer. `aspis init` and `aspis bootstrap`
  are separate commands; the handoff is carried by the project-lead first-action gate (run
  `aspis bootstrap --check` → delegate to the bootstrap agent). This works but is not the guided
  one-command experience.
- **FIXED (target invariants for F-020):** one user command (`aspis init`) with automatic,
  **non-blocking** follow-through; every stage **skippable** and **resumable**; operations stay
  independent (the workflow only orchestrates); a skipped run still leaves a **valid, runnable**
  project.
- **OPEN:** the exact screens/prompts; resume granularity; whether the orchestrator is a flag on
  `init` or its own internal driver; how much progress/telemetry to show.

## Integrations
- **Sequences** initialization + the pre-bootstrap resolution + bootstrapping + the post-heal.
  **Reads/writes** `.aspis/current/bootstrap_state.json` for resume/skip state. **Surfaces**
  runtime continuation from the runtime inventory (models-intelligence/detection). A change to any
  operation's stage boundaries ripples into the workflow's transitions.

## System contracts (guarantees)
A user runs **one** command and is guided to either a **live** project (continue) or a **valid,
runnable** project (skip); an interrupted run **resumes** from the decision state rather than
restarting; onboarding is **never re-asked** once complete; nothing blocks automation/CI (defaults
+ `--yes`).

## Future direction (F-020 builds this)
F-020 introduces this layer (the two-layer Operations/Workflow model from the new vision). Reserve
seams for later: named pre-init/post-init extension points; a future served onboarding GUI; the
global-tier install workflow (platform phase). Keep it a thin orchestrator over independent
operations.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-29 — Status → active. F-020 delivered: `operations/setup_workflow.py` (guided
  decision screen + state-machine next-step + resume), `aspis init` guided follow-through.
- 2026-06-29 — Created (F-020 planning). Status proposed pending the F-020 build. Defines the
  orchestration layer that was held in F-019; sequences init → pre-bootstrap → onboarding →
  bootstrap → post-heal → ready, skippable + resumable, one guided command.
