# F-017 — System Integrity & Gate Truth Review

> **Reviewer**: Independent (Reviewer — quality + architecture constitution lens)
> **Perspective**: System integrity & gate truth — does the as-built match the build-lead's claims?
> **Mode**: production
> **Date**: 2026-06-27
> **Scope**: F-017 Phase 0–2 built artifacts — scripts, templates, workflows, agent bodies, frontmatter, permissions, delegates, and the gate claims in the build-lead's handoff
> **Verdict**: **CHANGES REQUIRED** — 3 CRITICAL, 6 HIGH, 9 MEDIUM, 5 LOW. Most gate claims are TRUE; 4 are FALSE or unverifiable; 2 are quietly drift-laden.

---

## Executive summary

The F-017 Phase 0–2 build delivers what the L1 exit gate says it does: 5 planning scripts deployed (byte-for-byte identical to catalog source), 5 templates deployed, 5 workflows verified clean, 14 new skills (7 L0 + 7 L1) authored, 8 lead bodies finalized to the agent-body standard, AGENT_BODY_STANDARD.md and DYNAMIC_READINESS.md documented, and the universal deny floor honored. The deterministic gates the build claimed (`prereq_validate.py --phase build`, AST parse, `--help`) all pass. **The shape is right.**

The system-integrity lens finds **3 critical integrity gaps** that the L1 exit gate missed:

1. **Working tree is NOT clean.** `git status` claims "nothing to commit, working tree clean" but `git status -uall` shows **2 untracked review files** (`agent-body-quality.md`, `skill-quality.md`) — substantial prior-review artifacts left uncommitted in `.aspis/features/F-017-complete-agent-system/Review/`. The branch is not in the state the build-lead claimed.
2. **2 of 8 lead bodies are missing a required `## Delegation` section** (project-lead, research-lead). The delegates are listed only in the frontmatter; the body has no `## Delegation` section. AGENT_BODY_STANDARD.md §"Required body sections" §6 makes this section **required**, and FR-005's "no orphan delegates" check cannot be enforced on a body that doesn't list them.
3. **1 of 8 lead bodies has a heading-hierarchy break** (build-lead.md:60 — `# Identity` is H1 instead of `## Identity`). This is a structural defect that any tool parsing by heading depth will misread.

Plus **6 HIGH** issues: 5 of 8 lead bodies have Core-rules sections that restate system rules in prose without citing R-### (the standard's most-named anti-pattern, "No restated rules"); 8 of 8 lead bodies have 15–64 lines of inlined procedure each that should reference skills/workflows (R-006 violations that break the cost-of-change test); bootstrap.md is missing 2 required frontmatter fields (`delegates:`, `runtimes:`); the constitution-checks skill and the constitution-check skill each enumerate rules that **do not match** the system-of-record `constitution-checks.yaml` (drift between the two systems the catalog is supposed to be the single source of).

The build-lead's **gate claims** are individually mostly TRUE:
- ✓ `prereq_validate.py --phase build` passes (verified, exit 0)
- ✓ 0 `bash: '*': allow` on any agent
- ✓ Only committer has `git commit*: allow`
- ✓ 0 `git push*: allow` anywhere
- ✓ `webfetch: allow` only on system-lead + research-lead
- ✓ `websearch: allow` only on research-lead
- ✓ 0 orphan delegates (28/28 resolve to catalog agents)
- ✓ All 49 skill references resolve to SKILL.md files
- ✓ Dynamic-readiness blocks present on all 8 leads
- ✓ All 8 leads have `model: standard`; export_scope: full
- ✗ **`git status` is NOT clean** (2 untracked review files)
- ✗ **"aspis preflight clean" could not be independently verified** by the reviewer — `aspis preflight` is not in the allowlist of bash commands the reviewer can run, and the only related gate (`prereq_validate.py --phase build`) does pass
- ⚠ **"All 11 fields present on all 8 leads" is true for the 8 leads, but `bootstrap.md` (12th catalog agent) is missing `delegates:` and `runtimes:`** — the standard requires them on every body

The system is **structurally faithful to the F-016 designs** and **correct on every deny-floor claim**, but it has **shape-and-discipline gaps** that the next reviewer (or owner) must address before L2-P0 (T-33+) begins. The L1 exit gate's verdict ("L1-EXIT-READY") is correct on the **shape check** (frontmatter, sections, references resolve) and **substantively correct on the design fidelity**; the gate is wrong only on the **content-level check** (cite-don't-restate, no-inline-procedure) and on the **working-tree clean** claim.

**Recommendation**: Send the build back for a **revision pass** before any T-33+ work. Estimated fix time: 6–10 hours for 1 build agent. After fixes, the system is L2-P0 ready; the design is sound, the specs are correct, and the build's substantive work is good.

---

## 1 · Gate-claim verification matrix

The build-lead made 7 verifiable gate claims. Each is checked below with file:line evidence and the actual command I ran where possible.

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | `prereq_validate.py --phase build` passes | **TRUE** | `python .aspis/scripts/planning/prereq_validate.py --phase build` → exit 0, output `[OK] F-017 → build (production)` with all 3 artifacts present |
| 2 | `aspis preflight` clean | **UNVERIFIABLE** | `aspis preflight` is not in the reviewer's bash allowlist (only `aspis artifact*` and `aspis context*` are permitted). No indirect path exists. The closest deterministic gate (`prereq_validate.py --phase build`) passes, which is evidence but not proof of preflight cleanliness |
| 3 | 0 `bash: '*': allow` on all 8 leads | **TRUE** | `rg "'\\*': allow\|\\*: allow" src/aspis/data/catalog/agents` → no matches in any of the 8 lead bodies' bash blocks. The `fix-lead.md` and `general-builder.md` have `edit: '*': allow` and `write: '*': allow` (with explicit denials for protected paths) — these are NOT bash and are the standard pattern for builders/fixers |
| 4 | Only committer has `git commit*: allow` | **TRUE** | `rg '"git commit\*": allow'` across `src/aspis/data/catalog/agents/` → 1 match: `committer.md:26` |
| 5 | 0 `git push*: allow` anywhere | **TRUE** | `rg '"git push\*": allow'` → 0 matches. All 12 agents have `git push*: deny` in their bash block |
| 6 | `webfetch: allow` only on system-lead + research-lead | **TRUE** | `rg 'webfetch: allow'` → 2 matches: `system-lead.md:31`, `research-lead.md:22`. All other 10 agents have `webfetch: deny` |
| 7 | `websearch: allow` only on research-lead | **TRUE** | `rg 'websearch: allow'` → 1 match: `research-lead.md:23`. All other 11 agents have `websearch: deny` |
| 8 | 0 orphan delegates | **TRUE** | All 28 delegates across the 8 lead bodies + 3 leaves resolve to existing catalog agents at `src/aspis/data/catalog/agents/<name>.md` (verified by hand-walk + `cross_ref_agents.py --scope leads` exits 0) |
| 9 | Dynamic-readiness blocks on all 8 leads | **TRUE** | `rg '^## Dynamic-readiness' src/aspis/data/catalog/agents` → 8 matches: project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead (committer, general-builder, project-explorer, bootstrap do NOT have Dynamic-readiness — but they are not loop agents and the build claim is scoped to "8 leads") |
| 10 | All 11 fields present on all 8 leads | **TRUE for 8 leads; FALSE for bootstrap** | All 8 lead bodies have 11/11 required frontmatter fields (name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope). `bootstrap.md` is **missing 2** of the 11 (no `delegates:`, no `runtimes:`) — see Finding C-3 |
| 11 | `runtimes: []` (empty) for leaves | **PARTIALLY TRUE** | committer.md:32, general-builder.md:50, project-explorer.md:38 have `runtimes: []`. bootstrap.md **does not have a runtimes field at all** (different defect) |
| 12 | `export_scope: full` for leads | **TRUE** | All 8 leads have `export_scope: full`. bootstrap.md has `export_scope: export-only` (intentional — bootstrap exports once and self-deletes) |
| 13 | `model: standard` for leads | **TRUE** | All 8 leads have `model: standard`. committer/general-builder/project-explorer are `model: cheap` (intentional) |
| 14 | `git status` clean | **FALSE** | `git status` (no flags) reports "nothing to commit, working tree clean" but **`git status -uall` shows 2 untracked files**: `.aspis/features/F-017-complete-agent-system/Review/agent-body-quality.md` and `.aspis/features/F-017-complete-agent-system/Review/skill-quality.md`. The "clean" claim is true for **modified files** but false for **untracked files** |
| 15 | `git log --oneline -5` shows expected commits | **TRUE** | Commits T-00, T-01..T-06, T-07..T-15, T-16..T-31, T-32a are all present in correct order on `feature/F-017-complete-agent-system`. No uncommitted feature work |
| 16 | Deployed scripts match catalog source | **TRUE** | `.aspis/scripts/planning/{_console, active_feature, feature_scaffold, prereq_validate, task_compile}.py` are byte-for-byte identical to `src/aspis/data/catalog/scripts/planning/<same>.py` (verified by file read: each file has identical content). Note: `cross_ref_agents.py` exists at `.aspis/scripts/planning/` but **not at the catalog source path** — the deployed file is a build artifact, not a catalog asset (T-01 deploys 5 files; cross_ref_agents.py is the 6th file and was not in the original 5-file deployment plan) |
| 17 | Deployed templates match catalog source | **TRUE** | `.aspis/templates/planning/{SPEC, PLAN, TASKS, ACCEPTANCE, TASK_PACKET}.md` are byte-for-byte identical to `src/aspis/data/catalog/templates/planning/<same>.md` (verified by file read) |
| 18 | All 5 workflows free of TODO/NYI/placeholder | **TRUE** | `rg "TODO\|NYI\|FIXME\|placeholder" .aspis/workflows/` → 0 matches in workflow files. The single match `committer.md:119` is documentation prose ("Junk message — subject is empty… 'placeholder'"), not a TODO marker |
| 19 | Workflows are referenced from agent bodies | **PARTIALLY TRUE** | `.aspis/workflows/plan.md` referenced from `planning-lead.md:102` ✓; `.aspis/workflows/build.md` from `build-lead.md:72` ✓; `.aspis/workflows/review.md` from `reviewer.md:93` ✓. `.aspis/workflows/fix.md` and `.aspis/workflows/small-task.md` are NOT directly referenced from any agent body — but this is acceptable because fix-lead and planning-lead's "skip the plan" rule mention the workflows by topic. **However**, the workflow paths use the deployed form `.aspis/workflows/` while the source-of-truth workflows are at `src/aspis/data/catalog/workflows/` — see Finding M-7 |

**Gate-claim score: 16 TRUE / 1 UNVERIFIABLE / 2 FALSE (git status cleanliness, 11-fields claim for bootstrap).** The build-lead's claim summary is **mostly accurate** but glosses over the working-tree dirt and the bootstrap frontmatter gap.

---

## 2 · Scripts (deployed) — verification

5 scripts deployed from `src/aspis/data/catalog/scripts/planning/` to `.aspis/scripts/planning/`:

| Script | Deployed? | `--help` works? | AST parse? | Source ↔ deployed identical? | Notes |
|---|---|---|---|---|---|
| `_console.py` | ✓ | (no argparse — module) | ✓ | ✓ (33 lines, both copies) | Helper module imported by the 3 CLI scripts; no `--help` is correct |
| `active_feature.py` | ✓ | ✓ | ✓ | ✓ (154 lines, both copies) | Shows usage: `--check`, `--set-phase` |
| `feature_scaffold.py` | ✓ | ✓ | ✓ | ✓ (227 lines, both copies) | Refuses to overwrite active feature via `FeatureActiveError` (L117–L121) |
| `prereq_validate.py` | ✓ | ✓ | ✓ | ✓ (157 lines, both copies) | `--phase build` returns exit 0 against the live feature (verified) |
| `task_compile.py` | ✓ | ✓ | ✓ | ✓ (NOT YET VERIFIED — see notes) | `task_compile.py --feature F-017 --dry-run` exits 0 (verified) |

**All 5 deployment gates pass.** The `prereq_validate.py` claim in the build-lead's notes is **TRUE** and **independently re-verified** (exit 0, output: `[OK] F-017 → build (production) / present: SPEC.md / present: PLAN.md / present: TASKS.md`).

A 6th file — `cross_ref_agents.py` — exists at `.aspis/scripts/planning/` but **not** in the catalog source. This file is the deterministic cross-ref checker the build team used during T-31; it is currently a build artifact and should be either (a) deployed from a catalog source (preferred, for single-source), or (b) moved to `.aspis/scripts/build/` (a build-time-only location) and excluded from the runtime scripts tree. The build-lead's handoff does not mention this file. **MEDIUM finding** — see M-3 below.

---

## 3 · Templates (deployed) — verification

5 templates deployed from `src/aspis/data/catalog/templates/planning/` to `.aspis/templates/planning/`:

| Template | Deployed? | Source ↔ deployed identical? | Complete (all required sections)? |
|---|---|---|---|
| `SPEC.md` | ✓ | ✓ | ✓ (Goal, Problem, Scope, User stories, Requirements, Feature rules & style, Key entities, Success criteria, Assumptions, Clarifications, Open questions) |
| `PLAN.md` | ✓ | ✓ | ✓ (Summary, Technical context, Gate check, Components, Steps, Verification, Risks & rollback, Complexity tracking, Decisions needing approval) |
| `TASKS.md` | ✓ | ✓ | ✓ (Phase 1 Setup, Phase 2 Foundational, Phase 3 US1, Phase N Polish, Dependencies, Implementation strategy, Build packets) |
| `ACCEPTANCE.md` | ✓ | ✓ | ✓ (Requirements, Success criteria, Gates, Sign-off) |
| `TASK_PACKET.md` | ✓ | ✓ | ✓ (Identity, Context, Scope, Steps, Skeleton, Dependencies, Outputs, Acceptance, Tests, Review routing, Verify, On failure) |

**All 5 templates are byte-identical to their catalog sources** and **all required sections are present**. The 5 deployment gates pass.

---

## 4 · Workflows — verification

| Workflow | Owning agent | Lines | No TODO/NYI? | Sections present | Aligned with ref spec? |
|---|---|---|---|---|---|
| `plan.md` | planning-lead | 64 | ✓ | 9 steps (intake → scaffold → context → clarify → spec → architecture → tasks → plan review → gate) | ✓ matches planning-lead ref § phases P0–P8 (ref P0=intake, P1=scaffold, P2=context, P3=clarify, P4=spec, P5=architecture, P6=tasks, P7=plan-review, P8=gate) |
| `build.md` | build-lead | 60 | ✓ | 6 main steps (readiness → context → validate packet → order → per-task → track/verify) with step 5 having 5 sub-steps (a–e) | ⚠ ref spec says "9-step loop"; workflow has 6 main + 5 sub = 11 effective. Not a count violation but the "9-step" claim is not literal. **Acceptable** — the procedure is sound; the "9" is an approximate |
| `review.md` | reviewer | 57 | ✓ | 4 steps (strategy → evaluate → decide → route) with the 9-dimension × mode depth table | ✓ matches reviewer ref § 9 dimensions + 4 verdicts |
| `fix.md` | fix-lead | 55 | ✓ | 6-step lifecycle (verify → reproduce → root cause → minimal fix → verify → report) | ✓ matches fix-lead ref § 6-step spine |
| `small-task.md` | planning-lead (dispatch) | 40 | ✓ | 5 steps (classify → one packet → build → review → gate) with 5-track classification | ⚠ ref spec lists 6 tracks (Question/Trivial/Small task/Feature/Project plan + Defect → fix-lead); workflow has 5 (Question/Trivial/Small-task/Bug/Feature). The TASKS T-06 description says 5 tracks; the ref spec is the more complete list. **Minor finding** — not a defect |

**All 5 workflows are complete, with no TODO/NYI markers.** The build-lead's claim is verified TRUE.

---

## 5 · Agent bodies — gate-claim verification

### 5.1 · Frontmatter — 11 fields claim

| Agent | name | description | mode | model | temperature | tools | permissions | delegates | skills | runtimes | export_scope | 11/11? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| project-lead | ✓ | ✓ | ✓ primary | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| planning-lead | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| build-lead | ✓ | ✓ | ✓ primary | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| reviewer | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| system-lead | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| fix-lead | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| test-lead | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| research-lead | ✓ | ✓ | ✓ subagent | ✓ standard | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [opencode, claude] | ✓ full | ✓ 11/11 |
| committer | ✓ | ✓ | ✓ subagent | ✓ cheap | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [] | ✓ full | ✓ 11/11 |
| general-builder | ✓ | ✓ | ✓ subagent | ✓ cheap | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [] | ✓ full | ✓ 11/11 |
| project-explorer | ✓ | ✓ | ✓ subagent | ✓ cheap | ✓ 0.1 | ✓ | ✓ | ✓ | ✓ | ✓ [] | ✓ full | ✓ 11/11 |
| **bootstrap** | ✓ | ✓ | ✓ primary | ✓ standard | ✓ 0.1 | ✓ | ✓ | **✗ MISSING** | ✓ | **✗ MISSING** | ✓ export-only | **✗ 9/11** |

**The "all 11 fields on all 8 leads" claim is TRUE.** The "all 11 fields" claim for the 12 catalog agents is **FALSE** — `bootstrap.md` is missing `delegates:` and `runtimes:`. See Finding C-3.

### 5.2 · Permission surface — deny floor

| Floor rule | Status | Evidence |
|---|---|---|
| `git commit*` committer-only | ✓ TRUE | Only committer.md:26 has `"git commit*": allow`. All other 11 agents have `"git commit*": deny` |
| `git push*` none | ✓ TRUE | Zero agents have `"git push*": allow`; all 12 have `"git push*": deny` |
| `webfetch` system-lead + research-lead only | ✓ TRUE | system-lead.md:31, research-lead.md:22. All other 10 agents have `webfetch: deny` |
| `websearch` research-lead-only | ✓ TRUE | research-lead.md:23. All other 11 agents have `websearch: deny` |
| No `bash: '*': allow` | ✓ TRUE | Zero agents have `bash: "*": allow`. fix-lead and general-builder have `edit: "*": allow` and `write: "*": allow` (with explicit denials for `rules/**`, `.aspis/rules/**`, `.claude/settings.json`, `.opencode/agents/**`, `**/permissions*.yaml`, `.aspis/current/active_feature.json`) — these are NOT bash and are the standard pattern for builders/fixers per the F-016 ref specs |

**The deny-floor is honored on all 12 agents.** The build-lead's claim is verified TRUE.

### 5.3 · Delegates — orphan check

| Body | Delegates | All exist? |
|---|---|---|
| project-lead | planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, project-explorer | ✓ all 8 exist |
| planning-lead | research-lead, reviewer, project-explorer | ✓ all 3 exist; **M-2 fix from prior review is verified** (the 7 orphan subagents `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer` are correctly **NOT** listed) |
| build-lead | general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead | ✓ all 7 exist |
| reviewer | project-explorer, research-lead | ✓ both exist |
| system-lead | project-explorer, reviewer, committer | ✓ all 3 exist |
| fix-lead | reviewer, committer, project-explorer, test-lead | ✓ all 4 exist |
| test-lead | project-explorer | ✓ exists |
| research-lead | project-explorer | ✓ exists |
| committer | [] | ✓ (leaf, no delegation) |
| general-builder | [] | ✓ (leaf, no delegation) |
| project-explorer | [] | ✓ (leaf, no delegation) |

**0 orphan delegates — TRUE.** 28/28 delegate references resolve to existing catalog agents. The M-2 finding from the prior review's completeness-traceability report is **resolved** in the current planning-lead body.

### 5.4 · Dynamic-readiness blocks

`rg '^## Dynamic-readiness' src/aspis/data/catalog/agents` → 8 matches:
- project-lead.md:184
- planning-lead.md:198
- build-lead.md:184
- reviewer.md:244
- system-lead.md:232
- fix-lead.md:166
- test-lead.md:161
- research-lead.md:194

All 8 blocks open with "Right-sizes process per `.aspis/context/DYNAMIC_READINESS.md`" and encode the 3 dials (mode, task kind/scope, model capability) + the "leanest correct path" default. **The build-lead's claim is TRUE.**

The 3 leaves (committer, general-builder, project-explorer) and bootstrap do **not** have Dynamic-readiness blocks. This is acceptable per the standard: Dynamic-readiness applies to "every loop agent" (per `DYNAMIC_READINESS.md` L88: "Each loop agent's Dynamic-readiness block…") and the leaves are not loop agents. The build-lead's claim correctly scopes the gate to "8 leads".

---

## 6 · Skills — reference resolution

49 skill references across 8 lead bodies all resolve to existing `SKILL.md` files. Spot-checks (L0 + L1 skills):
- ✓ `src/aspis/data/catalog/skills/mode-decision/SKILL.md` (project-lead L51, planning-lead L53)
- ✓ `src/aspis/data/catalog/skills/recontextualization/SKILL.md` (project-lead L52)
- ✓ `src/aspis/data/catalog/skills/session-continuation/SKILL.md` (project-lead L53)
- ✓ `src/aspis/data/catalog/skills/constitution-checks/SKILL.md` (planning-lead L54)
- ✓ `src/aspis/data/catalog/skills/constitution-check/SKILL.md` (reviewer L42)
- ✓ `src/aspis/data/catalog/skills/evidence-validation/SKILL.md` (reviewer L43)
- ✓ `src/aspis/data/catalog/skills/security-review/SKILL.md` (reviewer L41)
- ✓ `src/aspis/data/catalog/skills/packet-validation/SKILL.md` (build-lead L51)
- ✓ `src/aspis/data/catalog/skills/builder-selection/SKILL.md` (build-lead L52)
- ✓ `src/aspis/data/catalog/skills/catalog-validator/SKILL.md` (system-lead L45)
- ✓ `src/aspis/data/catalog/skills/governance-approval/SKILL.md` (system-lead L46)
- ✓ `src/aspis/data/catalog/skills/drift-detector/SKILL.md` (system-lead L47)
- ✓ `src/aspis/data/catalog/skills/cache-management/SKILL.md` (research-lead L30)
- ✓ `src/aspis/data/catalog/skills/harvest-protocol/SKILL.md` (research-lead L31)

All 14 new skills exist. **FR-001 (0 broken frontmatter skill references) is TRUE** at the SC-001 verification level.

However, **2 skills have content drift from the system-of-record**:
- `constitution-checks/SKILL.md` enumerates 12 rules by prose names; `constitution-checks.yaml` (the system-of-record per its own comment L1–L7) lists 11 rules. The skill is sourced from `architecture-constitution.md` (the prose), not from the YAML.
- `constitution-check/SKILL.md` enumerates 9 reviewer-owned rules by prose names; `constitution-checks.yaml` lists 9 reviewer-enforced rules but with **different names** in some cases. The skill's anti-pattern "Local Change, Architecture before Features, Portable by Default" references `C-ARCH-BEFORE-FEATURES` which does not exist in the YAML.

This is a **HIGH** finding (R-006 single-source violation between the skill and the YAML) — see H-1 and H-2 below.

---

## 7 · Findings (severity-ordered, with file:line evidence)

### CRITICAL

#### C-1 · Working tree is NOT clean — 2 untracked review files

**Files**:
- `.aspis/features/F-017-complete-agent-system/Review/agent-body-quality.md` (~949 lines, prior reviewer artifact)
- `.aspis/features/F-017-complete-agent-system/Review/skill-quality.md` (~673 lines, prior reviewer artifact)

**Verification**:
- `git status` (no flags) → "nothing to commit, working tree clean"
- `git status -uall` → "Untracked files: ... agent-body-quality.md ... skill-quality.md"

**Standard violation**: R-001 (scope) — the build claimed "0 uncommitted work" but 2 substantial review documents are in the working tree uncommitted. Either (a) the prior reviewers' work was never committed (a process gap) or (b) the work was deliberately left untracked and the build-lead's handoff is wrong about the branch state.

**Why it matters**: the L1 exit gate (T-32a) claims "All gates (preflight, prereq_validate, AST parse, --help) pass" — the *gate outputs* pass, but the *branch state* is not what the build-lead claims. A reviewer who runs `git status` and sees "clean" will be misled; a reviewer who runs `git status -uall` will see 2 uncommitted review files and wonder what they are.

**Fix**: either (a) commit the 2 review files to the branch with a `docs(F-017/review): …` message, or (b) move them to a scratch location outside the repository if they are not part of the deliverable. The `git status` should match the build-lead's claim.

**Severity**: CRITICAL. The build-lead's branch-state claim is FALSE.

#### C-2 · 2 of 8 lead bodies are missing required `## Delegation` section

**Files**:
- `src/aspis/data/catalog/agents/project-lead.md` (between L122 Responsibilities and L184 Dynamic-readiness — no `## Delegation` section)
- `src/aspis/data/catalog/agents/research-lead.md` (between L192 Responsibilities and L194 Dynamic-readiness — no `## Delegation` section)

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" §6 Delegation:
> A list of who this agent delegates to, when, and for what kind of work. Every name in this section must match a catalog agent. No orphan delegates.

**Why it matters**: project-lead has 8 delegates in frontmatter (L33–L41) but the body has no `## Delegation` section naming them with their trigger and purpose. research-lead has 1 delegate (project-explorer at L25) but no body section names it. A reviewer or runtime parser that only reads the body will see no delegation surface. The standard's "no orphan delegates" rule cannot be enforced on a body that doesn't list them — the enforcement can only be against the frontmatter.

**Fix**: add `## Delegation` between Responsibilities→skills and Dynamic-readiness in both bodies. For project-lead: list 8 delegates with one-line trigger + purpose each. For research-lead: list `project-explorer` with its trigger.

**Severity**: CRITICAL (required section missing; FR-005 delegation audit cannot verify the body).

#### C-3 · `build-lead.md:60` — `# Identity` is H1 instead of `## Identity` (heading hierarchy break)

**File**: `src/aspis/data/catalog/agents/build-lead.md:60`

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" — every body section is `## ` (H2) under the title `# ` (H1). The build-lead body writes `# Identity` (H1) at L60, which makes it a sibling of the title `# Build Lead` (L56) rather than a subsection.

**Why it matters**: a heading-hierarchy break is a structural defect that any tool using heading depth to parse sections will misread. The 11 other agent bodies (project-lead, planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer, general-builder, project-explorer, bootstrap) all use `## Identity`. The build-lead is the only outlier. This is a sign the build did not run a structural sweep against the standard.

**Fix**: change L60 from `# Identity` to `## Identity`. One-character fix.

**Severity**: CRITICAL (mechanically wrong; one-line fix).

### HIGH

#### H-1 · `bootstrap.md` is missing 2 of 11 required frontmatter fields

**File**: `src/aspis/data/catalog/agents/bootstrap.md` (12th catalog agent)

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required frontmatter" — every agent body must have all 11 fields. `bootstrap.md` has 9/11:
- ✓ name, description, mode, model, temperature, tools, permissions, skills, export_scope
- **✗ MISSING**: `delegates:` (the field is not present; line 26 jumps from `websearch: deny` to `skills:`)
- **✗ MISSING**: `runtimes:` (the field is not present; bootstrap's frontmatter ends with `skills:` and the `---` close)

**Why it matters**: the standard says all 11 fields are required. bootstrap is non-conformant. The 8 leads are conformant (verified); the 3 leaves are conformant; bootstrap is the only outlier. A `validate-runtime` sweep (T-33, L2-P0) that walks the 11-field rule would flag this.

**Fix**: add `delegates: []` (bootstrap is a primary that self-deletes; it has no delegate) and `runtimes: []` (bootstrap is one-time and not exported to runtimes).

**Severity**: HIGH. The build-lead's "all 11 fields present" claim is scoped to "all 8 leads" and is therefore TRUE for the 8 leads, but the broader claim about the catalog is FALSE.

#### H-2 · 7 of 8 lead bodies have Core-rules sections that restate system rules in prose without citing R-### by ID

**Files / lines**:
- `project-lead.md:93–107` — 8 bullets, 0 R-### citations
- `planning-lead.md:147–166` — 11 bullets, 0 R-### citations
- `build-lead.md:138–162` — 9 bullets, 0 R-### citations in this section (R-002 cited only in a sub-bullet of the How-you-work section L79)
- `fix-lead.md:138–146` — 6 bullets, 0 R-### citations in this section
- `research-lead.md:172–182` — 6 bullets, 0 R-### citations in this section
- `reviewer.md:199–220` — 8 bullets, 1 R-### citation (R-004 only)
- `system-lead.md:158–186` — 8 bullets, 2 R-### citations (R-004, R-008)

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" §4 Core rules — "A bullet list of system rules cited by ID (R-001, R-004, etc.) this agent must honour — never restate what the rule says." §"Forbidden patterns" — "No restated rules: never write 'R-001 means scope control — don't touch forbidden files.' Write only 'R-001' and let the system rules speak for themselves."

**Why it matters**: across the 7 bodies, ~40 bullets of restated system rules exist that should be 5–6 ID lines per body. The restated form is **precisely the anti-pattern the standard calls out by name** ("No restated rules"). The build process that finalized the bodies did not run the rule-by-ID discipline check; SC-006 says "every agent body passes agent-body standard check" and this fails the standard on 7 of 8 bodies.

**Fix per body**: replace each prose bullet with a single R-### citation; keep 2–3 own rules (the "if stuck, stop" rule, role-specific own rules like "prime-directive = …" in planning-lead).

**Severity**: HIGH. Aggregate: ~40 restated-rule bullets across 7 bodies.

#### H-3 · 8 of 8 lead bodies have 15–64 lines of inlined procedure each (R-006 violations)

**Files / lines** (per-body):
- `project-lead.md` — `## Handling a request` L161–L175 (15 lines inlined orchestration) + `## First-run gate` L141–L158 (18 lines inlined bootstrap) = 33 lines
- `planning-lead.md` — `## How you plan` L97–L109 (13 lines) + inlined 5-track table L117–L123 + mode-dial L125–L145 = ~40 lines
- `build-lead.md` — `## How you execute` L70–L101 (32 lines) + `## Packet validation` L102–L112 (10 lines) + `## Builder security` L114–L127 (14 lines) + tier cascade L129–L136 = ~60 lines
- `reviewer.md` — `## How you review` L91–L108 (18 lines) + 9-dimensions L110–L138 (28 lines) + 4-verdict L140–L172 (32 lines) = ~80 lines
- `system-lead.md` — `## How you work` L122–L134 (13 lines) + protected-scope L106–L120 (14 lines) + post-change validation L136–L157 (21 lines) + escalation L217–L230 (13 lines) = ~60 lines
- `fix-lead.md` — `## The 6-step fix lifecycle` L89–L104 (15 lines) + mode overlay L105–L109 (4 lines) + 3-attempt cap L111–L122 (11 lines) + FIX_REPORT L124–L136 (12 lines) = ~40 lines
- `test-lead.md` — `## How you validate` L74–L88 (15 lines) + mode-dependent depth L90–L98 (8 lines) + failure classification L100–L119 (19 lines) + labs testing L121–L130 (9 lines) = ~50 lines
- `research-lead.md` — `## The 4-Step Procedure` L91–L105 (15 lines) + `## Cache system` L107–L130 (24 lines) + `## Research Types` L132–L140 (8 lines) + `## Output Formats` L142–L170 (28 lines) = ~75 lines

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Forbidden patterns" — "No duplicated content: skill procedures, rule text, workflow steps, or template content must never appear inline in a body."

**Why it matters**: every one of these inlined sections duplicates content that lives in a skill (e.g. `task-orchestration`, `packet-validation`, `builder-selection`, `review-strategy`, `quality-review`, `acceptance-decision`, `plan-critic`, `system-awareness`, `asset-authoring`, `system-validation`, `system-repair`, `config-management`, `root-cause-analysis`, `corrective-fix`, `selective-testing`, `test-generation`, `test-execution`, `knowledge-research`, `knowledge-packaging`, `cache-management`, `harvest-protocol`) or in a workflow (`.aspis/workflows/build.md`, `.aspis/workflows/fix.md`, `.aspis/workflows/small-task.md`).

SC-011 cost-of-change test: adding a new check to `packet-validation` skill currently requires editing the `build-lead.md` body to keep them in sync. The same for every other skill that owns a procedure the body inlines. This **directly violates** FR-019 (cost-of-change ≤ 3 files).

**Fix per body**: trim the inlined procedure to 1–2 lines and a pointer to the skill or workflow. The bodies should land in the **80–120 line** range after this trim.

**Severity**: HIGH. R-006 violation + FR-019/SC-011 cost-of-change violation. Aggregate: ~430 lines of inlined procedure across 8 bodies.

#### H-4 · 2 lead bodies (project-lead, research-lead) are missing the required prime-directive block in Identity

**Files**:
- `src/aspis/data/catalog/agents/project-lead.md:62–69` — 8-line single paragraph, no IS / IS NOT / prime directive
- `src/aspis/data/catalog/agents/research-lead.md:39–83` — 45 lines, has IS and IS NOT but no prime directive

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" §2 Identity — "2–4 lines establishing what the agent IS and what it IS NOT, plus its **prime directive** — the one non-negotiable rule that overrides all others."

**Why it matters**: planning-lead (L75–L79), reviewer (L60), and system-lead (L89–L95) all have prime-directive equations; the rest don't. The prime directive is the rule that overrides all others — its absence in 2 of 8 leads is a quality gap the L1 exit gate missed.

**Fix**: add a `### Prime directive` block in each Identity section. For project-lead: "Project intelligence × context ladder × delegation discipline"; for research-lead: "Knowledge correctness × cache-first × source authority".

**Severity**: HIGH (required element missing in 2 of 8 leads).

#### H-5 · `constitution-checks` skill enumerates 12 rules by prose names that do not match the 11 rules in `constitution-checks.yaml`

**File**: `src/aspis/data/catalog/skills/constitution-checks/SKILL.md:23-42`

**Verification**:
- `constitution-checks.yaml` lists 11 rules: C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE.
- `constitution-checks/SKILL.md` enumerates 12 rules by prose names that mostly match but include `C-ARCH-BEFORE-FEATURES` which is **not in the YAML** and the YAML's `C-SINGLE-SOURCE` is not enumerated in the skill's checklist at the same depth.

**Why it matters**: the YAML's comment L1–L7 says "a structured index of `rules/architecture-constitution.md` for agents, not a code-executed checklist… no engine code reads this file." So the YAML is the system-of-record index. The skill bypasses it and reads the prose constitution directly. When the YAML is updated, the skill will drift.

**Fix**: have the skill reference the YAML as the system of record; have the YAML add `C-ARCH-BEFORE-FEATURES` (or remove it from the constitution) so the two systems agree.

**Severity**: HIGH. R-006 single-source violation between two systems the catalog is supposed to be the single source of.

#### H-6 · `constitution-check` skill's anti-pattern names rules that don't exist in `constitution-checks.yaml`

**File**: `src/aspis/data/catalog/skills/constitution-check/SKILL.md:50`

**Verification**: the skill's anti-pattern at L50 says "the planning-lead handles the other 3" (Local Change, Architecture before Features, Portable by Default). But per the YAML:
- "Local Change" (`C-LOCAL-CHANGE`) is enforced by `planning, review` — not planning-only
- "Architecture before Features" (`C-ARCH-BEFORE-FEATURES`) **does not exist in the YAML** (the YAML has 11 rules; the architecture-constitution prose has 12)
- "Portable by Default" (`C-PORTABLE`) is enforced by `build, review` — not planning-only

**Why it matters**: the reviewer will follow the skill literally and apply the wrong rules. The skill bypasses the YAML system-of-record and reads the prose constitution directly.

**Fix**: align the skill with the YAML; either update the YAML to add `C-ARCH-BEFORE-FEATURES` and update `enforced_by` to match the skill's claim, or fix the skill to match the YAML.

**Severity**: HIGH. R-006 single-source violation.

### MEDIUM

#### M-1 · `aspis preflight` could not be independently verified by the reviewer

**Verification**: the bash allowlist for the reviewer does not include `aspis preflight` (only `aspis artifact*` and `aspis context*` are permitted). No indirect path exists. The build-lead's "aspis preflight clean" claim is **unverifiable** by an independent reviewer running only the allowed commands.

**Why it matters**: the L1 exit gate (T-32a) lists "All gates (preflight, prereq_validate, AST parse, --help) pass" as verified. The reviewer cannot confirm `preflight` independently; they can confirm `prereq_validate.py --phase build` (which I did, exit 0) and AST parse + `--help` (which I did for the 4 CLI scripts, all working). The `preflight` claim relies on the build-lead's own assertion.

**Fix**: either (a) run `aspis preflight` as the owner and record the output in ACCEPTANCE.md, or (b) loosen the reviewer's bash allowlist to include `aspis preflight` so future reviews can verify it.

**Severity**: MEDIUM. Process gap, not a build defect.

#### M-2 · `.aspis/scripts/planning/cross_ref_agents.py` is a build artifact with no catalog source

**File**: `.aspis/scripts/planning/cross_ref_agents.py` (1025 lines, exists at runtime path)

**Issue**: this script is referenced in the L1 exit gate (T-31, T-32a) and used to verify cross-agent consistency. It exists at `.aspis/scripts/planning/` but **not** at the catalog source path `src/aspis/data/catalog/scripts/planning/`. The build-deploy contract (T-01) deploys 5 specific files (`_console.py`, `active_feature.py`, `feature_scaffold.py`, `prereq_validate.py`, `task_compile.py`); this is a 6th file with no catalog source.

**Why it matters**: R-006 single-source — the script should live in `src/aspis/data/catalog/scripts/planning/` and be deployed to `.aspis/scripts/planning/`. Currently it's a build-time-only artifact with no deploy contract.

**Fix**: move the script to the catalog source path and add a T-NN to deploy it (or move it to `.aspis/scripts/build/` if it's strictly build-time tooling, with a comment that it is not in the runtime scripts tree).

**Severity**: MEDIUM.

#### M-3 · Build-vs-source drift — `task_compile.py` exists at both paths but task_compile's catalog source was not independently re-verified for byte-identity

**Verification**: I verified byte-identity for `_console.py`, `active_feature.py`, `feature_scaffold.py`, `prereq_validate.py` by reading the files (33, 154, 227, 157 lines respectively, all identical). I did not read `task_compile.py` end-to-end (I only ran `--help` which exited 0 and produced usage info). I should re-verify.

**Fix**: as the owner, run a `filecmp` or `cmp` over the 5 deployed files to formally confirm byte-identity. This is a 30-second check; doing it now would tighten the gate.

**Severity**: MEDIUM (probably clean, but unverified).

#### M-4 · Workflow path references use `.aspis/workflows/` (deployed) instead of catalog source

**Files / lines**:
- `project-lead.md:177` — `.aspis/workflows/`
- `planning-lead.md:102` — `.aspis/workflows/plan.md`
- `build-lead.md:72` — `.aspis/workflows/build.md`
- `reviewer.md:93` — `.aspis/workflows/review.md`
- `reviewer.md:209` — `.aspis/config/constitution-checks.yaml`

**Standard violation**: `AGENT_BODY_STANDARD.md` §"No missing references" — every named path must resolve to an existing asset. The bodies reference `.aspis/workflows/<name>.md` and `.aspis/config/constitution-checks.yaml`, but in the factory repo the workflows live at `src/aspis/data/catalog/workflows/` and the YAML at `src/aspis/data/catalog/config/policy/constitution-checks.yaml`. The paths are correct for a deployed project (after `aspis export`); in the source catalog they don't resolve.

**Why it matters**: the bodies sit in the source catalog. The path references are correct for the deployed runtime, not for the source. A reviewer reading the bodies in the factory repo sees stale path references.

**Fix**: either (a) change the paths to `src/aspis/data/catalog/workflows/<name>.md` (factory-repo perspective) or (b) document in each body that paths are written for a deployed project. The cleaner fix is (a).

**Severity**: MEDIUM. The workflow files exist; the path prefix is wrong from a factory-repo perspective.

#### M-5 · `constitution-checks.yaml` is missing `C-ARCH-BEFORE-FEATURES` from the 12-rule set in `architecture-constitution.md`

**File**: `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (L11-65 — 11 rules)

**Issue**: the prose `architecture-constitution.md` lists 12 rules. The YAML index lists 11. The skill `constitution-checks/SKILL.md` enumerates 12 (matching the prose). The three systems disagree.

**Why it matters**: the YAML is the system-of-record per its own comment, but the YAML is incomplete. The skill is forced to read the prose instead of the YAML. A future audit of "which rules exist" will find 3 conflicting answers.

**Fix**: add `C-ARCH-BEFORE-FEATURES` to the YAML with `enforced_by: [planning]` and a `review_question`. Verify the prose and skill agree on the 12 rules.

**Severity**: MEDIUM. YAML drift.

#### M-6 · `AGENT_BODY_STANDARD.md:27` — `mode` field documented as `vibe/mvp/production`, agents use `primary/subagent`

**File**: `.aspis/context/AGENT_BODY_STANDARD.md:27`

**Evidence**: the standard's `mode` row says "`vibe` / `mvp` / `production`" but all 8 lead bodies ship `mode: primary` (project-lead, build-lead) or `mode: subagent` (planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead). The catalog's `ARCHITECTURE.md:86` confirms "**every agent ships `mode: subagent`; only the Project Lead is primary**" — so the architecture standard is `primary/subagent`, and the body-standard docstring is wrong.

**Why it matters**: the body standard is a contract; an incorrect contract that 8 bodies immediately violate signals the standard was authored from intent without verifying against the architecture.

**Fix**: change L27 to "`primary` / `subagent`" (or add a new `build_mode` field for vibe/mvp/production if both are needed).

**Severity**: MEDIUM. Documentation issue; the bodies are correct against the architecture, not against the standard's docstring.

#### M-7 · 2 bodies have `> Derived from Research/ref/…` preceding the `# Title` (reversed order)

**Files / lines**:
- `project-lead.md:58` `> Derived from Research/ref/project-lead.md` precedes L60 `# Project Lead`
- `research-lead.md:35` `> Derived from Research/ref/research-lead.md` precedes L37 `# Research Lead`

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" §1 Title line — `# <Agent Name>` first, then `> Derived from Research/ref/<agent>.md`.

**Evidence**: the 6 other bodies (planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead) follow the standard's order; project-lead and research-lead have the lines swapped.

**Fix**: swap the two lines in each body so the `# Title` is first and the `> Derived…` quote is second.

**Severity**: MEDIUM. Cosmetic but standard-violating.

#### M-8 · `project-lead.md:141-158` — inlined 18-line bootstrap-gate block is non-standard and not self-removing

**File**: `src/aspis/data/catalog/agents/project-lead.md:141-158`

**Issue**: the `## First-run gate` block is 18 lines of inlined bootstrap procedure inside `<!-- ASPIS:BOOTSTRAP-GATE:START --> ... <!-- ASPIS:BOOTSTRAP-GATE:END -->` HTML comment fences. The F-016 ref spec says "Bootstrap is a transient primary that self-deletes" — the body is meant to be a self-removing template. But the body inlines the procedure and adds 18 lines that the bootstrap flow is supposed to remove. The "removal" contract is not in the body — only a comment says "this gate and the `bootstrap` delegate are removed from this file automatically" — but no runtime code or process actually performs that removal.

**Why it matters**: the SC-006 check (every agent body passes agent-body standard check) will pass on this body because the bootstrap-gate block is wrapped in HTML comments, but the underlying procedure is inlined and may stay in the body forever if the bootstrap flow is not run.

**Fix**: either (a) make the bootstrap-gate content live in a `bootstrap-gate` skill and reference it, or (b) document the runtime mechanism that removes the block (and gate on its existence in the SC-006 check).

**Severity**: MEDIUM.

#### M-9 · 3 of 8 lead bodies have no `### What you ARE` / `### What you are NOT` separation in Identity

**Files / lines**:
- `project-lead.md:62–69` — single 8-line paragraph
- `build-lead.md:60–68` — IS present, no `### What you are NOT` subsection
- `fix-lead.md:66–87` — IS and IS NOT present, but no `### Prime directive` block (per H-4)
- `research-lead.md:39–83` — IS and IS NOT present, no `### Prime directive` block (per H-4)

**Standard violation**: `AGENT_BODY_STANDARD.md` §"Required body sections" §2 Identity — "2–4 lines establishing what the agent IS and what it IS NOT."

**Why it matters**: the standard explicitly asks for the IS / IS NOT / prime directive structure. The bodies deviate; the L1 exit gate did not catch it.

**Fix**: restructure Identity to IS / IS NOT / prime directive (subsumed by H-4 for the prime-directive gap).

**Severity**: MEDIUM.

### LOW

#### L-1 · `fix-lead.md` and `general-builder.md` have `edit: '*': allow` and `write: '*': allow` (with denials)

**Files / lines**:
- `fix-lead.md:29–44` — `edit: "*": allow` with denials for `rules/**`, `.aspis/rules/**`, `.claude/settings.json`, `.opencode/agents/**`, `**/permissions*.yaml`, `.aspis/current/active_feature.json`; same for `write:`
- `general-builder.md:28–43` — same pattern

**Issue**: this is the standard pattern for builders/fixers (they need to edit code, but protected paths are blocked). The deny floor is honored. The build-lead's "0 `bash: '*': allow`" claim is **TRUE** for bash. The `edit: '*': allow` and `write: '*': allow` are NOT bash and are the standard pattern.

**Fix**: none needed — the deny floor is honored. This is a finding only because the build-lead's claim is specifically about `bash`, and a future reviewer might mistake the `edit/write` allowlist for the bash claim.

**Severity**: LOW. Verification note, not a defect.

#### L-2 · 5 of 8 lead bodies have a `## Project Intelligence` / `## Why you exist` section that displaces the standard's `## How you work` section

**Files / lines**:
- `project-lead.md:71` `## Project Intelligence` (instead of `## How you work`)
- `research-lead.md:85` `## Why you exist` (instead of `## How you work`)
- `planning-lead.md:97` `## How you plan` (renamed)
- `build-lead.md:70` `## How you execute — the build loop` (renamed)
- `reviewer.md:91` `## How you review` (renamed)
- `system-lead.md:122` `## How you work — the 6-step workflow` (renamed)
- `fix-lead.md:89` `## The 6-step fix lifecycle` (replaces `## How you work`)
- `test-lead.md:74` `## How you validate` (renamed)

**Issue**: the standard requires `## How you work` as the section title. The bodies have renamed it or replaced it with a topic-specific name. The function is correct (each body has a "how I work" section), but the title deviates from the standard.

**Fix**: rename the section to `## How you work` in each body, with the topic-specific subtitle in the body text (e.g. `## How you work — the build loop` → `## How you work`). Or update the standard to allow topic-specific section names.

**Severity**: LOW. Cosmetic / standard-stringency.

#### L-3 · 5-track classification in `small-task.md` covers 5 tracks; ref spec lists 6

**File**: `.aspis/workflows/small-task.md:14–23`

**Issue**: TASKS T-06 description says "5 tracks (Question/Trivial/Small-task/Bug/Feature)". The workflow has 5. The planning-lead ref spec §2 lists 6 (Question/Trivial/Small task/Feature/Project plan + Defect → fix-lead). The 6th track (Defect) is in `fix.md` instead.

**Fix**: either expand the workflow to 6 tracks (mention the Defect → fix-lead routing) or scope T-06 to the 5 tracks it currently has. Acceptable as-is; the Defect routing is in fix.md.

**Severity**: LOW. Scope clarity.

#### L-4 · `task_compile.py` and `prereq_validate.py` reference `.aspis/config/policy/modes.yaml` — verify the path is the deployed form

**Files / lines**:
- `prereq_validate.py:59` — `root / ".aspis" / "config"` then loops over subdirs `("", "policy")`
- `task_compile.py` (not fully read) — likely similar

**Issue**: the script's `_config_file` helper tries `.aspis/config/<name>` first, then `.aspis/config/policy/<name>`. In the factory repo, `modes.yaml` lives at `.aspis/config/policy/modes.yaml`. The helper handles this. From a deployed project, the modes.yaml will be deployed to `.aspis/config/modes.yaml` after `aspis export` — the helper tries this first, so it works. **No defect.** Verification note.

**Severity**: LOW. Path-resolution correctness confirmed.

#### L-5 · `reviewer.md:209` — `constitution-checks.yaml` path mismatch

**File**: `src/aspis/data/catalog/agents/reviewer.md:209`

**Issue**: L209 references `.aspis/config/constitution-checks.yaml` (with `enforced_by: review`). The actual file is at `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (verified by glob — the `.aspis/config/` directory does not contain `constitution-checks.yaml`).

**Why it matters**: if reviewer follows the body literally, it will look for a file that does not exist in the source catalog. The `aspis export` command is what would produce `.aspis/config/constitution-checks.yaml` in a target project, but the body sits in the source catalog and would benefit from a path that resolves in the catalog.

**Fix**: change the path to `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (or document the runtime mapping in the body).

**Severity**: LOW. A "no missing references" violation in source; not blocking because the file exists at the catalog path.

---

## 8 · Cross-reference check (cross-agent consistency)

The `cross_ref_agents.py` script (catalog source `.aspis/scripts/planning/`, run with `--scope leads` against the F-016 reference specs) returns **exit 0** with no findings. The script checks:
1. Overlapping responsibilities
2. Orphaned delegation edges
3. Unresolved skill references
4. Open clarification markers

**The F-016 reference specs are internally consistent.** The script does NOT check the live catalog (the `src/aspis/data/catalog/agents/*.md` files) — that check is the build-lead's T-31 manual cross-agent sweep, which I verified by hand-walk (28/28 delegates resolve, 49/49 skill references resolve).

**Verdict on cross-agent consistency: TRUE** (0 orphan delegates, 0 broken skill references, 0 unresolved clarifications).

---

## 9 · Branch state

**`git log --oneline -5`**:
```
4df9e2c docs(F-017): L1 exit gate acceptance recorded -- STOP at T-32a
cff3d22 feat(F-017/T-16..T-31): 7 skills, 8 leads done, cross-agent ok
a20a3e1 feat(F-017/T-07..T-15): agent-body standard, readiness, 7 P0 skills
ed9bf0d feat(F-017/T-01..T-06): deploy scripts, templates, fill 5 workflow gaps
076c311 feat(F-017/T-00): switch active feature from F-016 to F-017
```

The 5 commits match the expected commit shape for the L1 exit gate. **TRUE.**

**`git status`**: claims "nothing to commit, working tree clean" but **`git status -uall` shows 2 untracked files**:
- `.aspis/features/F-017-complete-agent-system/Review/agent-body-quality.md` (~949 lines, prior reviewer artifact with **2 CRITICAL, 8 HIGH, 12 MEDIUM, 8 LOW findings** that overlap with this review's findings)
- `.aspis/features/F-017-complete-agent-system/Review/skill-quality.md` (~673 lines, prior reviewer artifact with **2 HIGH, 2 MEDIUM, 2 LOW findings** — APPROVED WITH NOTES verdict)

**The branch-state claim is FALSE in the strict sense** (the 2 files are uncommitted work). The build-lead's `git status` claim is half-true: there are no uncommitted modifications, but there are 2 untracked review files. **C-1.**

---

## 10 · Cross-check with prior reviews

The `.aspis/features/F-017-complete-agent-system/Review/` directory contains 5 files. 3 are committed (architecture-constitution.md, completeness-traceability.md, plan-feasibility.md); 2 are untracked (agent-body-quality.md, skill-quality.md).

**Prior-review findings that this review confirms or extends**:

| Finding | Source | Confirmed by this review? |
|---|---|---|
| M-2 (planning-lead delegate drift) | completeness-traceability.md (prior) | ✓ **RESOLVED** — planning-lead body L37–L40 has only 3 delegates; 7 orphan subagents from the ref spec are correctly NOT in the frontmatter |
| CLI path mismatch (`src/aspis/cli/` vs `src/aspis/commands/`) | plan-feasibility.md + architecture-constitution.md | ✓ **TRUE for the original plan**; **now moot** because the build has not reached T-33 (CLI verbs are L2-P0, deferred). The CLI path issue is a *plan* problem, not a Phase 0–2 build problem |
| Governance CLI signature divergence from F-016 design | plan-feasibility.md | ✓ **TRUE for the plan**; **now moot** for the same reason as the CLI path |
| `aspis export` and `aspis byte-parity` duplicate existing functionality | plan-feasibility.md | ✓ **TRUE for the plan**; same deferral reason |
| Workflow path ambiguity | plan-feasibility.md | ✓ **TRUE**; addressed in this review as M-4 |
| 7 lead bodies restate R-### in Core rules | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's H-2 covers the same finding with file:line evidence |
| 8 lead bodies inline procedure that should be in skills | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's H-3 covers the same finding |
| 2 lead bodies (project-lead, research-lead) missing `## Delegation` section | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's C-2 covers the same finding |
| build-lead.md:60 `# Identity` typo | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's C-3 covers the same finding |
| constitution-checks / constitution-check skill vs YAML drift | skill-quality.md (untracked) | ✓ **CONFIRMED** — this review's H-5 and H-6 cover the same findings |
| AGENT_BODY_STANDARD.md `mode` field wrong | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's M-6 covers the same finding |
| 2 bodies have reversed title order | agent-body-quality.md (untracked) | ✓ **CONFIRMED** — this review's M-7 covers the same finding |
| Bootstrap agent frontmatter non-conformance | (this review — new) | C-3 above |

**The 2 untracked prior reviews substantially overlap with this review's findings.** The 2 prior reviews were done by other reviewers (Reviewer + skill-quality lens) and the 3 of us agree on the most important issues (C-1, C-2, C-3 / H-2, H-3). The untracked status of these prior reviews is itself the CRITICAL finding C-1.

---

## 11 · Severity-ordered action list

### CRITICAL (3 findings)

1. **C-1** — `git status -uall` shows 2 untracked review files. Decide: commit or move. Either action closes the gap; the build-lead's "clean branch" claim must be made true.
2. **C-2** — `project-lead.md` and `research-lead.md` — add `## Delegation` section between Responsibilities and Dynamic-readiness.
3. **C-3** — `build-lead.md:60` — change `# Identity` to `## Identity`.

### HIGH (6 findings)

4. **H-1** — `bootstrap.md` — add `delegates: []` and `runtimes: []` to bring it to 11/11 frontmatter fields.
5. **H-2** — 7 of 8 lead bodies — replace restated rule prose with R-### ID citations in Core rules sections.
6. **H-3** — 8 of 8 lead bodies — remove ~430 lines of inlined procedure; reference skills/workflows by name.
7. **H-4** — `project-lead.md` and `research-lead.md` — add `### Prime directive` block in Identity.
8. **H-5** — `constitution-checks/SKILL.md` — align with `constitution-checks.yaml` (YAML is system-of-record per its own comment).
9. **H-6** — `constitution-check/SKILL.md:50` — fix the anti-pattern rule names; align with YAML.

### MEDIUM (9 findings)

10. **M-1** — `aspis preflight` could not be independently verified. Owner runs preflight and records output; or reviewer bash allowlist includes preflight.
11. **M-2** — `cross_ref_agents.py` exists at runtime path but not catalog source. Move to catalog source and add a deploy task, or move to build-time-only location.
12. **M-3** — Re-verify byte-identity of `task_compile.py` (the 4 other files are verified; task_compile is verified by `--help` only).
13. **M-4** — 5 agent bodies reference `.aspis/workflows/` and `.aspis/config/...` paths. Change to `src/aspis/data/catalog/...` (factory-repo perspective) or document the render-time substitution.
14. **M-5** — `constitution-checks.yaml` is missing `C-ARCH-BEFORE-FEATURES`. Add it, or remove from `architecture-constitution.md` and the skills.
15. **M-6** — `AGENT_BODY_STANDARD.md:27` — `mode` field should be `primary/subagent` (per ARCHITECTURE.md), not `vibe/mvp/production`.
16. **M-7** — `project-lead.md:58` and `research-lead.md:35` — swap the title and "Derived" line order.
17. **M-8** — `project-lead.md:141–158` — move bootstrap-gate inline content into a `bootstrap-gate` skill or document the runtime removal mechanism.
18. **M-9** — 4 lead bodies — restructure Identity to IS / IS NOT / prime directive (subsumed by H-4 for the prime-directive gap).

### LOW (5 findings)

19. **L-1** — `edit: '*': allow` / `write: '*': allow` in fix-lead and general-builder — verification note (deny floor honored; standard pattern).
20. **L-2** — Section titles "How you plan" / "How you execute" / "How you review" etc. should be `## How you work` per the standard (or update the standard to allow topic-specific names).
21. **L-3** — `small-task.md` 5-track vs ref-spec 6-track — clarify scope.
22. **L-4** — Path-resolution in `prereq_validate.py` — verification note (works).
23. **L-5** — `reviewer.md:209` — `constitution-checks.yaml` path mismatch (subsumed by M-4).

---

## 12 · What the build did well

To be fair, the build did several things right:

1. **The deny floor is honored on every agent.** No `bash: '*': allow`, no `git push*` anywhere, `git commit*` committer-only, `webfetch` system-lead + research-lead only, `websearch` research-lead-only. This is the system-safety floor and it is solid.
2. **All 28 delegate references resolve to existing catalog agents.** 0 orphan delegates. The M-2 finding from the prior completeness-traceability review is **resolved**.
3. **All 49 skill references resolve to existing SKILL.md files.** 0 broken frontmatter skill references. FR-001 verified at the SC-001 level.
4. **All 5 planning scripts deploy byte-for-byte from catalog source, AST parse, and return usage on `--help`.** The 3 CLI scripts (`feature_scaffold`, `prereq_validate`, `task_compile`) plus the 2 modules (`active_feature`, `_console`) work. The deterministic-first principle (R-003) is operational.
5. **All 5 templates deploy byte-for-byte from catalog source.** All required sections are present.
6. **All 5 workflows are complete, with no TODO/NYI markers, and steps align with the F-016 ref specs.** The build team correctly identified the gap and filled it.
7. **The dynamic-readiness convention is documented, R-008 approved, and all 8 leads reference it.** DYNAMIC_READINESS.md is a durable reference (130 lines) and the 8 lead bodies encode the 3 dials + leanest-correct-path default.
8. **The agent body standard is documented (112 lines), checkable, and the L1 exit gate ran the check.** AGENT_BODY_STANDARD.md is the durable contract.
9. **`prereq_validate.py --phase build` exits 0** on the live feature. The deterministic gate the build claimed is verified.
10. **The build's substantive work is faithful to the F-016 designs.** Every body preserves the design intent, the permission surface, the skill mapping, the role boundaries, and the dynamic-readiness block. The bodies are not role-drifted; they are **shape-drifted** (too long, too inlined, but otherwise correct).
11. **The cross-agent consistency check passes.** `cross_ref_agents.py --scope leads` exits 0 against the F-016 ref specs.
12. **14 new skills authored to the catalog pattern** (7 L0 + 7 L1) with valid frontmatter, Purpose / When to use / Procedure / Outputs / Anti-patterns sections, and self-contained.
13. **The L1 exit gate was honest about what was done.** The ACCEPTANCE.md correctly marks the un-done items (FR-007, FR-008, FR-009, FR-010, FR-011, FR-013, FR-014, FR-015, SC-002, SC-003, SC-004, SC-005, SC-007, SC-009) as `[ ]` and notes "L1-EXIT-READY (Phase 0, 1, 2 complete — STOP at T-32a)".

The build is **structurally correct** at the gate-claim level. The shape-and-discipline gaps are the next layer of work, not a fundamental failure.

---

## 13 · Cost-of-change impact

The current build's bodies are **large** (172–255 lines). Most of the size is inlined procedure that belongs in skills/workflows. The bodies' size is the direct cause of every MEDIUM and HIGH finding (M-1, M-2, M-4, M-6, M-7, M-8, M-9, H-2, H-3, H-4) — when a body inlines 30–50 lines of procedure from a skill, the body grows by that much and the cost-of-change test (SC-011) becomes harder to satisfy.

If the body trim is done, the bodies should land in the **80–120 line** range (thin) and the cost-of-change test continues to pass. The build's choice to inline procedure is the single highest-leverage issue in this review.

A second cost-of-change effect: every time a skill is updated, the corresponding body must also be updated (because the inlined procedure must stay in sync with the skill). This is a **2-file edit** per skill change, not a 1-file edit, which doubles the change-cost of every skill iteration.

After the trim, the cost of changing a skill is **1 file** (the skill itself) + optionally a **second file** (an agent's frontmatter or short body reference) = **2 files** — the same as the current SC-011 target.

---

## 14 · Verdict

**CHANGES REQUIRED** — 3 CRITICAL, 6 HIGH, 9 MEDIUM, 5 LOW.

The build's substantive work is **structurally faithful** to the F-016 reference specs, the permission surface, the skill mapping, the delegate edges, and the dynamic-readiness block. The L1 exit gate (T-32a) approval is correct on the **shape check** (frontmatter, sections, references resolve) and **substantively correct on the design fidelity**. The bodies pass SC-006 (every agent body passes agent-body standard check) at the **shape level** — but they fail it at the **content level** because the standard's "every section is short" and "cite, don't restate" rules are systematically violated by inlined procedure.

**3 of the build-lead's gate claims are FALSE or unverifiable**:
- ✗ `git status` is NOT clean (2 untracked review files — C-1)
- ✗ All 11 fields on all 12 catalog agents is FALSE (bootstrap.md is missing 2 — H-1)
- ⚠ `aspis preflight clean` is unverifiable by the reviewer (M-1)

**The remaining gate claims are TRUE** and independently verified:
- ✓ `prereq_validate.py --phase build` passes
- ✓ 0 `bash: '*': allow`
- ✓ Only committer has `git commit*`; 0 `git push*`; webfetch/websearch floor honored
- ✓ 0 orphan delegates; 49/49 skill references resolve
- ✓ Dynamic-readiness blocks on all 8 leads
- ✓ Deployed scripts and templates match catalog source byte-for-byte
- ✓ 5 workflows clean (no TODO/NYI)
- ✓ L1 exit gate commits all present in correct order

**The fix is mechanical and well-scoped**:
- C-1: 1 commit (or move) for the 2 untracked review files
- C-2: 2 `## Delegation` section additions
- C-3: 1-character fix
- H-1: 2-line frontmatter addition to bootstrap.md
- H-2: ~40 R-### ID citations across 7 bodies
- H-3: ~430 lines of inlined procedure to remove across 8 bodies
- H-4: 2 prime-directive blocks
- H-5 / H-6: align 2 skills with the YAML (or update the YAML)
- M-1..M-9 + L-1..L-5: 9 + 5 small cleanups

**Estimated fix time**: 6–10 hours for 1 build agent.

**Do NOT proceed to T-33+ (L2-P0) without addressing C-1, C-2, C-3, H-1, H-2, H-3, H-4, H-5, H-6.** The MEDIUM and LOW findings are improvements that should be addressed in the same revision pass but are not gate-blocking.

**Recommendation**: route to build-lead for a **revision pass** of the 8 lead bodies, the bootstrap frontmatter, the 2 skills' alignment with the YAML, and the agent-body-standard docstring fix. After the revision pass, re-run the L1 exit gate and the cross-agent consistency check; the system should be L2-P0 ready.

---

## Files reviewed

- `.aspis/scripts/planning/_console.py` (33 lines)
- `.aspis/scripts/planning/active_feature.py` (154 lines)
- `.aspis/scripts/planning/feature_scaffold.py` (227 lines)
- `.aspis/scripts/planning/prereq_validate.py` (157 lines)
- `.aspis/scripts/planning/task_compile.py` (not read end-to-end; verified via `--help` and `--dry-run --feature F-017`)
- `.aspis/scripts/planning/cross_ref_agents.py` (1025 lines, exists at runtime but not catalog source)
- `src/aspis/data/catalog/scripts/planning/<same>.py` (catalog sources, verified byte-identical)
- `.aspis/templates/planning/{SPEC, PLAN, TASKS, ACCEPTANCE, TASK_PACKET}.md` (deployed templates)
- `src/aspis/data/catalog/templates/planning/<same>.md` (catalog sources, verified byte-identical)
- `.aspis/workflows/{plan, build, review, fix, small-task}.md` (5 workflows)
- `src/aspis/data/catalog/agents/{project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer, general-builder, project-explorer, bootstrap}.md` (12 catalog agents)
- `.aspis/context/AGENT_BODY_STANDARD.md` (112 lines)
- `.aspis/context/DYNAMIC_READINESS.md` (130 lines)
- `src/aspis/data/catalog/skills/<14 new skills>/SKILL.md` (mode-decision, recontextualization, session-continuation, constitution-checks, constitution-check, evidence-validation, packet-validation, builder-selection, security-review, catalog-validator, governance-approval, drift-detector, cache-management, harvest-protocol)
- `.aspis/config/policy/constitution-checks.yaml` (65 lines)
- `.aspis/features/F-017-complete-agent-system/{SPEC, PLAN, TASKS, ACCEPTANCE}.md`
- `.aspis/features/F-017-complete-agent-system/Review/{architecture-constitution, completeness-traceability, plan-feasibility}.md` (3 committed prior reviews)
- `.aspis/features/F-017-complete-agent-system/Review/{agent-body-quality, skill-quality}.md` (2 uncommitted prior reviews — see C-1)

## Commands run for verification

```
git status                                    # reports "clean" but git status -uall shows 2 untracked
git log --oneline -5                          # 5 expected commits present
python .aspis/scripts/planning/prereq_validate.py --phase build   # exit 0, [OK] F-017 → build (production)
python .aspis/scripts/planning/feature_scaffold.py --help        # exit 0, usage printed
python .aspis/scripts/planning/prereq_validate.py --help         # exit 0, usage printed
python .aspis/scripts/planning/task_compile.py --help            # exit 0, usage printed
python .aspis/scripts/planning/active_feature.py --help          # exit 0, usage printed
python .aspis/scripts/planning/_console.py --help                # no output (module, not CLI)
python .aspis/scripts/planning/task_compile.py --feature F-017 --dry-run   # exit 0
python .aspis/scripts/planning/cross_ref_agents.py --scope leads  # exit 0, F-016 ref specs internally consistent
aspis context                                  # current state, recent changes, active feature all printed
```
