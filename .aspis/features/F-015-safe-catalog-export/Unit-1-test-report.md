# F-015 Unit 1 — Test Gate Report: Pure protection engine

**Feature:** F-015 — Safe Catalog Export
**Unit:** 1 of 4 — Pure protection engine
**Branch:** `feature/F-015-safe-catalog-export`
**Date:** 2026-06-25
**Gate runner:** test-lead
**Gate verdict (first run):** **RED**

> **Re-gate addendum (2026-06-25, build-lead):** After the fixes documented in
> `Unit-1-build-report.md` §7, the build-lead re-ran the scoped gate:
> `uv run pytest tests/test_protect.py -x -q` → **45 passed, 0 failed**
> (JUnit XML: `tests=45 failures=0 errors=0 skipped=0 time=0.152`).
> **Current gate verdict: ✅ GREEN.** The RED analysis below is the historical
> first-gate record; the 5 failures it documents have all been resolved
> (test-file-only changes — `src/aspis/protect.py` was not modified).

---

## 1. Summary

| Metric | Value |
|---|---|
| Tests collected | **45** |
| Passed | **40** |
| Failed | **5** |
| Skipped | 0 |
| Duration | 0.23 s |
| Python | 3.12.13 |
| pytest | 9.1.0 |
| Platform | win32 |

**Gate command (executed):**
```
uv run pytest tests/test_protect.py -x -q
```

**Verdict:** RED. The Unit 1 gate cannot be declared GREEN.
Unit 1 cannot be declared done (R-002) until the failures below are resolved.
The full suite regression check was **not** run (per the gate protocol: only run if
Unit 1 passes first).

> **Note on test count discrepancy:** The build report's build report claims
> "38 tests" (build report §1, line 37). The actual collected count is **45**
> test methods across 6 test classes (15+5+6+8+7+4). The build report
> under-counted by 7; this is non-blocking but worth correcting in the
> build report.

---

## 2. Failures (5)

All 5 failures are in the test file `tests/test_protect.py`. The implementation
in `src/aspis/protect.py` was independently verified against `hashlib.sha256`
and the decision table — the code matches the PLAN §2.1 / §9 spec.

### F1. `tests/test_protect.py::TestSha256Text::test_known_abc` — TEST BUG

**Location:** line 27 (constant) → line 42 (assertion)

**Output:**
```
AssertionError: assert 'ba7816bf8f01...0ff61f20015ad' == 'ba7816bf8f01...0ff4f81565b8a'
  - 7a9cb410ff4f81565b8a
  + 7a9cb410ff61f20015ad
```

**Root cause:** The hardcoded test constant `SHA256_ABC` on line 27 is wrong.
The actual SHA-256 of `b"abc"` is:
`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`

The test's constant ends `...0ff4f81565b8a`; the correct constant ends
`...0ff61f20015ad`. One digit substring (`0ff4f81565b8a` → `0ff61f20015ad`)
is a hand-typed transcription error.

**Independent verification:**
```
$ python -c "import hashlib; print(hashlib.sha256(b'abc').hexdigest())"
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

The implementation is correct; the test's expected constant is wrong.

---

### F2. `tests/test_protect.py::TestSha256Text::test_leading_bom_stripped` — TEST BUG

**Location:** line 27 (constant) → line 64 (assertion)

**Output:** identical to F1 (same `SHA256_ABC` typo propagates).

**Root cause:** same wrong constant as F1.

---

### F3. `tests/test_protect.py::TestSha256Text::test_crlf_only_string_hashes_as_empty` — SPEC/IMPL MISMATCH

**Location:** line 77 (assertion)

**Output:**
```
AssertionError: assert '01ba4719c80b...f9805daca546b' == 'e3b0c44298fc...5991b7852b855'
  - e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  (expected: empty)
  + 01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b  (actual: hash of "\n")
```

**Root cause:** The test asserts that `sha256_text("\r\n")` should equal the
empty-string hash. The implementation in `protect.py` does
`text.replace("\r\n", "\n")`, so `"\r\n"` normalizes to `"\n"` (one byte),
whose hash is `01ba4719...`, not the empty-string hash
`e3b0c44298...`.

This is **not a simple test typo** — the test and the implementation disagree
on what CRLF-only should normalize to:

| Source | Says |
|---|---|
| PLAN §2.1 (line 63) — code block | `replace("\r\n", "\n")` |
| `src/aspis/protect.py` (line 70) | `text.replace("\r\n", "\n")` |
| `src/aspis/protect.py` docstring | "normalizing CRLF→LF" |
| Research T-5 (industry-patterns-verification.md line 795) | `sha256_text("\r\n\r\n") == expected_empty` |
| `tests/test_protect.py::test_crlf_only_string_hashes_as_empty` | `sha256_text("\r\n") == SHA256_EMPTY` |

**The build lead wrote code matching the PLAN and tests matching the
RESEARCH.** These two sources conflict on whether `\r\n`-only should hash as
empty or as `"\n"`.

**Decision needed from build-lead / reviewer (not the test lead):** choose
ONE behavior and update either the code or the test (and the docstring) so
they agree. The test lead is **not** picking this — the implications touch
Unit 2 (snapshot engine) and Unit 3 (write_export).

---

### F4. `tests/test_protect.py::TestSha256Bytes::test_known_bytes_abc` — TEST BUG

**Location:** line 27 (constant) → line 106 (assertion)

**Output:** identical to F1 (same `SHA256_ABC` typo propagates).

**Root cause:** same wrong constant as F1.

---

### F5. `tests/test_protect.py::TestPlanRuntime::test_full_six_way_mixture` — TEST SETUP BUG

**Location:** line 268 (assertion)

**Output:**
```
KeyError: 'add'
```

**Root cause:** The test asserts `result["add"].kind is DecisionKind.ADD`,
but the path `"add"` is **not present in any of the three input dicts**
(snapshot, live, regen). `plan_runtime` iterates over the **union of keys**,
so a key absent from all three dicts is absent from the result. Comments
on lines 252/259/266 explicitly say `"add"` is "deliberately absent" from
all three — but the test then asserts the result contains `"add"`. The
intent (testing the ADD case via `plan_runtime`) requires `"add"` to be
present in at least one input dict (typically `snapshot`, which gives
`live_hash=None` → ADD).

**Fix:** add `"add": H0` (any hash) to the `snapshot` dict. The result will
then include `"add"`, and the `decide(None, H0, None)` call will return ADD
(case 1 fires: `live_hash is None`).

---

## 3. Tests that PASSED (40) — independent confidence read

The 40 passing tests cover:

- **All 6 decision cases** (`TestDecideCases` — 6/6 pass)
- **All ordering edge cases** (`TestDecideOrdering` — 8/8 pass), including
  the two non-obvious cases the build report flags (case-1-before-case-3,
  case-2-before-case-3)
- **`plan_runtime` union semantics** for 5 of 6 paths; only the "add" path
  setup is broken
- **`summary` aggregation** (4/4 pass)
- **CRLF→LF normalization** for non-empty text (4/4 pass):
  `test_crlf_normalized_to_lf`, `test_crlf_matches_explicit_lf`,
  `test_multiple_crlf_all_normalized`, `test_bom_plus_crlf_combined`
- **Bare-CR preservation** (`test_bare_cr_not_normalized` — pass)
- **BOM strip leading only** (`test_trailing_bom_not_stripped` — pass)
- **Unicode (CJK/accented/emoji) determinism** (3/3 pass)
- **`sha256_bytes` no-normalization, PNG header, empty, text/bytes
  agreement** (4/5 pass; the 5th fails only due to F4's wrong constant)

The implementation is sound. The 5 failures are all in the test file or in
the spec reconciliation.

---

## 4. Coverage

Coverage tooling (`pytest-cov`, `coverage`) is not installed in this
project. Coverage was **not** measured. A separate unit would need to add
`pytest-cov` to the dev deps. Out of scope for this gate.

The PLAN's gate criterion (TASKS.md line 45) is "100% branch coverage on
`decide()` and `sha256_text()`". This cannot be verified at this gate.

---

## 5. Reproduction

To reproduce the failures:
```
cd "P:\AI_Empire\Projects\Agentic Software Production System\ASPIS"
uv run pytest tests/test_protect.py -v --tb=short
```

---

## 6. Hand-back to build-lead

**5 failures, all in `tests/test_protect.py`.** Recommended fixes (the test
lead is not making the changes — build-lead owns the code/test authorship):

| # | Failure | Fix |
|---|---|---|
| F1, F2, F4 | Wrong `SHA256_ABC` constant on line 27 | Replace the constant with the actual SHA-256 of `b"abc"`: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` (1-line fix; 3 tests go green) |
| F3 | CRLF-only vs empty-hash mismatch | **Reconcile PLAN §2.1 with Research T-5** — pick one behavior. Option A: change `replace("\r\n", "\n")` to also strip trailing newlines (e.g., `text.replace("\r\n", "").replace("\n", "")` — NO, this breaks the "line1\nline2" case). Option B: change test to `assert sha256_text("\r\n") == hashlib.sha256(b"\n").hexdigest()`. The PLAN's CRLF→LF wording supports B. Update the docstring if B is chosen. |
| F5 | Missing `"add"` key in `test_full_six_way_mixture` setup | Add `"add": H0` to the `snapshot` dict (line 247). The path will then resolve to ADD via `live_hash=None`. |

After fixes, re-run:
```
uv run pytest tests/test_protect.py -v
```

If green, run the full suite:
```
uv run pytest -q
```

---

## 7. Gate verdict

**RED** — Unit 1 gate is **NOT GREEN**. 5 of 45 tests fail. All failures are
in `tests/test_protect.py` (test-author errors, plus one spec-reconciliation
item). The implementation in `src/aspis/protect.py` is correct against
`hashlib` standards and the PLAN §2.1 / §9 spec.

**Status:** handed back to build-lead for fixes. Not committed. Review
cannot proceed meaningfully (R-005 requires passing-test evidence).
