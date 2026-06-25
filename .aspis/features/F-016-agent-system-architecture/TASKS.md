# F-016 — Tasks

Format: `- [ ] T-NN [P?] [US?] <description> (<exact file path>)`
- `T-NN` — sequential task id, in execution order.
- `[P]` — optional: parallelizable (different files, no dependency).
- `[US?]` — optional: the user story this serves (US1, US2 …), for traceability.
- Always name the exact file path(s) in backticks; `task-compile` reads them.

> Mode hints: **vibe** → a short flat list, large tasks. **mvp** → phases, medium
> tasks. **production** → phases + tests-first per story, small tasks.

## Phase 1 — Setup
Shared scaffolding everything else needs. Blocked by: nothing.
- [ ] T-01 [P] <project/dir/config setup> in `<path>`.

**Checkpoint**: foundation initialised.

## Phase 2 — Foundational (blocking)
Core infrastructure ALL stories depend on — no story work until this completes.
- [ ] T-02 <core change others depend on> in `<path>`.

**Checkpoint**: foundation ready.

## Phase 3 — User Story 1 — <title> (priority: P1) 🎯 MVP
**Goal**: <what this story delivers.>
**Independent test**: <how to verify it alone.>

Tests first (write failing, then implement):
- [ ] T-03 [P] [US1] <test for the story behaviour> in `<tests/path>`.

Implementation:
- [ ] T-04 [US1] <change> in `<path>` (depends on T-03).

**Checkpoint**: User Story 1 works independently.

## Phase N — Polish
Cross-cutting cleanup once stories land.
- [ ] T-NN <docs / final gate sweep>.

## Dependencies & execution order
- Setup → Foundational → User Stories (parallel once foundational is done) → Polish.
- Within a story: tests before implementation; models before services before wiring.
- Tasks marked `[P]` within a phase can run in parallel (different files).

## Implementation strategy
- **MVP first**: complete Setup + Foundational + User Story 1, then stop and validate.
- **Incremental**: add each next story, test independently, before moving on.

## Build packets
`task-compile` turns each task above into a self-contained packet at
`.aspis/features/<feature-id>/tasks/T-NN.md` from `.aspis/templates/TASK_PACKET.md`,
so a context-isolated builder can complete it with nothing else.
