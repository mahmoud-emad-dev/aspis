# F-016 Research — Planning Lead Subagent and Delegation System Design

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Phase:** plan (design input)
> **Compiled:** 2026-06-26
> **Author:** research-lead
> **Status:** validated design (consumed by system-lead for catalog edit + planning-lead for task allow-list)
> **Scope:** the complete subagent and delegation design for the planning-lead — existing delegates, new subagents, phase-by-phase flow, definition surface, and cost-aware routing.
> **Audience:** system-lead (catalog/live edit), planning-lead (task allow-list + workflow), reviewer (plan-critic cross-check).

---

## 0 · TL;DR (one paragraph)

The planning-lead is an **orchestrator with a 6-step planning lifecycle** (intake → context → clarify → spec → architecture → tasks). It already has 4 delegates in the live task allow-list — `research-lead` (knowledge), `reviewer` (plan-critic), `project-explorer` (codebase lookup), and a stray `committer` (drift, should be removed). It needs **8 more subagents** to do its work efficiently: `clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `scope-estimator`, `constitution-checker`, `dependency-analyzer`, `research-request-writer`. Of those, 3 are immediate (the trio called out in `local/agents/planning-lead.md` §Subagents + the old ASPS gap `prd-writer`), 3 are near-term as multi-feature planning becomes normal, 2 are defensive (constitution-checker is high-leverage, research-request-writer is cheap insurance). The cost shape is 60% cheap / 30% standard / 10% deep — different from build-lead (which is more deep-heavy) because planning is more parsing + classification than synthesis. Subagent definition is a thin YAML frontmatter over the same `CatalogAgent` shape already used by all 12 agents; the catalog at `src/aspis/data/catalog/agents/` is the single source of truth, the live at `.opencode/agents/` is generated. The planning-lead discovers its subagents the same way it already does: via the static task allow-list in its frontmatter.

---

## 1 · Existing delegates — audit and recommendations

The planning-lead's live task allow-list (`.opencode/agents/planning-lead.md` lines 26–31) currently reads:

```yaml
task:
  '*': deny
  research-lead: allow
  reviewer: allow
  project-explorer: allow
  committer: allow      # ← DRIFT — remove
```

### 1.1 `research-lead` — **keep, refine trigger**

- **When to delegate:** the planning-lead encounters a real unknown about current docs, APIs, frameworks, libraries, or external services that **cannot** be settled from the project itself. Examples: "is the OpenCode Agent tool's task-allow-list still mandatory in 2026.06?", "what's the current recommended way to package Python CLIs cross-platform?".
- **When NOT to delegate:** anything resolvable from `.aspis/context/`, `FILE_REGISTRY.yaml`, `CODE_MAP.md`, the project rules, or the architecture constitution. The `requirement-clarification` skill is explicit: "If a real unknown needs external docs or facts, request it from the Research Lead; don't research it yourself."
- **How to delegate:** a structured **research request packet** (see §2.8 `research-request-writer` — this is the *form* the planning-lead uses; the *destination* is the research-lead). The packet is a message; the research-lead is invoked via the `task` tool with the packet.
- **Tier:** the research-lead's own frontmatter says `model: deep` (catalog) / `opencode-go/deepseek-v4-pro` (live). For trivial lookups ("does this library exist?") it could be demoted to standard; the planning-lead cannot demote it but can mark the packet as `urgency: low` to signal the research-lead to use its cheap subagent `web-researcher` (`docs-fetcher`).

### 1.2 `reviewer` — **keep, narrow trigger**

- **When to delegate:** the plan-critic step in P6 of `workflows/plan.md`. Per `modes.yaml`:
  - **production mode** → `plan_review: independent` → delegate to reviewer (with the `plan-critic` skill as the procedure).
  - **mvp mode** → `plan_review: self` → planning-lead does a self-check using the `plan-critic` skill *without* delegating.
  - **vibe mode** → `plan_review: skip` → no delegate, no self-check.
- **How to delegate:** the full feature folder (`SPEC.md`, `PLAN.md`, `TASKS.md`, `ACCEPTANCE.md`) plus the `plan-critic` skill instruction. The reviewer returns a `REVIEW_REPORT` with a verdict (approved / approved-with-notes / changes-requested) and a findings list.
- **Tier:** reviewer is `deep` per `capabilities.yaml` (`review: preferred_tier: deep`). Correct — plan-critic is judgment-heavy.
- **Anti-pattern:** delegating the reviewer for *progress* questions ("how's it going?") — review is for completed work, not for in-flight planning. The planning-lead's self-check handles the in-flight case.

### 1.3 `project-explorer` — **keep, broaden trigger**

- **When to delegate:**
  - Phase 1 (intake): "what features already exist in `.aspis/features/` that touch this area?" → delegate the directory scan.
  - Phase 2 (context): "where is X implemented? which files import Y?" → delegate structural lookup.
  - Phase 3 (clarify): "is there a convention in the project for this kind of work?" → delegate convention lookup.
  - Phase 4 (spec): "what does the existing similar feature look like, end to end?" → delegate the pattern lookup.
  - Phase 5 (architecture): "what existing files does this change touch?" → delegate the impact scan (good input to scope-estimator).
- **When NOT to delegate:** reading a specific file the planning-lead already knows about (`read` directly). Reading the L1 hot context (`CURRENT_STATE.md`, `RECENT_CHANGES.md`, `active_feature.json`) — these are the planning-lead's hot reads, not the explorer's job.
- **Tier:** `cheap` per `capabilities.yaml` (`exploration: preferred_tier: cheap`). Correct.
- **Note:** the explorer is a *leaf* worker (no delegates). The planning-lead cannot fan out from it; one question = one invocation.

### 1.4 `committer` — **REMOVE (drift)**

- **Why it exists in live:** the `current-aspis-agents-2.md` research flagged this as the same drift shape as the project-lead's stray committer delegate. The planning-lead "produces templates, not code; doesn't commit." (catalog's task list is the correct one, without `committer`.)
- **Action:** remove `committer: allow` from `.opencode/agents/planning-lead.md` frontmatter, restore catalog parity, and re-run `aspis models --apply` (or a more targeted regeneration command) to keep the live file in sync.
- **Why this is safe:** the planning-lead has `git commit*: deny` in its bash permissions and no path through its workflow that would benefit from invoking the committer. The committer is for the build lead's "hand-off reviewed, gate-green work" handoff, not the planning lead's "hand off the approved plan" handoff. The build-lead invokes the committer at the end of the build, not the planning-lead at the end of the plan.

### 1.5 Summary of existing delegation edges

| From | To | Trigger | Tier | Direction |
|---|---|---|---|---|
| planning-lead | research-lead | Real external unknown | deep (own) → standard for trivial | down-stream |
| planning-lead | reviewer | Plan-critic in production mode | deep | side-ways (independent) |
| planning-lead | project-explorer | Codebase lookup | cheap | down-stream |
| planning-lead | committer | **REMOVE — drift** | n/a | n/a |

---

## 2 · New subagents — the 8 planning workers

Each subagent below follows the **canonical ASPIS subagent shape** (per §5): thin frontmatter, narrow role, fresh context, single packet handoff, single return. They are **all `mode: subagent`** (R-004 / D-004: only project-lead + 4 promoted are primary). They differ in tier and tools by job.

### 2.1 `clarify` — L3 subagent, 10-category ambiguity scan

| Field | Value |
|---|---|
| **Name** | `clarify` |
| **Purpose** | Run a structured 10-category ambiguity scan on a SPEC or raw request, surface the few questions that genuinely block planning, return prioritized clarification questions (max 5). |
| **Mode** | subagent |
| **Tier** | cheap (`exploration: preferred_tier: cheap` per `capabilities.yaml`) — this is classification work |
| **Tools** | `read`, `grep`, `glob`; bash limited to `python .aspis/scripts/context/*` |
| **Skills** | `requirement-clarification`, `clarify-routing` (proposed), `asps-trace-discipline` |
| **When invoked** | After `planning-intake` and after `prd-writer` produces a first SPEC draft. Specifically in the "vague request" or "thin SPEC" cases. |
| **Input packet** | `{ request, draft_spec?, conventions_yaml, max_questions: 5, taxonomy: 10-category }` |
| **Output** | `CLARIFICATION_REPORT.md`: resolved assumptions (3–8), open questions (1–5) ordered by impact × uncertainty, each with a recommended default. |
| **Cost** | cheap; runs once per plan |
| **Priority** | **immediate** — already referenced in `local/agents/planning-lead.md` §Subagents and in the old ASPS P1b phase |
| **Replaces** | the *current* `requirement-clarification` skill, which the planning-lead runs in-context. The skill stays; the subagent is the *implementation* for non-trivial clarifications. |
| **Evidence (old ASPS)** | "10-category ambiguity scan + max-5 prioritized questions (via `clarify`)" — P1b of the old ASPS planning workflow; taxonomy "harvested from Spec Kit clarify.md (MIT). D-008." |

**Why extract as subagent vs keep as skill:**
- Benefits from **fresh context** — the planning-lead's context is already heavy with project state; spinning out the ambiguity scan gives a clean window to think.
- Different **tier profile** — cheap model is sufficient (it's classification + pattern matching against the 10 categories); keeping it in-context means the planning-lead's deep model is wasted on it.
- **Parallelizable** in principle (multiple `clarify` subagents on different parts of a multi-area spec), though in practice usually serial.
- The decision rule from `local/agents/planning-lead.md`: "extract as subagents only when parallelism is needed." The deciding factor here is **fresh context + cheaper tier** more than parallelism.

**10-category taxonomy (the inherited Spec Kit shape, MIT-licensed per D-008):**
1. Language and terminology (what does "user" mean here?)
2. Actors and roles (who triggers; who consumes?)
3. Triggers and timing (when does it fire?)
4. Inputs (what data; what format; what source?)
5. Outputs (what artifact; where; to whom?)
6. Side effects (state changes; notifications; logs?)
7. Acceptance criteria (how is "done" measured?)
8. Scope and boundaries (what is deliberately NOT done?)
9. Dependencies (which existing things does it rely on?)
10. Error and edge cases (what fails; how is it handled?)

**Output contract (sketch):**

```markdown
# CLARIFICATION_REPORT — <feature-id>

## Resolved (from project conventions)
- <item> → <resolution> (source: <convention>)

## Open questions (max 5, ordered by impact × uncertainty)
1. **[CRITICAL]** <question> — Recommended default: <answer>. — Why it blocks: <reason>.
2. **[IMPORTANT]** <question> — ...
3. **[IMPORTANT]** <question> — ...
4. **[OPTIONAL]** <question> — ...

## Notes for the planning-lead
- <anything the planner should carry forward>.
```

### 2.2 `task-decomposer` — L3 subagent, PLAN → ordered TASKS

| Field | Value |
|---|---|
| **Name** | `task-decomposer` |
| **Purpose** | Take an approved `PLAN.md` (and `SPEC.md` for traceability) and produce a sequenced, dependency-ordered `TASKS.md` with phase markers, `[P]` (parallel) and `[US1]` (user story) tags, and exact file paths. Then invoke `task_compile.py` to emit per-task packets. |
| **Mode** | subagent |
| **Tier** | standard (`orchestration: preferred_tier: deep` but this is *decomposition* not synthesis — standard is sufficient and matches the old ASPS's choice of `model: standard`) |
| **Tools** | `read`, `grep`, `glob`, `write`, `edit`; bash limited to `python .aspis/scripts/planning/task_compile.py` and `python .aspis/scripts/planning/prereq_validate.py` |
| **Skills** | `task-decomposition`, `task-format`, `spec-to-plan`, `scope-control`, `asps-trace-discipline` |
| **When invoked** | Phase 6 of `workflows/plan.md`, after the architecture is approved, as the final planning step. |
| **Input packet** | `{ spec_path, plan_path, mode, task_size, story_count, parallelism_budget }` |
| **Output** | `TASKS.md` (matching `.aspis/templates/planning/TASKS.md`) + per-task `tasks/T-NN.md` packets (matching `.aspis/templates/planning/TASK_PACKET.md`). |
| **Cost** | standard; runs once per plan; one of the higher-token planning subagents |
| **Priority** | **immediate** — already referenced in `local/agents/planning-lead.md` §Subagents and the old ASPS P7 |
| **Replaces** | the `task-decomposition` skill (which stays); the subagent is the *executor* for non-trivial decompositions |

**Why extract:**
- The current `task-decomposition` skill is 41 lines (read above) — it tells the *agent* how to decompose. The subagent *does* the decomposition in fresh context, leaving the planning-lead's context free to read the result.
- It's a **synthesis-heavy** task; the subagent can read the whole SPEC + PLAN + code map in its own window without polluting the planning-lead's.
- **Output is large** — a 30-task TASKS.md + 30 packets = a lot of tokens; offloading keeps the planning-lead's context clean for the handoff conversation.

**Output contract:** the `TASKS.md` shape from the template (Setup → Foundational → US1 (P1) → US2 (P2) → Polish) plus the per-task `tasks/T-NN.md` packets (Identity / Context / Scope / Steps / Skeleton / Dependencies / Outputs / Acceptance / Tests / Review routing / Verify / On failure).

**Permission note:** `write` and `edit` allowed for `.aspis/features/F-NNN-*/TASKS.md` and `tasks/T-NN.md` only; `bash` limited to the two planning scripts.

### 2.3 `idea-capture` — L3 subagent, raw idea → P0 intake

| Field | Value |
|---|---|
| **Name** | `idea-capture` |
| **Purpose** | Take a raw user idea (often one sentence, often vague) and structure it into the P0 intake shape — goal, problem, value, constraints, rough scope, initial risks, a sensible mode. |
| **Mode** | subagent |
| **Tier** | cheap (`documentation: preferred_tier: cheap` — this is *parsing* + *structuring*, not synthesis) |
| **Tools** | `read`, `write`; no bash |
| **Skills** | `spec-to-plan`, `scope-control`, `planning-intake` |
| **When invoked** | Phase 1 (intake) of `workflows/plan.md` when the user request is **vague or one-sentence**. For well-formed requests the planning-lead does intake itself. |
| **Input packet** | `{ raw_request, project_yaml, modes_yaml }` |
| **Output** | `INTAKE.md` with the goal/problem/value/constraints/scope/risks/mode shape, written into `.aspis/features/F-NNN-slug/INTAKE.md` (or held in memory for the planning-lead to write the SPEC's Goal/Problem sections). |
| **Cost** | cheap; one of the smallest subagents |
| **Priority** | **immediate** — already referenced in `local/agents/planning-lead.md` §Subagents; matches the old ASPS P0 |

**Why extract:**
- The cheapest possible subagent; the planning-lead's deep model is overkill for "turn this sentence into a structured intake."
- The output is a small, structured document — easy to validate, easy for the planning-lead to consume in one read.

**When NOT to invoke:** if the user request is already structured ("add a `rate_limit` middleware to the FastAPI app, max 100 req/min per user") the planning-lead does intake directly. `idea-capture` is for the *opaque* end of the request spectrum.

### 2.4 `prd-writer` — L3 subagent, clarified requirements → full SPEC

| Field | Value |
|---|---|
| **Name** | `prd-writer` |
| **Purpose** | Take clarified requirements (post-`clarify`) and produce a full `SPEC.md` per the template — Goal, Problem, Scope, User stories (P1/P2), FR-###, SC-###, Feature rules, Key entities, Success criteria, Assumptions, Clarifications. |
| **Mode** | subagent |
| **Tier** | standard (this is *spec synthesis* — a real authoring task; standard matches the old ASPS's `model: standard` choice) |
| **Tools** | `read`, `grep`, `write`, `edit`; no bash |
| **Skills** | `feature-planning`, `spec-quality`, `spec-to-plan` |
| **When invoked** | Phase 4 of `workflows/plan.md` (Spec), after `clarify` has resolved the open questions. |
| **Input packet** | `{ intake_md, clarifications, spec_template, mode, story_count_target: 1-3 }` |
| **Output** | `SPEC.md` matching `.aspis/templates/planning/SPEC.md` (or its vibe/mvp-compressed variants per `modes.yaml`) |
| **Cost** | standard; runs once per plan |
| **Priority** | **immediate — this is the documented F-027 gap from the old ASPS** ("The `prd-writer` agent referenced in `PLANNING_WORKFLOW.md` P1 is **missing** — F-027, designed not built, noted as a real gap.") |
| **Replaces** | the *current* `feature-planning` skill when the SPEC is non-trivial. The skill stays; the subagent is the *writer*. |

**Why extract:**
- This is the **largest single planning artifact** (the SPEC is the spine of the plan). Writing it in fresh context prevents the planning-lead's context from being consumed by the synthesis.
- The SPEC is a **structured output** from a template — the work is "fill in this template thoughtfully" not "decide what's important." Standard tier is correct.
- The planning-lead **owns the SPEC** but doesn't have to **write every word** of it — the same orchestrator-worker pattern the build-lead uses with `general-builder`.
- **F-027 is an old known gap** — this subagent closes it cleanly.

**Output contract:** the SPEC template shape, with every required section populated; numbered `FR-###` and `SC-###`; user stories with priority and acceptance scenarios.

**Permission note:** `write` and `edit` allowed for `.aspis/features/F-NNN-*/SPEC.md` only. The planning-lead can read the file; the subagent writes the first draft.

### 2.5 `scope-estimator` — L3 subagent, SPEC → size + risk estimate

| Field | Value |
|---|---|
| **Name** | `scope-estimator` |
| **Purpose** | Take a SPEC (or intake) and produce a **first-pass size and risk estimate** — file count, complexity tier (small/medium/large), risk level (low/medium/high), Cost-of-Change reading (1-3 / 5-10 / 10+), and a recommended mode. Used by `planning-intake` to pick a mode *and* by the planning-lead to sanity-check the task-decomposer's output. |
| **Mode** | subagent |
| **Tier** | cheap (classification + count + lookup) |
| **Tools** | `read`, `grep`, `glob`; bash limited to `python .aspis/scripts/context/*` |
| **Skills** | `codebase-mapping`, `asps-context-navigation`, `scope-control` |
| **When invoked** | Phase 1 (intake) — to size the work and pick a mode — and Phase 6 (tasks) — to cross-check the decomposition. |
| **Input packet** | `{ spec_path?, intake_path?, active_feature, cost_of_change_test: true }` |
| **Output** | `SCOPE_ESTIMATE.md` with: `files_estimated: NN`, `files_actually_touched: predicted`, `complexity: small|medium|large`, `risk: low|medium|high`, `cost_of_change: 1-3|5-10|10+`, `recommended_mode: vibe|mvp|production`, `warnings: [...]`. |
| **Cost** | cheap; runs once or twice per plan |
| **Priority** | **near-term** — not blocking; the planning-lead can do this with `context-ladder` today. Extract when multi-feature planning becomes normal. |

**Why extract (near-term, not immediate):**
- The work is **classification + counting** — a perfect cheap-model job.
- It benefits from **fresh context** so the planning-lead's read of the spec isn't mixed with the size judgment.
- The current `planning-intake` skill asks the planning-lead to do this estimation *itself* — moving it to a subagent is a clean separation: the planning-lead *decides*; the scope-estimator *measures*.

**When NOT to invoke:** for vibe mode, the planning-lead skips ceremony and the estimate is "1 task, low risk." The subagent is for mvp and production modes.

### 2.6 `constitution-checker` — L3 subagent, PLAN vs 12 constitution rules

| Field | Value |
|---|---|
| **Name** | `constitution-checker` |
| **Purpose** | Take a `PLAN.md` and check it against the 12 architecture-constitution rules (the 11 currently in `constitution-checks.yaml` plus the local-change extension rule from `architecture-constitution.md`). Return a structured finding list. |
| **Mode** | subagent |
| **Tier** | standard (judgment work — `review: preferred_tier: deep`, but this is a *narrow* review against a fixed checklist, so standard is sufficient) |
| **Tools** | `read`, `grep`, `glob`; no bash, no write |
| **Skills** | `plan-critic`, `architecture-review`, `scope-audit`, `constitution-checks` (proposed) |
| **When invoked** | Phase 5 (architecture) of `workflows/plan.md`, after the PLAN is drafted, before plan-critic. |
| **Input packet** | `{ plan_path, spec_path, constitution_rules: [list of 12], current_architecture }` |
| **Output** | `CONSTITUTION_CHECK.md` with one row per rule: `rule_id`, `verdict: pass|warn|fail`, `evidence: <file:line or quote>`, `suggested_fix: <text>`. |
| **Cost** | standard; runs once per plan |
| **Priority** | **near-term (high-leverage)** — not blocking, but the current `architecture-planning` skill asks the planning-lead to do this check in its own context, which mixes "design the architecture" with "audit the architecture." Separating them improves both. |

**Why extract (and why high-leverage):**
- The constitution is **the spine of how the project grows** (12 rules, listed in `architecture-constitution.md`). A failed constitution check at the planning stage is a 5-minute fix; a failed check at the build stage is a 5-hour refactor.
- The work is **mechanical against a fixed list** — exactly what a subagent (and a future deterministic script) is good at. The 12 rules could be encoded as a deterministic checker *eventually*; for now, the subagent is the LLM-based implementation.
- **No edit/write** — the checker is read-only. The planning-lead applies any fixes.
- **Different from reviewer** — the reviewer does plan-critic (cross-artifact consistency, SC traceability, testability); the constitution-checker is a *single-lens* deep check on architecture rules. The reviewer runs after; the constitution-checker runs during.

**The 12 rules** (extending `constitution-checks.yaml`'s 11 by adding the explicit `local-change` rule from `architecture-constitution.md` §Extension rules):
1. C-COST — Cost of change (1-3 healthy, 10+ problem)
2. C-AUTOMATION — R-003 deterministic-first
3. C-LOCAL-CHANGE — add by creating files, not editing many
4. C-PLUGIN-FIRST — core never names a concrete implementation
5. C-SINGLE-SOURCE — every fact owned once
6. C-CONFIG-OVER-CODE — data, not `if` chains
7. C-NO-SPECIAL-CASE — no `if runtime == "x"`
8. C-DISCOVERY — load by convention, not registry
9. C-FILE-SELF-EXPLAINS — every file has Purpose / Responsibilities / Does Not / Used By
10. C-TESTABLE — every component testable in isolation (R-005)
11. C-PORTABLE — Windows + Linux, UTF-8, pathlib
12. C-ARCH-BEFORE-FEATURES — extension mechanism first, then features

### 2.7 `dependency-analyzer` — L3 subagent, multi-feature PLAN → dependency graph

| Field | Value |
|---|---|
| **Name** | `dependency-analyzer` |
| **Purpose** | Take a multi-feature PLAN (multiple `F-NNN` features) and produce a dependency graph: which features depend on which, the critical path, the parallel execution groups, and any circular dependencies. |
| **Mode** | subagent |
| **Tier** | cheap (this is graph extraction + topological sort — cheap tier handles it; could even be a deterministic script eventually) |
| **Tools** | `read`, `grep`, `glob`, `write`; bash limited to `python .aspis/scripts/planning/dependency_graph.py` (future) |
| **Skills** | `dependency-audit`, `codebase-mapping`, `asps-context-navigation` |
| **When invoked** | **Rarely** — when a plan spans more than one feature (e.g. a project-level plan or a feature that has been decomposed into multiple `F-NNN`s). Not invoked for single-feature plans. |
| **Input packet** | `{ feature_ids: [...], plan_paths: [...], existing_features }` |
| **Output** | `DEPENDENCY_GRAPH.md` with: adjacency list, critical path, parallel groups, cycles (if any), suggested execution order. |
| **Cost** | cheap; runs once per multi-feature plan |
| **Priority** | **future** — extract when multi-feature planning becomes normal (today, the planning-lead handles the rare case manually) |

**Why extract (future, not immediate):**
- The work is rare. A project-level plan is one per project at most; a multi-feature plan is one per quarter.
- When it *does* happen, the work is a focused analysis — fresh context helps.
- The output is a **structured graph** that could be deterministically computed (it's a DAG walk + topological sort); the subagent is the LLM-based prototype.

**When NOT to invoke:** single-feature plans. The `task-decomposer` already handles within-feature task ordering.

### 2.8 `research-request-writer` — L3 subagent, planning-lead's knowledge gap → research packet

| Field | Value |
|---|---|
| **Name** | `research-request-writer` |
| **Purpose** | Take the planning-lead's *raw* knowledge gap (a sentence or two of "I need to know X") and produce a **structured research request packet** for the research-lead. The packet is the *form* the planning-lead uses; this subagent produces the form. |
| **Mode** | subagent |
| **Tier** | cheap (parsing + structuring) |
| **Tools** | `read`, `write`; no bash |
| **Skills** | `knowledge-research` (input shape), `context-packaging` (output shape) |
| **When invoked** | Before every delegation to the `research-lead` (and before delegations to `research-request-writer` *that* go to research — a thin meta-layer, but valuable). The planning-lead may also write the packet itself; the subagent is the *insurance* that the packet is well-formed. |
| **Input packet** | `{ raw_question, what_a_good_answer_must_cover, sources_to_consult: [list], urgency: low|medium|high, mark_unverified: bool }` |
| **Output** | `RESEARCH_REQUEST.md` with: `question`, `must_cover`, `prefer_sources`, `version_constraints`, `urgency`, `format: "packaged reference (not raw dump)"`. |
| **Cost** | cheap; runs once per research delegation |
| **Priority** | **near-term (cheap insurance)** — adds a thin layer between the planning-lead and the research-lead. The cost is small; the value is "every research request is well-formed and includes the must-cover list the research-lead's `knowledge-research` skill says it needs." |

**Why extract (and why near-term):**
- The `knowledge-research` skill (read above) lists "Define the question. State precisely what's unknown and what a complete answer must cover" as step 1 — the planning-lead often skips this. The subagent is the *enforcement* of that step.
- **The pattern is exactly what the build-lead does with the task packet** — it enriches a task into a packet before delegating. The planning-lead should do the same with research. The subagent is the *enricher*.
- Cheap tier — the cost is trivial.

**Permission note:** `write` only, into `.aspis/features/F-NNN-*/Research/REQUESTS/<id>.md` (or a tmp file the planning-lead reads).

### 2.9 Summary — new subagents at a glance

| Name | Tier | Phase | Input | Output | Priority |
|---|---|---|---|---|---|
| `clarify` | cheap | 3 (clarify) | request, draft_spec, conventions, max_questions=5 | `CLARIFICATION_REPORT.md` (resolved + open) | immediate |
| `task-decomposer` | standard | 6 (tasks) | plan_path, mode, task_size | `TASKS.md` + `tasks/T-NN.md` packets | immediate |
| `idea-capture` | cheap | 1 (intake) | raw_request, modes_yaml | `INTAKE.md` (goal/problem/value/scope/risks/mode) | immediate |
| `prd-writer` | standard | 4 (spec) | clarifications, mode, spec_template | `SPEC.md` (template-shaped) | immediate (closes F-027) |
| `scope-estimator` | cheap | 1 + 6 (intake, tasks) | spec/intake, cost_of_change_test | `SCOPE_ESTIMATE.md` (files, complexity, risk, mode) | near-term |
| `constitution-checker` | standard | 5 (architecture) | plan_path, 12 rules | `CONSTITUTION_CHECK.md` (per-rule verdict) | near-term (high-leverage) |
| `dependency-analyzer` | cheap | rare (multi-feature) | feature_ids, plan_paths | `DEPENDENCY_GRAPH.md` (adjacency, critical path) | future |
| `research-request-writer` | cheap | before every research delegation | raw_question, must_cover, sources | `RESEARCH_REQUEST.md` | near-term (cheap insurance) |

**Cost shape for the 8 new subagents (per call):** 5 cheap + 2 standard + 0 deep + 1 cheap = **5 cheap, 3 standard** — the standard ones (`prd-writer`, `task-decomposer`, `constitution-checker`) are the synthesis work; the cheap ones are classification, parsing, and counting. The 10% deep tier is reserved for the planning-lead itself (which orchestrates) and for the reviewer (which plan-critics).

---

## 3 · Subagent vs skill — the decision rule and immediate-needs map

The rule from `local/agents/planning-lead.md` §Subagents: *"Specialized planning workers are extracted only when the work repeats enough to justify them."* The deeper rule, from the research and the production patterns (§3 of `production-loops-companies.md`): **extract as subagent when the work is parallelizable, benefits from fresh context, or needs a different model tier.**

| Need | Parallelizable? | Fresh context helps? | Different tier? | Decision |
|---|---|---|---|---|
| `clarify` | rarely | yes (clean ambiguity window) | yes (cheap) | **extract** |
| `task-decomposer` | no (single plan) | yes (large synthesis) | yes (standard, not deep) | **extract** |
| `idea-capture` | no | yes | yes (cheap) | **extract** |
| `prd-writer` | no | yes (large synthesis) | yes (standard, not deep) | **extract** (closes F-027) |
| `scope-estimator` | no | yes | yes (cheap) | **extract (near-term)** |
| `constitution-checker` | no | yes | no (standard) | **extract (near-term, high-leverage)** |
| `dependency-analyzer` | no | yes | yes (cheap) | **extract (future)** — not needed for single-feature plans |
| `research-request-writer` | no | no (just writes a packet) | yes (cheap) | **extract (near-term, cheap insurance)** |

**Immediate needs (3):** `clarify`, `task-decomposer`, `idea-capture` — already referenced in `local/agents/planning-lead.md` §Subagents and the old ASPS. Plus `prd-writer` (F-027 gap, **the most concrete known missing agent**).

**Near-term needs (3):** `scope-estimator`, `constitution-checker`, `research-request-writer` — add value today, are not blocking, but justify extraction.

**Future (1):** `dependency-analyzer` — only needed for multi-feature planning, which is rare today.

**Defensive note (1):** `prd-writer` and `constitution-checker` are the two highest-leverage extractions because they handle the **largest planning artifacts** (the SPEC and the architecture check) and currently force the planning-lead to do that work in its own context. The extraction is worth doing even when the parallelization argument is weak.

### Skills that stay (the 5 planning-lead skills)

The 5 existing skills the planning-lead runs *in its own context* — these do NOT become subagents:

- **`planning-intake`** — the planning-lead's classification + mode-pick is small enough (64 lines) to stay in-context. The *output* of intake (the scope-estimator's measurement) is what becomes a subagent.
- **`requirement-clarification`** — the *procedure* stays as a skill; the *executor* (`clarify`) is the subagent. The planning-lead reads the procedure; it delegates the work.
- **`feature-planning`** — the *procedure* stays; `prd-writer` is the *executor* for non-trivial SPECs. For trivial SPECs the planning-lead writes directly.
- **`architecture-planning`** — the *procedure* stays; `constitution-checker` is the *executor* for the audit step within the procedure. The planning-lead designs; the checker audits.
- **`task-decomposition`** — the *procedure* stays; `task-decomposer` is the *executor* for non-trivial decompositions. The planning-lead decides the shape; the decomposer fills it in.

This is the **skill/subagent split** the build-lead already uses: the build-lead has `task-orchestration` (procedure, in context) and delegates to `general-builder` (executor, fresh context). Same pattern, applied to planning.

---

## 4 · Delegation flow per planning phase

Mapping the 6 phases of `workflows/plan.md` to the subagent graph:

```
                    ┌────────────────────────────────────────────────────┐
                    │             project-lead (L1, primary)              │
                    │  delivers classified request + mode + context      │
                    └─────────────────────┬──────────────────────────────┘
                                          │ (delegate)
                                          ▼
                    ┌────────────────────────────────────────────────────┐
                    │           planning-lead (L2, primary)              │
                    │  orchestrator, holds the lifecycle, deep tier      │
                    └─────┬────────┬────────┬────────┬────────┬────────┬─┘
                          │        │        │        │        │        │
            ┌─────────────┘        │        │        │        │        │
            ▼                      ▼        ▼        ▼        ▼        ▼
   Phase 1: INTAKE         Phase 2-3:      Phase 4: Phase 5: Phase 6: Phase 7:
   - idea-capture          CONTEXT+CLARIFY  SPEC    ARCH     TASKS    PLAN-CRITIC
   - scope-estimator       - project-exp.  - prd-  - const- - task-  - reviewer
   - (planning-lead        - clarify         writer   checker  decom-  (independent
     does intake for       - research-                - research- poser  in production
     well-formed reqs)       request-                   request-         mode)
                            writer                      writer         (self in mvp,
                                                                       skip in vibe)
```

### Phase 1 — Intake (`planning-intake`)

- **Trigger:** the project-lead has classified the request and routed it to planning-lead with a mode hint (or no hint).
- **Subagents that fire:**
  - `idea-capture` (if the request is vague / one-sentence) — produces `INTAKE.md` with goal/problem/value/constraints/scope/risks/mode.
  - `scope-estimator` (always, in mvp/production modes) — produces `SCOPE_ESTIMATE.md` with files/complexity/risk/mode.
  - The planning-lead does `planning-intake` itself in-context for the final mode decision.
- **Tier mix:** cheap (both subagents), deep (planning-lead decision).
- **Sequencing:** `idea-capture` and `scope-estimator` can run in parallel (different files, no shared state); the planning-lead reads both before deciding the mode.

### Phase 2 — Context (`prestart-checks` + `context-ladder`)

- **Trigger:** mode decided; planning-lead needs project context.
- **Subagents that fire:**
  - `project-explorer` — for any L3 lookups (where is X? which files import Y?) the planning-lead doesn't already know from L1 hot context.
  - The planning-lead reads L1 hot state directly (`CURRENT_STATE.md`, `RECENT_CHANGES.md`, `active_feature.json`); `aspis context` if stale.
- **Tier mix:** cheap (project-explorer); deep (planning-lead).
- **Sequencing:** `project-explorer` runs first (provides the indexed view); planning-lead reads the explorer's compact summary in its own context.

### Phase 3 — Clarify (`requirement-clarification`)

- **Trigger:** the request still has open questions after phase 2.
- **Subagents that fire:**
  - `clarify` — runs the 10-category scan, returns `CLARIFICATION_REPORT.md` with resolved assumptions and max 5 prioritized questions.
  - `research-request-writer` — *if* the questions involve external knowledge the planning-lead can't resolve (e.g. "what's the current state of OAuth in this library?"), produces a `RESEARCH_REQUEST.md` packet that the planning-lead forwards to the `research-lead`.
  - `research-lead` (downstream) — receives the `RESEARCH_REQUEST.md` and returns a packaged reference.
- **Tier mix:** cheap (clarify, research-request-writer), deep (research-lead for non-trivial lookups).
- **Sequencing:** `clarify` first; if questions are external, `research-request-writer` then `research-lead`; then the planning-lead asks the user the final 1-3 questions.

### Phase 4 — Spec (`feature-planning`)

- **Trigger:** clarifications resolved (or accepted as assumptions).
- **Subagents that fire:**
  - `prd-writer` — produces `SPEC.md` from the template.
  - The planning-lead reviews and edits the SPEC; the subagent is the *drafter*, not the owner.
- **Tier mix:** standard (prd-writer), deep (planning-lead review).
- **Sequencing:** `prd-writer` runs first; planning-lead reads the draft in one read and edits/accepts.

### Phase 5 — Architecture (`architecture-planning`)

- **Trigger:** SPEC is settled.
- **Subagents that fire:**
  - `constitution-checker` — runs after the planning-lead drafts `PLAN.md`; produces `CONSTITUTION_CHECK.md` with per-rule verdicts.
  - `research-request-writer` (if any external knowledge is needed for the architecture, e.g. "what's the recommended pattern for this in 2026?") → `research-lead`.
  - `project-explorer` (if the architecture's impact analysis needs codebase structure).
- **Tier mix:** standard (constitution-checker), cheap (project-explorer), deep (research-lead for non-trivial).
- **Sequencing:** planning-lead drafts PLAN; constitution-checker runs; planning-lead applies the fixes; re-runs if needed (once).

### Phase 6 — Tasks (`task-decomposition`)

- **Trigger:** PLAN is settled and (in production mode) self-checks pass.
- **Subagents that fire:**
  - `task-decomposer` — produces `TASKS.md` + per-task packets.
  - `scope-estimator` (second invocation) — cross-checks the decomposer's output against the original size estimate.
  - `dependency-analyzer` (only in multi-feature plans, future) — for inter-feature ordering.
- **Tier mix:** standard (task-decomposer), cheap (scope-estimator, dependency-analyzer).
- **Sequencing:** `task-decomposer` runs; planning-lead + scope-estimator cross-check; re-run if mismatched.

### Phase 7 — Plan-critic (`plan-critic` skill + reviewer)

- **Trigger:** TASKS is settled; gate-check via `prereq_validate.py` passes.
- **Subagents that fire:**
  - **`reviewer`** (only in production mode, per `modes.yaml` `plan_review: independent`) — receives the full feature folder, returns a `REVIEW_REPORT` with verdict + findings.
  - The planning-lead addresses the findings.
- **Tier mix:** deep (reviewer).
- **Sequencing:** reviewer runs once; planning-lead applies fixes; optional re-review if the changes are substantial.

### Phase 8 — Gate and handoff

- **Subagents that fire:** none.
- **Planning-lead runs:** `prereq_validate.py --phase build`; on green, hand to build-lead.
- **Tier mix:** n/a (script-only).

### Total per-plan subagent usage (production mode)

| Subagent | Calls | Tier | Approximate share of planning tokens |
|---|---|---|---|
| `clarify` | 1 | cheap | 8% |
| `idea-capture` | 0-1 (depends on request clarity) | cheap | 0-5% |
| `prd-writer` | 1 | standard | 18% |
| `task-decomposer` | 1 | standard | 20% |
| `constitution-checker` | 1-2 (re-run if fixes) | standard | 10% |
| `scope-estimator` | 2 (intake + tasks) | cheap | 4% |
| `research-request-writer` | 0-3 (depends on unknowns) | cheap | 0-5% |
| `research-lead` (downstream) | 0-3 | deep (own) | 0-15% |
| `project-explorer` | 1-4 | cheap | 5% |
| `reviewer` (plan-critic) | 1 | deep | 15% |
| **planning-lead itself** | 1 | deep | 10-25% |
| **Total** | 8-19 | mixed | 100% |

The deep tier is concentrated in the planning-lead itself, the research-lead (for non-trivial research), and the reviewer (plan-critic). The 8 new subagents are 5 cheap + 3 standard = **no deep**, matching the principle that deep is for judgment and synthesis at the orchestration layer, not for parsing and classification at the worker layer.

---

## 5 · Subagent definition surface

### 5.1 The minimal frontmatter (all 8 new subagents)

Every new subagent follows the existing `CatalogAgent` shape (per `current-aspis-audit-1.md` §1.3):

```yaml
---
name: <name>                  # matches filename, kebab-case
description: <one-line role>  # used by the runtime to route
mode: subagent                # D-004: only project-lead + 4 promoted are primary
model: cheap|standard|deep    # a tier, resolved at render by agent-models.yaml
temperature: 0.1              # consistency with all current live agents
permission:
  read: allow
  grep: allow
  glob: allow
  edit: <allow|deny>          # allow only for the artifacts this subagent writes
  write: <allow|deny>
  bash:
    '*': deny
    '<whitelisted commands>': allow
    'git commit*': deny       # universal
    'git push*': deny         # universal
  task:
    '*': deny
    <delegate>: allow         # the subagent's own delegates (usually none)
  skill:
    '*': deny
    <skill>: allow
  webfetch: deny              # default
  websearch: deny             # default
---
# <Name>

## Identity
You are the <Name> — <one sentence role>.
You do not <X>. You do not <Y>. You do not <Z>.

## How you work
<3-5 numbered steps>

## Core rules
1. <rule>
2. <rule>

## On failure
- If blocked, STOP and report.
```

### 5.2 The required fields (planning-subagent-specific)

| Field | Required | Value | Why |
|---|---|---|---|
| `name` | yes | kebab-case, matches filename | OpenCode runtime requires it; catalog dataclass |
| `description` | yes | one line; what kind of work | OpenCode runtime uses for auto-routing |
| `mode` | yes | `subagent` | D-004; only project-lead + 4 promoted are primary |
| `model` | yes | `cheap` / `standard` / `deep` (tier; resolved to model id at render) | R-007: every agent declares explicit tier |
| `temperature` | yes | `0.1` | consistency with all current live agents |
| `permission.bash.*` | yes | `deny` | deny-wins permission model |
| `permission.bash.<whitelisted>` | yes | `allow` | the only commands this subagent needs |
| `permission.bash.git commit*` | yes | `deny` | universal (R-004) |
| `permission.bash.git push*` | yes | `deny` | universal (R-008) |
| `permission.task` | yes (if subagent delegates) | the agent names | the subagent's own delegates (usually none for the 8 new subagents) |
| `permission.skill` | yes | the skills this subagent needs | runtime skill allow-list |
| `permission.webfetch` | yes | `deny` (default) | universal; subagents don't webfetch directly |
| `permission.websearch` | yes | `deny` (default) | universal |
| `max_turns` | implicit (runtime default) | leave to runtime | 8-15 for leads; subagents can be lower (5-10) |
| `isolation` | implicit | `fresh_context: true` (subagent default) | each invocation is a new context window |

### 5.3 How subagents are registered in the catalog

The catalog is the single source of truth. Every new subagent is a markdown file at:

```
src/aspis/data/catalog/agents/<name>.md
```

The catalog parses every file in this directory into a `CatalogAgent` dataclass (per `current-aspis-audit-1.md` §1.3). The runtime adapters (OpenCode at `.opencode/agents/`, Claude at `.claude/agents/`) are generated from the catalog by `aspis promote` / `aspis export`. The system-lead owns catalog changes (D-008, §5 of `AGENT-SYSTEM-ARCHITECTURE.md`).

**Registration steps for each new subagent:**

1. Author `src/aspis/data/catalog/agents/<name>.md` with the frontmatter above.
2. Add the agent to `agent-capabilities.yaml` (`agents:` map) so the model-tier routing has a capability for it.
3. Add a tier override in `agent-models.yaml` `by_capability:` (or per-agent `agents:` block) if the subagent needs a non-default model.
4. Re-run `aspis models --apply` to materialize the model id into the catalog.
5. Add the subagent name to the **planning-lead's task allow-list** in the catalog: `task.planning-lead.delegates: [..., <name>]` (catalog field; renders as `permission.task.<name>: allow` in OpenCode).
6. Run the catalog content-conformance validator (`aspis validate-runtime`) to catch dangling references.
7. Re-export to `.opencode/agents/` and `.claude/agents/` via `aspis promote` (or `aspis export` for project scope).

The planning-lead's task allow-list is **the discovery mechanism** for its subagents — there is no separate "subagent registry." The static allow-list in the frontmatter is what the runtime uses to validate a `task` call.

### 5.4 How the planning-lead discovers available subagents

Two mechanisms, in order of priority:

1. **Static task allow-list** (the catalog `delegates` field). The planning-lead reads its own frontmatter (always present in the planning-lead's context) and knows exactly which agents it can call. This is the **authoritative** list.
2. **Skills that name subagents** (procedural reference). The `requirement-clarification` skill says "request it from the Research Lead" — the planning-lead reads the skill, sees the named agent, and uses the allow-list to confirm it's available. The skills are the *teaching*; the allow-list is the *enforcement*.

The planning-lead does NOT scan a registry at runtime. The catalog is the source of truth at *design* time (when the frontmatter is authored and rendered); at *run* time, the planning-lead consults its own allow-list.

### 5.5 The packet — the planning-lead's handoff shape

Every delegation is a **structured packet** (per the Cursor pattern, §3 of `production-loops-companies.md`):

```yaml
# Delegation packet (planning-lead → subagent)
to: <subagent-name>
purpose: <one sentence>
input:
  <key>: <value>           # varies by subagent (see §2)
output: <expected file path or shape>
context: <paths the subagent may read>
not_allowed: <paths the subagent may NOT touch>
constraints:
  mode: vibe|mvp|production
  tier_override: <optional; otherwise the subagent's default>
return:
  format: <markdown|file|inline>
  trace_event: <event-name>
```

The packet is **envelope + payload**. The envelope is fixed; the payload is the subagent's input. The planning-lead writes the packet (cheap; can be a template), the subagent reads it in its own context, returns a structured response.

---

## 6 · Cost-aware delegation

### 6.1 The cost shape across the system

From §6 of `AGENT-SYSTEM-ARCHITECTURE.md` (the 70/20/10 rule): **70% cheap / 20% standard / 10% deep** across the whole system. For the planning-lead, the per-plan shape is different because planning is **less synthesis-heavy than building**:

| Tier | System-wide target | Planning-lead actual | Notes |
|---|---|---|---|
| cheap | 70% | 60% (5 of 8 new subagents + project-explorer) | parsing, classification, counting, packet writing |
| standard | 20% | 30% (3 of 8 new subagents: prd-writer, task-decomposer, constitution-checker) | synthesis (SPEC, TASKS) + narrow judgment (constitution) |
| deep | 10% | 10% (planning-lead itself, reviewer, research-lead for non-trivial) | orchestration, plan-critic, research |

The deep tier is **concentrated at the orchestration + judgment layer** — exactly where the 70/20/10 rule puts it. The new subagents avoid deep because deep on a parsing job is wasted spend.

### 6.2 When cheap vs standard vs deep for the new subagents

The rule from `capabilities.yaml` + the planning subagent table:

| Subagent | Tier | Why |
|---|---|---|
| `clarify` | cheap | classification against 10 categories + max-5 prioritization |
| `idea-capture` | cheap | structuring a sentence into a template |
| `scope-estimator` | cheap | counting + lookup |
| `research-request-writer` | cheap | writing a packet from a sentence |
| `dependency-analyzer` | cheap | graph extraction + topological sort (deterministic candidate) |
| `prd-writer` | standard | synthesis (writes a SPEC, ~150 lines) |
| `task-decomposer` | standard | synthesis (writes TASKS.md + packets, ~10-30 artifacts) |
| `constitution-checker` | standard | judgment against 12 rules (narrow, but judgment) |
| `planning-lead` | deep | orchestration across the lifecycle + final decisions |
| `reviewer` (plan-critic) | deep | judgment, multi-lens (cross-artifact consistency) |
| `research-lead` | deep | judgment (validate sources, package) |

**When to override the default tier for a subagent:**

- `prd-writer` for a large SPEC (5+ user stories, multiple integrations) → escalate to deep. Override in the packet (`tier_override: deep`); the planning-lead signals this when the SPEC is bigger than the standard-tier sweet spot.
- `constitution-checker` for an architecture that touches protected paths (`.opencode/`, `.claude/`, `rules/**`) → escalate to deep. The protected-path branch is judgment-heavy and benefits from a stronger model.
- `task-decomposer` for a vibe-mode plan (1-2 tasks) → demote to cheap. The vibe work is small enough that the synthesis budget is tiny.

The override is **per-invocation**, not per-agent. The subagent's default tier is the right answer 80% of the time; the planning-lead's judgment is the override.

### 6.3 How user cost preferences flow down to subagent tier

`modes.yaml` already carries a `task_size` knob (`small` in production, `medium` in mvp, `large` in vibe). The `task_size` knob maps to subagent tier as follows:

| Mode | task_size | Subagent tier default | Override signal |
|---|---|---|---|
| **production** | small | standard for synthesis (prd-writer, task-decomposer, constitution-checker); cheap for the rest | `tier_override: deep` for very large SPECs |
| **mvp** | medium | cheap for synthesis (prd-writer, task-decomposer); cheap for the rest | rare overrides |
| **vibe** | large | cheap for everything | no overrides; skip most subagents entirely |

The user cost preference is set at `aspis mode <mode>` (the project-lead's one write) and propagates to:
- The planning-lead (mode-aware skill overlays).
- The subagent tiers (via the table above; the planning-lead reads the mode and picks the tier per subagent).

The **deep tier is never used for vibe**. The whole point of vibe is to be cheap. Vibe mode's planning-lead does intake + clarify + a 1-paragraph plan and skips the subagents entirely (or uses cheap-tier `idea-capture` and `scope-estimator` only).

### 6.4 The per-plan cost ceiling

For a production-mode full feature plan, the cost shape is:

- 1-2 × `prd-writer` (standard) — ~5-8k tokens
- 1 × `task-decomposer` (standard) — ~5-10k tokens
- 1-2 × `constitution-checker` (standard) — ~3-5k tokens
- 1-2 × `clarify` (cheap) — ~2-3k tokens
- 0-3 × `research-lead` (deep, downstream) — ~5-15k tokens per call
- 1 × `reviewer` (deep, plan-critic) — ~5-10k tokens
- 1-4 × `project-explorer` (cheap) — ~1-2k tokens per call
- **planning-lead itself** (deep) — ~10-20k tokens

**Total per plan: ~40-80k tokens**, dominated by the deep-tier calls (research-lead and reviewer). The 5 cheap subagents together are ~5-10k tokens — the right shape.

For vibe mode, the total is ~5-10k tokens (intake + 1-paragraph plan + skip). The 70/20/10 rule across many features lands the planning tier at the right proportion.

---

## 7 · Drift, gaps, and the implementation order

### 7.1 Drift to fix in the live file (immediate, before any new subagent)

- **Remove `committer: allow`** from `.opencode/agents/planning-lead.md` frontmatter. The catalog is correct (no committer); the live has drifted.
- The `.opencode/agents/planning-lead.md` body should add a one-line note: *"Planning produces templates, not commits; the build lead is the committer handoff. Do not invoke `committer`."*

### 7.2 New subagents to author (in order)

1. **`clarify`** (immediate) — closes a known old-ASPS gap; small, well-scoped, easy to author.
2. **`idea-capture`** (immediate) — closes a known old-ASPS gap; smallest subagent; cheap.
3. **`prd-writer`** (immediate) — closes F-027; the most concrete known gap; standard tier.
4. **`task-decomposer`** (immediate) — closes a known old-ASPS gap; the most-synthesis subagent.
5. **`research-request-writer`** (near-term) — small, low risk, high insurance value.
6. **`scope-estimator`** (near-term) — when multi-feature planning becomes normal.
7. **`constitution-checker`** (near-term) — high-leverage, narrow scope, replaces an in-context check.
8. **`dependency-analyzer`** (future) — only when multi-feature planning is real work.

### 7.3 Open questions for the system-lead

1. **The catalog's `defaults.yaml` may suppress some of these by name** (the old ASPS suppressed `prd-writer, spec-writer, plan-architect, acceptance-designer, lead-researcher`). The current ASPIS has no `defaults.yaml` in the live tree; verify with the system-lead that nothing is suppressing the 8 new subagents.
2. **The Claude runtime's `Agent` tool** — the current live Claude render lacks the `Agent` tool (per `old-asps-deep-analysis-1.md` §1 R-009). If the new subagents are to work in Claude, the Claude adapter needs the tool added. OpenCode is the primary target; Claude parity is a follow-up.
3. **The `test-lead` is missing from live** (the most concrete runtime gap, per `current-aspis-agents-2.md` §11). The planning-lead's task allow-list does not reference test-lead today, so this is independent of the new subagents — but it's the *one* live runtime gap the system-lead should fix in the same change set.
4. **Skill splits** — for each subagent, the corresponding *procedure* skill stays (per §3 above). The system-lead should add the new skills (`clarify-routing`, `spec-quality`, `task-format`, `constitution-checks` if not already present) in the same change set as the subagents.

### 7.4 What this design does NOT change

- The 5 primary agents (project-lead, planning-lead, build-lead, reviewer, system-lead). D-004 / D-026 are intact.
- The existing skills (38). The 5 planning skills stay; the new skills complement them.
- The catalog/live byte-parity moat. The new subagents are added to the catalog first; the live is generated.
- The 70/20/10 deep/standard/cheap target. The new subagents are 5 cheap + 3 standard, which strengthens the cheap share.
- The `git commit*` / `git push*` / `webfetch` / `websearch` universal denies. Every new subagent inherits the universal denies.

---

## 8 · The one-line summary

The planning-lead's delegation system is **8 new subagents (5 cheap, 3 standard, 0 deep) on top of 3 existing delegates (research-lead, reviewer, project-explorer), with `committer` removed as drift**. The subagents are classified by the planning phase they serve (intake → clarify → spec → architecture → tasks → plan-critic) and by the principle that **deep is for orchestration and judgment at the lead layer, not for parsing and classification at the worker layer**. The packet is the handoff; the catalog is the source of truth; the live is generated; and the planning-lead discovers its workers through the static task allow-list in its own frontmatter.

---

## Provenance

- Sources read: 6 source files (cited in the user prompt).
- Cross-references: `AGENT-SYSTEM-ARCHITECTURE.md` §6 (model tier strategy), `current-aspis-agents-2.md` §11–13 (drift + cross-agent matrix), `old-asps-deep-analysis-1.md` §3.6 (planning workers), `production-loops-companies.md` §0 Pattern 3 (recursive planners + isolated workers), `system-rules.md` (R-001…R-009), `architecture-constitution.md` (12 rules), `constitution-checks.yaml` (machine-readable index), `capabilities.yaml` (tier routing).
- Validation: every subagent proposal traced to a known gap (F-027 for `prd-writer`; old ASPS P0/P1b/P7 for `idea-capture`/`clarify`/`task-decomposer`) or a known best-fit tier (cheap for parsing, standard for synthesis, deep for judgment).
- Confidence: **high** for the 4 immediate subagents; **medium-high** for the 3 near-term; **low-urgency** for the 1 future.
- Refresh schedule: re-validate against the live agent roster when F-016 ships; re-validate tier mappings when `agent-models.yaml` changes.
