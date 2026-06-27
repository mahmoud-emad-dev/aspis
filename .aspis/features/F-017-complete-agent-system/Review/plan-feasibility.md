# F-017 — Plan-Feasibility Review

> **Reviewer:** Reviewer (independent quality authority)
> **Mode:** production
> **Scope:** `.aspis/features/F-017-complete-agent-system/{SPEC.md, PLAN.md, TASKS.md}`
> **Perspective:** plan feasibility & integrity — sequencing, dependencies, hidden blockers, structural correctness.
> **Date:** 2026-06-27
> **Verdict:** **REJECT** — 3 CRITICAL issues, 5 HIGH issues. Plan is structurally sound but contains path and design-divergence errors that will surface as build-time blockers or as silent scope drift.

---

## Executive summary

The 56-task plan is well-layered (L0 → L1 → L2-P0 → L2-P1 → Polish), follows a defensible cost-of-change rationale, and most sequencing is correct. However, three blocking issues prevent a clean build:

1. **CRITICAL — CLI path mismatch.** All L2-P0 / L2-P1 CLI-verb tasks (T-33, T-34, T-35, T-52, T-53, T-54) target a non-existent `src/aspis/cli/` directory. The actual pattern is `src/aspis/commands/<verb>.py` with a `register(subparsers)` contract; `src/aspis/cli.py` (the existing single-file dispatcher) would conflict with a new `cli/` package of the same name. The plan silently contradicts the architecture constitution's "plugin-first / new files over core edits" rule.
2. **CRITICAL — Governance CLI signature divergence from F-016 design.** T-36 (governance) is described with positional-argument subcommands (`request <path> <reason>`, `approve <request-id>`, `revoke <request-id>`), but F-016's `Research/ref/governance.md` §6 specifies flag-based, multi-arg, identity-bearing signatures (`approve --paths <paths> --reason <reason> --approver <id> [--expiry] [--glob-approval]`). F-017's stated assumption (SPEC.md:133) is that F-016 designs are authoritative — the plan violates its own assumption.
3. **CRITICAL — `aspis export` and `aspis byte-parity` duplicate existing functionality.** A robust export pipeline (`aspis init` + `src/aspis/export.py` + the 6-way protection engine in `src/aspis/protect.py`) already exists. The plan adds a parallel `aspis export` verb without explaining how it relates to `aspis init` — this is the same kind of special-case the constitution forbids.

Five HIGH issues follow: workflow-path ambiguity, missing `cross_ref_agents.py` script dependency, the unbuildable L1 end-to-end exit gate, a miscounted L0 skill heading ("Six" / 7), and the T-32 "HARD STOP" being a soft textual gate rather than an enforced one. The plan can be salvaged by fixing these six items; nothing structural needs to be rebuilt.

---

## Findings

### CRITICAL-1 — CLI verbs target a non-existent directory `src/aspis/cli/`

**Where:**
- PLAN.md:150 — "Three P0 CLI verbs implemented as deterministic Python scripts under `src/aspis/cli/`"
- PLAN.md:169 — "Governance module | `src/aspis/cli/governance.py`"
- TASKS.md:100, 101, 102, 105, 138, 139, 140 — file paths `src/aspis/cli/validate_runtime.py`, `byte_parity.py`, `export.py`, `governance.py`, `validate_index.py`, `drift.py`

**Evidence (filesystem):** No `src/aspis/cli/` directory exists. The actual pattern is `src/aspis/commands/<verb>.py` (a module exposing `register(subparsers)`), with `src/aspis/cli.py` as the dispatcher and `src/aspis/commands/__init__.py` owning a `COMMAND_MODULES` tuple that registers them. `src/aspis/cli.py` is a *file*, not a *package* — creating `src/aspis/cli/` would create a name collision (Python cannot have both `cli.py` and `cli/` in the same package).

**Why it matters:** The plan's CLI-verb tasks cannot be built as written. Either:
- the plan must change paths to `src/aspis/commands/<verb>.py` and add each verb to `COMMAND_MODULES` (the standard pattern); or
- the plan must rename the existing `src/aspis/cli.py` (a core edit that breaks the architecture-constitution rule "new files over core edits").

The plan gives no second option, so the first is the fix. Estimated fix: edit ~10 file paths and add registration entries.

**Severity rationale:** A CRITICAL finding is a blocker that prevents build from starting. Six of 56 tasks cannot be built as described.

---

### CRITICAL-2 — Governance subagent signatures diverge from F-016 design

**Where:**
- PLAN.md:174-181 — describes `request <path> <reason>`, `approve <request-id>`, `revoke <request-id>` as positional single-arg subcommands
- TASKS.md:105 — T-36 says "6 subcommands (`request`, `approve`, `audit`, `revoke`, `check`, `ledger`); exact-match path check against protected paths set"

**Evidence (F-016 design):** `Research/ref/governance.md` §6 (line 431+) defines, verbatim from the spec:
- `request --path <path> [--reason <reason>]` (line 442) — flag-based, multi-path, **passive** (no positional)
- `approve --paths <paths> --reason <reason> --approver <id> [--expiry <iso8601>] [--glob-approval]` (line 458) — required flags, identity-bearing
- `revoke --id <APRV-NNN> --reason <reason> [--approver <id>]` (line 497) — flag-based, reason required

**Why it matters:** F-017 SPEC.md:133 states "F-016 designs are authoritative and locked. F-017 builds to them, does not redesign." The plan's governance CLI is a redesign that drops:
- `--approver <id>` (the human identity — the R-008 invariant)
- `--expiry` (TTL on approvals)
- `--glob-approval` (the dangerous-extension flag the F-016 spec calls out as "explicitly opt-in")
- The `approver` field in the ledger (governance.md §4)

Without `--approver`, the R-008 gate becomes anonymous; the approval is no longer traceable to a human, which is the entire point of R-008.

**Severity rationale:** T-36 is R-008 territory; redesigning the R-008 mechanism is exactly the kind of change R-008 is supposed to gate. The plan contradicts itself.

---

### CRITICAL-3 — `aspis export` and `aspis byte-parity` duplicate existing functionality without acknowledgement

**Where:**
- TASKS.md:101 — T-34 "Build `byte-parity` CLI verb — renders each catalog agent for target runtime; compares to live file; reports CLEAN/CONFLICT/PROTECT"
- TASKS.md:102 — T-35 "Build `export` CLI verb — renders all catalog agents for target runtime(s); applies protection engine (CONFLICT/PROTECT); `--dry-run`"

**Evidence (existing code):**
- `src/aspis/export.py` (549 lines) — `plan_export` and `write_export`, full pipeline with protection engine integration
- `src/aspis/protect.py` — the 6-way `DecisionKind` (ADD / UNCHANGED / UNKNOWN / UPDATE / PROTECT / CONFLICT) decision engine
- `src/aspis/commands/init.py` — `aspis init` already exposes `--dry-run`, `--write`, `--check`, `--strict`, `--force-conflicts`, `--reset-snapshot`; the `aspis init --check` invocation produces exactly the per-target CLEAN/CONFLICT/PROTECT decisions T-34 and T-35 are designed to produce

**Why it matters:** Adding a parallel `aspis export` and `aspis byte-parity` without explaining the relationship to `aspis init` creates a special case. A user who runs both will see different (or duplicate) output for the same catalog. The plan needs to either:
- (a) make T-34 / T-35 thin wrappers that delegate to existing `plan_export` / `write_export` (good — honors architecture constitution's "new files over core edits"), or
- (b) explicitly deprecate / replace `aspis init`'s export flags and document the migration (also acceptable, but requires touching `commands/init.py`)

**Severity rationale:** Silent duplication of a 549-line module is a constitution violation and a maintenance trap.

---

### HIGH-1 — Workflow file paths are ambiguous; source vs. deployed location not specified

**Where:**
- TASKS.md:26-30 — T-02 to T-06 reference `.aspis/workflows/plan.md`, `build.md`, `review.md`, `fix.md`, `small-task.md`

**Evidence (filesystem):** The catalog source lives at `src/aspis/data/catalog/workflows/{plan,build,review,fix,small-task,bootstrap}.md` (six files, not five — `bootstrap.md` exists too). The `.aspis/workflows/` path is the deployed brain copy, produced by `aspis init`, which does not yet exist in this project (the active feature is F-016, not F-017). T-02-T-06 do not say which path to verify.

**Why it matters:** "Verify `.aspis/workflows/plan.md`" against an existing reference spec is the *deployed* copy, which doesn't exist yet. "Verify `src/aspis/data/catalog/workflows/plan.md`" is the *source* copy, which is what ships. The plan should be explicit (and T-01 / T-07 should add a workflow deployment step if the deployed copy is the target).

**Severity rationale:** Ambiguity in 5 of 56 tasks; easy fix.

---

### HIGH-2 — T-31 / T-32 depend on `cross_ref_agents.py` that is not in the deploy list

**Where:**
- PLAN.md:271 — `python .aspis/scripts/planning/cross_ref_agents.py  # if it exists; else manual check`
- TASKS.md:89 — T-31 "Run manual cross-reference check across all 8 agent bodies"

**Evidence (filesystem):** `cross_ref_agents.py` is not in `src/aspis/data/catalog/scripts/planning/` (the deploy source for T-01). F-016 BUILD_REPORT.md:72 references this script as a T-02 deliverable, but it is not deployed to `.aspis/scripts/planning/` by F-017's T-01, nor is there a task that builds it.

**Why it matters:** T-31 and T-32 are the L1 exit gate. Their core job is "verify 0 broken skill references across all 8 lead frontmatters; verify every delegate listed in a body exists as a catalog agent; verify no agent has `bash: '*': allow`; verify all deny-floor permissions honored" (TASKS.md:89). The plan explicitly drops to "manual" if `cross_ref_agents.py` doesn't exist. A 16-criterion manual sweep across 8 lead bodies is fragile and review-time-invisible.

**Severity rationale:** Either add a task to build/deploy `cross_ref_agents.py`, or replace T-31 with a deterministic cross-ref check that exists by then (e.g., `aspis validate-runtime` itself, but that's T-33 — post-L1).

---

### HIGH-3 — L1 exit gate (T-32) is unverifiable as described; requires post-L2 machinery

**Where:**
- PLAN.md:142 — "**L1 exit gate**: A sample feature runs plan→build→review→commit end-to-end on cheap/standard models."
- TASKS.md:90 — T-32 "**L1 EXIT GATE** — run plan→build→review→commit end-to-end on a sample feature using only cheap and standard model tiers. Verify: planning-lead plans → build-lead delegates to builder → reviewer reviews → committer commits. All gates pass. 0 deep model invocations. **HARD STOP — owner reviews before L2 begins. Do NOT roll into T-33.**"

**Why it matters:** The end-to-end loop requires:
- Planning-lead producing packets (`task_compile.py`, deployed in T-01) — T-32 can run after T-01
- Build-lead delegating to a builder (no new infrastructure)
- Reviewer reviewing (no new infrastructure)
- Committer committing (`aspis commit`, exists today) — T-32 can run

So in principle, T-32 is buildable from L0+L1 assets only. The plan's framing ("plan→build→review→commit runs end-to-end") is achievable. **But** "All gates pass" is undefined: which gates? The four system gates (`aspis validate-runtime`, `aspis byte-parity`, `aspis export --dry-run`, governance `check`) are all L2-P0 work. The L1 gate is the planning-loop gate (`prereq_validate.py --phase build`) plus the per-task review loop.

**Concrete defect:** "0 deep model invocations" is not enforceable from inside the planning loop. A `model: deep` agent (none exist as primary; the reviewer can drop to deep for V3-V4 packets) could be invoked, and the gate would have to be checked externally (via `aspis models` or by inspecting the run log, neither of which is named).

**Severity rationale:** A vague exit gate is worse than a missing one; the L1 owner-review checkpoint will not be evaluable.

---

### HIGH-4 — Internal inconsistency: PLAN.md says "Six P0 skills" but the table and TASKS.md both have 7

**Where:**
- PLAN.md:89 — "Six P0 skills that are prerequisites for the core loop, authored to the catalog pattern:"
- PLAN.md:91-100 — table lists **7** skills: mode-decision, recontextualization, constitution-checks, constitution-check, evidence-validation, packet-validation, builder-selection
- TASKS.md:41-47 — T-09 to T-15 = **7** L0 skills
- F-016 inventory (`Research/skills/inventory.md:90-91`) — 13 P0 skills total: 7 in L0 + 6 in L1 (cache-management, catalog-validator, drift-detector, governance-approval, harvest-protocol, security-review) = 13 ✓

**Why it matters:** A trivial typo, but it propagates: the Architecture diagram in PLAN.md:30-45 cites "6 shared P0 skills" in the L0 block. F-017 SPEC.md:13 says "the 13 P0 skills" but PLAN.md L0 block says 6. The total is correct; the heading and the L0 architecture block are wrong.

**Severity rationale:** Documentation defect that misleads at the gate review; trivial fix.

---

### HIGH-5 — T-32 "HARD STOP" is a soft textual checkpoint, not an enforced gate

**Where:**
- TASKS.md:90 — "**HARD STOP — owner reviews before L2 begins. Do NOT roll into T-33.**"
- PLAN.md:142 — "**L1 exit gate**: ... This is a hard gate — owner reviews at this checkpoint before L2 begins."

**Why it matters:** There is no machine-checked enforcement of this gate. The only mechanism is the textual order in TASKS.md. A builder agent could mark T-32 done and proceed to T-33. The plan needs one of:
- a T-32a review file at `.aspis/features/F-017-complete-agent-system/Review/owner-approval-<date>.md` whose existence is gated by a script (e.g., a `prereq_validate.py --phase l2` that requires the review file)
- a `commit-msg` hook that blocks `fix(F-017/T-3x..T-5x)` commits until the review file is present
- a task prerequisite in the artifact system (`aspis artifact review --task T-33` requires `T-32` review verdict)

The plan should specify which. The SPEC.md Clarification Q2 says "Hard gate in PLAN, not soft checkpoint" — the current PLAN is the latter.

**Severity rationale:** A "HARD STOP" with no machine enforcement is the exact R-008 territory the rest of the system takes seriously. The plan should hold itself to the same standard.

---

### MEDIUM-1 — `task_compile.py` works on the F-017 task list, but the chicken-and-egg the user asked about is real for the sample feature

The user explicitly asked about T-01 building `task_compile.py` which would compile its own tasks. **Answer:** No actual chicken-and-egg exists for F-017's own tasks — `task_compile.py` is not used to compile F-017's 56 tasks; those are pre-planned. It is used for the sample feature in T-32.

However, the *sample feature* in T-32 has its own constraint: `task_compile.py` reads `TASKS.md` and renders packets into `.aspis/features/<id>/tasks/`. The sample feature must therefore (a) use the standard `feature_scaffold.py` to create a feature dir, (b) have `SPEC/PLAN/TASKS` templates, (c) author a `TASKS.md` (any trivial work item, e.g. "add a comment to README"), (d) run `task_compile.py` to produce packets, (e) proceed.

**Issue:** The templates at `src/aspis/data/catalog/templates/planning/{SPEC,PLAN,TASKS,TASK_PACKET,ACCEPTANCE}.md` (5 files) need to be deployed alongside the planning scripts. T-01 only deploys the 5 `.py` files; no task deploys the templates. Without templates, `feature_scaffold.py` will fail at "copies SPEC/PLAN/TASKS from `.aspis/templates/planning/`" (line 11 of `feature_scaffold.py`).

**Severity:** Real hidden dependency. Add a T-01a: deploy planning templates from `src/aspis/data/catalog/templates/planning/` to `.aspis/templates/planning/`.

---

### MEDIUM-2 — `session-continuation` moved from P1 to L1 with insufficient justification

**Where:**
- PLAN.md:133 — "| project-lead | `session-continuation` (P1, but can stub P0) |"
- TASKS.md:58 — T-16 schedules session-continuation as a US2 (L1) task

**Why it matters:** F-016 inventory rates session-continuation P1 (line 103 of `inventory.md`). The F-016 project-lead ref spec rates it "Medium" (line 83 of `project-lead.md`). F-017's L1 exit gate is "plan→build→review→commit runs end-to-end" — that loop does not require interruption handling. The skill is needed for *robust* orchestration, not basic orchestration. Pulling it into L1 expands the L1 deliverable from "core loop works once" to "core loop works across interruptions" without an explicit claim in SPEC.md.

**Severity:** Scope creep on a single L1 task; easy fix (defer to L2-P1) but worth flagging.

---

### MEDIUM-3 — Existing agent frontmatters already reference skills T-09..T-15 will author

**Where (catalog evidence):**
- `src/aspis/data/catalog/agents/build-lead.md:51-52` — references `packet-validation` and `builder-selection` in frontmatter
- `src/aspis/data/catalog/agents/planning-lead.md:61-62` — references `mode-decision` and `constitution-checks` in frontmatter

**Why it matters:** Until T-09..T-15 author these skills, the frontmatters are technically broken (no `SKILL.md` exists for them). The L0 validation gate (T-15's checkpoint at "Each has valid frontmatter + required sections") resolves this, but the L1 agents that depend on these skills (T-18, T-19) are not blocked on the skills. They will, however, fail any structural check against the agent body standard ("Every skill an agent's frontmatter references MUST exist"). The plan should sequence L0 skill authoring before the L1 agent bodies that reference them (T-09..T-15 before T-18, T-19). The current order does — but T-15's checkpoint gate should be explicitly named as a prerequisite for T-18/T-19, not implied.

**Severity:** Sequencing is correct; the explicit gate is missing. One sentence fix in PLAN.md.

---

### MEDIUM-4 — T-29 (harvest-protocol) is L1; the mechanism it describes (R-008 / governance) is L2-P0

**Where:**
- TASKS.md:85 — T-29 is US2 (L1)
- TASKS.md:105 — T-36 (governance) is US3 (L2-P0)

**Why it matters:** `harvest-protocol` is the 7-step R-008-gated path for bringing external skill/source into the catalog. R-008 is enforced by governance. The skill is defined in L1; the mechanism it relies on is built in L2-P0. The skill can be authored (it describes the workflow), but until governance is built, harvest-protocol cannot run. The plan should either:
- (a) note explicitly that `harvest-protocol` is **authored but inactive** until T-36 lands, or
- (b) move harvest-protocol to L2-P0 (but that contradicts F-016's P0 priority for it)

**Severity:** Documentation defect, not a build blocker.

---

### MEDIUM-5 — T-55 packs 16 sub-changes into one task

**Where:** TASKS.md:143 — "for each of the 8 leads, add at least 2 error-handling / edge-case sections drawn from the agent's reference spec"

**Why it matters:** 8 agents × ≥2 edge-case sections = ≥16 body edits. The plan groups them into a single task with a single review. Per-agent review (T-21 reviewer body, T-25 system-lead body, etc.) is a one-shot pattern; per-agent edge-case work should mirror that. The review-routing table (TASKS.md:169-173) puts T-55 in "Low" (self-check against catalog pattern), which is wrong for a 16-section change.

**Severity:** Review-depth mismatch; one-line fix in TASKS.md.

---

### MEDIUM-6 — T-01 description miscounts: "3 planning scripts" but 5 files deploy

**Where:** TASKS.md:25 — "Deploy 3 planning scripts from catalog source to `.aspis/scripts/planning/` — byte-for-byte copy from `.../feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `_console.py`, `active_feature.py`"

**Why it matters:** 5 files are listed; the description says "3 scripts" (the public-API count). This matches PLAN.md:75 which also says "4 files" but lists 5. Cosmetic, but a future task-assignment or status check will get the count wrong.

**Severity:** Documentation defect.

---

### MEDIUM-7 — T-37, T-38, T-39 (leaf agents) under-scope what is actually a re-author

**Where:** TASKS.md:108-110 — "verify against agent body standard; verify 3 existing skills ... resolve; add Identity / How you work / Core rules / Responsibilities→skills / Delegation (none — leaf) / Dynamic-readiness sections"

**Evidence (catalog):** None of the 3 leaf agents currently have How you work, Core rules, Responsibilities→skills, Delegation, or Dynamic-readiness sections. They have only Identity. "Add 5 sections × 3 agents" is not "verify" — it is author-from-scratch.

**Severity:** Scope misnomer. The description should be "Finalize" (not "verify") because the work is substantive.

---

### MEDIUM-8 — R-008 / reviewer routing under-scoped for T-36 (governance)

**Where:** TASKS.md:170 — "T-33, T-34, T-35, T-36 = Reviewer lead (full review)"

**Why it matters:** T-36 is the R-008 mechanism. R-008 (`system-rules.md:101-103`) requires human approval for "Architecture, rules, permissions, security posture, and model-routing changes." Building the R-008 mechanism is a permissions + rules + security change; under R-008, this is the **highest** R-008 trigger. Reviewer-led review is appropriate for content quality, but the plan does not name the **human approval** the F-016 governance spec calls for at the gate. SPEC.md:290 ("Decisions needing approval") lists the governance subagent design and the protected-paths set as needing owner approval; the same approval should gate T-36 itself.

**Severity:** R-008 self-application gap.

---

### LOW-1 — Model-tier alignment with F-016 not in any T-17..T-30 task

F-016 reference specs assign per-agent tiers (project-lead=standard, build-lead=standard, reviewer=standard default with deep for V3-V4, etc.). TASKS.md T-17..T-30 verify permission surface and delegation but not model tier. The F-017 architecture-constitution rule and R-007 (pinned models) require that the declared tier matches the design. One bullet per task would close the gap.

---

### LOW-2 — T-56 over-broad final sweep

TASKS.md:152 — T-56 sweeps SC-001..SC-012. SC-001..SC-006 are already verified in T-40 / T-31; T-56 should focus on SC-007..SC-012 (governance, scope, edge cases) and route by SC-### to the responsible phase gate. Splitting T-56 into per-SC verifications would also make its review deterministic.

---

### LOW-3 — Risk coverage of PLAN risks — coverage is partial

- **Risk 1** (P0 skill design too thin) → mitigated in §Risks. **No task verifies this** (T-09..T-15 each take a single skill; there is no cross-skill consistency task).
- **Risk 2** (Claude adapter fix reveals deeper issues) → mitigated; T-35 explicitly scopes to `permission:` block. **Good.**
- **Risk 3** (L1 exit gate fails on unanticipated integration) → mitigated; "fix as part of L1." **Acceptable but vague.**
- **Risk 4** (ref spec contradiction with live code) → mitigated; "resolve in favor of ref spec." **No escalation path to F-018** for cases the ref spec can't decide.

**Severity:** Mitigations are present but uneven; the contradiction-resolution path for Risk 4 should be tied to F-018 (L3 follow-up), not the same feature.

---

## Cross-artifact consistency (plan-critic checklist)

| Check | Result | Notes |
|---|---|---|
| Every FR-### maps to ≥1 task | **PASS** | 19 FR-###, all covered (some are multi-task: FR-004 permission surface is verified in T-17..T-30 + T-37..T-39) |
| Every task maps to ≥1 FR-### or US | **PASS** | All 56 tasks have [US?] tags; orphan tasks: none |
| Every SC-### is observable | **PASS** | 12 SC-###, all measurable |
| Every SC-### is verified by some task | **PASS** | T-31, T-32, T-40, T-56 cover all 12; T-40 covers SC-003..005, T-31 covers SC-006, T-56 covers the rest |
| Plan approach delivers SPEC scope | **PARTIAL FAIL** | L2-P0 includes the 3 P0 CLI verbs; L2-P1 includes 3 P1 verbs. The plan builds them as net-new code paths rather than as wrappers over existing `aspis init` / `src/aspis/export.py`. See CRITICAL-3. |
| Phases respect dependencies | **PASS** | L0 → L1 → L2-P0 → L2-P1 → Polish ordering is correct. [P] tasks within a phase touch different files. |
| [P] tasks truly parallel | **MOSTLY PASS** | T-02..T-06 touch different workflow files ✓; T-09..T-15 touch different skill files ✓; T-41..T-51 (12 skills) all touch different files ✓. Exception: T-46 is the only reviewer P1 skill; T-43 (finding-format) and T-46 (scope-compliance) both belong to reviewer and reference each other's inputs in their Anti-patterns. This is fine — they are independent files. |
| Tests precede implementation | **PASS** | T-01 deploys scripts; their validation (`--help` / AST parse) is the first task's gate. L1 gate (T-32) is the integration test. T-40 and T-56 are the systemic acceptance. |
| No `[NEEDS CLARIFICATION]` survives | **PASS** | SPEC.md:152 "Open questions — None remaining." |
| R-008 self-application | **PARTIAL FAIL** | See MEDIUM-8 |
| Architecture constitution (cost-of-change ≤ 3) | **PASS** | PLAN.md:49 documents the 3-file add-cost |

---

## Phasing & dependency review (specifics the user asked about)

### 56-task sequencing

- **Phase 0 (T-01..T-06) — L0 Setup:** Scripts deploy, workflows verify. **Correctly sequenced**; T-01 must complete before any T that uses the scripts. T-02..T-06 are independent of each other. ✓
- **Phase 1 (T-07..T-15) — L0 Foundational:** Conventions + 7 shared P0 skills. T-07 and T-08 (convention docs) are foundational; T-09..T-15 (skills) can be parallel. **Correctly sequenced.** ✓
- **Phase 2 (T-16..T-32) — L1 Per-Lead:** 8 leads, each gets a body + own P0 skills. **Correctly parallelizable** after L0. The skill-before-body ordering within each lead is correct (T-16 before T-17, T-20 before T-21, etc.). T-31 (cross-ref) and T-32 (exit gate) are the integration step. ✓
- **Phase 3 (T-33..T-40) — L2-P0:** 3 P0 CLI verbs, governance, 3 leaf agents. **T-33, T-34, T-35 are parallel**; T-36 (governance) is independent; T-37, T-38, T-39 (leaf agents) are parallel; T-40 is the integration check. **But** — see CRITICAL-1 (paths) and CRITICAL-3 (duplication).
- **Phase 4 (T-41..T-55) — L2-P1:** 6 P1 + 5 P2 skills, 3 P1 verbs, edge cases. **T-41..T-46 and T-47..T-51 are 11 parallel skill authoring tasks.** T-52, T-53, T-54 (P1 verbs) are sequential after T-33..T-35 establish the CLI pattern. T-55 (edge cases) is post-Phase-2 body work. **Correct ordering**, but T-55 over-scope (MEDIUM-5).
- **Phase 5 (T-56) — Polish:** Final sweep. **Correctly the last task.** ✓

### L1 hard gate enforceability (T-32)

- **Answer: NO — it is a soft textual gate.** See HIGH-5.
- The plan text says "HARD STOP — owner reviews before L2 begins. Do NOT roll into T-33." (TASKS.md:90) but no machine check enforces it. A builder agent that marks T-32 done (or the owner who runs T-33 immediately) bypasses the gate.
- **Fix options:** Add a T-32a owner-approval task; add a `preflight --phase l2` script that checks for the approval file; or document explicitly that this is a *human-driven* gate (R-008-style) and rely on the committer-agent's review trail.

### Bootstrap chicken-and-egg (T-01 + task_compile)

- **Answer: No real chicken-and-egg** for F-017's own tasks (F-017 was planned with text, not task_compile). **But** a real hidden dependency: `feature_scaffold.py` (deployed in T-01) needs the planning templates at `.aspis/templates/planning/{SPEC,PLAN,TASKS,TASK_PACKET,ACCEPTANCE}.md`. T-01 only deploys the `.py` files. **Add a T-01a (or extend T-01) to deploy the 5 templates from `src/aspis/data/catalog/templates/planning/`.** See MEDIUM-1.

### Skill build ordering (L0 → L1)

- **L0 skills block the right L1 leads:** ✓
  - `packet-validation` + `builder-selection` (T-14, T-15) → build-lead body (T-19) ✓
  - `mode-decision` + `constitution-checks` (T-09, T-11) → planning-lead body (T-18) ✓
  - `constitution-check` + `evidence-validation` (T-12, T-13) → reviewer body (T-21) ✓
  - `recontextualization` (T-10) → project-lead body (T-17) ✓
- **L1 skills do not block each other.** ✓
- **L1 P0 skills (T-16, T-20, T-22..T-24, T-28, T-29) are all body-precedents.** ✓
- **No L1 skill is blocked on an unbuilt L0 skill.** ✓

### CLI verb dependencies

- **T-33 (`validate-runtime`) — needs:** catalog agent files (exist ✓), frontmatter parsing (catalog.py exists ✓), the agent-body standard (T-07 in L0 ✓). **Buildable as designed, except for the path issue (CRITICAL-1).**
- **T-34 (`byte-parity`) — needs:** the rendering logic (in `src/aspis/export.py` ✓), the protection engine (in `src/aspis/protect.py` ✓), the live runtime files (`.opencode/agents/`, `.claude/agents/` — **do not exist yet**; deployment is post-F-017 per SPEC.md:29). **T-34 will pass against the catalog but cannot verify live byte-parity** until the owner runs `aspis export`. **The L2-P0 gate (T-40) "byte-parity --runtime opencode exits 0" is therefore not achievable in F-017; it is achievable after the owner runs export.** **Hidden blocker.** See HIGH-3.
- **T-35 (`export`) — needs:** same as T-34 + the Claude Code adapter permission-block fix (F-016 cross-runtime.md §4 spec). The fix lives in either the adapter (if it exists in `src/aspis/runtimes/`) or the export's Claude render path. **The plan says "the fix lives in the adapter code (if it exists) or in the export verb's Claude render path" (PLAN.md:161).** Verify that `src/aspis/runtimes/` has a Claude adapter before T-35 begins.

### Task packet versioning (V0–V4)

- T-14 (packet-validation skill) explicitly mentions "V0–V4 maturity scaling." **Correct per F-016 design** (see `Research/ref/build-lead.md:208-214` and `planning-lead.md:619-627`).
- **No V0–V4 versioning in T-15 (builder-selection)** — but builder-selection *is* about picking the right tier per packet version. T-15 should also reference V0–V4. The F-016 design has it; the F-017 task description omits it. **Small fix: add "V0–V4 tier selection" to T-15's description.**

### Review routing

- **T-33, T-34, T-35, T-36 = "Reviewer lead (full review)."** Correct for the 3 CLI verbs. T-36 (governance) is R-008 territory — should add an R-008 owner-approval step in addition to the reviewer check. See MEDIUM-8.
- **T-17..T-30, T-37..T-39 = "Sub-reviewer or peer check."** Reasonable for body finalization.
- **T-41..T-56 = "Self-check against catalog pattern."** **T-55 should be promoted to "Sub-reviewer or peer check"** (it has 16 sub-changes; see MEDIUM-5).

### Agent body sequencing (plan→build→review→commit at L1 exit)

- The plan claims "All gates pass" at T-32. The four *envisaged* gates are:
  1. `prereq_validate.py --phase build` (deployed in T-01) ✓
  2. `aspis preflight` (exists ✓)
  3. Per-task review loop (build-lead delegates, reviewer reviews) ✓
  4. Per-task commit via committer (exists ✓)
- **All four exist or will exist after T-01.** T-32 is buildable from L0+L1 assets only. **No systemic gate is required at L1.** The systemic gates (`validate-runtime`, `byte-parity`, `export --dry-run`, governance) are L2-P0 work and run at T-40. **T-32 is achievable, with HIGH-3 caveats resolved.** ✓

### Hidden blockers

1. **Live runtime files do not exist.** F-017 explicitly defers `aspis export` regeneration to the owner (SPEC.md:29, CLARIFICATION Q3). T-34 and T-35 will run against the catalog; byte-parity against live files requires the owner to first run `aspis export`. T-40's gate ("`aspis byte-parity --runtime opencode` exits 0") is therefore **not achievable inside F-017**; it is achievable after the owner runs export post-F-017. The plan needs to either:
   - (a) document T-40's `byte-parity` gate as deferred to post-F-017 export, or
   - (b) add a T-40a: owner runs `aspis export` before T-40, or
   - (c) re-scope `byte-parity` to catalog-only ("catalog regenerates itself") and defer live byte-parity to F-018.
2. **T-01 doesn't deploy planning templates.** See MEDIUM-1.
3. **`cross_ref_agents.py` not in deploy list.** See HIGH-2.

### Risk coverage in TASKS

See LOW-3 above. The risks in PLAN.md:276-283 are partially mapped to tasks. **No task explicitly addresses "ref-spec contradiction with live code" (Risk 4) — this should escalate to F-018 rather than the same feature.**

---

## Recommendation

**VERDICT: REJECT**

### Conditions for re-approval

1. **CRITICAL-1:** Replace all `src/aspis/cli/<verb>.py` paths with `src/aspis/commands/<verb>.py` and add explicit registration via `COMMAND_MODULES` in `src/aspis/commands/__init__.py`. Document the convention in a comment in T-33 / T-34 / T-35 / T-52 / T-53 / T-54.
2. **CRITICAL-2:** Rewrite T-36's task description to match F-016 governance spec §6 signatures verbatim. List the dropped fields (`--approver`, `--expiry`, `--glob-approval`) and either retain them or document the explicit divergence under R-008.
3. **CRITICAL-3:** Either (a) rewrite T-34 and T-35 as thin wrappers over existing `aspis init` / `src/aspis/export.py`, or (b) explicitly migrate `aspis init`'s export flags into the new `aspis export` verb and deprecate the old flags. Either path requires touching `commands/init.py`.
4. **HIGH-1:** Make T-02..T-06 explicit about the source path (`src/aspis/data/catalog/workflows/<name>.md`).
5. **HIGH-2:** Add a T-31a task: build/deploy `cross_ref_agents.py` to `.aspis/scripts/planning/`, or replace T-31 with the equivalent `aspis validate-runtime` check (after T-33) and add a separate T-31b manual pre-check.
6. **HIGH-3:** Specify which gates T-32 verifies. "All gates pass" must enumerate the four L0/L1 gates (`prereq_validate.py`, `aspis preflight`, per-task review, committer); the four systemic L2-P0 gates are out of scope at L1.
7. **HIGH-4:** Fix the "Six P0 skills" → "Seven P0 skills" count in PLAN.md (lines 30, 89).
8. **HIGH-5:** Add a T-32a owner-approval task with a file artifact at `.aspis/features/F-017-complete-agent-system/Review/owner-approval-<date>.md`. Make T-33 dependent on T-32a's existence in the artifact system.
9. **MEDIUM-1:** Extend T-01 (or add T-01a) to deploy `src/aspis/data/catalog/templates/planning/*.md` to `.aspis/templates/planning/`.
10. **MEDIUM-2:** Either defer T-16 (session-continuation) to L2-P1 or add a sentence in SPEC.md justifying its L1 placement.
11. **MEDIUM-4:** Note in T-29's description that harvest-protocol is **authored but inactive** until T-36 lands.
12. **MEDIUM-5:** Promote T-55 to "Sub-reviewer or peer check" in the review-routing table.
13. **MEDIUM-6:** Fix T-01 count (5 files, not 3 scripts).
14. **MEDIUM-7:** Rename T-37, T-38, T-39 from "Finalize" to "Author and finalize" — they are re-author, not verify.
15. **MEDIUM-8:** Add an R-008 owner-approval step to T-36 (in addition to reviewer check).

After these 15 fixes, the plan is mechanically sound. The phasing, L0/L1/L2 split, [P] parallelization, gate structure, and SPEC↔PLAN↔TASKS traceability are all correct; the defects are concentrated in (a) the CLI path, (b) the governance redesign, and (c) the export duplication. All three are localizable, single-author fixes that do not require a structural rewrite.

---

## Appendix — quick numeric checks

- **Tasks per phase:** Phase 0: 6, Phase 1: 9, Phase 2: 17, Phase 3: 8, Phase 4: 15, Phase 5: 1 = **56 ✓**
- **FR-### coverage:** 19 requirements, all traced (T-09..T-15 cover 7 of 13 P0 skill FRs; T-16, T-20, T-22..T-24, T-28, T-29 cover 6 more; T-41..T-51 cover the P1/P2; T-33..T-39 cover CLI verbs; T-07, T-08 cover conventions; T-31, T-40, T-56 cover acceptance gates).
- **SC-### coverage:** 12 success criteria, all traced to T-31, T-32, T-40, T-56.
- **P0 skills scheduled:** L0 = 7, L1 = 6 = **13 ✓** (matches F-016 inventory)
- **P1 skills scheduled:** L1 (T-16, session-continuation, re-classified P1→"stub P0") + L2-P1 (T-41..T-46) = **7 ✓** (with the re-classification noted)
- **P2 skills scheduled:** L2-P1 (T-47..T-51) = **5 ✓**
- **Total skills:** 13 + 7 + 5 = **25 ✓**
- **CLI verbs scheduled:** P0 (T-33, T-34, T-35) + governance (T-36) + P1 (T-52, T-53) + governance completion (T-54) = **6 ✓**

The math is correct. The structural defects are in the *content* of how the verbs are built, not in the *count*.

---

*Reviewer: Reviewer (independent quality authority).*
*Date: 2026-06-27. Verdict: REJECT. Re-review on the 15 conditions above.*
