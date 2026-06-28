# Test report — <feature-id> / <task-id>

> Filled by the tester/reviewer to record what was tested and the result, so a
> later task can reuse it instead of re-running unchanged tests (the test ledger).
> The header is stamped by `aspis artifact`; you fill the rest from real output.
> This is the single source for TEST_REPORT needs — no duplicate template exists.

- **Feature**: <feature-id> — <Feature Title>
- **Task**: <task-id>
- **Date**: <date>
- **Result**: <pass | fail | partial>

## Test execution summary

| Metric | Value |
|--------|-------|
| Total tests | <N> |
| Passed | <N> |
| Failed | <N> |
| Skipped | <N> |
| Blocked (env) | <N> |
| Duration | <s> |

## Pass / fail breakdown

<Per-module or per-class breakdown with counts. Paste the actual test runner
output — pytest summary, unittest result, or equivalent. Do not summarize;
copy-paste the real counts.>

```
<e.g.:>
tests/test_export.py .........                        [100%]
tests/test_validate.py ..FF..                         [ 40%]
FAILED tests/test_validate.py::test_runtime — AssertionError: ...
FAILED tests/test_validate.py::test_index — KeyError: 'missing_field'
```

## Coverage stats

<If coverage data is available. Mark "not collected" if the run didn't produce it.>

| Module | Statements | Missed | Coverage |
|--------|-----------|--------|----------|
| src/aspis/commands/export.py | 45 | 2 | 96% |
| src/aspis/commands/validate.py | 120 | 8 | 93% |
| ... | | | |
| **TOTAL** | <N> | <N> | <N>% |

## Scope tested
<Which modules / behaviours this run covered.>

## Result
<The gate / suite output — counts and any failures, pasted not summarised.>

## Follow-ups
<Flaky tests, gaps, or cases deferred.>
