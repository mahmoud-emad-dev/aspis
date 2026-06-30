# F-020 — Tasks

> Mode: **production**, but **coarse big-task** granularity (the planner also applies). Each task
> lands with tests + green gates (ruff · pytest · validate-runtime 33/33) and changes **no** model files.

## Phase 1 — Foundational (read-only truth + state)
- [ ] **T-01 Pre-bootstrap resolution layer.** New read-only stage that classifies the project
  **state machine** (empty / initialized-not-onboarded / bootstrapped / legacy-ASPIS / incomplete-
  ASPIS / existing-code), builds the runtime/subscription/model-availability inventory (reuse
  `detect`/`runtime_inventory`/`settings` — no duplication), computes **stack + confidence**, loads
  system/project/user rule layers, and detects **plan files** (root + `docs/`, names
  `plan|arch|architecture|spec|prd|roadmap`, formats `.md/.html/.pdf/.txt/.docx`). Writes
  `.aspis/current/bootstrap_state.json`. Zero side effects beyond the state file.
  (`operations/pre_bootstrap.py`, `tests/test_pre_bootstrap.py`)

## Phase 2 — Orchestration + UX (the guided one command)
- [ ] **T-02 setup-workflow orchestrator.** Post-init decision screen (continue / skip / open
  runtime / stop); sequence init → pre-bootstrap → onboarding → bootstrap → post-heal → ready;
  **skip** leaves a valid project; **resume** from `bootstrap_state.json`; surface runtime
  continuation (exact launch command) + optional multi-runtime add. Non-blocking; `--yes` headless.
  (`operations/` + CLI on `init`, `tests/test_setup_workflow.py`)
- [ ] **T-03 Clear onboarding UX.** Per-question **meaning + example + default** for mode / goal /
  description / stack / runtime; explain vibe/mvp/production (meaning, speed, what each runs);
  colors/progress; ask-one-by-one or grouped; never block. (`operations/bootstrap.py`, `tests/`)

## Phase 3 — Bootstrap intelligence (asks, never decides)
- [ ] **T-04 Bootstrap agent + onboarding skill.** Edit catalog `agents/bootstrap.md` +
  `skills/project-onboarding/`: **confirm stack + mode with the user, never self-decide**; read the
  rule layers (user `.md` at configurable path + project + system); use **research-lead** for
  "latest/best/scalable stack & patterns" (never invent from cutoff); **read a detected plan file**
  to inform enrichment; do a **file-by-file enrichment review** (after init, per brain/project file:
  placeholder? stale? needs fill? → update). project-lead delegates + confirms on return.
  (catalog `agents/bootstrap.md`, `skills/project-onboarding/SKILL.md`; validate-runtime)
- [ ] **T-05 Rules reading + project-rules seed.** Read user(.md, configurable path)/project/system
  rule layers in pre-bootstrap; seed **project rules** via the rules subsystem (later changes via
  governance R-008). (`operations/`, `tests/`)

## Phase 4 — Robustness floor
- [ ] **T-06 Confidence-driven, correctable stack.** Confidence model (high/medium/unknown),
  robust format/regex, manual fallback, a later-correction verb (e.g. `aspis stack set <stack>`),
  and write stack → context + manifest + `.gitignore`. Not one-shot. (`detect.py`, new verb, `tests/`)
- [ ] **T-07 Deterministic post-bootstrap self-heal.** A post-stage that, when the agent didn't
  enrich (weak/offline/failed), deterministically fills/refreshes context files, FILE_REGISTRY,
  build history, `.gitignore` from stack, stack→context+manifest, via the update-all-context
  generators. **Expected files only — never invented content.** (`operations/` post-stage, `tests/`)
- [ ] **T-08 State machine recovery + resume.** Safe re-init/upgrade (never destroy `.aspis` or user
  code); resume interrupted init/onboarding/bootstrap from the state file; skippable; detect
  not-yet-bootstrapped when a runtime is used. (`detect.py`/`project.py` + guards, `tests/`)

## Phase 5 — Completeness + acceptance
- [ ] **T-09 Init export completeness.** Ensure init exports the full, current asset set — no
  missing or outdated agent/skill/instruction/template/script; add a check that flags gaps.
  (`export`/`init` + `tests/`)
- [ ] **T-10 Acceptance E2E + full gate sweep.** Empty dir → guided flow → live; skip leaves valid;
  resume continues; weak-agent run still ends non-skeleton (post-heal); existing-project safety; no
  model files changed. ruff + pytest + validate-runtime 33/33. Update subsystem changelogs + DECISIONS.
  (`tests/test_f020_e2e.py`)

## Phase 6 — Runtime choice + model floor (continuation, 2026-06-30)
- [x] **T-11 Runtime detection + interactive selection.** When no `--runtime` is pinned, detect the
  installed *supported* runtimes and offer a TTY multi-select menu (one or more). None installed →
  show the OpenCode install URL/command and proceed with OpenCode only after the user confirms;
  **never install a runtime, never auto-pick one the user didn't choose**. Pure logic in
  `operations/runtime_select.py`; I/O loop in `commands/init.py`; `init_core` stays deterministic.
  (`tests/test_runtime_select.py`)
- [x] **T-12 Runtime-aware lead model floor (pre-bootstrap).** Before export, seed the project's
  `agent-models.yaml` so the leads (`project-lead`/`bootstrap`/`*-lead`) render with a capable model
  *before* the runtime TUI/bootstrap. Temp policy: Claude→`claude-sonnet-4-6`,
  OpenCode→`opencode-go/deepseek-v4-pro`. Writes only the project file — **catalog model map stays
  frozen** (full best-available engine = F-021). (`operations/model_defaults.py`, `tests/test_model_floor.py`)

## Dependencies & execution order
- T-01 first (everything consumes the state machine + state file). Then T-02/T-03 (the flow),
  T-04/T-05 (bootstrap intelligence), T-06/T-07/T-08 (robustness), T-09/T-10 (completeness + gate).
- Within each task: tests alongside the change; gates green before moving on.

## Implementation strategy
- Ship each big task as its own commit (scope `F-020` or `F-020/SYS` for runtime/agent changes),
  gates green, on the branch. Pause for owner review at the end of each phase.
- Re-read the FIXED blocks of `initialization.md` + `bootstrapping.md` before each task.
