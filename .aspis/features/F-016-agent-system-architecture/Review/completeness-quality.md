# F-016 — Completeness & Quality Review

> **Reviewer:** reviewer (F-016, deep completeness + quality pass)
> **Date:** 2026-06-27
> **Scope:** All 28 FRs, all 12 SCs, 12 reference specs, 5 systemic specs, 11 (in-scope) catalog files, the 3 feature docs (SPEC/PLAN/TASKS), the BUILD_REPORT, and the T-30/T-38 review reports.
> **Stance:** Independent, evidence-backed. Assume every spec has gaps and every catalog file has drift; verify against the actual files, not the author's claims.
> **Verdict at a glance:** **APPROVE WITH CONDITIONS** (recommend a 4-issue follow-up, not a redo).

---

## 1 · Executive summary

F-016 is a large specification feature. The 8 lead reference specs are deep, well-cited, and pass an honest adversarial audit. The systemic specs (governance, modes, enforcement, planning-scripts, CLI-verbs, cross-runtime) are the most thoroughly-specified of the F-016 artifacts — governance.md in particular is exemplary (634 lines, append-only ledger with concurrency, three enforcement boundaries, no back door). The skills inventory is honest (25 missing, not the SPEC's "30+") and the catalog files have the required frontmatter shape after the `f574496` runtimes fix.

The feature is **not blocked** by the gaps below. They are:
- A consistent set of SPEC/catalog text drift (FR-007 wording wrong, system-lead `websearch` deny vs. the design source's allow, build_report claims vs. TASKS.md markers)
- A handful of contradictions between the reference specs that should be reconciled
- One design question (cost-of-change for an agent that needs a NEW profile) is left to "common case ≤3" but never proved for the F-017 subagents
- The build_report claims a successful end-to-end but TASKS.md still shows 22 tasks as `[ ]` and the `tasks/` folder is empty

Severity-weighted: 1 medium, 8 low. The reviewer audit (T-38) reached the same conclusion (0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW). I do not disagree with that verdict; I do recommend a brief follow-up to close the small drift items listed in §6 before the F-016 branch is merged.

The rest of this report drills into the evidence.

---

## 2 · FR coverage matrix (FR-001 through FR-028)

Each FR is rated **SATISFIED** / **PARTIAL** / **NOT MET** with file:line evidence.

### Agent specification requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-001** Complete reviewed spec for each of 11 agents | **SATISFIED** | 8 lead specs in `Research/ref/` (T-06..T-13), 3 leaf specs (T-15..T-17), `committer.md:229`, `general-builder.md:296`, `project-explorer.md:254` — all locked; T-38 review verdict APPROVED with notes. | 11/11 spec files present, all sections present. |
| **FR-002** Each spec defines identity/resp-skills/permission/delegation/model-tier/flows/use-cases/anti-patterns/error-handling/acceptance | **SATISFIED** | audit findings-1.md §A.1 confirmed 11/11 template coverage for project-lead, planning-lead, build-lead; 10/11 for system-lead/fix-lead; 8/11 for test-lead; 6/11 for research-lead at the time of the audit. T-04 Group-1 fixes (B-2: v1/v2 labelling; A-4: research-lead "if stuck" rule; A-5: reviewer "if stuck" rule) brought them all to 11/11. | See §5 contradiction: test-lead §9 is still titled "Escalation" rather than "Error Handling Matrix" (audit A-6 LOW, not fixed). |
| **FR-003** No two agents claim the same responsibility | **SATISFIED** | T-05 (7bfd679), T-14 (83abc72), T-18 (8d41c56), T-40 — all PASS via `cross_ref_agents.py`. 0 overlaps at sign-off. | |
| **FR-004** Every delegation edge points to an existing agent | **PARTIAL** | 38/45 edges resolve; 7/45 are F-017-deferred (planning-lead's `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer` — `planning-lead.md:42-48`). The catalog file annotates them as `# Future L3 subagents (referenced in spec, may not yet exist)`. | The build_notes and T-38 mark these as the owner-decided exception. Technically, FR-004 fails; the doc tells the gate to ignore it. The annotation is durable but the gate's "every delegate exists" rule is still passing. |
| **FR-005** Every agent declares a model tier | **SATISFIED** | All 8 lead specs have a Model Tier section (project-lead §3, planning-lead §5, build-lead §4, reviewer §4, system-lead §4, fix-lead §4, test-lead §4, research-lead §1). 3 leaves: committer §4 `cheap`, general-builder §4 `cheap`, project-explorer §4 `cheap`. Catalog frontmatters all carry `model:`. | |
| **FR-006** Every agent has a defined permission surface (read/edit/bash/delegation/skill/web) | **SATISFIED** | All 11 in-scope catalog files declare `permissions:` (bash + webfetch + websearch at minimum). 6 leaves-only or leaf-lite specs add edit/write blocks (fix-lead, general-builder). reviewer & project-explorer explicitly omit edit/write tools. R-001 / R-004 invariants hold (T-38 §Permission surface audit). | |
| **FR-007** Universal denies present in every agent's permission surface (`git commit*` denied except committer; `git push*` denied; `webfetch`/`websearch` denied except system-lead and research-lead) | **NOT MET** (text drift; the system is correct, the SPEC is wrong) | **The actual deny list holds across all 11 catalog files** (T-38 verified: committer is the only `git commit*: allow`; no agent has `git push*: allow`; webfetch/websearch are correct per role). But **the SPEC text contradicts the design** — FR-007 implies system-lead `websearch: allow`, while the system-lead reference spec (`system-lead.md:134`) says `websearch: allow` and the system-lead catalog (`system-lead.md:32`) says `websearch: deny`. The catalog is right (the design is "system-lead is local-only, deterministic"; the T-23 owner decision locked this; the audits agreed). The SPEC text and the system-lead ref spec disagree with each other on the same sentence. | See §5 contradiction C-1. Tracked as a T-39 SPEC clarification follow-up. |
| **FR-008** Reviewer read-only | **SATISFIED** | `reviewer.md:26-29` (catalog): `edit: *: deny`, `write: *: deny`. `reviewer.md:98-105` (ref spec): "Read-only by design (R-004)". T-38 verified. | |
| **FR-009** Committer is the only agent with `git commit*` allowed | **SATISFIED** | `committer.md:24, 26` (catalog): `aspis commit*: allow`, `git commit*: allow`. All 10 others have `git commit*: deny`. T-38 verified. | |

### Catalog asset requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-010** All 11 catalog agent files updated to reflect ref specs | **SATISFIED** | All 11 in-scope catalog files have `> Derived from Research/ref/<name>.md` header and a `## Identity` block. T-30 re-review (`reviews/T-30-review.md`) PASSED after `f574496` (runtimes field added). | |
| **FR-011** Every catalog agent frontmatter has: name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope | **SATISFIED** | T-38 §SC-003 verified 11/11 fields × 11/11 files. T-30 had FAIL on `runtimes` (was missing in all 11); T-30 re-review confirmed `f574496` added `runtimes: []` to all 11. | |
| **FR-012** Every skill referenced exists in the catalog | **PARTIAL** | 4 skills referenced in frontmatter but not in the skills catalog: `mode-decision`, `constitution-checks`, `packet-validation`, `builder-selection` (T-38 §SC-002; T-30 review; `Research/skills/inventory.md:212-219`). T-31 inventory lists all 4 with priorities (all P0). Deferred to the skills-build follow-up. | Technically fails. The T-31 inventory is the complete enumeration; building the SKILL.md files is out of scope. |

### Systemic requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-013** Core loop documented with per-phase ownership, gates, mode overlays | **SATISFIED** | `Research/ref/project-lead.md:534-693` (12 procedural flows), `Research/ref/planning-lead.md:54-127` (8 phases), `Research/ref/build-lead.md:47-80` (9-step loop). Each has a mode-overlay table. | |
| **FR-014** Delegation model documented (L1→L2→L3, 5-field packet, recontextualization, single-owner) | **SATISFIED** | `project-lead.md:695-744` (packet shape + recontextualization protocol), all 8 lead specs have a delegation table; `cross_ref_agents.py` enforces the edges. | |
| **FR-015** Permission model documented (deny→ask→allow, first-match-wins, 3 layers, 3 boundaries) | **SATISFIED** | `system-lead.md:208-242` (config tier model + protection engine), `system-lead.md:243-274` (hook system), `governance.md:344-426` (intervention handler, 3 boundaries), `cross-runtime.md` (CONFLICT/PROTECT). | |
| **FR-016** Model tier strategy documented (70/20/10, tiered routing, cascade-on-failure) | **PARTIAL** | `planning-lead.md:208-216` lists the 3 cost profiles (save-money 85/14/1, balanced 70/20/10, max-quality 40/30/30). Cascade-on-failure is in `planning-lead.md:200-207` (3 attempts). But there is **no single artifact** that says "70/20/10 is the default — here is how it is enforced" — the number lives in planning-lead's reference spec only. The system-lead ref spec doesn't restate it. The modes.yaml spec doesn't restate it. | R-007 (pinned models) is honoured by the catalog frontmatters, but the *strategy* is described in one place, not the three places the SPEC implies. |
| **FR-017** Error-handling matrix documented (catcher/fixer/reviewer, 3-attempt cap) | **SATISFIED** | `project-lead.md:828-845` (error matrix), `planning-lead.md:1081-1108`, `build-lead.md:539-568`, `fix-lead.md:212-228` (3-attempt hard cap), `governance.md:127-130` (workflow forbids). | |
| **FR-018** Governance subagent specified (protected paths, R-008, ledger, intervention) | **SATISFIED** | `Research/ref/governance.md` (634 lines, 7 sections). T-38 §SC-006 verified. | The spec is complete; the implementation is a follow-up. |
| **FR-019** modes.yaml specified with per-mode values for all 8 knobs | **SATISFIED** | `Research/specs/modes.yaml` (79 lines, 3 modes × 8 knobs = 24 values, all filled). | |
| **FR-020** Enforcement mode specified (`block` for runtime, `warn` for pre-commit, CI override) | **SATISFIED** | `Research/specs/enforcement.md` (71 lines, 3 boundaries × 3 modes, transition plan, CI override). | |

### Cross-runtime requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-021** Claude Code adapter preserves the `permission:` block | **SATISFIED (spec only)** | `Research/specs/cross-runtime.md:24-34` (target state + 5 acceptance criteria). | **The actual adapter fix is a follow-up**, not part of F-016. The spec is in place. |
| **FR-022** Cross-runtime byte-parity check (`aspis byte-parity`) specified with CONFLICT/PROTECT handling | **SATISFIED (spec only)** | `Research/specs/cross-runtime.md:42-49` (decision table), `cli-verbs.md:53-72` (CLI verb interface). | **The CLI is a follow-up**; the spec is in place. |

### Skills and tools requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-023** All 30+ missing skills specified with purpose, owning agent, priority | **PARTIAL** (count is wrong, but the substance is correct) | `Research/skills/inventory.md` lists 25 missing skills (13 P0, 7 P1, 5 P2). The SPEC says "30+"; T-39 clarification acknowledges the wording overstates. Each entry has: skill name, 1-line purpose, owning agent(s), priority, estimated sections, source citation. | Count is 25, not 30+; SPEC is wrong, inventory is correct. The substance — purpose, owner, priority — is fully present. |
| **FR-024** All 6 missing CLI verbs specified | **SATISFIED** | `Research/specs/cli-verbs.md` (172 lines, 6 verbs × purpose/priority/interface/caller/exit codes). | |
| **FR-025** All 3 planning scripts specified for deployment | **SATISFIED** | `Research/specs/planning-scripts.md` (97 lines, 3 scripts × source/destination/trigger/validation). | **The deployment itself is a follow-up**; the spec is in place. |

### Acceptance and quality requirements

| FR | Status | Evidence | Note |
|---|---|---|---|
| **FR-026** Every agent spec includes measurable acceptance criteria (checkbox list) | **SATISFIED** | project-lead §16 (18 checks), planning-lead §18 (19 checks), build-lead §14 (19 checks), reviewer §13 (12 checks), system-lead §14 (17 checks), fix-lead §12 (12 checks), test-lead §12 (10 checks), research-lead §13 (12 checks), committer §6 (14 checks), general-builder §6 (13 checks), project-explorer §6 (14 checks). | 11/11. |
| **FR-027** Every agent spec passes independent adversarial review with 0 CRITICAL and 0 HIGH unresolved | **SATISFIED** | T-03 audit (7 CRITICAL + 13 HIGH + 14 MEDIUM + 5 LOW = 49 findings). T-04 owner triage (Group 1 ~10 fixes applied; Group 2 deferred; Group 3 skip). T-38 re-verification: 0 CRITICAL, 0 HIGH. | |
| **FR-028** 12-point architecture constitution checked | **SATISFIED** | T-38 §"Architecture constitution compliance" walks all 12 rules; 12/12 PASS. | |

**FR coverage roll-up: 22 SATISFIED, 5 PARTIAL, 1 NOT MET (text drift).**

The "PARTIAL" cases are honest: 4 reference 7 future F-017 subagents (owner-decided), 1 references 4 skills not yet in the catalog (T-31 deferred), 1 cites a wrong count in the SPEC (clarified in T-39), 1 has the tier strategy in only one of the three places the SPEC implies. None are blockers; all are documented follow-ups.

The "NOT MET" (FR-007) is a text-drift between SPEC and design, not a system defect. See §5.

---

## 3 · SC verification (SC-001 through SC-012)

Each SC is rated **PASS** / **FAIL** / **PARTIAL** with measurable proof.

| SC | Status | Measurable Proof |
|---|---|---|
| **SC-001** 11 agent specs pass adversarial review, 0 CRITICAL, 0 HIGH unresolved | **PASS** | T-03 audit (39 unique findings: 7 CRITICAL + 13 HIGH + 14 MEDIUM + 5 LOW) + T-04 Group-1 fixes (10 applied) + T-38 verdict APPROVED with notes. Verifier: `REVIEW-F-016-T-38.md:506-512` (3 MEDIUM + 4 LOW, 0 CRITICAL, 0 HIGH). |
| **SC-002** Cross-agent consistency: 0 overlap, 0 orphaned edges, 0 references to non-existent skills | **PARTIAL** | T-05 (7bfd679), T-14 (83abc72), T-18 (8d41c56) all PASS via `cross_ref_agents.py`. 0 overlaps, 0 real orphans. **7 F-017 future subagents** in planning-lead's `delegates` and **4 missing skills** in frontmatters are owner-decided exemptions. Strictly: 11 violations (7 + 4) acknowledged, not "0". |
| **SC-003** 11 catalog files frontmatter-aligned with ref specs | **PASS** | T-30 PASS after `f574496`; T-38 §SC-003 verified 11/11 fields × 11/11 files. |
| **SC-004** 30+ missing skills specified | **PARTIAL** | Inventory has 25 missing (13 P0 + 7 P1 + 5 P2), not 30+. Substance correct; the "30+" wording overstates. T-39 SPEC clarification. |
| **SC-005** 6 missing CLI verbs specified | **PASS** | `cli-verbs.md`: 6 verbs × purpose/priority/interface/caller/exit codes. |
| **SC-006** Governance subagent spec R-008 compliant | **PASS** | `governance.md` 634 lines, 7 sections, 17 acceptance criteria. R-008 quoted verbatim from system-rules.md. |
| **SC-007** modes.yaml spec complete (every knob per mode) | **PASS** | `modes.yaml` spec: 3 modes × 8 knobs = 24 values, all filled. |
| **SC-008** Enforcement mode spec passes security review | **PASS** | `enforcement.md`: 3 boundaries, 3 modes, transition plan, CI override, no auto-fix. |
| **SC-009** 3 planning scripts have deployment specifications | **PASS** | `planning-scripts.md`: 3 scripts × source/destination/trigger/validation. |
| **SC-010** Claude adapter permission-block preservation specified | **PASS** | `cross-runtime.md`: 5 acceptance criteria for the fix + cross-runtime test procedure. |
| **SC-011** PLAN.md and TASKS.md ready for handoff (FR→task, SC→verification) | **PASS** | T-38 §SC-011 maps every FR to ≥1 task (28/28) and every SC to a verification method (12/12). |
| **SC-012** Cost-of-change ≤5 files to add a new agent | **PASS** | T-38 §SC-012 walks the 5-file worst case (ref spec + catalog + optional profile + optional SPEC + optional TASKS) and the 2-file common case. Healthy band per `architecture-constitution.md:33-38`. |

**SC roll-up: 9 PASS, 3 PARTIAL (SC-002, SC-004 — same root cause: documented deferrals / count overstatement; SC-002 contains the future-subagent and missing-skill caveats).**

---

## 4 · Section count verification

The BUILD_REPORT claims a section count per spec (12 specs × section counts). I verified:

| Spec | Claimed | Actual | Match? |
|---|---|---|---|
| project-lead | 16 | 16 (Identity, Resp→Skills, Model Tier, Permission, Delegation Map, Use Cases, Procedural Flows, Delegation Packet, Subagent Needs, Assets Inventory, Read-First Files, Error Handling, Core Rules, Anti-Patterns, Open Design, Acceptance) | ✓ |
| planning-lead | 17 | 17 (Identity, Planning Lifecycle, Mode System, Resp→Skills, Model Tier, Permission, Delegation Map, Use Cases, Task Packet System, Procedural Flow Production, Quality Standards, Dynamic Handling, Assets, Industry Patterns, Anti-Patterns, Error Handling, Open Design, Acceptance) | Actually 18, but `## 9 · Task Packet System` has 12 sub-sections (9.1-9.12) so the 17-section claim is defensible if the inventory treated 9 as one block. |
| build-lead | 16 | 16 (Identity, Lifecycle, Resp→Skills, Model Tier, Permission, Task Orchestration System, Delegation Map, Use Cases, Builder Security, Industry Patterns, Anti-Patterns, Error Handling, Open Design, Acceptance, plus core rules at end) | ✓ |
| reviewer | 16 | 13 (Identity, Review Types, Resp→Skills, Permission, 9 Review Dimensions, Verdict System, Plan Review, Industry Patterns, Use Cases, Anti-Patterns, Subagent Needs, Open Design, Acceptance) | **MISMATCH**: BUILD_REPORT says 16, actual is 13. |
| system-lead | 16 | 14 (Identity, Protected Scope, Resp→Skills, Model Tier, Permission, How System-Lead Works, Configuration Management, Hook System Management, System Health & Validation, Delegation Map, Use Cases, OLD ASPS Comparison, Open Design, Acceptance) | **MISMATCH**: claimed 16, actual 14. |
| fix-lead | 16 | 12 (Identity, Fix Lifecycle, Resp→Skills, Model Tier, Permission, Use Cases, 3-Attempt Cap, FIX_REPORT, Delegation Map, Anti-Patterns, Open Design, Acceptance) | **MISMATCH**: claimed 16, actual 12. |
| test-lead | 12 | 12 (Identity, Validation Lifecycle, Resp→Skills, Model Tier, Permission, Use Cases, Failure Classification, Anti-Patterns, Escalation, Open Design, Labs Testing, Acceptance) | ✓ (and §9 is still titled "Escalation", not "Error Handling Matrix" — finding A-6 from the audit, marked LOW, not fixed). |
| research-lead | 14 | 13 (Identity, 4-Step Procedure, Research Types, Use Cases, Cache System, Output Formats, Subagents, Escalation, Anti-Patterns, Full Use Case Catalog, Adversarial Findings, Skills/Tools/Subagents Inventory, Acceptance) | **MISMATCH**: claimed 14, actual 13. (Note: A-3 from the audit said "§10 is missing" but the doc was renumbered to 13 sections, not 14.) |
| committer | 6 | 6 (Identity, Resp→Skills, Permission, Model Tier, Use Cases, Acceptance) | ✓ |
| general-builder | 6 | 6 (Identity, Resp→Skills, Permission, Model Tier, Use Cases, Acceptance) | ✓ |
| project-explorer | 6 | 6 (Identity, Resp→Skills, Permission, Model Tier, Use Cases, Acceptance) | ✓ |
| governance | 7 | 7 (Identity, Protected Paths, R-008 Workflow, Approval Ledger, Intervention Handler, CLI Interface, Acceptance) | ✓ |

**4 mismatches** in the BUILD_REPORT section-count table: reviewer (16 vs 13), system-lead (16 vs 14), fix-lead (16 vs 12), research-lead (14 vs 13). All four *overstate* the section count. This is a documentation accuracy issue in the BUILD_REPORT, not a defect in the specs themselves. Low severity.

The leaf specs (committer, general-builder, project-explorer) and governance are exact.

---

## 5 · CONTRADICTION findings

The following contradictions exist in the F-016 artifacts. Each is rated by severity and named for follow-up.

### C-1 — SPEC FR-007 vs. design (system-lead `websearch`) — **MEDIUM**

| Where | What each says |
|---|---|
| `SPEC.md:69` (FR-007) | "All universal denies MUST be present in every agent's permission surface: `git commit*` denied except committer (R-004), `git push*` denied for all agents (R-008), `webfetch`/`websearch` denied except system-lead and research-lead." |
| `Research/ref/system-lead.md:134` | "`websearch` \| allow \| Runtime documentation and validation" (in the Permission Surface table) |
| `Research/ref/system-lead.md:432` (Open Design Questions #10) | "Live `websearch: allow` vs catalog `websearch: deny` drifts \| Reconcile" (acknowledges the drift) |
| `src/aspis/data/catalog/agents/system-lead.md:32` (catalog) | `websearch: deny` (the actual catalog frontmatter — what the runtime uses) |
| `Research/audit/findings-1.md:298-304` (D-4 INFORMATIONAL) | "system-lead.md has `webfetch: allow` and `websearch: allow` — correct" — this was true at audit time, when the live file had `websearch: allow`. |
| T-04 / T-23 | Owner-decided: keep `websearch: deny` in the catalog (T-23 build notes: "websearch: deny (align with catalog intent)") |
| `Research/system-lead-pentest.md:597, 976, 1209` | F-13 + F-24: "websearch allow is an open prompt-injection channel" (HIGH); "websearch live vs catalog drift" (MEDIUM) — both recommend deny. |
| T-39 plan | "Update SPEC.md Clarifications section with any decisions made during build" — open |

**The system is correct** (catalog has `websearch: deny` for system-lead, which the pentest and audit both say is the safer posture). **The SPEC text is wrong** (it implies allow) and **the system-lead ref spec is internally inconsistent** (its own §5 says allow; its own §13 says reconcile the drift). The runtime is consistent (deny). The drift is between the SPEC text and the design reality.

**Fix:** T-39 SPEC clarification must update FR-007 to "webfetch/websearch denied by default; webfetch and websearch both allowed only for research-lead" and update system-lead ref spec §5 to `websearch: deny` with the rationale already present in §13 and the pentest. This is the T-39 follow-up. Tracked.

### C-2 — system-lead reference spec §5 vs. §13 (internal) — **MEDIUM**

`system-lead.md:134` (Permission Surface table) says `websearch: allow`. `system-lead.md:432` (Open Design Questions) says "Live `websearch: allow` vs catalog `websearch: deny` drifts | Reconcile". The doc contradicts itself: the table says allow; the open question says the table's value drifted and needs reconciling (i.e., should be deny). Same fix as C-1.

### C-3 — planning-lead "if stuck" rule location — **LOW**

The audit (A-6 LOW) noted test-lead §9 is titled "Escalation" rather than "Error Handling Matrix". The owner decision was to skip (Group 3, conformance-only). The section is *content-correct*; only the *heading* disagrees with the project-lead/planning-lead convention. The triaged SKIP is justified by R-006 (state once, don't duplicate). Not a defect.

### C-4 — R-008 attribution in system-lead ref spec — **LOW**

`Research/ref/system-lead.md:10` (Identity) and `:103` (§3) both use R-008 as the human-gate citation. `governance.md:60-68` quotes the system-rules R-008 verbatim. R-008 is consistent. The build_notes say "R-008/R-009 attribution: All references to 'protected paths' and 'human approval' must cite R-008." This is followed.

### C-5 — T-38 says 0 CRITICAL/0 HIGH; build_report's findings-1 said 7 CRITICAL/13 HIGH — **LOW**

The audit findings are real and were resolved by T-04 Group-1 fixes; the T-38 verdict of 0 CRITICAL/0 HIGH is the *post-fix* state. This is the intended trajectory, not a contradiction. Documented.

### C-6 — BUILD_REPORT says 41/41 complete; TASKS.md shows 22 still `[ ]` — **MEDIUM**

The T-19..T-41 tasks (22 tasks) are written as `- [ ]` in TASKS.md (verified by reading the file). The T-38 review and the BUILD_REPORT (lines 8, 65-92) both claim 41/41 complete and 0 CRITICAL/0 HIGH. The T-30 review at line 49-50 says "T-19..T-29: 11 files aligned to ref specs" and T-31 ("Skills inventory") is "25 missing skills identified". The T-32..T-37 specs all exist on disk. T-38 verdict is APPROVED.

Yet the TASKS.md checkbox for T-19..T-41 was never flipped to `[x]`, and the `tasks/` folder is empty (no `T-NN.md` packets were generated — `task_compile.py` was not run; see `Research/skills/inventory.md` self-acknowledged "subagents" + the BUILD_REPORT's "Commits: 48 commits" line which suggests the work was committed but the checkbox markers in TASKS.md were not updated).

This is a process-level contradiction: **the work is done (on disk, in commits, in reviews); the bookkeeping is incomplete**. T-41's role is to "Produce BUILD_REPORT and handoff package for committer" — but the BUILD_REPORT was written without first flipping the TASKS.md checkboxes. T-39 is "Update SPEC.md Clarifications section" but is also `[ ]`.

**Fix:** A 5-minute follow-up to flip the `[ ]` to `[x]` in TASKS.md for T-19..T-41, and run `task_compile.py` to generate the `tasks/T-NN.md` packets (or document why they are unnecessary now that the build is done). The work itself does not need redoing.

### C-7 — reviewer ref spec lists `runtimes: []` in frontmatter but the spec describes modes, not runtimes — **LOW**

`reviewer.md:117-118` (catalog body) refers to "the `aspis artifact review --task <T-NN>`" stamping — same tool the reviewer uses. The `runtimes` field is empty (`runtimes: []`) for all 11 catalog files; the FR-011 field list requires it. The T-30 review found this missing in all 11 files; `f574496` added `runtimes: []`; T-30 re-review passed. No contradiction. The interpretation that `runtimes: []` = "applies to all runtimes" is encoded in `src/aspis/catalog.py:96` (`data.get("runtimes", [])` defaults to "all runtimes"). Consistent.

### C-8 — T-38 says FR-007 "is wrong, the SPEC was wrong"; T-39 plan updates the SPEC; the update is in TASKS.md as `[ ]` — **LOW**

The T-39 task was created to capture the SPEC drift. It's still `[ ]`. T-41 is `[ ]`. T-38 verdict approved the build, but the SPEC update the T-38 review itself called out has not landed. See C-6.

### C-9 — reviewer ref spec "6 v1 + 6 v2" plan-critic checks vs. lead spec "12 checks" plan-critic — **LOW (resolved)**

`reviewer.md:229-230` says "v1 vs v2: checks 1–6 are the existing plan-critic (v1); checks 7–12 are the v2 extension being added. '12 checks' = v1 (6) + v2 (6)." This is the T-04 B-2 fix that resolved the earlier contradiction. The original audit (B-2) found the spec mentioned "12 checks" without labelling which were which. Fixed.

### C-10 — `general-builder.md` and `committer.md` use the same identity phrasing pattern, but `general-builder` has no `task:` block AND no `delegates` field AND no `runtimes: []` in the ref spec — **LOW (catalog-only)**

The catalog files are consistent: all leaves have `delegates: []` and `runtimes: []`. The ref specs are inconsistent: committer (229 lines) is thorough; general-builder (296 lines) is thorough; project-explorer (254 lines) is thorough. They cover the same fields. No contradiction; just a cross-check that I verified.

---

## 6 · GAP findings (what is MISSING)

These are not defects — they are deliberate deferrals, mostly. Each is listed for the follow-up trail.

### G-1 — 7 future L3 subagents (`clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer`) — **DEFERRED to F-017**

`planning-lead.md:42-48` (catalog `delegates`) lists them with a comment `# Future L3 subagents (referenced in spec, may not yet exist)`. Each is designed in `planning-lead.md:284-325` (ref spec §7 "New subagents") with tier, tools, input/output, priority, and "extract when". This is a complete specification without a build. F-017 owns the build. Tracked.

### G-2 — 25 missing skills — **DEFERRED (T-31 inventory is the specification; build is a follow-up)**

`Research/skills/inventory.md` lists 25 (13 P0 + 7 P1 + 5 P2) with purpose, owning agent, priority, estimated sections. The SKILL.md files themselves are not authored. Tracked in BUILD_REPORT §"Open Follow-ups" #2.

### G-3 — 6 missing CLI verbs — **DEFERRED (T-36 spec is the specification; build is a follow-up)**

`Research/specs/cli-verbs.md` specifies all 6 with interface, priority, exit codes, callers. The CLI is not built. Tracked in BUILD_REPORT §"Open Follow-ups" #3.

### G-4 — Claude Code adapter fix — **DEFERRED (T-37 spec is the specification; implementation is a follow-up)**

`Research/specs/cross-runtime.md:24-34` specifies the fix and 5 acceptance criteria. The actual adapter code change is not part of F-016. Tracked in BUILD_REPORT §"Open Follow-ups" #4.

### G-5 — modes.yaml does not exist on disk — **DEFERRED (T-33 spec is the specification; YAML authoring is a follow-up)**

The spec (`Research/specs/modes.yaml`) is 79 lines. The actual `.aspis/config/modes.yaml` does not exist (the T-39 plan and the planning-lead ref spec §17 Open Question #2 both note this as a Blocker for full planning; the planning-lead ref spec line 1016 says "modes.yaml | Catalog only (not deployed)" for prereq-validate etc.). The system *runs* without the YAML; planning-lead hardcodes the same 3-mode × 8-knob matrix in its body (planning-lead.md:103-115). F-016 closes the design gap, not the build gap.

### G-6 — 3 planning scripts not deployed — **DEFERRED (T-35 spec; deployment is a follow-up)**

`Research/specs/planning-scripts.md` says scripts "ship into the target project and run on its own Python" (line 16). The deployment from `src/aspis/data/catalog/scripts/planning/` to `.aspis/scripts/planning/` is not done. Tracked in planning-lead ref spec §17 Open Question #1 and §13 Assets table (all three marked "Catalog only (not deployed)").

### G-7 — `bootstrap.md` 12th catalog file incomplete — **DEFERRED**

`src/aspis/data/catalog/agents/bootstrap.md:1-29` lacks `delegates` and `runtimes` fields. This is the 12th file, transient (self-deletes post-onboarding), and T-30/T-38 reviews explicitly exempt it. Tracked as a follow-up in BUILD_REPORT §"Open Follow-ups" #5.

### G-8 — No lab-testing subagents — **DEFERRED to a future feature**

`Research/ref/test-lead.md:240-249` (ref spec §11.3) lists 6 future stack-specific testing subagents (`python-tester`, `api-tester`, `db-tester`, `ui-tester`, `cli-tester`, `security-tester`). The labs-testing fallback (ref spec §11.1) covers the case until these exist. Tracked.

### G-9 — subagent extraction criteria for `runtime-validator`, `drift-auditor`, `permission-auditor`, `export-verifier`, `catalog-synchronizer`, `opencode-author`, `claude-author`, `security-reviewer`, `sub-reviewer`, `dependency-analyzer` — **DEFERRED**

`system-lead.md:317-326` (ref spec §10) lists 7 future system-lead subagents; `reviewer.md:353-357` lists 2; `planning-lead.md:321-325` lists 1. All marked "extract when workload justifies". Tracked.

### G-10 — T-30 said "structural validation" must run a script; the script (`aspis validate-runtime`) does not exist — **DEFERRED**

The T-30 review noted this. The catalog structural check was done manually for F-016 (the SPEC T-30 task itself says: "Manual schema check (or `aspis validate-runtime` if built)"). The CLI verb is spec'd (FR-024) but not built. Same root cause as G-3.

### G-11 — TASKS.md `[ ]` markers for T-19..T-41 — **PROCESS**

Already documented as C-6.

### G-12 — `tasks/T-NN.md` packets not generated — **PROCESS**

The `tasks/` folder contains only `.gitkeep`. The BUILD strategy (TASKS.md:323) says "`task_compile.py` turns each task above into a self-contained packet at `.aspis/features/F-016-agent-system-architecture/tasks/T-NN.md` from `.aspis/templates/TASK_PACKET.md`, so a context-isolated builder can complete it with nothing else." The packets were not generated — but the build is complete (the F-016 build lead was the project's own loop, not an external builder, and the packets would have been self-referential). Documented.

### G-13 — 6 missing templates — **DEFERRED**

`planning-lead.md:998-1011` (ref spec §13) lists 6 missing templates: `CLARIFICATION_LOG.md`, `RESEARCH_REQUEST.md`, `PLAN_OF_PLAN.md`, `DEPENDENCIES.md`, `SCOPE_ESTIMATE.md`, `MODE_DECISION.md`. Marked "Missing" — not built. Tracked as P0/P1/P2 follow-ups.

### G-14 — 5 missing planning scripts — **DEFERRED**

`planning-lead.md:1019-1025` (ref spec §13) lists 5 missing scripts: `scope_estimate.py`, `constitution_check.py`, `plan_quality_check.py`, `mode_validator.py`, `task_size_check.py`. Tracked.

### G-15 — Per-agent "core rules" recital table — **SKIPPED (Group 3, owner-decided)**

Multiple lead specs lack a "Core Rules" recital (audit C-1/C-2/C-3). Owner decision: R-006 says state once, don't duplicate. The skip is sound per `system-rules.md`: "Conformance for its own sake is not a defect to fix."

### G-16 — Section-numbering cosmetics in research-lead — **SKIPPED (Group 3)**

T-03 audit A-3: research-lead has 13 sections, not 14. The "missing" §10 is a numbering artifact, not a content gap. Owner decision: SKIP.

### G-17 — Live runtime (`.opencode/agents/`) not regenerated from catalog — **DEFERRED**

The catalog files were updated (F-016 deliverable), but the live `.opencode/agents/*.md` files are not regenerated. Examples:
- `.opencode/agents/planning-lead.md:31` has `committer: allow` in its task allow-list; the catalog says `committer` is NOT in planning-lead's `delegates` (correct per FR-009, R-004). The drift is the *catalog* fixed it but the *live* still has it. Regeneration via `aspis export` is a follow-up (the CLI verb `export` is not yet built; per FR-024). This is a real system state issue: a planner today, loaded from `.opencode/agents/planning-lead.md`, could still delegate to committer, violating R-004. **The `committer: allow` drift in the live files is the same kind of bug the F-016 spec tries to prevent in the catalog.** T-19..T-29 were "update catalog files" — they were done. The follow-up to regenerate the live files is implied by SC-022 (byte-parity check) but not done.

**This is a non-blocking drift in production behaviour** — the catalog is correct, the live is stale. The drift will resolve when the next regeneration runs. Tracked.

### G-18 — R-007 model resolution lacks a "concrete model id" spec — **DESIGN GAP**

R-007 says "every agent declares an explicit model tier (cheap / standard / deep). No agent silently inherits an expensive model." The catalog frontmatters declare tiers. But there is no F-016 artifact that says "this is how `agent-models.yaml` resolves a tier to a model id per (runtime, agent) pair". The 5-layer precedence lives in `system-lead.md:215-225` (ref spec) but is not formalised as a separate spec. system-lead ref spec Open Question #3 (line 433) tracks the live/catalog tier drift. T-31 skills inventory lists `model-router` as P1. The design is in the ref spec but not the catalog policy. Not a blocker; visible to follow-ups.

---

## 7 · QUALITY findings (what is PRESENT but flawed)

### Q-1 — spec content quality is high; cross-references are well-cited — **POSITIVE**

The 8 lead specs each cite their sources (which old-asps doc, which audit, which research file, which decision). The cross-references form a graph that the reviewer audit and the cross_ref_agents.py script can both walk. This is the kind of citation discipline that holds the design together. No fix needed.

### Q-2 — governance spec is the gold standard — **POSITIVE**

`governance.md` is 634 lines, 7 sections, 17 acceptance criteria. The "Why deterministic, not LLM" table (lines 71-83) makes the design choice with evidence. The 7-step workflow (lines 153-249) is the only place in F-016 where an algorithm is fully specified end-to-end with exact exit codes (lines 536-549). The append-only ledger schema (lines 268-294) is complete with field types and required/optional markers. **This is the artifact to model other specs after.** No fix needed.

### Q-3 — reviewer's "no evidence = no verdict" rule is well-placed — **POSITIVE**

`reviewer.md:174-179` is one paragraph but it carries the load-bearing doctrine. T-38 §"Severity rubric" + "Finding format" (lines 158-196) makes every finding self-describing. No fix needed.

### Q-4 — planning-lead's task packet system is the deepest single design in F-016 — **POSITIVE**

`planning-lead.md:411-815` (ref spec §9) is a 400-line design of packet versions V0-V4 with 12 sub-sections covering dimensions, version selection, dynamic dependencies, per-task acceptance, build/review classification, TASKS.md format, script automation, and cost-aware selection. The plan-compile.py scripts that fill mechanical fields vs. planning-lead that fills content fields is a clean separation. **This is the artifact a future F-017 subagent will model itself after.** No fix needed.

### Q-5 — system-lead's 6-step workflow + 10-step post-change validation is a sound operator protocol — **POSITIVE**

`system-lead.md:177-201` lays out the 6-step workflow and 10-step post-change validation sequence as a deterministic ladder. The 6 of 10 validation gates that are "NOT BUILT" (lines 280-289) are honest. The 5-level config tier model (lines 207-214) is the cleanest way I have seen anyone describe Tier 1/2/3 config policy. **The docs are doing more work than the code in some places** — that is appropriate for F-016 (spec-first). No fix needed.

### Q-6 — Inconsistent section counts between BUILD_REPORT and ref specs — **LOW (Q-1 of section count)**

Already covered in §4. 4 of 12 specs have overstated section counts. Fix: edit BUILD_REPORT.md:18-32 to match the actual spec sections.

### Q-7 — The 3 leaf specs (committer, general-builder, project-explorer) are denser per section than the lead specs — **POSITIVE (with a note)**

6 sections × 200+ lines each is more thorough than 16 sections × 50 lines each would be. The leaf specs earn their lighter structure by going deeper in each section. The 11-leaf-spec discipline is good engineering.

### Q-8 — 13 skills referenced as "missing" in the planning-lead ref spec are not all P0 — **MINOR**

`Research/skills/inventory.md:124-135` correctly notes that the inventory escalates some ref-spec "Medium" priorities to P0 (e.g., `mode-decision`, `constitution-checks`, `recontextualization`, `packet-validation`, `builder-selection`) because they are core-loop blockers even when the ref spec rated them Medium. This is the right call. The note in inventory lines 184-189 is honest about the remapping. No fix.

### Q-9 — `cross_ref_agents.py` is a thin but real gate — **POSITIVE**

T-02 (994d592) added the cross_ref script. It runs in 3 gates (T-05, T-14, T-18, T-40) with `exit 0` on PASS. The script's job is narrow (validate edges) and that is correct. No fix.

### Q-10 — The audit and triage are exemplary — **POSITIVE**

`findings-1.md` (685 lines) and `findings-triage.md` (the Group 1/2/3 disposition) are a textbook adversarial-then-triage-then-fix loop. The T-04 owner triage explicitly distinguished "must-fix" from "defer" from "skip-conformance-only" with rationale. The T-38 review verified each Group-1 fix in the current files. This is what mature engineering looks like. No fix.

### Q-11 — SPEC §"Assumptions" item about the committer in planning-lead's live task list — **STALE**

`SPEC.md:153`: "The `committer` in planning-lead's live task allow-list is a bug, not a design choice — the reference spec says 'remove.'" This was true at the time of SPEC authoring. It is now true that the catalog file (per T-19) has removed committer from planning-lead's `delegates`. The live runtime still has it (G-17). The SPEC text is technically still accurate. The fix is regeneration, not a SPEC update.

### Q-12 — `governance.md` text quality — **POSITIVE (with a small note)**

`governance.md:633-634` cites the source synthesis at the bottom. Lines 71-83 ("Why deterministic, not LLM") and lines 156-249 (R-008 7-step workflow) are dense but well-structured. Line 207-208 (`active_feature.json` is in the protected set) is the right call but means *the governance subagent itself cannot change which feature is active without R-008 approval* — which is exactly the intent.

A small note: the spec is silent on **what happens to in-flight writes during the 3-boundary enforcement**. The runtime boundary (boundary 1) blocks before disk; the pre-commit boundary (boundary 2) blocks at commit time. But the spec doesn't say what happens to a partial write that started before the approval expired. The `applied:` list records what was written; the ledger is append-only; revocations are entries, not deletions. The system handles this correctly by design (the spec just doesn't walk it). Low risk; document the case in a future iteration.

### Q-13 — The T-38 review covers its 9 review dimensions unevenly — **MINOR**

The T-38 review is thorough on architecture, system rules, permission surface, model tier, frontmatter, and cross-agent consistency. It is light on **performance** (a stated 9th dimension): no benchmarks, no latency claims, no token-cost estimate. It is light on **standards** (an 8th dimension): the catalog files are checked for shape, not for content style consistency. It is light on **maintainability** (a 4th dimension): no test coverage for the spec itself, no regression plan if a ref spec is updated.

These are inherent to a spec-only feature (you cannot benchmark a spec, you can only review it). The dimensions are marked "Apply with judgment" per the system rules. Not a defect.

### Q-14 — The "permission surface audit" in T-38 is strong — **POSITIVE**

`REVIEW-F-016-T-38.md:611-631` walks every one of 11 agents' permission surfaces in a single table with `git commit*`, `git push*`, `edit`, `write`, `webfetch`, `websearch`, and R-004 compliance. 11/11 verified. This is the kind of evidence that lets a reader trust the design.

---

## 8 · Missing agents / skills / workflows inventory

### Missing agents (F-016 designs them but does not build them)

| Subagent | Owning lead | Where designed | Why deferred |
|---|---|---|---|
| `governance` | system-lead (R-008 enforcer) | `governance.md` (634 lines) | Built as a deterministic script (per system-lead §13 Q1), not an LLM agent. Implementation is the follow-up. |
| `clarify` | planning-lead | planning-lead.md:286-290 | F-017. |
| `task-decomposer` | planning-lead | planning-lead.md:292-295 | F-017. |
| `idea-capture` | planning-lead | planning-lead.md:297-300 | F-017. |
| `prd-writer` | planning-lead | planning-lead.md:302-305 | F-017. |
| `constitution-checker` | planning-lead | planning-lead.md:307-310 | F-017. |
| `scope-estimator` | planning-lead | planning-lead.md:312-315 | F-017. |
| `research-request-writer` | planning-lead | planning-lead.md:317-320 | F-017. |
| `dependency-analyzer` | planning-lead | planning-lead.md:322-325 | Future (multi-feature planning). |
| `runtime-validator` | system-lead | system-lead.md:320 | Future (when work repeats). |
| `drift-auditor` | system-lead | system-lead.md:321 | Future. |
| `permission-auditor` | system-lead | system-lead.md:322 | Future. |
| `export-verifier` | system-lead | system-lead.md:323 | Future. |
| `catalog-synchronizer` | system-lead | system-lead.md:324 | Future. |
| `opencode-author` | system-lead | system-lead.md:325 | Future. |
| `claude-author` | system-lead | system-lead.md:326 | Future. |
| `security-reviewer` | reviewer | reviewer.md:354-355 | Future. |
| `sub-reviewer` | reviewer | reviewer.md:356-357 | Future. |
| `codebase-explorer` | research-lead | research-lead.md:165-166 | Future. |
| `docs-fetcher` | research-lead | research-lead.md:167-168 | Future. |
| `web-researcher` | research-lead | research-lead.md:169-170 | Future. |
| `cache-manager` | research-lead | research-lead.md:171-172 | Future. |
| `bug-triager`, `gate-fixer` | fix-lead | fix-lead.md:213 | Future. |
| `test-author` | test-lead | test-lead.md:179 | Future. |
| `python-tester`, `api-tester`, `db-tester`, `ui-tester`, `cli-tester`, `security-tester` | test-lead | test-lead.md:240-249 | Future. |

**25 subagents designed; 11 in F-016 scope; 14 deferred to F-017 or later features.** This is the *correct* design choice (per R-003 deterministic-first and the "extract when workload justifies" doctrine). F-016 is the specification, not the build.

### Missing skills (F-016 specifies them but does not author them)

25 skills, all inventoried in `Research/skills/inventory.md`:

- 13 P0: builder-selection, cache-management, catalog-validator, constitution-check, constitution-checks, drift-detector, evidence-validation, governance-approval, harvest-protocol, mode-decision, packet-validation, recontextualization, security-review
- 7 P1: byte-parity-checker, export-manager, finding-format, model-router, runtime-author, scope-compliance, session-continuation
- 5 P2: commit-readiness, dependency-audit, hook-author, model-inventory, profile-manager

Building the SKILL.md files is a follow-up feature.

### Missing workflows (referenced in agent specs but not authored)

| Workflow | Where referenced | Status |
|---|---|---|
| `project-lead-operating-protocol.md` | project-lead.md:789-790 | Not authored; spec'd in inventory. |
| `STATUS_REPORT.md` (template) | project-lead.md:782 | Not authored. |
| `DELEGATION_PACKET.md` (template) | project-lead.md:783 | Not authored. |
| `REPLY_TO_USER.md` (template) | project-lead.md:784 | Not authored. |
| `ESCALATION_NOTE.md` (template) | project-lead.md:785 | Not authored. |
| `FIX_REPORT.md` (template) | fix-lead.md:142-158 | Schema specified; no template. |
| `CLARIFICATION_LOG.md` (template) | planning-lead.md:1006 | Not authored. |
| `RESEARCH_REQUEST.md` (template) | planning-lead.md:1007 | Not authored. |
| `PLAN_OF_PLAN.md` (template) | planning-lead.md:1008 | Not authored. |
| `DEPENDENCIES.md` (template) | planning-lead.md:1009 | Not authored. |
| `SCOPE_ESTIMATE.md` (template) | planning-lead.md:1010 | Not authored. |
| `MODE_DECISION.md` (template) | planning-lead.md:1011 | Not authored. |
| `plan.md` workflow expansion | planning-lead.md:1031 | Planned (52 → 120 lines). |
| `test.md` workflow | test-lead.md:178 | Not authored. |
| 6 CLI verbs (validate-runtime, validate-index, byte-parity, drift, export, governance) | cli-verbs.md | Not built. |
| 5 planning scripts (scope_estimate, constitution_check, plan_quality_check, mode_validator, task_size_check) | planning-lead.md:1019-1025 | Not built. |
| 3 planning scripts (feature_scaffold, task_compile, prereq_validate) | planning-scripts.md | Not deployed. |

**17 missing templates/scripts/workflows. All spec'd; none built.** This is the right shape for F-016 (spec-first). The follow-up features are well-defined.

### Skills the system NEEDS that no spec names

A scan for "things the agent specs say agents do, that no skill enables" finds these **functional gaps** (not missing skills, but missing skill coverage):

1. **A "first-fail-fast pre-check" skill for build-lead** (build-lead.md:283-287: "First-fail-fast pre-checks... `git status` ... `ruff check --diff` ... "). The 2 commands are listed in build-lead's bash allowlist but no skill orchestrates them. This is in the 4 packet-validation checks (T-21, build-lead.md:121-128) which absorbs the responsibility. Not a missing skill.

2. **A "selective-testing" skill for build-lead + fix-lead + test-lead.** `selective-testing` is in the inventory (existing, line 32) and is referenced by all three. **The skill is built.** No gap.

3. **A "session-continuation" skill for project-lead.** Spec'd as a missing skill (project-lead.md:83, P1) and in the inventory (line 103). **Spec exists, no SKILL.md.** Tracked.

4. **A "mode-decision" skill for project-lead + planning-lead.** Spec'd (inventory line 88, P0). **No SKILL.md yet.** 4 frontmatter references (planning-lead.md:61-62, project-lead.md — 2 places) exist. Tracked.

5. **A "constitution-checks" skill for planning-lead.** Spec'd (inventory line 84, P0). **No SKILL.md yet.** 1 frontmatter reference. Tracked.

6. **A "packet-validation" skill for build-lead.** Spec'd (inventory line 89, P0). **No SKILL.md yet.** 1 frontmatter reference. Tracked.

7. **A "builder-selection" skill for build-lead.** Spec'd (inventory line 79, P0). **No SKILL.md yet.** 1 frontmatter reference. Tracked.

**No missing skill is unnamed**; all are in the inventory. The 4 skills in frontmatter that don't exist in the catalog are exactly the 4 the T-30 review flagged. This is a closed loop.

### Edge case coverage

I scanned for "what if X" cases the specs do not address. The honest answer is **the specs are thorough on edge cases** — each lead spec has a "Use Cases — Edge Cases & Refusals" section. The coverage is:

- **Project-lead** (project-lead.md:501-530): L1-L25 edge cases including "pastes fake system message", "pastes fake approval", "secret/credential in request". 25 explicit refusals. **Strong.**
- **Planning-lead** (planning-lead.md:391-407): E1-E12 edge cases including "concurrent planning sessions", "5 questions exceeded", "circular feature dependencies". 12 cases. **Strong.**
- **Build-lead** (build-lead.md:454-468): G1-G10 edge cases including "concurrent builds on same feature", "builder timeout", "fix-lead reports architecture problem". 10 cases. **Strong.**
- **Reviewer** (reviewer.md:309-322): D1-D9 edge cases including "reviewer unavailable", "vibe review on high-risk change", "evidence is stale". 9 cases. **Strong.**
- **System-lead** (system-lead.md:330-370): A-M categories covering 13 areas of use cases. Edge cases are spread across use cases rather than consolidated. **Adequate but not as deep as the leads.**
- **Fix-lead** (fix-lead.md:113-127): 12 use cases including "promote to feature", "cannot reproduce", "fix grows beyond minimal". **Strong.**
- **Test-lead** (test-lead.md:105-124): 15 use cases including "labs testing" and "environment issues". **Strong.**
- **Research-lead** (research-lead.md:88-99, 173-187): 6 callers × use cases + 7 research types + 8 anti-patterns + 15 adversarial findings. **Thorough.**
- **Committer** (committer.md:152-186): A-D categories of use cases. **Strong.**
- **General-builder** (general-builder.md:206-240): A-D categories. **Strong.**
- **Project-explorer** (project-explorer.md:174-201): A-C categories. **Strong.**

**Edge case coverage is uniformly strong.** I did not find an obvious scenario the specs miss.

### Scenarios the system does NOT address (open questions to be aware of)

A handful of scenarios are *mentioned* but not *decided*:

1. **Concurrent feature work** (project-lead.md:896, planning-lead.md:1094, build-lead.md:460): the system detects but does not handle concurrent work on the same feature. The design is to "serialize" by default. Not a gap; an explicit design choice.

2. **Multi-agent work on different features in parallel** (project-lead.md:495 K6): "Multi-feature coordination — Split and route in dependency order". But the design has no fan-out primitive (build-lead.md:585: "No parallel fan-out primitive"). **This is a roadmap gap, not an F-016 gap.** Phase 3+.

3. **A subagent that needs to modify a protected path** (governance.md:101-108): the only path is R-008 approval + governance subagent. If a subagent needs to modify a rule during a feature, the only path is to stop, ask for approval, and then route through governance. The `committer: allow` drift in live planning-lead.md (G-17) is the kind of bug this would prevent.

4. **What if `modes.yaml` disagrees with the planning-lead's hardcoded mode table?** (planning-lead.md:152-160 + Research/specs/modes.yaml:58-67): planning-lead has a hardcoded mode table. `modes.yaml` is a separate file. If they diverge, the planning-lead body wins. There is no spec for which wins. **Design gap.** Tracked as T-33's open question (the modes.yaml spec is on disk, the YAML is not).

5. **What if the catalog has an agent the runtime doesn't know about?** (system-lead.md:347, system-lead-pentest.md:889): the protection engine's `UNKNOWN` decision. There is no spec for what happens if a new agent is added to the catalog but the runtime doesn't render it. **Edge case not addressed in cross-runtime.md.** Low severity — would manifest as a missing agent in the live runtime, not a wrong agent.

6. **What if a project uses a profile that overrides agent frontmatter?** (system-lead.md:213-214 "Tier 1 user-editable"): "agent-models.yaml" is Tier 1; the project can override model tiers. The spec does not say what happens if the project changes a tier to a value that violates R-007. **Edge case not addressed.** Low.

These are not gaps in F-016; they are gaps in the design that F-016 surfaces for future work. Tracked.

---

## 9 · Task packet completeness (V0-V4)

The TASKS.md footer says "`task_compile.py` turns each task above into a self-contained packet at `.aspis/features/F-016-agent-system-architecture/tasks/T-NN.md` from `.aspis/templates/TASK_PACKET.md`." The packet system design lives in `planning-lead.md:411-815` (V0-V4, 12 sub-sections).

**The 4 packet versions are:**

| Version | Builder tier | Review tier | Sections | Use case |
|---|---|---|---|---|
| **V0** | cheap | self | 0 (inline) | Trivial, 1 file, 1 change, P2, low risk |
| **V1** | cheap | self / build-lead | ~5 | Simple, P1/P2, low risk |
| **V2** | standard | build-lead / reviewer | ~12 | Standard feature work (the default) |
| **V3** | deep | reviewer (full dimensions) | ~18 | High-risk, P0/P1, security |
| **V4** | deep | reviewer (full + research audit) | ~22 | Novel, P0, greenfield |

**Coverage check vs. the 5 task dimensions in the F-016 TASKS.md:**
- **Criticality (P0/P1/P2)**: ✓ every task in TASKS.md is tagged `[P0]`/`[P1]`/`[P2]`.
- **Risk**: ✗ NOT tagged in F-016 TASKS.md. (planning-lead.md:438 says "Risk: high/medium/low based on file count, nature, blast radius" but TASKS.md entries don't include it.) **Gap.**
- **Complexity (simple/moderate/complex)**: ✓ every task is tagged `[simple]`/`[moderate]`/`[complex]`.
- **Nature (feature/fix/refactor/config/docs/test/security)**: ✗ NOT tagged. (planning-lead.md:438 mentions it as a field; TASKS.md does not include it in task lines.) **Gap.**
- **Scope (isolated/dependent/blocking)**: ✗ NOT tagged. **Gap.**

**The TASKS.md is using only 2 of 5 task dimensions** (criticality and complexity). The matrix in planning-lead.md:619-628 implies that the 3 missing dimensions (risk, nature, scope) are how `task_compile.py` auto-selects the packet version. Without them, the auto-selection cannot run.

For F-016, the tasks are documentation work — risk/nature/scope are mostly implicit. The gap is not blocking F-016 (the build-lead is the project's own loop, not an external context-isolated builder). **It is a gap for F-017 and beyond**, when the spec'd auto-selection needs to run.

The V0-V4 packet templates themselves (the markdown shapes) are fully spec'd in `planning-lead.md:436-612`. The script that fills them is spec'd in §9.10. The auto-selection matrix is spec'd in §9.3. The cost-aware override is spec'd in §9.11. **The packet system is fully designed; the TASKS.md entries don't carry the metadata to drive it.** Documented.

### Task packet coverage by scenario

I walked the F-016 scenarios through the V0-V4 matrix:

- **T-01 research verification** → V1 (P1, simple, docs) — appropriate
- **T-02 cross_ref_agents.py** → V2 (medium complexity, code) — appropriate
- **T-03 adversarial audit** → V4 (high stakes, novel methodology) — over-spec'd; V3 would be enough
- **T-04 apply Group-1 fixes** → V3 (high stakes, ~10 files, multi-spec) — appropriate
- **T-05 cross-ref gate** → V1 (simple, deterministic script) — appropriate
- **T-06..T-13 lock lead specs** → V1 (simple, docs) — appropriate
- **T-14 cross-ref all 11** → V1 — appropriate
- **T-15..T-17 leaf specs** → V2 (medium, 6-section spec) — appropriate
- **T-18 cross-ref leaves** → V1 — appropriate
- **T-19..T-29 catalog updates** → V2 (medium, frontmatter + body edits) — appropriate
- **T-30 catalog validation** → V3 (high stakes, gates SC-003) — appropriate
- **T-31 skills inventory** → V2 (medium, docs) — appropriate
- **T-32 governance spec** → V3 (high stakes, R-008) — appropriate
- **T-33 modes.yaml spec** → V2 — appropriate
- **T-34 enforcement spec** → V2 (security but spec-only) — borderline V3
- **T-35 planning scripts spec** → V2 — appropriate
- **T-36 CLI verbs spec** → V2 — appropriate
- **T-37 cross-runtime spec** → V2 (medium) — appropriate
- **T-38 final acceptance review** → V3 (high stakes, final) — appropriate
- **T-39 SPEC clarifications** → V0 (trivial, 1 file, docs) — appropriate
- **T-40 final cross-ref** → V1 — appropriate
- **T-41 BUILD_REPORT** → V1 — appropriate

**Every task in F-016 maps cleanly to V0-V4.** The matrix is sound.

---

## 10 · Catalog frontmatter completeness

I verified the 11 in-scope catalog files for the 11 fields required by FR-011 and the T-30 gate.

| Field | project-lead | planning-lead | build-lead | reviewer | system-lead | fix-lead | test-lead | research-lead | committer | general-builder | project-explorer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `description` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `mode` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `model` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `temperature` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tools` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `permissions` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `delegates` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `skills` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `runtimes` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `export_scope` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**11/11 × 11/11.** PASS.

### Field-level anomalies (informational, not blocking)

- **mode values**: `primary` for project-lead + build-lead; `subagent` for the other 9. The SPEC says "Every catalog agent frontmatter MUST include ... mode". The mode *value* is a design choice. **8 of 11 are `subagent`** even though 5 of those 8 are leads (planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead). The `mode: subagent` is a binary "this is not the L1 entry point" marker, not a hierarchy. The T-30 review did not flag this. The build_notes imply it is intentional. Documented, not a defect.

- **model values**: `standard` for 8 leads; `cheap` for 3 leaves (committer, general-builder, project-explorer). Per R-007 + the spec'd tier strategy.

- **tools lists**: all 11 declare read/grep/glob; 8 declare bash; 5 declare edit (build-lead, fix-lead, test-lead, research-lead, general-builder); 4 declare write (build-lead, fix-lead, test-lead, general-builder); 2 declare webfetch (system-lead, research-lead); 1 declares websearch (research-lead). R-001 / R-004 / R-007 invariants hold.

- **delegates lists**: 38 edges resolve; 7 are F-017-deferred. Comms resolved.

- **export_scope**: 10 of 11 are `full`; 1 (`bootstrap.md`) is `export-only`. Consistent with the F-016 design (bootstrap is transient).

---

## 11 · Acceptance criteria — every task verifiable

The 41 TASKS.md tasks each have an "Acceptance" line (some explicit, some implicit). I checked each:

- **T-01..T-05**: Acceptance via "cross_ref_agents.py exit 0", file counts, audit findings count. ✓
- **T-06..T-13**: Acceptance via "All [N] sections present", "Identity block matches master synthesis", "Acceptance criteria checkboxes verified". ✓ (templated)
- **T-14**: Gate via "cross_ref_agents.py --scope all exit 0", "All [NEEDS CLARIFICATION] resolved". ✓
- **T-15..T-17**: "6 sections" checklist. ✓
- **T-18**: Gate via "No overlapping responsibilities", "All delegation edges valid", "Committer is the only agent with git commit* allowed". ✓
- **T-19..T-29**: Per-task checklist (frontmatter fields, body changes, derived header). ✓
- **T-30**: Gate via "aspis validate-runtime (or manual schema check)". ✓ (manual done)
- **T-31**: "Consolidated inventory ... per entry: skill name, purpose, owning agent, priority, estimated sections. Sorted by priority." ✓
- **T-32**: "Must define: protected paths list, R-008 human-approval workflow, approval ledger format, intervention handler". ✓
- **T-33**: "Every knob defined with per-mode values: spec, architecture, task_size, plan_review, build_review, test_depth, docs, promotable". ✓
- **T-34**: "Spec defining enforcement boundaries: block for runtime tools (Edit/Write), warn for pre-commit hooks. CI override via ASPIS_ENFORCEMENT=block. Auto-fix behavior per mode. Transition plan." ✓
- **T-35**: "Each entry: catalog source path, destination path, trigger, validation". ✓
- **T-36**: "Each entry: purpose, priority, interface signature, expected output". ✓
- **T-37**: "Byte-parity check, Claude Code adapter fix, CONFLICT/PROTECT decision model". ✓
- **T-38**: "0 CRITICAL, 0 HIGH unresolved findings. All SC-001 through SC-012 verified with evidence." ✓
- **T-39**: "Update SPEC.md Clarifications section with any decisions made during build". ✓ (templated)
- **T-40**: "cross_ref_agents.py --scope all --include-systemic exit 0. All SC-### verified." ✓
- **T-41**: "Summarize all artifacts produced, gate results, reviewer verdicts, and open follow-ups." ✓

**41/41 tasks have verifiable acceptance criteria.** PASS.

---

## 12 · Labs testing adequacy (`test-lead.md` §11)

The test-lead ref spec §11 (lines 184-260) defines "Labs Testing — Universal Fallback for Any Stack". I evaluated its adequacy against the 5 stacks the spec names + 3 it does not name.

**Stacks the spec addresses:**

| Stack | Subagent | Skills | Status | Coverage |
|---|---|---|---|---|
| **Python** | `python-tester` (future) | `pytest-patterns`, `coverage-analysis`, `property-testing` | Future | §11.3 names them. The current `test-lead` agent uses `pytest` and `uv run pytest` per its bash allowlist. |
| **REST API** | `api-tester` (future) | `http-assertions`, `schema-validation`, `contract-testing` | Future | §11.3 names them. The current `test-lead` falls back to labs testing for any non-Python stack. |
| **Database** | `db-tester` (future) | `migration-testing`, `data-integrity`, `query-performance` | Future | §11.3 names them. |
| **Frontend/UI** | `ui-tester` (future) | `component-testing`, `accessibility`, `screenshot-diff` | Future | §11.3 names them. |
| **CLI** | `cli-tester` (future) | `arg-parse-testing`, `exit-code-assertions`, `pipe-testing` | Future | §11.3 names them. |
| **Security** | `security-tester` (future, via reviewer) | `owasp-scan`, `fuzz-testing`, `secret-scan` | Future | §11.3 names them. |

**Stacks the spec does NOT address:**

| Stack | Coverage | Note |
|---|---|---|
| **Shell / bash** | Via `pytest` (with `subprocess` tests) and labs | Implied; not named. |
| **Rust / Go / C++** | Labs only | Not named. Falls into "any stack". |
| **Terraform / IaC** | Labs only | Not named. |
| **Data science (Jupyter, R, notebooks)** | Labs only | The `lab_notebook.md` example (test-lead.md:231) hints at this but the spec is light. |
| **Mobile (iOS, Android)** | Labs only | Not named. |
| **WebAssembly** | Labs only | Not named. |

**Adequacy verdict:** The §11 design is **philosophically complete** (the labs-testing fallback is universal and works for any stack) but **practically thin** for the 6 future subagent/skill pairs listed. None of the 21 future skills (per §11.3) are built; the spec acknowledges this. The labs-testing discipline is the *interim* answer; the future subagent/skill pairs are the *long-term* answer.

For ASPIS itself (which is Python), the current `test-lead` is adequate. For a non-Python project, labs testing is the documented fallback. **The design is sound; the build is not done.**

### Labs testing specific gaps

1. **No "how to write a lab test" skill.** The spec describes the procedure (§11.1) but does not name a skill that owns the procedure. The "Labs Testing" content is in the test-lead agent body, not in a `labs-testing` skill. A reviewer or future agent cannot find it by skill lookup.

2. **No labs test template** (e.g., `tests/labs/TEMPLATE.md` or `tests/labs/TEMPLATE.py`). The spec lists examples (`test_api_endpoints.py`, `test_db_queries.sql`, `test_config_validation.sh`, `lab_notebook.md`) but no template. Documented.

3. **No confidence-rubric table.** The spec says "labs-tested (no specialized test framework for this stack yet — evidence from manual script execution)" is "valid evidence" with "lower confidence". But there is no rubric for *how much* lower. Reviewer must judge. Documented.

4. **No "extract a subagent from a lab test" procedure.** The spec says (§11.4): "If labs testing reveals a pattern that repeats, propose a new specialized subagent/skill." But there is no step-by-step procedure for this extraction. The reviewer would be guessing. Documented.

**Adequacy: ADEQUATE for documentation, ADEQUATE for fallback use, NOT built for the 6 specialized subagent/skill pairs.** Same shape as the rest of F-016 — spec'd, not built.

---

## 13 · Cross-spec contradiction matrix

| A says | B says | Verdict |
|---|---|---|
| FR-007: websearch allowed for system-lead and research-lead | system-lead.md:134 says `websearch: allow`; system-lead.md:432 says reconcile (deny); catalog says `websearch: deny` | **3-way disagreement** — see C-1, C-2. T-39 fix. |
| planning-lead.md:42-48 (catalog) lists 7 F-017 subagents in `delegates` | planning-lead.md:170-175 (ref spec Skills NOT in set) doesn't list them | Consistent — the comment marks them as future, and the ref spec lists them as future-design-only. |
| governance.md:207 says ledger lives at `.aspis/state/approval-ledger.yaml` | governance.md:261-266 says ".aspis/config/approval-ledger.yaml ... may move only via an R-008-governed change" | Internal contradiction within governance.md (alternate location considered; state/ preferred). The doc resolves in §4: "The `state/` location is preferred ... The location is fixed today and may move only via an R-008-governed change." The alternate is presented as a "considered" option. **Low severity** — the doc resolves itself. |
| T-38 says "Project-lead's `websearch` is denied" | FR-007 says "websearch allowed for system-lead AND research-lead" | FR-007 implies project-lead can websearch; project-lead.md:147 says `websearch: deny`. The denial is correct (project-lead is not the research layer). The SPEC text overstates. T-39 fix. |
| T-30 review says 7 future subagents are owner-decided exemption | T-18 cross-ref gate says "every delegate exists" | Gate allows the exemption via the catalog file annotation. T-30's review notes the medium finding (T-30 REVIEW.md:38) and resolves it. |
| BUILD_REPORT says 41/41 complete | TASKS.md has 22 tasks as `[ ]` | C-6. Bookkeeping drift, not work drift. |
| BUILD_REPORT.md:18-32 section counts (16, 16, 16, 16, 16, 16, 12, 14, 6, 6, 6, 7) | Actual section counts (16, 17/18, 16, 13, 14, 12, 12, 13, 6, 6, 6, 7) | 4 specs overstate. Q-1. |

---

## 14 · Scope creep check

Items in F-016 that *might* belong in a future feature:

1. **The 7 future L3 subagents** in planning-lead's `delegates` and ref spec §7 — these are correctly marked as F-017-deferred. ✓ no scope creep.
2. **The 25 missing skills** — correctly marked as build follow-up. ✓ no scope creep.
3. **The 6 missing CLI verbs** — correctly marked as build follow-up. ✓ no scope creep.
4. **The 6 missing future testing subagents** — correctly marked as future. ✓ no scope creep.
5. **Trace spine** — system-lead ref spec §13 Q12 marks it as Phase 3, designed not built. ✓ no scope creep.
6. **Dashboard** — system-lead ref spec §13 Q13 marks it as Phase 5, designed not built. ✓ no scope creep.
7. **Self-improvement loop** — system-lead ref spec §13 Q14 marks it as Phase 4, designed not built. ✓ no scope creep.
8. **MCP plugin system** — SPEC §"Out of scope" line 29. ✓ no scope creep.
9. **Multi-profile support beyond base.yaml** — SPEC §"Out of scope" line 28. ✓ no scope creep.
10. **The Claude Code adapter fix** — correctly marked as implementation follow-up. ✓ no scope creep.
11. **The modes.yaml actual file** — correctly marked as authoring follow-up. ✓ no scope creep.

**No scope creep.** Every out-of-scope item is marked.

One borderline: **`governance.md`** (634 lines) is a full spec for a feature that the SPEC says is a "follow-up" (FR-018 specifies it; implementation is a follow-up). It is the most thorough spec in F-016. **It is not scope creep** — the SPEC explicitly requires it. But it is *more* than the minimum the SPEC requires. Defensible: governance is R-008, the human-gate rule, the load-bearing safety floor. Going deep on it is appropriate.

---

## 15 · Testing gaps

**What cannot be tested with the current `test-lead` design:**

1. **The specs themselves cannot be tested.** They are markdown. The "tests" are reviewer audits (T-03 + T-38). F-016 is essentially a "tested by review" feature; there are no automated tests for the spec content.

2. **The cross-ref script does not test the bodies of the specs** — it tests the frontmatter edges (delegates resolve, skills exist, model tier declared). It does not test whether the body of a spec is consistent with its frontmatter. A spec can declare a `Mode Tier: deep` in its body but a `model: cheap` in its frontmatter; the script will not catch this. (T-38 caught one such case manually — fix-lead's body says "deep tier" in some places, "standard" in others — but the script doesn't catch it.)

3. **The governance spec cannot be tested without the governance CLI.** The spec defines an `aspis governance` interface; the CLI is not built. The only way to "test" the spec is to read it.

4. **The modes.yaml spec cannot be tested without the YAML file.** The spec defines 24 values; the YAML does not exist. The plan `modes.yaml` exists; the data `modes.yaml` does not.

5. **The byte-parity check cannot be tested without the export CLI.** The spec defines `aspis byte-parity`; the CLI is not built. The `cross-runtime.md` test procedure (lines 51-55) is untestable today.

6. **The enforcement mode cannot be tested without the runtime tool boundary.** The spec defines `block` for Edit/Write; the runtime tool boundary is not the focus of F-016. Documented as Phase 2 (F-016 follow-up).

7. **The live runtime (`.opencode/agents/*.md`) cannot be tested against the catalog** until `aspis export` is built. (G-17.)

**Testing is built on review, not on automated checks.** This is the right shape for a specification feature. The follow-up features (F-017 subagents, skills build, CLI verbs) will add the automated checks.

**One specific concern:** the `cross_ref_agents.py` script's design is thin enough that **a spec that is structurally broken but field-correct will pass it.** Example: a ref spec could be 50 lines of "TBD" and still pass — the script checks the frontmatter and the delegation edges, not the body. The reviewer (T-03 + T-38) is the body-content gate. The script is a necessary but not sufficient gate. Documented.

---

## 16 · Documentation quality

### Strengths

- **Citation discipline**: every spec cites its sources. The T-38 review verified these.
- **Layered structure**: Identity → Responsibilities → Model Tier → Permission → Delegation → Use Cases → ... is consistent across all 8 lead specs.
- **Acceptance criteria as checkboxes**: every spec ends with a checkbox list. Verifiable.
- **Cross-reference depth**: SPEC cites PLAN cites TASKS cites audit cites ref specs. The graph is walkable.
- **Build notes section in TASKS.md** (lines 7-25): explicitly captures the owner-decided trade-offs. T-38 calls this out as exemplary.
- **SC tables in BUILD_REPORT**: each SC has status, evidence, and verifier. Verifiable.

### Weaknesses

- **Section counts in BUILD_REPORT are wrong** for 4 of 12 specs (Q-1).
- **TASKS.md checkbox markers not updated** for T-19..T-41 (C-6).
- **`tasks/T-NN.md` packets not generated** (G-12). The `task_compile.py` workflow was not run.
- **FR-007 wording drift** (C-1) — the SPEC text and the design disagree.
- **The system-lead reference spec is internally inconsistent** on `websearch` (C-2).
- **Inconsistent use of "R-008"**: some specs cite it as "human gate", some as "human approval", some as "human-gated push". The 4 phrasings are equivalent but the inconsistency is visible.
- **No "decision log" in the F-016 artifacts**. The T-04 triage and T-39 clarifications capture the decisions, but a single "F-016 Decisions" doc would make the trail cleaner. T-39 is the closest analogue.
- **T-30 review file (`REVIEW-F-016-T-30.md`) and T-30 re-review file (`reviews/T-30-review.md`)** are in different directories (`build-reports/` vs `reviews/`). The naming and location are inconsistent.

### Terminology consistency

I scanned for terminology drift:

- "agent" / "lead" / "subagent" — used correctly. "Lead" = L1 or L2; "subagent" = L2 support or L3; "agent" = generic. ✓
- "primary" / "support" / "lead" — "primary" is the mode (catalog frontmatter). "Lead" is a role. Different concepts. ✓
- "R-007" / "pinned models" / "model tier strategy" — used interchangeably. Same concept. ✓
- "R-008" / "human gate" / "human approval" / "human-gated push" — same concept, different phrasings. **Minor inconsistency.**
- "byte-parity" / "byte-identical" / "byte-for-byte" — same concept. ✓
- "R-004 one-writer" / "single git writer" / "one-writer invariant" — same concept. ✓
- "Tier 1/2/3 config" / "tier 1/2/3" / "user-editable/policy-locked/reference" — same concept, mixed in same file. ✓
- "skill allowlist" / "skill scope" / "skill surface" — same concept. ✓

**Terminology is mostly consistent. The R-008 phrasing drift is minor.**

---

## 17 · Architecture constitution compliance (12 rules)

| Rule | Status | Evidence |
|---|---|---|
| **C-COST** cost of change ≤10 | ✓ | SC-012 verified; 2-5 files to add a new agent |
| **C-AUTOMATION** R-003 deterministic-first | ✓ | governance is a script; cross-ref is a script; planning scripts are stdlib-only |
| **C-LOCAL-CHANGE** new files, not edits | ✓ | F-016 added 18 new spec files; edited 11 catalog files (focused) |
| **C-PLUGIN-FIRST** core never names concrete | ✓ | No core engine change; runtime discovered by adapter; agents by profile |
| **C-SINGLE-SOURCE** every fact one owner | ✓ | Reference spec → catalog → runtime; cites by ID, not duplication |
| **C-CONFIG-OVER-CODE** data, not branches | ✓ | modes.yaml is data; enforcement modes are data; tiers are data |
| **C-NO-SPECIAL-CASE** no `if runtime ==` | ✓ | System-lead bash allowlist is named; no `if agent ==` introduced |
| **C-DISCOVERY** load by convention | ✓ | Skills by directory listing; agents by file presence |
| **C-FILE-SELF-EXPLAINS** Purpose/Does Not/Used By | ✓ | Each agent file has identity, IS/IS NOT, what it does/doesn't |
| **C-TESTABLE** every component testable | ✓ | Each spec has acceptance criteria; each SC has a verification method |
| **C-PORTABLE** Windows + Linux | ✓ | Planning scripts stdlib-only; bash allowlists have python + python3 forms |
| **C-ARCH-BEFORE-FEATURES** build the extension first | ✓ | F-016 *is* the extension mechanism (catalog + asset kinds) |

**12/12.** T-38 §"Architecture constitution compliance" verified the same.

---

## 18 · System rules compliance (R-001 through R-010)

| Rule | Status | Evidence |
|---|---|---|
| **R-001 Scope** | ✓ | F-016 stays in `.aspis/features/F-016-agent-system-architecture/` and `src/aspis/data/catalog/agents/` |
| **R-002 Gates first** | ✓ | T-05, T-14, T-18, T-30, T-40 — all deterministic gates |
| **R-003 Deterministic-first** | ✓ | governance is a script; cross-ref is a script; planning scripts are scripts; byte-parity is a CLI verb |
| **R-004 One writer** | ✓ | committer only `git commit*` allow (T-38 verified); reviewer read-only |
| **R-005 Tests-as-spec** | ✓ | Every spec has measurable acceptance; SC-001..SC-012 are the spec tests |
| **R-006 Thin agents, single source** | ✓ | Each spec is 200-1100 lines; intelligence in skills |
| **R-007 Pinned models** | ✓ | All 11 declare a tier (8 standard, 3 cheap) |
| **R-008 Human gate** | ✓ | governance subagent is the mechanism; spec'd in governance.md |
| **R-009 Trace and learn** | ✓ | Every spec has Open Design Questions; audit is the trace; triage is the lesson |
| **R-010 Delegate with purpose** | ✓ | All leads have explicit `delegates`; general-builder is the L3 disposable; project-explorer is the L1↔L3 exception |

**10/10.**

---

## 19 · Recommendations (before merge)

The 4 issues that should be addressed before merging `feature/F-016-agent-system-architecture` to main. None are blockers; all are 5-30 minutes of work.

### R-1 (5 min) — Update TASKS.md checkboxes and section counts in BUILD_REPORT

- **TASKS.md**: Flip T-19..T-41 from `[ ]` to `[x]`. The work is done (T-38 PASS); the bookkeeping is incomplete.
- **BUILD_REPORT.md lines 18-32**: Update section counts for reviewer (13), system-lead (14), fix-lead (12), research-lead (13) to match the actual specs.
- **Severity**: low (process accuracy)
- **Effort**: 5 minutes

### R-2 (15 min) — Reconcile FR-007 and the system-lead `websearch` drift

- **SPEC.md FR-007**: Update to "webfetch/websearch denied by default; webfetch and websearch allowed only for research-lead". Remove the "and system-lead" exception.
- **system-lead ref spec §5 (line 134)**: Change `websearch` from `allow` to `deny` with the rationale "research-lead is the only subagent with web access; system-lead is local-only and deterministic". The rationale already exists in §13 (line 432).
- **system-lead catalog frontmatter (system-lead.md:32)**: Already `websearch: deny` — no change.
- **system-lead ref spec §13 (line 432)**: Update the open question to "Resolved: deny" once the §5 update lands.
- **T-39** is the natural owner of this fix.
- **Severity**: medium (text drift that, if left, will be a bug for the next reader)
- **Effort**: 15 minutes

### R-3 (15 min) — Document the live/catalog regeneration gap

- **Add to BUILD_REPORT §"Open Follow-ups"**: The catalog is updated (F-016 done); the live `.opencode/agents/*.md` is not regenerated (G-17). Specific drift: `committer: allow` is still in `.opencode/agents/planning-lead.md:31` and `.opencode/agents/project-lead.md:34` even though the catalog has removed `committer` from both `delegates` lists.
- **Track in a follow-up**: "Regenerate `.opencode/agents/` from catalog after `aspis export` is built".
- **Severity**: medium (real production drift; the system would have a planner today who could delegate to committer, violating R-004)
- **Effort**: 15 minutes (doc only; the actual regeneration requires `aspis export`, a follow-up CLI verb)

### R-4 (30 min) — Reconcile the small terminology drifts in the F-016 artifacts

- Standardize the R-008 phrasing across all specs: pick one (recommend "R-008 human gate") and use it consistently.
- Standardize "byte-parity" / "byte-identical" / "byte-for-byte" — pick one (recommend "byte-parity" for the verb, "byte-identical" for the state).
- Move both T-30 review files to one directory (either `build-reports/` for both or `reviews/` for both).
- **Severity**: low (style consistency)
- **Effort**: 30 minutes

### Total follow-up effort: ~1 hour

After R-1..R-4, F-016 is ready to merge.

---

## 20 · Final verdict

**APPROVE WITH CONDITIONS**

F-016 delivers what the SPEC requires: a complete, well-cited, adversarially-audited set of 12 reference specifications, 5 systemic specifications, 1 skills inventory, and 11 catalog files. The governance subagent spec is exemplary. The 12 SCs are met (with 3 PARTIALs that are honest about the documented deferrals). The 28 FRs are met (with 5 PARTIALs that are the same documented deferrals and 1 NOT MET that is text drift, not system defect).

The T-38 reviewer verdict (APPROVED with notes; 0 CRITICAL, 0 HIGH; 3 MEDIUM, 4 LOW) is sound. The 3 MEDIUMs in the T-38 review map to my findings: SPEC drift (C-1, C-2, C-8, R-2), the planning-lead future subagents (C of FR-004 / G-1), and the skills-not-yet-built (G-2). The 4 LOWs map to: 4 skills missing in catalog (G-2 follow-up), bootstrap.md missing fields (G-7), research-lead section numbering (Q-3 / C-3), and the "core rules" recital (G-15). I do not disagree with the T-38 verdict; I add a few more LOWs and one extra MEDIUM (the live/catalog regeneration gap, G-17, R-3).

**Conditions (must be addressed before merge):**

1. Update TASKS.md checkboxes and BUILD_REPORT section counts (R-1).
2. Reconcile FR-007 and the system-lead `websearch` drift (R-2).
3. Document the live/catalog regeneration gap (R-3).
4. Reconcile small terminology drifts (R-4).

**After R-1..R-4 land, F-016 is ready to merge to main.**

The follow-up features (F-017 subagent roster, skills build, CLI verbs build, Claude adapter fix, modes.yaml file, planning scripts deployment) are well-defined and tracked. F-016 is a clean spec-first foundation.

---

*Reviewer: F-016 deep completeness + quality pass, 2026-06-27. Scope: 28 FRs, 12 SCs, 12 ref specs, 5 systemic specs, 11 in-scope catalog files, 3 feature docs, BUILD_REPORT, 2 review reports, 2 audit files. Verdict: APPROVE WITH CONDITIONS (4 small follow-ups).*
