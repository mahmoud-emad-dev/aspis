# F-019 — Architecture Memory · Specification

> Mode: **mvp** — stories + acceptance; lean rigor.

## Goal
Give every ASPIS project a permanent, file-first memory of **architectural intent** —
one living markdown file per subsystem — so any agent or human in any future session
understands *why a subsystem exists, what it owns, what it must never own, how it
integrates, and what it guarantees* by reading one file, never by reconstructing intent
from source code, git history, or lost chats. Purpose: **prevent architectural drift as
the project scales.**

## Problem
As a project grows, no model (or person) can reliably reconstruct design intent from the
codebase alone. Implementation evolves, planning changes, git history grows, chats vanish,
context windows reset. Each new session re-derives the same understanding and risks
silently breaking the original design. ASPIS already has `ARCHITECTURE.md` (as-built
technical shape), `DECISIONS.md` (dated point decisions), planning artifacts (future work),
and `CURRENT_STATE.md` (live status) — but **none of them hold per-subsystem intent**:
the "why / responsibilities / boundaries / guarantees / evolution" of each part. That gap
is what causes drift.

## Scope
In scope:
- New brain location `.aspis/architecture/subsystems/` (one `<name>.md` per subsystem) + `INDEX.md`.
- A catalog template for the subsystem file (`catalog/templates/context/subsystem.md`), scaffolded by `aspis artifact subsystem <name>`.
- A catalog template for the change report (`catalog/templates/report/architecture-impact.md`).
- One new skill `architecture-memory`, owned by `project-lead`, referenced by `planning-lead`.
- Wiring into the planning phase: Impact Analysis (pre-plan), read-before-design, Impact Report on change, user-confirmed update, post-review Architecture Verification — **mode-gated** (full in production, collapsed in mvp, skipped in vibe).
- Mode knobs in `modes.yaml` for the loop.
- The first subsystem file, `architecture-memory.md` (this feature's own intent), as the worked example.
- Registration so no blank-purpose gap (`FILE_REGISTRY`/`purposes.json`).

Out of scope (deliberately NOT done):
- Inventing subsystem files for other subsystems (bootstrapping, models, etc.) — the owner supplies real intent for each, one at a time, in later increments. We do NOT generate them from memory or the codebase.
- Moving/renaming the existing `context/ARCHITECTURE.md` (possible later consolidation, not now).
- Any database, daemon, background service, git/commit-triggered hook, auto-update, drift-scoring engine, required-section CI gate, or new agent.
- Automatic edits to subsystem files — every change requires explicit user confirmation.

## User stories
Prioritized, each independently testable. P1 is the MVP slice.

### Story 1 — A subsystem has one living intent file (priority: P1) 🎯
- **Why this priority**: the durable artifact is the whole point; everything else serves it.
- **Independent test**: `aspis artifact subsystem payments` creates `.aspis/architecture/subsystems/payments.md` with all required sections from the template; `INDEX.md` lists it.
- **Acceptance scenarios**:
  1. **Given** a project, **when** `aspis artifact subsystem <name>` runs, **then** a conformant subsystem file is created with name + Created/Last-reviewed dates stamped and the lean 7-section skeleton.
  2. **Given** the new file, **when** the INDEX refresh runs, **then** the subsystem appears in the INDEX table with status + one-liner + last-reviewed.

### Story 2 — Planning reads intent and proposes changes through a confirmed gate (priority: P2)
- **Why this priority**: this is what keeps the files alive and prevents drift (the anti-rot levers: owner + in-workflow + recorded-artifact + confirm).
- **Independent test**: a production-mode planning run that touches an existing subsystem reads its file, and on a design change emits an `ARCHITECTURE_IMPACT.md`; project-lead asks the user to confirm before any subsystem file is edited.
- **Acceptance scenarios**:
  1. **Given** a feature that changes a subsystem's responsibility/boundary/contract/integration (or adds/removes one), **when** planning runs in production, **then** planning-lead reads the affected subsystem file(s) before designing and writes an `ARCHITECTURE_IMPACT.md` report into the feature folder.
  2. **Given** an Impact Report, **when** project-lead applies it, **then** it presents a Current/Proposed/Reason draft and updates the subsystem file **only after explicit user confirmation**, appending a dated changelog line.
  3. **Given** vibe mode, **when** a feature runs, **then** no Impact Analysis/Report/confirmation loop fires and nothing blocks — subsystem files are read-only orientation context.

### Story 3 — Built work is reconciled against approved intent (priority: P3)
- **Why this priority**: closes the loop; catches drift between what was approved and what shipped.
- **Independent test**: after review, project-lead compares approved intent vs the change and surfaces any divergence with a fix-or-update question.
- **Acceptance scenarios**:
  1. **Given** an implemented + reviewed change with an approved Impact Report, **when** project-lead runs Architecture Verification (production), **then** any divergence from approved intent is surfaced with "correct the implementation, or update Architecture Memory?" — never silently accepted.

## Requirements
- **FR-001**: The system MUST store subsystem intent as one markdown file per subsystem under `.aspis/architecture/subsystems/`, file-first, no external store.
- **FR-002**: The subsystem file MUST follow a lean, fixed format: Identity (status/dates/one-liner), Why it exists, Responsibilities & boundaries, Current behaviour (FIXED vs OPEN), Integrations, System contracts, optional Future direction, append-only Changelog.
- **FR-003**: `aspis artifact subsystem <name>` MUST scaffold a conformant file with deterministic fields stamped (name + dates), consistent with D-013.
- **FR-004**: Subsystem files MUST only be updated for **architectural** change (intent/responsibility/boundary/contract/integration, or add/remove). Bug fixes, refactors, renames, formatting, and perf work MUST NOT update them.
- **FR-005**: Every architectural change MUST append a dated changelog line (and edit the affected section); history is never rewritten — supersede instead.
- **FR-006**: Subsystem files MUST NEVER be updated automatically; an update requires explicit user confirmation of a Current/Proposed/Reason draft.
- **FR-007**: The governance loop (Impact Analysis → read → Impact Report → confirm → Verification) MUST be owned by `project-lead` via the `architecture-memory` skill; `planning-lead` is the detector/consumer. No new agent.
- **FR-008**: The loop MUST be mode-gated: full in `production`, collapsed (single yes/no; report+confirm only on yes; light verification) in `mvp`, skipped in `vibe`. It MUST NEVER block, slow, or hang a normal/light-mode user.
- **FR-009**: The trigger MUST be the planning phase, never git changes, commits, or file modifications.
- **FR-010**: The new brain location MUST be registered so every file has a non-blank purpose (no `build_registry --check` gap).

## Feature rules & style
- Catalog-first: author in `src/aspis/data/catalog/` + engine; never hand-edit live `.opencode/`/`.claude/`/`.aspis/` (D-003/D-005). Live dirs are regenerated.
- Honor R-001 (scope), R-002 (deterministic gates), R-005 (tests-as-spec), R-006 (thin instruction + skill), R-008 (human gate for rules/architecture).
- Owner's standing principle: lean, no over-engineering, never block/slow/hang normal use; `modes.yaml` is the rigor dial.
- Grounded in proven patterns: Memory Bank (read-first context), arc42 Building Block View (one file per part), ADR (timestamped log). Anti-rot levers: named owner, docs-as-code in-repo, recorded-artifact-on-change, in-workflow — ASPIS already has file-first in-repo.

## Key entities
- **Subsystem file** (`.aspis/architecture/subsystems/<name>.md`): the living intent of one subsystem.
- **INDEX.md**: table of subsystems — name · status · one-liner · last-reviewed.
- **ARCHITECTURE_IMPACT.md** (per feature): recorded proposal of an architectural change — affected subsystem(s), reason, summary, integration impact, questions needing confirmation.
- **`architecture-memory` skill**: the "how" — when to read, how to detect a change, how to write the report, how to confirm, how to apply the dated update, how to verify post-build.

## Success criteria
- **SC-001**: `aspis artifact subsystem X` produces a conformant file listed in INDEX.
- **SC-002**: A production planning run touching a subsystem reads its file and emits an Impact Report on a design change; no subsystem file changes without explicit user confirmation.
- **SC-003**: A vibe-mode feature completes with zero Architecture-Memory overhead and no blocking.
- **SC-004**: Post-review verification surfaces any divergence between approved intent and the built change.
- **SC-005**: All new files have a registered purpose; gates (ruff, pytest, validate-runtime) stay green.

## Assumptions
- The folder is a top-level brain location `.aspis/architecture/` (per owner's latest instruction), distinct from `context/ARCHITECTURE.md`, which is left in place.
- mvp mode is the build mode for F-019 itself.
- Only ONE subsystem file is created now (`architecture-memory.md`); all others are authored later from the owner's real per-subsystem intent.

## Clarifications

### Session 2026-06-29
- Q: Where does the subsystems folder live? → A: top-level `.aspis/architecture/subsystems/` (owner instruction), not nested under `context/`.
- Q: Which subsystem files do we seed now? → A: only this feature's own (`architecture-memory.md`); never invent others from memory or codebase — owner supplies each one's real intent later.
- Q: Mode-gating of the loop? → A: full/production, collapsed/mvp, skipped/vibe (owner confirmed "mode-gated as designed").

## Open questions
- Final word "architecture" vs owner's shorthand "arch" for the folder — using full word `architecture`; revert if owner prefers `arch`.
