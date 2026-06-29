# F-019 — Tasks

Format: `- [ ] T-NN [P?] [US?] <description> (<exact file path>)`

> Mode: **mvp** — phases, medium tasks.

## Phase 1 — Setup
Shared scaffolding everything else needs. Blocked by: nothing.
- [x] T-01 Create branch + feature folder + brain dir `.aspis/architecture/subsystems/` (this commit).
- [ ] T-02 Register `.aspis/architecture/` as a brain location + purposes so no blank-purpose gap in `purposes.json` / FILE_REGISTRY config.

**Checkpoint**: location exists and is registered.

## Phase 2 — Foundational (blocking)
Templates + the artifact kind ALL stories depend on.
- [ ] T-03 [P] [US1] Subsystem file template (lean 7-section) in `src/aspis/data/catalog/templates/context/subsystem.md`.
- [ ] T-04 [P] [US2] Impact report template in `src/aspis/data/catalog/templates/report/architecture-impact.md`.
- [ ] T-05 [US1] Register `subsystem` artifact kind → target `.aspis/architecture/subsystems/<name>.md`, stamp name+dates (artifact/assetkinds engine + `catalog/config/base.yaml`).

**Checkpoint**: `aspis artifact subsystem X` produces a conformant file.

## Phase 3 — User Story 1 — one living intent file (priority: P1) 🎯 MVP
**Goal**: a subsystem owns one conformant, indexed file.
**Independent test**: `aspis artifact subsystem payments` → conformant file; INDEX lists it.

Tests first:
- [ ] T-06 [P] [US1] Test: artifact creates conformant file (required sections, stamped fields) in `tests/test_artifact_subsystem.py`.
- [ ] T-07 [P] [US1] Test: INDEX refresh lists a created subsystem in `tests/test_subsystem_index.py`.

Implementation:
- [ ] T-08 [US1] INDEX refresh by extending an existing context script (catalog source under `scripts/context/`).
- [ ] T-09 [US1] Seed the first subsystem file (this feature's own) `.aspis/architecture/subsystems/architecture-memory.md` + `INDEX.md` (done in T-01 commit; verify conformant).

**Checkpoint**: Story 1 works independently.

## Phase 4 — User Story 2 — planning reads intent + confirmed-update gate (priority: P2)
**Goal**: planning reads subsystem files and proposes changes through a user-confirmed gate.
**Independent test**: production planning touching a subsystem reads it, emits `ARCHITECTURE_IMPACT.md`, project-lead confirms before edit.

- [ ] T-10 [US2] Skill `architecture-memory` (read/detect/report/confirm/apply/verify) in `src/aspis/data/catalog/skills/architecture-memory/SKILL.md`.
- [ ] T-11 [US2] Wire owner + consumer: `catalog/agents/project-lead.md` (skill + steps [A][D][E]), `catalog/agents/planning-lead.md` (steps [B][C]); planning workflow steps.
- [ ] T-12 [US2] Mode-gate the loop in `catalog/config/modes.yaml` (production full / mvp collapsed / vibe skipped).
- [ ] T-13 [P] [US2] Test: vibe mode runs a feature with no loop / no block in `tests/test_arch_memory_modes.py`.

**Checkpoint**: Story 2 works; nothing blocks light modes.

## Phase 5 — User Story 3 — verification against approved intent (priority: P3)
- [ ] T-14 [US3] Architecture Verification step [E] in the `architecture-memory` skill + project-lead post-review wiring.

**Checkpoint**: divergence is surfaced, never silently accepted.

## Phase 6 — Polish
- [ ] T-15 Full gate sweep: `ruff format --check` + `ruff check` + `pytest` + `validate-runtime --runtime all` (33/33) + `build_registry --check`.
- [ ] T-16 Update `.aspis/context/DECISIONS.md` (new D-### for Architecture Memory) + ROADMAP; refresh brain indexes.

## Dependencies & execution order
- Setup → Foundational → US1 → US2 → US3 → Polish.
- Within a story: tests before implementation.
- `[P]` tasks in a phase touch different files and can run in parallel.

## Implementation strategy
- **MVP first**: Setup + Foundational + US1 (the durable artifact + scaffolder), then validate and pause for owner review.
- **Incremental**: add US2 (the live loop), then US3 (verification).

## Build packets
`task-compile` turns each task into a packet at `.aspis/features/F-019-architecture-memory/tasks/T-NN.md` when we reach build.
