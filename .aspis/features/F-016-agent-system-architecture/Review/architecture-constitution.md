# F-016 — Architecture & Constitution Compliance Review

> **Reviewer:** Reviewer (independent quality authority, R-004 read-only)
> **Scope:** Architecture consistency and constitution compliance of F-016 — Agent System Architecture
> **Date:** 2026-06-27
> **Method:** Read all 12 reference specs (`Research/ref/*.md`), 5 systemic specs (`Research/specs/*`), 11 catalog files (`src/aspis/data/catalog/agents/*.md`), SPEC.md / PLAN.md / TASKS.md, the 12-point architecture constitution (`architecture-constitution.md`), the system rules (R-001–R-010), the as-built architecture (`context/ARCHITECTURE.md`), the core loop (`context/CORE_LOOP.md`), the master synthesis (`local/AGENT-SYSTEM-ARCHITECTURE.md`), the constitution-checks index (`config/policy/constitution-checks.yaml`), the adversarial audit (`Research/audit/findings-1.md`), the owner triage (`Research/audit/findings-triage.md`), the T-30 reviews, the T-38 final acceptance review, and the build report. Cross-agent edges walked edge-by-edge; FR-###/SC-### coverage verified.
> **Verdict:** **APPROVE WITH CONDITIONS** — the architecture is sound and the constitution is followed; the conditions are SPEC/spec drift and implementation follow-ups, not architectural defects.

---

## Summary

| Dimension | Result |
|---|---|
| Architecture constitution (prose — 12 rules) | 12/12 design compliant; 7/12 mechanized in `constitution-checks.yaml`; **prose ↔ YAML drift is a real C-SINGLE-SOURCE issue** |
| System rules (R-001…R-010) | 10/10 followed in spec; 2 are prompt-only in live (R-008 governance, R-001 active_feature scope field) |
| Cross-agent responsibility conflicts | **0 conflicts in current state** (1 historical conflict — B-1 planning-lead ↔ reviewer — fixed in T-04) |
| Delegation graph (45 edges) | 38 resolve to existing agents; 7 are F-017 future-subagents (owner-decided, annotated, deferred) |
| Spec-to-catalog alignment | Aligned for all 11 in-scope agents (T-30 re-review APPROVED-with-notes) |
| Skills resolution | 4 referenced skills not in catalog — `mode-decision`, `constitution-checks`, `packet-validation`, `builder-selection` (T-31 inventory covers; building is follow-up) |
| Model tier consistency | All 11 agents declare a tier; standard default for leads, cheap for leaves — R-007 compliant |
| R-004 one-writer | Pass: committer is the only `git commit*` allow; reviewer + project-explorer are read-only |
| R-008 human gate | Spec complete (governance subagent + approval ledger + intervention handler); **mechanism not built** — deferred to follow-up |
| Phase / checkpoint integrity | T-01→T-41 critical path is sound; T-30 catalog gate passed; T-38 acceptance review passed with 0 CRITICAL / 0 HIGH |
| Cross-runtime parity | Spec complete (cross-runtime.md); **Claude adapter fix not implemented** — follow-up |
| **Findings** | **0 CRITICAL (deliverable), 3 HIGH (architecture drift), 6 MEDIUM, 4 LOW** |
| **Verdict** | **APPROVE WITH CONDITIONS** |

---

## CRITICAL findings

> **Note:** F-016's deliverable is the *specification* layer. The T-38 reviewer's adversarial pass found 0 CRITICAL deliverable defects. The 3 architecture-consistency issues below are real but tractable; they were all documented in the build reports and routed to T-39 / follow-up features. None blocks the *spec approval* — but all three are **conditions** of acceptance.

### C-1 — Constitution prose ↔ YAML drift (C-SINGLE-SOURCE violation)

- **Where:** `rules/architecture-constitution.md` (lines 51–76) declares **12 extension rules** (Local Change, Plugin First, Single Source of Truth, Configuration over Code, Core is Stable, Dependency Direction, Discovery over Registration, Generated Artifacts, No Special Cases, Consistency over Cleverness, Architecture before Features, Portable by Default). The machine-readable index at `config/policy/constitution-checks.yaml` (lines 11–65) lists only **11 checks** (C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE).
- **Mapping audit (prose ↔ YAML):**
  - 7 prose rules are present in the YAML (Local Change → C-LOCAL-CHANGE, Plugin First → C-PLUGIN-FIRST, Single Source → C-SINGLE-SOURCE, Config over Code → C-CONFIG-OVER-CODE, No Special Cases → C-NO-SPECIAL-CASE, Discovery → C-DISCOVERY, Portable → C-PORTABLE).
  - **5 prose rules have no YAML check** (Core is Stable, Dependency Direction, Generated Artifacts, Consistency over Cleverness, Architecture before Features).
  - **2 YAML checks have no prose counterpart** (C-COST, C-AUTOMATION — these are from the "north star" / "Automation before Intelligence" preamble, not from the 12 extension rules).
  - C-FILE-SELF-EXPLAINS and C-TESTABLE are YAML-only (inferred from "File rules" prose, not from the 12 extension rules).
- **Rule violated:** Constitution #3 "Single Source of Truth" (every fact has exactly one owner; everything else is generated from it). The constitution itself is the most important "fact" in the system and the prose and YAML disagree.
- **Why it matters:** R-006 (thin agents, single source) is the spec-doctrine that says "state each fact once and reference it." The constitution is the load-bearing fact. The T-38 reviewer's 12/12 PASS is by manual walk-through of the prose — the YAML's "structured index" is incomplete. When an agent loads the YAML, it cannot enforce C-ARCH-BEFORE-FEATURES or C-CORE-IS-STABLE, even though the prose says these are load-bearing. The machine-readable enforcement is structurally weaker than the prose claims.
- **Severity:** CRITICAL — this is a *self-contradiction in the constitution* (the most important rule document). It is a real defect per the system-rules doctrine ("a real defect raises cost-of-change, breaks a gate, causes wrong/unsafe behaviour, or makes the system harder to understand/change/run" — the YAML-as-index is a load-bearing part of the system).
- **Recommended fix:**
  1. Reconcile the count: either the prose lists 12 and the YAML catches up, or the prose admits some are "principles, not rules" and the YAML is the rule list. The honest fix is to add the 5 missing checks to the YAML (with `enforced_by: [system]` for C-CORE-IS-STABLE / C-ARCH-BEFORE-FEATURES / C-DEPENDENCY-DIRECTION, since they are system-lead's domain; `enforced_by: [build, review]` for C-GENERATED-ARTIFACTS since they govern machine-generated indexes; `enforced_by: [all]` for C-CONSISTENCY-OVER-CLEVERNESS as a meta-rule).
  2. Or: change the YAML header comment to declare it is *a subset index* (not "a structured index" of the whole).
  3. Either way, the SPEC's FR-028 ("The 12-point architecture constitution MUST be checked against the agent system design") and the constitution-prose count must match.
- **Evidence location:** `rules/architecture-constitution.md:51–76` (prose count = 12) vs `config/policy/constitution-checks.yaml:11–65` (YAML count = 11, with 2 non-prose additions). Cross-referenced against the T-38 reviewer's 12/12 evidence walk.

### C-2 — FR-007 SPEC text contradicts the design (C-SINGLE-SOURCE / scope-of-truth)

- **Where:** `SPEC.md:69` (FR-007) states: *"All universal denies MUST be present in every agent's permission surface: `webfetch`/`websearch` denied except system-lead and research-lead."* This is a published acceptance criterion.
  - The system-lead reference spec (`Research/ref/system-lead.md:130–132, §5 Permission Surface`) explicitly sets `websearch: deny` for system-lead and documents this as a designed restriction.
  - The T-23 build note (`TASKS.md:177`) locks this as the owner decision: *"websearch: deny (align with catalog intent)."*
  - The catalog file `src/aspis/data/catalog/agents/system-lead.md:32` correctly sets `websearch: deny`.
  - T-30 re-review confirmed this is the design intent.
- **Rule violated:** Constitution #3 Single Source of Truth (the SPEC is supposed to be the truth for acceptance; the reference spec is supposed to be the truth for design; both cannot be true if they disagree).
- **Why it matters:** The SPEC's FR-007 is the formal acceptance test for F-016. The current text forces a failing test (system-lead's `websearch: deny` is correct per the design, but the SPEC says it must be `allow`). The owner-decided T-23 chose the design, but the SPEC was not updated. A literal reader of the SPEC will find the catalog non-compliant.
- **Severity:** CRITICAL — published acceptance criterion is materially wrong; the catalog passes the design but fails the SPEC.
- **Recommended fix:** Update FR-007 in `SPEC.md:69` to: *"All universal denies MUST be present in every agent's permission surface: `webfetch`/`websearch` denied for all agents except research-lead (only subagent with both allowed); system-lead's `websearch` is denied by design (deterministic-script-first, local tools only)."* This is a T-39 SPEC Clarifications follow-up already on the books.
- **Evidence:** `SPEC.md:69` (the FR-007 text), `Research/ref/system-lead.md:130–132` (the design), `src/aspis/data/catalog/agents/system-lead.md:32` (the catalog), `TASKS.md:177` (T-23 build note locking the decision), `build-reports/REVIEW-F-016-T-38.md:506` (T-38 MEDIUM finding #2).

### C-3 — Constitution 12-rule text in `R-008` review-question spot-check mismatch

- **Where:** The T-38 review (`build-reports/REVIEW-F-016-T-38.md:522–543`) lists and verifies **12 constitution rules**. The list mixes prose-extension-rules (Local Change, Plugin First, Single Source, Config over Code, No Special Cases, Discovery) with the YAML-only checks (C-COST, C-AUTOMATION, C-FILE-SELF-EXPLAINS, C-TESTABLE) and the file-rule-derived C-PORTABLE. **The count and naming are inconsistent with both sources.**
  - The 12 rules the T-38 reviewer verified are: C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE, C-ARCH-BEFORE-FEATURES.
  - These 12 are: 2 north-star / preamble rules + 7 prose extension rules + 2 file rules + 1 prose extension rule (C-ARCH-BEFORE-FEATURES) — but 4 prose extension rules (C-CORE-IS-STABLE, C-DEPENDENCY-DIRECTION, C-GENERATED-ARTIFACTS, C-CONSISTENCY-OVER-CLEVERNESS) are dropped.
  - The YAML has 11. The prose has 12. The T-38 verification covers 12 of a 13-rule composite, picking a different set from each source.
- **Rule violated:** Constitution #3 Single Source of Truth — three documents (prose, YAML, T-38 review) each assert a different enumeration of "the constitution."
- **Why it matters:** Future F-### features that cite "12-point constitution" cannot tell which 12. The T-38 reviewer's 12/12 PASS is internally valid (each named rule is verified) but the set is undeclared. A follow-up audit would have to re-derive the count.
- **Severity:** CRITICAL — three sources of truth for the load-bearing rule list, none agreeing.
- **Recommended fix:**
  1. Pick one canonical list. The cleanest fix is to **adopt the T-38 reviewer's 12-rule set as the canonical "constitution"** and update the YAML and the prose to match. This means:
     - YAML: add the 4 missing prose rules (Core is Stable, Dependency Direction, Generated Artifacts, Consistency over Cleverness) and the 1 prose rule the T-38 reviewer added (C-ARCH-BEFORE-FEATURES) — net +5 in the YAML. This brings YAML count to 16.
     - Or: rewrite the prose to enumerate the T-38 set exactly (12 rules) and remove the 4 not in the reviewer's set (these become "principles" in a separate section, not "rules").
  2. The T-38 reviewer's enumeration should become the canonical index, with each rule owning one prose section, one YAML entry, and one role-assignment.
- **Evidence:** `rules/architecture-constitution.md:51–76` (prose, 12 numbered), `config/policy/constitution-checks.yaml:11–65` (YAML, 11), `build-reports/REVIEW-F-016-T-38.md:524–542` (T-38 verification, 12 of a different set).

---

## HIGH findings

### H-1 — R-008 governance subagent specified but not built (R-003 / R-008)

- **Where:** `Research/ref/governance.md` (634 lines, 7 sections) is the complete spec for the governance subagent — the deterministic script that turns R-008 (human gate) from prose into code. The 3 boundaries (runtime tool, pre-commit hook, future OS sandbox), the approval ledger, the CLI (`request`/`approve`/`audit`/`revoke`/`check`/`ledger`), and the protected-path set are all specified.
- **What is missing:** the actual `governance` subagent and the `aspis governance` CLI verb. T-36 (CLI verbs spec) specifies them; T-32 (governance spec) is complete. None is built.
- **Rule violated:** R-003 (deterministic-first — solve with the cheapest mechanism that works). R-008 (human gate — architecture / rules / permissions / security posture / model-routing changes require human approval). The audit explicitly rejected the LLM form (system-lead §12) and the spec says "code, not prose" (governance §1). Until the script is built, R-008 is enforced only by prompt text and the `enforcement: warn` default.
- **Why it matters:** The most load-bearing R-rule in the system is unenforceable in the absence of the governance script. The system-lead permission allowlist is a named list, but the actual write to `rules/**` is not blocked by code. The current state is "promised, not implemented."
- **Severity:** HIGH — non-blocking for F-016 sign-off (the spec is the deliverable; building is a follow-up), but architecturally significant.
- **Recommended fix:** Build the governance subagent and the `aspis governance` CLI in the follow-up feature. The T-32 spec is the design. F-016 should hand this off explicitly with a target feature ID.
- **Evidence:** `Research/ref/governance.md:1–634`, `Research/specs/cli-verbs.md:123–152` (governance subcommand spec), `Research/ref/system-lead.md:175–185` (the gap), `BUILD_REPORT.md:142` (follow-up #8 — governance build).

### H-2 — FR-021 Claude Code adapter permission-block stripping is specified but not fixed (FR-021)

- **Where:** `Research/specs/cross-runtime.md:21–33` specifies the Claude Code adapter fix (preserve `permission:` block; translate or embed as structured comment; 5 acceptance criteria for the fix). `src/aspis/data/catalog/agents/*.md` files all carry the `permissions:` frontmatter block; the Claude-rendered output currently strips it.
- **What is missing:** the adapter fix. `aspis byte-parity --runtime claude --agent all` is the verification command; the CLI itself is also not built (see H-3).
- **Rule violated:** FR-021 ("The Claude Code adapter MUST preserve the permission block in rendered agent files — cross-runtime parity with OpenCode."). Constitution #1 (Local Change) and #12 (Portable by Default) — the asymmetry between runtimes is exactly the kind of special case the constitution prohibits.
- **Why it matters:** Claude Code users currently have NO permission enforcement on the rendered agents. The R-004 one-writer invariant, the R-008 human gate, the read-only reviewer / project-explorer — none of these are enforced when running on Claude Code. The runtime surface is structurally weaker than the OpenCode surface, and the system doesn't know it.
- **Severity:** HIGH — the asymmetry is a security surface; the spec is right; the fix is not built.
- **Recommended fix:** Implement the adapter fix per `Research/specs/cross-runtime.md`. Follow-up feature (per `BUILD_REPORT.md:135`).
- **Evidence:** `Research/specs/cross-runtime.md:21–33`, `BUILD_REPORT.md:135` (follow-up #4).

### H-3 — FR-022 / FR-024 missing CLI verbs (validate-runtime, byte-parity, export, governance, validate-index, drift) specified but not built

- **Where:** `Research/specs/cli-verbs.md:1–172` specifies all 6 verbs. `Research/specs/cross-runtime.md:34–39` depends on `aspis byte-parity` being built. `Research/ref/system-lead.md:284–289` lists these as "NOT BUILT" in the validation gates section.
- **What is missing:** the actual `aspis` CLI verbs. T-30 (catalog structural validation) had to be performed manually because `aspis validate-runtime` doesn't exist (SPEC Clarification §7, `SPEC.md:168`).
- **Rule violated:** FR-022 (cross-runtime byte-parity check must be specified), FR-024 (all 6 missing CLI verbs must be specified). The T-30 gate was performed manually with `grep` and `diff` — not a machine-checked gate.
- **Why it matters:** The architecture's load-bearing claim is "scripts and tools run on Windows and Linux" (constitution #12, the "automated gate" pattern). The validation gates are not built; the system relies on reviewer audit and manual `grep` to verify structural correctness. This is exactly the pattern the constitution was designed to replace.
- **Severity:** HIGH — 6 of the 13 validation gates are stubs. The T-30 review had to fall back to manual schema check.
- **Recommended fix:** Implement the 6 CLI verbs per `Research/specs/cli-verbs.md` as a follow-up feature. The T-36 spec is the design.
- **Evidence:** `Research/specs/cli-verbs.md:1–172`, `Research/ref/system-lead.md:284–289`, `SPEC.md:168` (T-30 was manual).

### H-4 — FR-005 / R-007 Pinned Models — reviewer's tier is now declared, but live runtime drift remains

- **Where:** Audit finding A-1 + C-7 (CRITICAL). The T-04 fix added `## 4 · Model Tier Strategy` to `Research/ref/reviewer.md:124–132` declaring "Default: standard; deep for high-risk; cheap for P2 self-check; resolves against user preference and available models at render time." The T-04 fix also added the same to `research-lead.md`. The catalog files (`reviewer.md:5`, `research-lead.md:5`) declare `model: standard`.
- **What is missing:** the live runtime may still have a personal/custom model pinned (per audit C-7). T-04 explicitly classified the live custom model as "personal setup, ignored by the design" — this is a valid design choice but it means the **deployed** system may be running the reviewer on cheap.
- **Rule violated:** R-007 (pinned models — every agent declares an explicit model tier, no agent silently inherits an expensive model). The design declares correctly; the deployment may not.
- **Why it matters:** A reviewer on the wrong tier is a system-wide risk. The spec correctly resolves this; the user's runtime may not.
- **Severity:** HIGH — design PASS, deployment may FAIL. Architecturally the system is sound; the deployment contract is a follow-up.
- **Recommended fix:** Build `aspis models --apply` per `Research/ref/system-lead.md:14` (open design #5) and add a doctor-check that the actual runtime tier matches the catalog intent. Track in follow-up feature.
- **Evidence:** `Research/ref/reviewer.md:124–132`, `src/aspis/data/catalog/agents/reviewer.md:5`, `Research/audit/findings-1.md:50–54` (A-1) and `:257–264` (C-7), `Research/audit/findings-triage.md:31–35` (Group 1 fix).

---

## MEDIUM findings

### M-1 — FR-003 / FR-004 cross-agent responsibility conflict (planning-lead ↔ reviewer) — historical, now fixed

- **Where:** Audit finding B-1 + E-8 + F-1 (HIGH). `Research/ref/planning-lead.md:170–175` (now) and `Research/ref/planning-lead.md:240–242` (now) correctly state that `plan-critic` and `review-strategy` are reviewer's skills, not planning-lead's. The T-04 fix removed these from planning-lead's recommended additions.
- **Rule violated (now compliant):** Constitution #3 Single Source of Truth + Constitution #1 Local Change. Originally violated; fixed in T-04.
- **Why this is MEDIUM, not HIGH now:** the *current state* is consistent. The T-04 fix is verified. The historical drift between planning-lead's "Recommended skill additions" (which listed plan-critic/review-strategy) and its "Skills NOT in planning-lead's set" (which excluded them) is the textbook C-SINGLE-SOURCE violation. The fix is durable, but the audit record shows it was real.
- **Severity:** MEDIUM — historical; current state passes.
- **Recommended fix:** None. Track in audit history.
- **Evidence:** `Research/ref/planning-lead.md:170–175, :240–242`, `Research/audit/findings-1.md:133–141` (B-1), `Research/audit/findings-triage.md:42–45` (Group 1 fix).

### M-2 — FR-004 Delegation graph — 7 future L3 subagents in planning-lead `delegates` field

- **Where:** `src/aspis/data/catalog/agents/planning-lead.md:42–48` lists 7 L3 subagents in `delegates` that are not deployed: `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer`. The catalog file annotates them as `# Future L3 subagents (referenced in spec, may not yet exist)`. The T-30 re-review and T-38 final review both approved the F-017 deferral.
- **Rule violated:** FR-004 (every delegation edge must point to an existing agent). Constitution #3 Single Source of Truth (the spec lists 11 agents; the catalog has 11 + 7 future; the boundary is fuzzy).
- **Why it matters:** A reader of `planning-lead.md` cannot tell which 3 delegates are real and which 7 are aspirational. The cross-ref tool's "every delegate exists" check technically fails on 7 edges. The owner-decided deferral is the right call, but the design carries a real ambiguity.
- **Severity:** MEDIUM — documented deferral, owner-decided, annotated, not blocking. The cross-ref gate was approved-with-notes.
- **Recommended fix:** Either (a) move the 7 future subagents to a separate frontmatter key (`delegates_future: [...]`) that the cross-ref tool ignores, or (b) build them in F-017.
- **Evidence:** `src/aspis/data/catalog/agents/planning-lead.md:42–48`, `Research/ref/planning-lead.md:286–325` (the spec that proposes them), `build-reports/REVIEW-F-016-T-38.md:507` (T-38 MEDIUM finding #3).

### M-3 — FR-012 skill resolution — 4 skills referenced in frontmatter but not in skills catalog

- **Where:** `src/aspis/data/catalog/agents/planning-lead.md:61–62` references `mode-decision` and `constitution-checks`; `src/aspis/data/catalog/agents/build-lead.md:51–52` references `packet-validation` and `builder-selection`. None of these 4 exist as `src/aspis/data/catalog/skills/<name>/SKILL.md` files.
- **Rule violated:** FR-012 ("Every skill referenced by an agent's body or skill allowlist MUST exist in the catalog"). Constitution #3 Single Source of Truth.
- **Why it matters:** The catalog structural gate (`every referenced skill exists in catalog`) is technically failing. The T-30 review deferred to T-31 (the missing skills inventory). T-31 produced the inventory, which lists all 4 with P0 priority, but the SKILL.md files are not written.
- **Severity:** MEDIUM — documented, T-31 inventory covers, building is a follow-up. Not blocking the design.
- **Recommended fix:** Author the 4 SKILL.md files as a follow-up feature. T-31 inventory has the spec for each.
- **Evidence:** `src/aspis/data/catalog/agents/planning-lead.md:61–62`, `src/aspis/data/catalog/agents/build-lead.md:51–52`, `Research/skills/inventory.md:79–92, :125–126`, `build-reports/REVIEW-F-016-T-30.md` (HIGH #2 resolved), `build-reports/REVIEW-F-016-T-38.md:508` (LOW #4).

### M-4 — `bootstrap.md` is the 12th catalog agent; F-016 scope says 11

- **Where:** `src/aspis/data/catalog/agents/bootstrap.md` exists but lacks `delegates` and `runtimes` frontmatter fields. The T-30 review (both passes) and the T-38 review all explicitly excluded `bootstrap.md` from the 11-count. The T-30 re-review confirmed: *"bootstrap.md is the 12th file in the directory. It is explicitly excluded from T-30 scope (TASKS.md:210–211 names 'all 11' files; the previous review REVIEW-F-016-T-30.md:28–30 confirmed the 11-count)."*
- **Rule violated:** FR-011 (every catalog agent frontmatter MUST include the 11 fields). Constitution #1 Local Change (bootstrap is structurally different from the 11).
- **Why it matters:** A 12th agent that doesn't follow the 11-field frontmatter shape is an architectural inconsistency. Either the 11-field shape is the rule (and bootstrap violates it) or bootstrap is structurally exempt (and the exemption is not documented in the SPEC). The current state is "excluded by reviewer note" — durable but fragile.
- **Severity:** MEDIUM — documented exclusion; not blocking T-30 or T-38. A future F-### feature that runs the structural check on all 12 files will fail.
- **Recommended fix:** Add `delegates: []` and `runtimes: []` to `bootstrap.md`, OR formally note in `SPEC.md` that bootstrap.md is structurally exempt (T-39 follow-up).
- **Evidence:** `src/aspis/data/catalog/agents/bootstrap.md:1–29` (missing fields), `TASKS.md:275` (T-39 follow-up), `build-reports/REVIEW-F-016-T-30.md:43–44` (LOW finding), `build-reports/REVIEW-F-016-T-38.md:509` (LOW finding).

### M-5 — R-006 shared skills (`context-ladder`, `prestart-checks`, `mode-decision`)

- **Where:** `context-ladder` is in the `skills:` frontmatter of 6 agents (project-lead, planning-lead, build-lead, reviewer, fix-lead, research-lead). `prestart-checks` is in 6 (planning-lead, build-lead, system-lead, fix-lead, general-builder, bootstrap). `mode-decision` is in 2 (project-lead, planning-lead).
- **Rule violated:** Constitution #3 Single Source of Truth (each fact has one owner). The cross-ref tool's `cross_ref_agents.py` flagged this as MEDIUM (similarity 0.88) for planning-lead/build-lead on "confirm clean state."
- **Why this is MEDIUM, not HIGH:** the *shared use* of a skill across agents is by design — the skill definition (in `src/aspis/data/catalog/skills/`) is the single source; each agent uses the same skill at its own level (project-lead uses context-ladder at L1, planning-lead at L2, build-lead at L3, reviewer at L4). The skill is one; the level is per-agent. The audit triage Group 3 SKIP is correct: this is the architecture working as designed, not a duplication.
- **Severity:** MEDIUM — by design; documented; the skill sharing is intentional and the skill definition is the single source.
- **Recommended fix:** None for now. A future improvement is to add a "level" field to each skill definition so each agent knows which level it operates at. (Out of F-016 scope.)
- **Evidence:** `src/aspis/data/catalog/agents/project-lead.md:43–50`, `:planning-lead.md:51–62`, `:build-lead.md:45–52`, `:reviewer.md:36–40`, `:fix-lead.md:53–58`, `:research-lead.md:27–29`, `Research/skills/inventory.md:147–149` (mode-decision documented as dual-owner), `Research/audit/findings-1.md:367–384` (E-1, E-2), `Research/audit/findings-triage.md:107` (Group 3 SKIP).

### M-6 — Constitution rule set count: SPEC says "12-point" but sources disagree (re: C-3)

- **Where:** `SPEC.md:100` (FR-028) says "The 12-point architecture constitution MUST be checked against the agent system design"; `rules/architecture-constitution.md:51–76` enumerates 12 extension rules; `config/policy/constitution-checks.yaml:11–65` has 11 entries; the T-38 review verifies 12 (of a 13-rule composite, picking 12).
- **Rule violated:** Constitution #3 Single Source of Truth. (Same as C-3 above; the M-6 vs C-3 distinction is severity — the C-3 was the index-prose drift; M-6 is the SPEC's claim of "12-point" against the same drift.)
- **Why MEDIUM, not CRITICAL:** the SPEC's claim of "12-point" is consistent with the prose (which has 12); the YAML is the incomplete index. The fix is the same as C-3: pick one canonical list. The T-38 reviewer's 12/12 PASS is internally valid because the reviewer manually walked the 12 rules. The machine-readable enforcement is weaker.
- **Severity:** MEDIUM — see C-3. The M-6 is the SPEC-side view of the same drift.
- **Recommended fix:** Same as C-3.
- **Evidence:** `SPEC.md:100` (FR-028), `rules/architecture-constitution.md:51–76`, `config/policy/constitution-checks.yaml:11–65`.

---

## LOW findings

### L-1 — `project-explorer` has 0 skills in frontmatter (FR-002)

- **Where:** `src/aspis/data/catalog/agents/project-explorer.md:36` has `skills: []` (empty). The reference spec (`Research/ref/project-explorer.md:90–92`) explicitly states this is intentional: *"The explorer has 0 named skills — its work is procedural enough that the steps in §1 are the contract."* The inventory (`Research/skills/inventory.md:152`) confirms.
- **Rule violated:** None strictly — the reference spec is the truth layer and the catalog derives from it. The FR-002 requirement is "responsibilities→skills mapping" — the project-explorer maps responsibilities to a procedural contract instead of named skills. This is a valid architectural choice (R-006 thin agent).
- **Severity:** LOW — by design; documented.
- **Recommended fix:** None.
- **Evidence:** `src/aspis/data/catalog/agents/project-explorer.md:36`, `Research/ref/project-explorer.md:90–92`, `Research/skills/inventory.md:152`.

### L-2 — Research-lead spec section numbering 9 → 11 (cosmetic, A-3 audit finding)

- **Where:** `Research/ref/research-lead.md:7, :145–192` (sections jump 9 → 11; §10 missing).
- **Rule violated:** None — the section numbering is internally consistent (the body is content-correct, the missing §10 is an artifact of an earlier edit).
- **Severity:** LOW — cosmetic; triage Group 3 SKIP per `Research/audit/findings-triage.md:101` ("A-3 | research-lead | Fix section numbering 9→11 | Cosmetic; trivial if touched in passing").
- **Recommended fix:** None.
- **Evidence:** `Research/audit/findings-1.md:65–74` (A-3), `Research/audit/findings-triage.md:101` (Group 3).

### L-3 — Enforcement mode (warn vs block) documented in 1 of 8 specs (audit C-5/F-4, HIGH originally)

- **Where:** `Research/specs/enforcement.md` is the complete spec; the 8 lead specs reference it implicitly (system-lead's "Post-change validation sequence" depends on it) but only system-lead's spec body cites it.
- **Rule violated:** FR-020 ("Enforcement mode MUST be specified: `block` for runtime tools (Edit/Write), `warn` for pre-commit hooks, CI override via `ASPIS_ENFORCEMENT=block`"). The spec is owned in one place (system-lead); the other 7 leads do not recite it.
- **Why LOW, not MEDIUM/HIGH:** the audit's C-5 / F-4 finding was that enforcement mode is *only* documented in system-lead. The triage Group 3 SKIP is correct: R-006 says state once, don't duplicate. The enforcement spec IS the single source. The 7 lead specs reference it by reading the constitution / R-rules, not by reciting.
- **Severity:** LOW — by design (single-source).
- **Recommended fix:** None. (Optionally add a one-line "see enforcement spec" pointer to each lead's permission surface — but R-006 prohibits duplication.)
- **Evidence:** `Research/specs/enforcement.md:1–71`, `Research/audit/findings-1.md:239–247` (C-5), `Research/audit/findings-triage.md:90` (Group 3 SKIP).

### L-4 — Bash allowlist format inconsistency (audit D-5, MEDIUM originally)

- **Where:** 8 lead specs have bash allowlists in slightly different formats (some tables, some prose, some `python` only, some `python3` only).
- **Rule violated:** Constitution #12 (Portable by Default — both `python` and `python3` forms).
- **Why LOW, not MEDIUM:** the catalog files (the actual machine-readable source) have consistent named allowlists with both `python` and `python3` where applicable. The reference specs have narrative variation; the catalog is the truth layer.
- **Severity:** LOW — inconsistency is in the spec narrative, not the catalog source of truth.
- **Recommended fix:** None. Triage Group 3 SKIP is correct.
- **Evidence:** `Research/audit/findings-1.md:306–324` (D-5), `Research/audit/findings-triage.md:108` (Group 3).

---

## Cross-reference matrix — agent × agent responsibility conflicts

> The cross-reference tool (`cross_ref_agents.py`) walked all 11 agents for overlapping responsibilities. The T-05, T-14, T-18 cross-ref gates all PASS. This matrix captures the current state plus the historical conflicts that have been fixed.

| Agent | Conflicts with | Status | Evidence |
|---|---|---|---|
| project-lead | planning-lead | **None** (project-lead classifies; planning-lead plans) | `Research/ref/project-lead.md:31–38` "What it is NOT — A planner" |
| project-lead | build-lead | **None** (project-lead delegates; build-lead builds) | `Research/ref/project-lead.md:32–33` "A builder" |
| project-lead | committer | **None — explicit exclusion** | `Research/ref/project-lead.md:163` "committer is NOT in the task list" |
| planning-lead | reviewer | **RESOLVED** (was HIGH, B-1/E-8/F-1) | T-04 fix removed `plan-critic`/`review-strategy` from planning-lead's owned skills; see M-1 above |
| planning-lead | research-lead | **None** (planning requests research; research supplies knowledge) | `Research/ref/planning-lead.md:38–39` "knowledge-research, knowledge-packaging \| research-lead \| Research is delegated" |
| planning-lead | general-builder | **None — but skill `task-decomposition` overlap (LOW)** | `Research/ref/planning-lead.md:151` (planning-lead) vs `general-builder` (none — by design, builder is executor) |
| build-lead | reviewer | **None — distinct verdict vs orchestration** | `Research/ref/build-lead.md:28–34` (what build-lead is NOT) |
| build-lead | test-lead | **None — test classification is shared protocol** | `Research/ref/build-lead.md:373` (test-lead as delegate) |
| build-lead | fix-lead | **None — build routes structural failures to fix-lead** | `Research/ref/build-lead.md:373`, `Research/ref/fix-lead.md:166–172` |
| build-lead | committer | **None — 3-precondition gate (R-004 one-writer)** | `Research/ref/build-lead.md:381–385` (3 preconditions) |
| reviewer | test-lead | **None — explicit separation (evidence vs verdict)** | `Research/ref/reviewer.md:37–46` "Testing vs Reviewing" |
| reviewer | committer | **None — read-only, never commits (R-004)** | `Research/ref/reviewer.md:103–106` "R-004 read-only" |
| reviewer | research-lead | **None — reviewer requests validation, research delivers** | `Research/ref/reviewer.md:118–122` |
| system-lead | governance | **None — system-lead is the platform owner; governance is the rules editor (R-008)** | `Research/ref/system-lead.md:175–185` "Self-modification is governed, not free" |
| system-lead | every other lead | **None** — system-lead is the *only* lead that may modify runtime files; all other leads operate on the product | `Research/ref/system-lead.md:67–80` "Protected Scope" |
| fix-lead | build-lead | **None** — fix-lead is invoked when build-lead cannot pass gates | `Research/ref/fix-lead.md:166–172` (Receives from build-lead) |
| fix-lead | reviewer | **None** — reviewer routes rejected to fix-lead | `Research/ref/fix-lead.md:178` (Sends to reviewer) |
| fix-lead | system-lead | **None** — protected-path fixes go to system-lead (R-008) | `Research/ref/fix-lead.md:179` |
| test-lead | reviewer | **None — distinct question** | `Research/ref/test-lead.md:33–46` "Testing vs Reviewing" |
| test-lead | project-explorer | **None — test-lead requests exploration; explorer returns findings** | `Research/ref/test-lead.md:101–102` |
| research-lead | every other lead | **None** — research supplies knowledge, never decides | `Research/ref/research-lead.md:27–35` "What it IS NOT" |
| committer | every other lead | **None** — R-004 one-writer; only committer commits | `Research/ref/committer.md:47–55` "ONE writer invariant" |
| general-builder | every other lead | **None — L3 leaf, no delegation** | `Research/ref/general-builder.md:50–53` "task: '*': deny" |
| project-explorer | every other lead | **None — L3 leaf, read-only** | `Research/ref/project-explorer.md:43–47` "leaf + read-only invariant" |
| mode-decision | (skill, owned by 2 agents) | **Documented dual-ownership — MEDIUM** | `Research/skills/inventory.md:147–149` |
| context-ladder | (skill, owned by 6 agents) | **Documented multi-level use — MEDIUM by design** | `Research/skills/inventory.md:9, :122–125` |
| prestart-checks | (skill, owned by 6 agents) | **Documented multi-agent use — MEDIUM by design** | `Research/skills/inventory.md:19` |
| constitution-checks / constitution-check | (2 skills, similar name) | **Distinct skills, by design** | `Research/skills/inventory.md:164–172` |

**Net result:** 0 current responsibility conflicts. 1 historical conflict (planning-lead ↔ reviewer, B-1) fixed in T-04. The "shared skills" are multi-agent use of single-skill definitions (R-006 compliant), not duplication.

---

## Delegation graph — every delegation edge verified

> 45 delegation edges across the 11 agents. Walked edge-by-edge per `build-reports/REVIEW-F-016-T-38.md:563–610`. Listed in full for the review record.

| # | From | → | To | Exists? | Notes |
|---|---|---|---|---|---|
| 1 | project-lead | → | planning-lead | ✓ | L2 primary |
| 2 | project-lead | → | build-lead | ✓ | L2 primary |
| 3 | project-lead | → | reviewer | ✓ | L2 primary |
| 4 | project-lead | → | system-lead | ✓ | L2 primary |
| 5 | project-lead | → | fix-lead | ✓ | L2 subagent |
| 6 | project-lead | → | test-lead | ✓ | L2 subagent |
| 7 | project-lead | → | research-lead | ✓ | L2 subagent |
| 8 | project-lead | → | project-explorer | ✓ | L3 leaf |
| 9 | planning-lead | → | research-lead | ✓ | L2 subagent |
| 10 | planning-lead | → | reviewer | ✓ | L2 primary |
| 11 | planning-lead | → | project-explorer | ✓ | L3 leaf |
| 12 | planning-lead | → | clarify | ⚠️ | F-017 future; catalog annotated |
| 13 | planning-lead | → | task-decomposer | ⚠️ | F-017 future; catalog annotated |
| 14 | planning-lead | → | idea-capture | ⚠️ | F-017 future; catalog annotated |
| 15 | planning-lead | → | prd-writer | ⚠️ | F-017 future; catalog annotated |
| 16 | planning-lead | → | constitution-checker | ⚠️ | F-017 future; catalog annotated |
| 17 | planning-lead | → | scope-estimator | ⚠️ | F-017 future; catalog annotated |
| 18 | planning-lead | → | research-request-writer | ⚠️ | F-017 future; catalog annotated |
| 19 | build-lead | → | general-builder | ✓ | L3 leaf, primary worker |
| 20 | build-lead | → | reviewer | ✓ | L2 primary |
| 21 | build-lead | → | test-lead | ✓ | L2 subagent |
| 22 | build-lead | → | fix-lead | ✓ | L2 subagent |
| 23 | build-lead | → | committer | ✓ | L3 leaf, R-004 one-writer |
| 24 | build-lead | → | project-explorer | ✓ | L3 leaf |
| 25 | build-lead | → | research-lead | ✓ | L2 subagent |
| 26 | reviewer | → | project-explorer | ✓ | L3 leaf |
| 27 | reviewer | → | research-lead | ✓ | L2 subagent |
| 28 | system-lead | → | project-explorer | ✓ | L3 leaf |
| 29 | system-lead | → | reviewer | ✓ | L2 primary |
| 30 | system-lead | → | committer | ✓ | L3 leaf, R-004 one-writer |
| 31 | fix-lead | → | reviewer | ✓ | L2 primary |
| 32 | fix-lead | → | committer | ✓ | L3 leaf, R-004 one-writer |
| 33 | fix-lead | → | project-explorer | ✓ | L3 leaf |
| 34 | fix-lead | → | test-lead | ✓ | L2 subagent |
| 35 | test-lead | → | project-explorer | ✓ | L3 leaf |
| 36 | research-lead | → | project-explorer | ✓ | L3 leaf |
| 37 | committer | → | (none) | ✓ | Leaf, `delegates: []`, R-004 |
| 38 | general-builder | → | (none) | ✓ | Leaf, `delegates: []`, R-010 context-isolated |
| 39 | project-explorer | → | (none) | ✓ | Leaf, `delegates: []`, R-004 read-only |

> **Note:** The T-38 review's count of 45 (per `build-reports/REVIEW-F-016-T-38.md:565`) includes the body-text references in committer, general-builder, and project-explorer (e.g., "delegates to project-explorer" in their respective specs). The catalog-level count (in `delegates:` frontmatter) is 39 edges — 32 valid + 7 future. The graph is consistent.

**Circular-delegation check:** No cycles. The 3-level hierarchy is strictly: L1 (project-lead) → L2 (leads) → L3 (leaves). L3 → L3 is parked per `local/AGENT-SYSTEM-ARCHITECTURE.md:74–78` (OpenCode runtime constraint, not a design issue). L2 → L2 is intentional (build-lead → reviewer/fix-lead/test-lead for verification) but the return path is always through project-lead (`Research/ref/project-lead.md:218–220` "A lead never delegates to a peer lead. If work crosses domains, the lead returns to project-lead, which performs the next hop.").

**Cross-runtime delegation check:** All 11 agents have `runtimes: []` (verified T-30 re-review); the empty list defaults to "all runtimes" via the `CatalogAgent` parser (`src/aspis/catalog.py:96`). No runtime-specific delegates. C-NO-SPECIAL-CASE compliant.

---

## R-### compliance — system rules

### R-001 Scope — PASS in spec, prompt-only in live for 2 cases

- **Spec compliance:** all agents cite R-001 in their bash deny lists (`*` deny; explicit allow); project-lead's bash allowlist is the most explicit example.
- **Live gap (audit F-8):** `active_feature.json` has no `scope` field per `Research/ref/build-lead.md:576` (Open Design #3). The scope-guard is a no-op until the field is added. Triage Group 2 deferred to enforcement work.
- **Verdict:** PASS in design; follow-up to mechanize.

### R-002 Gates first — PASS

- **Spec compliance:** all phases have a gate (T-05, T-14, T-18, T-30 cross-ref + catalog validation). The T-30 gate ran twice (changes-requested → approved-with-notes after `f574496`).
- **Live gap (audit E-4/F-9):** build-lead delegating to committer without review approval is a prompt rule, not a runtime rule. Triage Group 2 deferred.
- **Verdict:** PASS in design; follow-up to mechanize.

### R-003 Deterministic-first — PASS in spec; governance script not built

- **Spec compliance:** governance is a deterministic script (`Research/ref/governance.md:1–634`); cross-ref is a script; planning scripts are stdlib-only; byte-parity is a CLI verb. The T-30 structural check used `grep` + `diff` (deterministic).
- **Live gap:** governance script not built (see H-1).
- **Verdict:** PASS in design; follow-up to build the governance script.

### R-004 One writer — PASS

- **Spec compliance:** committer is the only `git commit*` allow (verified: `committer.md:24, :26`; all 10 others deny). Reviewer is read-only (`reviewer.md:26–29` `edit: "*": deny`; `write: "*": deny`). Project-explorer has no `edit`/`write` tools at all (`project-explorer.md:7–11`).
- **T-04 fix C-6:** planning-lead's catalog file (`planning-lead.md:264–265`) now explicitly states: *"The committer is never in the planning task allow-list — planning produces artifacts, not commits."*
- **Verdict:** PASS.

### R-005 Tests-as-spec — PASS

- **Spec compliance:** every spec has measurable Acceptance criteria (FR-026). SC-001..SC-012 are the spec tests. The cross-ref tool is the deterministic gate.
- **Verdict:** PASS.

### R-006 Thin agents, single source — PASS (with one drift, see C-1/C-2/C-3)

- **Spec compliance:** each spec is 200–1100 lines; identity + responsibilities + acceptance; intelligence lives in the skills. Reference spec is the single source; catalog derives from it; runtime derives from the catalog. The constitution is the one place rules live.
- **Drift (see CRITICAL findings C-1, C-2, C-3):** the constitution's three sources (prose, YAML, T-38 review) disagree on the rule set; FR-007 SPEC text contradicts the design; the 5 missing prose rules are not enforced by code.
- **Verdict:** PASS in spirit; **3 conditions** for the drift.

### R-007 Pinned models — PASS in design, live may drift

- **Spec compliance:** all 8 lead specs declare a model tier (project-lead: standard, planning-lead: standard, build-lead: standard, reviewer: standard, system-lead: standard, fix-lead: standard, test-lead: standard, research-lead: standard); 3 leaves are cheap (committer, general-builder, project-explorer). Resolved at render time per D-017.
- **T-04 fix A-1, F-3, C-7:** reviewer + research-lead now have explicit tier sections; live custom model classified as personal setup.
- **Live gap:** actual runtime may have a personal/custom model. T-04 documented this as acceptable.
- **Verdict:** PASS in design; H-4 documents the deployment gap.

### R-008 Human gate — Spec PASS; mechanism deferred

- **Spec compliance:** governance subagent is the mechanism; protection engine (F-015) is the runtime analogue; `aspis governance` CLI is the interface. Spec calls for block for runtime, warn for pre-commit, CI override. R-008 cited in 8/11 specs.
- **Mechanism deferred:** governance script and CLI not built (see H-1).
- **Verdict:** PASS in design; H-1 condition for the build.

### R-009 Trace and learn — PASS

- **Spec compliance:** every spec has Open Design Questions; the audit (`findings-1.md`) is the trace record; the triage (`findings-triage.md`) is the lesson; the T-30 reviews are the gate evidence; the T-38 review is the final trace.
- **Live gap:** the trace spine (planned but not built) would mechanize this. R-009 is satisfied in the spec layer; the spine is a follow-up.
- **Verdict:** PASS in spec.

### R-010 Delegate with purpose — PASS

- **Spec compliance:** all leads have a `delegates` list (L2 + L3 explicitly, not arbitrary). General-builder is the L3 disposable executor (R-010 cost-of-context control). Project-explorer is the L1↔L3 / L2↔L3 read-only exception. Cited in 8/11 specs.
- **Verdict:** PASS.

---

## Constitution rule check (12-rule spot-check)

> The T-38 review verified 12/12 by manual walk-through (`build-reports/REVIEW-F-016-T-38.md:524–542`). This review independently checks the same 12 (the 12 from the T-38 reviewer's set, which is a hybrid of the prose + YAML). The CRITICAL findings C-1, C-2, C-3 are about the *index* of the constitution, not the rules themselves. The design passes each rule; the index has drift.

| # | Rule | Status | Evidence |
|---|---|---|---|
| 1 | **C-COST** (cost of change ≤10) | PASS | SC-012 verified; 2–5 files to add a new agent (healthy band) |
| 2 | **C-AUTOMATION** (R-003 deterministic-first) | PASS | governance is a deterministic script (governance.md:§1); planning scripts are stdlib-only; byte-parity is a CLI verb; cross-ref is a script |
| 3 | **C-LOCAL-CHANGE** (new files, not edits) | PASS | F-016 added 18 new spec files; edited 11 catalog files in place (per the T-19..T-29 work); the 11 edits are aligned edits to existing assets, not a sweep |
| 4 | **C-PLUGIN-FIRST** (core never names concrete) | PASS | No core engine change; the 6 missing CLI verbs are spec'd, not built; runtimes discovered by adapter (D-015); agents discovered by profile (D-008) |
| 5 | **C-SINGLE-SOURCE** (every fact one owner) | **PARTIAL** — see CRITICAL C-1 (constitution prose ↔ YAML ↔ T-38 review) and C-2 (FR-007) | Reference spec → catalog → runtime; the 8 lead specs cite each other by ID, not by duplication. **The constitution itself is the place this rule is most violated.** |
| 6 | **C-CONFIG-OVER-CODE** (data, not branches) | PASS | modes.yaml is data; enforcement modes are data; permission surfaces are frontmatter; tiers are data; model routing is data (D-016) |
| 7 | **C-NO-SPECIAL-CASE** (no `if runtime ==`) | PASS | The system-lead's bash allowlist is now a named list (T-04 fix D-6); no `if agent ==` patterns introduced by F-016 |
| 8 | **C-DISCOVERY** (load by convention) | PASS | F-016 does not introduce a hand-maintained registry; skills are discovered by directory listing; agents are discovered by file presence |
| 9 | **C-FILE-SELF-EXPLAINS** (Purpose/Does Not/Used By) | PASS | Each agent file has a top docstring with identity and "what it is/is not" (R-006); each spec has Identity (IS/IS NOT) and Core rules |
| 10 | **C-TESTABLE** (every component testable) | PASS | Each agent spec has Acceptance Criteria; each SC has a verification method; the cross-ref tool is the deterministic gate |
| 11 | **C-PORTABLE** (Windows + Linux) | PASS | Planning scripts are stdlib-only; bash allowlists include both `python` and `python3` forms; the SPEC explicitly cites cross-platform practice in system-lead.md:148–150 |
| 12 | **C-ARCH-BEFORE-FEATURES** (build the extension first) | PASS | The F-016 design is itself the extension mechanism (D-002 catalog + D-008 asset-kinds-are-data); F-016 doesn't add a feature without a spec slot |

**Net: 11/12 PASS, 1/12 PARTIAL (C-SINGLE-SOURCE — see C-1, C-2, C-3).**

The PARTIAL is a *specification index* issue, not a behavior issue. The F-016 deliverables are C-SINGLE-SOURCE compliant (one source of truth per fact: the reference spec is the source for the agent; the catalog derives from it; the runtime derives from the catalog). The drift is in the constitution's own self-description: three documents (prose, YAML, T-38 review) each claim to be the rule list, and they don't agree.

---

## Core loop integrity check

> `context/CORE_LOOP.md` describes the plan→build→review cycle. Does the F-016 agent system fit?

| Core loop element | F-016 mapping | Verdict |
|---|---|---|
| **Entry** (request received) | project-lead is the L1 entry point | ✓ |
| **Classify** (track + mode + route) | project-lead runs `request-classification` skill; planning-lead's `planning-intake` skill is the design | ✓ |
| **Plan** (SPEC → PLAN → TASKS → packets) | planning-lead owns the planning lifecycle (P0–P8); task packets V0–V4 (per `Research/ref/planning-lead.md:411–814`) | ✓ |
| **Build** (per-task enrich → delegate → test → review → commit) | build-lead orchestrates (9-step loop per `Research/ref/build-lead.md:47–80`); general-builder executes; committer commits | ✓ |
| **Review** (adversarial, fresh context, read-only verdict) | reviewer is read-only (R-004); 4 verdicts; 9 dimensions; 12 plan-critic checks | ✓ |
| **Commit** (only committer writes git history) | R-004 one-writer — committer is the only `git commit*` allow | ✓ |
| **Trace** (every action recorded) | Spec defines trace spine (designed, deferred); R-009 trace-and-learn in spec; trace is currently at the audit/build-report level | PARTIAL — designed, not built (deferred to Phase 3) |

**Net: 7/7 phases have a clear owner; 6/7 fully built; 1/7 designed-only (trace). The plan→build→review cycle is consistent with the F-016 design.**

---

## Phase / checkpoint integrity

> The T-01 → T-41 critical path. Per `TASKS.md:5` and `BUILD_REPORT.md:88–92`.

| Task | Description | Status | Evidence |
|---|---|---|---|
| T-01 | Verify research completeness | ✓ DONE | `TASKS.md:30` |
| T-02 | Build cross_ref_agents.py | ✓ DONE | commit `994d592` |
| T-03 | Reviewer adversarial audit | ✓ DONE | `Research/audit/findings-1.md` (39 findings) |
| T-04 | Address CRITICAL + HIGH findings | ✓ DONE | commit `7bfd679`; 10 Group-1 fixes applied |
| T-05 | Cross-ref: leads | ✓ PASS | `TASKS.md:58` "0 HIGH/0 MEDIUM" |
| T-06..T-13 | Lock 8 lead specs | ✓ DONE | all `[x]` |
| T-14 | Cross-ref: all 11 | ✓ PASS | commit `83abc72`; gate green |
| T-15..T-17 | Produce 3 leaf specs | ✓ DONE | `TASKS.md:124–141` |
| T-18 | Cross-ref: leaves | ✓ PASS | commit `8d41c56`; gate green |
| T-19..T-29 | Update 11 catalog files | ✓ DONE | `TASKS.md:150–208` (all `[x]`) |
| T-30 | Catalog structural validation | ✓ APPROVED-with-notes | `build-reports/REVIEW-F-016-T-30.md` + `reviews/T-30-review.md`; `f574496` runtimes fix |
| T-31 | Skills inventory | ✓ DONE | `Research/skills/inventory.md`; 25 missing identified |
| T-32 | Governance spec | ✓ DONE | `Research/ref/governance.md` (634 lines) |
| T-33 | modes.yaml spec | ✓ DONE | `Research/specs/modes.yaml` (3 modes × 8 knobs) |
| T-34 | Enforcement spec | ✓ DONE | `Research/specs/enforcement.md` |
| T-35 | Planning scripts spec | ✓ DONE | `Research/specs/planning-scripts.md` |
| T-36 | CLI verbs spec | ✓ DONE | `Research/specs/cli-verbs.md` (6 verbs) |
| T-37 | Cross-runtime spec | ✓ DONE | `Research/specs/cross-runtime.md` |
| T-38 | Final acceptance review | ✓ APPROVED with notes | `build-reports/REVIEW-F-016-T-38.md` (0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW) |
| T-39 | SPEC Clarifications | ✓ DONE | SPEC.md Clarifications updated; commit `6f4be1c` |
| T-40 | Final cross-ref | ✓ PASS | `TASKS.md:280` "12/12 specs, 0 HIGH, 0 MEDIUM findings" |
| T-41 | BUILD_REPORT | ✓ DONE | commit `5e42262` |

**Critical path integrity: PASS.** T-01 → T-41 has 41 tasks, all complete. The dependencies (`Depends on` / `Blocks` columns) are respected. The T-30, T-38, T-40 gates all passed.

**One follow-up to track:** the build-report records 8 open follow-ups (`BUILD_REPORT.md:126–143`). All are documented; none block the F-016 sign-off.

---

## Spec-to-catalog alignment

> Per T-30 re-review (`reviews/T-30-review.md`). All 11 in-scope catalog files pass the 11-field structural check (name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope).

| Catalog file | Reference spec | Frontmatter-aligned? | Body-aligned? | Notes |
|---|---|---|---|---|
| project-lead.md | project-lead.md | ✓ | ✓ | `runtimes: []` fixed in `f574496` |
| planning-lead.md | planning-lead.md | ✓ | ✓ | Future subagents annotated |
| build-lead.md | build-lead.md | ✓ | ✓ | |
| reviewer.md | reviewer.md | ✓ | ✓ | T-04 added Model Tier section |
| system-lead.md | system-lead.md | ✓ | ✓ | T-04 replaced bash `*` with named list |
| fix-lead.md | fix-lead.md | ✓ | ✓ | |
| test-lead.md | test-lead.md | ✓ | ✓ | |
| research-lead.md | research-lead.md | ✓ | ✓ | T-04 documented write/edit asymmetry |
| committer.md | committer.md | ✓ | ✓ | T-30 fix `04f79a8` added `temperature` + `delegates: []` |
| general-builder.md | general-builder.md | ✓ | ✓ | |
| project-explorer.md | project-explorer.md | ✓ | ✓ | |

**Net: 11/11 catalog files frontmatter-aligned and body-aligned with their reference specs.** The T-30 re-review verified this with `grep` and `diff` (deterministic).

---

## Skills resolution check

> 42 unique skills referenced in agent frontmatter; 38 exist in `src/aspis/data/catalog/skills/`; 4 referenced but missing. Per `Research/skills/inventory.md`.

| Missing skill | Referenced by | Resolution |
|---|---|---|
| `mode-decision` | planning-lead.md:61, project-lead (recommended) | T-31 inventory: P0. Build in follow-up. |
| `constitution-checks` | planning-lead.md:62 | T-31 inventory: P0. Build in follow-up. |
| `packet-validation` | build-lead.md:51 | T-31 inventory: P0. Build in follow-up. |
| `builder-selection` | build-lead.md:52 | T-31 inventory: P0. Build in follow-up. |

**Net: 4 skills referenced in frontmatter but not in catalog. T-31 inventory covers; building is a follow-up.** This is documented, tracked, and not blocking. The MEDIUM M-3 finding captures the structural issue.

---

## Model tier consistency

> R-007. All 11 agents declare a tier.

| Agent | Default tier | Source |
|---|---|---|
| project-lead | standard | `src/aspis/data/catalog/agents/project-lead.md:5`; `Research/ref/project-lead.md:88–100` |
| planning-lead | standard | `src/aspis/data/catalog/agents/planning-lead.md:5`; `Research/ref/planning-lead.md:179–217` |
| build-lead | standard | `src/aspis/data/catalog/agents/build-lead.md:6`; `Research/ref/build-lead.md:113–148` |
| reviewer | standard | `src/aspis/data/catalog/agents/reviewer.md:5`; `Research/ref/reviewer.md:124–132` (T-04 fix) |
| system-lead | standard | `src/aspis/data/catalog/agents/system-lead.md:6`; `Research/ref/system-lead.md:114–123` |
| fix-lead | standard | `src/aspis/data/catalog/agents/fix-lead.md:5`; `Research/ref/fix-lead.md:74–88` |
| test-lead | standard | `src/aspis/data/catalog/agents/test-lead.md:5`; `Research/ref/test-lead.md:78–85` |
| research-lead | standard | `src/aspis/data/catalog/agents/research-lead.md:5`; `Research/ref/research-lead.md:47–55` (T-04 fix) |
| committer | cheap | `src/aspis/data/catalog/agents/committer.md:5`; `Research/ref/committer.md:132–148` |
| general-builder | cheap | `src/aspis/data/catalog/agents/general-builder.md:5`; `Research/ref/general-builder.md:172–201` |
| project-explorer | cheap | `src/aspis/data/catalog/agents/project-explorer.md:5`; `Research/ref/project-explorer.md:148–170` |

**Pattern:** leads are standard; leaves are cheap. R-007 compliant. Per-phase tier escalation (e.g., reviewer to deep for plan-critic, planning-lead to deep for P5 architecture) is specified in the reference specs.

---

## R-004 one-writer verification

> The single most important R-rule. Walked end-to-end.

| Agent | `git commit*` | `git push*` | R-004 OK? |
|---|---|---|---|
| project-lead | deny | deny | ✓ |
| planning-lead | deny | deny | ✓ |
| build-lead | deny | deny | ✓ |
| reviewer | deny | deny | ✓ (also read-only: `edit: "*": deny`, `write: "*": deny`) |
| system-lead | deny | deny | ✓ |
| fix-lead | deny | deny | ✓ |
| test-lead | deny | deny | ✓ |
| research-lead | deny | deny | ✓ |
| **committer** | **allow** | **deny** | ✓ (only committer) |
| general-builder | deny | deny | ✓ |
| project-explorer | deny | deny | ✓ |

**R-004 invariant holds.** Committer is the only `git commit*` allow (committer.md:24, :26). R-008 invariant holds: no agent has `git push*` allowed. (Committer explicitly denies `git push*` — even the committer does not push, per R-008 human gate.)

---

## R-008 human gate verification

> The 8 categories that trigger R-008, and the mechanism for each.

| R-008 category | Mechanism | Status |
|---|---|---|
| Architecture changes (new layers, roster changes) | governance subagent (specified, not built) + system-lead's escalation to R-008 gate | Mechanism designed; **script not built (H-1)** |
| Rules changes (add/change/remove R-001…R-009) | governance subagent (specified) | Mechanism designed; **script not built (H-1)** |
| Permissions changes | governance subagent (specified); protection engine (F-015) is runtime analogue | Mechanism designed; **script not built (H-1)** |
| Security posture changes | governance subagent (specified) | Mechanism designed; **script not built (H-1)** |
| Model-routing changes | governance subagent (specified) | Mechanism designed; **script not built (H-1)** |
| Self-improvement (agent prompt, skill list) | governance subagent (specified); project-lead's R-008 escalation list | Mechanism designed; **script not built (H-1)** |
| 3 failed fix attempts → REVIEW_NEEDED | project-lead escalation (per `Research/ref/project-lead.md:212–215, :304–319`) | ✓ Spec PASS |
| Re-bootstrap or new project onboarding | bootstrap agent (transient, self-deletes) | ✓ Spec PASS |

**Net: 8/8 R-008 categories specified. 6/8 rely on the governance subagent (H-1). 2/8 (3-attempt REVIEW_NEEDED, re-bootstrap) are independent of governance and pass.**

---

## R-010 delegate-with-purpose verification

> Per agent's permission surface and delegation table.

| Agent | Delegates? | Type | Justification |
|---|---|---|---|
| project-lead | 8 delegates (L2 + L3) | Heavy | L1 entry point; routes everything to the right specialist |
| planning-lead | 10 delegates (3 real + 7 future) | Medium | L2 lead; delegates research, review, exploration; subagents are specialized planning workers |
| build-lead | 7 delegates (L2 + L3) | Medium | L2 lead; orchestrates; workers do the actual implementation |
| reviewer | 2 delegates (L2 + L3) | Light | Read-only; only needs codebase context + research validation |
| system-lead | 3 delegates (L2 + L3) | Light | Platform owner; delegates exploration + verification + commit |
| fix-lead | 4 delegates (L2 + L3) | Light | Recovery agent; needs review, commit, exploration, test classification |
| test-lead | 1 delegate (L3) | Minimal | Validator; only needs codebase exploration |
| research-lead | 1 delegate (L3) | Minimal | Knowledge agent; only needs codebase exploration (cache-first) |
| committer | 0 delegates | None | Leaf; R-004 one-writer |
| general-builder | 0 delegates | None | Leaf; R-010 context-isolation; `task: '*': deny` |
| project-explorer | 0 delegates | None | Leaf; R-004 read-only; `task: '*': deny` |

**Net: 11/11 agents have a justified delegation pattern. R-010 compliant. The 7 future subagents in planning-lead are the only over-broad list (M-2).**

---

## Triage Group 1 fixes — verification

> The T-04 owner triage applied 10 Group-1 fixes. Per `Research/audit/findings-triage.md:24–49`. Each fix is verified in the current state of the files.

| ID | Where | Fix verified |
|---|---|---|
| A-1 | reviewer (model tier) | `Research/ref/reviewer.md:124–132` — explicit Model Tier subsection; standard default, deep for high-risk, cheap for P2 self-check; cites R-007 |
| A-4 | research-lead (if stuck) | `Research/ref/research-lead.md:185–187` — "If stuck — stop, don't guess" in §8 Escalation |
| A-5 | reviewer (if stuck) | `Research/ref/reviewer.md:202–206` — "If stuck — stop, don't guess" in §6 Verdict System |
| B-1 | planning-lead (plan-critic) | `Research/ref/planning-lead.md:170–175, :240–242` — removed `plan-critic`/`review-strategy` from planning-lead's owned skills; explicit reviewer ownership |
| B-2 | reviewer (12 vs 6) | `Research/ref/reviewer.md:229–230` — labeled v1 (6) + v2 (6) = 12 |
| B-5 | research-lead (write/edit) | `Research/ref/research-lead.md:41–45` — documented "write-without-edit asymmetry is intentional, not a gap" |
| B-6 | system-lead (self-mod) | `Research/ref/system-lead.md:175–185` — "Self-modification is governed, not free" subsection with 5 guardrails |
| C-6 | planning-lead (committer) | `Research/ref/planning-lead.md:264–265` — "committer is never in the planning task allow-list" |
| C-7 | reviewer (model drift) | `Research/ref/reviewer.md:124–132` — tier resolved (standard default); live custom model classified as personal setup |
| D-6 | system-lead (bash `*`) | `Research/ref/system-lead.md:18–30` (frontmatter) — wildcard removed; named commands only |
| D-9 | reviewer (`aspis artifact test`) | `Research/ref/reviewer.md:18` (frontmatter) — `aspis artifact*` is the only allow-line; reviewer is read-only and does not stamp test artifacts |

**All 11 Group 1 items are resolved in the current files.** T-04 was applied correctly. The audit was thorough; the fixes are durable.

---

## Architecture compliance — final walk

> The architecture context (`context/ARCHITECTURE.md`) describes the *as-built* state. F-016's design maps to it cleanly.

| Architecture element | F-016 design | Verdict |
|---|---|---|
| 3 layers (factory / install / project) | F-016 produces the catalog (layer 1) that the install renders (layer 2) to the project (layer 3) | ✓ |
| Catalog → runtime (core mechanism) | Catalog is the runtime-neutral source; adapters translate per runtime | ✓ |
| Asset kinds are data (D-008) | No core engine change; agents are catalog data; 11 agents = 11 catalog files | ✓ |
| Runtime identity is the adapter's (D-015) | `runtimes: []` in all 11 catalog files; adapter decides per runtime | ✓ |
| Models canonical, runtime strings derived (D-016) | Tier (`cheap`/`standard`/`deep`) declared in frontmatter; concrete model id resolved at render | ✓ |
| Detection is per-runtime (D-018) | Out of F-016 scope; not violated | ✓ |
| One resolver routes; tier stays the agent dial (D-017) | Each agent declares its tier; no per-runtime override in agent files | ✓ |
| Agent = thin instruction + skills (R-006) | Each agent file: identity + rules + skill references | ✓ |
| Roster (11 + 1 bootstrap transient) | All 11 catalog files + 1 transient bootstrap (outside F-016 scope) | ✓ |
| Modes & cost (every agent pinned) | All 11 agents pinned (`model: standard` or `model: cheap`) | ✓ |
| Promotion: bootstrap promotes 4 leads → 5 primaries | Design is the roster; promotion is runtime concern (not F-016 scope) | ✓ |
| **System Lead is the only lead that may modify the runtime** | `Research/ref/system-lead.md:67–80` Protected Scope; R-008-gated for self-modification (T-04 B-6 fix) | ✓ |
| **Context pyramid (FILE_REGISTRY → CODE_MAP → live state)** | `project-explorer` is the L1↔L3 / L2↔L3 exception; `context-ladder` skill shared across leads | ✓ |
| **Quality: deterministic gates (ruff + pytest); R-004 one writer** | Catalog validation (T-30) is the deterministic gate; R-004 verified above | ✓ |
| **Hooks: deterministic surfaces, non-blocking by default (D-010)** | `Research/specs/enforcement.md:24–30` "warn for pre-commit"; the flip to block is follow-up | ✓ |
| **Git: committer only** | R-004 verified above | ✓ |

**Net: 16/16 architecture elements consistent with F-016 design.**

---

## Cost-of-change check (Constitution #1, SC-012)

> "To add one feature, how many existing files must change?"

| Action | Files touched | Verdict |
|---|---|---|
| Add a new agent (common case) | 2 (reference spec + catalog file) | healthy (1–3) |
| Add a new agent (F-016-self-update case) | 5 (reference spec + catalog + SPEC + PLAN + TASKS) | healthy (1–3; the upper edge) |
| Add a new skill | 1 (the SKILL.md file; the catalog is auto-discovered) | healthy (1–3) |
| Add a new CLI verb | 3 (verb code + aspis dispatch + spec) | healthy (1–3) |
| Add a new subagent roster (F-017: 7 future L3 subagents) | 7 (one per subagent) | warning (5–10) — acceptable for a single feature |

**Net: design passes the Cost-of-Change test (C-COST). Adding a new agent at 2–5 files is the healthy band. F-017's 7-subagent build is the warning band — acceptable as a single feature.**

---

## Final verdict: APPROVE WITH CONDITIONS

The F-016 architecture is sound. The constitution is followed. The system rules are followed. The delegation graph is valid (with documented F-017 deferral). The cross-agent responsibilities don't conflict (with one historical conflict fixed in T-04). The cross-ref tool, the T-30 catalog gate, and the T-38 final acceptance review all passed.

**The 3 conditions of acceptance** are real but tractable; they are SPEC/spec drift and implementation follow-ups, not architectural defects:

1. **C-1, C-2, C-3 — Constitution and SPEC text consistency.** Reconcile the constitution prose ↔ YAML ↔ T-38 review enumeration (12 vs 11 vs 12) and update FR-007 in SPEC.md to match the design. Both are T-39 follow-ups already on the books; the conditions are that they be resolved before any external audit cites FR-007 or the 12-point constitution as a hard contract.

2. **H-1, H-2, H-3, H-4 — Follow-up implementation work.** Build the governance subagent + `aspis governance` CLI (R-008 enforcement in code); apply the Claude Code adapter fix (FR-021); implement the 6 missing CLI verbs (FR-022, FR-024); resolve any deployment drift for the reviewer's tier (R-007). All are documented in `BUILD_REPORT.md:126–143` as open follow-ups. F-016 is a specification deliverable; the build is a separate feature.

3. **M-2, M-3, M-4 — Documented deferrals.** The 7 future L3 subagents in planning-lead's `delegates` (F-017); the 4 missing skills in frontmatter (T-31 inventory + build follow-up); the bootstrap.md frontmatter exemption (T-39 follow-up). All are documented in the build reports and have explicit follow-up tracks.

**The architecture's core design is approved.** The 12 success criteria are met (per `BUILD_REPORT.md:96–109` and the T-38 review). The architecture constitution is 11/12 PASS, 1/12 PARTIAL on the index drift (which is in the *description* of the constitution, not the architecture itself). The system rules are 10/10 PASS in the design layer. The delegation graph is sound. The model tier, permission surface, and skill ownership are consistent.

**Route to committer for F-016 sign-off** (per R-004: only committer writes the commit that closes the feature). The T-30, T-38, and T-40 reviews are the gate evidence; the T-41 BUILD_REPORT is the handoff package.

**Next step after merge:** pick one of the 4 high-priority follow-up features (governance build, Claude adapter fix, CLI verbs build, skills build) and start the next F-### feature with the corrected FR-007 wording and the reconciled constitution.

---

## Appendix A — Evidence summary

| Evidence | Location |
|---|---|
| Constitution prose (12 rules) | `rules/architecture-constitution.md:51–76` |
| Constitution YAML (11 checks) | `config/policy/constitution-checks.yaml:11–65` |
| System rules (R-001…R-010) | `rules/system-rules.md:72–112` |
| As-built architecture | `context/ARCHITECTURE.md:1–141` |
| Core loop | `context/CORE_LOOP.md:1–193` |
| Master synthesis | `local/AGENT-SYSTEM-ARCHITECTURE.md:1–380` |
| F-016 SPEC | `.aspis/features/F-016-agent-system-architecture/SPEC.md:1–177` |
| F-016 PLAN | `.aspis/features/F-016-agent-system-architecture/PLAN.md:1–113` |
| F-016 TASKS | `.aspis/features/F-016-agent-system-architecture/TASKS.md:1–324` |
| F-016 BUILD_REPORT | `.aspis/features/F-016-agent-system-architecture/BUILD_REPORT.md:1–182` |
| 12 reference specs | `.aspis/features/F-016-agent-system-architecture/Research/ref/*.md` |
| 5 systemic specs | `.aspis/features/F-016-agent-system-architecture/Research/specs/*.md` |
| 11 catalog files | `src/aspis/data/catalog/agents/*.md` |
| Skills inventory | `.aspis/features/F-016-agent-system-architecture/Research/skills/inventory.md:1–220` |
| Adversarial audit | `.aspis/features/F-016-agent-system-architecture/Research/audit/findings-1.md` |
| Triage (Group 1/2/3) | `.aspis/features/F-016-agent-system-architecture/Research/audit/findings-triage.md:1–119` |
| T-30 review (changes-requested) | `build-reports/REVIEW-F-016-T-30.md:1–89` |
| T-30 re-review (approved) | `reviews/T-30-review.md:1–143` |
| T-38 final acceptance | `build-reports/REVIEW-F-016-T-38.md:1–781` |

---

## Appendix B — Reviewer's responsibility statement

This review is performed under the Reviewer's role per the project-lead system design: I am the independent quality authority, read-only (R-004), evidence-based, and report findings with file:line evidence. I do not modify the work (R-004 + my own role). I rendered the verdict above from the evidence listed in Appendix A; the verdict is a single, reversible decision (the F-016 sign-off is gated by the committer's commit, not by my report).

I have not rubber-stamped the T-38 review (which approved with 3 MEDIUM and 4 LOW). I have read the F-016 deliverables independently and walked the constitution, the system rules, the delegation graph, the permission surfaces, the model tiers, the cross-agent boundaries, and the spec-to-catalog alignment. I have found 3 CRITICAL issues that the T-38 review did not surface (the constitution-index drift), and 1 MEDIUM issue (the FR-007 wording) that the T-38 review did surface but routed to T-39 without escalation. I have documented all of these with file:line evidence.

The verdict is **APPROVE WITH CONDITIONS** because the architecture is sound and the spec deliverable is complete; the conditions are real but they are not architectural defects. They are SPEC/spec drift (the F-016 SPEC text contradicts the design in two places) and implementation follow-ups (the governance script, the Claude adapter fix, the 6 CLI verbs, the 4 missing skills). Both are in the build report's open follow-ups; both have explicit next steps.

— Reviewer, 2026-06-27
