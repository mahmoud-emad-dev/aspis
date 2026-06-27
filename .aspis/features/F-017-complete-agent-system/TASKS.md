# F-017 — Tasks

Format: `- [ ] T-NN [P?] [US?] <description> (<exact file paths>)`
- `T-NN` — sequential task id, in execution order.
- `[P]` — optional: parallelizable (different files, no dependency).
- `[US?]` — the user story this serves (US1=L0, US2=L1, US3=L2-P0, US4=L2-P1).
- Always name exact file paths in backticks.

> Mode: **production** — phased, tests-first per story, small tasks.

## Dependencies & execution order
```
Phase 0 (L0 Setup) → Phase 1 (L0 Foundational) → Phase 2 (L1 Per-Lead) → HARD GATE →
Phase 3 (L2-P0) → Phase 4 (L2-P1) → Phase 5 (Polish)
```
- Within a phase, tasks marked `[P]` run in parallel (different files, no shared state).
- L1 agents are independent of each other — all 8 can proceed in parallel once L0 completes.
- **HARD GATE after Phase 2**: owner review before any L2 work begins. Do NOT roll into L2.

---

## Phase 0 — L0 Setup (scripts + workflows)
Shared scaffolding everything else needs. Blocked by: nothing.

- [ ] **T-01** [US1] Deploy 5 planning scripts from catalog source to `.aspis/scripts/planning/` — byte-for-byte copy from `src/aspis/data/catalog/scripts/planning/feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `_console.py`, `active_feature.py` to `.aspis/scripts/planning/`. Validate: AST parse + `--help` exits 0 per script. (`src/aspis/data/catalog/scripts/planning/*` → `.aspis/scripts/planning/*`)
- [ ] **T-01a** [P] [US1] Deploy 5 planning templates from catalog source to `.aspis/templates/planning/` — byte-for-byte copy from `src/aspis/data/catalog/templates/planning/SPEC.md`, `PLAN.md`, `TASKS.md`, `ACCEPTANCE.md`, `TASK_PACKET.md` to `.aspis/templates/planning/`. Validate: each file exists, is valid markdown with correct section headers. (`src/aspis/data/catalog/templates/planning/*` → `.aspis/templates/planning/*`)
- [ ] **T-02** [P] [US1] Verify `plan.md` workflow completeness against planning-lead reference spec phases P0–P8. Fill gaps; remove TODO/NYI markers; align step names. (`.aspis/workflows/plan.md`)
- [ ] **T-03** [P] [US1] Verify `build.md` workflow completeness against build-lead reference spec 9-step loop. Fill gaps; remove TODO/NYI markers. (`.aspis/workflows/build.md`)
- [ ] **T-04** [P] [US1] Verify `review.md` workflow completeness against reviewer reference spec 9 dimensions + 4 verdicts. Fill gaps; remove TODO/NYI markers. (`.aspis/workflows/review.md`)
- [ ] **T-05** [P] [US1] Verify `fix.md` workflow completeness against fix-lead reference spec 6-step spine. Fill gaps; remove TODO/NYI markers. (`.aspis/workflows/fix.md`)
- [ ] **T-06** [P] [US1] Verify `small-task.md` workflow completeness — confirm all 5 tracks (Question/Trivial/Small-task/Bug/Feature) are represented. Fill gaps; remove TODO/NYI markers. (`.aspis/workflows/small-task.md`)

**Checkpoint**: Scripts deployed and validated. All 5 workflows complete with no TODO markers.

---

## Phase 1 — L0 Foundational (conventions + shared P0 skills)
Establishes the contracts every later layer follows. Blocked by: Phase 0 complete.

- [ ] **T-07** [US1] Author agent-body standard document — required frontmatter fields, required body sections (Identity / How you work / Core rules / Responsibilities→skills / Delegation / Dynamic-readiness), thin-agent rule, cite-don't-restate rule, checkable checklist. (`.aspis/context/AGENT_BODY_STANDARD.md`)
- [ ] **T-08** [US1] Author dynamic-readiness convention document — the 3 dials (mode, task kind/scope, model capability), key distinction (optimize path, never bar), leanest-correct-path default, how agents read dials from existing infrastructure. (`.aspis/context/DYNAMIC_READINESS.md`)
- [ ] **T-08a** [US1] **R-008 gate**: Owner reviews and approves `DYNAMIC_READINESS.md` before any agent body references it. Create owner-approval artifact at `.aspis/features/F-017-complete-agent-system/ACCEPTANCE.md` recording the approval. Blocked until owner signs off — do not proceed to T-09 without this approval. (`.aspis/features/F-017-complete-agent-system/ACCEPTANCE.md`)
- [ ] **T-09** [P] [US1] Author `mode-decision` skill — infer build mode from risk/scope, auto-escalation/downgrade rules, owned by planning-lead + project-lead. (`src/aspis/data/catalog/skills/mode-decision/SKILL.md`)
- [ ] **T-10** [P] [US1] Author `recontextualization` skill — translate a lead's return into project-aware language: read → fold → translate → decide. Owned by project-lead. (`src/aspis/data/catalog/skills/recontextualization/SKILL.md`)
- [ ] **T-11** [P] [US1] Author `constitution-checks` skill — audit a PLAN against the 12 architecture-constitution rules; emit CONSTITUTION_CHECK report. Owned by planning-lead. (`src/aspis/data/catalog/skills/constitution-checks/SKILL.md`)
- [ ] **T-12** [P] [US1] Author `constitution-check` skill — apply the 9 reviewer-owned constitution checks before verdict. Owned by reviewer. (`src/aspis/data/catalog/skills/constitution-check/SKILL.md`)
- [ ] **T-13** [P] [US1] Author `evidence-validation` skill — codify "verify, don't trust"; what counts as evidence per review dimension. Owned by reviewer. (`src/aspis/data/catalog/skills/evidence-validation/SKILL.md`)
- [ ] **T-14** [P] [US1] Author `packet-validation` skill — 4 packet checks (scope, feasibility, completeness, acceptance) with V0–V4 maturity scaling. Owned by build-lead. (`src/aspis/data/catalog/skills/packet-validation/SKILL.md`)
- [ ] **T-15** [P] [US1] Author `builder-selection` skill — pick builder tier (cheap/standard/deep) per packet version (V0–V4) and risk; V0–V1→cheap, V2→standard, V3–V4→deep. Owned by build-lead. (`src/aspis/data/catalog/skills/builder-selection/SKILL.md`)

**Checkpoint**: Agent-body standard + dynamic-readiness convention documented. 7 shared P0 skills authored to catalog pattern.

---

## Phase 2 — L1 Per-Lead Core (8 leads)
Each lead gets a final body + its own P0 skills. All 8 are independent once L0 is done.
**Exit gate**: plan→build→review→commit runs end-to-end on cheap+standard. HARD STOP for owner review.

### Project Lead
- [ ] **T-16** [US2] Author `session-continuation` skill — detect interruption, classify resumption (pause/crash/timeout/left), send resume packet. Owned by project-lead. (`src/aspis/data/catalog/skills/session-continuation/SKILL.md`)
- [ ] **T-17** [US2] Finalize project-lead body — verify against agent-body standard; add Identity / How you work / Core rules / Responsibilities→skills / Delegation / Dynamic-readiness sections; wire L0 skills (mode-decision, recontextualization, session-continuation) + existing skills; verify permission surface matches ref spec (no edit/write except `aspis mode`, bash allowlist, deny floor); verify delegation edges (planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer all exist). (`src/aspis/data/catalog/agents/project-lead.md`)

### Planning Lead
- [ ] **T-18** [US2] Finalize planning-lead body — verify against agent-body standard; add missing sections; wire L0 skills (mode-decision, constitution-checks) + existing 7 core skills + recommended (deterministic-first, scope-control); verify permission surface (feature artifacts only, bash allowlist, deny floor); verify delegates — ONLY existing agents: research-lead, reviewer, project-explorer. **Strip the 7 non-existent L3 subagents** (clarify, task-decomposer, idea-capture, prd-writer, constitution-checker, scope-estimator, research-request-writer) from frontmatter delegates list. Acceptance: 0 orphan delegates. (`src/aspis/data/catalog/agents/planning-lead.md`)

### Build Lead
- [ ] **T-19** [US2] Finalize build-lead body — verify against agent-body standard; add missing sections; wire L0 skills (packet-validation, builder-selection) + existing 6 skills; verify permission surface (orchestration artifacts only, product code delegated, bash allowlist, deny floor); verify delegates (general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead exist). (`src/aspis/data/catalog/agents/build-lead.md`)

### Reviewer
- [ ] **T-20** [US2] Author `security-review` skill — OWASP top 10, injection, authz, secret scan, exposure check before verdict. Owned by reviewer. (`src/aspis/data/catalog/skills/security-review/SKILL.md`)
- [ ] **T-21** [US2] Finalize reviewer body — verify against agent-body standard; add missing sections; wire L0 skills (constitution-check, evidence-validation) + own skill (security-review) + existing 5 skills; verify permission surface (read-only — no edit/write tools, bash allowlist, deny floor); verify delegates (project-explorer, research-lead exist). (`src/aspis/data/catalog/agents/reviewer.md`)

### System Lead
- [ ] **T-22** [US2] Author `catalog-validator` skill — structural check: refs resolve, no broken links, schema valid, no orphans. Owned by system-lead. (`src/aspis/data/catalog/skills/catalog-validator/SKILL.md`)
- [ ] **T-23** [US2] Author `governance-approval` skill — R-008 human-gate workflow for rules/permissions/model-routing/security changes. Owned by system-lead. (`src/aspis/data/catalog/skills/governance-approval/SKILL.md`)
- [ ] **T-24** [US2] Author `drift-detector` skill — detect catalog↔live frontmatter drift per field per agent. Owned by system-lead. (`src/aspis/data/catalog/skills/drift-detector/SKILL.md`)
- [ ] **T-25** [US2] Finalize system-lead body — verify against agent-body standard; add missing sections; wire own skills (catalog-validator, governance-approval, drift-detector) + existing 7 skills; verify permission surface (system assets only, named bash allowlist NOT `*`, `webfetch: allow`, `websearch: deny`, deny floor); verify delegates (project-explorer, reviewer, committer exist). (`src/aspis/data/catalog/agents/system-lead.md`)

### Fix Lead
- [ ] **T-26** [US2] Finalize fix-lead body — verify against agent-body standard; add missing sections; wire existing 6 skills; verify permission surface (read/write allow for debugging, tight bash allowlist, deny floor); verify delegates (reviewer, test-lead, committer, project-explorer exist). (`src/aspis/data/catalog/agents/fix-lead.md`)

### Test Lead
- [ ] **T-27** [US2] Finalize test-lead body — verify against agent-body standard; add missing sections; wire existing 2 skills; verify permission surface (read/write allow for tests/reports, tight bash allowlist, deny floor); verify delegates (project-explorer exist). (`src/aspis/data/catalog/agents/test-lead.md`)

### Research Lead
- [ ] **T-28** [US2] Author `cache-management` skill — enforce cache-first discipline; route to research only on cache miss. Owned by research-lead. (`src/aspis/data/catalog/skills/cache-management/SKILL.md`)
- [ ] **T-29** [US2] Author `harvest-protocol` skill — 7-step R-008-gated path for bringing external skill/source into catalog. Owned by research-lead. (`src/aspis/data/catalog/skills/harvest-protocol/SKILL.md`)
- [ ] **T-30** [US2] Finalize research-lead body — verify against agent-body standard; add missing sections; wire own skills (cache-management, harvest-protocol) + existing 3 skills; verify permission surface (tightest in system: write new files only, edit deny, bash deny except context scripts, `webfetch`/`websearch` allow, deny floor); verify delegates (project-explorer exist). (`src/aspis/data/catalog/agents/research-lead.md`)

### L1 Gate
- [ ] **T-31** [US2] Cross-agent consistency sweep — verify 0 broken skill references across all 8 lead frontmatters; verify every delegate listed in a body exists as a catalog agent; verify no agent has `bash: '*': allow`; verify all deny-floor permissions honored (committer-only `git commit*`, none `git push*`, `webfetch` system-lead + research-lead only, `websearch` research-lead-only). Run manual cross-reference check across all 8 agent bodies. (`src/aspis/data/catalog/agents/*.md`)
- [ ] **T-32** [US2] **L1 EXIT GATE** — run plan→build→review→commit end-to-end on a sample feature using only cheap and standard model tiers. Verify: planning-lead plans → build-lead delegates to builder → reviewer reviews → committer commits. All gates pass. 0 deep model invocations. **HARD STOP — owner reviews before L2 begins. Do NOT roll into T-33.**
- [ ] **T-32a** [US2] **Owner-approval artifact** — owner signs off on L1 exit gate results. Record the approval in `.aspis/features/F-017-complete-agent-system/ACCEPTANCE.md` (append to the T-08a entry). **T-33 depends on this approval — do not build any L2 task without it.** (`.aspis/features/F-017-complete-agent-system/ACCEPTANCE.md`)

**Checkpoint**: All 8 lead bodies finalized. All L0/L1 skills authored. Cross-agent consistency verified. Core loop runs end-to-end. **OWNER REVIEW HERE.**

---

## Phase 3 — L2-P0 (CLI verbs + governance + leaf agents)
Blocked by: L1 owner approval. Builds the deterministic validation spine and the workers.

### CLI Verbs (3 P0)
- [ ] **T-33** [US3] Build `validate-runtime` CLI verb — reads all catalog agents; checks structural validity (required frontmatter fields present, skill refs resolve, delegate refs resolve, no orphan delegates); exits 0 when all pass; reports per-agent pass/fail with file:line evidence on failure. **Also folds in the cross-agent consistency check** — 0 broken skill refs, 0 orphan delegates — so no separate cross_ref script is needed. Expose `register(subparsers)`, list in `COMMAND_MODULES` in `src/aspis/commands/__init__.py`, dispatched from `src/aspis/cli.py`. (`src/aspis/commands/validate_runtime.py`)
- [ ] **T-34** [US3] Build `byte-parity` CLI verb — **read-only reporter** over the existing rendering/protection pipeline (`plan_export`/`write_export`/`protect`). Renders each catalog agent in-memory; checks catalog self-consistency (render matches expected output shape, no broken refs, no missing fields); reports CLEAN/CONFLICT/PROTECT per protection engine contract; exits 0 when all CLEAN. Does NOT reimplement rendering or protection. Live `.opencode`/`.claude` parity verified only after the owner's manual post-F-017 `aspis export`. Expose `register(subparsers)`, list in `COMMAND_MODULES`, dispatched from `src/aspis/cli.py`. Acceptance: no duplication of rendering/protection engine. (`src/aspis/commands/byte_parity.py`)
- [ ] **T-35** [US3] Build `export` CLI verb — **thin wrapper** over the existing `plan_export`/`write_export`/`protect` pipeline (reconciles with `aspis init` — same pipeline, single source). Renders all catalog agents for target runtime(s); applies protection engine (CONFLICT/PROTECT); `--dry-run` reports plan without writing; preserves `permission:` block in Claude Code adapter output (fix stripping bug in `src/aspis/runtimes/claude.py`). Expose `register(subparsers)`, list in `COMMAND_MODULES`, dispatched from `src/aspis/cli.py`. Acceptance: no duplication of rendering/protection engine. (`src/aspis/commands/export_cmd.py`)

### Governance Subagent (minimal — R-008 backbone)
- [ ] **T-36** [US3] Build governance subagent — deterministic script matching **governance.md §6 verbatim**. 6 subcommands: `request --paths <path> [<path>...] --reason <text>`, `approve <request-id> --approver <name> [--expiry <ISO-date>] [--glob-approval]` (**--approver REQUIRED** — dropping it is a forbidden R-008 redesign), `audit [--since <date>] [--approver <name>]`, `revoke <request-id> --approver <name>`, `check <path>`, `ledger`. Append-only approval ledger at `.aspis/state/approval-ledger.yaml` with fields: `id`, `paths`, `reason`, `approver`, `expiry`, `glob_approval`, `status`, `timestamp`. Exact-match path check against protected paths set. `check <protected-path>` blocks without active (non-revoked, non-expired) approval. Process-level file lock on ledger writes; stale lock detection >60s. Expose `register(subparsers)`, list in `COMMAND_MODULES`, dispatched from `src/aspis/cli.py`. Minimal boundary-check — don't gold-plate. (`src/aspis/commands/governance.py`, `.aspis/state/approval-ledger.yaml`)

### Leaf Agents (3)
- [ ] **T-37** [US3] Author and finalize committer body — verify against agent-body standard; verify 3 existing skills (clean-tree-precondition, commit-message, commit-splitting) resolve; author missing sections (Identity / How you work / Core rules / Responsibilities→skills / Delegation (none — leaf) / Dynamic-readiness); verify permission surface (no edit/write tools, `git commit*` allowed, `git push*` denied, bash allowlist, no task block). (`src/aspis/data/catalog/agents/committer.md`)
- [ ] **T-38** [US3] Author and finalize general-builder body — verify against agent-body standard; verify 2 existing skills (prestart-checks, clean-tree-precondition) resolve; author missing sections (Identity / How you work / Core rules / Responsibilities→skills / Delegation (none — leaf) / Dynamic-readiness); verify permission surface (path-scoped edits, max-turns cap, no commit, no delegation, bash allowlist, no task block). (`src/aspis/data/catalog/agents/general-builder.md`)
- [ ] **T-39** [US3] Author and finalize project-explorer body — verify against agent-body standard; procedural agent (no named skills needed); author missing sections (Identity / How you work / Core rules / Responsibilities→skills / Delegation (none — leaf)); verify permission surface (no edit/write tools, bash allowlist for context scripts + git status/log/diff, `webfetch`/`websearch` denied, no task block). (`src/aspis/data/catalog/agents/project-explorer.md`)

### L2-P0 Gate
- [ ] **T-40** [US3] L2-P0 integration check — `aspis validate-runtime --runtime all` exits 0 (includes cross-agent consistency); `aspis byte-parity --dry-run` reports catalog self-consistency CLEAN; `aspis export --dry-run` exits 0 and reports correct plan; `aspis governance check rules/system-rules.md` blocks (no active approval). All 3 leaf agents pass body standard check.

**Checkpoint**: CLI validation spine functional. Governance blocks protected writes. Leaf agents complete. System can validate itself.

---

## Phase 4 — L2-P1 (remaining skills + P1 verbs + edge cases)
Blocked by: Phase 3 complete. Builds depth, quality, and edge-case robustness.

### P1 Skills (6 in L2-P1; session-continuation authored in L1/T-16)
- [ ] **T-41** [P] [US4] Author `byte-parity-checker` skill — prove catalog regenerates live runtime byte-for-byte; refuse export on mismatch. Owned by system-lead. (`src/aspis/data/catalog/skills/byte-parity-checker/SKILL.md`)
- [ ] **T-42** [P] [US4] Author `export-manager` skill — plan/apply export with ADD/UNCHANGED/UNKNOWN/UPDATE/PROTECT/CONFLICT decisions. Owned by system-lead. (`src/aspis/data/catalog/skills/export-manager/SKILL.md`)
- [ ] **T-43** [P] [US4] Author `finding-format` skill — required fields and severity rubric (CRITICAL/HIGH/MEDIUM/LOW) for review findings. Owned by reviewer. (`src/aspis/data/catalog/skills/finding-format/SKILL.md`)
- [ ] **T-44** [P] [US4] Author `model-router` skill — resolve model tier via 5-layer precedence (pin > per-agent > cap > project > global). Owned by system-lead. (`src/aspis/data/catalog/skills/model-router/SKILL.md`)
- [ ] **T-45** [P] [US4] Author `runtime-author` skill — author one runtime asset per adapter (OpenCode/Claude); single source, adapter-translated. Owned by system-lead. (`src/aspis/data/catalog/skills/runtime-author/SKILL.md`)
- [ ] **T-46** [P] [US4] Author `scope-compliance` skill — cross-check diff vs packet allowed/forbidden; enforce R-001. Owned by reviewer. (`src/aspis/data/catalog/skills/scope-compliance/SKILL.md`)

### P2 Skills (4; dependency-audit deferred to F-018)
- [ ] **T-47** [P] [US4] Author `commit-readiness` skill — verify hooks ran, no secrets, protected paths untouched, valid message before commit. Owned by reviewer. (`src/aspis/data/catalog/skills/commit-readiness/SKILL.md`)
- [ ] **T-48** [P] [US4] Author `hook-author` skill — author new hook (git or runtime) with parity test. Owned by system-lead. (`src/aspis/data/catalog/skills/hook-author/SKILL.md`)
- [ ] **T-49** [P] [US4] Author `model-inventory` skill — read runtime model inventory; surface staleness of `model_catalog.yaml`. Owned by system-lead. (`src/aspis/data/catalog/skills/model-inventory/SKILL.md`)
- [ ] **T-50** [P] [US4] Author `profile-manager` skill — create, inherit, merge profiles (defaults.yaml + per-project overrides). Owned by system-lead. (`src/aspis/data/catalog/skills/profile-manager/SKILL.md`)

### P1 CLI Verbs (3)
- [ ] **T-51** [US4] Build `validate-index` CLI verb — checks FILE_REGISTRY.yaml and CODE_MAP.md for staleness; exits 0 when fresh; reports stale files with file:line evidence. Expose `register(subparsers)`, list in `COMMAND_MODULES`, dispatched from `src/aspis/cli.py`. (`src/aspis/commands/validate_index.py`)
- [ ] **T-52** [US4] Build `drift` CLI verb — per-field per-agent catalog↔live drift detection; reports field-level drift with file:line evidence; exits 0 when no drift. Expose `register(subparsers)`, list in `COMMAND_MODULES`, dispatched from `src/aspis/cli.py`. (`src/aspis/commands/drift.py`)
- [ ] **T-53** [US4] Complete `governance` verb — if T-36 left any subcommands as stubs, fill them; ensure all 6 subcommands (request, approve, audit, revoke, check, ledger) match governance.md §6 signatures. (`src/aspis/commands/governance.py`)

### Edge-Case Coverage
- [ ] **T-54** [US4] Add edge-case coverage to lead agent bodies — for each of the 8 leads, add at least 2 error-handling / edge-case sections drawn from the agent's reference spec Error Handling section. Examples: planning-lead (stuck-on-ambiguous-request, mode-mismatch), build-lead (builder-timeout, packet-impossible), reviewer (same-model-contamination, no-evidence-verdict), system-lead (self-modification-guard, export-conflict), fix-lead (cannot-reproduce, scope-expansion), test-lead (flaky-classification, environment-issues), research-lead (cache-staleness, source-authority-conflict), project-lead (delegation-loop, concurrent-request). Review routing: sub-reviewer (medium risk — per-agent, additive content). (`src/aspis/data/catalog/agents/project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`, `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`)

**Checkpoint**: All 24 missing skills authored (13 P0 + 6 P1 + 4 P2 + session-continuation in L1). All 6 CLI verbs functional. Edge cases covered. System is robust.

---

## Phase 5 — Polish
Cross-cutting final sweep. Blocked by: Phase 4 complete.

- [ ] **T-55** [US4] Final acceptance sweep — run all systemic gates: `aspis validate-runtime --runtime all` exits 0 (includes cross-agent consistency), `aspis byte-parity --dry-run` reports catalog self-consistency CLEAN (live parity verified after owner's manual export), `aspis export --dry-run` exits 0 and reports correct plan, 0 broken skill refs across all 12 agent bodies, 0 orphan delegates, 0 missing deny-floor permissions. Verify SC-001 through SC-012 from SPEC, including SC-011 cost-of-change test (hypothetical new leaf agent or skill ≤3 files). Update RECENT_CHANGES.md. Review routing: sub-reviewer (low risk — validation sweep).

**Checkpoint**: F-017 complete. All acceptance criteria met. Ready for owner acceptance review.

---

## Implementation strategy

- **L0-first**: Complete Phase 0 + Phase 1 before any agent work. The conventions and shared skills are the contract.
- **L1 parallel**: All 8 leads can be worked on independently once L0 is done. Within a lead, skills before body.
- **HARD GATE after L1**: Owner reviews the working core loop before any L2 investment. Do NOT proceed to T-33 without approval.
- **L2-P0 before L2-P1**: The validation spine (CLI verbs) and governance mechanism are prerequisites for P1 depth work.
- **P1/P2 skills parallel**: All 10 remaining skills (T-41 through T-50) are independent — can be authored concurrently.
- **Incremental validation**: Every phase ends with a checkpoint gate. Don't accumulate untested work.

## Review routing

| Risk level | Tasks | Reviewer |
|---|---|---|
| **High** (governance, permissions, CLI verbs) | T-33, T-34, T-35, T-36 | Reviewer lead (full review) |
| **Medium** (agent bodies, shared skills) | T-07 through T-30, T-37, T-38, T-39 | Sub-reviewer or peer check |
| **Low** (P1/P2 skills, edge cases, polish) | T-41 through T-55 | Sub-reviewer (low risk) |

## Testing depth

| Test type | Applies to | Command |
|---|---|---|
| **AST parse** | All scripts + CLI verbs | `python -c "import ast; ast.parse(open('...').read())"` |
| **--help** | All scripts + CLI verbs | `python <script> --help` (exit 0) |
| **Dry-run** | validate-runtime, byte-parity, export, validate-index, drift | `aspis <verb> --dry-run` (exit 0) |
| **Structural validation** | All 12 agent bodies | `aspis validate-runtime` — 0 broken skill refs, 0 orphan delegates (folded into T-33) |
| **Standard shape check** | All 12 agent bodies | Required sections present; no duplicated content |
| **End-to-end loop** | L1 exit gate | Sample feature: plan → build → review → commit on cheap+standard |
| **Permission audit** | All 12 agent bodies | No `bash: '*': allow`; deny floor honored |
| **Governance block** | Protected path write | `aspis governance check <protected-path>` blocks |

## Task summary

| Phase | Tasks | Story | Checkpoint |
|---|---|---|---|
| 0 — L0 Setup | T-01 … T-06, T-01a | US1 | Scripts + templates deployed, workflows complete |
| 1 — L0 Foundational | T-07 … T-15, T-08a | US1 | Conventions approved + 7 shared skills authored |
| 2 — L1 Per-Lead | T-16 … T-32, T-32a | US2 | 8 leads finalized; core loop runs end-to-end. **OWNER REVIEW.** |
| 3 — L2-P0 | T-33 … T-40 | US3 | CLI verbs + governance + leaf agents functional |
| 4 — L2-P1 | T-41 … T-54 | US4 | 10 remaining skills + P1 verbs + edge cases |
| 5 — Polish | T-55 | US4 | Final acceptance sweep. F-017 complete. |

**Total: 58 tasks** across 5 phases, 4 user stories.
