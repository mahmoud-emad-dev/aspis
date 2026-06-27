# F-018 L1 Gate Report

> **Date:** 2026-06-27
> **Gate:** L1 exit gate (T-016)
> **Result:** PASS

## Summary

All 12 Tier-B helper scripts built, deployed, tested, and verified.

| Metric | Result |
|--------|--------|
| Scripts built | 12/12 |
| AST parse | 12 PASS |
| `--help` exit 0 | 12 PASS |
| Byte-parity | 12 PASS |
| Tests passing | 59/59 |
| Debris cleaned | CLEAN (none found) |

## Per-Script Results

### Planning Scripts (6)

| Script | AST | --help | Parity | Tests |
|--------|-----|--------|--------|-------|
| `scope_estimate.py` | OK | exit=0 | OK | 5/5 |
| `constitution_check.py` | OK | exit=0 | OK | 3/3 |
| `plan_quality_check.py` | OK | exit=0 | OK | 4/4 |
| `mode_validator.py` | OK | exit=0 | OK | 6/6 |
| `task_size_check.py` | OK | exit=0 | OK | 4/4 |
| `dependency_graph.py` | OK | exit=0 | OK | 5/5 |

### Research Scripts (5)

| Script | AST | --help | Parity | Tests |
|--------|-----|--------|--------|-------|
| `search_cache.py` | OK | exit=0 | OK | 5/5 |
| `check_staleness.py` | OK | exit=0 | OK | 6/6 |
| `rank_source.py` | OK | exit=0 | OK | 4/4 |
| `compare_versions.py` | OK | exit=0 | OK | 8/8 |
| `cross_ref.py` | OK | exit=0 | OK | 4/4 |

### Governance Script (1)

| Script | AST | --help | Parity | Tests |
|--------|-----|--------|--------|-------|
| `validate-approvals.py` | OK | exit=0 | OK | 5/5 |

## FR-L1 Compliance

- **FR-L1-001** (all 12 scripts exist): PASS — catalog at `src/aspis/data/catalog/scripts/`, deployed at `.aspis/scripts/`
- **FR-L1-002** (deterministic, stdlib-only): PASS — no network, no LLM, pure Python stdlib
- **FR-L1-003** (AST parse): PASS — all 12 parse clean
- **FR-L1-004** (--help exit 0): PASS — all 12 return usage info with exit 0
- **FR-L1-005** (byte-identical): PASS — verified with filecmp across all 12
- **FR-L1-006** (planning scripts location): PASS — `.aspis/scripts/planning/`
- **FR-L1-007** (research scripts location): PASS — `.aspis/scripts/research/`
- **FR-L1-008** (governance script location): PASS — `.aspis/scripts/system/`
- **FR-L1-009** (debris removed): PASS — no `_tmp_f017_*.py` found

## Debris Check (T-015)

`glob **/_tmp_f017_*.py` returned no files. CLEAN.

## Test Evidence

```
uv run pytest tests/unit/test_scripts/ -v
============================= 59 passed in 12.95s =============================
```

Full test output captured. 59 tests across 12 test files, all passing.

## Notes

- All scripts are stdlib-only except `mode_validator.py` and `validate-approvals.py` which have PyYAML fallback to JSON parsing.
- Unicode characters replaced with ASCII equivalents for Windows cp1252 compatibility (→ → ->, ✓ → [OK], ⚠ → [WARN]).
- `validate-approvals.py` is the P0 R-008 enforcement script — the single most critical validator. Remaining 7 CLI validators deferred to F-019 per spec.

## Verdict: PASS

All L1 requirements satisfied. Ready for L2.
