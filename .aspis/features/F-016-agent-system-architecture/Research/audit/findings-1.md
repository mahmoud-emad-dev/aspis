# F-016 Adversarial Audit — Findings Report #1

**Audit date:** 2026-06-27
**Scope:** All 8 lead reference specs at `.aspis/features/F-016-agent-system-architecture/Research/ref/`
**Method:** Adversarial review against the 12-rule architecture constitution, the 9 system rules (R-001…R-009), the master synthesis `local/AGENT-SYSTEM-ARCHITECTURE.md`, the F-016 SPEC requirements (FR-001…FR-028), and cross-agent consistency (no overlapping roles, no orphaned delegation edges).
**Reviewer stance:** Assume every spec has hidden issues; every claim needs evidence; nothing is correct until proven.

---

## Summary

| Severity | Count | Meaning |
|---|---|---|
| **CRITICAL** | 7 | Blocks ship of F-016; spec is non-compliant with its own SPEC or with system rules |
| **HIGH** | 13 | Spec gap that violates FR-### or R-###; requires fix before F-016 sign-off |
| **MEDIUM** | 14 | Spec inconsistency, missing section, or weak acceptance criterion |
| **LOW** | 5 | Style / naming / minor inconsistency; should be fixed in passing |
| **INFORMATIONAL** | 10 | Verifications that passed (universal denies, no orphaned edges, etc.); no defect |
| **TOTAL** | **49** | |

(Counts of 7 + 13 + 14 + 5 = 39 are unique findings after de-duplication of cross-references between per-dimension and detailed tables. The detailed table at the end of this report contains 43 numbered finding rows, of which 4 are explicit cross-references to other findings — see "Detailed Findings".)

**Cross-ref baseline:** `python .aspis/scripts/planning/cross_ref_agents.py --scope leads` already reported 1 MEDIUM + 9 LOW overlap findings. This adversarial review identifies **30+ additional findings** (7 CRITICAL, 13 HIGH, 14 MEDIUM, 5 LOW) not caught by the cross-ref tool, plus 10 INFORMATIONAL verifications.

**Verdict:** **FAIL.** Multiple CRITICAL and HIGH findings require remediation before the F-016 plan is shippable to build-lead.

---

## A. Structural Completeness

The audit's "structural completeness" axis checks each spec against the 11-element template required by the F-016 SPEC (FR-002). A spec is **conformant** if it has all of: Identity (IS / IS NOT), Responsibilities→Skills, Model Tier, Permission Surface, Delegation Map, ≥10 Use Cases, Anti-Patterns, Error Handling, Acceptance Criteria, Open Design Questions, "If stuck — don't guess" rule.

### A.1 — Section inventory

| Spec | Identity | Resp→Skills | Model Tier | Permission | Delegation | Use Cases | Anti-Patterns | Error Handling | Acceptance | Open Design | "If stuck" rule | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| project-lead | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (150+) | ✓ | ✓ | ✓ | ✓ | ✓ | 11/11 |
| planning-lead | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (110+) | ✓ | ✓ | ✓ | ✓ | ✓ | 11/11 |
| build-lead | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (89) | ✓ | ✓ | ✓ | ✓ | ✓ | 11/11 |
| **reviewer** | ✓ | ✓ | **✗ MISSING** | ✓ | partial (task table only) | ✓ (81) | ✓ | **✗ MERGED into "Edge Cases"** | ✓ | ✓ | **✗ MISSING** | 7/11 |
| system-lead | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (47) | partial (no dedicated §, anti-patterns embedded in REJECT table) | ✓ | ✓ | ✓ | ✓ | 10/11 |
| **fix-lead** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (45) | ✓ | **✗ embedded in lifecycle, not a matrix** | ✓ | ✓ | ✓ | 10/11 |
| **test-lead** | ✓ | ✓ | ✓ | ✓ | partial (only one delegate, no full map) | ✓ (37) | ✓ | **✗ only "Escalation" §, no error matrix** | ✓ | ✓ | ✓ | 8/11 |
| **research-lead** | ✓ | partial (no table, only listed in §2) | partial (tier mentioned but not in dedicated §) | ✓ | partial (only project-explorer, not a full map) | ✓ (32) | ✓ | **✗ only "Escalation" §, no error matrix** | ✓ | ✓ | **✗ MISSING** | 6/11 |

### A.2 — Per-spec findings

#### Finding A-1 — reviewer.md is missing the "Model Tier Strategy" section — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 94–125 (section 4 jumps from "Permission Surface" directly to "The 9 Review Dimensions")
**Severity:** CRITICAL
**What's wrong:** The reviewer spec has no dedicated "## 4 · Model Tier Strategy" section. The agent's own "Open Design Questions" (line 351) only treats tier as a *drift problem* (live `minimax-m3` cheap vs config `deepseek-v4-pro` deep) without declaring a default tier for the reviewer itself. R-007 ("Pinned models: every agent declares an explicit model tier") and FR-005 ("Every agent MUST declare a model tier … consistent with the tier strategy and its role's cognitive demands") are violated. The spec references tier in many places (cheap, standard, deep in §11 subagents and §5 9 dimensions) but never commits to the reviewer's own default.
**Why it matters:** R-007 is non-negotiable. The reviewer is the most important judgment agent in the system (verdict rendering); a missing tier means the spec contradicts its own system rules.
**Suggested fix:** Add `## 4 · Model Tier Strategy` between Permission Surface and "The 9 Review Dimensions". State "Reviewer: standard tier (default). Deep tier for V3-V4 / security / architecture reviews. Cheap tier for P2 self-checks. Per-dimension tier mapping." Cite R-007.

#### Finding A-2 — test-lead.md is missing the "Error Handling Matrix" section — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/test-lead.md`
**Lines:** 156–168 (section 9 is titled "Escalation" — no error matrix)
**Severity:** HIGH
**What's wrong:** Section 9 is named "Escalation" and lists where to route situations. There is no `## N · Error Handling` table showing failure → catcher → fixer → review, like the one in project-lead.md §12 or planning-lead.md §16. The other leads all have an explicit error-handling matrix; test-lead does not.
**Why it matters:** FR-002 lists "error handling" as a required section. Spec consistency requires the same structure across all 8 leads so the planning/build leads can copy the same template.
**Suggested fix:** Add a new `## 10 · Error Handling Matrix` (renumber subsequent sections) with rows for: pytest environment failure, ledger corruption, classification disagreement, builder test list diverges, etc.

#### Finding A-3 — research-lead.md is missing section 10 — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md`
**Lines:** 145–192 (sections jump 9 → 11; §10 is missing)
**Severity:** HIGH
**What's wrong:** Section numbering skips from `## 9 · Anti-Patterns` to `## 11 · Full Use Case Catalog`. Section 10 is missing. The "Anti-Patterns" section is §9; the next section should logically be a missing "Escalation" or "Cache Management" section. Looking at the content, it appears the missing section was originally "Subagent Details" or similar, accidentally deleted.
**Why it matters:** Numbered sections that skip values indicate either deleted content or a documentation bug. Either way it is a structural defect.
**Suggested fix:** Renumber the sections: §9 Anti-Patterns, §10 Subagent Details (extract from current §7/§13), §11 Full Use Case Catalog, §12 Adversarial Findings, §13 Skills/Tools/Subagents Inventory, §14 Acceptance Criteria.

#### Finding A-4 — research-lead.md is missing the "If stuck, stop — don't guess" rule in its body — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md`
**Lines:** 12 (identity), 173 (escalation table), 251 (adversarial findings), 327 (acceptance criteria)
**Severity:** CRITICAL
**What's wrong:** The spec's own §12 "Adversarial Findings" lists "**No "if stuck" rule — documented gap against system-wide doctrine | HIGH**" (line 251) as one of its top risks — but the spec never adds the rule. Every other spec has it: project-lead.md:847, planning-lead.md:1104, build-lead.md:566, fix-lead.md:227, test-lead.md:271, system-lead.md:440. The system-wide doctrine is universal; research-lead is the only subagent with both webfetch and websearch — a domain where getting stuck is most likely (3 web-tool failures, paywalled content, conflicting sources).
**Why it matters:** Self-documented gap, classified HIGH by the spec itself, that ships unfixed. Violates the cross-agent consistency rule that the "if stuck" rule is universal.
**Suggested fix:** Add a row to the §8 Escalation table: `Stuck after 3 web-tool failures / conflicting sources / paywalled content → STOP, hand back to delegating lead, do not guess. Cite R-003 + R-009.` Also add to §14 acceptance criteria.

#### Finding A-5 — reviewer.md is missing the "If stuck, stop — don't guess" rule — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 1–386 (no "if stuck" reference found)
**Severity:** CRITICAL
**What's wrong:** Despite reviewer's adversarial doctrine ("assume every plan has gaps, every change has issues") and §6 "No evidence = no verdict" rule, the spec never explicitly codifies "if stuck, stop — don't guess". Compare to all other specs which have the rule in their Error Handling or Escalation section.
**Why it matters:** The reviewer is the system-wide adversary; if it guesses when stuck, it injects false verdicts. Cross-agent consistency is broken.
**Suggested fix:** Add to §6 Verdict System or §10 Anti-Patterns: "If stuck (e.g., no evidence, contradictory inputs, dimension out-of-scope), STOP. Withhold verdict. Report to delegating lead. Do not guess." Cite R-007 / R-009.

#### Finding A-6 — test-lead.md uses only "Escalation" instead of a proper Error Handling section — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/test-lead.md`
**Lines:** 156–168
**Severity:** MEDIUM
**What's wrong:** Section 9 is "Escalation" — a list of routes for situations. It conflates errors and escalations. The system-wide convention is two separate sections: an "Error Handling Matrix" (failure → catcher → fixer → review) and an "Escalation" (when to hand back). Test-lead has only the latter.
**Suggested fix:** Rename §9 → "Escalation", add new §10 "Error Handling Matrix" with the standard rows (test infra failure, ledger poisoning, classification disagreement, etc.).

#### Finding A-7 — fix-lead.md has error handling embedded in lifecycle, not as a separate matrix — LOW

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/fix-lead.md`
**Lines:** 34–58 (the 6-step spine), 130–143 (3-attempt cap), 538–553 (Error Handling section is missing — search confirms no `## 12 · Error Handling`)
**Severity:** LOW
**What's wrong:** Fix-lead lists 12 sections (per the cross_ref), so by spec count it's complete, but the actual error handling is scattered across the lifecycle + 3-attempt cap sections rather than a dedicated matrix.
**Suggested fix:** Add a §12 "Error Handling Matrix" following the project-lead/planning-lead format.

#### Finding A-8 — research-lead.md has no dedicated "Delegation Map" section — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md`
**Lines:** 7 (Subagents), 145–161 (the "Subagents" section)
**Severity:** MEDIUM
**What's wrong:** Section 7 is "Subagents" but the structure is "current / future" — there is no clear "Receives from / Sends to" table like fix-lead.md §9. The master synthesis requires a "Delegation Map" section for every agent.
**Suggested fix:** Add `## 5 · Delegation Map` with "Receives from" (project-lead, planning-lead, build-lead, reviewer, fix-lead, system-lead) and "Sends to" (delegating lead, project-explorer, future subagents). Renumber subsequent sections.

#### Finding A-9 — test-lead.md has only one line of "Task delegation" and no full map — LOW

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/test-lead.md`
**Lines:** 100–101
**Severity:** LOW
**What's wrong:** Section 5 lists only `project-explorer` as a delegate, with no "Receives from" and no per-delegate profiles. Compare to fix-lead.md §9 with both directions and per-delegate watch-outs.
**Suggested fix:** Add a proper `## 6 · Delegation Map` with Receives-from / Sends-to.

---

## B. Architecture Constitution Compliance

The audit checked each spec against the 12 rules in `.aspis/rules/architecture-constitution.md`. The most load-bearing rules for a *specification* (as opposed to product code) are: C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-NO-SPECIAL-CASE, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-COST, C-PORTABLE.

### B.1 — Per-spec findings

#### Finding B-1 — planning-lead.md section §2.7 references skills that are in reviewer's domain — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/planning-lead.md`
**Lines:** 156–172 (Skills NOT in planning-lead's set), 167–168 (Recommended skill additions)
**Severity:** HIGH
**What's wrong:** §4 "Recommended skill additions" says: `plan-critic` and `review-strategy` are "Critical" priority to add to planning-lead's allow-list — yet §4 itself, just above, lists both skills as belonging to "reviewer". This contradicts the spec's own boundary claim ("Review is reviewer's domain"). §10 (Procedural Flow P7 Plan Review) delegates plan-critic to reviewer. So planning-lead would own a skill it doesn't use.
**Why it matters:** Violates C-SINGLE-SOURCE (skill ownership) and creates an orphaned/duplicated skill ownership.
**Suggested fix:** Remove `plan-critic` and `review-strategy` from planning-lead's recommended additions; cite reviewer.md as the owner. Move the table out of planning-lead entirely, or convert it to a cross-reference of skills planning-lead *consumes* (referencing reviewer.md as owner).

#### Finding B-2 — reviewer.md conflicts on plan-critic ownership — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 56, 79, 199 (plan-critic as a reviewer skill, with 12 checks), 351 (open design: "6 missing plan-critic checks")
**Severity:** HIGH
**What's wrong:** Section 7 "Plan Review (Plan-Critic)" lists 12 checks in a complete table. But the Open Design Questions #3 (line 351) says "6 missing plan-critic checks — extend from 6 to 12" — i.e., the spec simultaneously claims 12 checks exist and 6 are missing. Internal contradiction.
**Why it matters:** C-SINGLE-SOURCE / C-FILE-SELF-EXPLAINS. The reader cannot determine which is the ground truth without re-reading the spec twice.
**Suggested fix:** Either (a) move the 6 "missing" checks into a separate "Plan-critic v2" sub-table to clarify they are an extension, or (b) explicitly mark which 6 of the 12 are aspirational and which are existing. The spec already has the structure to do this — just label them.

#### Finding B-3 — system-lead.md has no explicit constitution compliance section — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/system-lead.md`
**Lines:** 1–452 (no 12-rule check section)
**Severity:** MEDIUM
**What's wrong:** Planning-lead.md §11 has a "Constitution compliance (12 rules)" subsection listing the rules. Project-lead.md §13 has "Core Rules Project-Lead Enforces". System-lead has neither — only an internal "Config tier model" and a vague "Architecture constitution (D-009) — machine-readable" mention in the OLD ASPS comparison.
**Why it matters:** System-lead is the *owner* of constitution-checks.yaml. The spec should describe *which* of the 12 rules it enforces vs consumes. FR-028 requires checking the 12 rules against the design.
**Suggested fix:** Add a `## 15 · Constitution Compliance` section enumerating which of the 12 rules system-lead enforces (C-PLUGIN-FIRST via assets profile, C-SINGLE-SOURCE via catalog, C-NO-SPECIAL-CASE via runtime adapters, etc.) and which it only consumes.

#### Finding B-4 — fix-lead.md and test-lead.md lack any constitution compliance section — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/fix-lead.md`, `Research/ref/test-lead.md`
**Lines:** (absent in both)
**Severity:** MEDIUM
**What's wrong:** Neither fix-lead nor test-lead has a section enumerating which of the 12 constitution rules they enforce or check. The rules are silently consumed but not declared.
**Why it matters:** FR-028 ("12-point architecture constitution MUST be checked against the agent system design") and R-006 ("Thin agents, single source — state each fact once") require explicit declaration.
**Suggested fix:** Add a "Constitution Compliance" or "Rules This Agent Enforces" subsection to each.

#### Finding B-5 — research-lead.md has "write: allow" but "edit: deny" — contradiction with §13 inventory — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md`
**Lines:** 38–45 (Permission Surface — Identity section), 264–283 (Skills, Tools & Subagents Inventory)
**Severity:** HIGH
**What's wrong:** §1 lists the permission surface as `write: allow (packaged references only), edit: deny`. But the spec needs to write reference files (RESEARCH_NOTE.md, OFFICIAL_REFERENCES.md). The justification "write without edit" is listed in §12 adversarial findings #14 as a MEDIUM issue (cache fragmentation). The spec documents the contradiction without resolving it.
**Why it matters:** C-SINGLE-SOURCE and C-PLUGIN-FIRST demand clean boundaries. A research-lead with `edit: deny` must delete-and-recreate files to update them, which is hostile to file-system history and atomicity.
**Suggested fix:** Either (a) allow both write+edit, with scope to `Research/` paths only, or (b) justify the asymmetry in writing (it currently lives only in the adversarial-findings table, not the permission surface section).

#### Finding B-6 — system-lead.md says "the only lead that may modify .opencode/, .claude/, and protected .aspis/" — but also says it can edit its own agent file — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/system-lead.md`
**Lines:** 17 (Identity), 142–152 (CRITICAL WARNING: Self-Modification Risk)
**Severity:** CRITICAL
**What's wrong:** §1 declares system-lead is "the **only** lead that may modify `.opencode/`, `.claude/`, and protected `.aspis/`". §5 (Permission Surface) includes its own agent file in edit scope. The §5 warning then admits: "System-lead can edit its own agent file. Can edit the committer's permissions. Can disable hooks. Can change any config." This is a direct contradiction with §1 — the "only lead" rule is broken by §5's own admission.
**Why it matters:** Violates C-SINGLE-SOURCE (the "only authority" claim) and the R-008 human-gate doctrine. The spec ships a known fatal flaw (self-modification) and treats it as a "warning" rather than a blocker.
**Suggested fix:** The spec must not declare system-lead as "the only lead" if it can self-modify. Either (a) add a sub-claim "system-lead is the only lead that may modify runtime files *without R-008 approval*" and route self-modification through the governance subagent, or (b) drop the "only" claim and accept that the governance subagent owns the rule.

#### Finding B-7 — No spec explicitly addresses C-PORTABLE — MEDIUM

**File:** All 8 specs
**Lines:** Cross-cutting
**Severity:** MEDIUM
**What's wrong:** Rule 12 of the architecture constitution ("Portable by Default: every script and tool runs on Windows and Linux; UTF-8 on stdio; pathlib over string paths; no console-codec assumption") is not addressed in any spec. Planning-lead.md and project-lead.md bash allowlists include both `python` and `python3` patterns (lines 134–135 of project-lead.md, 234–237 of planning-lead.md), which is one portable practice. But none of the specs state C-PORTABLE as a constraint on scripts the agent invokes or templates it produces.
**Why it matters:** FR-028 requires checking the 12 rules. Silent omission is a compliance gap.
**Suggested fix:** Add a one-line note to each spec's "Universal denies / bash allowlist" section: "All scripts must be C-PORTABLE compliant (UTF-8, pathlib, cross-platform)."

---

## C. System Rules Compliance

The audit checked each spec against R-001…R-009 from `.aspis/rules/system-rules.md`.

### C.1 — Per-spec findings

#### Finding C-1 — fix-lead.md cites R-001, R-004, R-005 only; omits R-002, R-006, R-007, R-008, R-009 — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/fix-lead.md`
**Lines:** 14, 29, 97, 190, 223 (only 5 R-### references found, all of R-001/R-004/R-005)
**Severity:** HIGH
**What's wrong:** Fix-lead's spec should cite or address R-002 (gates first — run gate before declaring done), R-006 (thin agents, single source), R-007 (pinned models — declaration of own tier), R-008 (human gate — protected paths), R-009 (trace and learn). It only cites R-001 (scope), R-004 (one writer), R-005 (tests-as-spec). R-002 is implicit but never stated.
**Why it matters:** R-006 ("State each fact once and reference it — don't duplicate") requires explicit citation of the rules the agent enforces. Silent omission defeats the traceability purpose.
**Suggested fix:** Add a `## 13 · Core Rules Fix-Lead Enforces` (or expand §10 anti-patterns) table mapping each R-### to how fix-lead enforces it (e.g., R-002: gate is run before FIX_REPORT is written; R-008: protected-path fixes escalated to system-lead before edit).

#### Finding C-2 — test-lead.md cites R-004, R-005, R-008 only; omits R-001, R-002, R-006, R-007, R-009 — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/test-lead.md`
**Lines:** 29, 30, 93, 111, 144, 162, 167, 266 (R-004, R-005, R-008 only)
**Severity:** HIGH
**What's wrong:** Same pattern as C-1. R-001 (test-lead should not write product code), R-002 (run gate before reporting), R-006 (thin agents), R-007 (pinned models — own tier), R-009 (trace and learn) are not cited. R-001 is implicit ("writes tests, not product code" in identity) but not stated.
**Why it matters:** Same as C-1.
**Suggested fix:** Add a "Core Rules Test-Lead Enforces" table.

#### Finding C-3 — research-lead.md cites R-001, R-004, R-008 only; omits R-002, R-005, R-006, R-007, R-009 — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md`
**Lines:** 28, 31, 75, 167, 168, 273, 336 (only R-001, R-004, R-008)
**Severity:** HIGH
**What's wrong:** Research-lead should cite R-005 (tests-as-spec — research findings are not tests, but the principle of "evidence" applies), R-006 (thin agents), R-007 (pinned models), R-009 (trace and learn — research artifacts ARE the trace). None are addressed.
**Why it matters:** Same as C-1.
**Suggested fix:** Add a "Core Rules Research-Lead Enforces" table.

#### Finding C-4 — reviewer.md is missing its own rule-enforcement declaration — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 1–386 (no "Core Rules" or "Enforcement" table)
**Severity:** MEDIUM
**What's wrong:** Project-lead.md §13 has a "Core Rules Project-Lead Enforces" table. Reviewer.md has no equivalent. The reviewer is the *primary enforcer* of R-002 (gates first — it rejects changes with red gates), R-005 (tests-as-spec), and the constitution. The spec describes the *what* (4 verdicts, 9 dimensions) but not the *rule mapping*.
**Suggested fix:** Add `## N · Core Rules Reviewer Enforces` mapping R-002, R-005, R-007, R-008, R-009 to specific review dimensions and verdicts.

#### Finding C-5 — enforcement mode (warn vs block) is documented in only 2 of 8 specs — HIGH

**File:** All 8 specs
**Lines:** Cross-cutting
**Severity:** HIGH
**What's wrong:** F-016 SPEC FR-020 requires: "Enforcement mode MUST be specified: `block` for runtime tools (Edit/Write), `warn` for pre-commit hooks, CI override via `ASPIS_ENFORCEMENT=block`." This is documented in detail only in system-lead.md §8 (lines 246–254). Build-lead.md §13 #2 mentions it as an open design question. The other 6 specs do not mention it. Project-lead.md §7 mentions "warn, don't block" only for preflight.
**Why it matters:** FR-020 is a system-wide policy. It must appear in every spec that touches protected paths or has edit/write scope, because those specs need to know which mode is active when they issue edits. R-008 (human gate) is meaningless if enforcement is `warn` everywhere.
**Suggested fix:** Add a one-line note to each spec's "Permission Surface" section: "Enforcement mode: `block` for Edit/Write on protected paths (system-lead §8). `warn` for pre-commit hooks. CI override: `ASPIS_ENFORCEMENT=block`."

#### Finding C-6 — planning-lead.md's open design #4 says "committer in live task allow-list — remove" — implies the spec is shipping a known violation — HIGH

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/planning-lead.md`
**Lines:** 1115 (Open Design #4), 1139 (acceptance criterion "committer removed from task allow-list")
**Severity:** HIGH
**What's wrong:** The spec ships with `committer` removed from the task allow-list (line 240: "committer is NOT in the task allow-list"). But the Open Design #4 flags that the *live* version still has it. The acceptance criterion #1139 says "committer removed from task allow-list". This is a known *deployed* violation that the spec documents as a fix to be done later.
**Why it matters:** The spec is the "target design" (per the frontmatter of every spec) but ships with a known live-vs-catalog drift. R-006 (single source) is violated because the live state is the truth in production but the spec is the truth on paper.
**Suggested fix:** Make the "Must fix" → "Fix at PLAN handoff" with a specific FR-### tie-in. Currently the language is ambiguous about whether the spec is *deployed* or *aspirational*.

#### Finding C-7 — reviewer.md's open design #1 says "Model drift: live minimax-m3 (cheap) vs config deepseek-v4-pro (deep)" — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 351 (Open Design #1)
**Severity:** CRITICAL
**What's wrong:** The reviewer spec ships with a documented model drift that is left unresolved. The fix is `aspis models --apply`. R-007 (pinned models — every agent declares an explicit model tier, no agent silently inherits an expensive model) is fundamentally violated by the reviewer itself.
**Why it matters:** The reviewer is the system-wide quality gate. A reviewer with the wrong model means every verdict is potentially wrong. The spec cannot claim R-007 compliance when it explicitly documents drift.
**Suggested fix:** Mark as P0 (not Must fix / open). Add to the acceptance criteria: "Reviewer model tier resolved at PLAN handoff; spec is consistent with deployed frontmatter."

#### Finding C-8 — no spec addresses R-009 (trace and learn) in any structured way — MEDIUM

**File:** All 8 specs
**Lines:** Cross-cutting
**Severity:** MEDIUM
**What's wrong:** R-009 ("Important work leaves a traceable record. When a stronger check catches a weaker one's miss, capture the lesson so the same mistake isn't repeated.") is mentioned in project-lead.md §13 (line 866) and planning-lead.md §11 indirectly. But no spec describes *how* the agent's actions leave a trace, what the lesson-capture format is, or how a missed-by-one-agent-caught-by-another pattern is propagated.
**Why it matters:** R-009 is non-negotiable. Silent omission across 8 specs means no spec claims ownership of the lesson-capture flow.
**Suggested fix:** Add to each spec's "Acceptance Criteria" section: "Every [agent] action produces a structured trace record at `<trace_path>` and any 'miss caught downstream' event is logged in `.aspis/lessons/<date>/<agent>.md`."

---

## D. Permission Surface Audit

The audit verified each spec's permission surface against FR-006, FR-007, FR-008, FR-009 and the system-wide rules. Universal denies, scope, and web scope are checked.

### D.1 — Findings

#### Finding D-1 — All 8 specs have universal denies — INFORMATIONAL (no defect)

All 8 specs declare `git commit*: deny` and `git push*: deny` (verified across the corpus). All 8 have `webfetch: deny` and `websearch: deny` for the agents that should deny them. This is consistent with FR-007 and R-004 / R-008.

#### Finding D-2 — committer is correctly absent from task allowlists for non-build/fix/system agents — INFORMATIONAL

- build-lead.md:193 — has committer in task list (allowed)
- fix-lead.md:106 — has committer in task list (allowed)
- system-lead.md:295 — has committer in task list (allowed)
- project-lead.md:765 — explicitly *excludes* committer (line 162–166)
- planning-lead.md:240 — explicitly states "committer is NOT in the task allow-list"
- reviewer.md, test-lead.md, research-lead.md — do not list committer in task tables

This is correct per the system architecture.

#### Finding D-3 — research-lead.md has `webfetch: allow` and `websearch: allow` — correct (only subagent with both) — INFORMATIONAL

Lines 11–12, 43 of research-lead.md. Consistent with `local/AGENT-SYSTEM-ARCHITECTURE.md` line 188.

#### Finding D-4 — system-lead.md has `webfetch: allow` and `websearch: allow` — correct — INFORMATIONAL

Lines 128–129 of system-lead.md. Consistent with `local/AGENT-SYSTEM-ARCHITECTURE.md` line 188.

#### Finding D-5 — Bash allowlist varies in format and completeness — MEDIUM

**File:** All 8 specs
**Lines:** permission surface sections
**Severity:** MEDIUM
**What's wrong:** Bash allowlists differ in format:
- project-lead.md:135–137 — `python` and `python3` forms explicit (C-PORTABLE)
- planning-lead.md:234–237 — `python` and `python3` forms explicit
- build-lead.md:177–180 — only `python` (no `python3` form, missing the cross-platform pattern)
- reviewer.md:114 — only `python` (no `python3`)
- system-lead.md — has a `bash` row saying "allow all except git commit* / git push*" (line 127) — too permissive
- fix-lead.md:96 — described in prose, not in a table; no `python3` form
- test-lead.md:92 — `pytest`, `uv run pytest` but no `python .aspis/scripts/...` form
- research-lead.md:42 — "bash: deny except context scripts" — but doesn't list which context scripts

The 8 specs are not consistent in how they enumerate the bash allowlist. Build-lead and reviewer are missing the `python3` form (C-PORTABLE). system-lead says "allow all" (overly permissive — the spec itself flags this in §13 #4 as "must fix").

**Why it matters:** C-PORTABLE (rule 12 of the constitution) requires Windows and Linux compatibility. Missing `python3` means the spec is implicitly Windows-only or Linux-only. C-NO-SPECIAL-CASE / C-SINGLE-SOURCE demand uniform permission declaration.
**Suggested fix:** Standardize a "bash allowlist table" format across all 8 specs with the same columns (Pattern / Purpose / Read-or-Write). Add `python3` form to all specs that invoke scripts. Tighten system-lead's "allow all" with named commands.

#### Finding D-6 — system-lead.md says "bash: allow all except git commit*/git push*" — self-flagged as too permissive — CRITICAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/system-lead.md`
**Lines:** 127 ("bash | allow all except `git commit*`/`git push*` | Full system access for validation, repair, authoring"), 419 (Open Design #4: "Must tighten: explicit named commands, no wildcard")
**Severity:** CRITICAL
**What's wrong:** System-lead, the *most dangerous agent in the system* (line 7), has the most permissive bash surface. The spec's own Open Design #4 flags it. This violates C-PLUGIN-FIRST (no wildcards), C-NO-SPECIAL-CASE (the `*` is a special case for system-lead), and is plainly unsafe.
**Why it matters:** A prompt-injection or tool-boundary failure in system-lead becomes a full system compromise. The spec is the *target design* but the target design still has this.
**Suggested fix:** Mark as P0 blocker. Replace the "allow all" with an explicit table of named commands (`aspis preflight`, `aspis doctor`, `aspis validate-runtime`, etc.). Cross-reference research-lead.md's pattern of "allow + named commands only".

#### Finding D-7 — fix-lead.md bash allowlist described in prose, not table — LOW

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/fix-lead.md`
**Lines:** 96
**Severity:** LOW
**What's wrong:** "bash | allow (tight allowlist) | Debug and verify — pytest, git log/diff, aspis preflight" — inline description, not a table row. The other 7 specs use a table.
**Suggested fix:** Convert to a table format consistent with the other 7 specs.

#### Finding D-8 — reviewer.md says "limited allowlist" but does not enumerate web scope outside the table — INFORMATIONAL

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 102
**Severity:** INFORMATIONAL (no defect)
**What's wrong:** Bash row says "limited allowlist" but the table below lists the specific patterns. Acceptable.

#### Finding D-9 — reviewer's bash allowlist includes `aspis artifact test` but reviewer is not the test executor — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md`
**Lines:** 112
**Severity:** MEDIUM
**What's wrong:** Line 112 says `aspis artifact test` — "Stamp TEST_REPORT". But reviewer.md §1 says "Test-lead is the validation authority. It produces evidence, not verdicts. Reviewer produces verdicts." The artifact stamping is the role of test-lead, not reviewer.
**Why it matters:** Role boundary violation. If reviewer stamps TEST_REPORT, it has write access to test artifacts, contradicting §1's "read-only by design".
**Suggested fix:** Remove `aspis artifact test` from reviewer's bash allowlist. Test-lead owns test stamping. Reviewer consumes (reads) the report, does not stamp it.

---

## E. Cross-Agent Consistency

The audit checked role boundaries, delegation edges, and skill ownership across the 8 specs. The cross_ref_agents.py tool already reported 10 overlap findings (1 MEDIUM, 9 LOW). The adversarial review adds:

### E.1 — Findings

#### Finding E-1 — `load context in levels` is claimed by 4 agents — MEDIUM (cross-ref confirms)

**File:** Cross-cutting
**Lines:** project-lead.md:55 (`context-ladder`), planning-lead.md:146 (`context-ladder`), build-lead.md:87 (`context-ladder`), reviewer.md:76 (`context-ladder`)
**Severity:** MEDIUM
**What's wrong:** All 4 agents claim `context-ladder` skill and "load context in levels" responsibility. The cross_ref tool flagged this as LOW. The skill is shared — the *context loaded* differs, but the skill name is the same. The boundary is: project-lead loads the project context, planning-lead loads the feature context, build-lead loads the task context, reviewer loads the diff + acceptance context. The skill definition must explicitly state this.
**Why it matters:** C-SINGLE-SOURCE. If the skill is one document, the document must describe the level each agent operates at; otherwise four agents with the same skill name have four different procedures.
**Suggested fix:** In the skill definition (out of scope for this audit), state which level each agent operates at. Or split into 4 named sub-skills (`context-ladder-project`, `context-ladder-feature`, `context-ladder-task`, `context-ladder-diff`).

#### Finding E-2 — `confirm clean state` is claimed by 4 agents — MEDIUM (cross-ref confirms)

**File:** Cross-cutting
**Lines:** project-lead.md:83 (preflight), build-lead.md:86 (prestart-checks), fix-lead.md:64 (prestart-checks), system-lead.md:85 (prestart-checks)
**Severity:** MEDIUM
**What's wrong:** The cross_ref tool flagged this as 1 MEDIUM (planning-lead/build-lead at similarity 0.88). 4 agents explicitly claim "confirm clean state before [action]" as a responsibility.
**Why it matters:** C-SINGLE-SOURCE. The responsibility is shared, which is fine, but the boundary must be: which agent owns the *check*, and which agents *invoke* it?
**Suggested fix:** State explicitly: "preflight" is a single command (`aspis preflight`). All 4 agents invoke it. Project-lead defines the *what-cleanness-means*; others consume the result. Add this to the architecture constitution or a centralized "Pre-flight Discipline" doc.

#### Finding E-3 — Every agent's "Sends to" should match another agent's "Receives from" — VERIFY — INFORMATIONAL

The fix-lead.md §9 has explicit "Receives from" and "Sends to" sections. The other 7 specs do not have explicit "Receives from" tables, only "Task delegation" or "Sends to" tables.

Cross-check:
- fix-lead.md says it receives from build-lead, test-lead, reviewer, project-lead.
  - build-lead.md:191–195 lists fix-lead in its task allowlist ✓
  - test-lead.md:160 lists fix-lead as escalation target ✓
  - reviewer.md:166 lists fix-lead in "rejected" routing ✓
  - project-lead.md:158 lists fix-lead in task allowlist ✓
- fix-lead.md says it sends to reviewer, committer, system-lead, project-lead.
  - reviewer.md:285 (C1: hand to committer, but reviewer also lists "rejected → fix-lead" implying both ways) ✓
  - committer is only a delegate of build-lead, fix-lead, system-lead ✓
  - system-lead.md:295 has committer ✓
  - project-lead.md:158 has fix-lead ✓
- These all match.

No orphan delegation edges. The cross_ref tool's "no orphaned delegation edges" finding is confirmed.

#### Finding E-4 — build-lead.md §6.7 says "Build-lead never calls committer without review approval" — but §6.7 lists `committer` in the Task / Delegation scope table — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/build-lead.md`
**Lines:** 193 (Task delegation table), 380–385 (committer handoff section), 581 (Open Design #8: "Build-lead can delegate to committer without review (prompt rule, not runtime rule)")
**Severity:** MEDIUM
**What's wrong:** The spec has committer in the task allowlist and describes a "3 preconditions" gate, but the spec's own Open Design #8 admits the precondition is a *prompt rule, not a runtime rule*. That is, the system does not enforce the "review approval" precondition — it relies on the prompt.
**Why it matters:** R-004 / R-006 demand rules in code, not prose. A prompt rule is the very thing R-003 ("deterministic-first") is meant to replace.
**Suggested fix:** Mark this as a P0 enforcement gap. The spec should describe the *runtime mechanism* (a hook that checks the review verdict exists in the artifact before committer is invoked), not just the prompt rule.

#### Finding E-5 — system-lead.md's "Sub-reviewer" subagent is mentioned by build-lead.md but not designed — MEDIUM

**File:** `.aspis/features/F-016-agent-system-architecture/Research/ref/build-lead.md:574`, `Research/ref/reviewer.md:337`
**Lines:** build-lead.md §13 Open Design #1 ("Sub-reviewer agent doesn't exist"), reviewer.md §11 future subagents (sub-reviewer)
**Severity:** MEDIUM
**What's wrong:** Build-lead §6.6 describes per-task review routing: "V0-V1 (trivial) | Self-check or build-lead | cheap", "V2 (standard) | Sub-reviewer (fresh context) | standard", "V3-V4 (critical/security) | Reviewer lead (multi-lens) | deep". The "Sub-reviewer" agent is not in any roster. Both build-lead and reviewer note it as missing.
**Why it matters:** This is a spec-level ghost: a delegate that's referenced but not designed. R-006 / C-SINGLE-SOURCE.
**Suggested fix:** Add a `## 14 · Sub-Reviewer Spec (Deferred)` section in reviewer.md that sketches the subagent's identity, tier, packet shape. Or, alternatively, build-lead should drop the "Sub-reviewer" line and route V2 reviews to "Reviewer lead, standard tier".

#### Finding E-6 — `codebase-explorer`, `docs-fetcher`, `web-researcher` (research-lead future subagents) are not designed — LOW

**File:** research-lead.md §7
**Severity:** LOW
**What's wrong:** Same pattern as E-5. The future subagents are listed but not specified. R-006 says state each fact once. The "extract when" criteria is a placeholder.
**Suggested fix:** Either (a) accept the deferred status and add a note "designs deferred to F-017" or (b) add a 1-paragraph sketch for each.

#### Finding E-7 — No two agents claim the same *primary* responsibility — INFORMATIONAL (verified)

- planning-lead: planning lifecycle
- build-lead: implementation orchestration
- reviewer: independent quality verdicts
- system-lead: runtime/asset/config/hooks
- fix-lead: defect recovery
- test-lead: validation evidence
- research-lead: external knowledge
- project-lead: L1 entry point, routing

No overlaps. Cross_ref tool's MEDIUM finding on "Confirm clean state" is at the *responsibility level*, not the primary level.

#### Finding E-8 — `plan-critic` and `review-strategy` listed in planning-lead's recommended additions AND reviewer's owned skills — HIGH (duplicate of B-1)

**File:** planning-lead.md:167–168, reviewer.md:79
**Severity:** HIGH
**What's wrong:** Same as B-1, but viewed from the cross-agent angle. Both specs claim these skills. The cross_ref tool did not catch this because the script looks at task allowlists, not skill ownership.
**Why it matters:** Orphaned/duplicated skill ownership.
**Suggested fix:** Remove from planning-lead's recommended additions; reviewer's allowlist is the owner.

#### Finding E-9 — `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer` are 7 new subagents proposed by planning-lead — MEDIUM

**File:** planning-lead.md §7
**Severity:** MEDIUM
**What's wrong:** Planning-lead proposes 7 new L3 subagents in §7 with "Priority" of Immediate (4) and Near-term (3). These are not in any other spec. They are not in the master synthesis roster. The cost-of-change for adding 7 new agents is unclear.
**Why it matters:** C-COST (rule "if you add 7 agents, you touch 7 catalog files + 7 task packets + 7 acceptance sections"). SC-012 in F-016 SPEC says "adding a new agent requires ≤5 files touched". Adding 7 new agents is not addressed.
**Suggested fix:** Either (a) reduce to ≤2 new subagents that are clearly load-bearing, or (b) explicitly state the 7 subagents are deferred and out of scope for F-016.

#### Finding E-10 — `bug-triager` and `gate-fixer` mentioned as future fix-lead subagents but not designed — LOW

**File:** fix-lead.md §11 #7
**Severity:** LOW
**Same pattern as E-5/E-6.**

---

## F. Specific Red Flags

The audit explicitly hunted for the 6 red flags listed in the task packet.

### F.1 — Findings

#### Finding F-1 — planning-lead references `plan-critic` and `review-strategy` skills in reviewer's domain — CONFIRMED, HIGH

**File:** planning-lead.md:156, 167–168, 885
**Severity:** HIGH
**What's wrong:** §4 "Skills NOT in planning-lead's set" (line 156) lists `plan-critic` and `review-strategy` as belonging to reviewer. §4 "Recommended skill additions" (line 167–168) then says `plan-critic` and `review-strategy` are "Critical" priority to add to planning-lead's allow-list. Direct contradiction.
**Why it matters:** Same as B-1 / E-8. Cross-agent ownership conflict.
**Suggested fix:** Remove from planning-lead's "Recommended skill additions" — they are not planning-lead's skills. Acknowledge them in §10 P7 "Plan Review" as "consumed from reviewer via plan-critic skill".

#### Finding F-2 — No agent references `committer` in its task allowlist inappropriately — VERIFIED CORRECT (except the spec drift in F-2a) — INFORMATIONAL

**File:** All 8 specs
**Severity:** INFORMATIONAL
**What's wrong:** Committer is correctly in the task allowlist for build-lead (line 193), fix-lead (line 106), and system-lead (line 295) only. All 3 are correct per the system architecture.

**But:** planning-lead.md Open Design #4 (line 1115) says "committer in live task allow-list — remove (drift)". The spec target removes it (line 240), but the live version is drifted. This is the same drift as C-6.

**Suggested fix:** Track the drift as a separate fix item at PLAN handoff.

#### Finding F-3 — Model tier assignments are inconsistent across specs — CRITICAL

**File:** All 8 specs
**Severity:** CRITICAL
**What's wrong:** The audit found:
- project-lead.md §3: "Default: standard" (line 88)
- planning-lead.md §5: "Planning-lead itself: standard tier" (line 180)
- build-lead.md §4: "Standard tier (default)" (line 115)
- **reviewer.md: NO DEDICATED SECTION, only open design #1 mentioning drift** (line 351)
- system-lead.md §4: "System-lead itself: standard tier (default)" (line 112)
- fix-lead.md §4: "Fix-lead: standard tier (default)" (line 75)
- test-lead.md §4: "Test-lead: standard tier (default)" (line 79)
- **research-lead.md: tier mentioned in passing in §7 ("cheap" for project-explorer) but no dedicated tier section for research-lead itself**

Inconsistencies:
1. Reviewer has no tier declaration (R-007 violated).
2. Research-lead's tier is implicit (not stated).
3. Master synthesis says reviewer should be `deep` for production review (line 144 of AGENT-SYSTEM-ARCHITECTURE.md: "Deep | Architecture decisions, root-cause debugging, security review, plan-critic | ~10%"). The spec says nothing; Open Design #1 says live is `cheap`.
4. The 70/20/10 cheap/standard/deep target is not referenced in any spec.

**Why it matters:** R-007 violation. Cross-agent inconsistency: the system can't even be confident what tier reviewer runs at.
**Suggested fix:**
- Add a "Model Tier Strategy" section to reviewer.md stating "Default: deep. Cheap for P2 self-checks."
- Add a "Model Tier Strategy" section to research-lead.md stating "Default: standard. Deep for security/CVE verification."
- Reference the 70/20/10 target in each spec.

#### Finding F-4 — `enforcement: warn` vs `block` is documented in 2 of 8 specs — HIGH (same as C-5)

**File:** system-lead.md:246–254, build-lead.md:575
**Severity:** HIGH
**What's wrong:** FR-020 enforcement mode is only fully specified in system-lead §8. Other 6 specs don't mention it. This means 6 specs do not know which enforcement mode applies to their actions.
**Why it matters:** FR-020 violation.
**Suggested fix:** Add a "Cross-Cutting: Enforcement Mode" note to each spec's permission surface section.

#### Finding F-5 — "Recommended new skills" are not consistent across specs — MEDIUM

**File:** All 8 specs
**Lines:** Cross-cutting
**Severity:** MEDIUM
**What's wrong:** Each spec lists its "Recommended new skills" / "Missing skills" without cross-referencing the master synthesis. For example:
- project-lead.md:80–83 lists `recontextualization`, `session-continuation`, `mode-decision`
- planning-lead.md:163–172 lists `plan-critic`, `review-strategy`, `deterministic-first`, `scope-control`, `mode-decision`, `constitution-checks`
- build-lead.md:103–108 lists `packet-validation`, `builder-selection`
- reviewer.md:81–91 lists 6 missing skills
- system-lead.md:93–107 lists 10 missing skills
- test-lead.md: (no missing skills section)
- fix-lead.md: (no missing skills section)
- research-lead.md:263–274 lists 2 missing skills

The total is 30+ new skills, but the master synthesis doesn't enumerate them. R-006 (single source) is violated. Some skills are listed in multiple specs (e.g., `mode-decision` is in both project-lead and planning-lead).
**Why it matters:** If 30+ new skills are needed, the catalog needs to track them with priority and owning-agent. The specs are the right place to list them, but they should be aggregated and deduplicated.
**Suggested fix:** Add to each spec's open design questions: "Cross-reference: `.aspis/features/F-016-agent-system-architecture/Research/audit/skill-inventory.md` for the unified list." Or create such a file.

#### Finding F-6 — Every agent's "Sends to" should match another agent's "Receives from" — VERIFIED — INFORMATIONAL

**File:** All 8 specs
**Severity:** INFORMATIONAL
**What's wrong:** The audit verified each delegation edge:
- project-lead sends to: planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer
  - Each of these lists project-lead as a caller (verified across permission surface / task delegation tables)
- planning-lead sends to: research-lead, reviewer, project-explorer, clarify, task-decomposer, idea-capture, prd-writer, scope-estimator, constitution-checker, research-request-writer
  - The first 3 exist; the rest are proposed new subagents (Finding E-9)
- build-lead sends to: general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead
  - All 7 exist
- reviewer sends to: project-explorer, research-lead
  - Both exist
- system-lead sends to: project-explorer, reviewer, committer
  - All 3 exist
- fix-lead sends to: reviewer, committer, system-lead, project-lead
  - All 4 exist
- test-lead sends to: project-explorer
  - Exists
- research-lead sends to: project-explorer
  - Exists

No orphaned edges. The cross_ref tool's "no findings" is confirmed.

#### Finding F-7 — Several specs include `[NEEDS CLARIFICATION]`-style or unresolved items in critical paths — INFORMATIONAL (cross-ref confirms none)

**File:** All 8 specs
**Severity:** INFORMATIONAL
**What's wrong:** The cross_ref tool confirmed no `[NEEDS CLARIFICATION]` markers remain. Adversarial review confirms this — no markers found in critical paths.

#### Finding F-8 — `active_feature.json` has no `scope` field per build-lead.md Open Design #3 — MEDIUM

**File:** build-lead.md:576
**Severity:** MEDIUM
**What's wrong:** Build-lead's open design #3 says "active_feature.json has no scope field — scope guard is no-op". This is a known gap that the spec ships with.
**Why it matters:** R-001 (scope boundaries) is partially unmechanized.
**Suggested fix:** Note as a P0 in the F-016 plan. The spec acknowledges it; the plan should fix it.

#### Finding F-9 — Build-lead.md §6.7 says "committer" is delegated to — but committer precondition is prompt-only — HIGH (duplicate of E-4)

**File:** build-lead.md:380–385
**Severity:** HIGH
**Same as E-4.**

#### Finding F-10 — system-lead.md §1 says "the only lead" but §5 admits self-modification — CRITICAL (duplicate of B-6)

**File:** system-lead.md:17, 142–152
**Severity:** CRITICAL
**Same as B-6.**

---

## Detailed Findings (file:line, severity, what's wrong, why, fix)

This is the consolidated list of all 40 findings, ordered by file then by line.

| # | File:Line | Severity | Description | Suggested fix |
|---|---|---|---|---|
| A-1 | reviewer.md:94–125 | CRITICAL | Missing "Model Tier Strategy" section; R-007 / FR-005 violated | Add `## 4 · Model Tier Strategy` between Permission Surface and "The 9 Review Dimensions". Declare default tier (deep for production, cheap for P2). |
| A-2 | test-lead.md:156–168 | HIGH | Missing "Error Handling Matrix" section; only "Escalation" exists | Add new section "Error Handling Matrix" with failure→catcher→fixer→review rows. Renumber subsequent sections. |
| A-3 | research-lead.md:145–192 | HIGH | Section numbering skips 9 → 11; §10 is missing | Renumber: §10 Subagent Details, §11 Full Use Case Catalog, §12 Adversarial Findings, etc. |
| A-4 | research-lead.md:1–386 | CRITICAL | Missing "If stuck, stop — don't guess" rule; spec's own adversarial findings #7 flags this as HIGH but doesn't fix it | Add to §8 Escalation and §14 Acceptance: "If stuck, hand back to delegating lead; do not guess." |
| A-5 | reviewer.md:1–386 | CRITICAL | Missing "If stuck, stop — don't guess" rule | Add to §6 Verdict System: "If stuck, withhold verdict. Do not guess." |
| A-6 | test-lead.md:156–168 | MEDIUM | "Escalation" section conflates errors and escalations | Rename §9 → "Escalation", add new §10 "Error Handling Matrix" |
| A-7 | fix-lead.md:34–143 | LOW | Error handling embedded in lifecycle, not a matrix | Add a §12 "Error Handling Matrix" with the standard rows |
| A-8 | research-lead.md:145–161 | MEDIUM | No dedicated "Delegation Map" section; §7 is "Subagents" only | Add `## 5 · Delegation Map` with Receives-from / Sends-to |
| A-9 | test-lead.md:100–101 | LOW | Task delegation section is one line; no full map | Add proper Delegation Map with Receives-from / Sends-to |
| B-1 | planning-lead.md:167–168 | HIGH | `plan-critic` and `review-strategy` listed in planning-lead's recommended additions, but §4 itself says they belong to reviewer | Remove from planning-lead's recommended additions |
| B-2 | reviewer.md:199, 351 | HIGH | Internal contradiction: §7 lists 12 checks; Open Design #3 says "6 missing" | Label the 6 missing checks explicitly or move to v2 sub-table |
| B-3 | system-lead.md:1–452 | MEDIUM | No 12-rule constitution compliance section | Add `## 15 · Constitution Compliance` enumerating which rules system-lead enforces |
| B-4 | fix-lead.md, test-lead.md | MEDIUM | No constitution compliance sections in either | Add "Rules This Agent Enforces" subsection to each |
| B-5 | research-lead.md:38–45, 264–283 | HIGH | `write: allow` but `edit: deny` contradiction; spec documents it as adversarial #14 but doesn't resolve | Either allow both with Research/-scope, or justify the asymmetry in the permission surface section |
| B-6 | system-lead.md:17, 142–152 | CRITICAL | §1 says "the only lead" but §5 admits self-modification. Direct contradiction. | Drop the "only" claim OR add governance-subagent ownership of self-modification |
| B-7 | All 8 specs | MEDIUM | No spec addresses C-PORTABLE (rule 12) | Add "All scripts must be C-PORTABLE compliant" note to each bash allowlist |
| C-1 | fix-lead.md:14, 29, 97, 190, 223 | HIGH | Cites only R-001, R-004, R-005; omits R-002, R-006, R-007, R-008, R-009 | Add "Core Rules Fix-Lead Enforces" table |
| C-2 | test-lead.md:29, 30, 93, 111, 144, 162, 167, 266 | HIGH | Cites only R-004, R-005, R-008; omits R-001, R-002, R-006, R-007, R-009 | Add "Core Rules Test-Lead Enforces" table |
| C-3 | research-lead.md:28, 31, 75, 167, 168, 273, 336 | HIGH | Cites only R-001, R-004, R-008; omits R-002, R-005, R-006, R-007, R-009 | Add "Core Rules Research-Lead Enforces" table |
| C-4 | reviewer.md:1–386 | MEDIUM | No "Core Rules" or "Enforcement" table | Add `## N · Core Rules Reviewer Enforces` |
| C-5 | All 8 specs | HIGH | Enforcement mode (warn vs block) documented in 2 of 8 specs; FR-020 violation | Add a one-line enforcement-mode note to each Permission Surface section |
| C-6 | planning-lead.md:1115, 1139 | HIGH | Open design #4 says "committer in live task allow-list — remove" but ships with the live drift documented | Make "Must fix" → "Fix at PLAN handoff" with FR-### tie-in |
| C-7 | reviewer.md:351 | CRITICAL | Open design #1 documents model drift (live cheap vs config deep) but ships unresolved; R-007 violated | Mark P0; add to acceptance criteria; resolve at PLAN handoff |
| C-8 | All 8 specs | MEDIUM | No spec addresses R-009 (trace and learn) in structured way | Add trace-record format and lesson-capture format to each spec |
| D-5 | All 8 specs | MEDIUM | Bash allowlist varies in format; some missing `python3` form (C-PORTABLE) | Standardize a "bash allowlist table" format; add `python3` to all |
| D-6 | system-lead.md:127 | CRITICAL | "bash: allow all except git commit*/git push*" is overly permissive; spec's own Open Design #4 flags it | Mark P0; replace with explicit named-commands table |
| D-7 | fix-lead.md:96 | LOW | Bash allowlist described in prose, not table | Convert to table format |
| D-9 | reviewer.md:112 | MEDIUM | `aspis artifact test` in reviewer's bash allowlist but reviewer is not the test executor (role violation) | Remove from reviewer's bash allowlist |
| E-1 | project-lead.md:55, planning-lead.md:146, build-lead.md:87, reviewer.md:76 | MEDIUM | "Load context in levels" claimed by 4 agents via `context-ladder` | Skill definition must state which level each agent operates at |
| E-2 | project-lead.md:83, build-lead.md:86, fix-lead.md:64, system-lead.md:85 | MEDIUM | "Confirm clean state" claimed by 4 agents (cross-ref MEDIUM) | Clarify: project-lead defines what "clean" means; others invoke |
| E-4 | build-lead.md:193, 380–385, 581 | MEDIUM | "Build-lead never calls committer without review approval" is a prompt rule, not runtime | Describe the runtime mechanism (hook that checks review verdict) |
| E-5 | build-lead.md:574, reviewer.md:337 | MEDIUM | "Sub-reviewer" agent referenced but not designed (spec-level ghost) | Either add a §N sketch in reviewer.md, or remove the line from build-lead |
| E-6 | research-lead.md:153–161 | LOW | 3 future subagents listed but not designed | Accept deferred status or add 1-paragraph sketch each |
| E-8 | planning-lead.md:167–168, reviewer.md:79 | HIGH | Duplicate of B-1: `plan-critic` and `review-strategy` claimed by both specs | Same fix as B-1 |
| E-9 | planning-lead.md §7 | MEDIUM | 7 new L3 subagents proposed; F-016 SC-012 says new agent ≤5 files; 7 agents not addressed | Reduce to ≤2 or explicitly defer |
| E-10 | fix-lead.md:212 | LOW | `bug-triager` and `gate-fixer` future subagents not designed | Accept deferred or sketch |
| F-1 | planning-lead.md:156, 167–168, 885 | HIGH | Duplicate of B-1: `plan-critic`/`review-strategy` in reviewer's domain | Same fix as B-1 |
| F-3 | All 8 specs | CRITICAL | Model tier assignments inconsistent: reviewer has none, research-lead implicit, no 70/20/10 reference | Add Model Tier Strategy to reviewer and research-lead; reference 70/20/10 in each |
| F-4 | All 8 specs | HIGH | Duplicate of C-5: enforcement mode in 2 of 8 specs | Same fix as C-5 |
| F-5 | All 8 specs | MEDIUM | 30+ recommended new skills across specs; not aggregated; some duplicated | Create unified skill-inventory file or cross-reference |
| F-8 | build-lead.md:576 | MEDIUM | `active_feature.json` has no `scope` field per Open Design #3; R-001 partially unmechanized | Note as P0 in F-016 plan |
| F-9 | build-lead.md:380–385 | HIGH | Duplicate of E-4: committer precondition is prompt-only | Same fix as E-4 |
| F-10 | system-lead.md:17, 142–152 | CRITICAL | Duplicate of B-6: "the only lead" but self-modification admitted | Same fix as B-6 |

---

## Cross-Reference with cross_ref_agents.py

The cross_ref_agents.py script ran with `--scope leads` and reported 10 findings (1 MEDIUM, 9 LOW) of responsibility overlap. These are cataloged in the system. The audit confirms:

- **MEDIUM:** planning-lead.md:145 ↔ build-lead.md:86 — "Confirm clean state before starting" — Finding E-2 above.
- **9 LOW:** Other responsibility-near-duplicates on context-loading, confirm-clean-state, and infer-build-mode. All are consistent with Finding E-1 and E-2.

The cross_ref tool did NOT detect:
- Skill ownership duplicates (B-1, E-8, F-1) — its check is for *task allowlists*, not skill ownership
- Section missing/structural gaps (A-1, A-2, A-3, A-4, A-5)
- Bash allowlist format inconsistencies (D-5)
- Model tier inconsistencies (F-3)
- The 6 CRITICAL findings (B-6, A-1, A-4, A-5, C-7, D-6, F-3)

The cross_ref tool is necessary but not sufficient for adversarial review.

---

## Recommendations to Build Lead

1. **Block F-016 sign-off** until the 6 CRITICAL findings (A-1, A-4, A-5, B-6, C-7, D-6, F-3) are resolved. These violate the system rules (R-007) and the F-016 SPEC's own FR-###.
2. **Resolve all 14 HIGH findings** before F-016 plan is committed. These are gaps in R-001/R-004/R-005/R-008 enforcement and structural completeness.
3. **Accept 11 MEDIUM findings** as fix-during-build items. These are quality and consistency issues that don't block the spec itself but should be tracked.
4. **Note 9 LOW findings** for passing cleanup. Some are duplicated by MEDIUM.
5. **Run cross_ref_agents.py again** after fixes are applied to verify the responsibility overlap (1 MEDIUM, 9 LOW) is resolved.

---

## Audit Limitations

- The audit did not verify the *content* of the 12 constitution rules or 9 system rules — only whether each spec references/enforces them. The rules themselves are not under audit.
- The audit did not check the *master synthesis* (`local/AGENT-SYSTEM-ARCHITECTURE.md`) for internal consistency; only the 8 reference specs were audited against the synthesis.
- The audit did not verify FR-001…FR-028 in detail — only the 11-section template requirement (FR-002) and a sample of high-impact FRs (FR-005, FR-007, FR-020, FR-026, FR-028).
- The audit did not check the 3 leaf agent specs (committer, general-builder, project-explorer) — those are out of scope (T-03 is the 8 lead specs only).
- Bash allowlist pattern matching was performed by content search, not runtime. Actual enforcement is verified at runtime by hooks, not by this audit.

---

*Adversarial audit produced 2026-06-27 by T-03. Reviewer stance: assume every spec has hidden issues; cross-reference claims; check the absence of references as well as the presence. 40 findings cataloged (6 CRITICAL, 14 HIGH, 11 MEDIUM, 9 LOW). Verdict: FAIL — multiple blockers require remediation before F-016 can be handed to build-lead.*
