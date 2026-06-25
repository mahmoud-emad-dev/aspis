# F-015 Unit 2 — Independent Code Review Report

**Feature:** F-015 Safe Catalog Export  
**Unit:** Unit 2 — Rewire `src/aspis/export.py` to use the protection engine  
**Reviewer:** Independent code reviewer  
**Date:** 2026-06-25  
**Files reviewed:**
- `src/aspis/export.py`
- `tests/test_export_snapshot.py`
- `tests/test_export_protection.py`
- `src/aspis/protect.py` (reference engine)

**Rules / spec / plan referenced:**
- `.aspis/rules/architecture-constitution.md`
- `.aspis/rules/system-rules.md`
- `.aspis/features/F-015-safe-catalog-export/PLAN.md`
- `.aspis/features/F-015-safe-catalog-export/SPEC.md`

---

## Verdict

**BLOCK**

Two correctness/spec-deviation issues must be fixed before commit: a double-close file-descriptor bug in the atomic snapshot error path, and `--strict` failing to raise on `PROTECT` (LIVE-CUSTOMIZED) decisions, which violates FR-010.

---

## Findings

| ID | Severity | Location | Description | Recommendation |
|----|----------|----------|-------------|----------------|
| F-001 | **BLOCKER** | `src/aspis/export.py:154-169` (`_save_snapshot`) | `tempfile.mkstemp()` returns an OS file descriptor that is passed to `os.fdopen()`. The `with os.fdopen(...)` context manager closes the descriptor when it exits. The `except Exception:` block then calls `os.close(fd)`, which is a double-close. On Unix this can close an unrelated descriptor if the number has been reused between closes; on Windows it raises `EBADF`, which is swallowed but still indicates incorrect fd ownership. | Remove `os.close(fd)` from the error path. When using `os.fdopen`, the file object owns the descriptor. If `os.fdopen` itself could fail, handle that separately before entering the `with` block. |
| F-002 | **BLOCKER** | `src/aspis/export.py:493-499` (`_write_decide`) | `--strict` only raises `ProtectionError` for `DecisionKind.CONFLICT`. SPEC FR-010 requires a non-zero exit when any file is classified as `CONFLICT` **or** `LIVE-CUSTOMIZED` during an `--apply` run. `PROTECT` maps to `LIVE-CUSTOMIZED`, so a `--strict --apply` run with a user-edited file currently exits 0 and silently preserves it. | Extend the strict check to also raise on `DecisionKind.PROTECT` (or add a separate strict guard for it). Add a regression test. |
| F-003 | WARNING | `src/aspis/export.py:455-458` (`_write_decide`) | For `UNKNOWN` decisions the code writes `paths[target_posix] = live_hash` even though the file is **not** overwritten. This matches PLAN §2.2 step 5 but contradicts the SPEC clarification: "snapshot only records what was actually written. The audit log records everything." | Reconcile the plan and spec. If the intent is to track first-seen unknown files for future protection, update the SPEC clarification explicitly; otherwise stop mutating the snapshot for preserved files and rely on the audit log. |
| F-004 | WARNING | `src/aspis/export.py:344-351` (`write_export`) | Runtime hook outputs from `emit_runtime_hooks` are **not** routed through the decide flow. They are emitted with their own `force`/`write` semantics and never recorded in the snapshot/log. This conflicts with PLAN §2.2 step 5a and the SPEC scope statement that "Runtime hook outputs ... are protected by the same decide flow as catalog actions." | Documented as a deferred follow-up in the module docstring. Acceptable as a scoped Unit-2 limitation because full implementation requires adapter API changes to expose the files written. Track as a follow-up issue and update the SPEC/PLAN if it remains out of scope. |
| F-005 | WARNING | `tests/test_export_protection.py`, `tests/test_export_snapshot.py` | Several important behaviors are not exercised: (a) `--strict` with a `PROTECT` decision, (b) `write_export(..., reset_snapshot=True)` on a corrupt snapshot through the public API, (c) `UNKNOWN` → snapshot `live_hash` behavior, (d) dry-run (`write=False, apply=False`) guarantees no file is created or modified, (e) render-op hash parity between `_regen_hash` and `_apply`, (f) lock contention when the PID in the lockfile is alive, (g) `_save_snapshot` temp-file cleanup on an error path. | Add tests for the missing coverage, especially (a) because it pairs with blocker F-002, and (d)/(e) because they guard against false PROTECT/CONFLICT decisions. |
| F-006 | NIT | `src/aspis/export.py:188-211` (`_regen_hash`) | The implemented signature is `_regen_hash(action, project_config, inventory) -> str \| None`, which differs from PLAN §9's `_regen_hash(source: Path, op: str) -> str`. The actual signature needs the extra context to compute render hashes, so the deviation is reasonable, but the plan should be updated to match. | Update PLAN §9 to reflect the real helper signature and return type. |
| F-007 | NIT | `src/aspis/export.py:436` (`_write_decide`) | The condition `if destination.exists() and not force:` includes `and not force`, but this branch is only reached when `force=False` (the `else` branch of the top-level `if force:` in `write_export`). The guard is redundant and slightly misleading. | Remove `and not force` or add a comment explaining it is defensive. |

**Finding counts:** 2 BLOCKER, 3 WARNING, 2 NIT.

---

## Build-lead decisions assessment

### D-U2-1 (write policy)
**Sound.** The dispatch correctly implements:
- `force=True` → overwrite all (FR-007).
- `apply=True` → write `ADD` and `UPDATE`; write `CONFLICT` only if `force_conflicts=True`; skip `UNCHANGED`, `UNKNOWN`, `PROTECT` (FR-006, FR-008).
- Plain `write=True` (no `apply`) → write only `ADD`, which is byte-identical to the old skip-if-exists guard for existing files (FR-014, SC-003).
- `write=False` and `apply=False` → dry-run; no `_apply` call is reachable because `effective_write` is false.

The policy is also constitution-compliant: no special cases per runtime/kind, and the write-or-skip decision is driven by the `DecisionKind` produced by the single `decide()` classifier.

### D-U2-2 (snapshot: record `regen_hash` on ADD/UPDATE, `live_hash` on UNKNOWN)
**Sound but spec-deviating.** Recording `regen_hash` for ADD/UPDATE is correct and aligns with "snapshot records what was written." Recording `live_hash` for UNKNOWN improves future protection (the next run can detect UNCHANGED/PROTECT/UPDATE instead of UNKNOWN again), but it directly contradicts the SPEC clarification that "snapshot only records what was actually written." This should be reconciled explicitly in the SPEC or the snapshot write for UNKNOWN should be removed. Treat as a WARNING, not a blocker, because user-visible write behavior is unchanged.

### D-U2-3 (runtime hooks deferred)
**Acceptable scoped limitation.** Full protection of `emit_runtime_hooks` outputs requires adapter changes so export.py can discover which files the adapter wrote and run them through the same decide/snapshot/log flow. Unit 2 is scoped to `export.py` and the adapters are not in that scope. The module docstring already documents the deferral. The gap should be tracked as a follow-up and the SPEC/PLAN updated if the deferral persists beyond Unit 2.

### D-U2-4 (6 DecisionKind vs SPEC's 5-category naming)
**Sound.** The 6-way table is a refinement of the SPEC's 5 categories: `NEW→ADD`, `IDENTICAL→UNCHANGED`, no-history files map to `UNKNOWN`, `CATALOG-CHANGED→UPDATE`, `LIVE-CUSTOMIZED→PROTECT`, and `CONFLICT→CONFLICT`. The terminology mismatch is benign; the extra `UNKNOWN` bucket prevents conflating "file matches catalog with no history" and "file exists but we have no history." This is constitution-compliant and consistent with the proven decision table.

---

## Constitution compliance checklist

| # | Rule | Status | Notes |
|---|------|--------|-------|
| 1 | Local Change | ✅ | Unit 2 changes are limited to `src/aspis/export.py` plus two test files. `src/aspis/protect.py` is Unit 1, already committed. |
| 2 | Plugin First | ✅ | The dispatch table uses `DecisionKind`; no runtime/kind/profile is named. |
| 3 | Single Source of Truth | ✅ | `decide()` is the sole classifier. `_regen_hash` reuses the same `transform.render_agent`/`render_command` calls as `_apply`. |
| 4 | Configuration over Code | ✅ | Behavior is controlled by flags/parameters, not by `if` chains on concrete kinds or runtimes. |
| 5 | Core is Stable | ✅ | `plan_export()` and `_apply()` are unchanged. `write_export()` keeps its original `force`/`write` parameters. |
| 6 | Dependency Direction | ✅ | `export.py` imports `protect.py`; `protect.py` has no ASPIS imports. |
| 7 | Discovery over Registration | ✅ | No hand-maintained registry added. |
| 8 | Generated Artifacts | ✅ | Snapshot and JSONL log are generated, atomic (`os.replace`), and append-only. |
| 9 | No Special Cases | ✅ | No `if runtime == "..."` or `if kind == "..."` in the new code. |
| 10 | Consistency over Cleverness | ✅ | Direct, table-driven decision logic. |
| 11 | Architecture before Features | ✅ | General protection mechanism usable by init, models, bootstrap. |
| 12 | Portable by Default | ✅ | Cross-platform PID check, `os.replace`, UTF-8 I/O, posix snapshot keys. |
| — | File rules | ✅ | `export.py` module docstring is updated; every new function has a docstring. |

---

## Plan/spec conformance checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| `write_export` extended signature | ✅ | Matches PLAN §2.2 / §9. |
| Lock acquisition (PLAN step 0) | ✅ | `O_CREAT \| O_EXCL \| O_RDWR`, stale-PID takeover, released in `finally`. |
| Load snapshot (PLAN step 1) | ✅ | Empty default, corruption raises unless `reset_snapshot`. |
| Scope filter (PLAN step 2 / FR-009) | ✅ | Filters by `action.target` prefix; partial snapshot update works. |
| Compute 3 hashes (PLAN step 3 / FR-001) | ✅ | `regen_hash`, `live_hash`, `snapshot_hash`. |
| Call `protect.decide()` (PLAN step 4) | ✅ | Correct argument order. |
| Dispatch per `DecisionKind` (PLAN step 5) | ✅ | ADD/UPDATE write and record `regen_hash`; UNCHANGED/PROTECT skip; UNKNOWN preserves and records `live_hash` (see F-003). |
| Runtime hooks routed through decide (PLAN step 5a / SPEC scope) | ❌ | Deferred; hooks bypass the flow (see F-004). |
| Atomic snapshot write (PLAN step 6 / FR-011) | ⚠️ | Uses `tempfile.mkstemp` + `os.fdopen` + `os.replace`, but the error path double-closes the fd (F-001). |
| JSONL audit log (PLAN step 7 / FR-005) | ✅ | One JSON object per line, append-only, no array wrapper. |
| `--force` bypasses decide (FR-007) | ✅ | `_write_force` skips classification. |
| `--apply` writes ADD+UPDATE, skips PROTECT+CONFLICT (FR-006) | ✅ | Correct. |
| `--force-conflicts` writes CONFLICT but not PROTECT (FR-008) | ✅ | Correct. |
| `--strict` raises on CONFLICT **and** LIVE-CUSTOMIZED (FR-010) | ❌ | Only raises on CONFLICT; PROTECT is ignored (F-002). |
| `--scope` filters by target prefix (FR-009) | ✅ | Correct. |
| `--reset-snapshot` recovers from corruption | ✅ | Implemented; full-flow test missing (F-005). |
| Backward compat: plain `--write` = skip-if-exists (FR-014 / SC-003) | ✅ | Verified by test and code inspection. |
| Helper signatures match PLAN §9 | ⚠️ | `_regen_hash` signature differs (F-006); `_load_snapshot` includes `reset` not shown in §9. |
| Snapshot only records what was written (SPEC clarification) | ⚠️ | UNKNOWN records `live_hash` for preserved files (F-003). |

---

## System rules checklist

| Rule | Status | Notes |
|------|--------|-------|
| R-001 Scope | ✅ | Review is read-only; only the review report file is written. |
| R-002 Gates first | ✅ | Build-lead reports GREEN gates: 24 passed in scoped gate, 4 passed in regression gate. |
| R-003 Deterministic-first | ✅ | Hash comparison and decision table are pure deterministic code. |
| R-005 Tests-as-spec | ✅ | Tests are behavior-only; no tests are weakened. Missing coverage is noted in F-005. |

---

## Test quality assessment

The 24 tests are behavior-focused and cover the primary flows well:
- Snapshot helper round-trip, corruption, reset, and atomic write.
- Audit log append-only JSONL behavior.
- Hash helper parity with `sha256_text`.
- Full decide-flow cycles: ADD, UNCHANGED, PROTECT, UPDATE, CONFLICT.
- `force`, `force_conflicts`, `strict`, `scope`, `apply implies write`, and stale-lock takeover.

Gaps that matter:
1. **Strict + PROTECT** — the missing test hides blocker F-002.
2. **`reset_snapshot=True` through `write_export`** — `_load_snapshot(..., reset=True)` is unit-tested, but the public recovery path is not.
3. **UNKNOWN → snapshot `live_hash`** — no test creates a pre-existing target before the first export.
4. **Dry-run no-write guarantee** — no assertion confirms that `write_export(..., write=False, apply=False)` creates no files and modifies no snapshot.
5. **Render-op hash parity** — all protection tests use `op="copy"`; `_regen_hash` for `render-agent`/`render-command` is not exercised end-to-end.
6. **Live-PID lock contention** — stale-lock takeover is tested, but the "lock held by a running process" path is not.
7. **`_save_snapshot` error cleanup** — the temp file cleanup path is not exercised.

No test asserts the wrong thing, and none are tautological.

---

## Conclusion

Unit 2 is architecturally sound and largely matches the plan, but it cannot be approved as-is because of two blockers:

1. **F-001** — the double-close in `_save_snapshot` is a resource-handling bug that can corrupt unrelated file descriptors on Unix.
2. **F-002** — `--strict` does not fail on `PROTECT` decisions, violating SPEC FR-010 and breaking the CI-safe strict-mode contract.

Once these are fixed and the missing strict+PROTECT test is added, the remaining items (UNKNOWN snapshot semantics, runtime-hook deferral, and coverage gaps) can be addressed as warnings or follow-up work. The verdict is **BLOCK**.

## Re-review (post-fix, 2026-06-25)

**Updated verdict:** APPROVE

The two blockers from the initial review are fixed correctly, the requested coverage tests are in place, and the re-gate is GREEN. No functional regressions were introduced.

### Per-finding re-check

| ID | Severity | Status | Note |
|---|---|---|---|
| F-001 | BLOCKER | RESOLVED | `_save_snapshot` now closes the fd exactly once on every path: `os.fdopen` failure closes it manually; success hands ownership to the file object, which the `with` block closes; error paths only unlink the temp file. |
| F-002 | BLOCKER | RESOLVED | `--strict` now raises `ProtectionError` on both `CONFLICT` and `PROTECT`; snapshot/log are flushed before raising (when `effective_write`); the lock is released by the outer `finally`; the CONFLICT message is unchanged. |
| F-003 | WARNING | ACCEPTED | The UNKNOWN `live_hash` recording remains per build-lead decision D-U2-2; the inline comment now documents the PLAN §2.2 step 5 vs SPEC clarification deviation. |
| F-004 | WARNING | REMAINS | Runtime hooks still bypass the decide flow, accepted as a scoped Unit-2 limitation requiring adapter changes; documented in the module docstring and build report. |
| F-005 | WARNING | ADDRESSED | All five high-value coverage gaps are now tested: strict+PROTECT, reset-snapshot recovery, UNKNOWN→snapshot, dry-run no-write, and render-op hash parity. |
| F-006 | NIT | ACCEPTED | `_regen_hash` signature still differs from PLAN §9; build report flags this for planning-lead update. |
| F-007 | NIT | RESOLVED | Redundant `and not force` removed from the directory-copy branch; behavior unchanged because that branch is only reached when `force=False`. |

### New tests validation

The five new tests in `tests/test_export_protection.py` are valid and behaviour-only:

1. `test_strict_raises_on_protect` — correct PROTECT setup, asserts `ProtectionError` with the new protected message, asserts lock released.
2. `test_reset_snapshot_recovers_from_corruption` — corrupts snapshot, asserts raise without reset, asserts recovery with `reset_snapshot=True`.
3. `test_unknown_records_live_hash_in_snapshot` — pre-existing live file → UNKNOWN, asserts preserved and live hash recorded.
4. `test_dry_run_writes_nothing` — asserts no files / no `.aspis/current/` in dry-run.
5. `test_render_op_hash_parity_is_unchanged` — render-agent twice, second UNCHANGED.

None of the pre-existing 14 tests were weakened; `test_strict_raises_on_conflict` still passes with the original match.

### New findings introduced by the fixes

- **F-008 (NIT):** `ProtectionError` docstring (line 56-57) still says "raised when --strict is set and a CONFLICT decision is encountered". It should be updated to include PROTECT, since F-002 now raises on both kinds. Non-blocking; purely documentation.

No other new functional issues or regressions were found.

### Verification performed

- Read `src/aspis/export.py`, `tests/test_export_protection.py`, `src/aspis/protect.py`, and `.aspis/features/F-015-safe-catalog-export/Unit-2-build-report.md`.
- Confirmed `src/aspis/protect.py` is unmodified.
- Re-ran the scoped gate: `uv run pytest tests/test_export_snapshot.py tests/test_export_protection.py -x -q` → 29 passed, 0 failed.
- Re-ran the regression gate: `uv run pytest tests/test_export.py -x -q` → 4 passed, 0 failed.
- Spot-checked that `plan_export()` and `_apply()` remain unchanged and contain no new special cases.

### Final recommendation

Ready to commit: **yes**. The blockers are resolved, tests pass, and the remaining warnings/nits are either accepted/documented or non-blocking documentation.
