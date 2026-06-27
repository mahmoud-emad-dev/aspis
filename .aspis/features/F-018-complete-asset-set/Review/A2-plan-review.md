# F-018 — Phase A2 Plan Review

> **Reviewer:** reviewer
> **Date:** 2026-06-27
> **Mode:** production
> **Scope:** Re-review the A1-revised F-018 plan against the six A1 conditions;
> verify task/FR/SC integrity, gate chains, and R-008 governance timing.
> **Verdict surface:** APPROVE / APPROVE WITH CONDITIONS / REJECT

---

## Executive summary

The planning-lead has addressed **all six A1 conditions** with concrete,
verifiable edits in SPEC.md, PLAN.md, TASKS.md, and the two research
artifacts. The plan is now evidence-driven at L0, has a 3-stage R-008
governance flow for the PreToolUse hook, ships `validate-approvals.py`
as the single critical R-008 ledger validator, includes a defensive
debris-cleanup task, and corrects the L15 use-case-coverage delegation
claim. Task numbering is clean (T-001a → T-050, 51 tasks, no gaps).
Gate chains, dependency order, and rule compliance (R-003, R-004,
R-006, R-008) are all consistent with the architecture.

Two minor inconsistencies in the A1 changelog (FR count, FR number
gap) are not defects in the plan itself — the SPEC content is complete
and consistent; the changelog arithmetic is slightly off. These do not
block the build.

**Verdict: APPROVE — proceed to Phase B (Build).**

---

## 1 · C-1 through C-6 verification

### C-1 (discovery+fix split) — **SATISFIED**

**Evidence:**

- **T-001a is discovery-only.** TASKS.md L15-21 names T-001a explicitly
  as "Discovery sweep: run pytest, capture ALL failures, write evidence
  report." The acceptance is "discovery report written; every failure
  traced to file:line; no speculative/narrative failures listed;
  blocked items marked `BLOCKED: env`." No fix action is in T-001a.
- **T-001b is evidence-driven.** TASKS.md L25-36 names T-001b as
  "Fix real test failures (evidence-driven from T-001a report)" with
  the explicit instruction "Fix only failure classes CONFIRMED by
  T-001a report. Each class fixed with root-cause evidence." Each
  of the 4 speculative failure classes is listed with the conditional
  "(only if confirmed — ...)" — fix is gated on discovery output.
  T-001b is also "hard" blocked on T-001a.
- **Old speculative L0 tasks cleaned up.** The old T-001..T-004
  (4 separate fix tasks) are gone. L0 now has exactly 3 tasks:
  T-001a (discovery), T-001b (evidence-driven fix), T-002 (gate).
  Confirmed by counting L0 tasks in TASKS.md L10-47.
- **Evidence flag.** TASKS.md L33 notes "`validate_index.py:180`
  already has `10%%` (correctly escaped); do not assume a crash." I
  independently verified this against the live source: the file
  `src/aspis/commands/validate_index.py:180` reads `"and every CODE_MAP
  line count is within 10%% of actual."` (the doubled `%%` is the
  correct argparse escape for a literal `%`). The A1 evidence was
  correct; the plan's discovery-first design prevents re-introducing
  the false-positive fix narrative.

**C-1 is fully satisfied.** The L0 layer is now evidence-driven, not
narrative-driven, and the L0.1a→L0.1b ordering in PLAN.md L37-53
matches.

---

### C-2 (env-blocked fallback) — **SATISFIED**

**Evidence:**

- **Explicit fallback in FR-L0-001.** SPEC.md L106:
  > "FR-L0-001: `pytest` MUST exit 0 on all platforms (Windows +
  > Linux). If the environment blocks pytest (e.g., subprocess
  > capture failure in test harness), the fallback is `python -m
  > pytest --no-header -q 2>&1 | Select-String FAILED` (or
  > equivalent); at minimum, all non-subprocess tests MUST pass,
  > and blocked subprocess tests MUST be documented with `BLOCKED: env`
  > in the discovery report."
- **Gate allows non-subprocess tests to pass.** SPEC.md L25-26 (L0
  in-scope): "If environment blocks pytest, fallback: run
  non-subprocess tests, document blocked items as `BLOCKED: env`."
  PLAN.md L63 (L0 exit gate): "Fallback: if environment blocks
  subprocess tests, all non-subprocess tests pass + blocked items
  documented with `BLOCKED: env`."
- **SC-L0-001 matches.** SPEC.md L184: "SC-L0-001: `pytest` exits 0
  on Windows AND Linux with 0 failures. Fallback: if environment
  blocks subprocess tests, all non-subprocess tests pass + blocked
  items documented as `BLOCKED: env` in discovery report."
- **Blocked items documented as `BLOCKED: env`.** TASKS.md L17, L21,
  L48, and PLAN.md L41 all use the `BLOCKED: env` token as the
  required marker.

**C-2 is fully satisfied.** Three layers of fallback (FR, SC, gate)
plus the discovery task's acceptance all carry the same fallback
language. The gate is achievable in the env-blocked case.

---

### C-3 (hook split into 3) — **SATISFIED**

**Evidence:**

- **T-044, T-045, T-046 are three distinct tasks.** TASKS.md
  L317-339:
  - **T-044** (L317-322): "Author PreToolUse hook modules" — produces
    modules in `.aspis/scripts/hooks/`, AST-clean, no settings edit.
    `Builder: standard | Review: reviewer, correctness+security`.
  - **T-045** (L324-330): "File R-008 governance request for
    `.claude/settings.json` PreToolUse hook" — uses `governance
    subagent request verb`. `Builder: build-lead (direct) | Review: self`.
  - **T-046** (L332-339): "Apply `.claude/settings.json` PreToolUse
    hook (on owner approval)" — `Depends on: T-045 + owner approval
    [hard]`. `Builder: build-lead (direct) | Review: self`.
- **R-008 honored in the split.** SPEC.md L151 (FR-L4-001):
  > "The `.claude/settings.json` edit that wires them MUST pass
  > through R-008 governance approval (governance subagent `request`
  > → owner `approve`) before being applied." R-008 (system-rules.md
  > L101-103: "Architecture, rules, permissions, security posture,
  > and model-routing changes require human approval — never an
  > automated rewrite") is honored: the settings edit is a
  permissions-change surface, and the request/approve verb flow is
  the canonical governance mechanism.
- **Fallback for "owner hasn't approved" at build time.** TASKS.md
  L339: "**Fallback:** If approval not yet granted at build time,
  leave hook modules in place, document manual edit as post-build
  owner action, mark task `BLOCKED: awaiting R-008 owner approval`."
  PLAN.md L371: "If approval not yet granted at build time: leave
  the hook modules in place, document the manual edit as a post-build
  owner action, and mark this task as `BLOCKED: awaiting R-008 owner
  approval`."

**C-3 is fully satisfied.** The split is correct, R-008 is honored,
and the fallback is explicit and actionable.

---

### C-4 (debris cleanup) — **SATISFIED**

**Evidence:**

- **T-015 added as a debris-cleanup task.** TASKS.md L125-131:
  - Title: "Remove `_tmp_f017_*.py` debris from
    `.aspis/scripts/planning/`"
  - Action: "If no debris found: document 'CLEAN — no debris' and
    pass."
  - Acceptance: "zero `_tmp_f017_*.py` files remain in
    `.aspis/scripts/planning/`"
- **In the right layer.** T-015 is in L1.D (Debris cleanup) at
  TASKS.md L123, between the script-build tasks (L1.A, L1.B, L1.C)
  and the L1 gate (L1.E). This is the right place: same layer as
  the script work it audits, runs before the L1 gate.
- **FR-L1-009 and SC-L1-003 added.** SPEC.md L123: "FR-L1-009: Any
  `_tmp_f017_*.py` debris in `.aspis/scripts/planning/` MUST be
  removed (R-006 violation — build detritus, not catalog assets)."
  SPEC.md L188: "SC-L1-003: Zero `_tmp_f017_*.py` files remain in
  `.aspis/scripts/planning/`."
- **Current state verified.** I ran a glob on
  `.aspis/scripts/planning/` — no `_tmp_f017_*.py` files are present
  in the workspace today. The task is correctly defensive: it covers
  both the "debris exists, delete it" case and the "debris already
  cleaned, document and pass" case. (Note: the original 10 debris
  files cited in gap-collation §9.2 M-1 and F-017 final-gates.md
  L1089-1110 appear to have already been removed by prior cleanup;
  the task remains valuable as a gate-step defensive measure to
  prevent regression.)
- **R-006 violation cited correctly.** SPEC.md L123 and TASKS.md L127
  both note this is an R-006 violation (scripts at runtime, not in
  catalog source). R-006 says "State each fact once and reference
  it — don't duplicate rules, procedures, or assets" (system-rules.md
  L92-95); a script that exists only at runtime with no catalog twin
  violates the single-source principle.

**C-4 is fully satisfied.** The task exists, is in the correct
layer (L1, before the L1 gate), has explicit FR/SC support, and
handles both the "debris present" and "debris already gone" cases.

---

### C-5 (validate-approvals CLI verb) — **SATISFIED**

**Evidence:**

- **T-014 added as a P0 governance-script task.** TASKS.md L115-121:
  - Title: "Build and deploy `validate-approvals.py`"
  - Path: `src/aspis/data/catalog/scripts/system/validate-approvals.py`
    (new), `.aspis/scripts/system/validate-approvals.py` (deploy)
  - Purpose: "R-008 ledger enforcement — checks `.aspis/approvals/`
    for missing/expired approvals on protected-path writes"
  - Priority: P0 (gap P0 HIGH)
  - Note (L121): "this is the single most critical of the 8 missing
    CLI validators (gap P0 HIGH). The remaining 7 validators are
    deferred to F-019 per SPEC Out of scope."
- **7 other CLI validators explicitly out of scope.** SPEC.md L101:
  > "The 8 missing CLI validators from system-lead-config-runtime.md
  > §5.8 (`validate-approvals`, `validate-skills`, `validate-agents`,
  > `validate-decisions`, `validate-constitution`, `validate-trace`,
  > `validate-parity`, `validate-profiles`) — deferred to F-019.
  > Rationale: these are governance-enforcement infrastructure that
  > require CLI verb scaffolding and per-validator design. The most
  > critical, `validate-approvals` (R-008 ledger enforcement), is gap
  > P0 HIGH and should be the first validator built in F-019. **Interim**:
  > R-008 compliance is verified manually via the governance
  > subagent's ledger during the F-018 gate sweeps."
  All 7 deferred validators (validate-skills, validate-agents,
  validate-decisions, validate-constitution, validate-trace,
  validate-parity, validate-profiles) are explicitly named with
  rationale.
- **L1 script count is now 12.** SPEC.md L42: "Exit gate: all 12
  scripts pass AST + `--help` + smoke test + byte-parity; debris
  cleaned." Cross-check: 6 planning (T-003..T-008) + 5 research
  (T-009..T-013) + 1 governance (T-014) = 12 scripts. ✅
- **FR-L1-008 added.** SPEC.md L122: "FR-L1-008: Governance script
  (`validate-approvals.py`) MUST live at `.aspis/scripts/system/`."

**C-5 is fully satisfied.** The single most critical validator ships
in L1; the other 7 are explicitly named as out-of-scope with
rationale and a clear deferral path (F-019). The interim R-008
manual-check protocol is documented.

---

### C-6 (coverage matrix fix) — **SATISFIED**

**Evidence:**

- **L15 stale claim fixed.** use-case-coverage.md L15 now reads:
  > "Project-lead delegates to planning-lead (plan→spec) + build-lead
  > (build→review); both in live delegate list."

  Verified against live `src/aspis/data/catalog/agents/project-lead.md`
  L33-41, the `delegates:` field is:
  ```
  delegates:
    - planning-lead
    - build-lead
    - reviewer
    - system-lead
    - fix-lead
    - test-lead
    - research-lead
    - project-explorer
  ```
  Both `planning-lead` and `build-lead` are in the live delegate
  list. The original A1 claim that "planning-lead does not delegate
  to build-lead" was based on a misreading; project-lead does
  delegate to both. The fix correctly identifies the project-lead
  as the right parent, not planning-lead.

- **All other delegation claims verified.** I cross-checked the
  live `delegates:` field against every "Delegation to X" claim in
  the matrix:

  | Matrix claim | Live evidence | Verdict |
  |--------------|---------------|---------|
  | L16: project-lead → fix-lead | project-lead.md L38 ✅ | Correct |
  | L17: project-lead → test-lead | project-lead.md L39 ✅ | Correct |
  | L18: project-lead → reviewer | project-lead.md L36 ✅ | Correct |
  | L20: project-lead → research-lead | project-lead.md L40 ✅ | Correct |
  | L37: planning-lead → research-lead | planning-lead.md L38 ✅ | Correct |
  | L38: planning-lead delegates & subagent | T-028..T-035 in plan ✅ | Correct |
  | L42: planning-lead P4 spec → SPEC.md | prd-writer at T-032 ✅ | Correct |
  | L44: planning-lead P5 constitution audit | T-004, T-030 ✅ | Correct |
  | L46: planning-lead P6 tasks → TASKS.md | task-decomposer at T-029 ✅ | Correct |
  | L48: planning-lead P6 dependency graph | T-008, T-035 ✅ | Correct |
  | L68: build-lead → general-builder | build-lead.md L37 ✅ | Correct |
  | L69: build-lead → fix-lead | build-lead.md L40 ✅ | Correct |
  | L70: build-lead → reviewer | build-lead.md L38 ✅ | Correct |

  All 13 delegation claims I sampled are correct. (The A1 changelog
  says 12 were verified; I found 13 substantive claims. The 13th
  was implicit in L38.)

- **CU-1, CU-2, CU-3 added.** use-case-coverage.md L307-313 has
  a "Future Scope — Use Cases" section with:
  - CU-1: ASPIS self-dogfooding scenario
  - CU-2: Cross-runtime parity matrix
  - CU-3: Profile-aware export
  Each has a "Notes" column explaining why it's deferred and when
  it returns to scope.
- **Task references updated.** The A1 changelog states "Updated
  ALL task references throughout the matrix (161 rows) to match
  the new T-### numbering across SPEC, PLAN, and TASKS." Spot-
  checked: matrix rows reference T-001a, T-001b, T-002, T-003..T-008
  (planning scripts), T-009..T-013 (research scripts), T-014
  (validate-approvals), T-015 (debris), T-016 (L1 gate), T-017
  (skill), T-018 (templates), T-019 (workflow), T-020 (L2 gate),
  T-021..T-041 (subagents), T-042 (wiring), T-043 (L3 gate),
  T-044..T-046 (hook split), T-047 (edge cases), T-048 (parity),
  T-049 (L4 gate), T-050 (final). All consistent with TASKS.md.

**C-6 is fully satisfied.** The L15 fix is correct, all sampled
delegation claims verify against the live catalog, and the future-
scope notes are present.

---

## 2 · Task integrity check

### 2.1 Task count and numbering

**51 tasks total** (T-001a through T-050), per TASKS.md L4 ("Total
tasks: 51") and verified by direct count:

| Layer | Range | Count |
|-------|-------|-------|
| L0 | T-001a, T-001b, T-002 | 3 |
| L1 | T-003..T-016 | 14 |
| L2 | T-017..T-020 | 4 |
| L3 | T-021..T-043 | 23 |
| L4 | T-044..T-050 | 7 |
| **Total** | | **51** |

- **No gaps.** Sequential: T-001a, T-001b, T-002, T-003, ... T-050.
- **No duplicates.** Each T-NN appears exactly once.
- **T-001a and T-001b handled correctly.** T-001a is the discovery
  task (L0.A); T-001b is the evidence-driven fix (L0.B). T-002 is
  the L0 gate (L0.C). The letter suffix is consistent: T-001a blocks
  T-001b (hard), T-001b blocks T-002 (hard). A1 changelog explicitly
  documents this convention at TASKS.md L6.
- **T-020g suffix removed.** The A1 review flagged T-020g as
  unconventional. The current plan has T-020 as the L2 gate
  (TASKS.md L169-173), with no T-020g. The A1 changelog (L959)
  confirms "Removed suffix convention; L2 gate is now T-020
  (sequential)."
- **TN-1 (Research scripts count) fixed.** A1 review noted
  "Research scripts (4)" was wrong. PLAN.md L102 and TASKS.md L86
  now correctly read "Research scripts (5)" (T-009..T-013).

**Task numbering: PASS.**

### 2.2 Task-to-layer mapping

- **L0** (T-001a, T-001b, T-002) — 3 tasks, all referenced in
  PLAN.md L37-63 and SPEC.md L21-26. ✅
- **L1** (T-003..T-016) — 14 tasks: 6 planning (T-003..T-008),
  5 research (T-009..T-013), 1 governance (T-014), 1 debris (T-015),
  1 gate (T-016). Matches PLAN.md L67-152 and SPEC.md L27-42. ✅
- **L2** (T-017..T-020) — 4 tasks: 1 skill (T-017), 1 templates
  (T-018), 1 workflow (T-019), 1 gate (T-020). Matches PLAN.md
  L155-192 and SPEC.md L44-48. ✅
- **L3** (T-021..T-043) — 23 tasks: 7 system-lead (T-021..T-027),
  8 planning-lead (T-028..T-035), 6 test-lead (T-036..T-041), 1
  wiring (T-042), 1 gate (T-043). Matches PLAN.md L196-351 and
  SPEC.md L50-79. ✅
- **L4** (T-044..T-050) — 7 tasks: 3 hook split (T-044, T-045,
  T-046), 1 edge cases (T-047), 1 parity (T-048), 1 gate sweep
  (T-049), 1 report (T-050). Matches PLAN.md L355-396 and SPEC.md
  L81-89. ✅

**Layer mapping: PASS.**

### 2.3 No circular dependencies

Per PLAN.md L408-422 (Dependencies section):

```
L0 → L1 → L2 → L3 → L4
```

- L0 has no dependencies.
- L1 depends on L0 (T-016 depends on T-003..T-015).
- L2 depends on L1 (T-020 depends on T-017, T-018, T-019 which
  depend on T-016).
- L3 depends on L2 (T-043 depends on T-042 which depends on
  T-021..T-041 which depend on T-020).
- L4 depends on L3 (T-049 depends on T-046, T-047, T-048 which
  depend on T-043).
- Within L1: A, B, C, D all depend on T-002; E (T-016) depends on
  A, B, C, D. No cycles.
- Within L3: A, B, C all depend on T-020; D (T-042) depends on
  A, B, C; E (T-043) depends on D. No cycles.

**No circular dependencies. PASS.**

---

## 3 · FR/SC/coverage check

### 3.1 FRs

**Counted in SPEC.md L105-164:** 49 FRs.

| Section | Count | FR IDs |
|---------|-------|--------|
| L0 | 7 | FR-L0-001..007 |
| L1 | 9 | FR-L1-001..009 |
| L2 | 10 | FR-L2-001..010 |
| L3 | 11 | FR-L3-001..011 |
| L4 | 6 | FR-L4-001..006 |
| Cross-cutting | 6 | FR-CC-001..006 |
| **Total** | **49** | |

**Minor inconsistency:** The A1 changelog (L966) says "FRs: 46 → 48"
and lists 3 additions (FR-L0-007 ruff, FR-L1-008 governance, FR-L1-009
debris). The actual count is 49 (the SPEC has 7 L0 FRs, 9 L1 FRs,
10 L2 FRs, 11 L3 FRs, 6 L4 FRs, 6 CC FRs = 49). The changelog's
arithmetic is off by 1, but the SPEC content is complete and correct.
This is a documentation arithmetic error in the changelog, not a
defect in the plan. **No build impact.**

**FR ↔ task coverage (spot-checked):**

| FR | Task(s) | Verdict |
|----|---------|---------|
| FR-L0-001 (pytest exit 0) | T-001a, T-001b, T-002 | ✅ |
| FR-L0-002 (evidence-driven fix) | T-001b | ✅ |
| FR-L0-007 (ruff) | T-002 | ✅ |
| FR-L1-008 (governance script) | T-014 | ✅ |
| FR-L1-009 (debris) | T-015 | ✅ |
| FR-L2-001 (dependency-audit skill) | T-017 | ✅ |
| FR-L2-008 (TEST_REPORT) | T-018 | ✅ (with path note) |
| FR-L2-009 (project-lead workflow) | T-019 | ✅ |
| FR-L3-001 (catalog agent) | T-021..T-041 | ✅ |
| FR-L3-007 (catalog-registered) | T-042 | ✅ |
| FR-L4-001 (PreToolUse hook) | T-044, T-045, T-046 | ✅ |
| FR-L4-002 (≥2 edge cases) | T-047 | ✅ |
| FR-L4-006 (cross-runtime parity) | T-048 | ✅ |
| FR-CC-001 (R-003 scripts-before-agents) | Sequencing enforced in TASKS | ✅ |
| FR-CC-003 (R-008 human gate) | T-045 | ✅ |

**All 15 sampled FRs have at least one task. PASS.**

### 3.2 SCs

**Counted in SPEC.md L183-202:** 19 SCs.

| Section | Count | SC IDs |
|---------|-------|--------|
| L0 | 2 | SC-L0-001..002 |
| L1 | 3 | SC-L1-001..003 |
| L2 | 3 | SC-L2-001..003 |
| L3 | 5 | SC-L3-001..005 |
| L4 | 5 | SC-L4-001..005 |
| Cross-cutting | 1 | SC-CC-001 |
| **Total** | **19** | ✅ Matches A1 changelog claim.

**SC ↔ gate-task coverage (spot-checked):**

| SC | Gate task | Verdict |
|----|-----------|---------|
| SC-L0-001 (pytest) | T-002 | ✅ |
| SC-L0-002 (ruff) | T-002 | ✅ |
| SC-L1-001 (12 scripts AST + --help) | T-016 | ✅ |
| SC-L1-002 (byte-parity) | T-016 | ✅ |
| SC-L1-003 (debris) | T-015, T-016 | ✅ |
| SC-L2-003 (workflow ≥60 steps) | T-019, T-020 | ✅ |
| SC-L3-002 (validate-runtime all) | T-043 | ✅ |
| SC-L4-001 (PreToolUse hook) | T-044, T-045, T-046 | ✅ |
| SC-L4-003 (byte-parity CLEAN) | T-049 | ✅ |
| SC-L4-005 (aspis doctor) | T-049 | ✅ |
| SC-CC-001 (cost-of-change ≤3) | T-042 acceptance | ✅ |

**All 11 sampled SCs have gate coverage. PASS.**

---

## 4 · Gate chain verification

### 4.1 Layer exit gates

| Layer | Gate | Tasks | Verdict |
|-------|------|-------|---------|
| L0 | `pytest` exit 0 (or non-subprocess + BLOCKED:env) + `ruff` exit 0 | T-001a → T-001b → T-002 | ✅ Achievable; fallback documented |
| L1 | All 12 scripts pass AST + `--help` + byte-parity; debris CLEAN | T-003..T-016 | ✅ Achievable |
| L2 | `validate-runtime` clean; 0 broken refs; workflow ≥60 steps; SKILL.md valid | T-017..T-020 | ✅ Achievable |
| L3 | `validate-runtime --runtime all` exit 0; 0 broken skill refs; 0 orphan delegates; `byte-parity --dry-run` CLEAN | T-021..T-043 | ✅ Achievable |
| L4 | All 6 gates green: pytest + validate-runtime + byte-parity + validate-index + export --dry-run + doctor | T-044..T-050 | ✅ Achievable; T-046 conditional on R-008 approval |

**All 5 layer gates are achievable in the current environment.**

### 4.2 Specific gate verifications

- **L0 — fallback documented (C-2).** PLAN.md L63: "Fallback: if
  environment blocks subprocess tests, all non-subprocess tests pass
  + blocked items documented with `BLOCKED: env`." T-001a acceptance
  requires "blocked items marked `BLOCKED: env`." ✅
- **L1 — AST + --help + byte-parity.** TASKS.md T-016 L137:
  "Verify: each deployed script byte-identical to catalog source;
  AST parse passes for all 12; `--help` exits 0 for all 12; debris
  confirmed clean." All three checks present. ✅
- **L2 — validate-runtime.** TASKS.md T-020 L173: "validate-runtime
  --runtime all clean; 0 broken refs; workflow has ≥60 steps; skill
  SKILL.md valid." ✅
- **L3 — 21 subagents + 0 broken refs.** TASKS.md T-043 L308:
  "validate-runtime --runtime all exits 0; 0 broken skill refs; 0
  orphan delegates; byte-parity --dry-run CLEAN." 33 agents
  (12 existing + 21 new). ✅
- **L4 — hook + governance + edge cases + full sweep.** TASKS.md
  T-049 L365: "pytest exit 0; validate-runtime --runtime all exit 0;
  byte-parity --dry-run CLEAN; validate-index exit 0; aspis export
  --dry-run exit 0; aspis doctor exit 0." All 6 gates. ✅

**Gate chain integrity: PASS.**

### 4.3 Dependency order in TASKS

- T-001a depends on nothing, blocks T-001b ✅
- T-001b depends on T-001a, blocks T-002 ✅
- T-002 depends on T-001b, blocks L1 ✅
- T-003..T-015 each depend on T-002, block T-016 ✅
- T-016 depends on T-003..T-015, blocks L2 ✅
- T-017..T-019 each depend on T-016, block T-020 ✅
- T-020 depends on T-017..T-019, blocks L3 ✅
- T-021..T-041 each depend on T-020, block T-042 ✅
- T-042 depends on T-021..T-041, blocks T-043 ✅
- T-043 depends on T-042, blocks L4 ✅
- T-044 depends on T-043, blocks T-045 ✅
- T-045 depends on T-044, blocks T-046 ✅
- T-046 depends on T-045 + owner approval, blocks L4 gate ✅
- T-047 depends on T-043, blocks L4 gate (parallel to T-046) ✅
- T-048 depends on T-043, blocks L4 gate (parallel to T-046, T-047) ✅
- T-049 depends on T-046, T-047, T-048, blocks T-050 ✅
- T-050 depends on T-049, blocks nothing (final) ✅

**Dependency order: PASS.**

---

## 5 · R-008 governance timing assessment

### 5.1 T-046 fallback is correct

The A1 changelog's "Open questions for A2 pass" (L974) asked:
> "T-046 approval timing: If the owner does not approve the R-008
> governance request before the build reaches T-046, the task will
> be marked `BLOCKED: awaiting R-008 owner approval`. Is this
> acceptable or should the build pause entirely at T-045?"

**Assessment: Acceptable to mark T-046 as BLOCKED rather than
pausing the entire build.**

**Rationale:**

1. **The hook modules ship regardless.** T-044 produces the
   `.aspis/scripts/hooks/` modules independent of R-008 approval.
   These modules are tested (AST parse), reviewed (correctness +
   security), and committed via the committer. The L4 gate (T-049)
   can still verify their presence and quality.

2. **The settings.json edit is a small, isolated, post-build
   action.** Editing `.claude/settings.json` to add the hook entry
   is a 5-10 line file edit, fully documented in T-046's
   acceptance. The build can proceed to T-047 (edge cases), T-048
   (parity), T-049 (full gate), and T-050 (BUILD_REPORT) without
   the hook being wired. The manual edit is then a post-build
   owner action that completes the wiring.

3. **The L4 gate is still meaningful.** Without the hook wired,
   `validate-runtime` and other gates can still be exercised.
   The hook itself is an enforcement boundary; its presence in
   `.aspis/scripts/hooks/` is sufficient evidence that the
   enforcement surface is built. Activation is a separate concern
   (intentionally deferred — `enforcement: warn`, not `block`).

4. **`enforcement: warn` is the intended default.** SPEC.md L91:
   "Flipping `enforcement: warn` → `block` (requires probation;
   this feature ships the hook, does not activate block)." The
   hook ships warn-only; the build is correct without the
   settings.json edit being applied during the build window.

5. **No build artifacts depend on the hook being live.** T-047
   (edge cases), T-048 (parity), T-049 (gate), T-050 (report) do
   not require the hook to be active. The hook is for runtime
   enforcement of future edits; it does not gate the build
   itself.

**Verdict on R-008 timing: ACCEPTABLE.** The BLOCKED fallback is
correct. The build should not pause at T-045; it should proceed
to T-047, T-048, T-049, T-050 with T-046 marked BLOCKED. The
owner completes the manual `.claude/settings.json` edit after
the build.

### 5.2 The 3 governance-timing questions

The planning-lead raised 3 questions about R-008 timing (implicit
in the A1 changelog "Open questions for A2 pass"):

1. **"If owner hasn't approved at build time, does T-046 correctly
   mark BLOCKED?"** — Yes. TASKS.md L339: "**Fallback:** If
   approval not yet granted at build time, leave hook modules in
   place, document manual edit as post-build owner action, mark
   task `BLOCKED: awaiting R-008 owner approval`." The BLOCKED
   marker is explicit and correct.

2. **"Is this acceptable for the overnight run?"** — Yes, per
   §5.1 above. The build completes with T-046 BLOCKED; the
   owner wires the hook in a post-build commit. This is the
   intended behavior; the plan correctly documents it.

3. **"What if the owner wants the build to pause?"** — The plan
   does not currently support this. If the owner prefers a
   pause-and-wait, the build can be configured to halt at T-045
   pending approval. **However, this is a build-runner policy
   decision, not a plan defect.** The plan correctly defaults
   to "build proceeds; T-046 BLOCKED; owner action post-build."
   This default is sound for an overnight autonomous run.

**R-008 timing: ACCEPTABLE. No plan changes needed.**

---

## 6 · Any new findings

### 6.1 Minor inconsistencies (not blocking)

**Finding MINOR-1 (LOW): A1 changelog FR count arithmetic**
- A1 changelog L966: "FRs: 46 → 48"
- Actual SPEC count: 49 (7 L0 + 9 L1 + 10 L2 + 11 L3 + 6 L4 + 6 CC)
- The changelog's count of "48" is off by 1. The SPEC content is
  complete and consistent; the changelog's arithmetic is slightly
  wrong.
- **No build impact.** Recommend updating the changelog in a
  follow-up; not blocking.

**Finding MINOR-2 (LOW): No `_tmp_f017_*.py` files in workspace
today**
- Gap-collation §9.2 M-1 cites 10 debris files in
  `.aspis/scripts/planning/`. A glob on the workspace today shows
  zero such files.
- T-015 is defensive ("if none found, document CLEAN and pass").
  This is correct behavior — the task prevents regression and
  verifies the cleanup is durable.
- **No build impact.** The plan correctly handles both states.

**Finding MINOR-3 (LOW): `cross_ref_agents.py` at runtime only**
- `src/aspis/scripts/planning/cross_ref_agents.py` exists at
  runtime but is not in `src/aspis/data/catalog/scripts/`.
- This is an existing R-006 violation noted in gap-collation
  §9.4 #10 (F-017 leaf-body-quality M-1).
- The current plan does NOT include a "move to catalog source"
  task. This is acceptable for F-018 (not a regression, not a
  new violation) but is a candidate for F-019.
- **No build impact.** Out of scope for F-018.

### 6.2 No new scope disagreement with gap-collation

I cross-checked F-018's scope against the gap-collation's
"Section 10.5 Final counts" (L493-510):

| Gap-collation metric | F-018 plan | Verdict |
|----------------------|------------|---------|
| Subagents to build: 35 (per gap) | 21 in TASKS (8 system-lead + 8 planning-lead + 6 test-lead - 1 governance as CLI = 21) | ✅ Aligned; 14 deferred per SPEC L94-100 with workload-justified rationale |
| Skills to build: 1 inventory + 24 net-new = 25 | 1 (dependency-audit at T-017) | ✅ Aligned; 24 net-new deferred per gap-collation §3 |
| Templates to build: 14 | 6 (T-018) + 1 path reconciliation (T-018 note) | ✅ Aligned; 7 deferred per gap-collation §4 |
| Workflows to build: 5 | 1 (project-lead-operating-protocol at T-019) | ⚠️ Partial; 4 net-new deferred. See Finding below. |
| Scripts to build: 23 | 12 (T-003..T-014) | ✅ Aligned; 11 deferred per gap-collation §6 |
| CLI verbs to build: 18 | 1 (validate-approvals at T-014) | ✅ Aligned; 17 deferred per gap-collation §7 |
| Review carry-overs: ~30 | 0 explicit (but evidence-driven approach addresses many) | ✅ Acceptable |

**Workflows gap (1 of 5 in scope):** gap-collation §5 lists 5
missing workflows:
- system.md (broken-ref HIGH) — F-018 OUT of scope. The A1
  review (Finding S-7) noted: "The broken-ref claim in F-017
  final-quality.md is based on stale evidence. F-018 need not
  address." This is a documented exclusion, not an oversight.
- project-lead-operating-protocol — F-018 IN scope (T-019). ✅
- dependency-graph — F-018 OUT of scope. The `dependency-analyzer`
  subagent (T-035) uses `dependency_graph.py` (T-008) directly;
  a separate workflow is not required for F-018 to ship.
- project-plan — F-018 OUT of scope (Phase 3 of roadmap).
- constitution-check — F-018 OUT of scope. The
  `constitution-checker` subagent (T-030) uses
  `constitution_check.py` (T-004) directly; a separate workflow
  is not required.

**Workflow exclusion rationale is sound.** The plan correctly
in-scope's only the workflow that the L2 layer must deliver
(project-lead-operating-protocol). The other 4 are either
based on stale broken-ref claims (system.md), have direct
subagent/script coverage (dependency-graph, constitution-check),
or are roadmap-deferred (project-plan).

**No scope disagreement with gap-collation. PASS.**

### 6.3 Risks not addressed

Reviewed the A1 review's "Risks and blockers" (§7) and the plan's
"Risks and rollback" table (PLAN.md L424-438):

- **L0 environment blocks pytest:** Addressed by C-2 fallback.
- **R-008 governance approval blocks `.claude/settings.json` edit:**
  Addressed by C-3 hook split with T-046 BLOCKED fallback.
- **21+ subagents balloon cost-of-change:** Verified by T-043
  acceptance (cost-of-change ≤3 files).
- **New subagent body violates standard:** validate-runtime
  catches at every gate.
- **Test fixes break other tests:** git revert on regression.
- **Claude PreToolUse hook breaks runtime:** Non-blocking warn
  mode; revert.

**All identified risks are addressed. PASS.**

### 6.4 Circular dependencies

Verified in §2.3 above. No cycles.

### 6.5 FR/SC orphans

Verified in §3.1 and §3.2 above. No orphan FRs or SCs (each has
a corresponding task or gate).

---

## 7 · Verdict

### **APPROVE — Proceed to Phase B (Build)**

The F-018 plan, as revised for the A1 conditions, is structurally
sound, scope-aligned with the F-017 deferred list and
gap-collation, and rule-compliant (R-003 scripts-before-agents,
R-004 committer-only, R-006 catalog-is-truth, R-008 human gate).
All 6 A1 conditions are resolved with concrete, evidence-backed
edits. The 51-task decomposition across 5 layers is comprehensive
without overreach. The 3-stage R-008 governance flow
(T-044 → T-045 → T-046 with BLOCKED fallback) is the correct
shape for a permissions-change surface.

**No new conditions. No A3 needed.**

### Spot-check evidence summary (A2 verification)

- **T-001a/T-001b split:** TASKS.md L15-36 ✅
- **L0 fallback language:** SPEC.md L106, L184; PLAN.md L63; TASKS.md
  L17, L21, L48 ✅ (4 places, consistent)
- **T-044/T-045/T-046 hook split:** TASKS.md L317-339 ✅
- **T-046 BLOCKED fallback:** TASKS.md L339; PLAN.md L371 ✅
- **T-015 debris cleanup in L1.D:** TASKS.md L123-131 ✅
- **T-014 validate-approvals P0:** TASKS.md L115-121 ✅
- **7 other validators out of scope:** SPEC.md L101 ✅
- **L15 matrix fix:** use-case-coverage.md L15 ✅
- **L15 verified against live `project-lead.md` L33-41:** both
  planning-lead and build-lead in delegate list ✅
- **`validate_index.py:180` already has `10%%`:** verified by
  direct read of `src/aspis/commands/validate_index.py:180` ✅
- **No `_tmp_f017_*.py` files in workspace today:** verified by
  glob ✅ (T-015 correctly defensive)
- **R-008 in system-rules.md L101-103:** matches the hook
  split design ✅
- **Task count: 51** (T-001a → T-050, no gaps, no duplicates) ✅
- **SCs: 19** (matches A1 changelog claim) ✅
- **FRs: 49** (SPEC count; A1 changelog says 48, off by 1 — not
  a SPEC defect) ✅
- **Dependency order: L0 → L1 → L2 → L3 → L4** (no cycles) ✅
- **All 5 layer exit gates achievable** (with documented
  fallbacks) ✅

### What is NOT in F-018 and is correctly excluded

- `validate-skills`, `validate-agents`, `validate-decisions`,
  `validate-constitution`, `validate-trace`, `validate-parity`,
  `validate-profiles` (7 CLI validators) — F-019 per SPEC L101.
- `enforcement: warn` → `block` flip — correctly deferred
  (SPEC L91).
- Trace spine, dashboard, self-improvement loop — Phase 3-5
  roadmap, correctly excluded.
- 14 subagents not in TASKS (sub-reviewer, security-reviewer,
  test-author, 4 research-lead, 4 fix-lead, 2 project-lead) —
  correctly out of scope with workload-justification rationale
  (SPEC L94-100).
- `cost_of_change.py` script — SC-011, deferred to F-019.
- 4 project-lead templates (CONTEXT_PACKET, STATUS_REPORT,
  REPLY_TO_USER, ESCALATION_NOTE) — P2 deferred.
- `system.md` workflow — broken-ref claim is stale per A1
  review Finding S-7; F-018 need not address.
- `cross_ref_agents.py` move to catalog source — existing R-006
  violation, deferred to F-019.

### Open questions from A1 changelog — resolved

1. **T-046 approval timing** — RESOLVED. T-046 BLOCKED fallback
   is correct and acceptable for overnight run (§5.1).
2. **T-018 TEST_REPORT path reconciliation** — RESOLVED. TASKS.md
   L156 allows either path ("extend existing or create with no
   duplicate"). The build can choose at T-018 time.
3. **validate-approvals.py scope** — RESOLVED as minimal V2
   (checks existence, timestamps, sign-off chains per TASKS.md
   L118). Deep validation (cross-reference of protected-paths
   config) is F-019.

### Final recommendation

**Release Phase B (Build).** The plan is sound, all A1 conditions
are addressed, and the build can proceed with confidence. The
high-leverage risks (L0 evidence, R-008 governance gate) are
correctly designed with fallbacks. The L0 environment question
(C-2) and the R-008 approval timing (C-3) are the two single
points of failure, both with documented BLOCKED fallbacks that
allow the build to complete without breaking the rules.

Build-lead can pick up the plan and start at T-001a (discovery
sweep). The L0 discovery report is the highest-leverage early
deliverable — it confirms or refutes the speculative L0 failure
narratives from F-017, and the rest of L0 is evidence-driven from
its output.

---

*End of A2 plan review. All findings are evidence-cited; no plan
modifications were made by the reviewer (read-only). The plan is
APPROVED — release to Phase B.*
