# F-018 — Use-Case Coverage Matrix

> Every use case each agent/role and asset must handle — happy path AND error/edge cases.
> Status: **covered** (exists and tested) | **partial** (exists but incomplete) | **missing** (not yet built).
> F-018 must close every `partial` and `missing`.

---

## Project-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| project-lead | A1-A16: Project intelligence (16 use cases) | Happy | covered | — | F-017 built `project-awareness`, `context-ladder`, `project-question-answering` skills |
| project-lead | B1-B3: Mode/configuration | Happy | covered | — | `aspis mode` verb built in F-017 |
| project-lead | C1-C14: Feature lifecycle (14 use cases) | Happy | covered | — | Project-lead delegates to planning-lead (plan→spec) + build-lead (build→review); both in live delegate list |
| project-lead | D1-D8: Defects/recovery (8 use cases) | Happy | covered | — | Delegation to fix-lead built in F-017 |
| project-lead | E1-E6: Testing/evidence (6 use cases) | Happy | covered | — | Delegation to test-lead built in F-017 |
| project-lead | F1-F7: Review/acceptance/security (7 use cases) | Happy | covered | — | Delegation to reviewer built in F-017 |
| project-lead | G1-G14: System/runtime/governance (14 use cases) | Happy | partial | T-020 | Delegation to system-lead built; **operating-protocol workflow missing** |
| project-lead | H1-H8: Research/knowledge (8 use cases) | Happy | covered | — | Delegation to research-lead built in F-017 |
| project-lead | I1-I8: Guidance/steering (8 use cases) | Happy | covered | — | `project-guidance` skill built in F-017 |
| project-lead | J1-J16: Health/ambient detection (16 use cases) | Happy | covered | — | `project-health` skill + `aspis doctor` built in F-017 |
| project-lead | K1-K12: Multi-step orchestration (12 use cases) | Happy | partial | T-020 | Core delegation works; **composed flows not documented** |
| project-lead | L1-L25: Edge cases & refusals (25 use cases) | Edge | partial | T-047 | 2 edge cases added in F-017/T-54; **full 25-case table not in body** |
| project-lead | Operating-protocol workflow | Asset | missing | T-020 | **`.aspis/workflows/project-lead-operating-protocol.md` does not exist** |
| project-lead | Delegation Loop edge case | Edge | covered | — | Added in F-017/T-54 |
| project-lead | Concurrent Request edge case | Edge | covered | — | Added in F-017/T-54 |

---

## Planning-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| planning-lead | A1-A6: Track-dependent entry points | Happy | covered | — | `planning-intake` skill built in F-017 |
| planning-lead | B1-B10: Feature lifecycle (10 use cases) | Happy | covered | — | Full planning lifecycle built in F-017 |
| planning-lead | C1-C5: Clarification & research | Happy | covered | — | `requirement-clarification` skill built in F-017 |
| planning-lead | D1-D9: Delegation & subagent (9 use cases) | Happy | partial | T-028..T-035 | Delegation to research-lead/reviewer/explorer works; **all 8 L3 planning subagents missing** |
| planning-lead | E1-E12: Edge cases & refusals | Edge | partial | T-028, T-047 | 2 edge cases added in F-017; **clarify subagent missing** (core edge-case handler) |
| planning-lead | P0 intake → plan-of-plan | Asset | missing | T-018 | **PLAN_OF_PLAN template missing** |
| planning-lead | P3 clarify → CLARIFICATION_LOG | Asset | missing | T-018, T-028 | **CLARIFICATION_LOG template missing**; **clarify subagent missing** |
| planning-lead | P4 spec → SPEC.md | Happy | covered | — | `feature-planning` skill + prd-writer designed but missing |
| planning-lead | P4 spec → SPEC.md (delegated) | Asset | missing | T-032 | **prd-writer subagent missing** |
| planning-lead | P5 architecture → PLAN.md | Happy | covered | — | `architecture-planning` skill built in F-017 |
| planning-lead | P5 constitution audit | Asset | missing | T-004, T-030 | **constitution_check.py script missing**; **constitution-checker subagent missing** |
| planning-lead | P6 tasks → TASKS.md | Happy | covered | — | `task-decomposition` skill built in F-017 |
| planning-lead | P6 tasks (delegated) | Asset | missing | T-029 | **task-decomposer subagent missing** |
| planning-lead | P0 scope estimate | Asset | missing | T-003, T-033 | **scope_estimate.py script missing**; **scope-estimator subagent missing** |
| planning-lead | P6 dependency graph | Asset | missing | T-008, T-035 | **dependency_graph.py script missing**; **dependency-analyzer subagent missing** |
| planning-lead | Mode validation | Asset | missing | T-006 | **mode_validator.py script missing** |
| planning-lead | Plan quality check | Asset | missing | T-005 | **plan_quality_check.py script missing** |
| planning-lead | Task size check | Asset | missing | T-007 | **task_size_check.py script missing** |
| planning-lead | P0 idea capture | Asset | missing | T-031 | **idea-capture subagent missing** |
| planning-lead | P3 research request writer | Asset | missing | T-018, T-034 | **RESEARCH_REQUEST template missing**; **research-request-writer subagent missing** |
| planning-lead | DEPENDENCIES template | Asset | missing | T-018 | **DEPENDENCIES template missing** |
| planning-lead | SCOPE_ESTIMATE template | Asset | missing | T-018 | **SCOPE_ESTIMATE template missing** |
| planning-lead | MODE_DECISION template | Asset | missing | T-018 | **MODE_DECISION template missing** |
| planning-lead | Stuck on Ambiguous Request edge case | Edge | covered | — | Added in F-017/T-54 |
| planning-lead | Mode Mismatch edge case | Edge | covered | — | Added in F-017/T-54 |

---

## Build-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| build-lead | A1-A3: Feature-level builds | Happy | covered | — | `task-orchestration` skill built in F-017 |
| build-lead | B1-B5: Task-level execution | Happy | covered | — | Delegation to general-builder built in F-017 |
| build-lead | C1-C7: Failure handling | Happy | covered | — | Delegation to fix-lead built in F-017 |
| build-lead | D1-D4: Review routing | Happy | covered | — | Delegation to reviewer built in F-017 |
| build-lead | E1-E3: Mode overlays | Happy | covered | — | `build-readiness` skill handles mode |
| build-lead | F1-F5: Prerequisite errors | Edge | covered | — | Error handling in `task-orchestration` |
| build-lead | G1-G10: Edge cases | Edge | partial | T-047 | 2 edge cases added in F-017; **remaining 8 not documented in body** |
| build-lead | Builder Timeout edge case | Edge | covered | — | Added in F-017/T-54 |
| build-lead | Packet Impossible edge case | Edge | covered | — | Added in F-017/T-54 |
| build-lead | dependency-audit skill | Asset | missing | T-017 | **`dependency-audit` skill missing** (last of 25-missing) |

---

## Reviewer — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| reviewer | A1-A6: Plan review (plan-critic) | Happy | covered | — | `plan-critic` skill built in F-017 |
| reviewer | B1-B7: Change review (quality review) | Happy | covered | — | `quality-review` skill built in F-017 |
| reviewer | C1-C4: Verdict handling | Happy | covered | — | `acceptance-decision` skill built in F-017 |
| reviewer | D1-D9: Edge cases | Edge | partial | T-047 | 2 edge cases added in F-017; **remaining 7 not documented in body** |
| reviewer | Same-Model Contamination edge case | Edge | covered | — | Added in F-017/T-54 |
| reviewer | No-Evidence Verdict edge case | Edge | covered | — | Added in F-017/T-54 |
| reviewer | Claude PreToolUse hook | Asset | missing | T-044..T-046 | **Runtime enforcement boundary not wired** (hook modules → R-008 governance → apply) |

---

## System-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| system-lead | A1-A7: Agent lifecycle | Happy | covered | — | `asset-authoring` skill built in F-017 |
| system-lead | B1-B5: Skill lifecycle | Happy | covered | — | `asset-authoring` skill built in F-017 |
| system-lead | C1-C3: Template lifecycle | Happy | covered | — | `asset-authoring` skill built in F-017 |
| system-lead | D1-D2: Workflow lifecycle | Happy | covered | — | `asset-authoring` skill built in F-017 |
| system-lead | E1-E3: Command lifecycle | Happy | covered | — | `asset-authoring` + CLI verbs built in F-017 |
| system-lead | F1-F7: Configuration management | Happy | covered | — | `config-management` skill built in F-017 |
| system-lead | G1-G7: Runtime management | Happy | covered | — | `system-repair` + export verb built in F-017 |
| system-lead | H1-H4: Hook management | Happy | covered | — | `hook-author` skill built in F-017 |
| system-lead | I1-I6: System health | Happy | covered | — | `system-validation` + validate-runtime verb built in F-017 |
| system-lead | J1-J7: Repair & recovery | Happy | covered | — | `system-repair` skill built in F-017 |
| system-lead | K1-K4: Profile management | Happy | covered | — | `profile-manager` skill built in F-017 |
| system-lead | L1-L4: Governance (R-008) | Happy | covered | — | `governance-approval` skill + governance subagent built in F-017 |
| system-lead | M1-M9: Future system | Happy | deferred | — | Deferred to post-F-018 (trace spine, dashboard, self-improvement) |
| system-lead | runtime-validator subagent | Asset | missing | T-021 | **Not yet built** |
| system-lead | drift-auditor subagent | Asset | missing | T-022 | **Not yet built** |
| system-lead | permission-auditor subagent | Asset | missing | T-023 | **Not yet built** |
| system-lead | export-verifier subagent | Asset | missing | T-024 | **Not yet built** |
| system-lead | catalog-synchronizer subagent | Asset | missing | T-025 | **Not yet built** |
| system-lead | opencode-author subagent | Asset | missing | T-026 | **Not yet built** |
| system-lead | claude-author subagent | Asset | missing | T-027 | **Not yet built** |
| system-lead | Self-Modification Guard edge case | Edge | covered | — | Added in F-017/T-54 |
| system-lead | Export Conflict edge case | Edge | covered | — | Added in F-017/T-54 |

---

## Fix-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| fix-lead | 1-12: All fix use cases | Happy | covered | — | Full fix lifecycle built in F-017 |
| fix-lead | Cannot Reproduce edge case | Edge | covered | — | Added in F-017/T-54 |
| fix-lead | Scope Expansion edge case | Edge | covered | — | Added in F-017/T-54 |

---

## Test-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| test-lead | 1-15: All test use cases | Happy | covered | — | `test-generation` + `test-execution` skills built in F-017 |
| test-lead | Flaky Classification edge case | Edge | covered | — | Added in F-017/T-54 |
| test-lead | Environment Issues edge case | Edge | covered | — | Added in F-017/T-54 |
| test-lead | python-tester subagent | Asset | missing | T-036 | **Not yet built** |
| test-lead | api-tester subagent | Asset | missing | T-037 | **Not yet built** |
| test-lead | db-tester subagent | Asset | missing | T-038 | **Not yet built** |
| test-lead | ui-tester subagent | Asset | missing | T-039 | **Not yet built** |
| test-lead | cli-tester subagent | Asset | missing | T-040 | **Not yet built** |
| test-lead | security-tester subagent | Asset | missing | T-041 | **Not yet built** |
| test-lead | TEST_REPORT template | Asset | missing | T-019 | **Not yet built** |
| test-lead | Labs testing coverage | Happy | partial | T-036..T-041 | Labs fallback documented in each stack tester |

---

## Research-Lead — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| research-lead | A-F: All caller use cases | Happy | covered | — | `knowledge-research` + `knowledge-packaging` skills built in F-017 |
| research-lead | Cache-first discipline | Happy | covered | — | `cache-management` skill built in F-017 |
| research-lead | search_cache.py script | Asset | missing | T-009 | **Not yet built** |
| research-lead | check_staleness.py script | Asset | missing | T-010 | **Not yet built** |
| research-lead | rank_source.py script | Asset | missing | T-011 | **Not yet built** |
| research-lead | compare_versions.py script | Asset | missing | T-012 | **Not yet built** |
| research-lead | cross_ref.py script | Asset | missing | T-013 | **Not yet built** |
| research-lead | Cache Staleness edge case | Edge | covered | — | Added in F-017/T-54 |
| research-lead | Source Authority Conflict edge case | Edge | covered | — | Added in F-017/T-54 |

---

## Committer — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| committer | A1-A3: Happy path commits | Happy | covered | — | Built in F-017; `aspis commit` verb operational |
| committer | B1-B5: Refusals | Edge | covered | — | Junk message, scope violation, dirty tree, git add -A, push attempt — all enforced |
| committer | C1-C3: Splitting and special paths | Happy | covered | — | `commit-splitting` skill built in F-017 |
| committer | D1-D4: Hook and gate interaction | Happy | covered | — | Pre-commit + commit-msg hooks built in F-017 |
| committer | Edge cases (body section) | Edge | missing | T-047 | **No `## Edge Cases` section in body** (leaf agent, F-017 skipped it) |

---

## General-Builder — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| general-builder | All packet execution use cases | Happy | covered | — | Built in F-017; receives enriched packets from build-lead |
| general-builder | Edge cases (body section) | Edge | missing | T-047 | **No `## Edge Cases` section in body** (leaf agent, F-017 skipped it) |

---

## Project-Explorer — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| project-explorer | All read-only exploration use cases | Happy | covered | — | Built in F-017; read-only helper, no skills |
| project-explorer | Edge cases (body section) | Edge | missing | T-047 | **No `## Edge Cases` section in body** (leaf agent, F-017 skipped it) |

---

## Bootstrap — Use Cases

| Agent/Role | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| bootstrap | Project onboarding use cases | Happy | covered | — | Self-deleting bootstrap built in F-017 |
| bootstrap | Edge cases (body section) | Edge | missing | T-047 | **No `## Edge Cases` section in body** (transient agent, F-017 skipped it) |

---

## CLI Verbs — Use Cases

| Verb | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| validate-runtime | Structural validation of all agents | Happy | covered | — | Built in F-017; 0 failures |
| byte-parity | Catalog-to-runtime byte-parity check | Happy | covered | — | Built in F-017; CLEAN |
| export | Catalog→runtime export with protection | Happy | covered | — | Built in F-017; --dry-run works |
| validate-index | Registry consistency check | Happy | covered | — | Built in F-017 |
| drift | Frontmatter field drift detection | Happy | covered | — | Built in F-017 |
| governance | R-008 approval workflow (6 subcommands) | Happy | covered | — | Built in F-017 |
| validate-runtime | Windows-specific subprocess edge case | Edge | missing | T-001a, T-001b | **Fails if confirmed by discovery sweep** |
| byte-parity | Claude permission block preservation | Edge | missing | T-048 | **Claude strips permission block — parity verification** |
| export | CONFLICT/PROTECT handling | Edge | covered | — | Protection engine tested in F-017 |

---

## Scripts — Use Cases

| Script | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| feature_scaffold.py | Feature dir + branch creation | Happy | covered | — | Deployed in F-017 |
| task_compile.py | Packet compilation from TASKS.md | Happy | covered | — | Deployed in F-017 |
| prereq_validate.py | Phase-order gate enforcement | Happy | covered | — | Deployed in F-017 |
| scope_estimate.py | SPEC→size+risk estimate | Happy | missing | T-003 | **Not yet built** |
| constitution_check.py | PLAN vs 12 constitution rules | Happy | missing | T-004 | **Not yet built** |
| plan_quality_check.py | 12 quality standards audit | Happy | missing | T-005 | **Not yet built** |
| mode_validator.py | Mode schema + override validation | Happy | missing | T-006 | **Not yet built** |
| task_size_check.py | Task count/size vs mode ceiling | Happy | missing | T-007 | **Not yet built** |
| dependency_graph.py | Multi-feature dependency graph | Happy | missing | T-008 | **Not yet built** |
| search_cache.py | Grep all research cache paths | Happy | missing | T-009 | **Not yet built** |
| check_staleness.py | Reference date vs type window | Happy | missing | T-010 | **Not yet built** |
| rank_source.py | T1-T6 source authority | Happy | missing | T-011 | **Not yet built** |
| compare_versions.py | Changelog diff between versions | Happy | missing | T-012 | **Not yet built** |
| cross_ref.py | Multi-source agreement check | Happy | missing | T-013 | **Not yet built** |
| validate-approvals.py | R-008 ledger enforcement | Happy | missing | T-014 | **Not yet built** (gap P0 HIGH; other 7 validators deferred to F-019) |

---

## Templates — Use Cases

| Template | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| SPEC.md | Feature specification | Happy | covered | — | Template exists in catalog |
| PLAN.md | Architecture plan | Happy | covered | — | Template exists in catalog |
| TASKS.md | Task decomposition | Happy | covered | — | Template exists in catalog |
| ACCEPTANCE.md | Acceptance criteria | Happy | covered | — | Template exists in catalog |
| TASK_PACKET.md | Per-task packet shape | Happy | covered | — | Template exists in catalog |
| BUILD_REPORT.md | Build report | Happy | covered | — | Template exists in catalog |
| FEATURE_REPORT.md | Feature report | Happy | covered | — | Template exists in catalog |
| FIX_REPORT.md | Fix report | Happy | covered | — | Template exists in catalog |
| REVIEW_REPORT.md | Review report | Happy | covered | — | Template exists in catalog |
| CLARIFICATION_LOG.md | Clarification questions+resolutions | Happy | missing | T-018 | **Not yet built** |
| RESEARCH_REQUEST.md | Research delegation packet | Happy | missing | T-018 | **Not yet built** |
| PLAN_OF_PLAN.md | P0 output: track, mode, artifacts | Happy | missing | T-018 | **Not yet built** |
| DEPENDENCIES.md | Multi-feature dependency graph | Happy | missing | T-018 | **Not yet built** |
| SCOPE_ESTIMATE.md | File count + risk estimate | Happy | missing | T-018 | **Not yet built** |
| MODE_DECISION.md | Mode selection rationale | Happy | missing | T-018 | **Not yet built** |
| TEST_REPORT.md | Test evidence + classification | Happy | missing | T-018 | **Path: existing at `templates/review/test.md`; extend or adopt, no duplicate** |

---

## Workflows — Use Cases

| Workflow | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| plan.md | Planning lifecycle | Happy | covered | — | Deployed in F-017 |
| build.md | Build lifecycle | Happy | covered | — | Deployed in F-017 |
| review.md | Review lifecycle | Happy | covered | — | Deployed in F-017 |
| fix.md | Fix lifecycle | Happy | covered | — | Deployed in F-017 |
| small-task.md | Small-task path | Happy | covered | — | Deployed in F-017 |
| project-lead-operating-protocol.md | Project-lead master frame | Happy | missing | T-019 | **Not yet built** (≥60 steps via 8 sections × ~8 steps) |

---

## Hooks — Use Cases

| Hook | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| pre-commit | Scope + secrets + junk + protected paths | Happy | covered | — | Built in F-017 |
| commit-msg | Convention validation | Happy | covered | — | Built in F-017 |
| post-commit | Brain refresh | Happy | covered | — | Built in F-017 |
| Claude PreToolUse | Runtime Edit/Write boundary enforcement | Happy | missing | T-044..T-046 | **Hook modules built, R-008 governance request filed, settings.json applied on approval** |
| Claude PreToolUse | Permission block preservation | Edge | missing | T-048 | **Claude strips permission block — parity verification** |

---

## Cross-Cutting — Use Cases

| Concern | Use Case | Path | Status | F-018 Task | Notes |
|---|---|---|---|---|---|
| pytest | Full suite passes on Windows+Linux | Happy | missing | T-001a, T-001b, T-002 | **Failing tests block release** (discovery sweep → evidence-driven fix → gate) |
| ruff | Format + lint clean | Happy | missing | T-002 | **Must exit 0** |
| modes.yaml | Mode ceiling + override validation | Happy | missing | T-006 | **modes.yaml not deployed to `.aspis/config/`** |
| R-003 scripts-before-agents | L1 scripts deployed before L3 agents | Ordering | missing | T-003..T-016 | **Sequencing enforced in plan** |
| R-006 single-source | No content duplicated across bodies | Quality | covered | — | validate-runtime checks for duplicates |
| R-008 human gate | Protected paths governed | Security | covered | — | governance subagent built in F-017 (L4 hook change requires fresh R-008 gate at T-045) |
| R-004 one-writer | Only committer has git commit* | Security | covered | — | Enforced in all body permissions |
| Cost-of-change ≤3 files | New agent adds ≤3 files | Quality | missing | T-042 | **Must verify after all 21 subagents built** |

---

## Future Scope — Use Cases (not in F-018)

| ID | Use Case | Notes |
|----|----------|-------|
| CU-1 | ASPIS self-dogfooding scenario | ASPIS using its own agents to plan/build/review ASPIS features. The CORE_LOOP scenario. Post trace-spine (Phase 3). |
| CU-2 | Cross-runtime parity matrix | Verify OpenCode-rendered and Claude-rendered agents are equivalent beyond the permission block (description field, body field, skill resolution). Partial coverage in T-048; full parity matrix deferred to F-019+. |
| CU-3 | Profile-aware export | What happens when `--profile` is changed between exports. Multi-profile beyond base.yaml is deferred per SPEC Out of scope. |

---

## Summary Counts

| Category | Covered | Partial | Missing | Total |
|---|---|---|---|---|
| project-lead | 8 | 2 | 1 | 11 |
| planning-lead | 5 | 2 | 14 | 21 |
| build-lead | 7 | 1 | 1 | 9 |
| reviewer | 5 | 1 | 1 | 7 |
| system-lead | 14 | 0 | 7 | 21 |
| fix-lead | 2 | 0 | 0 | 2 |
| test-lead | 3 | 0 | 9 | 12 |
| research-lead | 4 | 0 | 5 | 9 |
| committer | 4 | 0 | 1 | 5 |
| general-builder | 1 | 0 | 1 | 2 |
| project-explorer | 1 | 0 | 1 | 2 |
| bootstrap | 1 | 0 | 1 | 2 |
| CLI verbs | 7 | 0 | 2 | 9 |
| Scripts | 3 | 0 | 12 | 15 |
| Templates | 9 | 0 | 7 | 16 |
| Workflows | 5 | 0 | 1 | 6 |
| Hooks | 3 | 0 | 2 | 5 |
| Cross-cutting | 4 | 0 | 4 | 8 |
| **TOTAL** | **86** | **6** | **70** | **162** |

**F-018 target:** Close all 70 `missing` and 6 `partial` → 162/162 covered. (Count increased by 1: `validate-approvals.py` script added as P0 per A1 review C-5.)
