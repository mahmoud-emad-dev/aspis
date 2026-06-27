# F-017 L2-P1 Build Report

**Date:** 2026-06-27
**Phase:** 4 (L2-P1) + 5 (Polish)
**Tasks:** T-51 through T-55
**Branch:** `feature/F-017-complete-agent-system`

## Task summary

### T-51 — validate-index CLI verb
- **File:** `src/aspis/commands/validate_index.py` (new)
- **Status:** Complete
- Verifies `FILE_REGISTRY.yaml` entries resolve to real files and `CODE_MAP.md` line counts are within 10% of actual.
- Registered in `COMMAND_MODULES`; supports `--dry-run`.
- Exits 0 when fresh, 1 when stale.

### T-52 — drift CLI verb
- **File:** `src/aspis/commands/drift.py` (new)
- **Status:** Complete
- Per-field per-agent catalog↔live frontmatter drift detection.
- When no live runtime exists, reports "no live runtime — run aspis export first" and exits 0.
- Reuses `split_frontmatter` from `aspis.catalog` (same parse path as `byte_parity`).
- Registered in `COMMAND_MODULES`; supports `--runtime` scoping.

### T-53 — governance completion
- **File:** `src/aspis/commands/governance.py` (modified)
- **Status:** Complete
- All 6 subcommands (request, approve, audit, revoke, check, ledger) were already fully implemented.
- Added `--pretty` flag to `ledger` subcommand for YAML dump output.
- Added lock-state reporting (`held`/`free`) to `ledger` summary.

### T-54 — edge cases
- **Files:** 8 lead agent bodies (modified)
- **Status:** Complete
- Added `## Edge Cases` section with 2 scenarios each to all 8 lead bodies:
  - project-lead: Delegation Loop, Concurrent Request
  - planning-lead: Stuck on Ambiguous Request, Mode Mismatch
  - build-lead: Builder Timeout, Packet Impossible
  - reviewer: Same-Model Contamination, No-Evidence Verdict
  - system-lead: Self-Modification Guard, Export Conflict
  - fix-lead: Cannot Reproduce, Scope Expansion
  - test-lead: Flaky Classification, Environment Issues
  - research-lead: Cache Staleness, Source Authority Conflict

### T-55 — final sweep
- **Status:** Complete
- All systemic gates pass:
  - `validate-runtime --runtime all`: 12/12 agents PASS, 0 failures
  - `byte-parity --dry-run`: exit 0 CLEAN
  - `export --dry-run`: exit 0 OK
- TASKS.md boxes flipped to `[x]`.
- RECENT_CHANGES.md updated.
- This BUILD_REPORT.md written.

## Gate results

| Gate | Result |
|------|--------|
| `aspis validate-runtime --runtime all` | 12/12 PASS |
| `aspis byte-parity --dry-run` | CLEAN |
| `aspis export --dry-run` | OK |
| 0 broken skill refs | VERIFIED (validate-runtime) |
| 0 orphan delegates | VERIFIED (validate-runtime) |

## Files changed

| File | Action |
|------|--------|
| `src/aspis/commands/validate_index.py` | New (T-51) |
| `src/aspis/commands/drift.py` | New (T-52) |
| `src/aspis/commands/__init__.py` | Modified (+T-51/T-52 registrations) |
| `src/aspis/commands/governance.py` | Modified (+--pretty, lock-state) |
| `src/aspis/data/catalog/agents/project-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/planning-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/build-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/reviewer.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/system-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/fix-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/test-lead.md` | Modified (+Edge Cases) |
| `src/aspis/data/catalog/agents/research-lead.md` | Modified (+Edge Cases) |
| `.aspis/features/F-017-complete-agent-system/TASKS.md` | Modified (boxes flipped) |
| `.aspis/context/RECENT_CHANGES.md` | Modified (entry added) |

## Phase 4 checkpoint: CLEAR ✓

All L2-P1 tasks complete. System passes all validation gates. Ready for Phase 5 (Polish — final acceptance) or owner review.
