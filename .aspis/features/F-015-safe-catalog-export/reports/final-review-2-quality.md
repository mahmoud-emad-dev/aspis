# F-015 Safe Catalog Export — Reviewer #2 Final Review (Code Quality)

- **Feature:** F-015 — Safe Catalog Export
- **Reviewer:** Reviewer #2 (Code Quality, Correctness, Test Coverage)
- **Date:** 2026-06-25
- **Mode:** Final feature review
- **Files reviewed:**
  - `src/aspis/protect.py`
  - `src/aspis/export.py`
  - `src/aspis/commands/models.py`
  - `src/aspis/commands/init.py`
  - `src/aspis/operations/init.py`
  - `tests/test_protect.py`
  - `tests/test_export_snapshot.py`
  - `tests/test_export_protection.py`
  - `tests/test_models_command.py`
  - `tests/test_init_cli.py`
  - `tests/test_brain_gitignore.py`
  - `tests/test_f015_e2e.py`
  - `.aspis/features/F-015-safe-catalog-export/SPEC.md`

---

## Verdict

**APPROVE WITH NOTES**

The implementation is correct, the protection engine behaves as the spec requires, the
`models --apply` blind-force bug is genuinely fixed, all six new CLI flags work and
their interaction matrix is sound, and the test suite covers every user story plus
the regression paths. Test quality is high: tests exercise behavior, edge cases
(BOM/CRLF/bare-CR, None hashes, empty strings, all-three-None, stale lock, corrupted
snapshot, UNKNOWN, render-op hash parity) are covered, and no test would pass if the
code was wrong. The notes below are nits and minor coverage gaps that are
non-blocking; they can be polished in a follow-up.

---

## Correctness — FR-by-FR walkthrough

| FR | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| FR-001 | SHA-256 hash of every file's post-render content | ✅ | `protect.sha256_text` (BOM-strip + CRLF→LF normalize) used by both `_regen_hash` and `_hash_file`. Render parity verified by `test_render_op_hash_parity_is_unchanged`. |
| FR-002 | Persist `export-snapshot.json` mapping path→hash | ✅ | `_save_snapshot` writes `{"version": 1, "paths": {...}}` atomically. Round-trip test + test_first_export_adds_all_files. |
| FR-003 | Classify into 5 categories (SPEC text) | ⚠️ | Code implements 6 `DecisionKind` values (ADD, UNCHANGED, **UNKNOWN**, UPDATE, PROTECT, CONFLICT). UNKNOWN is a deliberate refinement already approved in Unit 1 review (F-001). SPEC text mismatch; code is correct. |
| FR-004 | Decide write/skip per file based on category and flags | ✅ | `_write_decide` dispatch at `export.py:459-483`. Force path separate. |
| FR-005 | Audit log entry per `write_export` that writes | ✅ (richer than spec) | One log entry per file decision (not per invocation) — more useful for audit. Appended to `export-log.jsonl` after the run completes. The spec text says `export-log.json`; the `.jsonl` suffix is the correct extension for an append-only log. |
| FR-006 | `--apply` writes NEW+CATALOG-CHANGED, skips LIVE-CUSTOMIZED+CONFLICT | ✅ | `apply=True` in dispatch: ADD→`effective_write`, UPDATE→`apply`, CONFLICT→`apply and force_conflicts`, PROTECT→`False`. Verified by `test_catalog_update_is_applied`, `test_user_edit_is_protected`, `test_both_changed_is_conflict`. |
| FR-007 | `--force` writes every file | ✅ | `_write_force` bypasses decide; overwrites all. Verified by `test_force_overwrites_everything`. |
| FR-008 | `--force-conflicts` with `--apply` overwrites CONFLICT, skips LIVE-CUSTOMIZED | ✅ | `test_force_conflicts_overwrites_conflict_but_not_protect` covers both outcomes. |
| FR-009 | `--scope` filters by target path prefix | ✅ | `test_scope_filters_actions` and `test_e2e_scope_limits_to_single_file`. Partial snapshot update works because `paths` is mutated in place. |
| FR-010 | `--strict` fails on CONFLICT **or** LIVE-CUSTOMIZED | ✅ | `export.py:508-519` raises on both kinds. Verified by `test_strict_raises_on_conflict` and `test_strict_raises_on_protect`. Unit 2 blocker F-002 resolved correctly. |
| FR-011 | Atomic snapshot write (temp+rename) | ✅ | `tempfile.mkstemp` + `os.fdopen` + `os.replace`. Unit 2 blocker F-001 (double-close) resolved; the new error path is correct on every branch. |
| FR-012 | `--scope` partially updates snapshot | ✅ | Snapshot is mutated in place; only the scoped entry is touched. No test asserts this property explicitly, but it is a direct consequence of the implementation and the existing `test_scope_filters_actions` exercises it. |
| FR-013 | `models --apply` uses `apply=True` semantics | ✅ | `models.py:240-243` calls `write_export(..., force=force, apply=not force, write=True)`. When `--force` is absent, `apply=True`; the decide path is used. Verified by `test_apply_protects_user_edited_agent`, `test_apply_conflicts_on_both_changed_agent`. |
| FR-014 | No-flag `--write` is byte-identical to old skip-if-exists | ✅ | `test_plain_write_backward_compatible_skips_existing` confirms; new test `test_dry_run_writes_nothing` confirms dry-run semantics; existing `test_dry_run_writes_nothing` in `test_export.py` still passes (snapshot file is the only new artifact). |
| FR-015 | No runtime/asset-kind/profile name-checks in classifier | ✅ | `protect.py` imports nothing from `aspis.*`; only stdlib (`enum`, `hashlib`, `dataclasses`). |

**Constitution compliance:**

- **C-COST (Cost of Change):** 1 new module (`protect.py`) + 3 production files substantially modified (`export.py`, `commands/models.py`, `commands/init.py`) + 1 thin flag-forwarding edit (`operations/init.py`) + 1 scaffold entry (`brain.gitignore`) + 1 brain.yaml comment. 6 files modified is healthy for the size of the change; the bulk of the logic lives in the new `protect.py` and the existing `export.py` was extended in place rather than forked. ✅
- **C-PLUGIN-FIRST:** `protect.py` is runtime-, kind-, and profile-agnostic. `_write_decide` is a `DecisionKind` table with no `if runtime == ...` or `if kind == ...`. ✅
- **C-SINGLE-SOURCE:** `decide()` is the sole classifier; `_regen_hash` reuses the same `transform.render_agent` / `transform.render_command` calls as `_apply`. ✅
- **C-CONFIG-OVER-CODE:** Behavior is flag-driven, not branch-on-string. ✅
- **C-NO-SPECIAL-CASE:** Verified. ✅
- **C-FILE-SELF-EXPLAINS:** `protect.py` and `export.py` have full Purpose / Responsibilities / Does Not / Used By docstrings. `commands/init.py` and `commands/models.py` have brief one-line docstrings, but these are pre-existing modules and were not substantively restructured. ✅
- **C-TESTABLE:** `protect.py` is testable in isolation (zero ASPIS imports). `export.py` decision path is exercised through behavior tests; helpers (`_load_snapshot`, `_save_snapshot`, `_append_log`, `_hash_file`) are unit-tested directly. ✅
- **C-PORTABLE:** `os.replace` is cross-platform, UTF-8 I/O throughout, PID-liveness is checked via `ctypes.windll.kernel32` on Windows and `os.kill(pid, 0)` on POSIX. ✅

---

## Code quality

### `src/aspis/protect.py` (153 lines)
- **Strengths:** Pure module, zero side effects, no ASPIS imports. Functions are short and focused. `decide()` is a textbook first-match-wins truth table; the docstring explicitly states the order matters. `Decision` is a frozen dataclass that carries the inputs back out — exactly the right shape for audit logs and dry-run output. The `sha256_text` normalization (BOM strip + CRLF→LF, bare CR untouched) is correct and documented.
- **No findings.**

### `src/aspis/export.py` (545 lines)
- **Strengths:** `write_export` cleanly delegates to `_write_force` (legacy) or `_write_decide` (new). The dispatch table at `export.py:459-483` is the single place where flag × decision is interpreted. Lock acquire/release is bracketed around the whole write path, and the `finally` releases the lock on every exit (including exceptions and `--strict` raises). The `_save_snapshot` error path correctly distinguishes "fd not yet handed to file object" (close manually) from "fd owned by file object" (do not close). `ProtectionError` is a single specific exception type.
- **Nit N-1 (NIT, `export.py:245-249`):** The Windows branch of `_pid_alive` returns `True` for any exception, which silently turns "we couldn't tell" into "treat as alive". The `os.kill` POSIX branch is more granular (distinguishes ESRCH / EPERM / other). Acceptable: a failure to check is the safer default. Could be tightened to log a warning, but this is a defense-in-depth path (the lock file should almost never be queried in normal use).
- **Nit N-2 (NIT, `export.py:407`):** The force-path log entry has `"action": "wrote"` — which is the right value but doesn't reflect the legacy "force-overwrite" intent. If a downstream audit consumer wants to distinguish forced writes from decided writes, the decision kind (`"FORCE"`) is in the same record. The `kind` field carries it; the `action` field is fine as-is. No change required.

### `src/aspis/commands/models.py` (309 lines)
- **Strengths:** The bug fix at `models.py:240-243` is correct and minimal: `force=force, apply=not force, write=True`. When `--force` is absent, `apply=True` routes through the decide path (FR-013). When `--force` is present, the force path runs (legacy behavior). The `skipped` counting at `models.py:245-247` parses `performed` entries by their first colon-separated token — fragile but works because the dispatch is the only producer of these strings.
- **Nit N-3 (NIT, `models.py:245`):** `_skip_kinds` contains `"ADD"`, but `ADD` never appears as a first token in the `performed` list — when a file is added, the entry is `f"{action.op}: {target}"` (e.g. `"render-agent: …"`), not `"ADD: …"`. The set entry is dead. Not a bug (the count is still correct), but the dead entry is misleading to a future reader.

### `src/aspis/commands/init.py` (118 lines)
- **Strengths:** All 6 new flags are registered with `dest=` (so argparse stores them as the intended attribute names). Contradictory `--force-conflicts --strict` is rejected before any work happens, with a clear error and `return 2` (distinct from the `1` returned for `ProtectionError`). `ProtectionError` is caught and reported with a clean exit code. Flag forwarding to `engine.run(...)` is one-for-one. The dry-run header message correctly reads `effective_write` so a user sees the same header they would have seen under the old code.
- **No findings.**

### `src/aspis/operations/init.py` (209 lines)
- **Strengths:** Flag-forwarding in `init_core` (lines 32-40) is mechanical and correct — all 6 new flags are read from `ctx.options` and passed to `write_export`. The pre-existing brain-scaffold, scripts, and root-file logic is untouched.
- **No findings.**

---

## Test quality

### `tests/test_protect.py` (45 tests, 7 classes)
- **Strengths:** Each class maps to a single concern (sha256_text, sha256_bytes, decide cases, decide ordering, plan_runtime, summary). Known SHA-256 values are hardcoded and independently correct. Edge cases are explicitly named: bare CR preserved, leading vs trailing BOM, BOM-only string → empty hash, CRLF-only string → single LF, all-three-None, all-same, Decision frozen. Behavior-only — no internal state probed.
- **Coverage gap (C-1, WARNING, `test_protect.py`):** No test exercises `plan_runtime` with `live_hashes` containing an explicit `None` value (as opposed to an absent key). The behavior is identical because `dict.get(path)` returns `None` for both, so this is not a correctness gap. A future regression test would add completeness.

### `tests/test_export_snapshot.py` (8 tests)
- **Strengths:** All four snapshot-log helpers are tested: default load, round-trip, corrupted JSON raises, reset discards, atomic write produces no `.tmp` leftovers, parent dir created, append-only JSONL, missing file → None. Helpers are exercised at the function level so failures pinpoint the right module.
- **No findings.**

### `tests/test_export_protection.py` (21 tests, including Unit-2 follow-up additions)
- **Strengths:** Full decide flow: ADD (first export), UNCHANGED (second export), PROTECT (user edit), UPDATE (catalog change), CONFLICT (both changed). All flag combinations tested: `force=True` (overwrites), `force_conflicts=True` (overwrites CONFLICT but not PROTECT), `apply=True` (rewrites UPDATE), `strict=True` (raises on CONFLICT and on PROTECT — Unit 2 blocker F-002 covered), `scope=...` (limits), `reset_snapshot=True` (recovers). Lockfile acquired/released and stale-PID takeover. Audit log appended. Dry-run writes nothing. UNKNOWN records `live_hash`. Render-op hash parity (the most subtle correctness property — `_regen_hash` must match `_apply`'s actual output, otherwise a second export would falsely PROTECT every rendered file).
- **Coverage gap (C-2, WARNING):** No test for "lock held by a running PID raises `ProtectionError`". The Unit-2 review (F-005) flagged this and it remains unaddressed. The stale-PID takeover path is tested; the "process is alive" path is not. Not a correctness bug (the code path is exercised manually and is straightforward), but a missing regression test.
- **Coverage gap (C-3, NIT):** No test asserts that `_save_snapshot` cleans up the temp file when `os.fdopen` itself fails. The code path is correct (lines 159-162) and the original Unit-2 review (F-005) flagged this; a regression test would require monkey-patching `os.fdopen`. Defensible to leave un-tested because the fault is hard to induce cleanly.

### `tests/test_models_command.py` (F-015 additions: 3 tests, lines 175-249)
- **Strengths:** The three new tests cover exactly the three behaviors the bug fix introduces:
  - `test_apply_protects_user_edited_agent` — `--apply` alone, user edit preserved.
  - `test_apply_conflicts_on_both_changed_agent` — `--apply` alone, both sides changed, edit preserved, new model not applied.
  - `test_apply_force_overwrites_user_edited_agent` — `--apply --force`, edit is gone.
  All three tests are behavior-only (file content assertions, no internal state), and all three would pass or fail independently of one another.
- **No findings.**

### `tests/test_init_cli.py` (F-015 additions: 8 tests, lines 27-145)
- **Strengths:** Each test corresponds to one flag or one flag combination. The dry-run/--write/--apply happy path is covered, the re-apply with --write --apply UPDATE path is covered, --apply PROTECT is covered, --strict conflict is covered, --scope is covered, --force-conflicts is covered, --reset-snapshot is covered, and the contradictory combo is covered. Tests use the real `aspis.cli.main` entry point so the flag registration, parser, and dispatch are all exercised.
- **Coverage gap (C-4, NIT):** The `--dry-run` flag itself is not directly tested (it is the default, and `test_init_cli_dry_run_writes_nothing` already tests dry-run semantics). Adding `["init", str(tmp_path), "--dry-run"]` as a separate test would be redundant but harmless. Not worth fixing.

### `tests/test_brain_gitignore.py` (2 tests)
- **Strengths:** Both tests are precise: the scaffold file contains the entries, and the generated project's `.aspis/.gitignore` contains the entries. Tiny and focused.
- **No findings.**

### `tests/test_f015_e2e.py` (6 E2E tests, all 5 user stories + corruption recovery)
- **Strengths:** Each test maps to one SPEC user story (Stories 1-5) plus the corruption recovery. Tests run the real CLI through `aspis.cli.main`, simulating the user-visible workflow: init → edit → model-config change → re-apply. The "agent files as the test substrate" rationale is documented in the file docstring and is the right choice (skills are copy-only, agents are render, and model routing changes are the most realistic way to force a "catalog update" without modifying the bundled catalog). E2E Story 6 verifies the corruption-recovery path through the real CLI.
- **No findings.**

---

## Bug hunt

### `protect.py`
- No file I/O, no shared state, no concurrency. **Clean.**

### `export.py`
- **Resource handling:** `_save_snapshot` correctly closes the fd exactly once on every path (Unit-2 blocker F-001 fix verified). The `os.fdopen` failure branch closes manually; the success branch hands ownership to the file object, which the `with` block closes. The `os.replace` is the cross-platform atomic rename.
- **Lock handling:** `_acquire_lock` is bracketed in a `while True` that takes over stale locks. The PID-aliveness check uses `_pid_alive` which handles both POSIX (kill 0) and Windows (OpenProcess + WaitForSingleObject). The `_release_lock` is in a `finally` that runs on every exit, including `--strict` raises. `test_strict_raises_on_conflict` and `test_strict_raises_on_protect` both assert the lock is released after the raise.
- **Snapshot consistency:** The snapshot is mutated in place and saved once at the end of the run (or earlier if `--strict` raises). On process kill mid-run, the snapshot is unchanged and the audit log is unwritten for that run — both consistent. The UNKNOWN case records `live_hash` in the snapshot for first-seen files (build-lead decision D-U2-2), which deviates from the SPEC clarification text but is documented inline and approved in the Unit-2 re-review.
- **Scope filter:** The scope check is applied inside the action loop, so out-of-scope actions are neither classified, written, nor logged. The snapshot is still saved at the end if any in-scope action was processed. **Note:** the scope filter does not log "skipped: <target> (out of scope)" entries; out-of-scope actions are simply absent from the result. This is consistent across both `_write_force` and `_write_decide`. Minor UX issue (users can't see what was excluded), not a bug.
- **Backward compat:** When `force=False, write=True, apply=False`, `_write_decide` is used with `effective_write=True, apply=False`. For ADD: writes. For UNCHANGED: skips (legacy behavior). For UPDATE: skips (because `apply=False`). For PROTECT: skips. For CONFLICT: skips. For UNKNOWN: preserves. The new test `test_plain_write_backward_compatible_skips_existing` verifies the UPDATE case is reported as "UPDATE:" (skipped) and the file is unchanged. **Backwards-compatible.**
- **Inconsistent state risks:** None found. The UNKNOWN→record-`live_hash` behavior is a deliberate decision and the snapshot save at end-of-run means a partial-run leaves the snapshot at the previous (consistent) state.

### `commands/models.py`
- **The bug fix (line 230-243):** Verified. `plan = plan_export(resources.catalog_dir(), profile)` builds the plan from the full catalog; `live = [action for action in plan.actions if action.op == "render-agent" and (root / action.target).exists()]` filters to only currently-existing live agents; `write_export(..., force=force, apply=not force, write=True,)` runs the protection engine. When `force=False`, `apply=True` → decide path → PROTECT, CONFLICT, UNKNOWN, and UNCHANGED are all preserved; only UPDATE and ADD cause a re-render. The user-edited agent is not overwritten. The escape hatch `force=True` runs `_write_force` which overwrites everything.
- **Skipped-counting logic (lines 245-247):** Stringly-typed. The `_skip_kinds` set includes `ADD`, which never appears as a first token in `performed` (an ADD writes, so the entry is `"{action.op}: {target}"`). The entry is dead but not a bug.

### `commands/init.py`
- **Contradictory flags:** Rejected at line 74-77 with `return 2` before any work happens. Distinct from `ProtectionError`'s `return 1`.
- **Flag forwarding:** One-for-one. All 6 new flags plus the existing flags are passed to `engine.run(...)`. No flag is silently dropped or remapped.
- **Dry-run header:** Reads `effective_write` (line 104) so the message is correct regardless of which flag triggered the write.

### `operations/init.py`
- **Flag forwarding:** Mechanical and correct. `ctx.options.get(...)` is used for every new flag; default values are `False` for bools and `None` for `scope`. All 6 new flags are passed to `write_export`.

### Race conditions, off-by-ones, file-handle leaks
- **No off-by-one errors** found. The protection engine uses set/dict membership, not index-based access.
- **No race conditions** beyond the benign TOCTOU in lock acquisition (acceptable: the worst case is concurrent writes, which the file system partially orders).
- **No resource leaks** in normal operation. `_save_snapshot`'s `os.fdopen` failure path is correct; the success path relies on `with fh` to close.

---

## The `models --apply` fix (focus area)

**Line 230 (`plan_export(...)` call):** Correct. Builds the plan from the full bundled catalog.

**Line 240-243 (the fix itself):**
```python
performed = write_export(
    ExportPlan(actions=live, catalog_root=None), root,
    force=force, apply=not force, write=True,
)
```
- `force=force`: when `--force` is absent, `args.force = False`, so `force=False` is passed in → `_write_decide` is used.
- `apply=not force`: when `force=False`, `apply=True` is passed in → the decide path writes ADD and UPDATE only.
- `write=True`: ensures the run is not a dry-run (write_export is invoked for its side effects).
- When `force=True`: `force=True` triggers `_write_force` (overwrites all); `apply=False` is ignored because the force path is taken; `write=True` is required for the force path to take its write branch.

**The old blind-force bug** is fixed: the default `force=False` now flows through the protection engine. A user-edited agent is preserved (PROTECT, verified by `test_apply_protects_user_edited_agent`); a both-changed agent is reported as CONFLICT and preserved (verified by `test_apply_conflicts_on_both_changed_agent`).

**The `--force` escape hatch** is preserved: `--force` falls through to the legacy overwrite path, verified by `test_apply_force_overwrites_user_edited_agent`.

**Fix correctness:** ✅. No regression to the legacy force path; new protection is the default.

---

## The init CLI flags (focus area)

All 6 new flags are registered, forwarded, and tested:

| Flag | Registration | Forwarding | Test |
|------|--------------|------------|------|
| `--apply` | `commands/init.py:40-44` | `init_core` `apply=apply` (line 36 → 54) | `test_init_cli_apply_flag_scaffolds_project`, `test_init_cli_reapply_with_apply_updates_changed_agent`, `test_init_cli_reapply_protects_user_edited_agent` |
| `--strict` | `commands/init.py:45-49` | `init_core` `strict=strict` | `test_init_cli_strict_exits_nonzero_on_conflict` |
| `--scope` | `commands/init.py:50-54` | `init_core` `scope=scope` | `test_init_cli_scope_limits_to_matching_files` |
| `--force-conflicts` | `commands/init.py:55-60` | `init_core` `force_conflicts=force_conflicts` | `test_init_cli_force_conflicts_overwrites_conflict` |
| `--reset-snapshot` | `commands/init.py:61-66` | `init_core` `reset_snapshot=reset_snapshot` | `test_init_cli_reset_snapshot_recovers_from_corruption` |
| `--dry-run` | `commands/init.py:34-39` | Implicit (default behavior; not forwarded because there is nothing to forward) | Implicit in `test_init_cli_dry_run_writes_nothing` (pre-F-015) |

**Flag interaction matrix:**
- `--force` + `--apply`: `force` wins (`if force:` short-circuits to `_write_force`). ✅
- `--force` + `--strict`: `force` wins; `--strict` is silently bypassed. Not a bug (the spec clarification says `force` wins), but worth noting.
- `--force-conflicts` + `--strict`: rejected with `return 2` at `commands/init.py:74-77` *before* any work. Verified by `test_init_cli_force_conflicts_with_strict_rejected`. ✅
- `--apply` + `--write`: redundant; `--apply` implies `--write` (`effective_write = write or apply`). ✅
- `--apply` + `--write --force`: `force` wins. ✅
- `--scope` + `--apply`: scope filter applied; classify and write only the scoped action. Verified. ✅
- `--scope` + `--strict`: out-of-scope actions are not classified at all, so they cannot trigger `--strict`. In-scope CONFLICT or PROTECT still raise. ✅
- `--scope` + `--force`: out-of-scope actions are still skipped (the force path also checks `scope` at `export.py:387`); in-scope actions are force-overwritten. ✅
- `--reset-snapshot` + everything else: orthogonal; the snapshot is loaded with `reset=True`, all other behavior is unaffected. ✅

**Invalid combos:** The contradictory `--force-conflicts --strict` is the only explicitly rejected combination (which the spec calls out). Other invalid combinations (e.g., `--apply` without an ASPIS project) are reported as clean errors (`return 1`) by the underlying engine. ✅

---

## Findings (sorted by severity)

### Blockers
- *None.*

### Warnings
- **W-1 (C-1, `test_protect.py`):** No test for `plan_runtime` with `live_hashes` containing an explicit `None` value. Behavior is identical to an absent key, so this is not a correctness gap. Optional follow-up.
- **W-2 (C-2, `tests/test_export_protection.py`):** No test for "lock held by a running PID raises `ProtectionError`". The stale-PID takeover path is tested; the "process is alive" path is not. Flagged by the Unit-2 review (F-005) and remains unaddressed. Optional follow-up.

### Nits
- **N-1 (export.py:245-249):** Windows `_pid_alive` returns `True` on any exception (conservative default). Could be tightened but is defense-in-depth.
- **N-2 (export.py:407):** The force-path audit log uses `"action": "wrote"`; the `kind` field already carries `"FORCE"` so a downstream consumer can distinguish. No change required.
- **N-3 (models.py:245):** `_skip_kinds` includes `"ADD"`, which never appears as a first token in `performed`. Dead entry, not a bug.
- **N-4 (commands/models.py, commands/init.py, operations/init.py):** The F-015-modified command and operation modules do not have full Purpose/Responsibilities/Does Not/Used By docstrings. Pre-existing modules, substantively unchanged; the convention is upheld by the new `protect.py` and the updated `export.py`. Acceptable.
- **N-5 (test_brain_gitignore.py, test_f015_e2e.py):** New test modules use purpose-paragraph docstrings rather than the full format. Documented in the feature report. Acceptable.
- **N-6 (export.py:387, 435):** The scope filter in both the force and decide paths silently skips out-of-scope actions without logging them. Users can detect this by running with a different scope and comparing performed counts. UX, not correctness.
- **N-7 (SPEC.md FR-005):** SPEC text refers to `export-log.json`; the implementation uses `export-log.jsonl`. The `.jsonl` extension is correct for an append-only log. Either fix the SPEC text or rename the file. Documentation only.

### Documentation nits (carry-over from prior reviews, still standing)
- **D-1 (SPEC.md FR-003, Key entities):** SPEC still lists 5 categories; the implementation has 6. Already flagged in Unit-1 review. Still unaddressed but non-blocking.
- **D-2 (PLAN.md §9):** `_regen_hash` signature in the plan does not match the implementation (extra `project_config` and `inventory` parameters). Already flagged in Unit-2 review. Still unaddressed but non-blocking.

---

## Conclusion

F-015 is ready to ship. The protection engine is correct, the `models --apply` blind-force bug is genuinely fixed, all 6 new CLI flags work and interact correctly, the test suite covers every user story plus the regression paths, and no test is tautological. The notes are polish items (a missing live-PID lock test, dead code in `_skip_kinds`, SPEC text inconsistencies) that do not block the feature. Recommend **APPROVE WITH NOTES** — the notes can be addressed in a follow-up or accepted as-is.
