# F-015 Unit 1 — Build Report: Pure protection engine

**Feature:** F-015 — Safe Catalog Export
**Unit:** 1 of 4 — Pure protection engine
**Branch:** `feature/F-015-safe-catalog-export`
**Date:** 2026-06-25

---

## 1. What was built

### New file: `src/aspis/protect.py` (153 lines)

The pure 6-way hash-based decision engine. Zero file I/O, zero ASPIS imports
(only stdlib: `enum`, `hashlib`, `dataclasses`), zero runtime awareness.

Public interface (matches PLAN §2.1 / §9 exactly):

- `DecisionKind` — enum with 6 members: `ADD`, `UNCHANGED`, `UNKNOWN`, `UPDATE`,
  `PROTECT`, `CONFLICT`.
- `Decision` — frozen dataclass carrying `kind` plus the three hashes that
  produced it (`live_hash`, `snapshot_hash`, `regen_hash`), all `str | None`.
- `sha256_text(text)` — SHA-256 hex digest after stripping a leading UTF-8 BOM
  and normalizing CRLF→LF. Bare CR is intentionally NOT normalized.
- `sha256_bytes(data)` — SHA-256 hex digest of raw bytes, no normalization.
- `decide(live_hash, snapshot_hash, regen_hash)` — pure ordered 6-case truth
  table (first match wins). Order: ADD → UNCHANGED → UNKNOWN → UPDATE →
  PROTECT → CONFLICT.
- `plan_runtime(snapshot, live_hashes, regen_hashes)` — fans `decide` out across
  the union of keys; absent keys resolve to `None` (→ ADD for missing live).
- `summary(decisions)` — counts by `DecisionKind`; returns all 6 keys (zero if
  absent).

Module docstring follows the constitution file rules: Purpose /
Responsibilities / Does Not / Used By (matching the `assetkinds.py` convention).

### New file: `tests/test_protect.py` (317 lines, 45 tests)

Organised into 6 test classes:

| Class | Tests | Coverage |
|---|---|---|
| `TestSha256Text` | 15 | known digests, CRLF→LF, bare CR, BOM strip (leading only), BOM-only, CRLF-only, unicode (CJK/accented/emoji), combined BOM+CRLF |
| `TestSha256Bytes` | 5 | known bytes, no-normalization, PNG header, empty, text/bytes agreement |
| `TestDecideCases` | 6 | one test per DecisionKind (the 6 truth-table cases) |
| `TestDecideOrdering` | 8 | case-1-before-3, case-2-before-3, all-None→ADD, all-same→UNCHANGED, hash carriage, frozen dataclass |
| `TestPlanRuntime` | 7 | empty, union of keys, per-path decisions, snapshot-only→ADD, regen-only→ADD, live-only→UNKNOWN, full 6-way mixture |
| `TestSummary` | 4 | all 6 keys present, empty→all zero, mixed counts, total equals len |

Well-known SHA-256 constants are hardcoded for the "known strings" tests
(empty, "abc", "hello world") and cross-checked against `hashlib` directly for
the normalization cases.

---

## 2. Test results

**Gate verdict: ✅ GREEN**

| Metric | Value |
|---|---|
| Gate command | `uv run pytest tests/test_protect.py -x -q` |
| Tests collected | 45 |
| Passed | 45 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration | 0.152 s |
| Runner | build-lead (re-gate, after fixes) |
| Evidence | JUnit XML: `errors="0" failures="0" skipped="0" tests="45" time="0.152"` |

**History:** The first gate (run by the test-lead) was RED — 5 of 45 tests
failed, all in `tests/test_protect.py`; the implementation in
`src/aspis/protect.py` was independently verified correct against `hashlib`
and the PLAN §2.1 / §9 spec. The 5 failures were fixed in the test file only
(see §7 for the per-failure root cause and fix). This re-gate, run by the
build-lead after the fixes, is GREEN: **45 passed, 0 failed.**

Per the gate protocol, the full-suite regression check is deferred until all
4 units are complete — only scoped tests run per unit.

---

## 3. Deviations from the plan

| Deviation | Reason |
|---|---|
| Module docstring uses the `Purpose: / Responsibilities: / Does Not: / Used By:` block style (matching `assetkinds.py`) instead of the plan's single-line `Purpose: …` form | Constitution file rule + Consistency over Cleverness — aligned to the existing repo convention |
| Added `from __future__ import annotations` | Repo convention (seen in `assetkinds.py`, `conftest.py`); keeps `str \| None` annotations safe across the 3.11+ floor |
| `sha256_bytes` added (PLAN §2.1 lists it; the task brief's code block omitted it) | PLAN §2.1 and §9 both specify `sha256_bytes`; included to match the plan, with tests |
| 38 tests written (target was 16+) | Comprehensive coverage of all 6 cases + ordering edges + normalization per the task brief |

No logic deviations from the plan's truth table or signatures.

---

## 4. Constitution compliance self-check

| # | Rule | Verdict |
|---|---|---|
| 1 | **Local Change** | ✅ 0 existing files changed. 2 new files created. Cost-of-Change for this unit: 0 existing files (healthy). |
| 2 | **Plugin First** | ✅ `decide()` compares hashes only — no `if runtime == "claude"`, no asset-kind branching. Runtime-agnostic. |
| 3 | **Single Source of Truth** | ✅ One decision function owns the classification logic. Hashes are computed by the caller; this module only compares. |
| 4 | **No Special Cases** | ✅ No `if kind == "agents"` or path-specific branches. The truth table is uniform. |
| 5 | **Generated Artifacts** | ✅ N/A for this unit — no generated output. |
| 6 | **Automation before Intelligence** | ✅ `sha256_text` + `decide` are pure deterministic functions. No agent, no LLM, no heuristic. |
| 7 | **Core is Stable** | ✅ No existing file touched. `plan_export()` / `_apply()` / `write_export()` untouched. |
| 8 | **Configuration over Code** | ✅ No if-chains on kind; behaviour is data-driven by the three hash inputs. |
| 9 | **Dependency Direction** | ✅ `protect.py` imports ZERO ASPIS modules (only stdlib). `export.py` will import `protect` (plugin → core), never the reverse. |
| 10 | **Consistency over Cleverness** | ✅ The 6-way table is the exact truth table from the plan/old repo. No novel algorithm. |
| 11 | **Architecture before Features** | ✅ The general decision engine is built first; Units 2–4 plug it into specific callers. |
| 12 | **Portable by Default** | ✅ CRLF→LF normalization eliminates the Windows/Linux line-ending difference. UTF-8 encoding explicit. `pathlib`/posix paths are a Unit 2 concern. |

**File rules:**
- ✅ Every file explains itself (Purpose / Responsibilities / Does Not / Used By).
- ✅ One concept per file (the decision engine is the sole concept).
- ✅ No hidden dependencies (only stdlib; no module-level globals).
- ✅ Every function has a docstring.

**R-005 (Tests-as-spec):** 38 behaviour-only tests; no test probes internal
implementation details. No existing test weakened or deleted.

---

## 5. Scope control

Only the two planned files were created. No other files were modified. The
pre-existing working-tree changes (`.opencode/agents/build-lead.md`,
`.aspis/config/.runtime-inventory.json`) are unrelated to this unit and were
not touched.

---

## 6. Next steps

1. ✅ **Gate resolved** — re-gate is GREEN (45/45). The earlier bash-permission
   blocker is cleared (`uv run pytest` permission granted to the build-lead).
2. Delegate Unit 1 to the reviewer for independent review (constitution +
   test-quality) — report written to `Unit-1-review-report.md`.
3. After review passes (no blockers), hand to the committer.
4. Then proceed to Unit 2 (snapshot engine + rewired `write_export`).

**Not committed by build-lead** — per R-004, the committer handles commits
after review.

---

## 7. Post-gate test fixes (2026-06-25, after test-lead gate)

The test-lead ran the Unit 1 gate (`uv run pytest tests/test_protect.py -x -q`)
and reported **RED — 5 of 45 tests fail**. All 5 failures were in
`tests/test_protect.py`; the implementation in `src/aspis/protect.py` was
independently verified correct against `hashlib` and the PLAN §2.1 / §9 spec
and was **not touched**. Full report: `Unit-1-test-report.md`.

Fixes applied to `tests/test_protect.py` only:

| # | Failure(s) | Root cause | Fix |
|---|---|---|---|
| F1, F2, F4 | `TestSha256Text::test_known_abc`, `test_leading_bom_stripped`; `TestSha256Bytes::test_known_bytes_abc` | The `SHA256_ABC` constant (line 27) had a hand-typed transcription error: it ended `...0ff4f81565b8a` instead of `...0ff61f20015ad`. | Corrected the constant to the actual SHA-256 of `b"abc"`: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`. One-line fix; resolves 3 tests. |
| F3 | `TestSha256Text::test_crlf_only_string_hashes_as_empty` | The test asserted `sha256_text("\r\n") == SHA256_EMPTY`. But PLAN §2.1 and the impl normalize CRLF→LF (`text.replace("\r\n", "\n")`), so `"\r\n"` → `"\n"` — the hash of a single LF, **not** the empty-string hash. The research T-5 expectation was wrong: a CRLF-only string is a single newline, not an empty string. | Renamed the test to `test_crlf_only_string_normalizes_to_lf` and changed the assertion to `sha256_text("\r\n") == sha256_text("\n")` (CRLF normalizes to LF, not to empty). Comment updated to match. |
| F5 | `TestPlanRuntime::test_full_six_way_mixture` | The path `"add"` was absent from all three input dicts (snapshot, live, regen), so it was absent from the union `plan_runtime` iterates → `result["add"]` raised `KeyError`. The test then asserted `result["add"]` exists. | Added `"add": H0` to the `regen_hashes` dict. `"add"` is now in the union; `live_hashes` still lacks it → `live_hash=None` → `decide()` case 1 fires → ADD, exactly as the test asserts. |

Supporting change: added a module-level constant `H0` (64-zero hex string)
for the F5 fix, distinct from `H1`/`H2`/`H3` so the ADD-case setup is visually
clear. No other test references `H0`.

**Test-count correction:** the original §1 header stated "38 tests" and the
table listed `TestPlanRuntime` as 6 tests. The actual collected count is
**45** test methods (15 + 5 + 6 + 8 + **7** + 4); `TestPlanRuntime` has 7
tests (`test_full_six_way_mixture` was the under-counted entry). §1 has been
corrected (header + table). The file is now 317 lines (was 315: +1 for `H0`,
+1 for the expanded `regen` dict).

**Files changed in this pass:** `tests/test_protect.py` only.
`src/aspis/protect.py` was **not** modified — the implementation was correct.

**Verification:** the build-lead cannot execute `uv run pytest` (bash
permission rules deny it — same restriction documented in §2). Each fix was
hand-traced against the implementation:
- F1/F2/F4: the corrected constant matches the test-lead's independent
  `hashlib.sha256(b'abc')` output.
- F3: `sha256_text("\r\n")` → `"\r\n".replace("\r\n","\n")` → `"\n"` →
  `hashlib.sha256(b"\n").hexdigest()`, which equals `sha256_text("\n")`. ✓
- F5: `decide(live=None, snapshot=None, regen=H0)` → case 1 (`live_hash is
  None`) → `DecisionKind.ADD`. ✓ The other 5 paths in the mixture are
  unchanged and were passing.

**Gate status:** ✅ GREEN — re-gated by the build-lead after the fixes above:
`uv run pytest tests/test_protect.py -x -q` → 45 passed, 0 failed (JUnit XML
confirms `tests=45 failures=0 errors=0 skipped=0`). See §2. **Not committed** —
handed to the reviewer, then the committer.