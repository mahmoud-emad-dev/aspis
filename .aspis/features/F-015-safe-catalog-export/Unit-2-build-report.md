# F-015 Unit 2 — Build Report: Snapshot engine + rewired `write_export`

**Feature:** F-015 — Safe Catalog Export
**Unit:** 2 of 4 — Snapshot engine + rewired `write_export`
**Branch:** `feature/F-015-safe-catalog-export`
**Date:** 2026-06-25
**Builder:** general-builder (delegated by build-lead)
**Gate runner:** build-lead (verified independently)

---

## 1. What was built

### Modified file: `src/aspis/export.py` (138 → 525 lines)

The writer was rewired from a single `destination.exists() and not force → skip`
guard to a hash-protected decide flow backed by `aspis.protect` (Unit 1).

**New public symbol:**
- `ProtectionError(RuntimeError)` — raised when `strict=True` and a CONFLICT is
  encountered during an `--apply` run.

**New helper functions (all docstring'd):**
- `_load_snapshot(target_root, *, reset=False) -> dict` — loads
  `.aspis/current/export-snapshot.json`; returns `{"version":1,"paths":{}}` when
  absent; raises `ProtectionError` on corruption unless `reset=True`.
- `_save_snapshot(target_root, snapshot) -> None` — atomic write via
  `tempfile.mkstemp` + `os.fdopen` + `os.replace` (NOT `NamedTemporaryFile`,
  which holds the file open on Windows); creates `.aspis/current/` first.
- `_append_log(target_root, entries) -> None` — appends JSONL entries (one JSON
  object per line) to `.aspis/current/export-log.jsonl`; true append-only.
- `_hash_file(path) -> str | None` — `sha256_text` of a file, or `None` (file
  missing or a directory).
- `_regen_hash(action, project_config, inventory) -> str | None` — hash of what
  the catalog would write; mirrors `_apply` exactly (render via `transform` for
  render ops, source hash for file copies, `None` for directory copies).
- `_pid_alive(pid) -> bool` — cross-platform process-liveness check (POSIX
  `os.kill(pid, 0)`; Windows `OpenProcess` + `WaitForSingleObject`).
- `_acquire_lock` / `_release_lock` — `export.lock` via
  `os.open(O_CREAT|O_EXCL|O_RDWR)`; stale locks (dead PID) are taken over.

**Rewired `write_export`** — extended signature:
```python
def write_export(plan, target_root, *, force=False, write=False,
                 apply=False, strict=False, scope=None,
                 force_conflicts=False, reset_snapshot=False) -> list[str]
```
Splits into `_write_force` (legacy backward-compatible path) and `_write_decide`
(hash-protected path). Lockfile acquired only when `write or apply` (so dry-run
never creates `.aspis/current/`), released in `finally`. Runtime hooks still
emit via `adapter.emit_runtime_hooks(...)` (unchanged — see §6).

**Unchanged (Core is Stable):** `plan_export()` and `_apply()` are byte-identical
to the pre-Unit-2 versions (verified by the builder and re-checked by the
build-lead). `ExportAction` / `ExportPlan` dataclasses unchanged.

### New file: `tests/test_export_snapshot.py` (86 lines, 10 tests)
Covers `_load_snapshot` (absent / round-trip / corrupt-raises / reset-discards),
`_save_snapshot` (atomic, no `.tmp` left, parent-dir creation), `_append_log`
(JSONL lines, append-only), `_hash_file` (missing→None, existing→`sha256_text`
with CRLF content cross-checked).

### New file: `tests/test_export_protection.py` (215 lines, 14 tests)
Covers all 12 TASKS.md Unit-2 acceptance criteria plus 2 lockfile tests:
first-export ADD + snapshot recorded; second-export UNCHANGED (no writes);
user-edit PROTECT; catalog-update UPDATE; both-changed CONFLICT; `force`
overwrites all; `force_conflicts` overwrites CONFLICT but not PROTECT; `strict`
raises `ProtectionError` (and releases the lock); `scope` filters; `apply`
implies `write`; audit log appended (one line per action); plain `write`
backward-compatible (skips existing UPDATE). Plus: lockfile created-then-released;
stale lock with dead PID taken over.

---

## 2. Test results

**Gate verdict: ✅ GREEN**

| Metric | Value |
|---|---|
| Scoped gate | `uv run pytest tests/test_export_snapshot.py tests/test_export_protection.py -x -q` |
| Tests collected | 29 (10 snapshot + 19 protection) |
| Passed | 29 |
| Failed / Errors / Skipped | 0 / 0 / 0 |
| Duration | 0.937 s |
| Runner | build-lead (independent re-run, post-review fixes) |
| Evidence | JUnit XML: `errors="0" failures="0" skipped="0" tests="29" time="0.937"` |

> **Note:** The first gate was 24 tests. After the Unit-2 review (BLOCK — 2
> blockers), the build-lead fixed both blockers and added 5 reviewer-requested
> tests (strict+PROTECT, reset-snapshot recovery, UNKNOWN-snapshot, dry-run
> no-write, render-op hash parity). The re-gate is 29 tests, GREEN. See §8.

**Regression (existing export behavior, backward compat):**

| Metric | Value |
|---|---|
| Command | `uv run pytest tests/test_export.py -x -q` |
| Result | 4 passed, 0 failed |

The 4 pre-existing `test_export.py` tests stay GREEN, confirming `force`/`write`
backward compatibility was preserved.

Per the gate protocol, the full-suite regression is deferred until all 4 units
are complete — only scoped tests run per unit.

---

## 3. Build-lead decisions (reconciling PLAN ↔ SPEC inconsistencies)

Four inconsistencies between `PLAN.md` and `SPEC.md` affect Unit 2 behavior.
The build-lead made conservative, backward-compatibility-prioritizing decisions
(documented here for the reviewer and planning lead):

| ID | Decision | Rationale |
|---|---|---|
| **D-U2-1** | The decide flow runs for classify/log/snapshot whenever `force=False`. Write policy: `force=True`→overwrite all; `apply=True`→write ADD+UPDATE (+CONFLICT if `force_conflicts`), skip UNCHANGED/UNKNOWN/PROTECT; plain `write=True` (no `apply`)→write **only ADD** (byte-identical to old skip-if-exists); `write=False`→dry-run. | Reconciles PLAN §2.2 (decide runs when `force=False`) with SPEC FR-014/SC-003 (no-flag behavior must equal skip-if-exists). Backward compat is the safe, explicit requirement. |
| **D-U2-2** | Snapshot records `regen_hash` on ADD/UPDATE and `live_hash` on UNKNOWN (per PLAN §2.2 step 5). | Operationally correct: recording UNKNOWN lets it later transition to UPDATE/CONFLICT instead of staying UNKNOWN forever. The SPEC clarification ("only record what was written") conflicts; PLAN step 5 is the more complete operational spec. |
| **D-U2-3** | Runtime hooks are **not** routed through the decide engine in Unit 2 — they keep current `emit_runtime_hooks` behavior. | Full decide-flow protection of hooks requires splitting `emit_runtime_hooks` into plan+apply (an adapter interface change to `runtimes/base.py` + adapters), which is outside Unit 2's file scope (`export.py` only) and absent from PLAN §6 Cost-of-Change. **Deferred follow-up; flagged for the planning lead** (PLAN §2.2 5a / SPEC scope vs §6 Cost-of-Change is a plan inconsistency). |
| **D-U2-4** | Use the 6 `DecisionKind` from committed `protect.py`. | The SPEC's 5-category terminology (FR-003) is a naming-layer mismatch already flagged by the Unit-1 reviewer (F-001). The code uses the 6-way table. |

**Builder's implementation decisions (within the above):**
- Lockfile acquired only when `write or apply` (`effective_write`) so dry-run
  never creates `.aspis/current/` (keeps `test_dry_run_writes_nothing` green).
- `_regen_hash` mirrors `_apply`'s rendering exactly (no logic duplication beyond
  calling the same `transform` functions).
- Directory copies stay on the legacy skip-if-exists path (not hash-protected),
  per SPEC assumptions.
- `strict` CONFLICT: the conflict is logged, snapshot/log flushed, then
  `ProtectionError` raised; the lock is released by the outer `finally`.
- `force=True` path now also records written-file hashes in the snapshot and a
  `FORCE` audit-log entry (so the snapshot stays accurate after a force write).

---

## 4. Constitution compliance self-check

| # | Rule | Verdict |
|---|---|---|
| 1 | **Local Change** | ✅ 1 existing file changed (`export.py`) + 2 new test files. Unit-2 Cost-of-Change: 1 existing file (healthy). Running feature total: 2 existing files changed (export.py + the Unit-1-untouched core). |
| 2 | **Plugin First** | ✅ The decide dispatch is uniform over `DecisionKind`; no `if runtime ==` / `if kind == "agents"`. Directory-copy legacy path is a capability check (`regen_hash is None`), not a special case. |
| 3 | **Single Source of Truth** | ✅ Catalog = source; snapshot = record; `decide()` = the one classification function (in `protect.py`). `_regen_hash` reuses `_apply`'s transforms (no second rendering truth). |
| 4 | **Configuration over Code** | ✅ Behavior is data-driven by the three hashes + flags; no if-chain on kind/runtime. |
| 5 | **Core is Stable** | ✅ `plan_export()` and `_apply()` byte-identical. New logic is new functions + a rewritten `write_export` body. |
| 6 | **Dependency Direction** | ✅ `export.py` imports `aspis.protect` (plugin→core). `protect.py` was not edited. No reverse dependency. |
| 7 | **No Special Cases** | ✅ No runtime/asset-kind/profile name-checks in the new code. |
| 8 | **Generated Artifacts** | ✅ Snapshot + audit log are generated by `write_export`, never hand-edited; written atomically / append-only. |
| 9 | **Automation before Intelligence** | ✅ `decide` is the pure deterministic `protect.decide`; lockfile/snapshot/log are deterministic stdlib mechanics. |
| 10 | **Consistency over Cleverness** | ✅ The 6-way dispatch table is the PLAN's table; no novel algorithm. |
| 11 | **Architecture before Features** | ✅ The protection mechanism is general over all `plan.actions`. |
| 12 | **Portable by Default** | ✅ `pathlib`, `os.replace`, explicit `encoding="utf-8"`, posix snapshot keys, cross-platform `_pid_alive` (POSIX + Windows). |

**File rules:** `export.py` module docstring updated with Purpose /
Responsibilities / Does Not / Used By (notes the protection + the deferred
runtime-hook protection). Every new function has a docstring. One concept per
file maintained. No hidden dependencies (roots passed explicitly).

**R-005 (Tests-as-spec):** 24 behaviour-only tests; no test probes internal
state beyond importing the listed helpers; no existing test weakened or deleted
(`test_export.py` untouched and still GREEN).

---

## 5. Scope control

Only `src/aspis/export.py` was modified; only the two new test files were
created. `git status` confirms:
- modified: `src/aspis/export.py` (intended)
- untracked: `tests/test_export_snapshot.py`, `tests/test_export_protection.py` (intended)
- `src/aspis/protect.py` NOT modified (Unit 1, imported only)
- runtime adapters NOT touched
- stray files `.opencode/agents/build-lead.md` and
  `.aspis/config/.runtime-inventory.json` left untouched (pre-existing, unrelated)

---

## 6. Known limitations / deferred

- **Runtime hooks not decide-protected (D-U2-3):** `emit_runtime_hooks` still
  writes via its own skip-if-exists guard. Full protection requires an adapter
  refactor (split into plan + apply) — out of Unit 2 scope, not in PLAN §6
  Cost-of-Change. Flagged for the planning lead to reconcile PLAN §2.2 5a.
- **Directory copies** use legacy skip-if-exists (not hash-protected) — per SPEC
  assumptions (directories are rare; legacy logic acceptable).
- **Stale-lock takeover** is best-effort: if the PID-liveness check errors for
  any reason, the lock is treated as live and the export refuses (safe side).

---

## 7. Next steps

1. ✅ Scoped gate GREEN (24/24) + regression GREEN (4/4), verified by build-lead.
2. Delegate Unit 2 to the reviewer for independent review (constitution +
   test-quality + plan/spec conformance) → `Unit-2-review-report.md`.
3. After review passes (no blockers), hand to the committer.
4. Then proceed to Unit 3 (models bug fix + init CLI flags).

**Not committed by build-lead** — per R-004, the committer handles commits
after review.

---

## 8. Post-review fixes (2026-06-25, after Unit-2 review BLOCK)

The Unit-2 independent review returned **BLOCK — 2 blockers / 3 warnings / 2
nits**. The build-lead fixed both blockers, cleaned up the nit, and added the
high-value missing tests. Full review: `Unit-2-review-report.md`.

**Blocker fixes (in `src/aspis/export.py`):**

| ID | Fix |
|---|---|
| F-001 (BLOCKER) | `_save_snapshot` double-close: restructured so `os.fdopen`'s ownership is respected — `os.fdopen` is called outside the `with`; if it fails, `os.close(fd)` + `os.unlink(tmp)` run (fd still ours); on success the `with fh:` closes the fd and the error path only `os.unlink`s the temp (no `os.close(fd)`). fd is now closed exactly once on every path. |
| F-002 (BLOCKER) | `--strict` now raises `ProtectionError` on `CONFLICT` **or** `PROTECT` (LIVE-CUSTOMIZED), per FR-010. Distinct messages per kind; the CONFLICT message is unchanged so the existing `test_strict_raises_on_conflict` still passes. |

**Nit fix:**
- F-007: removed the redundant `and not force` guard in `_write_decide`'s
  directory-copy branch (that branch is only reached when `force=False`).

**Warning addressed in code:**
- F-003: added an inline comment on the UNKNOWN `live_hash` recording explaining
  the deliberate PLAN §2.2 step 5 vs SPEC-clarification deviation (D-U2-2).

**Tests added (F-005 coverage gaps) — 5 new tests in `test_export_protection.py`:**
1. `test_strict_raises_on_protect` — strict + PROTECT → `ProtectionError` + lock released.
2. `test_reset_snapshot_recovers_from_corruption` — corrupt snapshot raises without reset; recovers with `reset_snapshot=True`.
3. `test_unknown_records_live_hash_in_snapshot` — pre-existing live file → UNKNOWN → preserved, live hash recorded.
4. `test_dry_run_writes_nothing` — `write=False, apply=False` creates no files / no `.aspis/current/`.
5. `test_render_op_hash_parity_is_unchanged` — render-agent exported twice → second run UNCHANGED (proves `_regen_hash` matches `_apply` for render ops).

**Warnings not fixed (deliberate, documented decisions):**
- F-003 (UNKNOWN snapshot) — kept per D-U2-2 (operationally correct); documented inline + in §3.
- F-004 (runtime hooks deferred) — kept per D-U2-3 (requires adapter refactor out of Unit 2 scope); documented in module docstring + §6.

**Nits not fixed (accepted deviations):**
- F-006 (`_regen_hash` signature vs PLAN §9) — the implemented signature
  `_regen_hash(action, project_config, inventory)` is functionally necessary for
  render ops; PLAN §9's `_regen_hash(source, op)` was incomplete. Flagged for the
  planning lead to update PLAN §9.

**Deliberately skipped test gaps (flaky / low-value):**
- Live-PID lock contention (F-005f) — testing a running PID is inherently flaky
  across platforms/CI; the dead-PID takeover path is already covered.
- `_save_snapshot` error-path temp cleanup (F-005g) — not reliably triggerable
  without injecting faults; the fix was verified by code inspection.

**Files changed in this pass:** `src/aspis/export.py`, `tests/test_export_protection.py`.
`plan_export()` / `_apply()` still byte-identical. `protect.py` untouched.

**Re-gate:** `uv run pytest tests/test_export_snapshot.py tests/test_export_protection.py -x -q`
→ 29 passed, 0 failed. Regression `uv run pytest tests/test_export.py -x -q` → 4 passed.
**Not committed** — handed back to the reviewer for confirmation, then the committer.
