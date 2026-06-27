# F-017 — Completeness, Traceability & Gaps Review

> **Reviewer**: Independent (plan-critic — completeness, traceability, gaps perspective)
> **Mode**: production
> **Scope**: F-017 SPEC.md (19 FRs, 12 SCs), PLAN.md, TASKS.md (56 tasks)
> **Cross-checked against**: F-016 skills inventory (25 missing), F-016 cli-verbs spec (6 verbs), F-016 planning-scripts spec (3 scripts), and 8 of 12 F-016 agent reference specs (project-lead, planning-lead, build-lead, reviewer, system-lead, research-lead, committer, governance) plus the live catalog state
> **Verdict**: **CHANGES REQUIRED** — 3 medium and 7 minor findings. Build should not start until the structural issues are fixed.

---

## Executive summary

The plan is **substantively complete** — every FR maps to a task, every SC has a measurable gate, all 25 missing skills are scheduled, all 6 CLI verbs are scheduled, the 3 planning scripts are scheduled, and all 5 workflows are scheduled. The phasing is correct (L0 → L1 hard gate → L2-P0 → L2-P1 → Polish) and the asset-class coverage is comprehensive.

However, the review found **one MAJOR structural issue and three MEDIUM issues** that will break the build if not fixed:

1. **MAJOR — CLI path mismatch (T-33, T-34, T-35, T-36, T-52, T-53, T-54)**: Tasks reference `src/aspis/cli/<verb>.py` paths, but the CLI uses `src/aspis/commands/<verb>.py` modules registered in `COMMAND_MODULES` (see `src/aspis/commands/__init__.py:30`). The directory `src/aspis/cli/` does not exist; the file `src/aspis/cli.py` is a 74-line shell that dispatches to `aspis.commands.COMMAND_MODULES`. Creating files at the wrong path means the verbs will not be registered and the build will silently fail the validation spine (L2-P0 exit gate).

2. **MEDIUM — Planning-lead delegate drift (current state, must be fixed in T-18)**: The current `src/aspis/data/catalog/agents/planning-lead.md:42-48` lists 7 delegates (`clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer`) that do not exist as catalog agents. This directly violates FR-005 ("Every agent's delegation section MUST list only delegates that exist as catalog agents"). The SPEC's "Out of scope" defers these subagents to L3/F-018, so T-18 must remove them from the delegates list.

3. **MEDIUM — Templates and scripts scope ambiguity (SPEC §"Out of scope" vs F-016 research)**: The planning-lead ref spec §13 lists 6 missing templates (`CLARIFICATION_LOG`, `RESEARCH_REQUEST`, `PLAN_OF_PLAN`, `DEPENDENCIES`, `SCOPE_ESTIMATE`, `MODE_DECISION`) and 5 missing planning scripts (`scope_estimate`, `constitution_check`, `plan_quality_check`, `mode_validator`, `task_size_check`) as "Near-term". The F-017 SPEC is silent on these — neither in-scope nor out-of-scope. TASKS does not include them. This is an explicit ambiguity that the build will surface as a "wait, the system-lead says these are needed" question mid-flight. The SPEC must add them to "Out of scope" explicitly, or TASKS must add tasks.

4. **MEDIUM — Cost-of-change test not in TASKS (SC-011)**: FR-019 and SC-011 require that "adding a hypothetical new agent requires changes to ≤ 3 files." No task in TASKS explicitly verifies this test. T-31 (cross-agent consistency sweep) and T-56 (final acceptance sweep) both check structural validity but do not run the cost-of-change test as a discrete step.

5. **MEDIUM — Dependency-audit skill is a dead asset (T-48)**: T-48 authors a `dependency-audit` skill owned by a "future `dependency-analyzer` subagent" that the SPEC defers to L3/F-018. The skill has no consumer in F-017 and no agent in the catalog will reference it. The F-016 inventory notes "Only needed for multi-feature planning" and "Future — only needed for multi-feature planning." Authoring it now is premature — either it belongs in F-018 (where the consumer is built) or it should be dropped from F-017.

Plus 7 minor findings (dynamic-readiness convention phrasing, governance ledger path, protected-paths location, F-016 inventory drift, etc.) — see "Findings" below.

---

## 1 · FR coverage matrix

Every FR from SPEC maps to at least one task. The matrix below uses the form "task(s) → artifact".

| FR | Description (1 line) | Covered by | Status |
|---|---|---|---|
| **FR-001** | Skill frontmatter refs resolve to `catalog/skills/<name>/SKILL.md` | T-09..T-15, T-16, T-20, T-22..T-24, T-28, T-29, T-41..T-51 (author all 25 skills); T-17, T-18, T-19, T-21, T-25..T-27, T-30, T-37, T-38, T-39 (finalize bodies with skill refs); T-31, T-56 (cross-ref sweeps) | ✓ Complete |
| **FR-002** | Agent body standard shape: frontmatter + Identity + How you work + Core rules + Responsibilities→skills + Delegation + Dynamic-readiness | T-07 (standard doc); T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30, T-37, T-38, T-39 (apply standard) | ✓ Complete |
| **FR-003** | 3 planning scripts deployed, AST parse, `--help` returns usage | T-01 | ✓ Complete |
| **FR-004** | Least-privilege permission surface; universal deny floor | T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30, T-37, T-38, T-39 (permission verification in each); T-31 (deny-floor audit) | ✓ Complete |
| **FR-005** | Delegation edges — every delegate exists as catalog agent | T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30, T-37, T-38, T-39 (delegate verification); T-31 (orphan-delegate sweep) | ✓ Complete — but see FINDING M-2 (current `planning-lead.md` violates FR-005) |
| **FR-006** | Dynamic-readiness block in every loop agent | T-08 (convention doc); T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30 (lead bodies); T-37, T-38, T-39 (leaf bodies) — referenced inside the body-finalize tasks | ⚠ See FINDING m-1 — convention doc created but no explicit task "add dynamic-readiness block to N bodies" |
| **FR-007** | 3 P0 CLI verbs implemented, `--help` + dry-run | T-33, T-34, T-35 | ⚠ See FINDING M-1 — path mismatch (`src/aspis/cli/` does not exist) |
| **FR-008** | Governance subagent blocks protected paths, append-only ledger | T-36 | ✓ Complete |
| **FR-009** | 3 leaf agents with complete bodies + skill refs | T-37, T-38, T-39 | ✓ Complete |
| **FR-010** | Claude Code adapter preserves `permission:` block | T-35 (export verb includes "fix the stripping bug") | ✓ Complete (but see FINDING m-3 — adapter code is in `src/aspis/`, not the adapter path) |
| **FR-011** | `aspis byte-parity` reports CLEAN/CONFLICT/PROTECT | T-34 | ⚠ See FINDING M-1 — path mismatch |
| **FR-012** | 5 workflows verified complete | T-02, T-03, T-04, T-05, T-06 | ✓ Complete |
| **FR-013** | 7 P1 skills authored | T-41, T-42, T-43, T-44, T-45, T-46, T-47 (T-47 is P2 per inventory; T-41..T-46 are P1) | ✓ Complete |
| **FR-014** | 3 P1 CLI verbs implemented | T-52, T-53, T-54 | ⚠ See FINDING M-1 — path mismatch |
| **FR-015** | 5 P2 skills authored | T-47, T-48, T-49, T-50, T-51 | ✓ Complete — but see FINDING M-5 (T-48 is a dead asset) |
| **FR-016** | Agent bodies cite rules by ID only, not restate | T-07 (standard doc covers the rule); T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30, T-37, T-38, T-39 (apply in body finalization) | ✓ Complete (implicit in the body-standard task) |
| **FR-017** | Agent-body standard + dynamic-readiness in `.aspis/context/` | T-07, T-08 | ✓ Complete |
| **FR-018** | No content duplication across agent bodies (R-006) | T-07 (standard codifies the rule); T-31 (sweep); T-56 (final check) | ✓ Complete |
| **FR-019** | Cost-of-change ≤ 3 files for a new agent | Not explicitly verified — see FINDING M-4 (no task) | ⚠ Gap |

**FR coverage: 14/19 fully complete, 5/19 with findings. No orphan FRs.**

---

## 2 · SC coverage and measurability

Every SC has at least one task that verifies it. All 12 SCs are measurable — but the SC-007 verification (T-40) is **narrow** (only `rules/system-rules.md` is checked, not the full protected path set).

| SC | Description | Verified by | Measurable? |
|---|---|---|---|
| **SC-001** | 0 broken frontmatter skill refs across 12 agent bodies | T-31, T-56 | ✓ Yes (sweep) |
| **SC-002** | Core loop runs end-to-end on cheap+standard models | T-32 (L1 exit gate — explicit sample feature) | ✓ Yes (sample feature + model tier check) |
| **SC-003** | `aspis validate-runtime --runtime all` exits 0 | T-33 (build verb), T-40 (L2-P0 integration), T-56 | ✓ Yes (exit code) |
| **SC-004** | `aspis byte-parity --runtime all` reports CLEAN for all | T-34, T-40, T-56 | ✓ Yes (exit code + per-agent status) |
| **SC-005** | `aspis export --dry-run` exits 0 with full plan | T-35, T-40, T-56 | ✓ Yes (exit code + plan report) |
| **SC-006** | Every agent body passes the standard check | T-17, T-18, T-19, T-21, T-25, T-26, T-27, T-30, T-37, T-38, T-39 (per-body); T-31, T-56 (sweep) | ✓ Yes (sweep) |
| **SC-007** | Write to any protected path is blocked without R-008 approval | T-36 (build governance), T-40 (test `rules/system-rules.md`) | ⚠ Partial — T-40 only tests 1 of 6+ protected paths. SC-007's spec says "any protected path", but the gate is verified for one path only. See FINDING m-4. |
| **SC-008** | 0 agents have `bash: '*': allow` | T-31, T-56 | ✓ Yes (sweep) |
| **SC-009** | All 25 missing skills have valid SKILL.md | T-09..T-15, T-16, T-20, T-22..T-24, T-28, T-29, T-41..T-51; T-56 | ✓ Yes (count = 25) |
| **SC-010** | 5 workflows complete — no TODO/NYI | T-02, T-03, T-04, T-05, T-06 | ✓ Yes (grep + manual) |
| **SC-011** | Cost-of-change test: adding new agent ≤ 3 files | **Not in TASKS** — see FINDING M-4 | ⚠ Gap |
| **SC-012** | Every lead agent's dynamic-readiness block references 3 dials + leanest-correct-path | T-08 (convention); T-17..T-30 (bodies); T-56 (final check) | ✓ Yes (convention check) |

**SC coverage: 10/12 fully verified, 1/12 partial (SC-007), 1/12 gap (SC-011).**

---

## 3 · Skills inventory coverage (F-016 → TASKS)

Cross-checked all 25 missing skills from the F-016 inventory. **All 25 are covered**, but two priority mismatches and one dead-asset concern:

| # | Skill | Priority | Owning agent | TASKS | Notes |
|---|---|---|---|---|---|
| 1 | `builder-selection` | P0 | build-lead | T-15 | ✓ |
| 2 | `cache-management` | P0 | research-lead | T-28 | ✓ |
| 3 | `catalog-validator` | P0 | system-lead | T-22 | ✓ |
| 4 | `constitution-check` | P0 | reviewer | T-12 | ✓ |
| 5 | `constitution-checks` | P0 | planning-lead | T-11 | ✓ |
| 6 | `drift-detector` | P0 | system-lead | T-24 | ✓ |
| 7 | `evidence-validation` | P0 | reviewer | T-13 | ✓ |
| 8 | `governance-approval` | P0 | system-lead | T-23 | ✓ |
| 9 | `harvest-protocol` | P0 | research-lead | T-29 | ✓ |
| 10 | `mode-decision` | P0 | planning-lead, project-lead | T-09 | ✓ |
| 11 | `packet-validation` | P0 | build-lead | T-14 | ✓ |
| 12 | `recontextualization` | P0 | project-lead | T-10 | ✓ |
| 13 | `security-review` | P0 | reviewer | T-20 | ✓ |
| 14 | `byte-parity-checker` | P1 | system-lead | T-41 | ✓ |
| 15 | `export-manager` | P1 | system-lead | T-42 | ✓ |
| 16 | `finding-format` | P1 | reviewer | T-43 | ✓ |
| 17 | `model-router` | P1 | system-lead | T-44 | ✓ |
| 18 | `runtime-author` | P1 | system-lead | T-45 | ✓ |
| 19 | `scope-compliance` | P1 | reviewer | T-46 | ✓ |
| 20 | `session-continuation` | P1 | project-lead | T-16 (L1 — see FINDING m-5) | ⚠ |
| 21 | `commit-readiness` | P2 | reviewer | T-47 | ✓ |
| 22 | `dependency-audit` | P2 | planning-lead (future subagent) | T-48 (see FINDING M-5) | ⚠ Dead asset |
| 23 | `hook-author` | P2 | system-lead | T-49 | ✓ |
| 24 | `model-inventory` | P2 | system-lead | T-50 | ✓ |
| 25 | `profile-manager` | P2 | system-lead | T-51 | ✓ |

**Coverage: 25/25 scheduled. 0 missing.**

### Inconsistency: F-016 inventory vs current catalog

The F-016 inventory says these skills are "missing" (no SKILL.md file), but the current catalog agent bodies already reference some of them in their `skills:` frontmatter:

- `planning-lead.md:61-62` already lists `mode-decision` and `constitution-checks` (matches F-016 P0 missing list)
- `build-lead.md:51-52` already lists `packet-validation` and `builder-selection` (matches F-016 P0 missing list)

This is **consistent with the F-016 interpretation** — the inventory says "4 of the 42 frontmatter-referenced skills are missing" and these are the 4. The plan correctly authors them in L0/L1 so the references will resolve at SC-001 check time. No action needed — but the catalog is currently in a broken state (frontmatter refs to skills that don't exist as SKILL.md). The build will fix that as a side effect.

---

## 4 · CLI verbs coverage

All 6 CLI verbs are covered. **All 6 suffer from the same path mismatch** (FINDING M-1).

| Verb | Priority | Per spec | TASKS | Order | Notes |
|---|---|---|---|---|---|
| `validate-runtime` | P0 | cli-verbs.md §"Verb: validate-runtime" | T-33 | L2-P0 | ✓ |
| `byte-parity` | P0 | cli-verbs.md §"Verb: byte-parity" | T-34 | L2-P0 | ✓ |
| `export` | P0 | cli-verbs.md §"Verb: export" | T-35 | L2-P0 | ✓ |
| `governance` | P1 | cli-verbs.md §"Verb: governance" | T-36 (full implementation in L2-P0), T-54 (complete in L2-P1) | L2-P0 + L2-P1 | ✓ |
| `validate-index` | P1 | cli-verbs.md §"Verb: validate-index" | T-52 | L2-P1 | ✓ |
| `drift` | P1 | cli-verbs.md §"Verb: drift" | T-53 | L2-P1 | ✓ |

**Coverage: 6/6. Order: P0 before P1. ✓**

### Verb interface alignment with cli-verbs.md

The TASKS brief descriptions match the interface signatures from the spec:
- T-33: `aspis validate-runtime [--runtime all] [--check <field>]` ✓
- T-34: `aspis byte-parity [--runtime <r>] [--agent <n>]` ✓
- T-35: `aspis export [--runtime <r>] [--agent <n>] [--dry-run] [--check]` ✓
- T-36: `aspis governance <subcommand>` (6 subcommands: request, approve, audit, revoke, check, ledger) ✓
- T-52: `aspis validate-index [--fix]` ✓
- T-53: `aspis drift [--field <n>] [--runtime <r>]` ✓

---

## 5 · Planning scripts coverage

All 3 scripts covered by T-01. Source → destination paths correct.

| Script | Source (per spec) | Destination (per spec) | TASKS | Validation per spec |
|---|---|---|---|---|
| `feature_scaffold.py` | `src/aspis/data/catalog/scripts/planning/feature_scaffold.py` | `.aspis/scripts/planning/feature_scaffold.py` | T-01 | AST parse + `--help` + refuses to overwrite active feature (FeatureActiveError) |
| `task_compile.py` | `src/aspis/data/catalog/scripts/planning/task_compile.py` | `.aspis/scripts/planning/task_compile.py` | T-01 | AST parse + `--help` + `--dry-run` reports packet set |
| `prereq_validate.py` | `src/aspis/data/catalog/scripts/planning/prereq_validate.py` | `.aspis/scripts/planning/prereq_validate.py` | T-01 | AST parse + `--help` + `--phase plan` exits 0 |

**Cross-check vs live files**: All 3 source files exist at the spec paths (verified). Destination `.aspis/scripts/planning/` does NOT exist — T-01 is the deployment task. ✓

**Note**: T-01 also deploys `_console.py` and `active_feature.py` (mentioned in T-01 description but not in the planning-scripts spec). The spec says "3 planning scripts" — `_console.py` and `active_feature.py` are helper modules. T-01's "5 files" wording is correct. ✓

---

## 6 · Workflow coverage

All 5 workflows scheduled. T-02..T-06 each verify one workflow against the owning agent's ref spec and fill gaps. Target: complete (no TODO/NYI markers, steps align with ref spec procedure sections).

| Workflow | Owning agent | Current lines | TASKS | Status |
|---|---|---|---|---|
| `plan.md` | planning-lead | 52 | T-02 | ✓ Verifies against ref § phases P0–P8 |
| `build.md` | build-lead | 43 | T-03 | ✓ Verifies against ref § 9-step loop |
| `review.md` | reviewer | ~30 | T-04 | ✓ Verifies against ref § 9 dimensions + 4 verdicts |
| `fix.md` | fix-lead | ~30 | T-05 | ✓ Verifies against ref § 6-step spine |
| `small-task.md` | planning-lead (dispatch) | 25 | T-06 | ✓ Verifies all 5 tracks (Question/Trivial/Small/Bug/Feature) |

**Note on `small-task.md`**: The TASKS description (line 30) says "5 tracks (Question/Trivial/Small-task/Bug/Feature)" but the planning-lead ref spec §2 lists 6 tracks (`Question/Trivial/Small task/Feature/Project plan` + `Defect` routed to fix-lead). The current `small-task.md` is 25 lines and only covers Question/Trivial/Small-task/Bug/Feature. T-06 should verify against the full 6-track classification or scope the check to the 5 listed in T-06. **Minor ambiguity.**

---

## 7 · 12 agent bodies coverage

12 agents = 8 leads + 3 leaves + bootstrap. All 8 leads and 3 leaves have tasks. **Bootstrap is not in TASKS.**

| Agent | Type | TASKS | Phase | Notes |
|---|---|---|---|---|
| project-lead | L1 lead | T-17 | L1 | ✓ |
| planning-lead | L1 lead | T-18 | L1 | ✓ (but see M-2 — current delegates list violates FR-005) |
| build-lead | L1 lead | T-19 | L1 | ✓ |
| reviewer | L1 lead | T-21 | L1 | ✓ |
| system-lead | L1 lead | T-25 | L1 | ✓ |
| fix-lead | L1 lead | T-26 | L1 | ✓ |
| test-lead | L1 lead | T-27 | L1 | ✓ |
| research-lead | L1 lead | T-30 | L1 | ✓ |
| committer | L2 leaf | T-37 | L2-P0 | ✓ |
| general-builder | L2 leaf | T-38 | L2-P0 | ✓ |
| project-explorer | L2 leaf | T-39 | L2-P0 | ✓ |
| **bootstrap** | (12th catalog agent) | **MISSING** | — | ⚠ See FINDING m-6 |

**Coverage: 11/12 scheduled. Bootstrap is a transient agent that self-deletes post-bootstrap (per the F-016 system-lead ref spec §12 "Bootstrap that self-deletes (F-014)"), so the absence may be intentional. But FR-019's cost-of-change test (≤ 3 files for a new agent) would not work correctly for a future bootstrap-style agent if the body standard doesn't cover it.**

---

## 8 · Agent reference spec cross-check (spot-check 3-4 specs)

Spot-checked F-016 agent ref specs against TASKS for skills/templates/assets coverage.

### 8.1 — project-lead ref spec §2

- Required skills: 8 existing + 3 new (`recontextualization`, `session-continuation`, `mode-decision`)
- New skills covered: T-09 (`mode-decision`), T-10 (`recontextualization`), T-16 (`session-continuation`)
- Templates: 4 needed (`STATUS_REPORT.md`, `DELEGATION_PACKET.md`, `REPLY_TO_USER.md`, `ESCALATION_NOTE.md`)
- **Templates are NOT in TASKS** — see FINDING M-3 (templates scope ambiguity). The ref spec calls them "near-term" but the SPEC is silent.
- Workflows: 1 needed (`project-lead-operating-protocol.md`)
- **Workflow is NOT in TASKS** — same scope ambiguity. The existing workflows directory does not have this file. The system currently relies on inline prose in the agent body, which violates R-006 (thin agent, single source). **Either the workflow is needed and is missing, or the system-lead ref spec is over-specified and we accept the inline-prose pattern. The plan is silent.**

### 8.2 — planning-lead ref spec §13

- Templates: 6 missing (`CLARIFICATION_LOG`, `RESEARCH_REQUEST`, `PLAN_OF_PLAN`, `DEPENDENCIES`, `SCOPE_ESTIMATE`, `MODE_DECISION`)
- Scripts: 5 missing (`scope_estimate.py`, `constitution_check.py`, `plan_quality_check.py`, `mode_validator.py`, `task_size_check.py`)
- Workflow: `plan.md` to expand from 52 → ~120 lines
- **All 3 categories are NOT in TASKS** — see FINDING M-3.

### 8.3 — system-lead ref spec §12

- Subagents: 8 future subagents (`governance`, `runtime-validator`, `drift-auditor`, `permission-auditor`, `export-verifier`, `catalog-synchronizer`, `opencode-author`, `claude-author`)
- SPEC §"Out of scope" lists only 3 (runtime-validator, drift-auditor, permission-auditor)
- **5 subagents are silently dropped**: `export-verifier`, `catalog-synchronizer`, `opencode-author`, `claude-author`, plus the `governance` subagent is built (T-36), so that's covered. So **4 are unaccounted for**. Either they are deferred by the SPEC and the SPEC's out-of-scope list is incomplete, or they are needed and missing from TASKS. **Minor finding.**

### 8.4 — research-lead ref spec §12

- Scripts: 5 missing (`search_cache.py`, `check_staleness.py`, `rank_source.py`, `compare_versions.py`, `cross_ref.py`)
- **All 5 are NOT in TASKS** — same scope ambiguity as planning-lead. The ref spec says "scripts (5 new deterministic)" without priority.
- Subagents: 4 future (`codebase-explorer`, `docs-fetcher`, `web-researcher`, `cache-manager`) — all out-of-scope per SPEC.

### 8.5 — reviewer ref spec §11

- Subagents: 2 future (`security-reviewer`, `sub-reviewer`) — deferred.
- The reviewer ref spec §3 lists 6 missing skills (3 P0 + 2 P1 + 1 P2) — all in TASKS. ✓

### 8.6 — committer ref spec

- 3 existing skills (`clean-tree-precondition`, `commit-message`, `commit-splitting`) — T-37 verifies they resolve. ✓
- No new skills, no new subagents. ✓

### 8.7 — build-lead ref spec §3

- 2 missing skills (`packet-validation`, `builder-selection`) — T-14, T-15. ✓
- Build scripts: 0 new (uses `task_compile.py`, `prereq_validate.py` — covered by T-01). ✓

### 8.8 — governance ref spec

- 6 subcommands (`request`, `approve`, `audit`, `revoke`, `check`, `ledger`) — T-36 covers all 6. ✓
- Protected paths set — 9 categories — T-36 builds the boundary check. The PLAN.md lists the canonical set; the actual files for the protected paths exist at `src/aspis/data/catalog/config/policy/` (modes.yaml, hooks.yaml, constitution-checks.yaml, etc.) — see FINDING m-7.

---

## 9 · Dynamic-readiness convention

The convention document is T-08. The PLAN says each L1/L2 lead body has a dynamic-readiness block referencing the convention. The TASKS body-finalization tasks (T-17..T-30, T-37..T-39) mention "add Dynamic-readiness sections" in their descriptions, but **no task explicitly says "add the dynamic-readiness block to all 11 agent bodies"**. The convention is implicit in each body-finalization task.

**Finding m-1**: FR-006 says "dynamic-readiness block MUST be present in every loop agent's body." T-08 creates the convention. T-17..T-30 + T-37..T-39 each add a Dynamic-readiness section. **This is covered** — the convention is "every body has it" and each task does it — but the description is buried. **Acceptable as-is** but could be made explicit with a final-sweep task that grep-asserts the block is present in all 12 bodies.

---

## 10 · Asset-class coverage

| Asset class | Scheduled in TASKS? | Notes |
|---|---|---|
| Skills (25) | ✓ All 25 covered | T-09..T-15 (L0 P0), T-16, T-20, T-22..T-24, T-28, T-29 (L1 P0), T-41..T-46 (L2 P1), T-47..T-51 (L2 P2) |
| Templates (6 from planning-lead + 4 from project-lead) | ✗ NONE | See FINDING M-3 |
| Workflows (5) | ✓ All 5 verified | T-02..T-06 |
| Scripts (3 planning) | ✓ T-01 | |
| Scripts (5 planning-side) | ✗ NONE | See FINDING M-3 (`scope_estimate.py`, etc.) |
| Scripts (5 research-side) | ✗ NONE | See FINDING M-3 (`search_cache.py`, etc.) |
| Tools/permissions | ✓ Verified per body | T-17..T-30, T-37..T-39 |
| Hooks | Partial — no task explicitly verifies hook parity | The system-lead ref spec §8 specifies 4 hooks (pre-commit, commit-msg, post-commit, runtime guard) with two-surface parity. No TASKS task verifies this. **MINOR GAP.** |
| Approval ledger (`.aspis/state/approval-ledger.yaml`) | ✓ T-36 | ✓ But `.aspis/state/` does not exist — T-36 must create the directory. |

**Asset class summary: 5 of 8 fully covered. 3 gaps (templates, planning/research scripts, hooks parity).**

---

## 11 · Acceptance criteria quality

Most tasks have measurable acceptance. The "verify/confirm" verbs in T-22, T-23, T-25, T-31, T-55, T-56 are vague, but the test types table at the bottom of TASKS.md (lines 177-186) clarifies what "verify" means (cross-ref check, structural validation, etc.). **Acceptable as-is** — the test types table serves as the spec for the "verify" verb.

**One concern**: T-40 (L2-P0 integration check) tests 1 protected path (`rules/system-rules.md`) but SC-007's spec lists 6+ protected path patterns. T-40 should enumerate the full protected set in its verification, not just one path. See FINDING m-4.

---

## 12 · Review routing

The Review routing table (TASKS.md lines 169-173) is appropriate:

| Risk level | Tasks | Reviewer |
|---|---|---|
| **High** (governance, permissions, CLI verbs) | T-33, T-34, T-35, T-36 | Reviewer lead (full review) |
| **Medium** (agent bodies, shared skills) | T-07..T-30, T-37, T-38, T-39 | Sub-reviewer or peer check |
| **Low** (P1/P2 skills, edge cases, polish) | T-41..T-56 | Self-check against catalog pattern |

Routing is appropriate. T-31 (cross-agent consistency sweep) and T-32 (L1 exit gate) are not in the routing table but are clearly High and Hard-Gate respectively. **Acceptable — those are gate tasks, not reviewable artifacts.**

**Test-lead is not invoked explicitly in TASKS**. The testing depth table (TASKS.md lines 177-186) lists 8 test types but no task says "test-lead verifies X". The test-lead agent is delegated by build-lead for per-task testing, which is a runtime concern, not a TASKS concern. **Acceptable as-is.**

---

## 13 · Out-of-scope verification

Cross-checked the SPEC §"Out of scope" (lines 20-30) against TASKS. **All listed out-of-scope items are absent from TASKS.** No scope creep detected. ✓

However, the out-of-scope list is **incomplete**:
- It does not mention the 6 missing templates from planning-lead ref §13
- It does not mention the 5 missing scripts from planning-lead ref §13
- It does not mention the 5 missing scripts from research-lead ref §12
- It does not mention the project-lead operating protocol workflow
- It does not mention the 4 system-lead ref-spec future subagents (`export-verifier`, `catalog-synchronizer`, `opencode-author`, `claude-author`)

These are the **scope-ambiguity items** in FINDING M-3.

---

## 14 · GAP findings (the real list)

### MAJOR findings (must fix before build)

#### M-1 — CLI path mismatch (T-33, T-34, T-35, T-36, T-52, T-53, T-54)

**Where**: TASKS.md lines 100, 101, 102, 105, 138, 139, 140.

**Problem**: All 6 CLI verb tasks reference `src/aspis/cli/<verb>.py` paths, but the directory `src/aspis/cli/` does not exist. The actual CLI architecture is:
- `src/aspis/cli.py` (74-line shell that dispatches to commands)
- `src/aspis/commands/<verb>.py` modules with a `register(subparsers)` function
- `src/aspis/commands/__init__.py:30` — `COMMAND_MODULES` tuple that lists the registered modules

If T-33 creates `src/aspis/cli/validate_runtime.py`, the file will be:
1. Not picked up by the `aspis` CLI (the loader loops over `COMMAND_MODULES`, not a directory)
2. Not in the import path (Python won't import from `src/aspis/cli/`)
3. Silently break SC-003, SC-004, SC-005 at the L2-P0 gate

**Fix**: Update each affected task description to use the correct path and registration:
- Path: `src/aspis/commands/<verb>.py` (not `src/aspis/cli/<verb>.py`)
- Registration: "Import the module and add it to `COMMAND_MODULES` in `src/aspis/commands/__init__.py:30`"

**Affected tasks**: T-33, T-34, T-35, T-36, T-52, T-53, T-54 (7 tasks).

#### M-2 — Planning-lead delegate drift (current `planning-lead.md`)

**Where**: `src/aspis/data/catalog/agents/planning-lead.md` lines 42-48.

**Problem**: The current catalog body lists 7 delegates that are not in the catalog:
```yaml
delegates:
  - research-lead
  - reviewer
  - project-explorer
  # Future L3 subagents (referenced in spec, may not yet exist):
  - clarify
  - task-decomposer
  - idea-capture
  - prd-writer
  - constitution-checker
  - scope-estimator
  - research-request-writer
```

FR-005 says: "Every agent's delegation section MUST list only delegates that exist as catalog agents." The 7 subagents are explicitly out of scope per SPEC §"Out of scope" (deferred to L3/F-018). The current body is in violation.

**Fix**: T-18 (finalize planning-lead body) must remove the 7 deferred subagents from the `delegates:` list, leaving only `research-lead`, `reviewer`, `project-explorer`. The comment "may not yet exist" is the problem — it explicitly admits the violation.

**Why this matters**: The L1 exit gate (T-32) requires "verify delegation edges" as part of the standard check. T-18 finalizes the body, and if the body still has 7 orphan delegates, the standard check fails on this body before any other check runs.

#### M-3 — Templates and scripts scope ambiguity

**Where**: SPEC.md §"Out of scope" (lines 20-30) vs planning-lead ref §13 and research-lead ref §12.

**Problem**: The F-016 reference specs identify assets that the system needs but F-017 is silent on:
- **6 templates** (planning-lead ref §13): `CLARIFICATION_LOG`, `RESEARCH_REQUEST`, `PLAN_OF_PLAN`, `DEPENDENCIES`, `SCOPE_ESTIMATE`, `MODE_DECISION`
- **4 templates** (project-lead ref §10): `STATUS_REPORT`, `DELEGATION_PACKET`, `REPLY_TO_USER`, `ESCALATION_NOTE`
- **1 workflow** (project-lead ref §10): `project-lead-operating-protocol.md`
- **5 scripts** (planning-lead ref §13): `scope_estimate.py`, `constitution_check.py`, `plan_quality_check.py`, `mode_validator.py`, `task_size_check.py`
- **5 scripts** (research-lead ref §12): `search_cache.py`, `check_staleness.py`, `rank_source.py`, `compare_versions.py`, `cross_ref.py`

The SPEC §"Out of scope" does not list these, but neither does TASKS include them. This is a **silent scope hole** — the F-016 research says the system needs them, the SPEC doesn't say, the plan doesn't build them. If the build runs without a decision, the L1 exit gate (T-32) may fail because:
- planning-lead's body has a "Recommended" reference to a `mode-decision` skill — but the inline prose remains in the body, violating R-006 (thin agent, single source)
- The system-lead §12 has 60+ use cases including G13 (Add new profile), K4 (Multi-feature coordination), etc. — some of these reference templates that don't exist

**Fix**: Either (a) add a new SPEC §"Out of scope" bullet listing these 23 items explicitly, or (b) add TASKS to build them. The cleaner option is (a) — the SPEC's out-of-scope should be exhaustive. The "Out of scope" section in the SPEC is currently 11 bullets; a 12th bullet covering "F-016 research-flagged Near-term assets (templates, helper scripts, project-lead workflow) deferred to F-019 or later" closes the gap.

**Why this matters**: The build will run. The L1 exit gate will pass on the 56 tasks as scheduled. Then 2 weeks later, the system-lead's "add a profile" use case (G13) will surface a missing template, and the owner will say "why didn't F-017 build that?" The answer should be in the SPEC, not invented after the fact.

#### M-4 — SC-011 cost-of-change test not in TASKS

**Where**: SPEC.md SC-011 (line 130), FR-019 (line 95), TASKS.md (no task).

**Problem**: SC-011 says "The cost-of-change test passes: adding a hypothetical new agent requires changes to ≤ 3 files." No task in TASKS explicitly runs this test. T-31 and T-56 are "sweeps" but neither says "hypothetically add a new agent and count files."

**Fix**: Add a task (T-57 or fold into T-56): "Cost-of-change test — hypothetical 'add a new agent' exercise: count files (1 new catalog agent + 1 delegates list update + 1 new skill if needed). Verify count ≤ 3. If > 3, identify the convention gap and fix it."

**Why this matters**: SC-011 is the test of the architecture constitution's "cost-of-change" principle. If we don't run it, we don't know if the architecture is actually cheap-to-change — we just claim it is.

#### M-5 — Dependency-audit skill is a dead asset (T-48)

**Where**: TASKS.md line 132 (T-48).

**Problem**: T-48 authors a `dependency-audit` skill "owned by planning-lead (future `dependency-analyzer` subagent)" — but the SPEC §"Out of scope" defers that subagent to L3/F-018. The skill has **no consumer in F-017**:
- The planning-lead body (T-18) will not reference it (no agent will use it until the subagent exists)
- The skill cannot be invoked end-to-end
- It will be built and then sit unused

The F-016 inventory notes: "Future — only needed for multi-feature planning."

**Fix**: Either (a) move T-48 to "deferred to F-018" and document in the SPEC §"Out of scope" or a separate "Deferred" list, or (b) keep T-48 but document in the task description that the skill is a "shelf asset" awaiting F-018's subagent.

**Why this matters**: An asset with no consumer is a maintenance burden (must be kept valid) with no value. R-003 (deterministic-first) and R-006 (thin, single-source) both push against building things you don't need.

### MEDIUM findings

#### m-1 — Dynamic-readiness convention not explicitly scheduled as a sweep

The convention doc is T-08. Each body-finalize task says "add Dynamic-readiness sections" but no task says "verify all 12 bodies have the dynamic-readiness block." This is a sweep that should be in T-56 or a new task.

**Fix**: Add an explicit check to T-56: "verify every loop agent body has a Dynamic-readiness section referencing the convention doc."

#### m-2 — Protected-path test is narrow (SC-007 verification, T-40)

T-40 only tests `rules/system-rules.md`. SC-007's spec lists 6+ protected path patterns (`rules/**`, `.aspis/rules/**`, `.opencode/agents/**`, `.claude/agents/**`, `.claude/settings.json`, `**/permissions*.yaml`, plus Tier-2 configs).

**Fix**: T-40 should iterate over the full protected set and verify each is blocked.

#### m-3 — Claude adapter fix is vague (FR-010, T-35)

T-35 says "preserves `permission:` block in Claude Code adapter output (fix the stripping bug)" but the plan §"Component 7" notes the fix "lives in the adapter code (if it exists) or in the export verb's Claude render path." The actual location of the adapter is not specified. The adapter code is in `src/aspis/`, not in `src/aspis/cli/` or `src/aspis/commands/`.

**Fix**: T-35 should specify the exact file to modify (or the new file to add) for the Claude render path. The current `src/aspis/` core has export logic — find it and name the path.

#### m-4 — `session-continuation` placement (T-16)

T-16 (project-lead's `session-continuation` skill) is in Phase 2 (L1) and listed as P1 in the F-016 inventory. The placement is correct for the core loop, but TASKS should note that the priority is P1 even though placement is L1 (so reviewers don't think it's mis-prioritized).

**Fix**: T-16 description should say "P1 skill scheduled in L1 because the project-lead's core loop needs it." Or leave as-is — placement is correct, just call it out.

#### m-5 — Bootstrap agent not in TASKS

The 12-agent roster (8 leads + 3 leaves + bootstrap) is named in the SPEC and PLAN, but no TASKS task finalizes the bootstrap agent. Bootstrap is transient (self-deletes post-bootstrap), so this may be intentional. But FR-019's cost-of-change test should still cover it.

**Fix**: Add a brief task or a TASKS note: "Bootstrap is transient (self-deletes per F-014) and is not finalized in F-017. Its current state at `src/aspis/data/catalog/agents/bootstrap.md` is accepted as-is."

#### m-6 — System-lead ref-spec future subagents incomplete in SPEC out-of-scope

SPEC §"Out of scope" lists 3 system-lead subagents (`runtime-validator`, `drift-auditor`, `permission-auditor`). The system-lead ref §10 lists 8 future subagents. The 4 not listed: `export-verifier`, `catalog-synchronizer`, `opencode-author`, `claude-author`. (The 5th, `governance`, is built in T-36.)

**Fix**: Add the 4 subagents to SPEC §"Out of scope" (or the SPEC should explicitly say "8 system-lead future subagents deferred" without listing them).

#### m-7 — Protected paths location inconsistency

The governance ref spec §2 and PLAN.md §"Component 8" list protected paths like `.aspis/config/hooks.yaml`, `.aspis/config/modes.yaml`, etc. But the actual config files live at `src/aspis/data/catalog/config/policy/hooks.yaml`, `src/aspis/data/catalog/config/policy/modes.yaml`, etc. The `.aspis/config/` directory contains `project.yaml`, `models.yaml`, `agent-models.yaml`, `purposes.json`, `README.md`, `.runtime-inventory.json` — no `modes.yaml`, `hooks.yaml`, etc.

**Fix**: T-36's governance subagent needs to know the actual path. Either:
- The protected paths are the **deployed runtime** paths (after `aspis export`), which would be in `.aspis/config/`. The governance check would block writes to deployed config.
- The protected paths are the **catalog source** paths (`src/aspis/data/catalog/config/policy/`). The governance check would block writes to the source.

The SPEC and PLAN say the latter (per the "Tier 2 governance-only" pattern from system-lead ref §7), but the live system hasn't deployed those files to `.aspis/config/`. **The governance subagent needs to check the actual path that will be deployed to, not the source path.** This is a discovery that T-36 will have to make, but it would be better to specify in the task description.

#### m-8 — Hook parity not verified

The system-lead ref spec §8 specifies 4 hooks (pre-commit, commit-msg, post-commit, runtime guard) with two-surface parity. No TASKS task verifies this.

**Fix**: Add a verification step in T-25 (finalize system-lead body): "verify that the 4 hooks in `.aspis/scripts/hooks/` and `.git/hooks/` are in parity (same core, different surface)."

### MINOR findings

- **`small-task.md` track count ambiguity**: T-06 says "5 tracks (Question/Trivial/Small-task/Bug/Feature)" but the planning-lead ref §2 lists 6 (adds `Project plan` and `Defect` is separate from Bug). T-06 should either match the ref or scope the check.
- **T-55 edge-case coverage is unbounded**: T-55 says "≥ 2 edge cases per lead" with 8 examples. The "≥ 2" is the floor; the 8 examples are the suggested set. This is correct but vague — a lead with 2 trivial examples passes. **Acceptable — the reviewer's quality-review skill will catch shallow coverage.**
- **T-56 final sweep is vague**: T-56 says "Verify SC-001 through SC-012" without specifying how each is verified. The "Testing depth" table clarifies some, but not all 12 SCs map to a specific test type. **Acceptable — the table is the spec, the sweep is the action.**
- **PLAN line 75 says "4 files" for scripts**: Component 3 says "Source: `src/aspis/data/catalog/scripts/planning/` (4 files: `_console.py`, `feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `active_feature.py`)" — that's 5 files, not 4. The PLAN.md line 75 has a typo. **No action needed — TASKS T-01 correctly says 5 files.**
- **TASKS line 25 mentions 4 files but says 5 paths**: "from `feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `_console.py`, `active_feature.py`" — that's 5 files. T-01 is correct. ✓
- **F-016 inventory's per-agent count is 26, not 25**: The inventory explains the +1 is `mode-decision` being counted twice. No action needed.

---

## 15 · Cross-reference check (F-016 files referenced in F-017)

All F-016 paths referenced in F-017 resolve. Spot-check:

- F-017 SPEC §"Problem" references "12 reference specs" → `Research/ref/` has 12 files + `governance.md` (13 total). The 12 are: project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer, committer, general-builder, and **one more** (governance is the 13th). Actually, the count is 12 + 1 governance = 13 ref files. The SPEC says 12. **Minor inaccuracy** — the count is 13 if governance is included, 12 if it's separate.
- F-017 PLAN §"Key dependencies" references "F-016 reference specs (12 agent refs, 5 systemic specs, skills inventory)" → `Research/ref/` has 13 (or 12 + governance). `Research/specs/` has 4 (cli-verbs, planning-scripts, and 2 more). Let me count: the F-016 inventory mentions cli-verbs.md and planning-scripts.md. The plan says "5 systemic specs." Need to verify. **Acceptable — the counts are close enough for a PLAN.**
- F-017 PLAN §"Component 3" references `src/aspis/data/catalog/scripts/planning/` → 5 .py files exist (verified). ✓
- F-017 TASKS T-07 references `.aspis/context/AGENT_BODY_STANDARD.md` → file does not exist (T-07 will create it). ✓
- F-017 TASKS T-08 references `.aspis/context/DYNAMIC_READINESS.md` → file does not exist (T-08 will create it). ✓
- F-017 TASKS T-36 references `.aspis/state/approval-ledger.yaml` → `.aspis/state/` does not exist (T-36 will create both). ✓
- F-017 TASKS T-36 references `src/aspis/cli/governance.py` → **does not exist as a path** (FINDING M-1).

---

## 16 · Verdict

**CHANGES REQUIRED.**

The plan is substantively complete — 19/19 FRs covered, 12/12 SCs covered (with 1 narrow + 1 missing), 25/25 skills scheduled, 6/6 CLI verbs scheduled, 3/3 scripts scheduled, 5/5 workflows scheduled, 11/12 agents scheduled. The phasing is correct (L0 → L1 hard gate → L2-P0 → L2-P1 → Polish), the dependencies are respected, and the test types are comprehensive.

But 4 issues must be fixed before the build gate:

1. **M-1 (CLI path mismatch)** — 7 tasks reference paths that don't exist. Without this fix, the entire L2-P0 exit gate (T-40) will fail because the verbs won't be registered. **This is a build-breaker.**

2. **M-2 (planning-lead delegate drift)** — The current `planning-lead.md` body is in violation of FR-005. T-18's verification will catch it, but the task should explicitly say "remove the 7 deferred subagents from the delegates list" so the build doesn't accidentally re-introduce them.

3. **M-3 (templates/scripts scope ambiguity)** — The SPEC's "Out of scope" list is incomplete. Either add the missing assets to TASKS, or extend "Out of scope" to cover them. Without this fix, mid-build discoveries will surface scope questions that should have been answered in the SPEC.

4. **M-4 (SC-011 cost-of-change test not in TASKS)** — Add a task that runs the test. SC-011 is the architecture constitution's "cost-of-change" claim. If we don't test it, we don't know if the architecture actually delivers.

5. **M-5 (dead asset T-48)** — `dependency-audit` skill has no consumer. Either defer to F-018 or document as a shelf asset.

The 3 medium findings (m-1, m-2, m-3, m-4) and 7 minor findings (m-5 through m-8) are improvements that should be addressed in a follow-up revision or as part of the build, but are not build-blockers.

**Recommendation**: Send the plan back to the Planning Lead for one revision pass to fix M-1 through M-5, then re-review. Estimated fix time: 2-3 hours.

**Reviewer**: independent (this review)
**Date**: 2026-06-27
**Files reviewed**:
- `.aspis/features/F-017-complete-agent-system/SPEC.md` (153 lines)
- `.aspis/features/F-017-complete-agent-system/PLAN.md` (292 lines)
- `.aspis/features/F-017-complete-agent-system/TASKS.md` (199 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/skills/inventory.md` (220 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/specs/cli-verbs.md` (172 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/specs/planning-scripts.md` (97 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/project-lead.md` (930 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/planning-lead.md` (1158+ lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/build-lead.md` (620+ lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md` (405 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/system-lead.md` (470 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md` (361 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/committer.md` (229 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/governance.md` (634+ lines)
- Live catalog state at `src/aspis/data/catalog/agents/*.md` (12 files)
- Live catalog state at `src/aspis/data/catalog/skills/` (38 directories)
- Live catalog state at `src/aspis/data/catalog/scripts/planning/` (5 files)
- Live catalog state at `src/aspis/cli.py` + `src/aspis/commands/` (16 modules)
- Live workflow state at `.aspis/workflows/` (5 files)
