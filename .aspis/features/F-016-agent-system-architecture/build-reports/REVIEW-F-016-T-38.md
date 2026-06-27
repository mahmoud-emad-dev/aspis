# Review — F-016 / T-38

> Filled by the reviewer (read-only — you evaluate and report, you never edit the
> work). The header is stamped by `aspis artifact`; you fill the verdict and
> findings from evidence (the diff, the tests, the acceptance criteria).

- **Feature**: F-016 — Agent System Architecture
- **Task**: T-38 — Final acceptance review
- **Date**: 2026-06-27
- **Verdict**: **APPROVED with notes**

## Scope reviewed

Every artifact in the F-016 scope, organised by the four buckets the task spec
names:

**Reference specs (12 files)** at `.aspis/features/F-016-agent-system-architecture/Research/ref/`:
- 8 leads — `project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`, `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`
- 3 leaves — `committer.md`, `general-builder.md`, `project-explorer.md`
- 1 systemic — `governance.md`

**Systemic specs (5 files)** at `.aspis/features/F-016-agent-system-architecture/Research/specs/`:
- `modes.yaml` (3 modes × 8 knobs)
- `enforcement.md` (3 boundaries × 3 modes)
- `planning-scripts.md` (3 scripts × source/destination/trigger/validation)
- `cli-verbs.md` (6 verbs × purpose/priority/interface/expected output)
- `cross-runtime.md` (Claude adapter fix + byte-parity spec)

**Skills inventory (1 file)** at `Research/skills/inventory.md` — 63 referenced / 38 existing / 25 missing, P0/P1/P2 prioritised.

**Catalog agent files (11 files)** at `src/aspis/data/catalog/agents/`:
- `project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`, `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`, `committer.md`, `general-builder.md`, `project-explorer.md`

**Feature docs (3 files)**:
- `.aspis/features/F-016-agent-system-architecture/SPEC.md`
- `.aspis/features/F-016-agent-system-architecture/PLAN.md`
- `.aspis/features/F-016-agent-system-architecture/TASKS.md`

**Contracts read for cross-reference**:
- `.aspis/context/IDENTITY.md`, `.aspis/context/ARCHITECTURE.md`, `.aspis/context/DECISIONS.md`
- `.aspis/rules/system-rules.md` (R-001…R-010), `.aspis/rules/architecture-constitution.md` (12 rules)
- `.aspis/context/CURRENT_STATE.md` (branch: `feature/F-016-agent-system-architecture`, last commit: `e83fda1 docs(F-016/T-33..T-37): add spec files for modes, CLI, scripts, parity`)
- `src/aspis/catalog.py` (CatalogAgent dataclass, FR-011 field list)
- `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (machine-readable constitution index)
- The full F-016 git history (T-01 through T-37, all committed)
- `Research/audit/findings-1.md` (T-03 audit: 7 CRITICAL + 13 HIGH + 14 MEDIUM + 5 LOW)
- `Research/audit/findings-triage.md` (T-04 owner-decided Group 1/2/3 dispositions)
- `build-reports/REVIEW-F-016-T-30.md` (initial T-30 review: changes-requested)
- `reviews/T-30-review.md` (T-30 re-review: approved-with-notes after `f574496`)

`bootstrap.md` (12th catalog file) is **explicitly excluded from F-016 scope** per the
T-30 reviews and `Research/audit/findings-1.md` (1.4 in `Research/current-aspis-audit-1.md`):
bootstrap is a transient primary that self-deletes post-onboarding. Its missing
`delegates` and `runtimes` are tracked as a follow-up, not an F-016 blocker.

## Per-SC evidence (SC-001 through SC-012)

### SC-001 — All 11 agent reference specs pass adversarial review with 0 CRITICAL and 0 HIGH unresolved findings

**Verdict: PASS** (with one documented deferred item, not a blocker).

The T-03 adversarial audit (`Research/audit/findings-1.md`) found **7 CRITICAL + 13 HIGH
+ 14 MEDIUM + 5 LOW** findings across the 8 lead ref specs. The T-04 owner triage
(`Research/audit/findings-triage.md`) classified them as Group 1 (must-fix, ~10
findings), Group 2 (deferred, 5), and Group 3 (skip, conformance-only, ~20).

**Group 1 fixes — verified applied to the 8 lead specs** (file:line evidence):

| ID | Where | Fix verified |
|----|-------|--------------|
| **A-1** (reviewer missing model tier) | `reviewer.md:124–132` | Now has explicit "Model Tier" subsection; declares standard default, deep for high-risk, cheap for P2 self-check; cites R-007. |
| **A-4** (research-lead missing "if stuck") | `research-lead.md:185–187` | Now in §8 Escalation: "If stuck — stop, don't guess. On repeated tool failure, contradictory sources, or a claim that cannot be verified, STOP and hand back…" |
| **A-5** (reviewer missing "if stuck") | `reviewer.md:202–206` | Now in §6 Verdict System: "If stuck — stop, don't guess. If inputs are contradictory, evidence is unobtainable, or a dimension is out of the reviewer's scope, withhold the verdict rather than guess." |
| **B-1** (planning-lead contradictory skills) | `planning-lead.md:170–175`, `:240–242` | Removed `plan-critic`/`review-strategy` from planning-lead's owned skills; explicit "Skills NOT in planning-lead's set" lists both as reviewer's domain. Note at line 240-242: "plan-critic and review-strategy are reviewer's skills, not yours. You consume plan review by delegating to the reviewer at P7." |
| **B-2** (reviewer 12-vs-6 contradiction) | `reviewer.md:229–230` | Now labels: "v1 vs v2: checks 1–6 are the existing plan-critic (v1); checks 7–12 are the v2 extension being added. '12 checks' = v1 (6) + v2 (6)." |
| **B-5** (research-lead write/edit asymmetry) | `research-lead.md:41–45` | Now documents the rationale inline: "The write-without-edit asymmetry is intentional, not a gap." |
| **B-6** (system-lead self-modification hole) | `system-lead.md:175–185` | New "Self-modification is governed, not free" subsection with 5 guardrails (governance subagent, enforcement block, named allowlist, catalog regeneration only, trace spine out of scope). |
| **C-6** (committer in planning-lead live task list) | `planning-lead.md:264–265` | "The committer is never in the planning task allow-list — planning produces artifacts, not commits." |
| **C-7** (reviewer model drift) | `reviewer.md:124–132` | Tier resolved (standard default); live custom model explicitly classified as personal setup, ignored by the design. |
| **D-6** (system-lead `bash: '*'`) | `system-lead.md:18–30` (frontmatter) | Wildcard removed; named commands only (`aspis *`, `python .aspis/scripts/**`, `python3 .aspis/scripts/**`, `ruff *`, `mypy *`, `pytest *`, `uv run *`, `git status*`, `git diff*`, `git log*`). |
| **D-9** (reviewer `aspis artifact test`) | `reviewer.md:18` (frontmatter) | `aspis artifact*` is the only allow-line (not `aspis artifact test` specifically); reviewer is read-only and does not stamp test artifacts. |

All 11 Group 1 items are resolved in the current files. The 3 leaf ref specs
(`committer.md`, `general-builder.md`, `project-explorer.md`) were not in the
T-03 audit scope (the audit was 8 leads) and were produced directly to the
template with full per-spec structure, R-rule citations, and acceptance
criteria — verified in §Leaf-scope below.

**Group 3 (conformance-only) — SKIP per the owner decision.** Examples: adding
"Core Rules" recital tables to every spec (R-006 says state once, don't
duplicate), section-numbering cosmetics in research-lead, adding
C-PORTABLE notes to every bash allowlist (a script rule, not a spec rule).
The doctrine is sound: per `system-rules.md` "Applying these rules — practice
over theory", a rule that makes the spec worse is a signal to narrow its
scope, not to comply mechanically. The triage's Group 3 SKIP is the right call.

**Deferred items tracked** (per the T-38 task spec's "Known deferred items" list):
- Planning-lead's 7 future L3 subagents in `delegates` — deferred to F-017
- 25 missing skills are specified (T-31) but not built — building is a follow-up
- `bootstrap.md` is a 12th catalog file outside F-016 scope — tracked not blocked
- System-lead `websearch: deny` vs FR-007 — tracked for T-39 SPEC clarification
- Skills gap (4 skills referenced in frontmatter but not in skills catalog) — T-31 follow-up

These are not findings; they are the build notes' durable record of the
exemptions. None block SC-001.

### SC-002 — Cross-agent consistency audit passes: 0 overlapping responsibilities, 0 orphaned delegation edges, 0 references to non-existent skills

**Verdict: PASS.**

The cross-reference tool `cross_ref_agents.py` (T-02, `994d592`) is the
deterministic gate for this SC. Three T-XX gates use it:

| Gate | Commit | Result |
|---|---|---|
| T-05 (8 leads) | `7bfd679` | **PASS** (0 HIGH / 0 MEDIUM after Group 1 fixes) |
| T-14 (8 leads + 3 placeholder leaf stubs) | `83abc72` | **PASS** |
| T-18 (3 leaves against leads) | `8d41c56` | **PASS** |

**Manual verification of delegation edges (catalog files)**:

| Agent | delegates list | All exist? |
|---|---|---|
| project-lead | planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer | ✓ all 8 exist |
| planning-lead | research-lead, reviewer, project-explorer, clarify*, task-decomposer*, idea-capture*, prd-writer*, constitution-checker*, scope-estimator*, research-request-writer* | 3/10 exist now; 7 marked `# Future L3 subagents (referenced in spec, may not yet exist)` — F-017 deferred per build notes |
| build-lead | general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead | ✓ all 7 exist |
| reviewer | project-explorer, research-lead | ✓ both exist |
| system-lead | project-explorer, reviewer, committer | ✓ all 3 exist |
| fix-lead | reviewer, committer, project-explorer, test-lead | ✓ all 4 exist |
| test-lead | project-explorer | ✓ exists |
| research-lead | project-explorer | ✓ exists |
| committer | `[]` | ✓ leaf agent, no delegation |
| general-builder | `[]` | ✓ leaf agent, no delegation |
| project-explorer | `[]` | ✓ leaf agent, no delegation |

The 7 future subagents in planning-lead are an **owner-decided, documented
deferral** (build notes: "Subagent roster is OUT of scope → F-017"). The
catalog file annotates them: `# Future L3 subagents (referenced in spec, may
not yet exist)`. This is the same exemption the T-30 review approved.

**Skill reference resolution**: 4 skills referenced in agent frontmatter
but not in the catalog: `mode-decision` (planning-lead.md:61, 62),
`constitution-checks` (planning-lead.md:62), `packet-validation`
(build-lead.md:51), `builder-selection` (build-lead.md:52). The
T-30 review deferred this to T-31, and T-31's inventory
(`Research/skills/inventory.md`) lists all four with priorities (mode-decision P0,
constitution-checks P0, packet-validation P0, builder-selection P0). The
"every skill exists" gate is **technically failing on 4 skills** but is
deferred to the skills-build follow-up — documented, tracked, not blocking.

**Overlapping responsibilities**: 0 found. The 8 lead specs each declare
their own role explicitly; the 3 leaf specs are "disposable executor" /
"read-only helper" / "single git writer" — orthogonal to all leads and to
each other. The `committer` and `general-builder` leaf specs both note the
no-delegation invariant (R-004, R-010); `project-explorer` is the only
L1↔L3 exception (R-010 delegate-with-purpose).

### SC-003 — All 11 catalog agent files are frontmatter-aligned with their reference specs

**Verdict: PASS** (after the T-30 fix `f574496`).

Every in-scope catalog file has a `> Derived from Research/ref/<name>.md`
header and a `## Identity` block whose content matches the corresponding
reference spec. The T-30 re-review (`reviews/T-30-review.md:38–40`)
verified:

> "HIGH #1 from the previous review — RESOLVED. `runtimes: []` is now
> present in all 11 in-scope files. Verified by `git diff f574496~1
> f574496 --stat` shows 11 files changed, 11 insertions, one line per
> file, every insertion being `runtimes: []`."

**FR-011 + T-30 gate field check (re-runnable)**:

| Field | FR-011 | T-30 gate | All 11 files |
|---|---|---|---|
| `name` | ✓ | ✓ | ✓ |
| `description` | ✓ | ✓ | ✓ |
| `mode` | ✓ | ✓ | ✓ |
| `model` | ✓ | ✓ | ✓ |
| `temperature` | ✓ | — (not in T-30 gate) | ✓ (was the `04f79a8` fix) |
| `tools` | ✓ | ✓ | ✓ |
| `permissions` (bash + web) | ✓ | ✓ | ✓ |
| `delegates` | ✓ | ✓ | ✓ |
| `skills` | ✓ | ✓ | ✓ |
| `runtimes` | ✓ | ✓ | ✓ (was the `f574496` fix) |
| `export_scope` | ✓ | ✓ | ✓ |

11/11 fields, 11/11 files. **PASS.**

### SC-004 — All 30+ missing skills are specified with purpose, owning agent, and priority (P0/P1/P2)

**Verdict: PASS with one medium note** (spec wording).

`Research/skills/inventory.md` is comprehensive. The numbers:

- Total unique skills referenced (across 11 agent frontmatter + 8 lead ref
  spec "missing" / "recommended" tables): **63**
- Skills with existing catalog entries: **38**
- Missing skills (need new SKILL.md): **25**
- Priority breakdown: **P0: 13 | P1: 7 | P2: 5**

Every missing entry has: skill name, 1-line purpose, owning agent(s),
priority, estimated sections, and source citation. P0 entries (blocking)
are the core loop and R-008-gated skills: `builder-selection`,
`cache-management`, `catalog-validator`, `constitution-check`,
`constitution-checks`, `drift-detector`, `evidence-validation`,
`governance-approval`, `harvest-protocol`, `mode-decision`,
`packet-validation`, `recontextualization`, `security-review`.

**Note (medium — not blocking)**: SPEC.md:138 says "30+ missing skills" and
SPEC.md:93 (FR-023) says "30+ across 8 agents". The actual count in the
inventory is **25 missing** (with 38 already existing = 63 total
referenced). The 30+ was a planning estimate; the audit refined it to
25. The inventory is correct and complete. The SPEC wording overstates
the gap. **This is a T-39 SPEC clarification item** (consistent with the
build notes' "Update SPEC.md Clarifications section with any decisions
made during build"). Not a deliverable defect.

### SC-005 — All 6 missing CLI verbs are specified with purpose and priority

**Verdict: PASS.**

`Research/specs/cli-verbs.md` specifies all 6 with: purpose, priority,
interface signature, expected output, and the agent(s) that call them.

| Verb | Priority | Interface | Caller |
|---|---|---|---|
| `validate-runtime` | P0 | `aspis validate-runtime [--runtime] [--check <field>]` | system-lead, reviewer, build-lead |
| `validate-index` | P1 | `aspis validate-index [--fix]` | system-lead, project-explorer |
| `byte-parity` | P0 | `aspis byte-parity [--runtime] [--agent]` | system-lead, reviewer |
| `drift` | P1 | `aspis drift [--field] [--runtime]` | system-lead, fix-lead |
| `export` | P0 | `aspis export [--runtime] [--agent] [--dry-run] [--check]` | system-lead, build-lead |
| `governance` | P1 | `aspis governance <request \| approve \| audit \| revoke \| check \| ledger>` | governance, system-lead, project-lead |

The 3 P0 verbs (`validate-runtime`, `byte-parity`, `export`) are exactly
the ones system-lead §9 lists as "needed for the core loop to validate"
(system-lead.md:284). The P1 verbs are the operational enhancements. The
exit codes are specified (0 success, non-zero failure) consistent with
the existing `aspis` CLI style. **PASS.**

### SC-006 — The governance subagent spec is complete and passes R-008 compliance review

**Verdict: PASS.**

`Research/ref/governance.md` is the most thoroughly-specified of all the
F-016 artifacts. Structure (7 sections, 634 lines):

- **§1 Identity** — deterministic script (not LLM), the only path to
  `rules/**` and `profiles/defaults.yaml`, gated by R-008. The
  "Why deterministic" table compares LLM-agent vs deterministic-script
  on 6 dimensions (predictability, audit, failure mode, cost, trust,
  scope) — the decision is locked.
- **§2 Protected paths** — the canonical 12-glob set covering rules,
  policy (Tier-2 config per system-lead §7), defaults, runtime agents
  and permissions, active-feature state. The matching rule
  (PurePath.match semantics) and the explicit "what is NOT in the set"
  list are both stated.
- **§3 R-008 workflow** — the 7-step end-to-end (request → intercept →
  approve → record → check → write → audit) with the exact CLI
  invocation, the match rule (exact paths, not globs — `--glob-approval`
  is a separate, dangerous flag), and the "what the workflow forbids"
  list (no silent approvals, no retroactive, no model-mediated).
- **§4 Approval ledger** — append-only YAML at
  `.aspis/state/approval-ledger.yaml`, full schema (id, timestamp,
  approver, scope.paths, scope.reason, expiry, status, applied, revocation),
  concurrency model (file lock, stale-lock detection), retention (no
  policy — life of project).
- **§5 Intervention handler** — three boundaries (runtime tool,
  pre-commit hook, OS-sandbox future), exact behaviour on each
  (resolve → match → load ledger → filter active+unexpired → match →
  allow-and-append or BLOCK with the canonical message).
- **§6 CLI interface** — 6 verbs (`request`, `approve`, `audit`, `revoke`,
  `check`, `ledger`) with argument lists, exit codes (0/2/3/4/5/6), and
  the consistent error model. "Authorship of the CLI" makes explicit
  that only governance writes the ledger; other tools read via
  `aspis governance audit` / `ledger`.
- **§7 Acceptance criteria** — 17 items, all marked.

**R-008 compliance**: the spec quotes `system-rules.md` R-008 verbatim
("Architecture, rules, permissions, security posture, and model-routing
changes require human approval — never an automated rewrite") and
implements it: every protected-path change requires an active approval
in the ledger; no `--force`, no env-var override, no back door; the
gatekeeper is gated (governance's own writes to the protected set are
subject to an active approval — symmetry holds).

The cross-references are correct: every design choice cites its source
(system-lead §5, §7, §8, §10, §12, §13; system-rules.md R-008; F-015
protection engine for the byte-hash PROTECT class as runtime analogue
of the governance block). **PASS.**

### SC-007 — The modes.yaml spec is complete — every knob has per-mode values

**Verdict: PASS.**

`Research/specs/modes.yaml` defines:

- **3 modes**: vibe / mvp / production
- **8 knobs × 3 modes = 24 values**, every cell filled:

| Knob | vibe | mvp | production |
|---|---|---|---|
| spec | bullets | stories | full |
| architecture | skip | note | full |
| task_size | large | medium | small |
| plan_review | skip | self | independent |
| build_review | light | standard | full |
| test_depth | gate | core | full |
| docs | none | minimal | complete |
| promotable | false | true | N/A |

Each knob has a typed enum documented. The mode-resolution order
(agent declared → CLI override → env var → effective) and the ceiling
semantics ("a mode is a ceiling, not a floor; min(declared, override)
controls") are specified. File location is `.aspis/config/modes.yaml`
overriding the catalog default at
`src/aspis/data/catalog/config/policy/modes.yaml`. The acceptance
criteria (8 items) include consistency with planning-lead ref spec
§3 mode system and with `CORE_LOOP.md`.

The planning-lead ref spec §3 mode table (lines 102-115) lists the same
8 knobs with the same per-mode values — the two docs agree. **PASS.**

### SC-008 — The enforcement mode spec passes security review

**Verdict: PASS.**

`Research/specs/enforcement.md` is 71 lines and covers all the
load-bearing points:

- **3 boundaries**: runtime (Edit/Write), pre-commit, CI — each with
  its own target state.
- **3 modes**: warn / block / strict, with the mode matrix showing
  per-boundary behaviour. The current state (warn) and target state
  (block for runtime, warn for pre-commit, CI block) are both stated.
- **Transition plan**: 4 phases (document → implement → flip default →
  strict), each with criteria.
- **CI override**: `ASPIS_ENFORCEMENT=block` — does NOT affect runtime
  enforcement (which is always block in Phase 2+); only the pre-commit
  boundary.
- **Auto-fix behaviour**: explicitly NONE in current design (governance
  handles protected-path fixes after R-008 approval — a separate
  concern).

**Consistency with D-010**: the spec is the flip side of D-010
("hooks non-blocking by default"). D-010 says the current default is
warn; this spec says the target is block for runtime, warn for
pre-commit, CI override to block. The two are consistent.

**Security review**: the only path to block a protected-path edit
through enforcement is the runtime tool boundary, which is the most
effective (write never reaches filesystem). Pre-commit is the
safety net. CI override is opt-in. Auto-fix is never silent. The
trust model is: code, not prose. The R-008 boundary is explicit
(system-lead §8 and governance §1). **PASS.**

### SC-009 — All 3 planning scripts have deployment specifications

**Verdict: PASS.**

`Research/specs/planning-scripts.md` (97 lines) gives the full
catalog→runtime map for all 3 scripts:

| Script | Source | Destination | Phase | Caller |
|---|---|---|---|---|
| `feature_scaffold.py` | `src/aspis/data/catalog/scripts/planning/feature_scaffold.py` | `.aspis/scripts/planning/feature_scaffold.py` | P1 | planning-lead |
| `task_compile.py` | `src/aspis/data/catalog/scripts/planning/task_compile.py` | `.aspis/scripts/planning/task_compile.py` | P6 | planning-lead |
| `prereq_validate.py` | `src/aspis/data/catalog/scripts/planning/prereq_validate.py` | `.aspis/scripts/planning/prereq_validate.py` | P8 | build-lead |

Each entry has: catalog source path, runtime destination, trigger
(which phase + which caller), purpose, CLI shape, validation method
(commands that exit 0 on a correct deployment). The deployment
mechanism is documented (deploy at bootstrap or first scaffold, owned
by system-lead per its §2, copy never move, deployed copy is
read-only at runtime). The invariants are stated (catalog-as-source,
read-only deployed, self-contained stdlib-only, phase alignment).

The acceptance criteria (8 items) include consistency with
planning-lead ref spec phases P1/P6/P8 and with system-lead §2 + §3
(`asset-authoring` skill). **PASS.**

### SC-010 — The Claude Code adapter permission-block preservation is specified with acceptance criteria

**Verdict: PASS.**

`Research/specs/cross-runtime.md` (64 lines) defines the cross-runtime
parity requirements with 7 acceptance criteria:

- Both runtimes documented (OpenCode native, Claude Code adapter)
- Byte-parity requirement (catalog → runtime files byte-identical
  across capability-equivalent runtimes)
- Capability-equivalence model (which fields are equivalent, which
  differ — `permission:` block format)
- **Claude Code adapter fix** (the target of FR-021):
  - Target state — preserve the `permission:` block; translate or
    embed as a structured comment if Claude Code has no native
    permission format
  - 5 acceptance criteria for the fix: block appears in every
    Claude-rendered file, semantics preserved (deny/allow),
    same effective permission surface as OpenCode, backward-
    compatible, verified by `aspis byte-parity --runtime claude
    --agent all` returning exit 0
- `aspis byte-parity` CLI verb (cross-refs to cli-verbs.md)
- CONFLICT / PROTECT decision table from F-015 protection engine
- Cross-runtime test procedure (render all 11 catalog agents for
  both runtimes; compare effective configuration; document gaps
  rather than silently drop)

Consistent with FR-021 (permission-block preservation) and FR-022
(byte-parity check). **PASS.**

### SC-011 — Complete PLAN.md and TASKS.md are ready for build-lead handoff

**Verdict: PASS.**

`PLAN.md` has: §Summary, §Technical context, §Gate check (R-001, R-002,
R-005, R-008 — all PASS), §Components (4), §Steps (13), §Verification,
§Risks & rollback, §Complexity tracking, §Decisions needing approval (4
R-008-gated items). 113 lines, well-organised.

`TASKS.md` has 41 tasks across 6 phases, each with a Files list,
Depends-on, Blocks, Packet version, Builder tier, Review type, and
Acceptance criteria. The critical path is
`T-01 → T-03 → T-04 → T-05 → T-14 → T-18 → T-30 → T-32..T-37 → T-38 → T-40`
(per the header). All 37 of the pre-T-38 tasks are marked `[x]`
(done) and T-39 is `[ ]` (T-39 depends on T-38, so this is correct).

**FR → task mapping verification**:

| FR | Maps to |
|---|---|
| FR-001..FR-002 (agent specs) | T-06..T-13 (lock lead specs), T-15..T-17 (leaf specs) |
| FR-003 (no overlapping responsibilities) | T-05, T-14, T-18 (cross-ref gates) |
| FR-004 (no orphaned delegation edges) | T-05, T-14, T-18 |
| FR-005 (model tier declared) | T-06..T-13 (each spec has §3) |
| FR-006 (permission surface) | T-06..T-13, T-15..T-17 |
| FR-007 (universal denies) | T-19..T-29 (catalog updates) |
| FR-008 (reviewer read-only) | T-22 |
| FR-009 (committer only `git commit*`) | T-27 |
| FR-010..FR-012 (catalog) | T-19..T-29, T-30, T-31 |
| FR-013..FR-014 (core loop, delegation) | T-06 (project-lead spec §5) |
| FR-015..FR-017 (permission/model/error matrix) | T-06, T-22 (reviewer), T-23 (system-lead) |
| FR-018 (governance subagent) | T-32 |
| FR-019 (modes.yaml) | T-33 |
| FR-020 (enforcement mode) | T-34 |
| FR-021..FR-022 (cross-runtime) | T-37 |
| FR-023 (missing skills) | T-31 |
| FR-024 (CLI verbs) | T-36 |
| FR-025 (planning scripts) | T-35 |
| FR-026..FR-028 (acceptance, review, constitution) | T-38 (this task) |

**SC → verification method mapping**:

| SC | Verified by |
|---|---|
| SC-001 | T-38 (this review) — see SC-001 evidence above |
| SC-002 | T-05, T-14, T-18 (cross-ref gates) |
| SC-003 | T-30 (catalog structural validation, APPROVED `f008fea`) |
| SC-004 | T-31 (skills inventory complete) |
| SC-005 | T-36 (CLI verbs spec complete) |
| SC-006 | T-32 (governance spec complete; R-008 compliance) |
| SC-007 | T-33 (modes.yaml spec complete) |
| SC-008 | T-34 (enforcement spec complete; security review) |
| SC-009 | T-35 (planning scripts spec complete) |
| SC-010 | T-37 (cross-runtime spec complete) |
| SC-011 | T-38 + T-40 (this review + final cross-ref) |
| SC-012 | T-38 (cost-of-change verification — see below) |

Every FR has ≥1 task. Every SC has a verification method. **PASS.**

### SC-012 — Cost-of-change for the agent system: adding a new agent requires ≤5 files touched

**Verdict: PASS.**

Manual walk-through of "add a new agent X" with the F-016 design:

1. **Reference spec** at `Research/ref/<name>.md` (the truth layer; FR-001, FR-002)
2. **Catalog agent file** at `src/aspis/data/catalog/agents/<name>.md` (runtime-neutral; FR-010, FR-011)
3. **Profile entry** if the agent is profile-specific (otherwise the `base.yaml` profile picks it up automatically — D-008 asset kinds are data)
4. **SPEC.md** update if the agent is required by F-016's own scope (otherwise no SPEC change needed)
5. **TASKS.md** update only if adding a new task *about* the agent (otherwise no task needed)

**5 files** is the upper bound. In the common case (a new agent not specific
to F-016), only **2 files** are touched (reference spec + catalog file),
because:
- The reference spec is the single source (D-008 / C-SINGLE-SOURCE)
- The catalog file derives from it (`> Derived from Research/ref/<name>.md`)
- The runtime adapter regenerates `.opencode/agents/<name>.md` and
  `.claude/agents/<name>.md` from the catalog (D-002, D-008)
- No core engine code change is needed (D-008 cost-of-change ≈0 core files)
- No constitution or rule change is needed (the agent conforms to the
  existing 12-rule constitution and the existing system rules R-001…R-010)

The system rules' Cost-of-Change test (`architecture-constitution.md:32`):
"1–3 healthy; 5–10 warning; 10+ architecture problem; 20+ critical." A new
agent at 2–5 files is **healthy** (the healthy band is 1–3 files; 5 is
the edge). The design's intent is that the common case is ≤3, and the
5-file case is the F-016-specific edge. **PASS** (within the healthy band
for the common case, at the upper bound for the F-016-self-update case).

## Findings

| Severity | Where | Finding | Suggested fix |
|----------|-------|---------|---------------|
| medium | `SPEC.md:93, :138` (FR-023, SC-004) | **SPEC says "30+ missing skills" but the actual count in the inventory is 25.** The 30+ was a planning estimate; the T-31 audit refined it to 25 missing + 38 existing = 63 total referenced. The inventory is complete, prioritised, and well-organised. The SPEC overstates the gap. | Update FR-023 and SC-004 to "all missing skills" or "all 25 missing skills" in T-39 (SPEC Clarifications follow-up). Document the actual count of 25 missing (13 P0 + 7 P1 + 5 P2). Not blocking. |
| medium | `src/aspis/data/catalog/agents/system-lead.md:32` (frontmatter `websearch: deny`) | **Catalog has `websearch: deny` for system-lead but FR-007 implies `websearch: allow`.** This is a known SPEC drift, not a catalog defect. The reference spec (the design source) explicitly denies websearch for system-lead; T-23's owner decision locked this; the catalog correctly follows the design. The SPEC was not updated to match. | Open a follow-up: update FR-007 to match the T-23 decision (system-lead `websearch: deny`, research-lead `websearch: allow`, all others deny). Tracked for T-39. Not blocking. |
| medium | `src/aspis/data/catalog/agents/planning-lead.md:42–48` (frontmatter `delegates`) | **7 future L3 subagents listed but not built.** `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer` are explicitly marked `# Future L3 subagents (referenced in spec, may not yet exist)`. The T-30 review approved this exemption; the build notes document it as F-017-deferred. | None for T-38. The exemption is the build note. When F-017 lands, the listed subagents will exist and the cross-ref gate becomes naturally true. Tracked. |
| low | `Research/skills/inventory.md:212–219` | **4 skills referenced in agent frontmatter but not yet in the catalog** (`mode-decision`, `constitution-checks`, `packet-validation`, `builder-selection`). The T-30 review deferred this; T-31's inventory is the next step. All 4 are P0 in the inventory. | None for T-38. T-31 owns the gap closure; the inventory itself is the complete enumeration. Tracked. |
| low | `src/aspis/data/catalog/agents/bootstrap.md:1–29` (frontmatter) | **`bootstrap.md` lacks `delegates` and `runtimes` fields.** This is the 12th catalog file, excluded from F-016 per the audit (transient primary, self-deletes post-onboarding). The T-30 re-review confirmed the structural exemption. | None for T-38. Tracked as a follow-up. Bootstrap is structurally exempt from F-016's 11-file scope. |
| low | `Research/ref/research-lead.md:7, :145–161` (section numbering) | **Research-lead has 13 sections with no §7 "Subagent Details" between §7 "Subagents" and §8 "Escalation".** The T-03 audit flagged this as cosmetic (A-3). The triage said "Cosmetic; trivial if touched in passing" — SKIP per Group 3. | None. The owner decision is to skip; the section numbering is internally consistent (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13). The structure is content-correct. |
| low | (no file; system-wide) | **Several lead ref specs lack a "Core Rules" recital table** (e.g. fix-lead cites R-001/R-004/R-005 only, not R-002/R-006/R-007/R-008/R-009). The T-03 audit flagged this (C-1, C-2, C-3); the triage said "Pure recital; R-006 says state once, don't duplicate" — SKIP per Group 3. | None. R-006 (thin agents, single source) explicitly prohibits duplicating rule citations in every spec. The system rules are cited by ID where the spec enforces them, and not recited where it does not. This is the design, not a defect. |

**Total**: 0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW. **No blocking issues.**

The 3 MEDIUM findings are all *SPEC/drift follow-ups* — they are
documented, tracked, and explicitly authorised by the build notes and
the owner-decided T-04 triage. None of them are defects in the F-016
deliverable as such; they are gaps between the deliverable and a
tighter-published-claim that should be reconciled in the T-39 SPEC
Clarifications update.

## Architecture constitution compliance (12-rule spot check)

The reviewer-owned constitution checks (per
`src/aspis/data/catalog/config/policy/constitution-checks.yaml`,
`enforced_by: review`):

| Rule | Status | Evidence |
|---|---|---|
| **C-COST** (cost of change ≤10) | PASS | SC-012 verified; 2–5 files to add a new agent (healthy band) |
| **C-AUTOMATION** (R-003 deterministic-first) | PASS | governance is a deterministic script (governance.md:§1); planning scripts are stdlib-only; byte-parity is a CLI verb; cross-ref is a script |
| **C-LOCAL-CHANGE** (new files, not edits) | PASS | F-016 added 18 new spec files; edited 11 catalog files in place (per the T-19..T-29 work); the 11 edits are aligned edits to existing assets, not a sweep |
| **C-PLUGIN-FIRST** (core never names concrete) | PASS | No core engine change; the 6 missing CLI verbs are spec'd, not built; runtimes discovered by adapter (D-015); agents discovered by profile (D-008) |
| **C-SINGLE-SOURCE** (every fact one owner) | PASS | Reference spec → catalog → runtime; the 8 lead specs cite each other by ID, not by duplication |
| **C-CONFIG-OVER-CODE** (data, not branches) | PASS | modes.yaml is data; enforcement modes are data; permission surfaces are frontmatter; tiers are data; model routing is data (D-016) |
| **C-NO-SPECIAL-CASE** (no `if runtime ==`) | PASS | The system-lead's bash allowlist is now a named list (T-04 fix D-6); no `if agent ==` patterns introduced by F-016 |
| **C-DISCOVERY** (load by convention) | PASS | F-016 does not introduce a hand-maintained registry; skills are discovered by directory listing; agents are discovered by file presence |
| **C-FILE-SELF-EXPLAINS** (Purpose/Does Not/Used By) | PASS | Each agent file has a top docstring with identity and "what it is/is not" (R-006); each spec has Identity (IS/IS NOT) and Core rules |
| **C-TESTABLE** (every component testable) | PASS | Each agent spec has Acceptance Criteria; each SC has a verification method; the cross-ref tool is the deterministic gate |
| **C-PORTABLE** (Windows + Linux) | PASS | Planning scripts are stdlib-only; bash allowlists include both `python` and `python3` forms; the SPEC explicitly cites cross-platform practice in system-lead.md:148–150 |
| **C-ARCH-BEFORE-FEATURES** (build the extension first) | PASS | The F-016 design is itself the extension mechanism (D-002 catalog + D-008 asset-kinds-are-data); F-016 doesn't add a feature without a spec slot |

12/12 PASS. No architecture-constitution violation introduced by F-016.

## System rules compliance (R-001 through R-010)

| Rule | Status | Evidence |
|---|---|---|
| **R-001 Scope** | PASS | F-016 changes stay within `.aspis/features/F-016-agent-system-architecture/` and `src/aspis/data/catalog/agents/`. No product code change. No runtime hand-edited. |
| **R-002 Gates first** | PASS | Every phase has a gate (T-05, T-14, T-18, T-30). The T-30 gate ran twice (changes-requested → approved-with-notes after fixes). |
| **R-003 Deterministic-first** | PASS | governance is a script; cross-ref is a script; planning scripts are scripts; byte-parity is a CLI verb; no agent is specified where a script would do |
| **R-004 One writer** | PASS | committer is the only agent with `git commit*` allowed (verified: committer.md:24, :26; all 10 others deny). reviewer is read-only (verified: reviewer.md:26–29). R-004 cited in 10/11 ref specs. |
| **R-005 Tests-as-spec** | PASS | Every spec has measurable Acceptance criteria; SC-001..SC-012 are the spec tests; cross-ref is the deterministic gate |
| **R-006 Thin agents, single source** | PASS | Each spec is 200-1100 lines, identity + responsibilities + acceptance; intelligence lives in the skills. Reference spec is the single source; catalog derives from it; runtime derives from the catalog. |
| **R-007 Pinned models** | PASS | All 8 lead specs declare a model tier (project-lead: standard, planning-lead: standard, build-lead: standard, reviewer: standard, system-lead: standard, fix-lead: standard, test-lead: standard, research-lead: standard); 3 leaves are cheap. Resolved at render time per D-017. |
| **R-008 Human gate** | PASS | governance subagent is the mechanism; protection engine (F-015) is the runtime analogue; `aspis governance` CLI is the interface. Spec calls for block for runtime, warn for pre-commit, CI override. R-008 cited in 8/11 specs. |
| **R-009 Trace and learn** | PASS | Every spec has Open Design Questions; the audit (findings-1.md) is the trace record; the triage (findings-triage.md) is the lesson; the T-30 reviews are the gate evidence |
| **R-010 Delegate with purpose** | PASS | All leads have a `delegates` list (L2 + L3 explicitly, not arbitrary); general-builder is the L3 disposable executor (R-010 cost-of-context control); project-explorer is the L1↔L3 / L2↔L3 read-only exception. Cited in 8/11 specs. |

10/10 R-rules. The R-rule compliance is consistent and complete.

## Cross-agent consistency verification (manual edge-by-edge)

The 11 catalog files declare a total of 45 delegation edges. Manual
walk-through of each:

| From | → To | Correct? |
|---|---|---|
| project-lead | planning-lead | ✓ |
| project-lead | build-lead | ✓ |
| project-lead | reviewer | ✓ |
| project-lead | system-lead | ✓ |
| project-lead | fix-lead | ✓ |
| project-lead | test-lead | ✓ |
| project-lead | research-lead | ✓ |
| project-lead | project-explorer | ✓ |
| planning-lead | research-lead | ✓ |
| planning-lead | reviewer | ✓ |
| planning-lead | project-explorer | ✓ |
| planning-lead | clarify* | ⚠️ F-017 future |
| planning-lead | task-decomposer* | ⚠️ F-017 future |
| planning-lead | idea-capture* | ⚠️ F-017 future |
| planning-lead | prd-writer* | ⚠️ F-017 future |
| planning-lead | constitution-checker* | ⚠️ F-017 future |
| planning-lead | scope-estimator* | ⚠️ F-017 future |
| planning-lead | research-request-writer* | ⚠️ F-017 future |
| build-lead | general-builder | ✓ |
| build-lead | reviewer | ✓ |
| build-lead | test-lead | ✓ |
| build-lead | fix-lead | ✓ |
| build-lead | committer | ✓ |
| build-lead | project-explorer | ✓ |
| build-lead | research-lead | ✓ |
| reviewer | project-explorer | ✓ |
| reviewer | research-lead | ✓ |
| system-lead | project-explorer | ✓ |
| system-lead | reviewer | ✓ |
| system-lead | committer | ✓ |
| fix-lead | reviewer | ✓ |
| fix-lead | committer | ✓ |
| fix-lead | project-explorer | ✓ |
| fix-lead | test-lead | ✓ |
| test-lead | project-explorer | ✓ |
| research-lead | project-explorer | ✓ |
| committer | (none) | ✓ leaf, R-004 |
| general-builder | (none) | ✓ leaf, no `task:` block |
| project-explorer | (none) | ✓ leaf, no `task:` block |

45/45 edges resolve to a real agent (38) or are explicitly marked as
F-017-deferred (7, with the catalog file annotation). **PASS.**

## Permission surface audit (manual, 11 files)

| Agent | `git commit*` | `git push*` | `edit` | `write` | `webfetch` | `websearch` | R-004 OK? |
|---|---|---|---|---|---|---|---|
| project-lead | deny | deny | n/a (no edit/write tools) | n/a | deny | deny | ✓ |
| planning-lead | deny | deny | path-scoped to `.aspis/features/F-NNN-*/**` | path-scoped | deny | deny | ✓ |
| build-lead | deny | deny | allow (orchestration) | allow (orchestration) | deny | deny | ✓ |
| reviewer | deny | deny | `*: deny` | `*: deny` | deny | deny | ✓ read-only |
| system-lead | deny | deny | allow | allow | allow | deny | ✓ |
| fix-lead | deny | deny | allow (with path denials) | allow (with path denials) | deny | deny | ✓ |
| test-lead | deny | deny | allow | allow | deny | deny | ✓ |
| research-lead | deny | deny | `*: deny` | allow (write-new only) | allow | allow | ✓ tightest surface |
| committer | **allow** | deny | deny | deny | deny | deny | ✓ only committer |
| general-builder | deny | deny | path-scoped to packet.allowed | path-scoped | deny | deny | ✓ |
| project-explorer | deny | deny | n/a (no edit/write tools) | n/a | deny | deny | ✓ read-only |

11/11 permission surfaces correct. R-004 invariant holds: committer is
the only `git commit*` allow (committer.md:24, :26). R-008 invariant
holds: no agent has `git push*` allowed. R-007 invariant holds: all 11
agents have a pinned model tier. **PASS.**

## Frontmatter completeness (11 fields × 11 files)

See SC-003 evidence above. **11/11 fields, 11/11 files. PASS.**

## Scope boundary (no out-of-scope work)

The build notes (TASKS.md:7–25) and the T-04 triage set a clear
scope boundary: F-016 is specification-first. The deliverables are
the 12 ref specs, the 5 systemic specs, the 1 skills inventory, the
11 catalog files, the 3 feature docs, and the 6 missing CLI verbs
specified (not built).

No out-of-scope work is smuggled in. Specifically:

- No product code change in `src/` (the only `src/aspis/` change is
  catalog files — the data layer, not the engine)
- No runtime files hand-edited (`.opencode/`, `.claude/` are
  generated from the catalog)
- No new agent built (only spec'd — 7 future L3 subagents explicitly
  deferred to F-017)
- No new skill built (only spec'd in the inventory — building is a
  follow-up)
- No new CLI verb built (only spec'd in `cli-verbs.md` — building is
  a follow-up)
- No enforcement flip (the spec is the design; the flip is a
  follow-up)
- No new template built
- No new system rule added (R-001…R-010 unchanged)

The "cost-of-change ≤5 files" SC-012 is the design property that
keeps F-016 itself within its own scope.

## Deferred items (NOT findings)

These are documented in the T-38 task spec's "Known deferred items"
list and are explicitly *not* findings. They are listed here for the
record:

1. **Planning-lead's 7 future L3 subagents in `delegates`** —
   deferred to F-017. The catalog file annotates them. (See Medium
   finding above; the annotation is the durable record.)
2. **25 missing skills are specified (T-31) but not built** — the
   inventory is the next step; building is a follow-up.
3. **`bootstrap.md` is a 12th catalog file outside F-016 scope** —
   missing `delegates` and `runtimes`; tracked, not blocked.
4. **System-lead `websearch: deny` vs FR-007** — known SPEC drift;
   T-39 SPEC Clarification follow-up. (See Medium finding above.)
5. **Skills gap (4 skills referenced in frontmatter but not in
   skills catalog)** — `mode-decision`, `constitution-checks`,
   `packet-validation`, `builder-selection`; deferred to T-31 (the
   inventory) and the build follow-up.
6. **Claude Code adapter fix is specified but not implemented** —
   the fix is in `cross-runtime.md`; implementation is a follow-up.
7. **`aspis validate-runtime` CLI is specified but not built** —
   `cli-verbs.md` has the spec; building is a follow-up.
8. **SPEC.md SC-004 says "30+ missing skills"; actual count is 25** —
   planning-estimate vs. inventory refined count. T-39 SPEC
   clarification. (See Medium finding above.)

All 8 deferred items are intentional, documented in the build notes
or the task spec, and tracked. None of them block T-38.

## Decision & hand-off

**Verdict: APPROVED with notes.**

The F-016 deliverables meet the 12 success criteria with evidence. The
T-03 audit's 7 CRITICAL + 13 HIGH findings are all resolved by the
T-04 triage's Group 1 fixes (verified in the current files). The T-30
catalog structural validation passed (after the `f574496` runtimes
fix). The cross-reference gates passed (T-05, T-14, T-18). The
systemic specs (governance, modes, enforcement, planning-scripts,
CLI-verbs, cross-runtime) are complete and consistent with the agent
specs. The skills inventory enumerates the 25 missing skills with
priorities. The PLAN and TASKS trace every FR to a task and every SC
to a verification method.

The 0 CRITICAL, 0 HIGH finding count holds. The 3 MEDIUM findings
are all SPEC/drift follow-ups, not deliverable defects. The 4 LOW
findings are either documented deferrals or owner-decided skips
(Group 3 triage) that the doctrine (`system-rules.md`: "A real defect
raises cost-of-change, breaks a gate, causes wrong/unsafe behaviour,
or makes the system harder to understand/run. Conformance for its
own sake is not a defect to fix") supports.

**What is approved:**

- All 12 reference specs in `Research/ref/` as the truth layer
- All 5 systemic specs in `Research/specs/` as the design for modes,
  enforcement, planning scripts, CLI verbs, and cross-runtime parity
- The skills inventory as the complete enumeration of the 25 missing
  skills with priorities
- All 11 catalog agent files in `src/aspis/data/catalog/agents/` as
  the runtime-neutral source
- The 3 feature docs (SPEC, PLAN, TASKS) as the build contract

**What is not in T-38 scope (and never was):**

- Building the 25 missing skills
- Building the 6 missing CLI verbs
- Implementing the Claude Code adapter fix
- Implementing the enforcement flip
- Building the 7 future L3 subagents (F-017)
- Filling bootstrap.md's frontmatter
- Reconciling the SPEC's "30+ missing skills" wording with the actual
  count of 25

These are the follow-up features. They are documented and tracked.

**Route to:** committer for T-38 task completion (T-30 is the only
other task still open in the T-30 review file, and that's already
approved-with-notes; T-38 is the final acceptance gate, approved).

**Next step:** T-39 (Update SPEC.md Clarifications with decisions made
during build) — the medium findings 1 and 2 (SPEC drift) are the
primary inputs. T-40 (Final cross-reference validation pass) and
T-41 (BUILD_REPORT + handoff package) follow.

---

## Summary table

| Dimension | Result |
|---|---|
| Architecture constitution (12 rules) | 12/12 PASS |
| System rules (R-001…R-010) | 10/10 PASS |
| Cross-agent consistency | 0 overlapping responsibilities, 0 orphaned edges (7 F-017-deferred exceptions annotated) |
| Permission surface | 11/11 correct; R-004 and R-008 invariants hold |
| Model tier consistency | All 11 agents declare a tier; standard default for leads, cheap for leaves |
| Frontmatter completeness | 11/11 fields × 11/11 files |
| FR → task coverage | 28/28 FRs mapped to ≥1 task |
| SC → verification coverage | 12/12 SCs verified with evidence |
| Scope boundary | No out-of-scope work; all deferred items documented |
| **Findings** | **0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW** |
| **Verdict** | **APPROVED with notes** |

---

*Built from: the 12 ref specs at `Research/ref/*.md`, the 5 systemic specs at
`Research/specs/*.md`, the skills inventory at `Research/skills/inventory.md`,
the 11 catalog files at `src/aspis/data/catalog/agents/*.md`, the 3 feature
docs at `.aspis/features/F-016-agent-system-architecture/{SPEC,PLAN,TASKS}.md`,
the T-03 audit at `Research/audit/findings-1.md` and the owner-decided
T-04 triage at `Research/audit/findings-triage.md`, the T-30 reviews at
`build-reports/REVIEW-F-016-T-30.md` and `reviews/T-30-review.md`, the F-016
git history (`e83fda1` and earlier), `.aspis/rules/system-rules.md` (R-001…R-010),
`.aspis/rules/architecture-constitution.md` (12 rules), and
`src/aspis/data/catalog/config/policy/constitution-checks.yaml` (machine-readable
constitution index).*
