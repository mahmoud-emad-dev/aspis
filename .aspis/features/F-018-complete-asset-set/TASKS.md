# F-018 — Tasks

> Mode: production
> Total tasks: 51
> Critical path: L0 (T-001a→T-002) → L1 (T-003→T-016) → L2 (T-017→T-020) → L3 (T-021→T-043) → L4 (T-044→T-050)
> Convention: suffix letters (a/b/c) denote task splits from A1 review conditions. Letter-suffixed tasks are sequential within their group.

---

## Layer 0 — Green pytest gate (3 tasks)
*Blocked by: nothing. Makes every downstream gate trustworthy.*

### L0.A — Discovery (1)

- [x] T-001a [P0] [high] [moderate] [verify] — Discovery sweep: run pytest, capture ALL failures, write evidence report
  - Files: `L0_DISCOVERY_REPORT.md` (new, in feature dir)
  - Action: Run `pytest` or `python -m pytest --no-header -q 2>&1`. If subprocess capture blocks on this env, fallback to `python -m pytest --no-header -q 2>&1 | Select-String FAILED` (or grep equivalent). Capture EVERY failure with file:line, stack trace, and failure class.
  - At minimum: all non-subprocess tests must pass. Subprocess-blocked tests documented with `BLOCKED: env` and rationale.
  - Depends on: none | Blocks: T-001b [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+evidence
  - Acceptance: discovery report written; every failure traced to file:line; no speculative/narrative failures listed; blocked items marked `BLOCKED: env`

### L0.B — Evidence-driven fix (only confirmed failures)

- [x] T-001b [P0] [high] [moderate] [fix] — Fix real test failures (evidence-driven from T-001a report)
  - Files: `tests/**` (modify), `src/aspis/**` (fix if root cause in source)
  - Fix only failure classes CONFIRMED by T-001a report. Each class fixed with root-cause evidence:
    - Windows subprocess failures (only if confirmed — `encoding='utf-8'`, `shell=False`, pathlib)
    - Model-tier reconciliation (only if confirmed — match catalog `model_catalog.yaml` / `agent-models.yaml`)
    - Promotion logic (only if confirmed — bootstrap promotion, mode=N/A, 5 primaries only)
    - Rule-layer assertions / D-006 (only if confirmed)
  - Any failure class NOT in the discovery report → mark "no-op — not reproducible" with evidence.
  - Key: `validate_index.py:180` already has `10%%` (correctly escaped); do not assume a crash.
  - Depends on: T-001a [hard] | Blocks: T-002 [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope+evidence
  - Acceptance: every CONFIRMED failure fixed; unconfirmed classes documented as no-op; no speculative fixes

### L0.C — Gate

- [x] T-002 [P0] [high] [simple] [verify] — L0 exit gate: full pytest + ruff sweep
  - Files: `L0_GATE_REPORT.txt` (new, capture in feature dir)
  - Run: `pytest` exit 0 (or all non-subprocess pass + blocked items documented).
  - Run: `ruff format --check .` exit 0; `ruff check .` exit 0.
  - Capture output to `L0_GATE_REPORT.txt` as evidence.
  - Depends on: T-001b [hard] | Blocks: L1 entry [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: pytest exit 0 (or all non-subprocess pass + BLOCKED: env documented); ruff exit 0; report written

---

## Layer 1 — Tier-B helper scripts + debris cleanup (14 tasks)
*Blocked by: L0 green. R-003: scripts before agents.*

### L1.A — Planning scripts (6)

- [x] T-003 [P1] [medium] [moderate] [feature] — Build and deploy `scope_estimate.py`
  - Files: `src/aspis/data/catalog/scripts/planning/scope_estimate.py` (new), `.aspis/scripts/planning/scope_estimate.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-004 [P1] [medium] [moderate] [feature] — Build and deploy `constitution_check.py`
  - Files: `src/aspis/data/catalog/scripts/planning/constitution_check.py` (new), `.aspis/scripts/planning/constitution_check.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-005 [P1] [medium] [moderate] [feature] — Build and deploy `plan_quality_check.py`
  - Files: `src/aspis/data/catalog/scripts/planning/plan_quality_check.py` (new), `.aspis/scripts/planning/plan_quality_check.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-006 [P1] [medium] [moderate] [feature] — Build and deploy `mode_validator.py`
  - Files: `src/aspis/data/catalog/scripts/planning/mode_validator.py` (new), `.aspis/scripts/planning/mode_validator.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-007 [P1] [medium] [moderate] [feature] — Build and deploy `task_size_check.py`
  - Files: `src/aspis/data/catalog/scripts/planning/task_size_check.py` (new), `.aspis/scripts/planning/task_size_check.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-008 [P2] [medium] [moderate] [feature] — Build and deploy `dependency_graph.py`
  - Files: `src/aspis/data/catalog/scripts/planning/dependency_graph.py` (new), `.aspis/scripts/planning/dependency_graph.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

### L1.B — Research scripts (5)

- [x] T-009 [P1] [medium] [moderate] [feature] — Build and deploy `search_cache.py`
  - Files: `src/aspis/data/catalog/scripts/research/search_cache.py` (new), `.aspis/scripts/research/search_cache.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-010 [P1] [medium] [moderate] [feature] — Build and deploy `check_staleness.py`
  - Files: `src/aspis/data/catalog/scripts/research/check_staleness.py` (new), `.aspis/scripts/research/check_staleness.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-011 [P1] [medium] [moderate] [feature] — Build and deploy `rank_source.py`
  - Files: `src/aspis/data/catalog/scripts/research/rank_source.py` (new), `.aspis/scripts/research/rank_source.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-012 [P2] [medium] [moderate] [feature] — Build and deploy `compare_versions.py`
  - Files: `src/aspis/data/catalog/scripts/research/compare_versions.py` (new), `.aspis/scripts/research/compare_versions.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-013 [P2] [medium] [moderate] [feature] — Build and deploy `cross_ref.py`
  - Files: `src/aspis/data/catalog/scripts/research/cross_ref.py` (new), `.aspis/scripts/research/cross_ref.py` (deploy)
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

### L1.C — Governance script (1)

- [x] T-014 [P0] [medium] [moderate] [feature] — Build and deploy `validate-approvals.py`
  - Files: `src/aspis/data/catalog/scripts/system/validate-approvals.py` (new), `.aspis/scripts/system/validate-approvals.py` (deploy)
  - Purpose: R-008 ledger enforcement — checks `.aspis/approvals/` for missing/expired approvals on protected-path writes
  - Stdlib-only, deterministic. Input: ledger path + config. Output: per-approval pass/warn/fail → stdout.
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Note: this is the single most critical of the 8 missing CLI validators (gap P0 HIGH). The remaining 7 validators are deferred to F-019 per SPEC Out of scope.

### L1.D — Debris cleanup (1)

- [x] T-015 [P0] [medium] [simple] [fix] — Remove `_tmp_f017_*.py` debris from `.aspis/scripts/planning/`
  - Files: `.aspis/scripts/planning/_tmp_f017_*.py` (delete if any exist)
  - R-006 violation: these are build detritus, not catalog assets. They pollute byte-parity checks.
  - If no debris found: document "CLEAN — no debris" and pass.
  - Depends on: T-002 [hard] | Blocks: L1 gate [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: zero `_tmp_f017_*.py` files remain in `.aspis/scripts/planning/`

### L1.E — Gate (1)

- [x] T-016 [P0] [high] [simple] [verify] — L1 exit gate: byte-parity + AST + smoke for all 12 scripts
  - Files: none (verification only; fix any failures)
  - Verify: each deployed script byte-identical to catalog source; AST parse passes for all 12; `--help` exits 0 for all 12; debris confirmed clean.
  - Depends on: T-003..T-015 [hard] | Blocks: L2 entry [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: all 12 scripts pass AST parse + `--help` exit 0 + byte-parity from catalog; zero debris files

---

## Layer 2 — Remaining skill + templates + workflow (4 tasks)
*Blocked by: L1 green.*

- [x] T-017 [P2] [medium] [moderate] [feature] — Author `dependency-audit` skill
  - Files: `src/aspis/data/catalog/skills/dependency-audit/SKILL.md` (new)
  - Reference: planning-lead frontmatter (add `dependency-audit` to skills list)
  - Depends on: T-016 [hard] | Blocks: L2 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Acceptance: valid SKILL.md with 5 sections; planning-lead frontmatter references it

- [x] T-018 [P1] [medium] [moderate] [feature] — Author 7 missing templates
  - Files: `src/aspis/data/catalog/templates/planning/CLARIFICATION_LOG.md` (new), `RESEARCH_REQUEST.md` (new), `PLAN_OF_PLAN.md` (new), `DEPENDENCIES.md` (new), `SCOPE_ESTIMATE.md` (new), `MODE_DECISION.md` (new)
  - Note: TEST_REPORT already exists at `src/aspis/data/catalog/templates/review/test.md`. Extend or adopt that existing file rather than creating a duplicate at `templates/report/TEST_REPORT.md`.
  - Depends on: T-016 [hard] | Blocks: L2 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope (per-template review granularity)
  - Acceptance: all 6 new templates exist with correct frontmatter + structured body; TEST_REPORT path reconciled (extend existing or create with no duplicate)

- [x] T-019 [P0] [high] [complex] [feature] — Author project-lead operating-protocol workflow
  - Files: `.aspis/workflows/project-lead-operating-protocol.md` (new)
  - Reference: project-lead body "How you work" section (add workflow pointer)
  - Target: ≥60 numbered steps via 8 sections × ~8 steps each (see PLAN.md L2.3 for outline)
  - Depends on: T-016 [hard] | Blocks: L2 gate [hard]
  - Packet: V3 (deep) | Builder: standard | Review: reviewer, correctness+scope+architecture
  - Acceptance: ≥60 numbered steps; covers all 5 phases + 13 stop-and-ask + recontextualization + per-delegate profiles + human-gate + 10 flows

- [x] T-020 [P0] [high] [simple] [verify] — L2 exit gate: validate-runtime + completeness
  - Files: none (verification only)
  - Depends on: T-017, T-018, T-019 [hard] | Blocks: L3 entry [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: `validate-runtime --runtime all` clean; 0 broken refs; workflow has ≥60 steps; skill SKILL.md valid

---

## Layer 3 — Leaf subagents (23 tasks)
*Blocked by: L2 green. R-003 honoured: L1 scripts deployed, L2 skill+templates built.*

### L3.A — System-lead subagents (7)

- [x] T-021 [P1] [medium] [moderate] [feature] — Build `runtime-validator` subagent
  - Files: `src/aspis/data/catalog/agents/runtime-validator.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-022 [P1] [medium] [moderate] [feature] — Build `drift-auditor` subagent
  - Files: `src/aspis/data/catalog/agents/drift-auditor.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-023 [P1] [medium] [moderate] [feature] — Build `permission-auditor` subagent
  - Files: `src/aspis/data/catalog/agents/permission-auditor.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-024 [P2] [medium] [moderate] [feature] — Build `export-verifier` subagent
  - Files: `src/aspis/data/catalog/agents/export-verifier.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-025 [P2] [medium] [moderate] [feature] — Build `catalog-synchronizer` subagent
  - Files: `src/aspis/data/catalog/agents/catalog-synchronizer.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-026 [P2] [medium] [moderate] [feature] — Build `opencode-author` subagent
  - Files: `src/aspis/data/catalog/agents/opencode-author.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-027 [P2] [medium] [moderate] [feature] — Build `claude-author` subagent
  - Files: `src/aspis/data/catalog/agents/claude-author.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

### L3.B — Planning-lead subagents (8)

- [x] T-028 [P0] [medium] [moderate] [feature] — Build `clarify` subagent
  - Files: `src/aspis/data/catalog/agents/clarify.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-029 [P0] [medium] [moderate] [feature] — Build `task-decomposer` subagent
  - Files: `src/aspis/data/catalog/agents/task-decomposer.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-030 [P1] [medium] [moderate] [feature] — Build `constitution-checker` subagent
  - Files: `src/aspis/data/catalog/agents/constitution-checker.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Priority note: demoted from gap P0 to plan P1 — consumes L0-L2 outputs, no upstream dependencies; can ship in P1 batch

- [x] T-031 [P0] [medium] [moderate] [feature] — Build `idea-capture` subagent
  - Files: `src/aspis/data/catalog/agents/idea-capture.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-032 [P0] [medium] [moderate] [feature] — Build `prd-writer` subagent
  - Files: `src/aspis/data/catalog/agents/prd-writer.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-033 [P1] [medium] [moderate] [feature] — Build `scope-estimator` subagent
  - Files: `src/aspis/data/catalog/agents/scope-estimator.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-034 [P1] [medium] [moderate] [feature] — Build `research-request-writer` subagent
  - Files: `src/aspis/data/catalog/agents/research-request-writer.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-035 [P2] [medium] [moderate] [feature] — Build `dependency-analyzer` subagent
  - Files: `src/aspis/data/catalog/agents/dependency-analyzer.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

### L3.C — Test-lead stack-specific testers (6)

- [x] T-036 [P1] [medium] [moderate] [feature] — Build `python-tester` subagent
  - Files: `src/aspis/data/catalog/agents/python-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-037 [P2] [medium] [moderate] [feature] — Build `api-tester` subagent
  - Files: `src/aspis/data/catalog/agents/api-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-038 [P2] [medium] [moderate] [feature] — Build `db-tester` subagent
  - Files: `src/aspis/data/catalog/agents/db-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-039 [P2] [medium] [moderate] [feature] — Build `ui-tester` subagent
  - Files: `src/aspis/data/catalog/agents/ui-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-040 [P2] [medium] [moderate] [feature] — Build `cli-tester` subagent
  - Files: `src/aspis/data/catalog/agents/cli-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope

- [x] T-041 [P2] [medium] [moderate] [feature] — Build `security-tester` subagent
  - Files: `src/aspis/data/catalog/agents/security-tester.md` (new)
  - Depends on: T-020 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Note: `security-tester` (testing) is distinct from deferred `security-reviewer` (review); security surface is covered

### L3.D — Catalog wiring (1)

- [x] T-042 [P0] [medium] [complex] [feature] — Wire all 21 new subagents into owning leads' delegates + prose
  - Files: `src/aspis/data/catalog/agents/system-lead.md` (modify +7 delegates frontmatter + ## Delegation prose), `src/aspis/data/catalog/agents/planning-lead.md` (modify +8 delegates frontmatter + ## Delegation prose), `src/aspis/data/catalog/agents/test-lead.md` (modify +6 delegates frontmatter + ## Delegation prose)
  - Must update BOTH frontmatter `delegates:` AND the `## Delegation` prose section in each lead body (list each delegate with purpose and scope)
  - Depends on: T-021..T-041 [hard] | Blocks: L3 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Acceptance: all 21 subagents appear in frontmatter + prose of owning lead; 0 orphan delegates; cost-of-change ≤3 files per subagent verified

### L3.E — Gate (1)

- [x] T-043 [P0] [high] [simple] [verify] — L3 exit gate: validate-runtime for all 33 agents
  - Files: none (verification only; fix any failures)
  - Depends on: T-042 [hard] | Blocks: L4 entry [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: `validate-runtime --runtime all` exits 0; 0 broken skill refs; 0 orphan delegates; `byte-parity --dry-run` CLEAN

---

## Layer 4 — Hardening (7 tasks)
*Blocked by: L3 green.*

### L4.A — PreToolUse hook (3)

- [x] T-044 [P0] [high] [moderate] [feature] — Author PreToolUse hook modules
  - Files: `.aspis/scripts/hooks/` (new: scope check, secret scan, protected-path validation modules)
  - Each module: deterministic, stdlib-only, callable from Claude PreToolUse hook framework
  - Depends on: T-043 [hard] | Blocks: T-045 [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+security
  - Acceptance: all hook modules exist and pass AST parse; each module has documented purpose

- [x] T-045 [P0] [high] [simple] [governance] — File R-008 governance request for `.claude/settings.json` PreToolUse hook
  - Action: Use governance subagent `request` verb to file approval request for adding PreToolUse hook to `.claude/settings.json`
  - The proposed edit: hook entry referencing `.aspis/scripts/hooks/` modules, `enforcement: warn`, auto-fix enabled, non-blocking
  - Depends on: T-044 [hard] | Blocks: T-046 [hard] (blocks on owner approval)
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: governance request filed with evidence; approval pending owner action
  - **Note:** This is a permissions-change surface (R-008 gate). The settings.json edit is NOT applied until owner approves via governance subagent `approve` verb.

- [~] T-046 [P0] [high] [simple] [feature] — Apply `.claude/settings.json` PreToolUse hook (on owner approval)
  - Files: `.claude/settings.json` (modify — add PreToolUse hook entry)
  - Gate: owner must have approved the R-008 governance request from T-045 before this task executes
  - Configuration: `enforcement: warn`, auto-fix enabled, hook references resolve to existing `.aspis/scripts/hooks/` modules
  - Depends on: T-045 + owner approval [hard] | Blocks: L4 gate [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: `.claude/settings.json` is valid JSON; hook reference resolves; `enforcement: warn`
  - **Fallback:** If approval not yet granted at build time, leave hook modules in place, document manual edit as post-build owner action, mark task "BLOCKED: awaiting R-008 owner approval"

### L4.B — Edge cases (1)

- [x] T-047 [P1] [medium] [moderate] [feature] — Add edge-case sections to bodies that lack them
  - Files: `src/aspis/data/catalog/agents/committer.md` (modify), `general-builder.md` (modify), `project-explorer.md` (modify), `bootstrap.md` (modify — codify exception in AGENT_BODY_STANDARD.md first per L4-2 finding) + all 21 new subagent bodies (ensure ≥2 edge cases each)
  - Depends on: T-043 [hard] | Blocks: L4 gate [hard]
  - Packet: V2 (standard) | Builder: standard | Review: reviewer, correctness+scope
  - Acceptance: every agent body has ≥2 documented edge cases; bootstrap exception codified in standard

### L4.C — Cross-runtime parity (1)

- [x] T-048 [P1] [medium] [simple] [verify] — Verify cross-runtime parity (Claude permission block preservation)
  - Files: none (verification only; fix adapter if gap found)
  - First: check whether the defect exists — F-017 final-completeness.md L121 says FR-010 PASSED in commit 36ab7b5
  - Run: `aspis byte-parity --runtime claude --agent all`
  - Depends on: T-043 [hard] | Blocks: L4 gate [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: MUST produce explicit verdict — `"present-and-fixed"` (defect found, now fixed) or `"not-present"` (already resolved). No silent pass-through.

### L4.D — Gate sweep (2)

- [x] T-049 [P0] [high] [simple] [verify] — L4 full gate sweep
  - Files: none (verification only; fix any failures)
  - Depends on: T-046, T-047, T-048 [hard] | Blocks: T-050 [hard]
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: self
  - Acceptance: `pytest` exit 0; `validate-runtime --runtime all` exit 0; `byte-parity --dry-run` CLEAN; `validate-index` exit 0; `aspis export --dry-run` exit 0; `aspis doctor` exit 0

- [x] T-050 [P0] [high] [simple] [verify] — Stamp BUILD_REPORT + final acceptance
  - Files: `.aspis/features/F-018-complete-asset-set/BUILD_REPORT.md` (new)
  - Depends on: T-049 [hard] | Blocks: none (final)
  - Packet: V1 (light) | Builder: build-lead (direct) | Review: reviewer, correctness
  - Acceptance: every SC-### checked against evidence; BUILD_REPORT complete with gate results; feature ready for owner review

---

## Parallelism summary

| Group | Tasks | Can run in parallel? |
|-------|-------|---------------------|
| L1.A planning scripts | T-003..T-008 | Yes — all 6 in parallel |
| L1.B research scripts | T-009..T-013 | Yes — all 5 in parallel |
| L1.A + L1.B | — | Yes — both groups in parallel |
| L3.A system-lead subagents | T-021..T-027 | Yes — all 7 in parallel |
| L3.B planning-lead subagents | T-028..T-035 | Yes — all 8 in parallel |
| L3.C test-lead testers | T-036..T-041 | Yes — all 6 in parallel |
| L3.A + L3.B + L3.C | — | Yes — all 3 groups in parallel |

## Execution strategy

1. **L0 first** — discovery sweep (T-001a) then evidence-driven fix (T-001b) then gate (T-002). Nothing can proceed without a trustworthy test foundation.
2. **L1 in parallel groups** — planning scripts (T-003..T-008), research scripts (T-009..T-013), and validate-approvals (T-014) in parallel. Then debris cleanup (T-015). Then gate (T-016).
3. **L2 in parallel** — skill (T-017), templates (T-018), workflow (T-019) in parallel. Then gate (T-020).
4. **L3 in three parallel groups** — system-lead (7), planning-lead (8), test-lead (6) all in parallel. Then wire (T-042). Then gate (T-043).
5. **L4 sequentially** — hook modules (T-044) → governance request (T-045) → apply hook on approval (T-046) → edge cases (T-047) → parity verify (T-048) → gate sweep (T-049) → report (T-050).

**Review strategy:** Per-task review by reviewer (standard for V2, deep for V3, self for V1). Build-lead does direct-execution tasks (V1 gate tasks) itself — no subagent delegation.

## Priority demotion notes

Per A1 review Finding L3-1: `runtime-validator` (T-021), `drift-auditor` (T-022), `permission-auditor` (T-023), and `constitution-checker` (T-030) are gap P0 but plan P1. Rationale: these are auditors/validators that consume L0-L2 outputs and have no upstream dependencies blocking other work; they can safely ship in the P1 batch alongside the P0 subagents.
