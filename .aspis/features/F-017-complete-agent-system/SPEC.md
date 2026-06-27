# F-017 — Complete the Agent System · Specification

> Mode: **production** — full rigor.

## Goal
Every ASPIS agent is production-complete: a final, best-pattern body plus the full asset set it needs (skills, templates, workflows, scripts, tools, hooks), so the core loop (plan → build → review → commit, plus fix, test, research, system) runs end-to-end on cheap/standard models. Smart, scalable, cheap to change.

## Problem
F-016 *designed* the agent system — 12 reference specs, 5 systemic specs, a 25-skill inventory, and 11 thin catalog bodies. But the system cannot *run* from designs. Every agent frontmatter references skills that don't exist yet, the planning scripts live in catalog but not at their runtime paths, the dynamic-readiness contract is undocumented, and no agent has been verified end-to-end. Without building the working assets, the core loop cannot execute on the designs F-016 produced.

## Scope
In scope:
- **L0 — Shared foundation**: cross-cutting P0 skills shared by multiple agents, the 3 planning scripts deployed to `.aspis/scripts/planning/`, workflow verification, the agent-body standard, and the dynamic-readiness convention.
- **L1 — Per-lead core**: each of the 8 leads gets a final body to the standard shape, its own P0 skills not covered in L0, wired tools/hooks, and verified permissions. Exit gate: plan→build→review→commit runs end-to-end on cheap+standard models.
- **L2 P0 — CLI verbs, governance, leaf agents**: the 3 P0 CLI verbs (validate-runtime, byte-parity, export), the governance subagent (minimal boundary-check, R-008 backbone), and the 3 leaf agents (committer, general-builder, project-explorer) with full asset sets.
- **L2 P1 — Depth**: the 6 P1 skills not already authored in L1, the 3 P1 CLI verbs (validate-index, drift, governance verb), and richer error-handling / edge-case coverage across the lead agents.
- **24 of the 25 missing skills** from the F-016 inventory (13 P0 + 7 P1 + 4 P2; `dependency-audit` deferred to F-018 — no consumer yet), authored to the existing catalog pattern.
- **Dynamic-readiness** baked into every loop agent's body — the "skip the plan" logic generalized, mode × task × model capability dials, leanest-correct-path default.

Out of scope:
- **Heavy 5-layer model-router engine** — designed, built later. Bodies reference mode/model/task dials but the full router is a future feature.
- **Full per-task dynamic context budgeting** — deferred.
- **Self-improvement loop** (Phase 4 of roadmap) — deferred.
- **Trace spine** (Phase 3 of roadmap) — deferred.
- **Dashboard** (Phase 5 of roadmap) — deferred.
- **System-lead L3 subagents** (runtime-validator, drift-auditor, permission-auditor, export-verifier, catalog-synchronizer, opencode-author, claude-author) — deferred to L3/F-018.
- **Planning-lead L3 subagents** (clarify, task-decomposer, constitution-checker, idea-capture, prd-writer, scope-estimator, research-request-writer, dependency-analyzer) — deferred to L3/F-018.
- **Stack-specific tester subagents** — deferred.
- **Live runtime auto-regeneration** of `.opencode/` and `.claude/` — owner runs `aspis export` manually after F-017 lands.
- **Multi-profile support beyond base.yaml** — deferred.
- **~10 ref-spec templates** (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, BUILD_REPORT, FEATURE_REPORT, TEST_REPORT, FIX_REPORT) — deferred to F-018.
- **~10 helper scripts** (scope_estimate, constitution_check, plan_quality_check, mode_validator, task_size_check, dependency_graph, search_cache, check_staleness, rank_source, compare_versions, cross_ref) — deferred to F-018.
- **project-lead operating protocol workflow** — deferred to F-018.

## User stories
Prioritized, each independently testable.

### Story 1 — L0 Shared Foundation (priority: P1)
- **Why this priority**: Every agent, skill, and script depends on the conventions, shared assets, and infrastructure L0 establishes. Nothing else can be built correctly without it.
- **Independent test**: `python .aspis/scripts/planning/feature_scaffold.py --help` exits 0. All shared P0 skills have valid SKILL.md files in `catalog/skills/`. The agent-body standard document is checkable against any agent body.
- **Acceptance scenarios**:
  1. **Given** the catalog script sources at `src/aspis/data/catalog/scripts/planning/`, **when** deployed to `.aspis/scripts/planning/`, **then** all 3 scripts (`feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`) pass AST parse and `--help` returns usage.
  2. **Given** a shared P0 skill (e.g. `mode-decision`), **when** checked against the catalog pattern, **then** it has valid frontmatter, a SKILL.md with Purpose / When to use / Procedure / Outputs / Anti-patterns sections, and is referenced by name from owning agents.
  3. **Given** the agent-body standard document, **when** any agent body is checked against it, **then** every required section (Identity, How you work, Core rules, Responsibilities→skills, Delegation, Dynamic-readiness) is present and follows the thin/single-source pattern.
  4. **Given** the dynamic-readiness convention, **when** any loop agent receives a task, **then** its body encodes how to right-size process from mode × task × model capability without weakening output quality.

### Story 2 — L1 Per-Lead Core (priority: P1)
- **Why this priority**: The 8 leads are the spine of the system. Until they can run the core loop end-to-end on cheap/standard models, the system is a design, not a working factory. This is the first concrete milestone the owner reviews.
- **Independent test**: A sample feature runs plan→build→review→commit end-to-end on cheap/standard models. Every lead's frontmatter skill references resolve to existing SKILL.md files. 0 broken references.
- **Acceptance scenarios**:
  1. **Given** the 8 lead agents (project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead), **when** each body is checked against the standard shape, **then** every section is present and no skill/template/workflow reference is broken.
  2. **Given** a sample feature request, **when** the planning-lead plans it and hands to build-lead, **then** build-lead delegates to a builder, reviewer reviews, and committer commits — all on cheap/standard models, all gates pass.
  3. **Given** the permission surface of each lead, **when** verified against its reference spec, **then** every tool grant is least-privilege, every deny floor is honored (`git commit*` committer-only, `git push*` none, `webfetch` system-lead + research-lead only, `websearch` research-lead-only), and no agent has `bash: '*': allow`.
  4. **Given** the delegation edges of each lead, **when** checked against the subagent roster, **then** every delegate listed exists as a catalog agent, and no lead lists a delegate that doesn't exist.

### Story 3 — L2 P0 — CLI Verbs, Governance, Leaf Agents (priority: P2)
- **Why this priority**: The 3 P0 CLI verbs are the deterministic validation spine the core loop needs. Governance is the R-008 mechanism. The 3 leaf agents (committer, general-builder, project-explorer) are the workers every lead delegates to. Without these, the loop has no workers and no deterministic gates.
- **Independent test**: `aspis validate-runtime --runtime all` exits 0. `aspis byte-parity --dry-run` reports catalog self-consistency CLEAN. `aspis export --dry-run` exits 0. The governance subagent's boundary-check rejects a write to `rules/` without R-008 approval. All 3 leaf agents have complete asset sets and can receive/execute packets.
- **Acceptance scenarios**:
  1. **Given** all 11 catalog agents, **when** `aspis validate-runtime --runtime all` runs, **then** it reports per-agent pass/fail with file:line evidence and exits 0 when all agents are structurally valid.
  2. **Given** the catalog, **when** `aspis byte-parity --dry-run` runs, **then** it reports per-agent catalog self-consistency (CLEAN/CONFLICT/PROTECT) and exits 0 when all are CLEAN. (Live `.opencode`/`.claude` parity is verified only after the owner's manual post-F-017 `aspis export`.)
  3. **Given** a protected path write attempt (e.g. `rules/system-rules.md`), **when** the governance subagent intercepts it, **then** it blocks the write, surfaces the R-008 requirement, and logs to the approval ledger.
  4. **Given** a task packet for the general-builder, **when** dispatched, **then** it edits only allowed files, reports distilled summary, and stops on scope violation — all on a cheap model.

### Story 4 — L2 P1 — Depth + Remaining Skills (priority: P2)
- **Why this priority**: P1 skills, P1 CLI verbs, and edge-case coverage turn a working system into a robust one. The core loop runs without these, but quality/reliability/operational health are incomplete.
- **Independent test**: All 6 P1 skills (session-continuation already in L1) have valid SKILL.md files. `aspis validate-index` exits 0. `aspis drift` reports zero drift. `aspis governance check` exits 0. Every lead agent handles at least 2 edge cases per its error-handling spec.
- **Acceptance scenarios**:
  1. **Given** the P1 skill inventory, **when** all 6 P1 skills (session-continuation already in L1) are authored to catalog, **then** each has a valid SKILL.md and is referenced by its owning agent.
  2. **Given** the `aspis validate-index` verb, **when** run against the project, **then** it checks FILE_REGISTRY.yaml and CODE_MAP.md for staleness and exits 0 when fresh.
  3. **Given** the `aspis drift` verb, **when** run against catalog and live runtimes, **then** it reports per-field per-agent drift and exits 0 when none.

## Requirements
Numbered so tasks and acceptance can trace to them.

### Asset-class outcomes
- **FR-001**: Every skill an agent's frontmatter references MUST exist as a valid `catalog/skills/<name>/SKILL.md` file with Purpose / When to use / Procedure / Outputs / Anti-patterns sections.
- **FR-002**: Every agent body MUST follow the standard shape: frontmatter + Identity + How you work + Core rules + Responsibilities→skills table + Delegation + Dynamic-readiness block. No duplicated content (R-006).
- **FR-003**: The 3 planning scripts MUST be deployed from `src/aspis/data/catalog/scripts/planning/` to `.aspis/scripts/planning/`, pass AST parse, and return usage on `--help`.
- **FR-004**: Every agent's permission surface MUST be least-privilege with the universal deny floor (`git commit*` committer-only, `git push*` none, `webfetch` system-lead + research-lead only, `websearch` research-lead-only, no `bash: '*': allow`).
- **FR-005**: Every agent's delegation section MUST list only delegates that exist as catalog agents. No broken references.
- **FR-006**: The dynamic-readiness block MUST be present in every loop agent's body, encoding the three dials (mode, task kind/scope, model capability) and the "leanest correct path" default.
- **FR-007**: The 3 P0 CLI verbs (validate-runtime, byte-parity, export) MUST be implemented, passing `--help` and a dry-run against the project.
- **FR-008**: The governance subagent MUST block writes to protected paths without R-008 approval and maintain an append-only approval ledger.
- **FR-009**: The 3 leaf agents (committer, general-builder, project-explorer) MUST have complete bodies matching the standard shape and all skills they reference.
- **FR-010**: The Claude Code adapter MUST preserve the `permission:` block (not strip it), maintaining capability-equivalence with the OpenCode runtime.
- **FR-011**: The `aspis byte-parity` verb MUST be a read-only reporter over the existing rendering/protection pipeline, checking catalog self-consistency per agent per field and reporting CLEAN/CONFLICT/PROTECT status. Live catalog-to-runtime parity is verified only after the owner's manual post-F-017 `aspis export`.
- **FR-012**: Every workflow file (plan.md, build.md, review.md, fix.md, small-task.md) MUST be verified complete against its owning agent's reference spec and fill any gaps.
- **FR-013**: The 6 P1 skills authored in L2-P1 (byte-parity-checker, export-manager, finding-format, model-router, runtime-author, scope-compliance) MUST be authored to the catalog pattern. (`session-continuation` authored in L1/T-16.)
- **FR-014**: The 3 P1 CLI verbs (validate-index, drift, governance) MUST be implemented with `--help` and a dry-run.
- **FR-015**: The 4 P2 skills (commit-readiness, hook-author, model-inventory, profile-manager) MUST be authored to the catalog pattern. (`dependency-audit` deferred to F-018 — no consumer yet.)
- **FR-016**: Every agent body MUST cite system rules by ID only (R-001, R-004, etc.), not restate them.

### Cross-cutting
- **FR-017**: The agent-body standard and dynamic-readiness convention MUST be documented in `.aspis/context/` as durable reference files, so every agent author and reviewer checks against the same contract.
- **FR-018**: No asset content (skill procedure, rule text, workflow step) MUST be duplicated across agent bodies. Agents reference by name/path only (R-006).
- **FR-019**: The cost-of-change for adding a new agent or skill MUST be ≤ 3 files: the new catalog file, the owning agent's frontmatter, and (if shared) any referencing agent's frontmatter.

## Feature rules & style
- **R-006 Thin agents, single source** — Content lives once in its asset (skill/workflow/template/data file); agent bodies reference, never duplicate.
- **R-003 Deterministic-first** — Script before agent. The 3 planning scripts and 6 CLI verbs are deterministic code; they never invoke an LLM.
- **R-004 One writer** — Only the committer has `git commit*`. Every other agent's bash allowlist denies it.
- **R-007 Pinned models** — Every agent declares its model tier explicitly in frontmatter. No silent inheritance.
- **R-008 Human gate** — Architecture, rules, permissions, security posture, and model-routing changes require human approval via the governance subagent.
- **R-010 Delegate with purpose** — Leads push mechanical/context-heavy work to cheap subagents; leads keep their higher model for judgment.
- **Architecture constitution**: Low cost-of-change, new files over core edits, plugin-first, no special-cases, discovery over registration.
- **Asset authoring pattern**: Skills use the `catalog/skills/<name>/SKILL.md` format (frontmatter + Purpose / When to use / Procedure / Outputs / Anti-patterns). Templates in `catalog/templates/`. Workflows in `.aspis/workflows/`. Scripts in `catalog/scripts/` (source) → `.aspis/scripts/` (deployed).
- **Permissions**: Universal deny floor: `git commit*` committer-only, `git push*` none, `webfetch` research-lead + system-lead only, `websearch` research-lead-only. No agent has `bash: '*': allow`.

## Key entities
- **Skill**: A reusable thinking procedure at `catalog/skills/<name>/SKILL.md`. References from agent frontmatter `skills:` list. Owned by one agent; may be allowlisted by others.
- **Agent body**: The instruction file at `catalog/agents/<name>.md`. Thin — holds identity, rules, and skill/workflow references only.
- **Workflow**: A multi-step procedure at `.aspis/workflows/<name>.md`. Agents point to it; do not restate steps.
- **Script**: Deterministic Python code at `catalog/scripts/` (source) or `.aspis/scripts/` (deployed). No LLM invocation. Prefer over an agent (R-003).
- **CLI verb**: A subcommand of `aspis` implemented as a deterministic script. Returns exit 0 on success, non-zero with file:line evidence on failure.
- **Dynamic-readiness block**: A short section in each loop agent's body encoding how it right-sizes its process from mode × task × model capability.
- **Governance subagent**: The deterministic R-008 enforcement mechanism — not an LLM agent. Boundary-check on protected paths, append-only approval ledger.

## Success criteria
Measurable and technology-agnostic — the bar acceptance checks against.

- **SC-001**: 0 frontmatter skill references without a corresponding `catalog/skills/<name>/SKILL.md` file, across all 12 agent bodies.
- **SC-002**: The core loop (plan → build → review → commit) runs end-to-end on a sample feature using only cheap and standard model tiers — no deep models required.
- **SC-003**: `aspis validate-runtime --runtime all` exits 0 for all 12 agent bodies.
- **SC-004**: `aspis byte-parity --dry-run` reports catalog self-consistency (catalog render matches expected output shape; no broken refs, no missing fields). Live `.opencode`/`.claude` parity is verified only after the owner's manual post-F-017 `aspis export`.
- **SC-005**: `aspis export --dry-run` exits 0 and reports the full export plan (ADD/UNCHANGED/UPDATE/PROTECT/CONFLICT decisions per file).
- **SC-006**: Every agent body passes the agent-body standard check — all required sections present, no duplicated content, skill references resolve.
- **SC-007**: A write attempt to any protected path (`rules/**`, `.aspis/rules/**`, `.opencode/agents/**`, `.claude/agents/**`, `.claude/settings.json`, `**/permissions*.yaml`) is blocked without R-008 approval.
- **SC-008**: 0 agents have `bash: '*': allow` in their permission surface.
- **SC-009**: All 24 in-scope missing skills from the F-016 inventory have valid SKILL.md files in the catalog (`dependency-audit` deferred to F-018 — no consumer yet).
- **SC-010**: All 5 workflows (plan.md, build.md, review.md, fix.md, small-task.md) are verified complete — no TODO markers, no "NYI" references, steps align with owning agents' reference specs.
- **SC-011**: The cost-of-change test passes: adding a hypothetical new leaf agent or skill requires changes to ≤ 3 files (the new catalog file, the owning agent's frontmatter, and at most one referencing agent's frontmatter).
- **SC-012**: Every lead agent's dynamic-readiness block references the 3 dials (mode, task kind/scope, model capability) and encodes the "leanest correct path" default.

## Assumptions
- F-016 designs are authoritative and locked. F-017 builds to them, does not redesign.
- The 4 catalog script source files at `src/aspis/data/catalog/scripts/planning/` are correct and need no logic changes — deployment is a copy operation.
- The existing 38 skills in `catalog/skills/` are correct and need no changes beyond verification.
- The 11 thin catalog agent bodies from F-016 are the starting point for finalization, not a rewrite.
- The existing `.aspis/workflows/` files have the right structure; F-017 verifies and fills gaps, does not restructure.
- Models resolve per `config/models.yaml` tier map. The cheap/standard/deep tier labels are already defined there.
- The `enforcement: warn` default from D-010 remains until the runtime block is implemented and probation completes.

## Clarifications
Resolved questions, newest session first.

### Session 2026-06-27
- **Q1 — L2 scope boundary**: Which CLI verbs / governance / subagents in F-017 vs deferred?
  → **A**: L2 P0 = 3 P0 CLI verbs (validate-runtime, byte-parity, export) + governance subagent (minimal boundary-check, R-008 backbone). L2 P1 = 3 P1 CLI verbs (validate-index, drift, governance verb) + remaining P1 skills. Deferred to L3/F-018: ALL system-lead subagents, ALL planning-lead subagents. Scripts before agents (R-003).
- **Q2 — First milestone**: Owner review after L1 or continuous?
  → **A**: Explicit owner-review gate after L1. L1 exit = plan→build→review→commit runs end-to-end on cheap+standard. Hard gate in PLAN, not soft checkpoint. Do NOT roll into L2.
- **Q3 — Live runtime regeneration**: Include in F-017 or defer?
  → **A**: Build export verb so catalog→live works on demand with dry-run target + byte-parity. Do NOT auto-regenerate `.opencode/` / `.claude/`. Owner runs manually after F-017 lands.

## Open questions
- None remaining. All decisions resolved.
