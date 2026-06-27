# F-018 — Build Report

**Date:** _(filled after Phase B)_
**Phase:** B (Build)
**Tasks:** T-001 through T-048
**Branch:** `feature/F-018-complete-asset-set`

---

## Task summary

### Layer 0 — Green pytest gate

| Task | Description | Status | Notes |
|------|-------------|--------|-------|
| T-001 | Fix Windows 3.14 subprocess failures | _ | _ |
| T-002 | Reconcile model-tier test expectations | _ | _ |
| T-003 | Fix promotion logic edge cases | _ | _ |
| T-004 | Reconcile "three rule layers" (D-006) assertions | _ | _ |
| T-005 | L0 exit gate: full pytest + ruff sweep | _ | _ |

### Layer 1 — Tier-B helper scripts

| Task | Script | Status | Notes |
|------|--------|--------|-------|
| T-006 | `scope_estimate.py` | _ | _ |
| T-007 | `constitution_check.py` | _ | _ |
| T-008 | `plan_quality_check.py` | _ | _ |
| T-009 | `mode_validator.py` | _ | _ |
| T-010 | `task_size_check.py` | _ | _ |
| T-011 | `dependency_graph.py` | _ | _ |
| T-012 | `search_cache.py` | _ | _ |
| T-013 | `check_staleness.py` | _ | _ |
| T-014 | `rank_source.py` | _ | _ |
| T-015 | `compare_versions.py` | _ | _ |
| T-016 | `cross_ref.py` | _ | _ |
| T-017 | L1 exit gate: byte-parity + AST + smoke | _ | _ |

### Layer 2 — Remaining skill + templates + workflow

| Task | Asset | Status | Notes |
|------|-------|--------|-------|
| T-018 | `dependency-audit` skill | _ | _ |
| T-019 | 7 templates (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, TEST_REPORT) | _ | _ |
| T-020 | project-lead operating-protocol workflow | _ | _ |
| T-020g | L2 exit gate | _ | _ |

### Layer 3 — Leaf subagents

| Task | Subagent | Status | Notes |
|------|----------|--------|-------|
| **System-lead** ||||
| T-021 | `runtime-validator` | _ | _ |
| T-022 | `drift-auditor` | _ | _ |
| T-023 | `permission-auditor` | _ | _ |
| T-024 | `export-verifier` | _ | _ |
| T-025 | `catalog-synchronizer` | _ | _ |
| T-026 | `opencode-author` | _ | _ |
| T-027 | `claude-author` | _ | _ |
| **Planning-lead** ||||
| T-028 | `clarify` | _ | _ |
| T-029 | `task-decomposer` | _ | _ |
| T-030 | `constitution-checker` | _ | _ |
| T-031 | `idea-capture` | _ | _ |
| T-032 | `prd-writer` | _ | _ |
| T-033 | `scope-estimator` | _ | _ |
| T-034 | `research-request-writer` | _ | _ |
| T-035 | `dependency-analyzer` | _ | _ |
| **Test-lead** ||||
| T-036 | `python-tester` | _ | _ |
| T-037 | `api-tester` | _ | _ |
| T-038 | `db-tester` | _ | _ |
| T-039 | `ui-tester` | _ | _ |
| T-040 | `cli-tester` | _ | _ |
| T-041 | `security-tester` | _ | _ |
| **Wiring + gate** ||||
| T-042 | Wire delegates in owning leads | _ | _ |
| T-043 | L3 exit gate: validate-runtime for 33 agents | _ | _ |

### Layer 4 — Hardening

| Task | Description | Status | Notes |
|------|-------------|--------|-------|
| T-044 | Claude PreToolUse hook in `.claude/settings.json` | _ | _ |
| T-045 | Edge-case sections for all bodies | _ | _ |
| T-046 | Cross-runtime parity verification | _ | _ |
| T-047 | L4 full gate sweep | _ | _ |
| T-048 | Stamp BUILD_REPORT + final acceptance | _ | _ |

---

## Gate results

| Gate | Layer | Result | Detail |
|------|-------|--------|--------|
| `pytest` | L0 | _ | _ |
| `ruff format --check .` | L0 | _ | _ |
| `ruff check .` | L0 | _ | _ |
| 11 scripts AST + `--help` | L1 | _ | _ |
| 11 scripts byte-parity | L1 | _ | _ |
| `validate-runtime --runtime all` | L2 | _ | _ |
| `validate-runtime --runtime all` (33 agents) | L3 | _ | _ |
| `byte-parity --dry-run` | L3 | _ | _ |
| `validate-index` | L3 | _ | _ |
| Claude PreToolUse hook valid JSON | L4 | _ | _ |
| `aspis byte-parity --runtime claude` | L4 | _ | _ |
| `aspis export --dry-run` | L4 | _ | _ |
| `aspis doctor` | L4 | _ | _ |
| Full pytest + ruff (final) | L4 | _ | _ |

---

## Acceptance criteria verification

| SC | Description | Status | Evidence |
|----|-------------|--------|----------|
| SC-L0-001 | pytest exit 0 on all platforms | _ | _ |
| SC-L0-002 | ruff format+check exit 0 | _ | _ |
| SC-L1-001 | 11 scripts pass AST + --help + smoke | _ | _ |
| SC-L1-002 | Byte-parity verified for all scripts | _ | _ |
| SC-L2-001 | dependency-audit SKILL.md valid | _ | _ |
| SC-L2-002 | 7 templates exist with correct frontmatter | _ | _ |
| SC-L2-003 | project-lead workflow has ≥60 steps | _ | _ |
| SC-L3-001 | 21+ new subagents exist as catalog files | _ | _ |
| SC-L3-002 | validate-runtime green for all 33 agents | _ | _ |
| SC-L3-003 | 0 broken skill references | _ | _ |
| SC-L3-004 | 0 orphan delegates | _ | _ |
| SC-L3-005 | 0 agents with bash: '*': allow | _ | _ |
| SC-L4-001 | Claude PreToolUse hook configured | _ | _ |
| SC-L4-002 | Every agent has ≥2 edge cases | _ | _ |
| SC-L4-003 | byte-parity CLEAN | _ | _ |
| SC-L4-004 | aspis export --dry-run exits 0 | _ | _ |
| SC-L4-005 | aspis doctor exits 0 | _ | _ |
| SC-CC-001 | Cost-of-change ≤3 files per new asset | _ | _ |

---

## Files changed

| File | Action | Task |
|------|--------|------|
| _(filled after build)_ | _ | _ |

---

## Phase B checkpoint: _ (filled after build)

_(Summary of build completion state.)_
