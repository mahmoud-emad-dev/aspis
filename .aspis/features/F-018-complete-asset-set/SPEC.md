# F-018 — Complete the Asset Set & Harden to a Reliable Release · Specification

> Mode: **production** — full rigor.

## Goal
Every designed asset from F-016 is built, tested, and hardened: green CI, all 12 helper scripts deployed, all remaining skills and templates authored, all 21+ leaf subagents built and cataloged, runtime tool-use hooks enforced (with R-008 governance gate), debris cleaned from `.aspis/scripts/planning/`, and every agent's edge cases covered — yielding a shippable, self-validating ASPIS runtime.

## Problem
F-017 completed the core loop (plan→build→review→commit) on the 12 primary agents and built 24 of 25 missing skills. But the system is **not complete**:

- **L0 — pytest gate is not green.** Windows subprocess failures in 3.14, model-tier test conflicts, promotion logic gaps, and "three rule layers" edge cases cause test failures that would block a release.
- **L1 — 12 helper scripts are missing + debris exists.** The planning-lead and research-lead ref specs call for deterministic scripts (scope_estimate, constitution_check, plan_quality_check, mode_validator, task_size_check, dependency_graph, search_cache, check_staleness, rank_source, compare_versions, cross_ref, validate-approvals) that don't exist. R-003 requires scripts before agents. Additionally, build detritus (`_tmp_f017_*.py`) pollutes `.aspis/scripts/planning/` (R-006 violation).
- **L2 — 1 skill + 7 templates + 1 workflow are missing.** The `dependency-audit` skill (last of the 25-missing inventory), 7 ref-spec templates (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, TEST_REPORT), and the project-lead operating-protocol workflow are all designed but not built.
- **L3 — 21+ leaf subagents are missing.** System-lead's 7, planning-lead's 8, test-lead's 6 stack-specific testers, plus reviewer/research-lead/fix-lead subagents — every leaf agent designed in F-016 ref specs that isn't yet a catalog agent.
- **L4 — Runtime hardening is missing.** Claude PreToolUse hook is not wired in `.claude/settings.json`. Per-agent edge-case sections from the coverage matrix are absent from many bodies. The enforcement boundary is warn, not block.

## Scope

### In scope

**L0 — Green pytest gate:**
- Discovery sweep: run pytest, capture ALL real failures, write evidence report (T-001a)
- Fix only confirmed failures (T-001b), evidence-driven from discovery report. No speculative fixes.
- If environment blocks pytest, fallback: run non-subprocess tests, document blocked items as `BLOCKED: env`
- Exit gate: `pytest` exits 0 on all platforms (or all non-subprocess tests pass + blocked items documented)

**L1 — Tier-B helper scripts (11) + validate-approvals + debris cleanup:**
1. `scope_estimate.py` — SPEC→size+risk estimate (planning-lead P0)
2. `constitution_check.py` — PLAN vs 12 constitution rules (planning-lead P5)
3. `plan_quality_check.py` — 12 quality standards audit (planning-lead P7)
4. `mode_validator.py` — modes.yaml schema + override validation (planning-lead P0)
5. `task_size_check.py` — task count/size vs mode ceiling (planning-lead P6)
6. `dependency_graph.py` — multi-feature dependency graph (planning-lead P6)
7. `search_cache.py` — grep all research cache paths (research-lead)
8. `check_staleness.py` — compare reference date to type-specific window (research-lead)
9. `rank_source.py` — T1-T6 source authority hierarchy (research-lead)
10. `compare_versions.py` — changelog diff between two versions (research-lead)
11. `cross_ref.py` — multi-source agreement check (research-lead)
12. `validate-approvals.py` — R-008 ledger enforcement: checks governance ledger for missing approvals on protected-path changes (P0)
13. `_tmp_f017_*.py` debris cleanup — remove build detritus from `.aspis/scripts/planning/` (R-006 violation)
- Every script: deterministic, stdlib-only, `--help` exit 0, AST parse passes, deployed to `.aspis/scripts/` with byte-parity from catalog source
- Exit gate: all 12 scripts pass AST + `--help` + smoke test + byte-parity; debris cleaned

**L2 — Remaining skill + templates + workflow:**
- `dependency-audit` skill (P2, planning-lead's dependency-analyzer subagent)
- 7 templates: CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, TEST_REPORT
- project-lead operating-protocol workflow (`.aspis/workflows/project-lead-operating-protocol.md`)
- Exit gate: skill has valid SKILL.md; templates copied to `catalog/templates/`; workflow passes completeness check

**L3 — All leaf subagents from F-016 ref specs (21+):**

System-lead (7):
1. `runtime-validator` — Runs all 8 validation gates, returns single verdict
2. `drift-auditor` — Cross-checks catalog↔live frontmatter per field per agent
3. `permission-auditor` — Cross-checks every agent's allow-list vs policy
4. `export-verifier` — Verifies last export: snapshot matches live, log consistent
5. `catalog-synchronizer` — Ensures catalog↔runtime consistency
6. `opencode-author` — Writes one OpenCode asset at a time
7. `claude-author` — Writes one Claude Code asset at a time

Planning-lead (8):
1. `clarify` — 10-category ambiguity scan, returns CLARIFICATION_REPORT
2. `task-decomposer` — PLAN→ordered TASKS+packets
3. `constitution-checker` — PLAN vs 12-rule constitution audit
4. `idea-capture` — Raw idea→structured INTAKE
5. `prd-writer` — Clarified requirements→SPEC.md
6. `scope-estimator` — SPEC→file count+risk+mode recommendation
7. `research-request-writer` — Knowledge gap→structured RESEARCH_REQUEST
8. `dependency-analyzer` — Multi-feature PLAN→dependency graph

Test-lead stack-specific testers (6):
1. `python-tester` — pytest patterns, coverage analysis, property testing
2. `api-tester` — HTTP assertions, schema validation, contract testing
3. `db-tester` — Migration testing, data integrity, query performance
4. `ui-tester` — Component testing, accessibility, screenshot diff
5. `cli-tester` — Arg-parse testing, exit-code assertions, pipe testing
6. `security-tester` — OWASP scan, fuzz testing, secret scan

Every new subagent: thin catalog body (7-section standard), frontmatter with tool grants + skills + delegates, catalog-registered, validate-runtime clean, exists at `src/aspis/data/catalog/agents/<name>.md`.

**L4 — Hardening:**
- Claude PreToolUse hook modules authored in `.aspis/scripts/hooks/` (T-044)
- R-008 governance request filed for `.claude/settings.json` edit (T-045)
- On owner approval, `.claude/settings.json` hook applied (T-046, non-blocking, `enforcement: warn`)
- Per-agent edge-case sections from coverage matrix added to all bodies that lack them
- Every body has ≥2 documented edge cases
- `validate-runtime --runtime all` exits 0 for all agents (12 existing + all new)
- `byte-parity --dry-run` reports CLEAN

### Out of scope
- Flipping `enforcement: warn` → `block` (requires probation; this feature ships the hook, does not activate block)
- Full live-runtime auto-regeneration (owner runs `aspis export` manually)
- Trace spine (Phase 3 roadmap)
- Self-improvement loop (Phase 4 roadmap)
- Dashboard (Phase 5 roadmap)
- Multi-profile beyond base.yaml
- Reviewer's `sub-reviewer` and **`security-reviewer`** (distinct from the `security-tester` subagent, which IS in scope at T-041) — deferred to post-F-018 when their workloads justify extraction. The security surface is covered by `security-tester` (testing) + reviewer (human review); the dedicated `security-reviewer` subagent returns when the security-review skill matures.
- Research-lead's `codebase-explorer`, `docs-fetcher`, `web-researcher`, `cache-manager` — deferred to post-F-018 when their workloads justify extraction
- Fix-lead's `bug-triager`, `gate-fixer` — deferred to post-F-018
- Project-lead's `context-feeder`, `context-summarizer` — deferred to post-F-018. Note: `context-feeder` requires the trace spine (Phase 3 roadmap) and returns to scope after that feature lands.
- **The 8 missing CLI validators** from system-lead-config-runtime.md §5.8 (`validate-approvals`, `validate-skills`, `validate-agents`, `validate-decisions`, `validate-constitution`, `validate-trace`, `validate-parity`, `validate-profiles`) — deferred to F-019. Rationale: these are governance-enforcement infrastructure that require CLI verb scaffolding and per-validator design. The most critical, `validate-approvals` (R-008 ledger enforcement), is gap P0 HIGH and should be the first validator built in F-019. Interim: R-008 compliance is verified manually via the governance subagent's ledger during the F-018 gate sweeps.

## Requirements

### L0 — Green pytest gate
- **FR-L0-001**: `pytest` MUST exit 0 on all platforms (Windows + Linux). If the environment blocks pytest (e.g., subprocess capture failure in test harness), the fallback is `python -m pytest --no-header -q 2>&1 | Select-String FAILED` (or equivalent); at minimum, all non-subprocess tests MUST pass, and blocked subprocess tests MUST be documented with `BLOCKED: env` in the discovery report.
- **FR-L0-002**: Any test failures discovered in the L0 discovery sweep (T-001a) MUST be fixed with root-cause evidence, not assumed narratives. Failures are fixed only if confirmed by the discovery report; unconfirmed failure classes are marked no-op with documentation.
- **FR-L0-003**: Windows subprocess test failures (if confirmed) MUST be resolved — any test using `subprocess.run` with Python 3.14 MUST pass on Windows.
- **FR-L0-004**: Model-tier test expectations (if confirmed) MUST match the canonical catalog (`model_catalog.yaml`, `agent-models.yaml`). No test may assert a tier that contradicts the catalog.
- **FR-L0-005**: Promotion logic (if confirmed) MUST correctly handle all edge cases: bootstrap promotion, mode=N/A for production, promotion to 5 primaries only.
- **FR-L0-006**: "Three rule layers" (D-006) test assertions (if confirmed) MUST be reconciled — system/project/user rule layering tests must pass.
- **FR-L0-007**: `ruff format` and `ruff check` MUST exit 0 on all source files.

### L1 — Tier-B helper scripts
- **FR-L1-001**: All 12 scripts MUST exist at `.aspis/scripts/<category>/<name>.py` with catalog source at `src/aspis/data/catalog/scripts/<category>/<name>.py`.
- **FR-L1-002**: Every script MUST be deterministic (stdlib-only, no LLM, no network).
- **FR-L1-003**: Every script MUST pass AST parse (`python -c "import ast; ast.parse(open(p).read())"`).
- **FR-L1-004**: Every script MUST return usage on `--help` and exit 0.
- **FR-L1-005**: Scripts MUST be byte-identical between catalog source and deployed path.
- **FR-L1-006**: Planning scripts (scope_estimate, constitution_check, plan_quality_check, mode_validator, task_size_check, dependency_graph) MUST live at `.aspis/scripts/planning/`.
- **FR-L1-007**: Research scripts (search_cache, check_staleness, rank_source, compare_versions, cross_ref) MUST live at `.aspis/scripts/research/`.
- **FR-L1-008**: Governance script (`validate-approvals.py`) MUST live at `.aspis/scripts/system/`.
- **FR-L1-009**: Any `_tmp_f017_*.py` debris in `.aspis/scripts/planning/` MUST be removed (R-006 violation — build detritus, not catalog assets).

### L2 — Remaining skill + templates + workflow
- **FR-L2-001**: `dependency-audit` skill MUST exist at `src/aspis/data/catalog/skills/dependency-audit/SKILL.md` with Purpose / When to use / Procedure / Outputs / Anti-patterns sections.
- **FR-L2-002**: CLARIFICATION_LOG template MUST exist at `src/aspis/data/catalog/templates/planning/CLARIFICATION_LOG.md`.
- **FR-L2-003**: RESEARCH_REQUEST template MUST exist at `src/aspis/data/catalog/templates/planning/RESEARCH_REQUEST.md`.
- **FR-L2-004**: PLAN_OF_PLAN template MUST exist at `src/aspis/data/catalog/templates/planning/PLAN_OF_PLAN.md`.
- **FR-L2-005**: DEPENDENCIES template MUST exist at `src/aspis/data/catalog/templates/planning/DEPENDENCIES.md`.
- **FR-L2-006**: SCOPE_ESTIMATE template MUST exist at `src/aspis/data/catalog/templates/planning/SCOPE_ESTIMATE.md`.
- **FR-L2-007**: MODE_DECISION template MUST exist at `src/aspis/data/catalog/templates/planning/MODE_DECISION.md`.
- **FR-L2-008**: TEST_REPORT template MUST exist. Note: a test report template already lives at `src/aspis/data/catalog/templates/review/test.md`. F-018 MUST either adopt and extend that existing file OR create `src/aspis/data/catalog/templates/report/TEST_REPORT.md` and update references — no duplicate templates.
- **FR-L2-009**: project-lead operating-protocol workflow MUST exist at `.aspis/workflows/project-lead-operating-protocol.md` with: 5-phase master frame, 13 stop-and-ask conditions, recontextualization protocol, per-delegate profiles, human-gate protocol, all as numbered steps.
- **FR-L2-010**: All 7 templates MUST follow the catalog template pattern (frontmatter + structured body sections).

### L3 — Leaf subagents
- **FR-L3-001**: Every new subagent MUST exist as a catalog agent file at `src/aspis/data/catalog/agents/<name>.md`.
- **FR-L3-002**: Every new subagent body MUST follow the 7-section agent body standard (Identity, How you work, Core rules, Responsibilities→skills, Delegation, Dynamic-readiness, Edge cases).
- **FR-L3-003**: Every new subagent MUST have valid frontmatter with all 11 required fields (name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope).
- **FR-L3-004**: Every new subagent's `skills:` field MUST reference only existing catalog skills.
- **FR-L3-005**: Every new subagent's `delegates:` field MUST reference only existing catalog agents.
- **FR-L3-006**: Every new subagent's permission surface MUST honour the universal deny floor: `git commit*` and `git push*` denied, no `bash: '*': allow`.
- **FR-L3-007**: Every new subagent MUST be catalog-registered — its name appears in the `COMMAND_MODULES` or agent registry such that `validate-runtime` discovers and validates it.
- **FR-L3-008**: System-lead's 7 subagents MUST be built at production depth (full bodies, all sections, edge cases).
- **FR-L3-009**: Planning-lead's 8 subagents MUST be built at production depth.
- **FR-L3-010**: Test-lead's 6 stack-specific testers MUST be built at MVP depth (standard body, P0 sections, labs-fallback documented in each).
- **FR-L3-011**: `validate-runtime --runtime all` MUST exit 0 for all agents (12 existing + all new).

### L4 — Hardening
- **FR-L4-001**: Claude PreToolUse hook modules MUST be authored in `.aspis/scripts/hooks/` (catalog source + deployed). The `.claude/settings.json` edit that wires them MUST pass through R-008 governance approval (governance subagent `request` → owner `approve`) before being applied. Configuration: `enforcement: warn`, auto-fix enabled, scope+secret+protected-path checks active.
- **FR-L4-002**: Every agent body (existing + new) MUST have an `## Edge Cases` section with at least 2 documented edge-case scenarios and responses.
- **FR-L4-003**: `byte-parity --dry-run` MUST report CLEAN for all agents.
- **FR-L4-004**: `aspis export --dry-run` MUST exit 0 and report full export plan.
- **FR-L4-005**: `aspis doctor` MUST exit 0 with no FAIL findings.
- **FR-L4-006**: The cross-runtime enforcement gap (Claude strips permission block) MUST be verified fixed — Claude-rendered agents include permission-equivalent content.

### Cross-cutting
- **FR-CC-001**: R-003 (scripts before agents) — L1 scripts MUST be deployed and verified before L3 leaf subagents reference them.
- **FR-CC-002**: R-006 (single source, catalog is truth) — no asset content duplicated across bodies. Agents reference by name/path only.
- **FR-CC-003**: R-008 (human gate for permissions) — governance subagent MUST enforce protected-path writes.
- **FR-CC-004**: R-004 (committer only) — only committer has `git commit*`. Every other agent's bash allowlist denies it.
- **FR-CC-005**: Every layer (L0→L1→L2→L3→L4) has a hard exit gate: `pytest` + `validate-runtime` + `byte-parity` + `validate-index` all green.
- **FR-CC-006**: Cost-of-change for adding a hypothetical new leaf agent ≤ 3 files: the new catalog file, owning agent's frontmatter, and at most one referencing agent's frontmatter.

## Feature rules & style
- **R-003 Deterministic-first** — Script before agent. L1 scripts must ship before L3 leaf subagents.
- **R-006 Thin agents, single source** — Content lives once; bodies reference, never duplicate.
- **R-004 One writer** — Only committer has `git commit*`.
- **R-008 Human gate** — Protected-path changes require governance approval.
- **Catalog is truth** — Author in `src/aspis/data/catalog/`; generated runtime files at `.opencode/`/`.claude/` are never hand-edited.
- **Every subagent = thin catalog body** — 7-section standard, frontmatter, skill refs, delegate refs.
- **Universal deny floor**: `git commit*` committer-only, `git push*` none, `webfetch` system-lead + research-lead only, `websearch` research-lead-only.
- **No `bash: '*': allow`** on any agent.

## Key entities
- **Helper script**: Deterministic Python at `catalog/scripts/` (source) → `.aspis/scripts/` (deployed). Stdlib-only, `--help`, AST-clean.
- **Leaf subagent**: Thin catalog agent body at `catalog/agents/<name>.md`. 7-section standard, frontmatter, cheap tier by default, scoped to one mechanical task.
- **Template**: Structured markdown at `catalog/templates/<category>/<name>.md`. Frontmatter + body sections. Copied by `aspis artifact`.
- **Workflow**: Multi-step procedure at `.aspis/workflows/<name>.md`. Numbered steps, gates, stop conditions.
- **Hook**: Deterministic enforcement boundary. Claude PreToolUse in `.claude/settings.json`, per D-010.

## Success criteria
- **SC-L0-001**: `pytest` exits 0 on Windows AND Linux with 0 failures. Fallback: if environment blocks subprocess tests, all non-subprocess tests pass + blocked items documented as `BLOCKED: env` in discovery report.
- **SC-L0-002**: `ruff format --check .` and `ruff check .` both exit 0.
- **SC-L1-001**: All 12 scripts pass AST parse + `--help` exit 0 + smoke test.
- **SC-L1-002**: Byte-parity verified between catalog source and deployed path for all 12 scripts.
- **SC-L1-003**: Zero `_tmp_f017_*.py` files remain in `.aspis/scripts/planning/`.
- **SC-L2-001**: `dependency-audit` skill has valid SKILL.md with all 5 sections.
- **SC-L2-002**: All 7 templates exist at their catalog paths with correct frontmatter.
- **SC-L2-003**: project-lead operating-protocol workflow has ≥60 numbered steps covering all 5 phases + stop-and-ask + recontextualization.
- **SC-L3-001**: 21+ new subagents exist as catalog agent files.
- **SC-L3-002**: `validate-runtime --runtime all` exits 0 for all agents (12 existing + all new).
- **SC-L3-003**: 0 broken skill references across all agent bodies.
- **SC-L3-004**: 0 orphan delegates across all agent bodies.
- **SC-L3-005**: 0 agents have `bash: '*': allow`.
- **SC-L4-001**: Claude PreToolUse hook modules exist in `.aspis/scripts/hooks/`. R-008 governance request filed for `.claude/settings.json` edit. On owner approval, `.claude/settings.json` contains PreToolUse hook configuration with `enforcement: warn`.
- **SC-L4-002**: Every agent body has ≥2 documented edge cases.
- **SC-L4-003**: `byte-parity --dry-run` reports CLEAN.
- **SC-L4-004**: `aspis export --dry-run` exits 0.
- **SC-L4-005**: `aspis doctor` exits 0.
- **SC-CC-001**: Cost-of-change for a new leaf agent ≤ 3 files (catalog file + owning frontmatter + at most 1 referencing frontmatter).

## Assumptions
- F-016 designs are authoritative and locked. F-018 builds to them.
- F-017 completed 24 of 25 missing skills; only `dependency-audit` remains.
- The 5 existing planning scripts in catalog (`feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `_console.py`, `active_feature.py`) are correct.
- The 7 new planning scripts and 4 new research scripts are greenfield — no legacy code to reconcile.
- The 21+ new subagents are thin bodies (≤60 lines each) following the 7-section standard with frontmatter.
- Models resolve per `config/models.yaml` tier map.
- `enforcement: warn` default from D-010 remains; F-018 ships the hook, does not flip to block.
- System-lead's `governance` subagent is built (F-017); F-018 does not rebuild it.

## Clarifications
Resolved at planning time.

### Session 2026-06-27
- **Q1 — Exact subagent count:** Which leaf subagents from F-016 ref specs are in scope?
  → **A**: System-lead's 7 (runtime-validator, drift-auditor, permission-auditor, export-verifier, catalog-synchronizer, opencode-author, claude-author) + planning-lead's 8 (clarify, task-decomposer, constitution-checker, idea-capture, prd-writer, scope-estimator, research-request-writer, dependency-analyzer) + test-lead's 6 stack-specific testers (python-tester, api-tester, db-tester, ui-tester, cli-tester, security-tester) = 21 total. Reviewer's security-reviewer/sub-reviewer, research-lead's codebase-explorer/docs-fetcher/web-researcher/cache-manager, fix-lead's bug-triager/gate-fixer, and project-lead's context-feeder/context-summarizer are deferred to post-F-018 (workload-justified extraction per D-005).
- **Q2 — Template scope:** Which templates from F-017 deferred list?
  → **A**: 7 templates: CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, TEST_REPORT. BUILD_REPORT, FEATURE_REPORT, and FIX_REPORT already exist from F-017.
- **Q3 — L0 test fix scope:** What specific test failures?
  → **A**: Windows 3.14 subprocess failures, model-tier reconciliation, promotion logic, "three rule layers" assertions. Fix root causes, not suppress symptoms.
- **Q4 — Build depth for new subagents:** Production or MVP?
  → **A**: System-lead and planning-lead subagents at production depth (full 7-section bodies). Test-lead stack testers at MVP depth (standard body, labs-fallback). All must pass validate-runtime.

## Open questions
- None remaining. All scope decisions resolved.
