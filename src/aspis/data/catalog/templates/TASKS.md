# <feature-id> — Tasks

Format: `- [ ] T-NN [P?] <description> (<exact file path>)`
- `T-NN` — sequential task id, in execution order.
- `[P]` — optional: parallelizable (different files, no dependency).

## Tasks

### Phase 1 — Foundation
Blocked by: nothing.
- [ ] T-01 [P] <setup / core change> in `<path>`.
- [ ] T-02 <core change others depend on> in `<path>`.

### Phase 2 — <slice title>
Blocked by: Phase 1.
- [ ] T-03 [P] <change> in `<path>`.
- [ ] T-04 <change> in `<path>`.

### Phase 3 — Polish
- [ ] T-05 <docs / final gate sweep>.

## Dependencies & parallelism
- Phase 2 depends on Phase 1; Phase 3 depends on Phase 2.
- Tasks marked `[P]` within a phase can run in parallel.

## Build packets
Promote any task that needs its own self-contained context to a packet using
`.asps/templates/TASK_PACKET.md` at `.asps/features/<feature-id>/build/T-NN.md`.
