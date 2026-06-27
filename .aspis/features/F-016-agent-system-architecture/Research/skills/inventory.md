# Missing Skills Inventory — F-016

> Generated from cross-referencing all 11 agent catalog files and 8 lead reference specs
> against the existing skills catalog at `src/aspis/data/catalog/skills/`.
>
> Sources:
> - 11 agent files at `src/aspis/data/catalog/agents/*.md` (project-lead, planning-lead,
>   build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer,
>   general-builder, project-explorer) plus `bootstrap.md`
> - 8 lead reference specs at `.aspis/features/F-016-agent-system-architecture/Research/ref/`
>   (the 3 leaf specs — committer, general-builder, project-explorer — were skipped per task
>   scope; their frontmatter-only skill sets are already covered in the agent file scan)

## Summary

- **Total unique skills referenced**: 63
- **Skills with existing catalog entries**: 38
- **Missing skills (need new SKILL.md)**: 25
- **Priority breakdown**: P0: 13 | P1: 7 | P2: 5

> The 63 total combines 42 unique skills referenced in agent `skills:` frontmatter fields
> (across all 11 agents + bootstrap) and 21 additional skills referenced in lead reference
> spec Responsibility tables / "Missing skills" / "Recommended skill additions" sections.
> 4 of the 42 frontmatter-referenced skills are missing; the remaining 21 are ref-spec-only.

## Existing skills (baseline)

The 38 directories present in `src/aspis/data/catalog/skills/`:

| # | Skill | Source agent |
|---|---|---|
| 1 | acceptance-decision | reviewer |
| 2 | architecture-planning | planning-lead |
| 3 | asset-authoring | system-lead |
| 4 | build-readiness | build-lead |
| 5 | clean-tree-precondition | committer, general-builder |
| 6 | commit-message | committer |
| 7 | commit-splitting | committer |
| 8 | config-management | system-lead |
| 9 | context-ladder | project-lead, planning-lead, build-lead, reviewer, fix-lead, research-lead |
| 10 | context-packaging | project-lead |
| 11 | corrective-fix | fix-lead |
| 12 | deterministic-first | planning-lead, system-lead |
| 13 | feature-planning | planning-lead |
| 14 | knowledge-packaging | research-lead |
| 15 | knowledge-research | research-lead |
| 16 | lead-routing | project-lead |
| 17 | plan-critic | reviewer |
| 18 | planning-intake | planning-lead |
| 19 | prestart-checks | planning-lead, build-lead, system-lead, fix-lead, general-builder, bootstrap |
| 20 | project-awareness | project-lead |
| 21 | project-guidance | project-lead |
| 22 | project-health | project-lead |
| 23 | project-onboarding | bootstrap |
| 24 | project-question-answering | project-lead |
| 25 | quality-review | reviewer |
| 26 | request-classification | project-lead |
| 27 | requirement-clarification | planning-lead |
| 28 | review-strategy | reviewer |
| 29 | root-cause-analysis | fix-lead |
| 30 | scope-control | planning-lead, build-lead, fix-lead |
| 31 | selective-testing | build-lead, fix-lead |
| 32 | system-awareness | system-lead |
| 33 | system-repair | system-lead |
| 34 | system-validation | system-lead |
| 35 | task-decomposition | planning-lead |
| 36 | task-orchestration | build-lead |
| 37 | test-execution | test-lead |
| 38 | test-generation | test-lead |

## Missing skills inventory

Sorted by priority (P0 → P1 → P2), then alphabetically within tier.

### P0 — Blocking (core loop, system integrity, or R-008-gated)

| # | Skill Name | Purpose (1 line) | Owning Agent(s) | Priority | Est. Sections |
|---|---|---|---|---|---|
| 1 | builder-selection | Pick the right builder tier (cheap / standard / deep) per packet version and risk matrix | build-lead | P0 | 4 |
| 2 | cache-management | Enforce cache-first discipline: scan both cache locations, decide hit-fresh / hit-stale / miss, route to research step only on miss | research-lead | P0 | 5 |
| 3 | catalog-validator | Structural check on the catalog: every reference resolves, no broken links, schema valid, no orphan assets | system-lead | P0 | 4 |
| 4 | constitution-check | Apply the 9 reviewer-owned architecture-constitution checks to any change before verdict | reviewer | P0 | 6 |
| 5 | constitution-checks | Audit PLAN against the 12 architecture-constitution rules and emit a CONSTITUTION_CHECK report | planning-lead | P0 | 6 |
| 6 | drift-detector | Detect catalog↔live frontmatter drift per field per agent; emit a drift report for system-lead to act on | system-lead | P0 | 4 |
| 7 | evidence-validation | Codify "verify, don't trust" — what counts as evidence per dimension, evidence hierarchy, when to withhold verdict | reviewer | P0 | 4 |
| 8 | governance-approval | R-008 human-gate workflow: request approval, record decision, audit trail; the only sanctioned path to rules/permissions/model-routing/security changes | system-lead | P0 | 5 |
| 9 | harvest-protocol | 7-step R-008-gated path for bringing external skill/source into the catalog: candidate → record → license → adapt → prove → review → promote | research-lead | P0 | 6 |
| 10 | mode-decision | Named procedure for inferring the build mode (vibe / mvp / production) from risk and scope, with auto-escalation and auto-downgrade rules | planning-lead, project-lead | P0 | 5 |
| 11 | packet-validation | Run the 4 packet validation checks (scope, feasibility, completeness, acceptance) with packet-maturity-scaled actions (V0–V4) | build-lead | P0 | 5 |
| 12 | recontextualization | Named procedure for translating a lead's return into project-aware language: read return → fold into state → translate → decide next hop | project-lead | P0 | 4 |
| 13 | security-review | Apply OWASP top 10, injection analysis, authz review, secret scan, and exposure check to a change before verdict | reviewer | P0 | 6 |

### P1 — Important (quality / validation / repair; should be built soon after P0)

| # | Skill Name | Purpose (1 line) | Owning Agent(s) | Priority | Est. Sections |
|---|---|---|---|---|---|
| 14 | byte-parity-checker | Prove the catalog regenerates live runtime byte-for-byte; emit parity report and refuse export on mismatch | system-lead | P1 | 4 |
| 15 | export-manager | Plan and apply catalog export; handle ADD / UNCHANGED / UNKNOWN / UPDATE / PROTECT / CONFLICT decisions; manage `ASPIS_ALLOW_PROTECTED` gate | system-lead | P1 | 5 |
| 16 | finding-format | Required fields (file:line, what's wrong, why it matters, severity, fix, evidence) and severity rubric (CRITICAL/HIGH/MEDIUM/LOW) | reviewer | P1 | 4 |
| 17 | model-router | Resolve model tier via the 5-layer precedence (per-(runtime,agent) pin > per-agent > per-(runtime,capability) > per-capability > project > global) | system-lead | P1 | 5 |
| 18 | runtime-author | Author one runtime asset correctly per adapter (OpenCode / Claude) — single source, adapter-translated, never hand-written per runtime | system-lead | P1 | 5 |
| 19 | scope-compliance | Cross-check diff vs packet allowed/forbidden, enforce R-001, emit scope finding | reviewer | P1 | 4 |
| 20 | session-continuation | Detect interruption state, classify resumption type (pause / crash / timeout / user-left), send a "resume" packet (not a fresh packet) to the owning lead | project-lead | P1 | 4 |

### P2 — Nice-to-have (docs / guidance / health; fills a gap but system operates without it)

| # | Skill Name | Purpose (1 line) | Owning Agent(s) | Priority | Est. Sections |
|---|---|---|---|---|---|
| 21 | commit-readiness | Verify pre-commit hook ran, secrets absent, protected paths untouched, message format valid, before signaling "ready to commit" | reviewer | P2 | 4 |
| 22 | dependency-audit | Multi-feature dependency analysis — build a dependency graph from PLANs, surface circular dependencies and ordering issues | planning-lead (future dependency-analyzer subagent) | P2 | 4 |
| 23 | hook-author | Author a new hook (git or runtime) with the parity test that proves git and runtime surfaces share the same core | system-lead | P2 | 4 |
| 24 | model-inventory | Read the runtime model inventory; run `aspis models --available`; surface staleness of `model_catalog.yaml` | system-lead | P2 | 4 |
| 25 | profile-manager | Create, inherit, and merge profiles (`profiles/defaults.yaml` and per-project overrides) | system-lead | P2 | 4 |

### Priority definitions

- **P0**: Blocking — the core loop cannot operate without this skill, or it is R-008 / system-integrity territory that must be enforced before any further work. Build first.
- **P1**: Important — major quality / validation / repair gap; the system can run without it but ships with risk. Build soon after P0 is done.
- **P2**: Nice-to-have — fills a known gap but the system operates without it; build when adjacent work makes it cheap, or defer to a later feature.

## Per-agent skill gap summary

| Agent | Skills Referenced | Existing | Missing | Missing Names |
|---|---|---|---|---|
| project-lead | 11 (8 frontmatter + 3 ref) | 8 | 3 | recontextualization, session-continuation, mode-decision |
| planning-lead | 12 (11 frontmatter + 1 ref) | 9 | 3 | mode-decision, constitution-checks, dependency-audit |
| build-lead | 8 (all frontmatter) | 6 | 2 | packet-validation, builder-selection |
| reviewer | 11 (5 frontmatter + 6 ref) | 5 | 6 | security-review, constitution-check, evidence-validation, finding-format, scope-compliance, commit-readiness |
| system-lead | 17 (7 frontmatter + 10 ref) | 7 | 10 | governance-approval, catalog-validator, drift-detector, byte-parity-checker, runtime-author, export-manager, model-router, profile-manager, hook-author, model-inventory |
| fix-lead | 6 (all frontmatter) | 6 | 0 | — |
| test-lead | 2 (all frontmatter) | 2 | 0 | — |
| research-lead | 5 (3 frontmatter + 2 ref) | 3 | 2 | cache-management, harvest-protocol |
| committer | 3 (all frontmatter) | 3 | 0 | — |
| general-builder | 2 (all frontmatter) | 2 | 0 | — |
| project-explorer | 0 (empty frontmatter) | 0 | 0 | — |
| bootstrap | 2 (all frontmatter) | 2 | 0 | — |

> Note: `mode-decision` is counted in both project-lead and planning-lead because it is
> referenced in both agents' frontmatter (and called out separately in the project-lead
> ref spec as a recommended new skill). The unique-missing count (25) and the per-agent
> sum (26) differ by 1 for this reason.

## Notes

### Edge cases found

- **`mode-decision` is owned by two agents.** It appears in the planning-lead frontmatter
  *and* in the project-lead ref spec's "Recommended new skills" table. It is a single
  skill with two consumers; build once and grant both agents the allowlist.
- **`project-explorer` declares no skills** in its frontmatter and has no ref-spec
  "Responsibilities → skills" additions either. It is intentionally minimal (read-only
  helper, no orchestration intelligence of its own).
- **`bootstrap` is not in the 11 main agents** but is a 12th catalog agent with two
  skills (prestart-checks, project-onboarding) — both already exist. It is included for
  completeness because the task says "all 11 catalog agent files" and the bootstrap file
  is the actual onboarding file. If the strict-11 reading is required, subtract it.
- **`dependency-audit` is for a future subagent**, not for planning-lead itself. The
  planning-lead ref spec (§6, `dependency-analyzer`) marks it as "Future — only needed
  for multi-feature planning." It is recorded as P2 and as a "deferred / future"
  addition, not a current gap.
- **Skills marked "Sufficient" in the ref spec body but listed in the missing table** —
  none found. The ref specs are honest about which skills need work.

### Skills that may be merged / consolidated

- **`constitution-checks` (planning-lead) and `constitution-check` (reviewer)** are
  related but separate skills. Planning-lead's version audits a PLAN before build
  (does the plan violate the constitution?); reviewer's version audits a change against
  the 9 reviewer-owned rules at review time. They share the 12-rule source but differ
  in input (PLAN vs diff) and output (CONSTITUTION_CHECK.md vs review finding).
  Recommend keeping them separate; merge only if a follow-up feature shows the
  duplication is a maintenance burden.
- **`evidence-validation` (reviewer) and `commit-readiness` (reviewer)** could share
  the "what counts as evidence" content. Recommend keeping separate but cross-link.
- **`runtime-author` (system-lead) and `asset-authoring` (existing)** overlap on
  authoring concerns. `asset-authoring` is the catalog-side authoring; `runtime-author`
  is the adapter-translation step. Keep separate.

### Intentionally deferred / out of scope

- **`dependency-audit`** — deferred per planning-lead ref spec §6; only needed for
  multi-feature planning (likely Phase 4+).
- **All 10 `system-lead` ref-spec missing skills are P0/P1/P2 by their ref spec's
  own priority ranking**, not by my mapping. I have followed the ref-spec priorities
  exactly for system-lead and reviewer; the priorities I assigned to planning-lead and
  project-lead ref-spec skills (mode-decision, constitution-checks, recontextualization,
  packet-validation, builder-selection) are escalated to P0 because they are core-loop
  blockers, even when the ref spec lists them as "Medium". The "Medium" rating in those
  refs is a build-priority signal, not a system-criticality signal.
- **Stack-specific testing subagents and skills** (per test-lead ref spec §11.3 —
  `python-tester`, `api-tester`, `db-tester`, `ui-tester`, `cli-tester`,
  `security-tester`, plus skills like `pytest-patterns`, `coverage-analysis`,
  `property-testing`, `http-assertions`, `schema-validation`, `contract-testing`,
  `migration-testing`, `data-integrity`, `query-performance`, `component-testing`,
  `accessibility`, `screenshot-diff`, `arg-parse-testing`, `exit-code-assertions`,
  `pipe-testing`, `owasp-scan`, `fuzz-testing`, `secret-scan`) are explicitly
  "Future" / "Future enhancement" in the ref spec and are NOT in this inventory.
  They are intentionally deferred.

### Sources of priority labels

- **reviewer ref spec** assigns P0/P1/P2 to its 6 missing skills — used verbatim.
- **system-lead ref spec** assigns P0/P1/P2 to its 10 missing skills — used verbatim.
- **project-lead ref spec** uses "High / Medium" — mapped to P0 / P1.
- **planning-lead ref spec** uses "High / Medium" and "Future" — mapped to P0 / P1 / P2.
- **build-lead ref spec** uses "High / Medium" — mapped to P0 / P1.
- **research-lead ref spec** uses "Build" (no explicit priority) for cache-management and
  harvest-protocol — both are P0 because cache-first discipline is core to research-lead
  and harvest-protocol is R-008-gated (R-008 territory is always P0).

### Verification of totals

- Existing skills (38) — verified by `ls src/aspis/data/catalog/skills/` (38 directories).
- Unique skills referenced in agent frontmatter (42) — verified by reading all 11
  catalog agent files + bootstrap.
- Unique skills referenced in 8 lead ref specs (21 additional) — verified by reading
  Responsibilities→Skills tables and "Missing skills" / "Recommended skill additions"
  sections.
- Total unique referenced: 42 + 21 = 63. Of these, 38 exist in the catalog; 25 are
  missing. (63 = 38 + 25 ✓)
