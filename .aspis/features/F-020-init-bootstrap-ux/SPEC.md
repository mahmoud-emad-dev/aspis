# F-020 — Accurate, guided Init + Bootstrap UX · Specification

> Mode: **production** — auto-escalated (architecture change to the initialization & bootstrapping
> subsystems + protected paths + many files). Honors the **FIXED (must not break)** contracts in
> `.aspis/architecture/subsystems/initialization.md` and `…/bootstrapping.md`.

## Goal
Make first-run **one simple command with a guided, clear, friendly follow-through**: `aspis init`
scaffolds, then ASPIS guides the user through onboarding and makes the project live — without the
user needing to remember `bootstrap` / `import` / `models sync` / `runtime apply`, and without
needing to already know what "mode", "goal", "description", or "stack" mean. The result is a
correct, working project every time — even on a weak/free model, offline, or after an agent fails —
because a deterministic layer guarantees the floor.

## Problem
Today init→bootstrap works mechanically but the **UX and accuracy** fall short of the intent:
- The user must run several commands and already understand build modes, goal/description, and
  stack — there are **no hints/examples**, so onboarding is opaque to a normal user.
- Stack detection is one-shot and brittle (format failures), with no confidence model, no manual
  fallback, and no later correction.
- There is **no pre-bootstrap resolution layer**: runtime usability, subscriptions/model
  availability, the full project-state machine, and the rule layers aren't gathered/confirmed
  before bootstrap acts — so the system can start on a broken/free-bad setup or an unconfirmed mode.
- The **bootstrap agent can act on its own** (guess/confirm) instead of asking the user; mode and
  stack — which shape everything — can be set without explicit user confirmation.
- If an agent is weak/offline/fails, the project can be left half-enriched: context, registry,
  history, gitignore, and stack not filled — with **no deterministic self-heal**.
- No plan-file awareness (a user dropping a plan can't have it read for stack/patterns), no
  resumable onboarding, and weak guards for legacy/incomplete-ASPIS / existing-code projects.

## Scope
In scope:
- A **guided one-command flow**: after `aspis init`, a clear decision screen (continue onboarding /
  skip for now / open a runtime to continue / stop after scaffold) and automatic follow-through.
- A **pre-bootstrap resolution layer** (read-only truth-gathering, its own scripts/stage — NOT
  inside bootstrap): runtime inventory + usability, subscription/model availability, the project
  **state machine**, **stack detection with confidence**, and loading the system/project/user rule
  layers. Writes a resumable `.aspis/current/bootstrap_state.json` (the decision state bootstrap
  consumes). Reuses existing `detect`/`runtime_inventory`/`settings` modules — does not duplicate.
- **Clear onboarding** with hints/examples for every question: build **mode** (vibe/mvp/production
  — what each means, how fast, what steps it runs), **goal**, **description**, **stack** (how to
  write it, e.g. `python`, `typescript+fastapi`, `langgraph`), runtime(s). Colors/progress;
  ask-one-by-one or a clear grouped onboarding; minimum questions; every prompt has a default.
- **Plan-file awareness**: detect a plan file at a known location (the user may drop a ChatGPT/др.
  plan into the repo), and let the bootstrap agent **read it** to learn stack/patterns/description
  for enrichment; ask for a plan when one would help. (Detection deterministic; reading by agent.)
- **Bootstrap agent behavior**: `project-lead` delegates to the `bootstrap` agent; the bootstrap
  agent **asks and confirms with the user** — it never self-decides stack or mode. It reviews the
  rule layers; it may use **research-lead** for "latest/best/scalable stack & market patterns"
  when the user asks for that, instead of inventing a stack from model cutoff; it returns to
  project-lead, who confirms with the user.
- **Rules integration**: read user rules (from a configurable path if present) + project + system
  rules to inform stack/style; seed **project rules** via the rules subsystem (bootstrap may
  call/init it; later rule changes go through governance R-008).
- **Post-bootstrap deterministic self-heal**: a post-stage that, via scripts, guarantees the floor
  even if the agent was weak/offline/failed — fill/refresh context files, FILE_REGISTRY, build
  history, `.gitignore` from stack, and write the stack into context + manifest; run the
  update-all-context generators. **Deterministic restore of expected files only — never agent
  invention** (upholds bootstrapping FIXED #6 / the IB-4 definition).
- **State machine + recovery + resume**: detect empty / initialized-not-onboarded / bootstrapped /
  legacy-ASPIS / incomplete-ASPIS / existing-code; re-init/upgrade never destroys an existing
  `.aspis` brain or user code; interrupted init/onboarding/bootstrap resumes from
  `bootstrap_state.json`. Skippable; system detects "not yet bootstrapped" when a runtime is used.
- **Runtime continuation**: show detected runtimes; offer to continue in this CLI (full onboarding)
  or **open a runtime tool with the exact launch command** (CLI/TUI/GUI/desktop), telling the user
  it will start with project-lead → delegates to bootstrap; offer installing additional runtimes
  (optional, with the exact command). Ensure the correct settings module + model are set for the
  bootstrap/project-lead agent **before** they are used.

Out of scope (deferred / forbidden here):
- The **deep model decision engine** (Discover→Inventory→Subscriptions→Capabilities→Policy→
  Assignments) and any change to model files — that is **F-021 (models-intelligence)**; models are
  **frozen** (do NOT run `aspis export`/`models --apply`). F-020 only *detects/recommends* and
  **reserves the seam** that F-021's resolver fills; pre-bootstrap records the inventory.
- The **git subsystem** re-arch (commit staging, branch policy) — **F-022**.
- The remote catalog / global cross-project brain / onboarding GUI dashboard — platform phase.
- Defining the **canonical global user-rules path** — read it if present at a configurable path;
  the canonical location is reserved (owner to define later).
- Any edit to catalog-managed agent **bodies** by the self-erase mechanism (parity moat — use the
  marker-strip on deployed copies + the export-only package, per bootstrapping FIXED #4).

## User stories
Prioritized; each independently testable. P1 = MVP slice.

### Story 1 — One guided command (priority: P1) 🎯
- **Why first**: this is the headline UX; everything else hangs off the guided flow.
- **Independent test**: `aspis init --write` on an empty dir scaffolds, then presents a clear
  decision screen (continue / skip / open runtime / stop); choosing "continue" runs the rest
  automatically to a live project; "skip" leaves a valid, runnable project.
- **Acceptance**:
  1. **Given** an empty dir, **when** `aspis init` runs, **then** the project is structurally
     complete and the user is shown next-step options in plain language (no command memorization).
  2. **Given** "continue onboarding", **when** chosen, **then** pre-bootstrap → onboarding →
     bootstrap → post-heal run as automatic internal stages, ending live.

### Story 2 — Clear onboarding with hints/examples (priority: P1)
- **Why**: the user doesn't know what mode/goal/description/stack mean; opacity is the core pain.
- **Independent test**: each onboarding question shows a one-line explanation + example; the mode
  question explains vibe/mvp/production (meaning, speed, what each runs); defaults are shown.
- **Acceptance**:
  1. **Given** the mode prompt, **then** it explains all three modes with a hint and a default.
  2. **Given** the goal/description/stack prompts, **then** each shows meaning + an example; Enter
     accepts the default; nothing blocks (non-interactive `--yes` uses defaults).

### Story 3 — Pre-bootstrap resolution layer (priority: P2)
- **Independent test**: a read-only stage produces `.aspis/current/bootstrap_state.json` with
  detected runtimes + usability, subscription/model availability, project state, stack + confidence,
  and rule-layer summary — making **zero** side-effecting changes.
- **Acceptance**:
  1. **Given** a project, **when** pre-bootstrap runs, **then** it writes the decision state and
     classifies the project state correctly (empty/initialized/bootstrapped/legacy/incomplete/existing).
  2. **Given** no usable runtime/model (blocked policy), **then** the system stops and tells the
     user what to install/open — it never silently proceeds on a broken/free-bad setup.

### Story 4 — Bootstrap agent asks, never self-decides (priority: P2)
- **Independent test**: the bootstrap agent body requires confirming stack + mode with the user
  and forbids self-deciding; it may delegate stack research to research-lead; project-lead confirms.
- **Acceptance**:
  1. **Given** a detected/guessed stack, **then** the agent asks the user to confirm/override
     before it is written — even with a high-confidence guess, even on a weak/free model.
  2. **Given** the user asks for "latest/best stack", **then** the agent uses research-lead and
     still confirms the result with the user before writing it.

### Story 5 — Plan-file awareness (priority: P2)
- **Independent test**: a plan file at the known location is detected; the agent reads it to inform
  stack/description/patterns; absence is handled gracefully (offer to add one).
- **Acceptance**:
  1. **Given** a plan file present, **then** pre-bootstrap flags it and the bootstrap agent reads
     it to enrich (still confirming with the user).

### Story 6 — Post-bootstrap deterministic self-heal (priority: P1)
- **Why P1**: the guarantee that the project always ends correct, regardless of agent/model/network.
- **Independent test**: simulate the agent NOT enriching; the post-stage deterministically fills
  context files, FILE_REGISTRY, build history, `.gitignore` from stack, and stack→context+manifest.
- **Acceptance**:
  1. **Given** a bootstrap where the agent failed to enrich (weak/offline/error), **when** the
     post-stage runs, **then** the brain is non-skeleton and all expected files are present/filled
     by scripts (deterministic restore of expected files only — no invented content).

### Story 7 — State machine, recovery & resume (priority: P2)
- **Acceptance**:
  1. **Given** an existing `.aspis` project (or existing user code), **when** init/upgrade runs,
     **then** it never destroys the brain or user code; it recovers/upgrades safely.
  2. **Given** an interrupted onboarding/bootstrap, **when** re-run, **then** it resumes from
     `bootstrap_state.json` rather than restarting; onboarding is skippable and never re-asked once done.

### Story 8 — Runtime continuation & multi-runtime (priority: P3)
- **Acceptance**:
  1. **Given** detected runtimes, **then** the user can continue in this CLI or get the **exact
     launch command** to open a runtime (CLI/TUI/GUI), with the correct settings/model set for the
     entry agent first; and can optionally add another runtime via a shown command.

## Requirements
- **FR-001**: `aspis init` MUST remain deterministic, offline, and produce a structurally complete,
  runnable project; it MUST own its first commit and never sweep user code (initialization FIXED).
- **FR-002**: After init, the CLI MUST present a clear decision screen (continue / skip / open
  runtime / stop) and, on continue, run pre-bootstrap → onboarding → bootstrap → post-heal as
  automatic internal stages — the user MUST NOT need to run `bootstrap`/`models`/`apply` manually.
- **FR-003**: Onboarding MUST explain each question (mode, goal, description, stack, runtime) with a
  one-line meaning + example, show defaults, and never block; `--yes`/flags MUST drive it headless
  (bootstrapping FIXED #2).
- **FR-004**: A **pre-bootstrap** stage MUST gather, read-only, into
  `.aspis/current/bootstrap_state.json`: runtime inventory + usability, subscription/model
  availability, project state (empty/initialized/bootstrapped/legacy/incomplete/existing), stack +
  confidence, and a rule-layer summary. It MUST reuse `detect`/`runtime_inventory`/`settings`, not
  duplicate them, and make no side-effecting writes beyond the state file.
- **FR-005**: The system MUST NOT proceed to bootstrap on a **blocked** setup (no usable
  runtime/model); it MUST stop and tell the user what to install/open. Policy tiers: preferred /
  acceptable-fallback / blocked.
- **FR-006**: The `bootstrap` agent MUST NOT self-decide stack or build mode; it MUST confirm them
  with the user (or via project-lead). `project-lead` MUST delegate to it and never self-run the
  bootstrap (bootstrapping FIXED #3).
- **FR-007**: The bootstrap flow MUST read the system/project/user rule layers (user rules from a
  configurable path if present) and MAY use **research-lead** for stack/pattern research; it MUST
  NOT invent a stack from model cutoff. Project rules seeding MUST go through the rules subsystem;
  later rule changes through governance (R-008).
- **FR-008**: Stack handling MUST be confidence-driven and correctable: auto-confirm on high
  confidence, ask on low, allow manual entry on unknown, accept robust formats (regex), and allow
  later correction via a command / system-lead — not one-shot.
- **FR-009**: A plan file at a known location MUST be detected by pre-bootstrap and readable by the
  bootstrap agent to inform enrichment; absence MUST be handled gracefully.
- **FR-010**: A **post-bootstrap** stage MUST deterministically guarantee the floor when the agent
  did not: fill/refresh context files, FILE_REGISTRY, build history, `.gitignore` from stack, and
  write stack→context+manifest, via the update-all-context generators. It MUST be a deterministic
  restore of **expected** files only — never agent-invented content (bootstrapping FIXED #5/#6).
- **FR-011**: Re-init/upgrade MUST NOT destroy an existing `.aspis` brain or user code; interrupted
  init/onboarding/bootstrap MUST resume from `bootstrap_state.json`; onboarding MUST be skippable
  and never re-asked once complete; the not-yet-bootstrapped state MUST be detectable when a runtime
  is used.
- **FR-012**: Self-erasure of the onboarding package MUST NOT edit catalog-managed agent bodies
  (parity moat) — it strips deployed copies via markers and removes the export-only package
  (bootstrapping FIXED #4); the project MUST end with exactly 5 primaries and zero bootstrap residue.
- **FR-013**: The flow MUST show detected runtimes and the **exact launch command** to continue in a
  chosen runtime (CLI/TUI/GUI), setting the correct settings module + model for the entry agent
  before use; adding another runtime MUST be offered optionally with its command.
- **FR-014**: F-020 MUST NOT change model files or run export/`models --apply`; it only detects/
  recommends and reserves the seam for F-021's resolver (models frozen).

## Feature rules & style
- Catalog-first; author in `src/aspis/data/catalog/` + engine; never hand-edit live runtime/brain.
- Operations stay independent (Before→Core→After); a Workflow layer orchestrates them; deterministic
  work stays outside agents; runtime detection + model resolution stay modular (no hardcoded runtime
  names or model strings — D-002/D-008/D-015/D-016).
- Honor R-001/002/003/005/006/008/010 and the architecture constitution. Prefer adding new files
  over editing many; respect every recorded decision (D-001…D-019).
- The don't-break baseline = the FIXED blocks of `initialization.md` + `bootstrapping.md`.

## Key entities
- **`bootstrap_state.json`** (`.aspis/current/`): the resumable pre-bootstrap decision state.
- **Project state** enum: empty / initialized-not-onboarded / bootstrapped / legacy-ASPIS /
  incomplete-ASPIS / existing-code.
- **Stack record**: value + confidence (high/medium/unknown) + source (detected/researched/user).
- **Runtime inventory**: installed runtimes, usability, subscriptions/model availability, launch command.
- **Onboarding question**: prompt + meaning + example + default + value.

## Success criteria
- **SC-001**: From an empty dir, `aspis init` → guided flow → a **live** project with **one**
  user command and only a few clearly-explained questions.
- **SC-002**: Skipping after init leaves a valid, runnable project; resuming continues, never restarts.
- **SC-003**: With a weak/offline/failed agent, the project still ends non-skeleton (post-heal floor).
- **SC-004**: Stack & mode are never written without user confirmation; no blocked setup proceeds silently.
- **SC-005**: Existing `.aspis`/user code is never destroyed by init/upgrade.
- **SC-006**: Gates green (ruff, pytest, validate-runtime 33/33); no model files changed.

## Assumptions
- Build mode F-020 itself: **production** (auto-escalated).
- Model decision engine + model file changes are F-021; git re-arch is F-022.
- The canonical global user-rules path is configurable now; its fixed location is defined later.

## Clarifications

### Session 2026-06-29
- Q: Bootstrap agent autonomy? → A: it asks/confirms with the user; never self-decides stack/mode;
  may use research-lead; project-lead delegates and confirms.
- Q: Post-bootstrap self-heal vs "no autonomous writes"? → A: self-heal is **deterministic script
  restore of expected files only** (IB-4) — not agent invention; the invariant holds.
- Q: Plan file? → A: detected at a known location; read by the agent to enrich; graceful if absent.
- Q: `import`? → A: dropped as a term; project-learning lives inside pre-bootstrap/bootstrap.

## Open questions
- The exact known location(s) for a dropped **plan file** (repo root? `.aspis/plan/`?).
- The configurable **user-rules path** for this phase (env var? `~/.config/aspis/rules.md`?).
- Onboarding shape: strictly one-question-at-a-time vs a grouped screen (both must stay non-blocking).
