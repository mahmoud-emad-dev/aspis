# F-015: Safe Catalog Export — Build Tasks

**Feature:** F-015 — Exporter Hardening
**Mode:** Production
**Review level:** LIGHT — build-lead self-reviews against constitution checklist
**Task size:** MEDIUM (4 units, 2–3 plan steps each)

---

## Execution strategy

1. **Sequential within units, units are sequential** (each depends on prior).
2. **Every unit produces a passing test suite** before the next begins.
3. **Self-review:** after each unit, the build-lead runs the constitution checklist
   (Cost-of-Change ≤ 3 files, no special cases, pure functions where deterministic).
4. **Merge-ready after Unit 4:** all gates green, acceptance scenarios passing.

---

## Unit 1 — Pure protection engine (`src/aspis/protect.py`)

**Plan steps:** Step 1

**Files to create:**
- `src/aspis/protect.py` — DecisionKind enum, Decision dataclass, `sha256_text()`,
  `decide()`, `plan_runtime()`, `summary()`
- `tests/test_protect.py` — 16+ tests

**Files to modify:**
- *(none — all new files)*

**Objective:** Implement the pure 6-way hash-based decision engine. Zero file I/O,
zero ASPIS imports, zero runtime awareness. The module is self-contained and
testable in isolation. Includes UTF-8 BOM stripping in `sha256_text()` and a
separate `sha256_bytes()` function for binary files.

**Key acceptance:**
- [ ] `sha256_text()` produces correct SHA-256 hex digest, normalizes CRLF→LF
- [ ] `decide()` correctly resolves all 6 cases of the truth table (ADD, UNCHANGED,
  UNKNOWN, UPDATE, PROTECT, CONFLICT) from the 3-input hash matrix
- [ ] `plan_runtime()` fans out `decide()` across a union of keys
- [ ] `summary()` aggregates counts by DecisionKind
- [ ] All edge cases: None hashes, empty strings, pure-crlf strings, all-three-None

**Gate:** `pytest tests/test_protect.py -x -q` — 100% branch coverage on `decide()` and `sha256_text()`

**Depends on:** nothing

---

## Unit 2 — Snapshot engine + rewired `write_export`

**Plan steps:** Step 2 + Step 3

**Files to modify:**
- `src/aspis/export.py` — add `ProtectionError`, `_load_snapshot`, `_save_snapshot`,
  `_append_log`, `_hash_file`, `_regen_hash`; extend `write_export` signature and
  replace skip-if-exists with the decide flow

**Files to create:**
- `tests/test_export_snapshot.py` — 8 tests
- `tests/test_export_protection.py` — 12 tests

**Objective:** Add snapshot/log persistence helpers. Rewire `write_export` to compute
hashes per action, call `protect.decide()`, and dispatch write/skip per DecisionKind.
`--force` bypasses the loop entirely (backward-compatible). `--apply` writes NEW and
UPDATE files, skips PROTECT and CONFLICT. The audit log uses JSONL format (one
JSON object per line, true append-only). A lockfile mechanism guards against
concurrent runs. The snapshot is written atomically using
`tempfile.mkstemp` + `os.replace`, with `path.parent.mkdir(parents=True,
exist_ok=True)` called first. Runtime hook outputs (`emit_runtime_hooks`) are
tracked in the snapshot and protected by the same decide flow.

**Key acceptance:**
- [ ] Snapshot loads/saves atomically (tempfile + `os.replace`); corruption raises
  clear error unless `reset_snapshot`
- [ ] First export: all files written as ADD, snapshot records every hash
- [ ] Second export (unchanged): all UNCHANGED, no writes
- [ ] User edits a file → re-export skips it (PROTECT)
- [ ] Catalog updates a file → re-export writes it (UPDATE)
- [ ] Both user and catalog change → re-export skips (CONFLICT)
- [ ] `--force` overwrites everything regardless of category
- [ ] `--force-conflicts` overwrites CONFLICT files but still skips PROTECT
- [ ] `--strict` raises `ProtectionError` on CONFLICT during `--apply`
- [ ] `--scope` filters actions by catalog source path prefix
- [ ] `--apply` implies `--write`; `--force` overrides `--apply`
- [ ] Audit log appends an entry per file per `write_export` invocation

**Gate:** `pytest tests/test_export_snapshot.py tests/test_export_protection.py -x -q`

**Depends on:** Unit 1

---

## Unit 3 — Models bug fix + init CLI flags

**Plan steps:** Step 4 + Step 5

**Files to modify:**
- `src/aspis/commands/models.py` — line 230: `force=True` → `apply=True`; add
  `--force` flag to `aspis models --apply` as escape hatch
- `src/aspis/commands/init.py` — add `--dry-run`, `--apply`, `--strict`, `--scope`,
  `--force-conflicts`, `--reset-snapshot` flags to `register()` and pass through in
  `_run()`
- `src/aspis/operations/init.py` — read new flags from `ctx.options` and forward
  to `write_export()`

**Files to create:**
- `tests/test_models_command.py` — 3 tests (if new; otherwise extend existing)
- `tests/test_init_cli.py` — 6 tests (extend existing)

**Objective:** Fix the `models --apply` blind-force bug so hand-edited agent files are
protected. Add the 6 new CLI flags to `aspis init` and wire them through to
`write_export`. Flag interaction validation rejects contradictory combinations.

**Key acceptance:**
- [ ] `models --apply` with catalog-changed agent → UPDATE (agent re-rendered)
- [ ] `models --apply` with user-edited agent → PROTECT (agent skipped)
- [ ] `models --apply` with both-changed agent → CONFLICT (reported, not overwritten)
- [ ] `aspis init --write --apply` writes NEW + UPDATE, skips PROTECT + CONFLICT
- [ ] `aspis init --write --apply --strict` exits non-zero on CONFLICT
- [ ] `aspis init --write --scope=path` limits to matching actions
- [ ] `aspis init --write --reset-snapshot` recovers from corrupt snapshot
- [ ] `aspis init --dry-run` shows decision table without writing
- [ ] Invalid flag combos (`--force-conflicts --strict`) are rejected with clear error

**Gate:** `pytest tests/test_commands_models.py tests/test_commands_init.py -x -q`

**Depends on:** Unit 2

---

## Unit 4 — Brain gitignore + end-to-end acceptance

**Plan steps:** Step 6 + Step 7

**Files to modify:**
- `src/aspis/data/catalog/scaffold/brain.gitignore` — add `current/export-snapshot.json`
  and `current/export-log.json`

**Files to create:**
- `tests/test_brain_gitignore.py` — verify scaffold includes export entries
- `tests/test_f015_e2e.py` — 6 acceptance tests

**Objective:** Ensure generated brain `.gitignore` ignores the export snapshot and log
files. Validate the full feature with end-to-end acceptance tests covering all 5 user
stories.

**Key acceptance:**
- [ ] Generated `.aspis/.gitignore` contains `current/export-snapshot.json` and
  `current/export-log.json`
- [ ] **E2E Story 1:** Init → user-edit skill A → catalog-update skill B →
  re-apply: skill A PROTECTED, skill B UPDATED
- [ ] **E2E Story 2:** Init → user-edit agent X → catalog-change agent X →
  re-apply: CONFLICT detected, file not overwritten; `--force-conflicts` overwrites it
- [ ] **E2E Story 3:** `--scope` limits to a single file; other files untouched
- [ ] **E2E Story 4:** Conflict scenario + `--strict` → non-zero exit
- [ ] **E2E Story 5:** `models --apply` protects user-edited agents after model
  routing change
- [ ] **E2E:** Corrupted snapshot + `--reset-snapshot` → recovery; export proceeds

**Gate:** `pytest tests/test_brain_gitignore.py tests/test_f015_e2e.py -x -q`

**Depends on:** Units 1, 2, 3

---

## Verification checklist (build-lead self-review)

After each unit, confirm:

| # | Rule | Check |
|---|---|---|
| 1 | **Local Change** | 4 existing product files changed total (export.py, init.py, models.py, operations/init.py) — within warning range |
| 2 | **No Special Cases** | No `if kind == "agents"` or `if runtime == "claude"` in new code |
| 3 | **Automation before Intelligence** | `decide()` and `sha256_text()` are pure deterministic functions |
| 4 | **Core is Stable** | `plan_export()` and `_apply()` unchanged |
| 5 | **Dependency Direction** | `protect.py` imports zero ASPIS modules; `export.py` imports `protect` |
| 6 | **Portable by Default** | CRLF→LF normalization, posix paths in snapshot, `os.replace` (cross-platform) |
| 7 | **Single Source of Truth** | Catalog = source; snapshot = record; decide = hash comparison only |
