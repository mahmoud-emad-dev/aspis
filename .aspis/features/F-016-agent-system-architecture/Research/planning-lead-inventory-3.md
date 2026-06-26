# F-016 Research — Planning-Lead Inventory: Skills, Scripts, Gates, Templates, Workflows

> **For:** planning-lead (F-016)
> **Compiled:** 2026-06-26
> **Sources verified through:** 2026-06-26
> **Scope:** every skill, script, validation gate, template, and workflow the planning-lead
> needs across all 8 phases (P0 intake → P5 plan-critic → final prereq-validate), with
> deployment status for each.
> **Sources read:** `.opencode/agents/planning-lead.md`, `local/agents/planning-lead.md`,
> `.aspis/workflows/plan.md`, `local/AGENT-SYSTEM-ARCHITECTURE.md`, the 3 F-016 research
> files (current-aspis-audit-1, old-asps-workflows-scripts-2, system-agent-tooling), plus
> direct file-system verification of `.opencode/skills/`, `.claude/skills/`,
> `.aspis/scripts/`, `.aspis/templates/`, `.aspis/workflows/`,
> `.aspis/config/policy/`, and `src/aspis/data/catalog/`.
> **Provenance:** live tree at `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS`
> verified 2026-06-26. The catalog is the source of truth; `.opencode/` and `.claude/` are
> the deployed renderings; `.aspis/` is the project brain.

---

## TL;DR — The five top-line findings

1. **The bash allow-list in planning-lead.md is broken.** It permits
   `python .aspis/scripts/planning/*` but that directory **does not exist** on disk.
   The 5 catalog scripts (`feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`,
   `active_feature.py`, `_console.py`) live only in `src/aspis/data/catalog/scripts/planning/`.
   Either the renderer must export them to `.aspis/scripts/planning/` on `aspis init`,
   or the planning-lead's bash allow-list must use the catalog path. **The audit
   claimed 23 catalog scripts are deployed; they are deployed for `context/`, `git/`,
   `hooks/` — but not for `planning/`.** This is the single most operationally
   important gap.

2. **The plan workflow references two skills that are not in planning-lead's
   allow-list.** Step 7 of `plan.md` says *"skill `review-strategy` + the
   `plan-critic` workflow"*. Both skills exist in the catalog and are deployed to
   `.opencode/skills/`, but `planning-lead.md` only allow-lists 7 skills
   (prestart-checks, context-ladder, planning-intake, requirement-clarification,
   feature-planning, architecture-planning, task-decomposition). **The workflow
   asks for a tool the allow-list denies.**

3. **Plan-critic is the right shape but is light** (44 lines; the audit's
   "light" rating). The OLD ASPS had a multi-axis check (CHK001–CHK013, 3 groups:
   Content Quality, Requirement Completeness, Feature Readiness). Current
   `plan-critic/SKILL.md` covers 6 axes (traceability, measurability, coherence,
   ordering, resolved unknowns, rules & gate) but has no script that automates
   the check (e.g. "every FR-### is covered by at least one task").

4. **There are no per-mode workflow variants.** A single `plan.md` with overlay
   bullets. OLD ASPS's `PLANNING_WORKFLOW.md` was mode-aware. The current
   modes.yaml has 8 knobs; the workflow only reads 3 (architecture, plan_review,
   test_depth). The other 5 (spec, task_size, build_review, docs, promotable) are
   not consulted by `plan.md`.

5. **Five templates planning-lead needs are not on disk.** CLARIFICATION_LOG,
   RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE. The
   workflow names them implicitly ("record answers in the SPEC's Clarifications",
   "send genuine unknowns to the Research Lead", "state the plan-of-plan in one
   or two lines") but no template exists. Per-mode variants (SPEC.vibe.md etc.)
   are also missing — the current shape uses inline mode hints.

---

## 1 · Skills — existing + missing

### 1.1 The 7 skills in the planning-lead allow-list (LIVE)

Source: `.opencode/agents/planning-lead.md` lines 32–40.

| # | Skill | Deployed `.opencode/skills/<n>/SKILL.md`? | Deployed `.claude/skills/<n>/SKILL.md`? | Catalog `src/aspis/data/catalog/skills/<n>/SKILL.md`? | Sufficient? | What's missing |
|---|---|---|---|---|---|---|
| 1 | `prestart-checks` | YES | YES | YES | Yes — global gate; well-shaped | None — used as-is |
| 2 | `context-ladder` | YES | YES | YES | Yes — the L1→L4 ladder is proven | No real gap; this is the right shape |
| 3 | `planning-intake` | YES | YES | YES | Mostly — 65 lines, reads modes.yaml | See §1.3 below |
| 4 | `requirement-clarification` | YES | YES | YES | Mostly — 41 lines, max-5-questions rule | See §1.3 below |
| 5 | `feature-planning` | YES | YES | YES | Mostly — 40 lines, fills SPEC template | See §1.3 below |
| 6 | `architecture-planning` | YES | YES | YES | Mostly — 39 lines, gate-check is named not automated | See §1.3 below |
| 7 | `task-decomposition` | YES | YES | YES | Mostly — 41 lines, fills TASKS + packets | See §1.3 below |

### 1.2 Skills in catalog but NOT in planning-lead's allow-list (DEPLOYED but DENIED)

| # | Skill | Where used (workflow / other agent) | Why planning-lead needs it | Status |
|---|---|---|---|---|
| A | `plan-critic` | `plan.md` step 7 EXPLICITLY names it; also `reviewer` agent's allow-list | Step 7 of the workflow requires it; current allow-list denies it | **CRITICAL — wire it in** |
| B | `review-strategy` | `plan.md` step 7 EXPLICITLY names it; also `reviewer` agent | Step 7 says "skill `review-strategy` + the `plan-critic` workflow"; allow-list denies it | **CRITICAL — wire it in** |
| C | `deterministic-first` | `system-lead` agent; design pattern | Planning should know it: the cheap mechanism first (script → tool → workflow → agent) | Should be allow-listed for P0/P3 |
| D | `scope-control` | `build-lead`, `fix-lead` | Planning needs it when designing the task packets' allowed/forbidden files | Should be allow-listed for P4 |
| E | `context-packaging` | `project-lead` | Planning is the consumer of context-packets from project-lead | Optional — useful for receiving packets |
| F | `quality-review` | `reviewer` | The "what to check" lens for the plan | Optional — covered by plan-critic for now |
| G | `acceptance-decision` | `reviewer` | Mirror of the plan-critic verdict | Optional — reviewer's domain |

### 1.3 Per-skill sufficiency — what's missing from each of the 7

#### `planning-intake` (65 lines)
**Sufficient:** Mode resolution (request → active → project → modes.yaml), track classification, knob reading, plan-of-plan.

**Missing:**
- **No `mode-decision` skill** — the decision of which mode is implicit. There is no scripted rubric ("if blast radius > X, refuse vibe; if files touched > 5, require architecture: note"). The skill says "you may infer" and "confirm with the user" but offers no heuristic.
- **No `scope-estimation` skill** — the "how big is this" read is done by the model from prose. The plan-of-plan is "one or two lines" but has no script that produces a rough effort estimate (number of files, number of tasks, risk score) from a request.
- **No `cost-estimation` skill** — there is no guidance on the token / model cost of running the plan. The audit says "70% cheap / 20% standard / 10% deep"; planning-intake shades task_size by model but does not project cost.
- The "shade by builder's model" rule (line 41–42) is right but the lookup is manual ("read `agent-models.yaml`"). A script (`mode_validator.py` or `scope_estimate.py`) would make it mechanical.

#### `requirement-clarification` (41 lines)
**Sufficient:** 5-step procedure (gather context → resolve from convention → identify research → prioritize → ask minimally), max-5-questions rule.

**Missing:**
- **No `CLARIFICATION_LOG.md` template** — the skill says "record these as explicit assumptions" and the workflow says "record answers in the SPEC's Clarifications" but there is no structured place. Today it's a free-text blob inside SPEC.md.
- **No `RESEARCH_REQUEST.md` template** — the skill says "request it from the Research Lead" but there is no standard form. The OLD ASPS had `RESEARCH_NOTE.template.md` (research-lead's output); the request side is unstructured.
- **No 10-category ambiguity scan** — OLD ASPS's `clarify` skill had a 10-category scan (functional, non-functional, data, integration, security, performance, usability, edge cases, error handling, operational). Current skill is 5 procedural steps, no taxonomy.

#### `feature-planning` (40 lines)
**Sufficient:** 6-step procedure (goal+problem → scope → behavior → requirements → acceptance → assumptions).

**Missing:**
- **No `plan-quality-check` script** — the procedure is correct, but there is no automated check that the SPEC has the right shape (FR-### numbers, SC-### numbers, scope section, no `[NEEDS CLARIFICATION]` surviving in production mode). The audit's "Feature Quality Checklist" (CHK001–CHK013) was a 13-item pre-build gate; nothing equivalent exists today.
- **No Given/When/Then template helper** — the skill says "Given/When/Then scenarios for each slice" but the SPEC template uses free-form bullets. The structure is asked for, not enforced.
- **No measurable-criterion lint** — "measurable, technology-agnostic success criteria" is a hand-wave. A `plan_quality_check.py` that lints SC-### lines for "is this objectively checkable" would close this.

#### `architecture-planning` (39 lines)
**Sufficient:** 5-step procedure (approach → structure → context → steps+gates → risks+rollback).

**Missing:**
- **No `constitution_check.py`** — the skill says "gate-check vs architecture constitution" but there is no script that reads `constitution-checks.yaml` and verifies the plan against each check. Today it's "the agent reads the rules and asks the question." A deterministic check on the plan text would close the loop.
- **No `constitution-check` skill** — the 11 checks in `constitution-checks.yaml` (C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE) are split across `enforced_by: planning | build | review` but no skill owns "the planning-time check." A new skill (`constitution-check`) or a new step in `architecture-planning` would close this.
- **No `dependency-graph.py`** — the skill says "ordered steps" but no script builds a dependency graph from the plan. The audit's `dependency_graph.py` was a proposed addition; not implemented.

#### `task-decomposition` (41 lines)
**Sufficient:** 5-step procedure (decompose → sequence → packets → strategy → record).

**Missing:**
- **No `task_size_check.py`** — `modes.yaml` defines `task_size: large|medium|small` per mode but there is no script that verifies each task packet's granularity. Old ASPS's `BUILD_UNIT.template.md` had "When to split into a build unit" guidance; the current procedure has no mechanical check.
- **No `dependency-graph.py`** — `[P]` markers (parallel) and ordering are hand-written; a script that validates the dependency graph (no cycles, `[P]` tasks touch different files) would be valuable.
- **No packet-acceptance linter** — TASK_PACKET.md is filled by `task_compile.py` for the deterministic fields; the rich fields (context, skeleton, acceptance, review routing) are "guidance for the Build Lead to enrich." No check that the enriched packet is build-ready.

### 1.4 Missing skills (referenced in old ASPS or implied by workflow — not in catalog)

| # | Missing skill | Why planning-lead needs it | OLD ASPS equivalent | Priority |
|---|---|---|---|---|
| M1 | `review-strategy` | **Already in catalog** — just not in allow-list (§1.2 row B). Add to allow-list. | Same name | **CRITICAL** |
| M2 | `plan-critic` | **Already in catalog** — just not in allow-list (§1.2 row A). Add to allow-list. | Same name | **CRITICAL** |
| M3 | `plan-quality-check` | A scripted pre-build gate (CHK001–CHK013 equivalent) that lints SPEC/PLAN/TASKS shape. | `CHECKLIST.template.md` (13 items, 3 groups) | HIGH |
| M4 | `scope-estimation` | Determines `task_size`, story count, blast radius from a request, before intake commits to a mode. | `idea-capture` sub-agent (F-027 draft) | HIGH |
| M5 | `constitution-check` | Owns the planning-time gate against `constitution-checks.yaml` C-COST, C-LOCAL-CHANGE, C-TESTABLE. | Implicit in `spec-to-plan` skill | HIGH |
| M6 | `mode-decision` | A rubric that maps request features (blast radius, risk, dependencies) → mode, not just "you may infer." | Implicit | MEDIUM |
| M7 | `cost-estimation` | Projects token/model cost of a plan (cheap vs deep per task) from a draft. | Not in OLD ASPS | LOW (post-trace-spine) |
| M8 | `dependency-graph` (skill) | Owns the [P]/[US] validation: no cycles, parallel tasks touch different files. | `dependency-audit` skill | MEDIUM |
| M9 | `clarify` (subagent) | 10-category ambiguity scan + max-5 prioritized questions; was a subagent in old ASPS. | `clarify` (subagent, 10 categories) | MEDIUM |
| M10 | `task-decomposer` (subagent) | PLAN → ordered TASK packets, with [P]/[US] markers computed, not guessed. | `task-decomposer` subagent | LOW (can stay as skill) |

### 1.5 Skills parity: catalog vs `.opencode` vs `.claude` vs allow-list

| Skill | Catalog | `.opencode/skills/` | `.claude/skills/` | planning-lead allow-list | Notes |
|---|---|---|---|---|---|
| prestart-checks | YES | YES | YES | YES | full parity |
| context-ladder | YES | YES | YES | YES | full parity |
| planning-intake | YES | YES | YES | YES | full parity |
| requirement-clarification | YES | YES | YES | YES | full parity |
| feature-planning | YES | YES | YES | YES | full parity |
| architecture-planning | YES | YES | YES | YES | full parity |
| task-decomposition | YES | YES | YES | YES | full parity |
| plan-critic | YES | YES | YES | **NO** | **wire it in** |
| review-strategy | YES | YES | YES | **NO** | **wire it in** |
| deterministic-first | YES | YES | YES | NO | optional |
| scope-control | YES | YES | YES | NO | optional |
| context-packaging | YES | YES | YES | NO | optional |
| quality-review | YES | YES | YES | NO | optional |
| acceptance-decision | YES | YES | YES | NO | optional |
| All other 24 skills (38 total) | YES | YES | YES | NO | not planning-lead's domain |

**Verification:** glob on `.opencode/skills/*/SKILL.md` returns 19 directories (the live deployment after some artifacts were removed); glob on `.claude/skills/*/SKILL.md` returns 20 directories; the catalog has 38. The live runtime is **partially deployed** — about half the catalog's skills are in each runtime. This is a deeper gap than the planning-lead allow-list alone.

---

## 2 · Scripts — existing + missing

### 2.1 The 3 scripts in the bash allow-list (planning-lead's allow-list has `python .aspis/scripts/planning/*`)

| # | Script | In catalog? | In `.aspis/scripts/planning/`? | What it does | Deployment status |
|---|---|---|---|---|---|
| 1 | `feature_scaffold.py` | YES — `src/aspis/data/catalog/scripts/planning/feature_scaffold.py` | **NO** — directory missing | Allocate F-NNN, create `.aspis/features/F-NNN-slug/`, copy SPEC/PLAN/TASKS, write active pointer, create branch | **DEPLOYMENT GAP** — script exists in catalog but not in project's `.aspis/scripts/`. The bash allow-list references a path that does not exist. |
| 2 | `task_compile.py` | YES — `src/aspis/data/catalog/scripts/planning/task_compile.py` | **NO** | Parse TASKS.md → render one TASK_PACKET.md per task into `tasks/` (fills deterministic fields) | **DEPLOYMENT GAP** — same as above |
| 3 | `prereq_validate.py` | YES — `src/aspis/data/catalog/scripts/planning/prereq_validate.py` | **NO** | Gate phase order (no plan without SPEC, no build without TASKS); relaxes by mode | **DEPLOYMENT GAP** — same as above |
| 4 | `active_feature.py` | YES — `src/aspis/data/catalog/scripts/planning/active_feature.py` | **NO** | Read/write `.aspis/current/active_feature.json` | **DEPLOYMENT GAP** — same as above |
| 5 | `_console.py` | YES — `src/aspis/data/catalog/scripts/planning/_console.py` | **NO** | Shared stdlib-only console helper | **DEPLOYMENT GAP** — same as above |

**The audit (current-aspis-audit-1.md §4.4) said 5 planning scripts are deployed. They are deployed to the catalog. They are NOT deployed to `.aspis/scripts/planning/`. The other 3 script groups (context, git, hooks) are deployed correctly to `.aspis/scripts/{context,git,hooks}/`.** This is an asymmetric deployment gap. Resolution: either the export must copy the planning scripts on `aspis init`, or planning-lead's allow-list must point to the catalog.

### 2.2 Verifying what IS in `.aspis/scripts/`

| Group | Files deployed to `.aspis/scripts/` | What works |
|---|---|---|
| `context/` | 6 files (`_common.py`, `build_code_map.py`, `build_registry.py`, `build_state.py`, `record_changes.py`, `update.py`) | YES — used by `aspis preflight`, `aspis context` |
| `git/` | 1 file (`compose.py`) | YES — used by `aspis commit` |
| `hooks/` | 10 files (`_config.py`, `_git.py`, `cleanup.py`, `commitmsg.py`, `findings.py`, `gitignore.py`, `install.py`, `postcommit.py`, `precommit.py`, `runtime_guard.py`, `scope.py`, `secret_scan.py`) | YES — wired into git hooks |
| `planning/` | **0 files — directory does not exist** | **NO — workflow is broken** |

### 2.3 Missing scripts (not in catalog at all)

| # | Missing script | Why planning-lead needs it | Priority |
|---|---|---|---|
| S1 | `scope_estimate.py` | Read a request, scan project for impact (file count by area, blast radius, dependency touchpoints) → emit a numeric score. Used by `planning-intake` to pick mode. | HIGH |
| S2 | `constitution_check.py` | Read a feature's PLAN.md + the 11 checks in `constitution-checks.yaml` → run a text-pattern check (e.g. "C-COST: count files changed; if > 10, WARN") → emit pass/fail per check. | HIGH |
| S3 | `plan_quality_check.py` | Read SPEC.md + PLAN.md + TASKS.md, lint: (a) every FR-### has at least one task; (b) every SC-### is testable; (c) no `[NEEDS CLARIFICATION]` in production; (d) phases are in order; (e) `[P]` tasks touch different files. | HIGH |
| S4 | `mode_validator.py` | Validate that the project's chosen mode has consistent knobs (e.g. `plan_review: skip` + `build_review: full` is incoherent). | MEDIUM |
| S5 | `task_size_check.py` | Read TASKS.md, count tasks, count paths per task, estimate packet complexity. Flag tasks above/below the mode's `task_size` knob. | MEDIUM |
| S6 | `dependency_graph.py` | Build the task dependency graph from `[US]` markers + file paths, validate no cycles, emit a DOT/Mermaid diagram. | MEDIUM |
| S7 | `template_fill.py` | A general-purpose template placeholder filler (used by feature_scaffold, task_compile, and any future template-driven artifact). Today each script has its own `_fill`. | LOW (refactor) |
| S8 | `clarification_log.py` | Read/write `CLARIFICATION_LOG.md`; track assumptions, questions, and resolutions. | LOW (paired with template) |
| S9 | `scope_estimate_report.py` | Produce a human-readable scope report from a project scan. | LOW |

### 2.4 What bash commands planning-lead needs beyond the current allowlist

Current allowlist (`.opencode/agents/planning-lead.md`):
```yaml
bash:
  '*': deny
  'git status*': allow
  'git diff*': allow
  'git log*': allow
  'aspis preflight*': allow
  'aspis findings*': allow
  'aspis context*': allow
  'python .aspis/scripts/context/*': allow
  'python3 .aspis/scripts/context/*': allow
  'python .aspis/scripts/planning/*': allow     # BROKEN — see §2.1
  'python3 .aspis/scripts/planning/*': allow    # BROKEN
  'git commit*': deny
  'git push*': deny
```

| Command | Why needed | Status |
|---|---|---|
| `python .aspis/scripts/planning/*` | feature_scaffold, task_compile, prereq_validate, active_feature | **Listed but directory missing** — see §2.1 |
| `python src/aspis/data/catalog/scripts/planning/*` | same scripts, alternate path | Not listed; the planning scripts only exist in the catalog |
| `aspis mode*` | Read current mode for planning-intake step 3 | Not in allowlist — the skill says "read modes.yaml" but `aspis mode` is the CLI |
| `aspis artifact*` | Stamp ACCEPTANCE.md on demand (modes gate this) | Not in allowlist |
| `aspis tests*` | Skip-list check (file-first test ledger) | Not in allowlist; planning doesn't run tests |
| `git checkout*` | Switch branch after scaffold (if user asked to keep current) | Not in allowlist — feature_scaffold already does this on write |
| `git status -s*` | Lightweight check (current is `git status*` which matches) | Covered |
| `git rev-parse*` | Find the current HEAD ref for the plan's branch reference | Not in allowlist |
| `python .aspis/scripts/constitution_check.py` (proposed) | Constitution gate | Not in allowlist; doesn't exist |
| `python .aspis/scripts/plan_quality_check.py` (proposed) | Plan-quality gate | Not in allowlist; doesn't exist |
| `python .aspis/scripts/scope_estimate.py` (proposed) | Scope estimation | Not in allowlist; doesn't exist |
| `python .aspis/scripts/task_size_check.py` (proposed) | Task-size validation | Not in allowlist; doesn't exist |

---

## 3 · Validation gates — per phase

The plan workflow has 8 steps. Each step ends with a deterministic check or a skill that
emits a verdict. The audit (`current-aspis-audit-1.md` §3) confirms: hooks and policy
data are the *enforcement*; skills are the *judgment*. The mixed table below names
**what must pass** at each phase, the **mechanism** (script vs skill vs hook), and
the **current deployment status**.

### P0 — Intake gate (after planning-intake)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| Request classified (track: question / trivial / small / feature / project) | `planning-intake` skill | DEPLOYED | No script that parses the request — classification is model judgment |
| Complexity assessed (scope, risk, dependencies, unknowns, blast radius) | `planning-intake` skill | DEPLOYED | No `scope_estimate.py` — see §2.3 S1 |
| Mode picked (request → active → project → modes.yaml) | `planning-intake` skill | DEPLOYED | No `mode-decision` skill — see §1.4 M6; no `mode_validator.py` |
| Mode knobs read from `.aspis/config/modes.yaml` | `planning-intake` skill + file read | DEPLOYED | OK |
| Plan-of-plan stated (track, mode, artifacts) | `planning-intake` skill | DEPLOYED | No `PLAN_OF_PLAN.md` template — see §4 |

**Gate:** the plan-of-plan in one or two lines, recorded in the active feature pointer (or in a placeholder). **Currently**: no formal record; the skill says "state" but no template.

### P1 — Clarify gate (after requirement-clarification)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| Assumptions resolved from project convention | `requirement-clarification` skill | DEPLOYED | No `CLARIFICATION_LOG.md` — see §4 |
| Research needs identified and sent to research-lead | `requirement-clarification` skill | DEPLOYED | No `RESEARCH_REQUEST.md` template — see §4 |
| Open questions prioritized (critical / important / optional) | `requirement-clarification` skill | DEPLOYED | No 10-category scan — see §1.3 |
| Max 5 questions asked | `requirement-clarification` skill | DEPLOYED | OK (but no tool to enforce; the skill is the only check) |
| Anything unresolved → `[NEEDS CLARIFICATION]` in SPEC.md | workflow step 3 | DEPLOYED (manual) | No lint that checks the marker count |

**Gate:** SPEC.md has a `## Clarifications` section with each assumption/question listed, and any unresolved is tagged `[NEEDS CLARIFICATION]`. **Currently**: shape is informal; the SPEC template's structure is the only enforcement.

### P2 — Spec gate (after feature-planning)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| SPEC.md has goal + problem (1-2 sentences each) | `feature-planning` skill | DEPLOYED | No lint |
| SPEC.md has scope (in AND out) | `feature-planning` skill | DEPLOYED | No lint |
| SPEC.md has Given/When/Then scenarios per slice | `feature-planning` skill | DEPLOYED (asked) | No template helper, no lint |
| FR-### numbered, testable | `feature-planning` skill | DEPLOYED (asked) | No `plan_quality_check.py` |
| SC-### numbered, measurable | `feature-planning` skill | DEPLOYED (asked) | No `plan_quality_check.py` |
| No `[NEEDS CLARIFICATION]` survives in production mode | `plan-critic` step 5 | DEPLOYED (skill) | **No script enforces this** — only the plan-critic skill (light) catches it at P5 |

**Gate:** SPEC.md passes `plan_quality_check.py` (or, in the absence of the script, the planning-lead's own check). **Currently**: informal; plan-critic is the only structural check, and it runs at P5, not P2.

### P3 — Architecture gate (after architecture-planning)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| PLAN.md has approach (strategy, 2-3 sentences) | `architecture-planning` skill | DEPLOYED | No lint |
| PLAN.md has structure (components, data flow, interfaces, dependencies) | `architecture-planning` skill | DEPLOYED | No lint |
| PLAN.md has steps + deterministic gates per step | `architecture-planning` skill | DEPLOYED (asked) | No `dependency_graph.py` |
| PLAN.md has risks + rollback | `architecture-planning` skill | DEPLOYED | No lint |
| Constitution gate-check (11 checks) | `architecture-planning` skill (named) | DEPLOYED (asked) | **No `constitution_check.py` script** — see §1.3 architecture-planning missing, §2.3 S2 |
| Consistency with `.aspis/context/ARCHITECTURE.md` (as-built) | `architecture-planning` skill (line 68-70 of planning-lead.md) | DEPLOYED (asked) | No script compares; manual read |
| For mvp / vibe: gate-check may be lighter per mode | modes.yaml | DEPLOYED (mode knob `architecture`) | OK |

**Gate:** PLAN.md passes `constitution_check.py` (when it exists). **Currently**: planning-lead reads the 11 rules and asks the question; no script. The audit's note on constitution (`constitution_check.py` was listed as "missing") stands.

### P4 — Tasks gate (after task-decomposition)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| TASKS.md has phased structure (Setup → Foundational → per-story tests-first → Polish) | `task-decomposition` skill | DEPLOYED (asked) | No lint for phase ordering |
| TASKS.md has `[P]` markers for parallel tasks | `task-decomposition` skill | DEPLOYED (asked) | No lint for `[P]` correctness |
| TASKS.md has `[US]` markers traceable to SPEC stories | `task-decomposition` skill | DEPLOYED (asked) | No lint for traceability |
| TASKS.md has exact paths in backticks per task | `task-decomposition` skill + `task_compile.py` parser | DEPLOYED | OK — `task_compile.py` parses |
| TASK_PACKET.md emitted per task into `tasks/` | `task_compile.py` | DEPLOYED (in catalog; **NOT deployed to .aspis/scripts/**) | See §2.1 |
| Each packet's deterministic fields filled | `task_compile.py` | DEPLOYED (catalog) | OK |
| Each packet's rich fields enriched from feature context | `task-decomposition` skill + build-lead (later) | DEPLOYED (asked) | No lint for "is this packet build-ready" |
| Task size per mode (`task_size: large|medium|small`) | modes.yaml knob | DEPLOYED (asked) | No `task_size_check.py` — see §2.3 S5 |
| Dependency graph valid (no cycles) | `task-decomposition` skill | DEPLOYED (asked) | No `dependency_graph.py` — see §2.3 S6 |

**Gate:** TASKS.md passes `plan_quality_check.py` and `task_size_check.py`. **Currently**: only the workflow's structural check; no scripts.

### P5 — Plan-critic gate (after review-strategy + plan-critic)

This is the only step in the workflow that explicitly invokes a non-allow-listed skill.

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| Traceability: every FR-### and story maps to ≥1 task | `plan-critic` step 1 | DEPLOYED (skill) | No script that parses FR-### and links to tasks |
| Measurability: every SC-### is observable + has a task or test | `plan-critic` step 2 | DEPLOYED (skill) | No script |
| Coherence: plan's approach delivers spec's scope | `plan-critic` step 3 | DEPLOYED (skill) | No script; model judgment |
| Ordering: phases respect dependencies; `[P]` tasks touch different files; tests precede impl | `plan-critic` step 4 | DEPLOYED (skill) | No `dependency_graph.py` |
| Resolved unknowns: no `[NEEDS CLARIFICATION]` survives in production | `plan-critic` step 5 | DEPLOYED (skill) | No script lint |
| Rules & gate: plan's gate-check is honest; R-009 flags surfaced | `plan-critic` step 6 | DEPLOYED (skill) | No script |
| `plan-critic` skill loaded | bash allowlist | **NOT ALLOWED** | **wire `plan-critic` into the allow-list** |
| `review-strategy` skill loaded | bash allowlist | **NOT ALLOWED** | **wire `review-strategy` into the allow-list** |
| Production mode: independent Reviewer pass | modes.yaml `plan_review: independent` | DEPLOYED (asked) | The Reviewer's `plan-critic` invocation is a delegation — needs `permission.task: reviewer: allow` (it is allowed) |

**Gate:** `plan-critic` returns a verdict (ready / changes-required). **Currently**: only the skill, no script to back it; allow-list denies the skill. **Two corrections needed: (a) allow-list `plan-critic` and `review-strategy`; (b) write a `plan_quality_check.py` script.**

### Final — prereq-validate gate (before handoff to build-lead)

| Check | Mechanism | Status | What's missing |
|---|---|---|---|
| Phase = build, mode resolved, artifacts present | `prereq_validate.py` | DEPLOYED (in catalog; **NOT in `.aspis/scripts/`**) | See §2.1 |
| Required artifacts per phase present (SPEC, PLAN, TASKS) | `prereq_validate.py` | DEPLOYED (catalog) | OK |
| Mode relaxation: `architecture: skip` → PLAN.md not required | `prereq_validate.py` (lines 120-121) | DEPLOYED (catalog) | OK |
| Active feature pointer resolves to the right feature | `prereq_validate.py` → `active_feature.py` | DEPLOYED (catalog) | OK |
| Exit 0 = pass, 1 = block | `prereq_validate.py` (line 153) | DEPLOYED (catalog) | OK |

**Gate:** `prereq_validate.py --phase build` returns 0. **Currently**: script works in catalog; cannot be invoked from `.aspis/scripts/planning/` (path doesn't exist).

---

## 4 · Templates — existing + missing

### 4.1 Existing templates in `.aspis/templates/`

Verified by glob on `.aspis/templates/`.

| Template | Path | Stamped by | Mode gate |
|---|---|---|---|
| SPEC.md | `.aspis/templates/planning/SPEC.md` | `feature_scaffold.py` (per feature) | per mode |
| PLAN.md | `.aspis/templates/planning/PLAN.md` | `feature_scaffold.py` (per feature) | per mode |
| TASKS.md | `.aspis/templates/planning/TASKS.md` | `feature_scaffold.py` (per feature) | per mode |
| TASK_PACKET.md | `.aspis/templates/planning/TASK_PACKET.md` | `task_compile.py` (per task) | per mode |
| ACCEPTANCE.md | `.aspis/templates/planning/ACCEPTANCE.md` | `aspis artifact acceptance` | none |
| ARCHITECTURE.md | `.aspis/templates/context/ARCHITECTURE.md` | init seeds it; bootstrap enriches | n/a |
| feature.md | `.aspis/templates/report/feature.md` | `aspis artifact feature` | `docs != none` |
| build.md | `.aspis/templates/report/build.md` | `aspis artifact build --task T-NN` | `docs != none` |
| review.md | `.aspis/templates/review/review.md` | `aspis artifact review --task T-NN` | `build_review != light` |
| test.md | `.aspis/templates/review/test.md` | `aspis artifact test --task T-NN` | `test_depth != gate` |

**Total: 10 templates, 4 categories** (per audit §5). 5 are planning-related (SPEC, PLAN, TASKS, TASK_PACKET, ACCEPTANCE).

### 4.2 Missing templates (workflow names them; files do not exist)

| # | Missing template | Why planning-lead needs it | Workflow reference | Priority |
|---|---|---|---|---|
| T1 | `CLARIFICATION_LOG.md` | Structured record of assumptions, questions, and resolutions; referenced by `requirement-clarification` step 5 and the workflow step 3 ("record answers in the SPEC's Clarifications") | plan.md step 3; requirement-clarification step 2 | HIGH |
| T2 | `RESEARCH_REQUEST.md` | The handoff from planning to research; today the skill says "request it from the Research Lead" but no form exists. OLD ASPS had `RESEARCH_NOTE.template.md` (research side) but the request side was also free-form. | plan.md step 3; requirement-clarification step 3 | HIGH |
| T3 | `PLAN_OF_PLAN.md` | The 1-2 line plan-of-plan that `planning-intake` says to "state" before proceeding. Today it lives in chat only. | plan.md step 1; planning-intake step 5 | MEDIUM |
| T4 | `DEPENDENCIES.md` | The dependency graph output from `dependency_graph.py`. | plan.md step 6 (tasks) | MEDIUM |
| T5 | `SCOPE_ESTIMATE.md` | The numeric scope estimate from `scope_estimate.py`. | plan.md step 1 (intake) | MEDIUM |
| T6 | `CONSTITUTION_REPORT.md` | The output of `constitution_check.py` — per-check verdict, evidence, and the planning-lead's notes. | plan.md step 5 (architecture) | MEDIUM |
| T7 | `RISKS_AND_ROLLBACK.md` (separate) | Currently embedded in PLAN.md; a standalone file would let `risk-analysis.py` work it independently. | architecture-planning step 5 | LOW (refactor) |
| T8 | `ACCEPTANCE_TRACE.md` | Maps each FR-###/SC-### to the test that proves it (output of `plan_quality_check.py`). | plan-critic step 2 | MEDIUM |
| T9 | `PLAN_QUALITY_REPORT.md` | Output of `plan_quality_check.py`. | plan.md step 7 | MEDIUM |
| T10 | `MODE_DECISION.md` | Records why a mode was chosen (evidence + rubric), so the choice is reviewable. | planning-intake step 3 | LOW |

### 4.3 Per-mode template variants (planned but not shipped)

`plan.md` step 4 says "compress step 4 to a few SPEC bullets" for vibe; "step 5 is a light note" for mvp. The audit (current-aspis-audit-1.md §12.2) said "modes.yaml is the single source" but `feature_scaffold.py` writes one SPEC.md / PLAN.md / TASKS.md per feature, and the templates' mode hints are inline. There is no `SPEC.vibe.md` / `SPEC.mvp.md` / `SPEC.production.md` triplet, no `PLAN.mvp.md` light variant, no `TASKS.vibe.md` coarse variant.

| Missing template variant | What it would carry | Priority |
|---|---|---|
| `SPEC.vibe.md` | Few bullets, no FR/SC numbers, scope only | LOW (inline hints suffice) |
| `SPEC.mvp.md` | Stories + light FR numbers, no SC numbers | LOW |
| `SPEC.production.md` | Full Given/When/Then, FR-###, SC-### | LOW (the current SPEC is already production-shaped) |
| `PLAN.vibe.md` | Skip entirely (`architecture: skip`) | N/A (the prereq-validate already handles) |
| `PLAN.mvp.md` | Light note only | LOW |
| `TASKS.vibe.md` | Coarse, large tasks, fewer `[P]`/`[US]` markers | LOW |
| `TASKS.production.md` | Small, every task has a test | LOW |

**Conclusion:** per-mode variants are a nice-to-have, not a critical gap. The current single template + inline mode hint is workable; the audit's note on "maturity of templates" is fair but the gap is polish, not blocker.

### 4.4 Template per-phase field map (what's where today)

| Field | SPEC.md | PLAN.md | TASKS.md | TASK_PACKET.md | ACCEPTANCE.md |
|---|---|---|---|---|---|
| Goal / problem | YES | — | — | — | — |
| Scope (in/out) | YES | — | — | — | — |
| Behavior (Given/When/Then) | YES (asked) | — | — | — | — |
| FR-### | YES (asked) | — | — | — | mirror |
| SC-### | YES (asked) | — | — | — | mirror |
| Clarifications | partial | — | — | — | — |
| Approach | — | YES | — | — | — |
| Structure / components | — | YES | — | — | — |
| Technical context | — | YES | — | — | — |
| Steps + gates | — | YES | — | — | — |
| Risks + rollback | — | YES | — | — | — |
| Constitution gate-check | — | YES (asked) | — | — | — |
| Phased tasks | — | — | YES | — | — |
| `[P]` / `[US]` markers | — | — | YES (asked) | — | — |
| Task ID + title + paths | — | — | YES | YES (auto) | — |
| Allowed files | — | — | — | YES (auto from paths) | — |
| Steps | — | — | — | YES (enrich) | — |
| Tests | — | — | — | YES (enrich) | — |
| Done when | — | — | — | YES (enrich) | — |
| Review routing | — | — | — | YES (enrich) | — |
| Sign-off | — | — | — | — | YES |

**The deterministic fields (auto-filled by `task_compile.py`) are feature id, task id, title, paths. The rich fields (context, skeleton, acceptance, review routing) are filled by the Build Lead during packet enrichment.** This split is correct per the audit; the planning-lead's P4 work is the rich-field authoring.

---

## 5 · Workflows

### 5.1 Current workflow inventory

Verified by glob on `.aspis/workflows/`. **5 workflows** (the audit said 6, including bootstrap.md — but bootstrap is in catalog only, not in the live `.aspis/workflows/` after self-clean).

| # | Workflow | Path | Owner | Mode overlays? |
|---|---|---|---|---|
| 1 | plan.md | `.aspis/workflows/plan.md` | planning-lead | YES (vibe / mvp / production bullet) |
| 2 | build.md | `.aspis/workflows/build.md` | build-lead | YES |
| 3 | review.md | `.aspis/workflows/review.md` | reviewer | YES |
| 4 | fix.md | `.aspis/workflows/fix.md` | fix-lead | YES (production rigor regardless of feature mode) |
| 5 | small-task.md | `.aspis/workflows/small-task.md` | (no lead — used by build-lead or planning-lead) | implied |

### 5.2 Is `plan.md` sufficient?

The plan.md is 52 lines; 8 steps. The audit's "Workflow doc depth" rating: **C+** (lean, 30-50 lines; old ASPS's were 200+ with status discipline).

| Aspect | Current `plan.md` | Sufficient? | What's missing |
|---|---|---|---|
| Numbered steps | 8 | YES | — |
| Each step names the skill | YES (step 1, 3, 4, 5, 6, 7) | YES | Step 2 (scaffold) names the script; step 8 (gate) names the script — good |
| Each step names the script | YES (step 2, 6, 8) | YES | — |
| Each step names the artifact | YES (SPEC, PLAN, TASKS, tasks/) | YES | — |
| Mode overlays | YES (vibe / mvp / production) | PARTIAL | The overlays touch 3 of 8 modes.yaml knobs (architecture, plan_review, task_size via "coarse" / "all"). The other 5 (spec, build_review, test_depth, docs, promotable) are not consulted. |
| Output shape | YES | YES | — |
| Handoff | "Hand to Build Lead with feature id and mode" | YES | — |
| Status discipline (`[ ]` / `[~]` / `[x]` / `[!]`) | NO | NO | Old ASPS encoded this in ASCII; current does not |
| Trace events | NO | NO | Old ASPS named required trace events (`phase_start`, `phase_end`, `handoff`); current does not |
| Failure / blocked | NO | NO | No "what to do if a step fails" — old ASPS had a status transition rule |
| Plan-of-plan recording | "state the plan-of-plan in one or two lines" (step 1) | NO template | No `PLAN_OF_PLAN.md` to write to |
| Clarification log | "record answers in the SPEC's Clarifications" (step 3) | NO template | No `CLARIFICATION_LOG.md` |
| Research handoff | "send genuine unknowns to the Research Lead" (step 3) | NO template | No `RESEARCH_REQUEST.md` |
| Constitution gate | "gate-check vs architecture constitution" (step 5) | NO script | No `constitution_check.py` |
| Plan-critic invocation | "skill `review-strategy` + the `plan-critic` workflow" (step 7) | SKILL NOT IN ALLOW-LIST | See §1.2 |
| prereq-validate invocation | "run `python .aspis/scripts/planning/prereq_validate.py --phase build`" (step 8) | SCRIPT NOT IN `.aspis/scripts/planning/` | See §2.1 |
| Severity vocabularies | NO | NO | Review template has CRITICAL/HIGH/MEDIUM/LOW; plan workflow does not — but plan-critic is the right place |

**Verdict on plan.md:** shape is right; depth is lean; 4 explicit gaps (plan-of-plan record, clarification log, research request form, constitution script). Plus the two allow-list / deployment gaps.

### 5.3 Per-mode workflow variants

`plan.md` has 3 mode overlays in a single 4-line section. The OLD ASPS had mode-specific procedures (`P0..P9` with mode gating in each step). The current shape is workable.

| Missing variant | Why | Priority |
|---|---|---|
| `plan.vibe.md` | "1-paragraph plan, no PLAN.md, no review, coarse tasks" | LOW (the overlay covers it) |
| `plan.mvp.md` | "Light architecture, self-check review, medium tasks" | LOW |
| `plan.production.md` | "Full SPEC/PLAN/TASKS, independent review, small tasks" | LOW |
| `plan.small-task.md` | One-task trivial plan, skip most steps | LOW (small-task.md exists for the build side; planning-side equivalent does not) |

The single plan.md + overlays is fine for now. The audit's "Workflow doc depth" is a polish concern, not a blocker.

### 5.4 What steps are missing from `plan.md`?

| Missing step | What it would do | Why |
|---|---|---|
| Step 0.5 — **Scope estimate** | Run `scope_estimate.py` (or use the model) to get a numeric score; record in `SCOPE_ESTIMATE.md` | Today classification is purely model judgment |
| Step 1.5 — **Mode decision record** | After picking a mode, write the rationale to `MODE_DECISION.md` | Today the mode is decided but the rationale is not durable |
| Step 3.5 — **Clarification log commit** | After clarifying, write a `CLARIFICATION_LOG.md` entry; gate the rest of the plan on `[NEEDS CLARIFICATION]` count = 0 in production | Today the log is informal |
| Step 3.6 — **Research request commit** | If research is needed, write a `RESEARCH_REQUEST.md` and hand to research-lead | Today the request is free-form |
| Step 5.5 — **Constitution check** | Run `constitution_check.py` against PLAN.md; require 0 FAIL | Today the constitution is read, not checked |
| Step 6.5 — **Dependency graph** | Run `dependency_graph.py`; require 0 cycles and `[P]` correctness | Today the graph is hand-written |
| Step 6.6 — **Task-size check** | Run `task_size_check.py`; require all tasks within the mode's `task_size` knob | Today the granularity is judgment |
| Step 7.5 — **Plan quality check** | Run `plan_quality_check.py`; require 0 FAIL | Today the plan-critic is a skill, not a script |
| Step 7.6 — **Handoff packet** | Generate a `HANDOFF.md` summarizing what's ready for build-lead | Today the handoff is one sentence |

---

## 6 · What's missing — comprehensive gap analysis

### 6.1 Skills in catalog but not in planning-lead's allow-list (top priority)

| # | Skill | Why | Fix |
|---|---|---|---|
| G1 | `plan-critic` | `plan.md` step 7 explicitly names it; **allow-list denies it** | Add to `permission.skill` in `.opencode/agents/planning-lead.md` |
| G2 | `review-strategy` | `plan.md` step 7 explicitly names it; **allow-list denies it** | Add to `permission.skill` |
| G3 | `deterministic-first` | The deterministic-first ladder (script → tool → workflow → agent) is the design pattern; planning should consult it for P0/P3 | Add to `permission.skill` |
| G4 | `scope-control` | Planning designs the allowed/forbidden files for each packet | Add to `permission.skill` |
| G5 | `context-packaging` | Optional — for receiving context-packets from project-lead | Optional |

### 6.2 Scripts referenced but not deployed to `.aspis/scripts/planning/`

| # | Script | Where it exists | Where it's referenced | Fix |
|---|---|---|---|---|
| D1 | `feature_scaffold.py` | `src/aspis/data/catalog/scripts/planning/` | `plan.md` step 2; planning-lead's bash allow-list; agent body | **Add to `aspis init` export** (copy 5 planning scripts into `.aspis/scripts/planning/`) |
| D2 | `task_compile.py` | catalog | `plan.md` step 6; planning-lead body | Same fix |
| D3 | `prereq_validate.py` | catalog | `plan.md` step 8; planning-lead body | Same fix |
| D4 | `active_feature.py` | catalog | (used internally by scaffold + validate) | Same fix |
| D5 | `_console.py` | catalog | (helper, used by 1-4) | Same fix |

**The export gap is in the renderer** — the `init` operation's `export.py` only copies `context/`, `git/`, `hooks/` to `.aspis/scripts/`, not `planning/`. This is the single most operationally important gap.

### 6.3 Validation checks not automated

| # | Check | What it would do | Where in workflow | Status |
|---|---|---|---|---|
| V1 | Scope estimate | Numeric score from a request | P0 | Missing — `scope_estimate.py` |
| V2 | Mode coherence | Check chosen mode's knobs are consistent | P0 | Missing — `mode_validator.py` |
| V3 | Clarification count | Lint `[NEEDS CLARIFICATION]` markers; gate production | P1 | Missing |
| V4 | Plan-quality | Lint SPEC/PLAN/TASKS shape (FR-SC traceability, phase order, etc.) | P2, P4, P5 | Missing — `plan_quality_check.py` |
| V5 | Constitution check | Run 11 constitution checks against the plan | P3 | Missing — `constitution_check.py` |
| V6 | Task size | Validate each task is within mode's `task_size` knob | P4 | Missing — `task_size_check.py` |
| V7 | Dependency graph | Validate no cycles; `[P]` tasks touch different files | P4, P5 | Missing — `dependency_graph.py` |
| V8 | Plan-critic | The light script that does what `plan-critic` skill does, in code | P5 | Missing — `plan_critic.py` (or upgrade the skill to call a script) |
| V9 | prereq-validate | Phase-order gate | Final | EXISTS in catalog, NOT in `.aspis/scripts/` (see D3) |

### 6.4 Templates not created

See §4.2. Top 5:
- T1 `CLARIFICATION_LOG.md` (HIGH)
- T2 `RESEARCH_REQUEST.md` (HIGH)
- T3 `PLAN_OF_PLAN.md` (MEDIUM)
- T4 `DEPENDENCIES.md` (MEDIUM)
- T5 `SCOPE_ESTIMATE.md` (MEDIUM)

### 6.5 Workflow steps not documented

See §5.4. Top 4:
- Step 0.5 scope estimate
- Step 3.5 clarification log commit
- Step 5.5 constitution check
- Step 7.5 plan quality check

### 6.6 Summary scorecard — what planning-lead has vs what it needs

| Dimension | Current | Needed | Gap |
|---|---|---|---|
| Skills in allow-list | 7 | 11 (add plan-critic, review-strategy, deterministic-first, scope-control) | +4 (2 critical, 2 optional) |
| Skills in catalog but not in agent's domain (out-of-scope) | 31 | unchanged | none |
| Scripts in allow-list | 0 (the path is broken) | 4 (scaffold, compile, prereq, active_feature) | DEPLOY — copy to `.aspis/scripts/planning/` |
| Scripts in catalog but not deployed | 5 (all of planning/) | 0 | DEPLOY — see D1-D5 |
| Validation gates automated | 1 of 9 (prereq-validate only) | 9 | +8 (plan_quality, constitution, scope_estimate, mode_validator, task_size, dependency_graph, clarification_count, plan_critic) |
| Templates | 5 in planning/ | 10+ in planning/ | +5 (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE) |
| Workflow steps | 8 | 12-13 | +4-5 (scope, clarification, constitution, plan-quality, handoff) |
| Per-mode workflow variants | 1 (overlays) | 4 (per mode) | optional, LOW |
| Bash allow-list commands | 11 | 13-15 | +2-4 (aspis mode, constitution_check.py, plan_quality_check.py) |
| Mode knobs consulted by workflow | 3 of 8 | 8 of 8 | +5 (spec, task_size, build_review, test_depth, docs) |

---

## 7 · Top 10 priority items (for F-016 to act on)

Sorted by leverage (impact × frequency of use × fix cost).

1. **DEPLOY the 5 planning scripts to `.aspis/scripts/planning/`.** Fix the renderer (or fix the planning-lead's bash allow-list to point at the catalog). **Today the plan workflow cannot be executed.** Single highest-priority item.
2. **Add `plan-critic` and `review-strategy` to the planning-lead allow-list.** The workflow names them; the allow-list denies them. Two-line fix in `.opencode/agents/planning-lead.md`.
3. **Add `deterministic-first` and `scope-control` to the planning-lead allow-list.** These are the design patterns planning should consult at P0 and P4.
4. **Write `CLARIFICATION_LOG.md` and `RESEARCH_REQUEST.md` templates.** The workflow says "record answers" and "send genuine unknowns"; no forms exist. Pair with a `clarification_log.py` script.
5. **Write `plan_quality_check.py` and call it from P2 / P4 / P5.** The audit's CHK001–CHK013 has 13 items; the script can lint SPEC/PLAN/TASKS for shape, FR-SC traceability, and phase order. Today the plan-critic skill is the only check, and it's light.
6. **Write `constitution_check.py` and call it from P3.** The 11 checks in `constitution-checks.yaml` are read but not executed. A text-pattern / structural check closes the loop.
7. **Write `scope_estimate.py` and `mode_validator.py` and call them from P0.** Replaces the "you may infer" prose with a deterministic decision (or a documented rubric).
8. **Write `task_size_check.py` and `dependency_graph.py` and call them from P4 / P5.** The mode's `task_size` knob is read; no check that the tasks obey it. The `[P]` markers are hand-written; no check that they're correct.
9. **Add `PLAN_OF_PLAN.md`, `SCOPE_ESTIMATE.md`, `MODE_DECISION.md`, `DEPENDENCIES.md` templates.** Small (50-100 lines each) but they make every step of the workflow durably recorded. Today most of P0 is chat-only.
10. **Upgrade `plan.md` from 52 to ~120 lines.** Add the 5 missing steps (scope, clarification log, constitution, plan quality, handoff), the 5 missing mode-knob consults, the status discipline, and the severity vocabularies. Old ASPS's PLANNING_WORKFLOW.md was 200+ lines for a reason.

---

## Provenance & version

- **Sources verified:** live tree at `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS` on 2026-06-26.
- **Catalog:** 38 skills, 12 agents, 10 templates, 6 workflows, 11 config files, 23 catalog scripts (per `current-aspis-audit-1.md`).
- **Deployed:** 19-20 skills to `.opencode/skills/` and `.claude/skills/`, 10 agents, 10 templates, 5 workflows (no bootstrap.md in live), 23 catalog scripts **except** the 5 in `planning/`.
- **Plan workflow step count:** 8 (P0 intake → P1 clarify → P2 spec → P3 architecture → P4 tasks → P5 plan-critic → final prereq-validate).
- **Mode knobs in `modes.yaml`:** 8 per mode (`spec`, `architecture`, `task_size`, `plan_review`, `build_review`, `test_depth`, `docs`, `promotable`).
- **Constitution checks:** 11 in `constitution-checks.yaml`.
- **This inventory:** valid as of 2026-06-26; re-verify after any change to `plan.md`, `planning-lead.md`, the export renderer, or `modes.yaml`.

---

*End of inventory. Companion files in F-016/Research/: `current-aspis-audit-1.md`
(the source audit), `old-asps-workflows-scripts-2.md` (the OLD ASPS comparison),
`system-agent-tooling.md` (external patterns). For the planning-lead's day-to-day,
this inventory + the 5 workflow files + the 7 allow-listed skills is the working
set. The top 10 in §7 are the changes that close the largest gaps.*
