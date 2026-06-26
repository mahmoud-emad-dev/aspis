# F-016 — Agent System Architecture · Specification

> Mode: **production** — full rigor.

## Goal
Define and deliver the complete, documented agent system architecture for ASPIS: the roster, roles, responsibilities, permissions, delegation maps, model tiers, lifecycles, and systemic rules for all 11 agents, grounded in industry-proven patterns and verified against the live codebase.

## Problem
ASPIS has 12 catalog agents, 10 live agents, and zero comprehensive documentation of how the system is meant to operate end-to-end. Every agent has a thin live file (~60–150 lines) and scattered catalog entries, but there is no authoritative specification that defines: (a) what each agent IS, (b) what it owns vs. delegates, (c) its permission surface, (d) its model tier strategy, (e) its procedural flows, (f) its error handling, and (g) how it fits into the whole. Without this specification, agents drift from design, cross-agent consistency is unenforced, systemic gaps accumulate undetected, and planning/quality-review/runtime-validation have no stable contract to enforce against. The research phase produced 12 research files and 8 complete agent reference specs — this feature crystallizes them into the system's durable specification and implementation plan.

## Scope
In scope:
- **11 agents** fully specified with identity, responsibilities, skills, permissions, delegation map, model tier, procedural flows, use cases, anti-patterns, error handling, and acceptance criteria
- **8 primaries/support agents** with complete reference specs: project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead
- **3 leaf agents** with lighter (but complete) specs: committer, general-builder, project-explorer
- **System-wide cross-cutting concerns**: core loop, delegation model, permission model, model tier strategy, error-handling matrix, skill-to-agent mapping, the 9 system rules (R-001–R-009), 12-point architecture constitution compliance
- **Live-vs-catalog gap reconciliation**: 13 catalog-runtime gaps across 8 agents catalogued in F-016 research
- **Systemic findings resolution**: enforcement warn→block, governance subagent design, modes.yaml authoring, planning script deployment, test-lead deployment verification
- **Agent catalog assets**: updating 11 catalog agent files at `src/aspis/data/catalog/agents/` to match the reference specs
- **Missing skills specification**: 30+ new skills needed across agents, defined by purpose and priority
- **Missing CLI verbs specification**: 6 validation gates not yet built
- **Cross-runtime parity**: ensuring Claude Code adapter preserves permission blocks

Out of scope:
- **Runtime rendering engine changes** — adapter fixes are F-016 follow-ups tracked in the PLAN, not the agent specs themselves
- **Trace spine implementation** (Phase 3 of roadmap) — designed, not built
- **Dashboard** (Phase 5 of roadmap) — designed, not built
- **Multi-profile support beyond base.yaml** — deferred
- **MCP plugin system** — deferred
- **Self-improvement loop** (Phase 4 of roadmap) — designed, not built
- **Actual product code** — F-016 produces specifications, plans, and tasks; the build phase implements them
- **Changing the `aspis` CLI engine** — unless a bug in the engine blocks an agent spec requirement

## User stories
Prioritized, each independently testable. P1 is the MVP slice.

### Story 1 — Core Agent Specs (priority: P1) 🎯 MVP
- **Why this priority**: The 8 primary/support agents are the operating system of ASPIS. Without their specs, no other work can be validated, reviewed, or enforced. Every downstream story depends on having the core agent contracts defined.
- **Independent test**: All 8 agent reference specs pass adversarial review (reviewer audit: 0 CRITICAL, 0 HIGH findings). Every agent has: identity, responsibilities→skills mapping, permission surface, delegation map, model tier, procedural flows, use cases, anti-patterns, error handling, acceptance criteria. Cross-agent consistency verified (no role overlap, no orphaned delegation edges).
- **Acceptance scenarios**:
  1. **Given** the 8 research-produced reference specs in `Research/ref/`, **when** reviewed against the architecture constitution and system rules, **then** all 8 specs are approved (0 CRITICAL findings, 0 HIGH unresolved).
  2. **Given** the approved reference specs, **when** a developer reads any single agent spec, **then** they can understand that agent's complete role, boundaries, and operating procedure without consulting other documents.
  3. **Given** all 8 agent specs, **when** cross-referenced for consistency, **then** no two agents claim the same responsibility, no delegation edge points to a non-existent agent, and every agent referenced by another exists.

### Story 2 — Leaf Agents + Catalog Assets (priority: P2)
- **Why this priority**: The 3 leaf agents (committer, general-builder, project-explorer) are lighter-weight but essential for the production loop. Once the core leads are spec'd, the workers that execute their instructions must be specified. Additionally, the catalog agent files must reflect the reference specs.
- **Independent test**: All 3 leaf agent specs complete. All 11 catalog agent files at `src/aspis/data/catalog/agents/` match their reference specs (frontmatter fields aligned, body updated). Missing skills specified with purpose and priority.
- **Acceptance scenarios**:
  1. **Given** the leaf agent reference specs, **when** reviewed against the system rules (R-004 one-writer for committer, R-006 thin agents), **then** all 3 pass with 0 violations.
  2. **Given** the 11 catalog agent files, **when** compared against their reference specs, **then** frontmatter fields (mode, model, permissions, delegates, skills, runtimes) are consistent, and body instructions reflect the spec's identity and rules.

### Story 3 — Systemic Gaps & Governance (priority: P3)
- **Why this priority**: The governance subagent, enforcement mode (warn→block), modes.yaml, planning scripts, and missing CLI verbs are cross-cutting infrastructure. They must be specified but can be built after the agent roster is stable.
- **Independent test**: Governance subagent spec complete (R-008 enforcement in code). Enforcement mode design documented (block for runtime, warn for pre-commit). modes.yaml spec complete (all mode knobs). Planning scripts spec complete (feature_scaffold.py, task_compile.py, prereq_validate.py). Missing CLI verbs specified (validate-runtime, validate-index, byte-parity, drift, export, governance).
- **Acceptance scenarios**:
  1. **Given** the governance subagent spec, **when** reviewed against R-008, **then** it defines: which paths are protected, how human approval is recorded, how intervention blocks in-flight writes, and how the approval ledger is audited.
  2. **Given** the modes.yaml spec, **when** compared against the current planning workflow, **then** every knob (spec, architecture, task_size, plan_review, build_review, test_depth, docs, promotable) has a value per mode (vibe/mvp/production).

## Requirements
Numbered so tasks and acceptance can trace to them.

### Agent specification requirements
- **FR-001**: The system MUST have a complete, reviewed, and approved reference specification for each of the 11 agents (8 primaries/support + 3 leaves).
- **FR-002**: Every agent spec MUST define: identity (what it IS / is NOT), responsibilities→skills mapping, permission surface (read/write/bash/delegation), delegation map (receives from / sends to), model tier strategy, procedural flows, use cases, anti-patterns, error handling, and acceptance criteria.
- **FR-003**: No two agents MUST claim the same responsibility. Role boundaries MUST be non-overlapping.
- **FR-004**: Every delegation edge in every agent spec MUST point to an agent that exists in the roster. No orphaned delegate references.
- **FR-005**: Every agent MUST declare a model tier (cheap/standard/deep) consistent with the tier strategy and its role's cognitive demands.
- **FR-006**: Every agent MUST have a defined permission surface: read scope, edit/write scope, bash allowlist, task/delegation allowlist, skill allowlist, and web scope.
- **FR-007**: All universal denies MUST be present in every agent's permission surface: `git commit*` denied except committer (R-004), `git push*` denied for all agents (R-008), `webfetch`/`websearch` denied except system-lead and research-lead.
- **FR-008**: The reviewer agent MUST be read-only (edit/write denied) — R-004.
- **FR-009**: The committer agent MUST be the only agent with `git commit*` allowed — R-004.

### Catalog asset requirements
- **FR-010**: All 11 catalog agent files at `src/aspis/data/catalog/agents/` MUST be updated to reflect their reference specs: frontmatter fields aligned, body instructions consistent with the spec's identity and rules.
- **FR-011**: Every catalog agent frontmatter MUST include: name, description, mode, model (tier), temperature, tools, permissions (bash + web), delegates, skills, runtimes, export_scope.
- **FR-012**: Every skill referenced by an agent's body or skill allowlist MUST exist in the catalog at `src/aspis/data/catalog/skills/<name>/SKILL.md`.

### Systemic requirements
- **FR-013**: The core loop (ENTRY → CLASSIFY → PLAN → BUILD → REVIEW → COMMIT) MUST be documented with per-phase ownership, gates, and mode overlays.
- **FR-014**: The delegation model MUST be documented: L1→L2→L3, packet shape (5 fields), recontextualization protocol, "single owner per request" rule.
- **FR-015**: The permission model MUST be documented: deny→ask→allow, first-match-wins, three layers (static rules + hooks + OS sandbox), scope enforcement at three boundaries (packet + frontmatter + pre-commit hook).
- **FR-016**: The model tier strategy MUST be documented: 70/20/10 cheap/standard/deep target, tiered routing, cascade-on-failure, per-agent tier assignments.
- **FR-017**: The error-handling matrix MUST be documented: who catches what, who fixes what, who reviews the fix, and escalation rules including the 3-attempt hard cap.
- **FR-018**: The governance subagent MUST be specified: protected paths list, R-008 human-approval workflow, approval ledger, intervention handler for in-flight writes.
- **FR-019**: The modes.yaml file MUST be specified with per-mode values for all knobs: spec depth, architecture depth, task size, plan review, build review, test depth, docs, promotable.
- **FR-020**: Enforcement mode MUST be specified: `block` for runtime tools (Edit/Write), `warn` for pre-commit hooks, CI override via `ASPIS_ENFORCEMENT=block`.

### Cross-runtime requirements
- **FR-021**: The Claude Code adapter MUST preserve the permission block in rendered agent files — cross-runtime parity with OpenCode.
- **FR-022**: Cross-runtime byte-parity check (`aspis byte-parity`) MUST be specified: catalog regenerates live runtime files byte-for-byte, with defined CONFLICT/PROTECT decision handling.

### Skills and tools requirements
- **FR-023**: All missing skills identified across agent specs (30+ across 8 agents) MUST be specified with: purpose statement, owning agent, priority (P0/P1/P2), and estimated effort.
- **FR-024**: All missing CLI verbs (validate-runtime, validate-index, byte-parity, drift, export, governance) MUST be specified with purpose and priority.
- **FR-025**: All three planning scripts (feature_scaffold.py, task_compile.py, prereq_validate.py) MUST be specified for deployment from catalog to `.aspis/scripts/planning/`.

### Acceptance and quality requirements
- **FR-026**: Every agent spec MUST include measurable acceptance criteria (checkbox list).
- **FR-027**: Every agent spec MUST pass independent adversarial review (reviewer audit) with 0 CRITICAL and 0 HIGH unresolved findings.
- **FR-028**: The 12-point architecture constitution MUST be checked against the agent system design: no special cases, plugin-first, single source of truth, cost-of-change ≤10 files.

## Feature rules & style
Project rules and conventions this feature must honour.

- **R-001 Scope**: Changes stay within `.aspis/features/F-016-agent-system-architecture/` (specs, plans, tasks) and `src/aspis/data/catalog/agents/` (catalog files). No product code changes unless specified in PLAN steps.
- **R-002 Gates first**: Every phase of F-016 has a deterministic gate before proceeding.
- **R-003 Deterministic-first**: Agent specs are documents — no code needed for the spec itself. For implementation, prefer scripts over agents.
- **R-004 One writer**: planning-lead produces the SPEC/PLAN/TASKS; reviewer audits them; committer commits them.
- **R-005 Tests-as-spec**: Agent acceptance criteria are the "tests" — every checkbox must be verifiable.
- **R-006 Thin agents, single source**: Reference specs are the single source for each agent. Catalog files derive from specs, not vice versa.
- **R-008 Human gate**: The governance subagent design, enforcement mode flip, and model routing changes in this feature require human sign-off.
- **R-009 Trace and learn**: Every decision in this feature is traceable to a research file, reference spec, or existing decision (D-###).

**Architecture constitution alignment:**
- **Local Change**: Agent specs are new files in `Research/ref/`; catalog updates are focused edits to existing files.
- **Plugin First**: No core engine changes; agents are catalog data.
- **Single Source of Truth**: Reference specs are the truth; catalog files derive from them.
- **No Special Cases**: Agent behaviors are governed by data (modes.yaml, permissions, tier assignment), not `if agent == "x"` logic.

## Key entities

- **Agent**: A named role with identity, responsibilities, skills, permissions, delegation map, model tier, and operating procedure. 11 agents in the system.
- **Reference Spec** (`Research/ref/<agent>.md`): The durable specification document for one agent — 12–18 sections covering identity through acceptance criteria. The single source of truth for that agent's design.
- **Catalog Agent** (`src/aspis/data/catalog/agents/<agent>.md`): The runtime-neutral catalog file with YAML frontmatter + body instructions, from which runtime-specific files (`.opencode/agents/`, `.claude/agents/`) are rendered.
- **Skill** (`src/aspis/data/catalog/skills/<name>/SKILL.md`): A named procedure (with Purpose, When to use, Procedure, Outputs, Anti-patterns) that agents load to perform specific work.
- **Delegation Packet**: The 5-field handoff (intent · context · constraints · references · expected outcome) from one lead to another or from a lead to a worker.
- **Core Loop**: The universal request lifecycle: ENTRY → CLASSIFY → PLAN → BUILD → REVIEW → COMMIT, with per-phase ownership and mode overlays.
- **Mode**: The rigor dial (vibe / MVP / production) that scales planning depth, review depth, test depth, and task granularity — a ceiling, not a floor.
- **Model Tier**: The cognitive capability assignment (cheap / standard / deep) per agent, resolved at render time to a concrete model id via the model catalog.
- **Governance Subagent**: The only agent permitted to edit `rules/**` and protected paths, gated by R-008 human approval.

## Success criteria
Measurable and technology-agnostic.

- **SC-001**: All 11 agent reference specs pass adversarial review with 0 CRITICAL findings and 0 HIGH unresolved findings.
- **SC-002**: Cross-agent consistency audit passes: 0 overlapping responsibilities, 0 orphaned delegation edges, 0 references to non-existent skills.
- **SC-003**: All 11 catalog agent files at `src/aspis/data/catalog/agents/` are frontmatter-aligned with their reference specs.
- **SC-004**: All 30+ missing skills are specified with purpose, owning agent, and priority (P0/P1/P2).
- **SC-005**: All 6 missing CLI verbs are specified with purpose and priority.
- **SC-006**: The governance subagent spec is complete and passes R-008 compliance review.
- **SC-007**: The modes.yaml spec is complete — every knob has per-mode values — and passes review against the planning workflow.
- **SC-008**: The enforcement mode spec (block for runtime, warn for pre-commit) passes security review.
- **SC-009**: All 3 planning scripts have deployment specifications (source, destination, trigger, validation).
- **SC-010**: The Claude Code adapter permission-block preservation is specified with acceptance criteria.
- **SC-011**: The complete PLAN.md and TASKS.md are ready for build-lead handoff — every FR maps to ≥1 task, every SC has a verification method.
- **SC-012**: Cost-of-change for the agent system: adding a new agent requires ≤5 files touched (catalog agent file + profile if new + SPEC entry + PLAN entry + TASKS entry).

## Assumptions
- The 8 reference specs in `Research/ref/` are the authoritative design. F-016 synthesizes them; it does not redesign them.
- The 3 leaf agents (committer, general-builder, project-explorer) need lighter specs — 6–8 sections each, not the full 12–18 of the leads.
- The live-vs-catalog gaps documented in `current-aspis-agents-2.md` are real and must be resolved. The reference specs describe the *target* state; the PLAN addresses the gap.
- test-lead IS deployed in the live runtime (contrary to some local draft claims), but its reference spec still needs validation.
- The `committer` in planning-lead's live task allow-list is a bug, not a design choice — the reference spec says "remove."
- Modes.yaml does not exist on disk. This feature specifies it; building it may be a follow-up task.
- The Claude Code adapter permission-block stripping is a confirmed bug that this feature's PLAN must address.
- Existing decisions (D-001 through D-018) are authoritative and constrain the design. New decisions created by F-016 will be numbered D-019+.

## Clarifications
Resolved questions, newest session first.

### Session 2026-06-26
- Q: Which agents get full reference specs vs. lighter specs? → A: The 8 primaries/support agents get full 12–18 section specs. The 3 leaves (committer, general-builder, project-explorer) get lighter 6–8 section specs. The leaves' roles are narrower and deterministic enough that the full template is unnecessary.
- Q: Is test-lead deployed or not? → A: Deployed — confirmed in `current-aspis-agents-2.md` (line 27: test-lead EXISTS at `.opencode/agents/test-lead.md`). The local draft claim of "not deployed" was an accuracy error corrected by the reviewer audit.
- Q: Should the 3 leaf agent specs be full or light? → A: Light — 6–8 sections. Their roles are bounded (committer: commit only; general-builder: one packet, one report; project-explorer: read-only exploration). The full 12–18 section template would be over-specification.
- Q: What is the R-008/R-009 attribution? → A: R-008 is the human gate. R-009 is "Trace and learn." All references to "protected paths" and "human approval" must cite R-008. The local draft confusion has been corrected in the master synthesis `local/AGENT-SYSTEM-ARCHITECTURE.md`.

## Open questions
- None remaining — all design questions resolved across the 8 reference specs' §Open Design Questions sections and the 2 reviewer audits. Any deferred questions are tracked per-agent in their reference spec's §Open Design Questions, with status (Decided/Deferred/Blocker).
