# F-015 — Safe Catalog Export · Specification

> Mode: **production** — full spec, full architecture, small tasks, independent review.

## Goal

Let users safely re-apply catalog updates to an ASPIS project without overwriting
files they have hand-customized since the last export.

## Problem

The current `write_export` has exactly one guard: "if file exists AND not `--force`
→ skip". There is no content hashing, no way to detect user customizations, and no
way to safely re-apply catalog changes without destroying hand-tuned live files.
`aspis models --apply` hard-codes `force=True`, blindly overwriting every live
agent file — even ones the user edited.

## Scope

In scope:
- `.aspis/current/export-snapshot.json` — hash snapshot of what was last written
- `.aspis/current/export-log.jsonl` — append-only audit log of every export decision
- Runtime hook outputs (emit_runtime_hooks) are protected by the same decide
  flow as catalog actions.
- Hash-based classification of every export target into 6 categories
- `--apply` flag: write only safe files (NEW + CATALOG-CHANGED)
- `--scope` flag: limit export to a single project-relative path
- `--strict` flag: fail on conflicts (non-zero exit)
- `--force-conflicts` flag: with `--apply`, also overwrite CONFLICT files
- `models --apply` uses safe classification instead of blind force
- Integration into `write_export` (new parameters, classification loop)
- Backward compatibility: no-flag `aspis init --write` behaves identically

Out of scope:
- Staging directory (two-phase write-then-commit flow)
- Clobber classification (differentiating semantic from cosmetic diffs)
- Accept/rebaseline API (user edits catalog source, not lock file)
- Trace events or self-validation (separate concern)
- Per-runtime lock files (one snapshot covers all runtimes)
- Orphan detection or dead lock pruning
- Directory-level hashing (directories use legacy skip-if-exists logic)
- Snapshot-aware `--force` (force still writes everything; snapshot records it)

## User stories

### Story 1 — Safe re-apply after catalog update (priority: P1)
- **Why this priority**: This is the core value — the reason the feature exists.
- **Independent test**: Run `aspis init --write`, edit a skill file by hand, update
  the catalog's version of a different skill, run `aspis init --write --apply`.
  Verify: hand-edited file is untouched (LIVE-CUSTOMIZED → skipped), catalog-changed
  file is updated (CATALOG-CHANGED → written).
- **Acceptance scenarios**:
  1. **Given** a project initialized with `aspis init --write`, **when** the user
     edits `.opencode/skills/planning-intake/SKILL.md` and the catalog ships a new
     version of `.opencode/skills/feature-planning/SKILL.md`, **then**
     `aspis init --write --apply` updates the feature-planning skill, skips the
     planning-intake skill, and logs both decisions.
  2. **Given** a fresh directory with no snapshot, **when** `aspis init --write`
     runs, **then** all new files are written and a snapshot is created recording
     every written file's hash.

### Story 2 — Conflict detection and reporting (priority: P2)
- **Why this priority**: Users need to know when their edits collide with catalog
  changes — even if they choose not to apply.
- **Independent test**: Init a project, edit a file, change the catalog version of
  the same file, run `aspis init --write` (no `--apply`). Verify: the conflict is
  detected and logged, but the file is NOT overwritten.
- **Acceptance scenarios**:
  1. **Given** a project where the user edited `.opencode/agents/project-lead.md`
     AND the catalog version of that agent also changed, **when**
     `aspis init --write --apply` runs, **then** the file is skipped, the category
     "CONFLICT" is logged, and the user is told how to resolve it.
  2. **Given** the same scenario, **when** `aspis init --write --apply --force-conflicts`
     runs, **then** the file is overwritten with the catalog version (user's
     customization lost, catalog wins).

### Story 3 — Single-file scope application (priority: P2)
- **Why this priority**: Enables surgical updates — the user knows exactly which
  file changed and wants to apply just that one.
- **Independent test**: Init a project, edit two files. Run
  `aspis init --write --apply --scope .opencode/agents/project-lead.md`. Verify:
  only the scoped file is classified and potentially written; the other edited
  file is not touched.
- **Acceptance scenarios**:
  1. **Given** a project with multiple changed files, **when**
     `aspis init --write --apply --scope .opencode/skills/x/SKILL.md` runs,
     **then** only that one file is considered; its category determines write/skip.
  2. **Given** a scope path that matches no export action, **when** the command
     runs, **then** a clear "no asset matches scope" message is shown.

### Story 4 — CI-safe strict mode (priority: P3)
- **Why this priority**: Enables automation — a CI pipeline can run `aspis init
  --apply --strict` and fail if there are unresolved conflicts.
- **Independent test**: Create a conflict scenario, run `aspis init --write --apply
  --strict`. Verify exit code is non-zero and the conflict is in the output.
- **Acceptance scenarios**:
  1. **Given** a project with a CONFLICT file, **when** `aspis init --write --apply
     --strict` runs, **then** the command exits with code 1 and reports the conflict.
  2. **Given** a clean project (all IDENTICAL), **when** `aspis init --write --apply
     --strict` runs, **then** the command exits 0.

### Story 5 — Protected model application (priority: P2)
- **Why this priority**: `models --apply` is a commonly-used workflow; its blind
  force is the problem this feature was created to fix.
- **Independent test**: Init a project, hand-edit an agent file, change a model
  assignment in `agent-models.yaml`, run `aspis models --apply`. Verify: the
  hand-edited agent is skipped (LIVE-CUSTOMIZED), other agents whose model routing
  changed are re-rendered (CATALOG-CHANGED).
- **Acceptance scenarios**:
  1. **Given** a project where the user customized an agent's instruction text,
     **when** `aspis models --apply` runs after a model routing change, **then**
     the customized agent is skipped, not overwritten.
  2. **Given** a project where no agent files were hand-edited, **when**
     `aspis models --apply` runs after a model routing change, **then** all live
     agent files are re-rendered with the new model (same effective behavior as
     the old `force=True` for untouched files).

## Requirements

- **FR-001**: The system MUST compute a SHA-256 hash of every file's post-render
  content before deciding whether to write it.
- **FR-002**: The system MUST persist a snapshot (`export-snapshot.json`) mapping
  every written file's project-relative path to its hash.
- **FR-003**: The system MUST classify every export target into exactly one of
  six categories: ADD, UNCHANGED, UNKNOWN, UPDATE, PROTECT, CONFLICT.
- **FR-004**: The system MUST decide write-or-skip per file based on its category
  and the active flags (`--force`, `--apply`, `--force-conflicts`).
- **FR-005**: The system MUST append an audit entry to `export-log.jsonl` for every
  `write_export` invocation that performs writes.
- **FR-006**: The `--apply` flag MUST write NEW and CATALOG-CHANGED files, and
  MUST skip LIVE-CUSTOMIZED and CONFLICT files.
- **FR-007**: The `--force` flag MUST write every file regardless of category
  (backward-compatible legacy behavior).
- **FR-008**: The `--force-conflicts` flag, when combined with `--apply`, MUST
  also write CONFLICT files while still skipping LIVE-CUSTOMIZED files.
- **FR-009**: The `--scope` flag MUST limit all export decisions to actions whose
  target path starts with the given prefix.
- **FR-010**: The `--strict` flag MUST cause a non-zero exit code when any file
  is classified as CONFLICT or LIVE-CUSTOMIZED during an `--apply` run.
- **FR-011**: The snapshot MUST be atomically written (temp file + rename) to
  prevent corruption on partial writes.
- **FR-012**: When `--scope` is used, the snapshot MUST be partially updated
  (only the scoped file's entry changes; all other entries are preserved).
- **FR-013**: `aspis models --apply` MUST use `apply=True` semantics instead of
  `force=True`, so hand-customized agent files are protected.
- **FR-014**: Without `--apply`, `--force`, or `--force-conflicts`, the behavior
  MUST be identical to the current "skip if exists" rule (backward compatible).
- **FR-015**: The classification mechanism MUST NOT name-check any runtime, asset
  kind, or profile — it operates purely on hashes and paths.

## Feature rules & style

- **Constitution #1 (Local Change)**: New protection logic lives in
  `src/aspis/protect.py`; existing files change only at integration points.
- **Constitution #2 (Plugin First)**: No `if runtime == "opencode"` anywhere.
- **Constitution #3 (Single Source of Truth)**: Catalog is the source; snapshot is
  the record of what was written from it.
- **Constitution #8 (Generated Artifacts)**: Snapshot and audit log are generated,
  never hand-edited. They ship under `.aspis/current/`.
- **Constitution #9 (No Special Cases)**: No `if kind == "agents"` or
  `if scope == "something"`.
- **R-003 (Automation before Intelligence)**: Hash comparison is a deterministic
  function, not an agent decision.

## Key entities

- **ExportSnapshot** (`export-snapshot.json`): Maps project-relative paths to
  SHA-256 hashes of the content as last written. Versioned. One per project.
- **ExportAuditEntry**: A record of one `write_export` invocation — timestamp,
  flags, every file's category and decision, and a summary count. Appended to
  `export-log.jsonl`.
- **Category**: One of `NEW`, `IDENTICAL`, `CATALOG_CHANGED`, `LIVE_CUSTOMIZED`,
  `CONFLICT` — the result of comparing three hashes (disk, snapshot, catalog).

## Success criteria

- **SC-001**: A user who hand-edits an exported file can run `aspis init --write
  --apply` and their edit is not overwritten.
- **SC-002**: A user who has NOT edited any exported files can run `aspis init
  --write --apply` and receive all catalog updates (same net effect as `--force`
  for untouched files).
- **SC-003**: Running `aspis init --write` (no new flags) produces byte-identical
  behavior to the current version (except the snapshot file is also written).
- **SC-004**: A CI pipeline can run `aspis init --apply --strict` and get a
  non-zero exit when conflicts exist.
- **SC-005**: Every write-or-skip decision is traceable via the audit log.

## Assumptions

- Directories exported via `shutil.copytree` are rare in practice and can use
  legacy skip-if-exists logic (no hash-based decisions for directories).
- The snapshot is always writable under `.aspis/current/` (created by init's
  `_scaffold_brain`).
- `--apply` implies `--write` (passing `--apply` without `--write` is equivalent
  to passing both).
- The `--scope` path format is exactly the project-relative target path as
  produced by `assetkinds.target()`.

## Clarifications

### Session 2026-06-24
- Q: Should `--apply` imply `--write`? → A: Yes. `--apply` without `--write` is
  meaningless; `--apply` overrides `write=False`.
- Q: Should `--force` override `--apply`? → A: Yes. If both are passed, `force`
  wins (writes everything, including LIVE-CUSTOMIZED and CONFLICT).
- Q: Should the snapshot record files that were skipped? → A: No. The snapshot
  only records what was actually written — except UNKNOWN targets, whose live
  hash is recorded so a future run can reclassify them. The audit log records
  everything.
- Q: Should `models --apply` change behavior? → A: Yes — this is the feature's
  explicit goal. The old `force=True` is the problem statement.
