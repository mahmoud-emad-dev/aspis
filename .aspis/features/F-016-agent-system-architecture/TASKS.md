# F-016 — Tasks

> Mode: **production**
> Total tasks: 41
> Critical path: T-01 → T-03 → T-04 → T-05 → T-14 → T-18 → T-30 → T-32..T-37 → T-38 → T-40

## Build notes — locked decisions (read before starting)

- **T-01, T-02, T-03 are DONE** — research verified; `cross_ref_agents.py` built
  (`994d592`); `findings-1.md` audit produced (`d0e2d88`). **Resume at T-04.**
- **T-04 is scoped by `Research/audit/findings-triage.md`** (owner-decided):
  apply the ~10 Group-1 fixes only, NOT all 40 findings. Group-2 = defer /
  handled elsewhere; Group-3 = skip (conformance-only).
- **Catalog is the truth.** Fix the design in the catalog (Phase 4); the owner's
  *live* runtime is a personal/custom setup — do not chase it. Fixes are
  **iterative, not final** — set what a clear, minimal role needs now.
- **Keep each role clear and minimal** (role + skills + assets) so standard/cheap
  models succeed; differentiate do-it-myself vs delegate (R-010).
- **Subagent roster is OUT of scope → F-017.** The "future subagents" named in the
  specs are NOT built here — leave them as references. See
  `Research/subagent-roster-and-delegation.md`.
- **Rules reorg is already DONE** (4-layer model + R-010 + `project-rules.md`,
  live+catalog synced). Do not redo; keep agent specs consistent with it.
- **Model tiers:** standard default / deeper when warranted, per user preference +
  available models. Full model-tier scoring is a **future feature** — not built here.

## Phase 1 — Setup
Shared scaffolding everything else needs. Blocked by: nothing.

- [x] T-01 [P0] [low] [simple] [config] — Verify research completeness: confirm all 12 research files, 8 reference specs, and 2 reviewer audits exist and are accessible — **DONE**
  - Files: `Research/core-loops-2026.md` through `Research/review-local-docs-rules.md` (14 files total)
  - Depends on: none | Blocks: T-03
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-02 [P1] [medium] [moderate] [feature] [P] — Create cross-reference validation script `cross_ref_agents.py` — **DONE** (`994d592`)
  - Files: `.aspis/scripts/planning/cross_ref_agents.py` (new)
  - Depends on: none | Blocks: T-05, T-14, T-18, T-40
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Script spec**: Reads all 11 `Research/ref/*.md` files. Validates: (1) no two agents claim the same responsibility, (2) every delegation edge points to an existing agent, (3) every skill referenced resolves to a catalog entry, (4) every `[NEEDS CLARIFICATION]` is flagged. Outputs PASS/FAIL with file:line findings.

**Checkpoint**: research verified, cross-ref tool ready.

## Phase 2 — Foundational (blocking)
Core infrastructure ALL stories depend on — no story work until this completes.

- [x] T-03 [P0] [high] [complex] [review] — Reviewer adversarial audit of all 8 lead reference specs — **DONE** (`d0e2d88`; triaged in `findings-triage.md`)
  - Files: All 8 `Research/ref/{project-lead,planning-lead,build-lead,reviewer,system-lead,fix-lead,test-lead,research-lead}.md`
  - Depends on: T-01 | Blocks: T-04, T-05
  - Packet: V3 (deep) | Builder: deep | Review: reviewer (multi-lens, all 9 dimensions)
  - **Goal**: Produce `Research/audit/findings-1.md` — adversarial review of all 8 specs against the architecture constitution, system rules, and cross-agent consistency. Classify findings: CRITICAL / HIGH / MEDIUM / LOW. Every finding has file:line evidence.

- [x] T-04 [P0] [high] [moderate] [fix] — Address CRITICAL and HIGH findings from audit — **DONE** (`7bfd679`)
  - Files: Affected `Research/ref/*.md` files (subset, determined by T-03 findings)
  - Depends on: T-03 | Blocks: T-05
  - Packet: V3 (deep) | Builder: standard | Review: build-lead
  - **Goal**: Apply the LOCKED work-order in `Research/audit/findings-triage.md` (owner-decided) — the focused **~10 Group-1 fixes, NOT all 40**. Honour its refinements: system-lead modifies runtime **only via tools scoped to `.aspis/`** (B-6); research-lead `write:allow`/`edit:deny` is **intentional** — document the rationale, don't add edit (B-5); reviewer + research-lead tiers = **standard default / deeper when warranted** per user preference + available models, **ignore the live custom model** (F-3/A-1/C-7); reviewer drops `aspis artifact test` (D-9); remove `plan-critic`/`review-strategy` from planning-lead (B-1); add the "if stuck, stop" rule to reviewer + research-lead (A-4/A-5); reviewer plan-critic 12-vs-6 labelled (B-2). Also **reword one side** of the planning-lead↔build-lead "confirm clean state" responsibility so the cross-ref gate (E-2 MEDIUM) goes green. Group-2 = defer; Group-3 = skip. Each resolution documented (finding ref, what changed, why sufficient).

- [x] T-05 [P0] [medium] [moderate] [test] — Cross-reference consistency check: run `cross_ref_agents.py` on all 8 lead specs — **DONE** — gate PASS (0 HIGH/0 MEDIUM)
  - Files: `cross_ref_agents.py`, all 8 `Research/ref/*.md`
  - Depends on: T-02, T-04 | Blocks: T-06..T-14
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Gate**: `python .aspis/scripts/planning/cross_ref_agents.py --scope leads` exit 0. Fix any FAIL.

**Checkpoint**: 8 lead specs audited, findings resolved, cross-reference clean.

## Phase 3 — User Story 1 — Core Agent Specs (priority: P1) 🎯 MVP
**Goal**: All 8 lead agent reference specs are locked (finalized, sign-off ready).
**Independent test**: `cross_ref_agents.py --scope leads` exit 0. Every spec has all required sections. 0 CRITICAL, 0 HIGH unresolved findings.

- [x] T-06 [P1] [medium] [simple] [docs] [US1] [P] — Lock project-lead reference spec (final pass) — **DONE**
  - Files: `Research/ref/project-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self
  - **Acceptance**: All 16 sections present. Identity block matches master synthesis. "If stuck, stop" rule present. Acceptance criteria checkboxes verified.

- [x] T-07 [P1] [medium] [simple] [docs] [US1] [P] — Lock planning-lead reference spec — **DONE**
  - Files: `Research/ref/planning-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-08 [P1] [medium] [simple] [docs] [US1] [P] — Lock build-lead reference spec — **DONE**
  - Files: `Research/ref/build-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-09 [P1] [medium] [simple] [docs] [US1] [P] — Lock reviewer reference spec — **DONE**
  - Files: `Research/ref/reviewer.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-10 [P1] [medium] [simple] [docs] [US1] [P] — Lock system-lead reference spec — **DONE**
  - Files: `Research/ref/system-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-11 [P1] [medium] [simple] [docs] [US1] [P] — Lock fix-lead reference spec — **DONE**
  - Files: `Research/ref/fix-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-12 [P1] [medium] [simple] [docs] [US1] [P] — Lock test-lead reference spec — **DONE**
  - Files: `Research/ref/test-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [x] T-13 [P1] [medium] [simple] [docs] [US1] [P] — Lock research-lead reference spec — **DONE**
  - Files: `Research/ref/research-lead.md` (modify)
  - Depends on: T-05 | Blocks: T-14
  - Packet: V1 (light) | Builder: cheap | Review: self

- [ ] T-14 [P1] [medium] [moderate] [test] [US1] — Re-run cross-reference validation on all 11 specs (8 leads + 3 placeholder leaf stubs)
  - Files: `cross_ref_agents.py`, all 8 locked `Research/ref/*.md`
  - Depends on: T-06..T-13 | Blocks: Phase 4
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Gate**: `python .aspis/scripts/planning/cross_ref_agents.py --scope all` exit 0. All `[NEEDS CLARIFICATION]` resolved.

**Checkpoint**: User Story 1 complete — all 8 lead specs locked and cross-validated. This is the MVP.

## Phase 4 — User Story 2 — Leaf Agents + Catalog (priority: P2)
**Goal**: 3 leaf agent specs produced; all 11 catalog files updated; missing skills inventoried.
**Independent test**: All 11 catalog files pass structural validation. Every skill referenced resolves to a catalog entry. Leaf specs pass review.

### Leaf agent specs (parallel)
- [ ] T-15 [P1] [low] [simple] [docs] [US2] [P] — Produce committer reference spec (light, 6 sections)
  - Files: `Research/ref/committer.md` (new)
  - Depends on: T-14 | Blocks: T-18
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Sections**: Identity, Responsibilities→Skills, Permission Surface, Model Tier, Use Cases, Acceptance Criteria. R-004 one-writer enforced. `git commit*` is the only bash write.

- [ ] T-16 [P1] [low] [simple] [docs] [US2] [P] — Produce general-builder reference spec (light, 6 sections)
  - Files: `Research/ref/general-builder.md` (new)
  - Depends on: T-14 | Blocks: T-18
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Sections**: Identity, Responsibilities→Skills, Permission Surface, Model Tier, Use Cases, Acceptance Criteria. Context-isolated. One packet, one report, exit.

- [ ] T-17 [P1] [low] [simple] [docs] [US2] [P] — Produce project-explorer reference spec (light, 6 sections)
  - Files: `Research/ref/project-explorer.md` (new)
  - Depends on: T-14 | Blocks: T-18
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Sections**: Identity, Responsibilities, Permission Surface, Model Tier, Use Cases, Acceptance Criteria. Read-only. Compact summaries, never raw output.

- [ ] T-18 [P1] [medium] [moderate] [test] [US2] — Cross-reference leaf specs against leads
  - Files: `cross_ref_agents.py`, 3 new `Research/ref/{committer,general-builder,project-explorer}.md`
  - Depends on: T-15, T-16, T-17 | Blocks: T-19..T-29
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Gate**: No overlapping responsibilities with leads. All delegation edges to these agents from leads are valid. Committer is the only agent with `git commit*` allowed.

### Catalog file updates (parallel per agent, serialized per batch)

- [ ] T-19 [P1] [medium] [moderate] [config] [US2] — Update project-lead catalog file to match reference spec
  - Files: `src/aspis/data/catalog/agents/project-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Changes**: Frontmatter: mode=primary, model=standard, delegates aligned (remove committer if present), skills verified. Body: identity block matches spec. Add `> Derived from Research/ref/project-lead.md` header.

- [ ] T-20 [P1] [medium] [moderate] [config] [US2] [P] — Update planning-lead catalog file
  - Files: `src/aspis/data/catalog/agents/planning-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Changes**: Frontmatter: mode=subagent (until promoted), model=standard, delegates aligned (remove committer), skills verified. Body: planning lifecycle phases, mode system, task packet versions.

- [ ] T-21 [P1] [medium] [moderate] [config] [US2] [P] — Update build-lead catalog file
  - Files: `src/aspis/data/catalog/agents/build-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-22 [P1] [medium] [moderate] [config] [US2] [P] — Update reviewer catalog file
  - Files: `src/aspis/data/catalog/agents/reviewer.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Changes**: edit/write: deny (R-004 read-only). Add 9 review dimensions. Add 4-verdict system with severity rubric.

- [ ] T-23 [P1] [medium] [moderate] [config] [US2] [P] — Update system-lead catalog file
  - Files: `src/aspis/data/catalog/agents/system-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Changes**: Protected scope boundaries explicit. Deterministic-first ladder. Post-change validation sequence. websearch: deny (align with catalog intent).

- [ ] T-24 [P1] [medium] [moderate] [config] [US2] [P] — Update fix-lead catalog file
  - Files: `src/aspis/data/catalog/agents/fix-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-25 [P1] [medium] [moderate] [config] [US2] [P] — Update test-lead catalog file
  - Files: `src/aspis/data/catalog/agents/test-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-26 [P1] [medium] [moderate] [config] [US2] [P] — Update research-lead catalog file
  - Files: `src/aspis/data/catalog/agents/research-lead.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Changes**: Cache-first discipline. Tightest permission surface. edit: deny. bash: context scripts only.

- [ ] T-27 [P1] [medium] [moderate] [config] [US2] [P] — Update committer catalog file
  - Files: `src/aspis/data/catalog/agents/committer.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-28 [P1] [medium] [moderate] [config] [US2] [P] — Update general-builder catalog file
  - Files: `src/aspis/data/catalog/agents/general-builder.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-29 [P1] [medium] [moderate] [config] [US2] [P] — Update project-explorer catalog file
  - Files: `src/aspis/data/catalog/agents/project-explorer.md` (modify)
  - Depends on: T-18 | Blocks: T-30
  - Packet: V2 (standard) | Builder: standard | Review: build-lead

- [ ] T-30 [P0] [high] [complex] [test] [US2] — Catalog structural validation: all 11 files pass schema check
  - Files: All 11 `src/aspis/data/catalog/agents/*.md`
  - Depends on: T-19..T-29 | Blocks: T-31, Phase 5
  - Packet: V3 (deep) | Builder: standard | Review: reviewer
  - **Gate**: Manual schema check (or `aspis validate-runtime` if built). Every frontmatter has: name, description, mode, model, tools, permissions, delegates, skills, runtimes, export_scope. Every referenced skill exists in catalog. Every delegate exists. No committer in non-committer task lists.

- [ ] T-31 [P1] [medium] [moderate] [docs] [US2] — Produce missing skills inventory
  - Files: `Research/skills/inventory.md` (new)
  - Depends on: T-30 | Blocks: none
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Consolidated inventory of all 30+ skill gaps across all agent specs. Per entry: skill name, purpose (1 line), owning agent, priority (P0/P1/P2), estimated sections. Sorted by priority. Cross-referenced against existing catalog at `src/aspis/data/catalog/skills/`.

**Checkpoint**: User Story 2 complete — leaf specs produced, all catalog files aligned, skills inventoried.

## Phase 5 — User Story 3 — Systemic Gaps & Governance (priority: P3)
**Goal**: All systemic infrastructure gaps are specified.
**Independent test**: Every systemic spec passes cross-reference against the agent specs that depend on it.

- [ ] T-32 [P1] [high] [complex] [feature] [US3] [P] — Produce governance subagent spec
  - Files: `Research/ref/governance.md` (new)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V3 (deep) | Builder: standard | Review: reviewer (security focus)
  - **Goal**: Spec defining the governance subagent — the ONLY agent permitted to edit `rules/**` and `profiles/defaults.yaml`. Must define: protected paths list (from `hooks.yaml`), R-008 human-approval workflow (request → record → audit), approval ledger format, intervention handler for blocking in-flight writes to protected paths. Deterministic script, not LLM agent (per system-lead §12 decision).

- [ ] T-33 [P1] [high] [moderate] [feature] [US3] [P] — Produce modes.yaml spec
  - Files: `Research/specs/modes.yaml` (new spec document, not the actual YAML file)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Complete spec for `.aspis/config/modes.yaml`. Every knob defined with per-mode values: spec (bullets/stories/full), architecture (skip/note/full), task_size (large/medium/small), plan_review (skip/self/independent), build_review (light/standard/full), test_depth (gate/core/full), docs (none/minimal/complete), promotable (false/true/N/A). Consistent with planning-lead reference spec §3 and current `CORE_LOOP.md`.

- [ ] T-34 [P1] [high] [moderate] [feature] [US3] [P] — Produce enforcement mode spec
  - Files: `Research/specs/enforcement.md` (new)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Spec defining enforcement boundaries: `block` for runtime tools (Edit/Write), `warn` for pre-commit hooks. CI override via `ASPIS_ENFORCEMENT=block`. Auto-fix behavior per mode. Transition plan from current warn-only to block. Consistent with D-010 (hooks non-blocking by default) — this is the flip decision.

- [ ] T-35 [P1] [medium] [moderate] [feature] [US3] [P] — Produce planning scripts deployment spec
  - Files: `Research/specs/planning-scripts.md` (new)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Spec for deploying 3 scripts from catalog to `.aspis/scripts/planning/`: `feature_scaffold.py` (P1 scaffold), `task_compile.py` (P6 tasks), `prereq_validate.py` (P8 gate). Each entry: catalog source path, destination path, trigger (when called), validation (how to confirm deployed correctly), and the agent that calls it.

- [ ] T-36 [P1] [medium] [moderate] [feature] [US3] [P] — Produce missing CLI verbs spec
  - Files: `Research/specs/cli-verbs.md` (new)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Spec for 6 missing CLI verbs: `validate-runtime` (structural frontmatter check), `validate-index` (registry consistency), `byte-parity` (catalog↔runtime parity), `drift` (frontmatter field drift detection), `export` (catalog→runtime export with protection engine), `governance` (R-008 approval workflow). Each entry: purpose, priority (P0/P1), interface signature, expected output.

- [ ] T-37 [P1] [medium] [moderate] [feature] [US3] [P] — Produce cross-runtime parity spec
  - Files: `Research/specs/cross-runtime.md` (new)
  - Depends on: T-30 | Blocks: T-38
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Goal**: Spec defining cross-runtime parity requirements. Claude Code adapter must preserve `permission:` block (currently stripped). Byte-parity check: `aspis byte-parity` proves catalog regenerates live byte-for-byte. CONFLICT/PROTECT decision handling from F-015 protection engine. Cross-runtime test: same catalog → both runtimes generate byte-identical assets where capability-equivalent.

**Checkpoint**: User Story 3 complete — all systemic gaps specified.

## Phase 6 — Polish
Cross-cutting cleanup and final acceptance.

- [ ] T-38 [P0] [high] [complex] [review] — Final acceptance review: all artifacts pass independent reviewer audit
  - Files: All files in scope — `Research/ref/*.md` (11), `Research/specs/*.md` (6), `Research/skills/inventory.md`, `src/aspis/data/catalog/agents/*.md` (11), `SPEC.md`, `PLAN.md`, `TASKS.md`
  - Depends on: T-32..T-37, all prior checkpoints | Blocks: T-40
  - Packet: V3 (deep) | Builder: deep | Review: reviewer (full multi-lens, all 9 dimensions)
  - **Gate**: 0 CRITICAL, 0 HIGH unresolved findings. All SC-001 through SC-012 verified with evidence.

- [ ] T-39 [P2] [low] [simple] [docs] [P] — Update SPEC.md Clarifications section with any decisions made during build
  - Files: `SPEC.md` (modify)
  - Depends on: T-38 | Blocks: none
  - Packet: V0 (inline) | Builder: cheap | Review: self

- [ ] T-40 [P0] [medium] [moderate] [test] — Final cross-reference validation pass
  - Files: `cross_ref_agents.py`, all 11 `Research/ref/*.md`, `Research/specs/*.md`
  - Depends on: T-38 | Blocks: none
  - Packet: V2 (standard) | Builder: standard | Review: build-lead
  - **Gate**: `python .aspis/scripts/planning/cross_ref_agents.py --scope all --include-systemic` exit 0. All SC-### verified.

- [ ] T-41 [P1] [low] [simple] [docs] — Produce BUILD_REPORT and handoff package for committer
  - Files: `BUILD_REPORT.md` (new)
  - Depends on: T-40 | Blocks: none
  - Packet: V1 (light) | Builder: cheap | Review: self
  - **Goal**: Summarize all artifacts produced, gate results, reviewer verdicts, and open follow-ups. Package: feature id, completed artifacts, task completion markers, active pointer. Hand to committer.

## Dependencies & execution order
- Setup (T-01, T-02) → Foundational (T-03→T-05) → US1: Core Specs (T-06→T-14) → US2: Leaf + Catalog (T-15→T-31) → US3: Systemic (T-32→T-37) → Polish (T-38→T-41).
- Within US1: T-06..T-13 are all [P] (parallel) once T-05 completes. T-14 serial after all locks.
- Within US2: T-15..T-17 are [P] (parallel). T-18 serial after all 3 leaf specs. T-19..T-29 are [P] (parallel) once T-18 completes. T-30 serial after all catalog updates. T-31 after T-30.
- Within US3: T-32..T-37 are all [P] (parallel) once T-30 completes.
- Polish: T-38 serial (needs all prior). T-39 parallel after T-38. T-40 serial after T-38. T-41 after T-40.

## Task criticality summary
| Level | Tasks | Count |
|---|---|---|
| **P0** (blocking) | T-01, T-03, T-04, T-05, T-30, T-38, T-40 | 7 |
| **P1** (important) | T-02, T-06..T-29, T-31..T-37, T-41 | 33 |
| **P2** (nice-to-have) | T-39 | 1 |

## Packet version distribution
| Version | Tasks | Count |
|---|---|---|
| **V0** (inline) | T-39 | 1 |
| **V1** (light) | T-01, T-06..T-13, T-41 | 10 |
| **V2** (standard) | T-02, T-05, T-14..T-37 (except V0/V1/V3) | 25 |
| **V3** (deep) | T-03, T-04, T-30, T-32, T-38 | 5 |
| **V4** (comprehensive) | — | 0 |

## Implementation strategy
- **MVP first**: Complete Setup + Foundational + US1 (T-01→T-14), then stop and validate. This delivers the 8 lead specs — the core of F-016.
- **Incremental**: Add US2 (leaf specs + catalog), validate independently. Then US3 (systemic gaps), validate. Finally polish and final acceptance.
- **Parallel where safe**: Within each user story, tasks touching different files can run in parallel. The [P] markers indicate this.
- **Critical path watch**: T-03 (audit) and T-30 (catalog validation) are the riskiest tasks — they have the most findings surface and the deepest review requirements.

## Build packets
`task_compile.py` turns each task above into a self-contained packet at
`.aspis/features/F-016-agent-system-architecture/tasks/T-NN.md` from `.aspis/templates/TASK_PACKET.md`,
so a context-isolated builder can complete it with nothing else.
