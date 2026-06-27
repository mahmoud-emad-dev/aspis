# F-018 — Complete the Asset Set & Harden · Implementation Plan

> Mode: **production** — full rigor.
> 50+ steps across 5 layers (L0→L4), each with deterministic gates.

## Approach

**Layer by layer, bottom-up, each gated before the next.** L0 discovers real test failures first (evidence-driven, not speculative), then fixes them. L1 ships deterministic scripts — the cheapest mechanism (R-003) — before any agent references them, plus cleans debris. L2 fills skill + template + workflow gaps. L3 builds all 21+ leaf subagents as thin catalog bodies. L4 hardens the runtime with hook modules, governance-gated settings change, and edge-case coverage.

**Design invariants:**
- Every layer exit gate: `pytest` green + `validate-runtime --runtime all` green + `byte-parity --dry-run` CLEAN + `validate-index` green.
- Scripts before agents (R-003): L1 scripts deployed and verified before L3 leaf subagents.
- Catalog is truth: author in `src/aspis/data/catalog/`; generated runtime never hand-edited.
- Cost-of-change ≤ 3 files per new asset: the catalog file, owning agent's frontmatter, at most one referencing frontmatter.

## Technical context
- **Language:** Python 3.12+
- **Key dependencies:** pytest, ruff, pyyaml
- **Catalog root:** `src/aspis/data/catalog/`
- **Script deploy target:** `.aspis/scripts/` (planning/, research/)
- **Agent catalog:** `src/aspis/data/catalog/agents/`
- **Skill catalog:** `src/aspis/data/catalog/skills/`
- **Template catalog:** `src/aspis/data/catalog/templates/`
- **Workflow target:** `.aspis/workflows/`
- **Runtime targets:** `.opencode/` (native), `.claude/` (adapter)

## Layers

### L0 — Green pytest gate

**Goal:** Discover real test failures (evidence-driven, not speculative), fix them, and establish a trustworthy foundation every downstream gate depends on.

#### Component A: Discovery sweep

**Source:** `tests/` directory, `src/aspis/`

1. **L0.1a — Discovery sweep**
   - Run full pytest suite: `pytest` or `python -m pytest --no-header -q 2>&1`.
   - If the test harness blocks subprocess capture on this environment, fall back to `python -m pytest --no-header -q 2>&1 | Select-String FAILED` (or equivalent grep).
   - Capture ALL real failures (not env artifacts) into `L0_DISCOVERY_REPORT.md` with per-failure evidence (stack trace, file:line, failure class).
   - At minimum, all non-subprocess tests must pass. Subprocess-blocked tests documented with `BLOCKED: env` and rationale.
   - Gate: discovery report written, every failure traced to file:line, no assumed narratives.

#### Component B: Evidence-driven fix (only confirmed failures)

2. **L0.1b — Fix real test failures**
   - Input: `L0_DISCOVERY_REPORT.md` from T-001a.
   - Fix only confirmed failure classes: Windows subprocess (if real), model-tier reconciliation (if real), promotion logic (if real), rule-layer assertions (if real).
   - Any failure class NOT confirmed by the discovery report → mark as "no-op — not reproducible" with evidence.
   - Key evidence notes from A1 review:
     - `validate_index.py:180` already has `10%%` (correctly escaped); the F-017 gap-collation L192 cite is stale. Do not assume a crash.
     - F-017 final-gates.md C-1 is not reproducible against current source without live pytest run.
   - Gate: every confirmed failure class fixed; unconfirmed classes documented as no-op.

#### Component C: Full gate sweep

3. **L0.5 — Full gate sweep**
   - Run full test suite: `pytest` exit 0 (or all non-subprocess pass + blocked items documented).
   - Run `ruff format --check .` + `ruff check .` exit 0.
   - Capture output to `L0_GATE_REPORT.txt` as evidence.
   - Gate: ALL green (or documented env-blocked).

**L0 exit gate:** `pytest` exit 0 + `ruff` exit 0 on all platforms. Fallback: if environment blocks subprocess tests, all non-subprocess tests pass + blocked items documented with `BLOCKED: env`.

---

### L1 — Tier-B helper scripts (12) + debris cleanup

**Goal:** Build and deploy all 12 deterministic helper scripts, clean build detritus. R-003: scripts before agents.

#### Component A: Planning scripts (6)

**Source:** `src/aspis/data/catalog/scripts/planning/` → `.aspis/scripts/planning/`

6. **L1.1 — `scope_estimate.py`**
   - Input: SPEC/INTAKE path. Output: file count, complexity, risk, cost-of-change, recommended mode → stdout YAML.
   - Stdlib-only. `--help` exits 0. AST parse clean.
   - Deploy to `.aspis/scripts/planning/scope_estimate.py`.

7. **L1.2 — `constitution_check.py`**
   - Input: PLAN path + SPEC path. Output: one-row-per-rule report (pass/warn/fail + evidence + fix) → stdout.
   - 12 rules from architecture-constitution.md.
   - Deploy to `.aspis/scripts/planning/constitution_check.py`.

8. **L1.3 — `plan_quality_check.py`**
   - Input: SPEC + PLAN + TASKS paths. Output: 12 quality-standards audit (S-01 through S-12) → stdout.
   - Deploy to `.aspis/scripts/planning/plan_quality_check.py`.

9. **L1.4 — `mode_validator.py`**
   - Input: mode string + modes.yaml path. Output: validated mode with ceiling applied + warnings → stdout.
   - Auto-escalation triggers (E1-E3) implemented.
   - Deploy to `.aspis/scripts/planning/mode_validator.py`.

10. **L1.5 — `task_size_check.py`**
    - Input: TASKS.md path + mode. Output: per-task size vs mode ceiling, over-size warnings → stdout.
    - Deploy to `.aspis/scripts/planning/task_size_check.py`.

11. **L1.6 — `dependency_graph.py`**
    - Input: one or more TASKS.md paths. Output: dependency graph (Mermaid or adjacency list), circular-dep detection → stdout.
    - Deploy to `.aspis/scripts/planning/dependency_graph.py`.

#### Component B: Research scripts (5)

**Source:** `src/aspis/data/catalog/scripts/research/` → `.aspis/scripts/research/`

12. **L1.7 — `search_cache.py`**
    - Input: keyword(s) + cache root path. Output: matching reference paths with staleness status → stdout.
    - Searches `.aspis/research/` and per-feature `Research/` folders.
    - Deploy to `.aspis/scripts/research/search_cache.py`.

13. **L1.8 — `check_staleness.py`**
    - Input: reference date + reference type. Output: FRESH/STALE verdict with window → stdout.
    - Staleness windows per type (7-day security, 30-90 framework, 6-12 month stable).
    - Deploy to `.aspis/scripts/research/check_staleness.py`.

14. **L1.9 — `rank_source.py`**
    - Input: source URL/type. Output: T1-T6 authority tier → stdout.
    - T1=official vendor docs, T6=general web.
    - Deploy to `.aspis/scripts/research/rank_source.py`.

15. **L1.10 — `compare_versions.py`**
    - Input: library name + version A + version B. Output: changelog diff (stub — fetches via webfetch when research-lead available, else reports "no live fetch — stub") → stdout.
    - Deploy to `.aspis/scripts/research/compare_versions.py`.

16. **L1.11 — `cross_ref.py`**
    - Input: claim + source paths. Output: agreement report (consensus/conflict/insufficient) → stdout.
    - Deploy to `.aspis/scripts/research/cross_ref.py`.

#### Component C: Governance script (1)

17. **L1.12 — `validate-approvals.py`**
    - Input: `.aspis/approvals/` ledger path + protected-paths config. Output: per-approval pass/warn/fail → stdout.
    - Checks: every protected-path write has a corresponding governance approval entry; no approval is expired; no write bypassed governance.
    - R-008 ledger enforcement — closes the honor-system gap pending F-019's full 8-validator suite.
    - Deploy to `.aspis/scripts/system/validate-approvals.py`.

#### Component D: Debris cleanup

18. **L1.13 — Remove `_tmp_f017_*.py` debris**
    - Check `.aspis/scripts/planning/` for any `_tmp_f017_*.py` files (build detritus from F-017, R-006 violation).
    - If found: delete them. If none found: document "CLEAN — no debris" and pass.
    - Gate: zero `_tmp_f017_*.py` files remain in `.aspis/scripts/planning/`.

#### Component E: Byte-parity and gate

19. **L1.14 — Byte-parity verification**
    - Verify each deployed script is byte-identical to its catalog source.
    - `python -c "import ast; ast.parse(open(p).read())"` for all 12 scripts.
    - `python <script> --help` exits 0 for all 12.
    - Gate: all pass.

**L1 exit gate:** All 12 scripts pass AST + `--help` + byte-parity; zero debris files remain.

---

### L2 — Remaining skill + templates + workflow

**Goal:** Fill the last skill gap, 7 template gaps, and 1 workflow gap.

18. **L2.1 — `dependency-audit` skill**
    - Path: `src/aspis/data/catalog/skills/dependency-audit/SKILL.md`
    - Sections: Purpose, When to use, Procedure (multi-feature dependency analysis), Outputs, Anti-patterns.
    - References: R-003 (deterministic-first — use `dependency_graph.py` script).
    - Owned by: planning-lead (frontmatter skill ref added).

19. **L2.2 — 7 templates**
    - All to `src/aspis/data/catalog/templates/planning/`:
      - `CLARIFICATION_LOG.md` — structured questions + resolutions
      - `RESEARCH_REQUEST.md` — structured research delegation packet
      - `PLAN_OF_PLAN.md` — P0 output: track, mode, artifacts
      - `DEPENDENCIES.md` — multi-feature dependency graph
      - `SCOPE_ESTIMATE.md` — file count + risk estimate
      - `MODE_DECISION.md` — mode selection rationale
    - One to `src/aspis/data/catalog/templates/report/`:
      - `TEST_REPORT.md` — test evidence + classification + confidence
    - Each: frontmatter (template name, category, purpose) + structured body with placeholder fields.

20. **L2.3 — project-lead operating-protocol workflow**
    - Path: `.aspis/workflows/project-lead-operating-protocol.md`
    - Content (≥60 numbered steps, target ~64 via 8 sections × ~8 steps each):
      - §1: The 5-phase master frame (ENTRY→CLASSIFY→CONTEXT→ACT→RECONTEXTUALIZE→EXIT) — ~10 steps
      - §2: 6 pre-flight checks — ~6 steps (one per check)
      - §3: 13 stop-and-ask conditions — ~13 steps (one per condition)
      - §4: Recontextualization protocol — ~8 steps
      - §5: Per-delegate profiles (planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer) — ~8 steps (one per delegate)
      - §6: Human-gate (R-008) protocol — ~7 steps
      - §7: Delegation packet shape (5 fields) — ~5 steps
      - §8: Flows (Feature Request, Status Query, Defect/Fix, Review, Research, System Change, Mode Change, Ambiguous Request, Continuation, Health Detection) — ~10 steps (one per flow)
    - References: `context-packaging` skill, `lead-routing` skill, `recontextualization` skill.
    - Owned by: project-lead (body references it in "How you work" section).

**L2 exit gate:** Skill SKILL.md valid; all 7 templates exist with correct frontmatter; workflow has ≥60 steps; `validate-runtime` clean.

---

### L3 — Leaf subagents (21+)

**Goal:** Build every leaf subagent from F-016 ref specs that isn't yet a catalog agent.

#### Component A: System-lead subagents (7)

21. **L3.1 — `runtime-validator`**
    - Body: `src/aspis/data/catalog/agents/runtime-validator.md`
    - Purpose: Runs all 8 validation gates, returns single pass/fail verdict with evidence.
    - Tier: cheap. Tools: bash (aspis validate-*, python scripts), read. Skills: system-validation, catalog-validator.
    - Delegates: none (leaf). Runtimes: opencode, claude.
    - Gates referenced: validate-runtime, validate-index, byte-parity, drift, permissions-audit, governance-check, doctor, preflight.

22. **L3.2 — `drift-auditor`**
    - Body: `src/aspis/data/catalog/agents/drift-auditor.md`
    - Purpose: Cross-checks catalog↔live frontmatter per field per agent, returns drift report.
    - Tier: cheap. Tools: bash (aspis drift), read. Skills: drift-detector.
    - Delegates: none.

23. **L3.3 — `permission-auditor`**
    - Body: `src/aspis/data/catalog/agents/permission-auditor.md`
    - Purpose: Cross-checks every agent's allow-list vs policy, returns permission audit report.
    - Tier: cheap. Tools: read, grep, glob, bash (aspis permissions-audit). Skills: system-validation.
    - Delegates: none.

24. **L3.4 — `export-verifier`**
    - Body: `src/aspis/data/catalog/agents/export-verifier.md`
    - Purpose: Verifies last export: snapshot matches live, log consistent.
    - Tier: cheap. Tools: bash (aspis export --check), read. Skills: export-manager.
    - Delegates: none.

25. **L3.5 — `catalog-synchronizer`**
    - Body: `src/aspis/data/catalog/agents/catalog-synchronizer.md`
    - Purpose: Ensures catalog↔runtime consistency — detects drift, proposes fixes.
    - Tier: cheap. Tools: bash (aspis byte-parity, aspis drift), read, write (catalog only). Skills: catalog-validator, drift-detector, byte-parity-checker.
    - Delegates: none. Export_scope: `src/aspis/data/catalog/**`.

26. **L3.6 — `opencode-author`**
    - Body: `src/aspis/data/catalog/agents/opencode-author.md`
    - Purpose: Writes one OpenCode asset at a time — agent, skill, command, hook.
    - Tier: cheap. Tools: read, write, bash (aspis export --runtime opencode). Skills: runtime-author, asset-authoring.
    - Delegates: none. Export_scope: `.opencode/**`.

27. **L3.7 — `claude-author`**
    - Body: `src/aspis/data/catalog/agents/claude-author.md`
    - Purpose: Writes one Claude Code asset at a time — agent, skill, settings.
    - Tier: cheap. Tools: read, write, bash (aspis export --runtime claude). Skills: runtime-author, asset-authoring.
    - Delegates: none. Export_scope: `.claude/**`.

#### Component B: Planning-lead subagents (8)

28. **L3.8 — `clarify`**
    - Body: `src/aspis/data/catalog/agents/clarify.md`
    - Purpose: 10-category ambiguity scan on raw request + draft SPEC, returns CLARIFICATION_REPORT with resolved assumptions + open questions.
    - Tier: cheap. Tools: read, grep, glob. Skills: requirement-clarification.
    - Delegates: project-explorer (for conventions lookups).

29. **L3.9 — `task-decomposer`**
    - Body: `src/aspis/data/catalog/agents/task-decomposer.md`
    - Purpose: SPEC+PLAN→ordered TASKS.md + per-task packets using task_compile.py.
    - Tier: standard. Tools: read, write, edit, bash (task_compile.py, prereq_validate.py). Skills: task-decomposition.
    - Delegates: none.

30. **L3.10 — `constitution-checker`**
    - Body: `src/aspis/data/catalog/agents/constitution-checker.md`
    - Purpose: PLAN vs 12 architecture-constitution rules → CONSTITUTION_CHECK report.
    - Tier: standard. Tools: read, grep, glob, bash (constitution_check.py). Skills: constitution-checks.
    - Delegates: none.

31. **L3.11 — `idea-capture`**
    - Body: `src/aspis/data/catalog/agents/idea-capture.md`
    - Purpose: Raw idea→structured INTAKE.md with goal/problem/value/constraints/scope/risks/mode.
    - Tier: cheap. Tools: read, write. Skills: planning-intake.
    - Delegates: none.

32. **L3.12 — `prd-writer`**
    - Body: `src/aspis/data/catalog/agents/prd-writer.md`
    - Purpose: Clarified requirements→SPEC.md following the SPEC template, mode-scaled.
    - Tier: standard. Tools: read, write, edit. Skills: feature-planning.
    - Delegates: none.

33. **L3.13 — `scope-estimator`**
    - Body: `src/aspis/data/catalog/agents/scope-estimator.md`
    - Purpose: SPEC/INTAKE→SCOPE_ESTIMATE with file count, complexity, risk, cost-of-change, recommended mode.
    - Tier: cheap. Tools: read, grep, glob, bash (scope_estimate.py). Skills: scope-control.
    - Delegates: none.

34. **L3.14 — `research-request-writer`**
    - Body: `src/aspis/data/catalog/agents/research-request-writer.md`
    - Purpose: Knowledge gap→structured RESEARCH_REQUEST packet for research-lead.
    - Tier: cheap. Tools: read, write. Skills: context-packaging.
    - Delegates: none.

35. **L3.15 — `dependency-analyzer`**
    - Body: `src/aspis/data/catalog/agents/dependency-analyzer.md`
    - Purpose: Multi-feature PLAN→DEPENDENCIES graph using dependency_graph.py.
    - Tier: cheap. Tools: read, grep, glob, bash (dependency_graph.py). Skills: dependency-audit.
    - Delegates: none.

#### Component C: Test-lead stack-specific testers (6)

All 6 at MVP depth: standard 7-section body, labs-fallback documented, cheap tier.

36. **L3.16 — `python-tester`**
    - Body: `src/aspis/data/catalog/agents/python-tester.md`
    - Purpose: Python-specific testing — pytest patterns, coverage analysis, property testing.
    - Skills: test-generation, test-execution. Tools: read, write, bash (pytest, coverage).
    - Labs fallback: "If no pytest available, write test scripts in `tests/labs/`."

37. **L3.17 — `api-tester`**
    - Body: `src/aspis/data/catalog/agents/api-tester.md`
    - Purpose: REST API testing — HTTP assertions, schema validation, contract testing.
    - Skills: test-generation, test-execution. Tools: read, write, bash.
    - Labs fallback: "Use curl/httpie scripts with expected response assertions."

38. **L3.18 — `db-tester`**
    - Body: `src/aspis/data/catalog/agents/db-tester.md`
    - Purpose: Database testing — migration testing, data integrity, query performance.
    - Skills: test-generation, test-execution. Tools: read, write, bash.
    - Labs fallback: "Write SQL scripts with expected output comments."

39. **L3.19 — `ui-tester`**
    - Body: `src/aspis/data/catalog/agents/ui-tester.md`
    - Purpose: Frontend/UI testing — component testing, accessibility, screenshot diff.
    - Skills: test-generation, test-execution. Tools: read, write, bash.
    - Labs fallback: "Manual test procedures with documented expected results in `lab_notebook.md`."

40. **L3.20 — `cli-tester`**
    - Body: `src/aspis/data/catalog/agents/cli-tester.md`
    - Purpose: CLI testing — arg-parse testing, exit-code assertions, pipe testing.
    - Skills: test-generation, test-execution. Tools: read, write, bash.
    - Labs fallback: "Shell scripts with exit-code checks and output assertions."

41. **L3.21 — `security-tester`**
    - Body: `src/aspis/data/catalog/agents/security-tester.md`
    - Purpose: Security testing — OWASP scan, fuzz testing, secret scan.
    - Skills: test-generation, test-execution, security-review. Tools: read, write, bash.
    - Labs fallback: "Run secret scanners, fuzz input generators, record findings."

#### Component D: Catalog wiring

42. **L3.22 — Catalog registration**
    - Add all new subagent names to the agent registry so `validate-runtime` discovers them.
    - Add `delegates:` references in owning leads' frontmatter:
      - system-lead: +7 delegates (runtime-validator, drift-auditor, permission-auditor, export-verifier, catalog-synchronizer, opencode-author, claude-author)
      - planning-lead: +8 delegates (clarify, task-decomposer, constitution-checker, idea-capture, prd-writer, scope-estimator, research-request-writer, dependency-analyzer)
      - test-lead: +6 delegates (python-tester, api-tester, db-tester, ui-tester, cli-tester, security-tester)
    - **Also update the `## Delegation` prose section** in each lead body (not just frontmatter) to reference the new subagents with their purpose and scope.
    - Cost-of-change verified: each new subagent touches 2 files (catalog file + owning lead frontmatter); planning-lead subagents may reference the `dependency-audit` skill (3 files max).

43. **L3.23 — L3 gate**
    - `validate-runtime --runtime all` exits 0 for all agents (12 existing + 21 new = 33).
    - 0 broken skill refs. 0 orphan delegates.
    - `byte-parity --dry-run` CLEAN.

**L3 exit gate:** All 21+ new subagents catalog-registered, validate-runtime green, 0 broken refs.

---

### L4 — Hardening

44. **L4.1a — Author PreToolUse hook modules**
    - Author hook modules in `.aspis/scripts/hooks/` (catalog source + deployed): scope check, secret scan, protected-path validation.
    - Each module: deterministic, stdlib-only, callable from the Claude PreToolUse hook framework.
    - Gate: all hook modules exist and pass AST parse.

45. **L4.1b — File R-008 governance request for `.claude/settings.json` edit**
    - Use the governance subagent to file a `request` for the `.claude/settings.json` PreToolUse hook entry.
    - The settings.json edit adds: `PreToolUse` hook referencing `.aspis/scripts/hooks/` modules, `enforcement: warn`, auto-fix enabled, non-blocking.
    - Gate: governance request filed; approval pending owner action.
    - **Documentation:** the `.claude/settings.json` edit is a permissions-change surface (R-008). This task files the request; the edit is NOT applied until owner approval.

46. **L4.1c — Apply `.claude/settings.json` hook (on owner approval)**
    - On governance-approve from owner, apply the `.claude/settings.json` PreToolUse hook entry.
    - Gate: settings.json is valid JSON; hook reference resolves to existing script; `enforcement: warn`.
    - If approval not yet granted at build time: leave the hook modules in place, document the manual edit as a post-build owner action, and mark this task as "BLOCKED: awaiting R-008 owner approval."

47. **L4.2 — Per-agent edge-case sections**
    - Audit all 12 existing agent bodies for `## Edge Cases` section.
    - F-017/T-54 added edge cases to 8 lead bodies. Audit the remaining 4 (committer, general-builder, project-explorer, bootstrap).
    - Add ≥2 edge cases to any body that lacks them.
    - Add ≥2 edge cases to all 21+ new subagent bodies.
    - Codify the bootstrap exception in AGENT_BODY_STANDARD.md before adding bootstrap edge cases (bootstrap is a documented special case — transient, self-deleting).
    - Gate: `validate-runtime` confirms edge-case section present in all bodies.

48. **L4.3 — Cross-runtime parity fix verification**
    - Verify Claude Code adapter preserves `permission:` block (FR-010 from F-017).
    - First: check whether the defect exists in current runtime (F-017 final-completeness.md L121 says FR-010 PASSED in commit 36ab7b5).
    - Run `aspis byte-parity --runtime claude --agent all`.
    - Gate: MUST produce a verdict — `"present-and-fixed"` (defect found, now fixed) or `"not-present"` (defect already resolved). No silent pass-through.

49. **L4.4 — Full gate sweep**
    - `pytest` exit 0.
    - `validate-runtime --runtime all` exit 0.
    - `byte-parity --dry-run` CLEAN.
    - `validate-index` exit 0.
    - `aspis export --dry-run` exit 0.
    - `aspis doctor` exit 0.
    - Gate: ALL green.

**L4 exit gate:** All 6 gates green. System is shippable.

---

### Final gate

50. **F-018 final gate**
    - Every layer gate re-verified.
    - All SC-### checked against evidence.
    - BUILD_REPORT stamped.
    - Feature ready for owner review.

## Dependencies

```
L0 (test fixes)
 └─→ L1 (scripts) ──→ L2 (skill+templates+workflow)
                          └─→ L3 (subagents)
                                  └─→ L4 (hardening)
```

- L0 is prerequisite for all layers (gates must be trustworthy).
- L1 must complete before L3 (R-003: scripts before agents — L3 subagents reference L1 scripts).
- L2 is independent of L1 (can run in parallel) but must complete before L3 (L3 subagents reference L2 skill + templates).
- L4 depends on L3 (all bodies must exist before hardening).
- Within L1: planning scripts (L1.1-L1.6) and research scripts (L1.7-L1.11) can run in parallel.
- Within L3: system-lead subagents (L3.1-L3.7), planning-lead subagents (L3.8-L3.15), and test-lead testers (L3.16-L3.21) can run in parallel.

## Risks and rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| L0 discovery finds no real failures (all tests pass) | Medium | Low | T-001a documents evidence; T-001b collapses to no-op; L0 gate is a 1-task sweep |
| L0 environment blocks pytest (subprocess capture) | Medium | High | Fallback: non-subprocess tests must pass; blocked tests documented as BLOCKED: env |
| Test fixes break other tests | Medium | High | Run full suite after each L0 fix; git revert on regression |
| Script deployment path conflicts | Low | Medium | Byte-parity check catches; catalog source is always the recovery point |
| New subagent body violates standard | Medium | Medium | validate-runtime catches at every gate; fix in catalog source |
| 21+ subagents balloon cost-of-change | Low | High | Each is ≤60 lines, thin body, skill-referenced; count verified ≤3 files per |
| R-008 governance approval blocks `.claude/settings.json` edit | Medium | Medium | Hook modules ship regardless; manual edit documented as post-build owner action |
| Claude PreToolUse hook breaks runtime | Medium | High | Non-blocking warn mode; revert `.claude/settings.json` if issues |
| Cross-runtime parity breaks | Low | Medium | byte-parity check catches before commit; adapter fix is one-file |

**Rollback:** Any layer can be reverted independently. Catalog source is the single source of truth — redeploy from catalog. `.claude/settings.json` is version-controlled; revert to prior commit.

## Build mode: PRODUCTION

All tasks at production depth: small packets, per-task review, full gates, complete reports.
