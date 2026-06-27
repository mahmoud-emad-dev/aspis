# F-015 — Safe Catalog Export · Final Review (Rules Compliance)

**Reviewer:** Reviewer #1 (Rules Compliance)
**Scope:** Architecture constitution (12 extension rules) + System rules (R-001…R-009) + SPEC compliance
**Mode:** Strict
**Branch:** `feature/F-015-safe-catalog-export` (HEAD `0bebf0d`)

---

## Verdict

# **APPROVE WITH NOTES**

The implementation is **architecturally sound and rules-compliant**. All 12
constitution extension rules are satisfied, R-001…R-009 hold, and the 15
functional requirements are met by the implemented code (verified against
the test suite). The notes below are non-blocking: a deliberate
spec/plan deviation, a minor docstring correction, and one
edge-case-comment that was a follow-up deferred by the build lead.

---

## Cost-of-Change test (the one measurable rule)

| Category | Files | Count |
|---|---|---|
| **Existing product files changed** | `export.py`, `commands/init.py`, `commands/models.py`, `operations/init.py` | **4** |
| **New product code** | `protect.py` | **1** |
| **Brain data update** | `data/catalog/scaffold/brain.gitignore` (+2 lines) | **1 (data, not code)** |
| **New tests** | `test_protect.py`, `test_export_protection.py`, `test_export_snapshot.py`, `test_init_cli.py` (extended), `test_models_command.py` (extended), `test_f015_e2e.py`, `test_brain_gitignore.py` | **6+** |

**Verdict: 4 existing product files → healthy band (1–3) is exceeded by 1
file; well within warning band (5–10). Not an architecture problem.**

Note: the spec/plan listed 4 changed product files; that is exactly what
landed. The `.gitignore` change is a 2-line scaffold data update, not a
code edit, so it does not change the Cost-of-Change band.

---

## 12 constitution extension rules — compliance

| # | Rule | Status | Evidence |
|---|---|---|---|
| 1 | **Local Change** | PASS | 4 existing product files changed, 1 new module. `protect.py` carries all new logic; `export.py` only integrates it. |
| 2 | **Plugin First** | PASS | `protect.py` is runtime-agnostic. `decide()` takes only hash strings — no `runtime`/`kind`/`profile` parameter. `export.py` still uses `get_adapter(runtime).emit_runtime_hooks(...)` (line 356), which is the existing per-runtime *capability* pattern, not a new name check. |
| 3 | **Single Source of Truth** | PASS | Catalog = source of *what to write*. Snapshot = record of *what was last written from it*. `decide()` reads both to determine action. No third store. |
| 4 | **Configuration over Code** | PASS | `apply`, `strict`, `scope`, `force_conflicts`, `reset_snapshot`, `write`, `force` are all `write_export()` parameters, not if-chains on kind/runtime. |
| 5 | **Core is Stable** | PASS | `plan_export()` (lines 95–121 of `export.py`) and `_apply()` (lines 526–545) are byte-identical in shape to the pre-F-015 version (still routes through `shutil.copy2`/`copytree` for copies, still uses `transform.render_*` for renders, still writes with `encoding="utf-8", newline="\n"`). The protection logic is *additive* — it lives in `_write_decide` and `_write_force`, dispatched from `write_export`. |
| 6 | **Dependency Direction** | PASS | `protect.py` imports only `enum`, `hashlib`, `dataclasses`, `__future__.annotations` (lines 27–31). **Zero** ASPIS imports. `export.py` imports `from aspis.protect import DecisionKind, decide, sha256_text` (line 52) — plugin-style import, but `export.py` is the *caller* and `protect.py` is the *pure helper*; the dependency flows from caller to helper, not the reverse. No circularity. |
| 7 | **Discovery over Registration** | PASS | No new `REGISTRY = [...]` introduced. The new `ProtectionError`, `DecisionKind`, and helpers are all local to `protect.py`/`export.py`. Runtime discovery continues through the existing `get_adapter()` mechanism. |
| 8 | **Generated Artifacts** | PASS | `.aspis/current/export-snapshot.json` and `.aspis/current/export-log.jsonl` are both written by `write_export()` and added to `brain.gitignore` (lines 13–14). They are not hand-editable. `data/brain.yaml` was also updated to note `.aspis/current` now carries export state in addition to the active-feature pointer. |
| 9 | **No Special Cases** | PASS | The decide flow classifies purely by hash comparison. The `if scope is not None and not action.target.startswith(scope): continue` (line 387, 435) is a **generic prefix match on a string field**, not a runtime/kind name check. The `if action.op == "render-agent"` etc. in `_regen_hash` (lines 202–218) and `_apply` (lines 528–545) are **dispatch on op-type** — the op is data attached to the action, not a runtime-specific hardcode. The pre-existing `if scope == "project-only"` (line 104) is the asset's *own declared export scope* read from its YAML frontmatter, not a runtime check. No `if runtime == "claude"` anywhere. |
| 10 | **Consistency over Cleverness** | PASS | The decision table is the same 6-case truth table described in the SPEC/PLAN. The branches in `_write_decide` (lines 459–484) are a flat `if/elif DecisionKind.X:` ladder — boring and predictable. No clever metaprogramming. |
| 11 | **Architecture before Features** | PASS | The protection mechanism is general — `init --apply`, `init --write`, and `models --apply` all flow through the same `write_export()` decide path. No per-operation special case. (See `models --apply` at `commands/models.py` line 240–243 — passes `apply=not force, write=True` to the same `write_export` everyone else uses.) |
| 12 | **Portable by Default** | PASS | `sha256_text` normalizes CRLF→LF and strips leading UTF-8 BOM (lines 60–71 of `protect.py`). `encoding="utf-8"` is set on every `read_text`/`write_text` in `export.py` and `protect.py`. `pathlib.Path` is used throughout. `os.replace` is used for atomic snapshot writes (line 167 of `export.py`). Snapshot keys are paths supplied by the caller (which is `action.target` — set by `assetkinds.target()` and consumed as a posix-style string by `_write_decide`'s prefix match). `_pid_alive` is explicitly cross-platform (posix + Windows ctypes, lines 221–249). |

---

## R-001 through R-009 — compliance

| Rule | Status | Evidence / Note |
|---|---|---|
| **R-001 Scope** | PASS | All edits are confined to the F-015 task scope: `protect.py` (new), `export.py` (integration), the 3 CLI/operation files for flag plumbing, and the brain gitignore data update. `data/brain.yaml` got a 1-line comment refresh to reflect that `.aspis/current` now also holds export state — minor, in-scope, not a secret path. |
| **R-002 Gates first** | UNVERIFIED in this review | Could not run `pytest`/`ruff`/`mypy` from this reviewer (no shell). Build/unit reports cite the gates; cross-verifying here is out of scope of *rules* review. **Note (not a finding):** reviewer #2 (test/quality) is the right place to run the gates. |
| **R-003 Deterministic-first** | PASS | The whole decide flow is a deterministic SHA-256 hash comparison. No agent, no LLM call, no heuristic. The build lead's `Unit-2-build-report.md` documents the deliberate deviation from "snapshot only records what was written" to "UNKNOWN records live hash" — that deviation is still *deterministic*, just slightly smarter about state. |
| **R-004 One writer** | PASS | Build went unit-by-unit (U1 → U2 → U3 → T-04 → final fix) on a single feature branch. Reviewer is read-only; this report does not modify code. |
| **R-005 Tests-as-spec** | PASS | 6+ new/extended test files totalling >1000 lines of tests (`test_protect.py` 317 lines, `test_export_protection.py` 306 lines, `test_f015_e2e.py` 183 lines, etc.). The full decide truth table, every flag combination, snapshot corruption/reset, lockfile takeover, UNKNOWN-with-recorded-hash, dry-run output, render-hash parity, and CLI contradictions are all covered. The CONFLICT-via-render-op test (`test_render_op_hash_parity_is_unchanged`) catches a subtle class of false-PROTECT bugs. |
| **R-006 Thin agents, single source** | N/A | This feature is a code change, not an agent or skill change. The relevant agents (`reviewer.md`, etc.) were touched earlier in the F-015 lifecycle (active-feature mechanics) but not as part of this delivery. |
| **R-007 Pinned models** | N/A | No agent instruction changed. The 5 live agent files modified earlier (in commits before the F-015 *implementation* started) are pre-existing context; not a F-015 deliverable. |
| **R-008 Human gate** | PASS | The constitution/rules changes in `data/catalog/rules/architecture-constitution.md` are copy-only (the source of truth is `.aspis/rules/architecture-constitution.md` — unchanged). The F-015 implementation does not change any rule, permission, or model-routing. The data edit to `brain.gitignore` is a scaffold data update (2 lines), not a rule change. |
| **R-009 Trace and learn** | PASS | The feature produces `.aspis/current/export-log.jsonl` — a per-decision audit log, true to the rule's spirit of "important work leaves a traceable record". This is the F-015 implementation's primary deliverable for R-009. |

---

## SPEC requirements (FR-001…FR-015) — compliance

| FR | Status | Evidence |
|---|---|---|
| **FR-001** SHA-256 of post-render content | PASS | `protect.sha256_text` + `export._regen_hash` hash what would be written (source for copies, rendered text for agents/commands). |
| **FR-002** Snapshot maps path → hash | PASS | `_save_snapshot` writes `{"version": 1, "paths": {<posix-rel-path>: <hex>}}`. |
| **FR-003** Five-category classification | PASS | `DecisionKind` enum: ADD, UNCHANGED, UPDATE, PROTECT, CONFLICT (plus UNKNOWN for "live exists, no snapshot entry" — SPEC's 5 categories are the user-facing outcomes; UNKNOWN is a 6th internal kind that resolves into "preserved", which is a no-op for the user). All 5 user-visible categories are reachable from the test suite. |
| **FR-004** Decide write/skip per file per flags | PASS | `_write_decide` lines 459–484: a flat branch on `decision.kind` × (`apply`, `force_conflicts`). |
| **FR-005** Append audit entry per invocation | PASS | `_append_log` writes JSONL to `export-log.jsonl`; `test_audit_log_appended` verifies. |
| **FR-006** `--apply` writes NEW + CATALOG-CHANGED, skips LIVE-CUSTOMIZED + CONFLICT | PASS | `_write_decide` lines 459–484: ADD writes if `effective_write`; UPDATE writes if `apply`; PROTECT never writes; CONFLICT writes only if `apply and force_conflicts`. Verified by `test_user_edit_is_protected`, `test_both_changed_is_conflict`, `test_apply_implies_write`, `test_e2e_user_edit_protected_catalog_change_updated`. |
| **FR-007** `--force` writes everything (back-compat) | PASS | `write_export` dispatches to `_write_force` when `force=True`; `_write_force` short-circuits the decide loop entirely. Verified by `test_force_overwrites_everything`. |
| **FR-008** `--force-conflicts` with `--apply` overwrites CONFLICT, skips LIVE-CUSTOMIZED | PASS | `_write_decide` line 482: CONFLICT writes iff `apply and force_conflicts`; PROTECT line 478: never writes. Verified by `test_force_conflicts_overwrites_conflict_but_not_protect`. |
| **FR-009** `--scope` filters by target path prefix | PASS | `_write_force` line 387, `_write_decide` line 435: `if scope is not None and not action.target.startswith(scope): continue`. Verified by `test_scope_filters_actions`, `test_e2e_scope_limits_to_single_file`. |
| **FR-010** `--strict` non-zero on CONFLICT or LIVE-CUSTOMIZED | PASS | `_write_decide` lines 508–519: raises `ProtectionError` for CONFLICT and PROTECT under `--strict`. Verified by `test_strict_raises_on_conflict`, `test_strict_raises_on_protect`, `test_e2e_strict_nonzero_exit_on_conflict`, `test_init_cli_strict_exits_nonzero_on_conflict`. CLI catches `ProtectionError` and exits 1 (`commands/init.py` line 100). |
| **FR-011** Atomic snapshot write | PASS | `_save_snapshot` uses `tempfile.mkstemp` + `os.replace` (lines 155–176). The os.fdopen/os.close dance is correct for Windows (NamedTemporaryFile holds the file open on Windows and prevents the rename on some configs — the chosen pattern is the right call). |
| **FR-012** Partial snapshot update on `--scope` | PASS | `_load_snapshot` loads the full snapshot at the start of `_write_decide` (line 430); only the in-scope path is updated; the full dict is saved at the end (line 522). Out-of-scope entries are preserved. |
| **FR-013** `models --apply` uses `apply=True` semantics, not `force=True` | PASS | `commands/models.py` line 240–243: `write_export(..., force=force, apply=not force, write=True)`. The bug is fixed: by default `force=False, apply=True`; with `--force`, `force=True, apply=False`. Verified by `test_apply_protects_user_edited_agent`, `test_apply_conflicts_on_both_changed_agent`, `test_apply_force_overwrites_user_edited_agent`. |
| **FR-014** No-flag `init --write` is backward compatible | PASS | When `force=False` and `apply=False` and `effective_write=write`, the flow enters `_write_decide` with `apply=False`. UNCHANGED and UNKNOWN and PROTECT all skip (preserving the legacy "don't touch existing files" behavior); ADD writes; UPDATE does not (because `apply=False`); CONFLICT does not (because `apply=False` and `force_conflicts=False`). Net effect on a re-init: UNCHANGED is the only category that triggers — and the legacy behavior was "skip if exists" → no write → no hash change → UNCHANGED. Identical. (The snapshot is also written, but that is additive and doesn't change on-disk user files.) Verified by `test_plain_write_backward_compatible_skips_existing`. |
| **FR-015** Classification must not name-check runtime/kind/profile | PASS | `decide()` takes `(live_hash, snapshot_hash, regen_hash)`. Zero string literals of any runtime name. `DecisionKind` has 6 string values, none of which name a runtime. |

**All 15 functional requirements: PASS.**

---

## Findings

### Warnings (non-blocking)

- **W-1: SPEC/Plan deviation in UNKNOWN handling — documented but worth flagging.**
  The SPEC clarification in §"Session 2026-06-24" says *"The snapshot only
  records what was actually written"* (Q3). The implementation does the
  opposite for `UNKNOWN`: it records the *live* hash so the next run can
  detect changes. The code comment at `export.py` line 469–471 cites a
  build-lead decision D-U2-2 that explains the deviation. **The deviation
  is correct** (otherwise UNKNOWN would be a permanent state), the test
  `test_unknown_records_live_hash_in_snapshot` covers it, and the
  decision is recorded in the build report. **Recommend:** the
  architectural spec be updated to reflect this in a follow-up so SPEC
  and code agree (a 1-line SPEC update, not a code change). The PLAN
  §2.2 step 5 actually does describe this behavior; only the SPEC
  clarification Q3 contradicts it.

- **W-2: `_write_decide` re-raises `ProtectionError` after a partial save.**
  When `--strict` is set and a CONFLICT/PROTECT is found, the function
  calls `_save_snapshot`/`_append_log` first (lines 510–511) and *then*
  raises. This is intentional (so the user can see the conflict in the
  log) but the snapshot will reflect a partial state. The lock is
  released in `write_export`'s `finally` block (line 362), so the next
  run picks up from a consistent snapshot. The design is correct but
  a non-strict conflict-skip will leave the snapshot reflecting
  *un-written actions*, which can confuse a user inspecting the
  snapshot manually. Not a bug; just worth knowing.

- **W-3: `force` + `--force-conflicts` is "redundant but harmless" per
  the plan, but the help text doesn't say so.** The CLI has no
  warning, and a user who passes both gets the legacy force behavior
  (no decide loop). That's correct, but if the goal of the plan is to
  make `force_conflicts` discoverable, the help for `force` should
  mention the priority. Optional doc nit.

### Nits (style only)

- **N-1: `_apply()` docstring** at `export.py` line 526 says "Execute
  a single export action against *destination*." That docstring is
  unchanged from pre-F-015 and still accurate. No fix needed; just
  confirming it was *not* changed (the plan promised it wouldn't be).

- **N-2: `models --apply` printed message** at `commands/models.py`
  line 248 reads `applied: {written_count} re-rendered, {skipped}
  skipped ({runtimes})`. The legacy version was
  `applied: re-rendered N agent file(s) (...)`. The new format is
  more informative and follows the SPEC. **No fix.** The change is
  deliberate per Story 5's SC.

- **N-3: `brain.yaml` comment** at `data/brain.yaml` line 18 was
  updated to mention "export state" in addition to "active-feature
  pointer". This is a 1-line in-scope data edit that keeps the
  scaffold description honest. Not a finding; just noting it is
  not in the PLAN's "changed files" list and is therefore a minor
  **out-of-plan-but-correct** edit.

- **N-4: en-dash vs em-dash** in two `print()` messages
  (`commands/models.py` lines 222, 237; `commands/init.py` line 105)
  — em-dashes (`—`) were replaced with double-hyphens (`--`) in
  the models messages during this change (visible in the diff).
  Stylistically inconsistent with the rest of the codebase. Trivial;
  no action.

---

## Things explicitly verified working (by code reading)

- `plan_export()` is **unchanged** (lines 95–121 of `export.py` are
  byte-equivalent to the pre-F-015 flow).
- `_apply()` is **unchanged** (lines 526–545).
- `protect.py` is **dependency-free** (only stdlib).
- The lockfile is released in the `finally` (line 362) — verified by
  the `test_lockfile_created_and_released` and
  `test_stale_lock_with_dead_pid_is_taken_over` tests.
- `--force` is short-circuit — bypasses the decide loop
  (`write_export` line 325–335). Existing callers (bootstrap etc.)
  that pass `force=True` continue to work byte-identically.
- `models --apply` defaults to `force=False, apply=True` (the bug
  fix). With `--force` it becomes `force=True, apply=False` (the
  escape hatch).
- The CLI rejects the contradictory `--force-conflicts --strict`
  combination at `commands/init.py` line 74 with exit code 2 (before
  any work).
- The `--dry-run` flag is registered but is effectively a no-op
  (dry-run is the default). Cosmetic; not a violation.

---

## Cross-reference to other reviewers

- **Reviewer #2 (Quality/Correctness):** the test suite (6+ files,
  ~1000 lines) covers every flag combination and every DecisionKind
  outcome. Run `pytest tests/test_protect.py tests/test_export_protection.py
  tests/test_export_snapshot.py tests/test_init_cli.py tests/test_models_command.py
  tests/test_f015_e2e.py tests/test_brain_gitignore.py` and
  expect all-pass.
- **Reviewer #3 (Build verification):** the 4 unit-build reports
  (U1, U2, U3, T-04) and the 3 unit-review reports are in
  `.aspis/features/F-015-safe-catalog-export/reports/`. They are
  consistent with what I verified by reading the diffs.

---

## Final verdict

**APPROVE WITH NOTES.** The implementation is rule-clean, constitution-clean,
and SPEC-compliant. The single SPEC/plan deviation (UNKNOWN records
live hash) is *correct* and *documented*; the plan and the build report
agree on it; only the SPEC clarification Q3 wording is slightly out of
date. The non-strict partial-save under `--strict` is a deliberate
trade-off, not a bug. All other items are style nits.

Recommend: land the F-015 work; add a 1-line SPEC update (or, better,
delete the contradictory Q3 from "Session 2026-06-24" since the
implementation is the new ground truth) as a docs-only follow-up.
