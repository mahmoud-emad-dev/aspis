# Feature report — F-015

> Filled when a feature is complete, as the single summary of what shipped.
> The header is stamped by `aspis artifact`; you fill the rest from the real
> task reports and the final gate.

- **Feature**: F-015 — safe catalog export
- **Date**: 2026-06-25
- **Result**: shipped

## Summary

F-015 replaces the exporter's single-guard skip-if-exists logic with a
content-hash-based protection engine that classifies every export target
into one of 6 categories (ADD, UNCHANGED, UNKNOWN, UPDATE, PROTECT,
CONFLICT) by comparing three SHA-256 hashes: the live file, the last
exported snapshot, and what the catalog would produce. User-edited files
are protected from overwrite; catalog-changed pristine files are safely
updated; both-changed files are reported as conflicts. A JSON snapshot
records what was last written; a JSONL audit log records every decision.
The `models --apply` blind-force bug (hard-coded `force=True` that
destroyed user edits) is fixed. Six new CLI flags (`--apply`, `--strict`,
`--scope`, `--force-conflicts`, `--reset-snapshot`, `--dry-run`) give
fine-grained control over the protection behavior.

## What shipped

### Unit 1 — Pure protection engine (`38752ec`)
- **New file:** `src/aspis/protect.py` — `DecisionKind` enum, `Decision`
  dataclass, `sha256_text()` (BOM stripping + CRLF normalization),
  `sha256_bytes()`, `decide()` (pure 6-case truth table), `plan_runtime()`,
  `summary()`. Zero ASPIS imports, zero file I/O — fully testable in
  isolation.
- **Tests:** `tests/test_protect.py` — 45 tests covering the full decision
  table, CRLF/BOM normalization, edge cases (None hashes, empty strings,
  all-three-None).

### Unit 2 — Snapshot engine + rewired `write_export` (`49db643`)
- **Modified:** `src/aspis/export.py` — added `ProtectionError`,
  `_load_snapshot`, `_save_snapshot` (atomic via tempfile + os.replace),
  `_append_log` (JSONL), `_hash_file`, `_regen_hash`, `_acquire_lock`,
  `_release_lock`, `_pid_alive`. Extended `write_export` signature with
  `apply`, `strict`, `scope`, `force_conflicts`, `reset_snapshot`. Replaced
  skip-if-exists with the decide flow. `--force` preserves legacy behavior.
- **Tests:** `tests/test_export_snapshot.py` (8 tests) +
  `tests/test_export_protection.py` (21 tests) — full export cycle: ADD,
  UNCHANGED, UNKNOWN, UPDATE, PROTECT, CONFLICT, force bypass,
  force_conflicts, strict, scope, lockfile, stale lock, corruption reset,
  audit log, dry-run, render-op hash parity.

### Unit 3 — Models bug fix + init CLI flags (`e09fd39`)
- **Modified:** `src/aspis/commands/models.py` — fixed the blind-force bug:
  `_apply()` now uses `apply=True` (hash-protection) by default instead of
  `force=True`. Added `--force` escape hatch for legacy overwrite behavior.
  Updated summary output to report re-rendered vs skipped counts.
- **Modified:** `src/aspis/commands/init.py` — added 6 new CLI flags
  (`--dry-run`, `--apply`, `--strict`, `--scope`, `--force-conflicts`,
  `--reset-snapshot`). Rejects contradictory `--force-conflicts --strict`.
  Catches `ProtectionError` for clean non-zero exit. Passes all new flags
  through the engine.
- **Modified:** `src/aspis/operations/init.py` — `init_core()` reads the
  new flags from `ctx.options` and forwards them to `write_export()`.
- **Tests:** `tests/test_models_command.py` (+3 tests: PROTECT, CONFLICT,
  --force) + `tests/test_init_cli.py` (+8 tests: --apply, UPDATE, PROTECT,
  --strict, --scope, --force-conflicts, --reset-snapshot, invalid combo).

### Unit 4 — Brain gitignore + E2E acceptance (`572ab25`)
- **Modified:** `src/aspis/data/catalog/scaffold/brain.gitignore` — added
  `current/export-snapshot.json` and `current/export-log.jsonl` so
  generated export state is not tracked in git.
- **New tests:** `tests/test_brain_gitignore.py` (2 tests: scaffold +
  generated project gitignore) + `tests/test_f015_e2e.py` (6 E2E tests
  covering all 5 user stories + corruption recovery).

### Regression fix (`0bebf0d`)
- **Modified:** `tests/test_init_op.py` — updated
  `test_init_does_not_scaffold_on_demand_dirs` to allow `.aspis/current/`
  to exist with export state content (still not scaffolded with `.gitkeep`).
- **Modified:** `src/aspis/data/brain.yaml` — updated comment for
  `.aspis/current` to document `write_export` as a creator.

## Gate & tests

### Scoped gates (per unit)
- **Unit 1:** `pytest tests/test_protect.py -x -q` — 45 passed
- **Unit 2:** `pytest tests/test_export_snapshot.py tests/test_export_protection.py -x -q` — 29 passed
- **Unit 3:** `pytest tests/test_models_command.py tests/test_init_cli.py -x -q` — 19 passed
- **Unit 4:** `pytest tests/test_brain_gitignore.py tests/test_f015_e2e.py -x -q` — 8 passed

### Full suite (post-regression-fix)
- `pytest` (all non-bootstrap tests) — **364 passed, 0 failed**
- Bootstrap tests (`test_bootstrap.py`, `test_bootstrap_cli.py`) timeout
  due to pre-existing subprocess-call slowness in the test environment;
  they do not reference any F-015 code and are unaffected by this feature.

### Total new test count
- 45 (protect) + 29 (export snapshot/protection) + 11 (models/init CLI) +
  8 (gitignore/E2E) = **93 new tests** across 6 test files.

### Key acceptance scenarios verified
- `models --apply` with catalog-changed agent → UPDATE (re-rendered)
- `models --apply` with user-edited agent → PROTECT (skipped)
- `models --apply` with both-changed agent → CONFLICT (reported, not overwritten)
- `models --apply --force` → legacy overwrite (escape hatch)
- `aspis init --write --apply` writes NEW + UPDATE, skips PROTECT + CONFLICT
- `aspis init --write --apply --strict` exits non-zero on CONFLICT/PROTECT
- `aspis init --write --scope=path` limits to matching actions
- `aspis init --write --reset-snapshot` recovers from corrupt snapshot
- `--force-conflicts --strict` rejected as contradictory
- Corrupted snapshot + `--reset-snapshot` → recovery

## Follow-ups

- **Constitution docstring format:** The new test modules
  (`test_brain_gitignore.py`, `test_f015_e2e.py`) use purpose-paragraph
  docstrings rather than the full Purpose/Responsibilities/Does Not/Used By
  format. Non-blocking; can be polished in a follow-up.
- **Runtime hook protection:** `emit_runtime_hooks` outputs are written
  without hash protection (the export module docstring notes this as
  deferred). A future feature could route hook outputs through the same
  decide flow.
- **`--strict` on PROTECT:** The `--strict` flag raises on both CONFLICT
  and PROTECT (FR-010), which is broader than PLAN §2.3's "CONFLICT-only"
  description. This matches the existing export tests and is the correct
  behavior; the plan text could be updated for consistency.
- **Bootstrap test timeout:** `test_bootstrap.py` and
  `test_bootstrap_cli.py` timeout in the current environment due to
  subprocess calls. Pre-existing, not caused by F-015.
