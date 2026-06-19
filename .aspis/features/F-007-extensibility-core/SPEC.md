# F-007 — Extensibility core + architecture constitution · Specification

Mode: **mvp** — focused rigor. P1 makes the core extension-ready; P2 ships the
constitution + agent wiring; P3 records the why and updates the docs.

## Goal

Make ASPIS grow by **adding files, not editing core**, and make that discipline
enforceable by the agents themselves. Two halves:

1. **Extensibility core** — asset kinds become *data + discovery*, and runtimes
   gain a *capability model*, so adding a new asset kind, runtime, or profile
   needs **zero edits to `export.py`/`profiles.py`** (Cost-of-Change → ~0 files).
2. **Architecture constitution** — a global engineering-standards rule asset
   (the "why" behind the design), shipped to every project and wired into the
   planning lead, build lead, and reviewer so plans, code, and reviews are held
   to it.

## Problem

Adding one asset kind today edits the core in two places: `profiles.py` (a new
field **and** the `ASSET_KINDS` tuple) and `export.py` (the `_target_and_op`
literal map **and** `_RUNTIME_KINDS`). The removed F-005 "guards" proved the
cost: one concept forced edits across `profiles.py`, `export.py`, `base.py`, two
runtime adapter modules, and a bespoke `export_guards.py` — 6+ core files for one
kind. That violates Local Change and Cost-of-Change, and there is no shared
standard the planning/build/review agents check against, so the same drift will
recur with every future profile, runtime, dashboard, or tracing feature.

## Scope

In scope:
- An **asset-kind registry** (`src/aspis/assetkinds.py`) — the single source for
  every kind's placement (brain vs per-runtime) and write op (copy / render).
  Default: a catalog dir maps to a brain copy; a small override table covers the
  rendered/per-runtime kinds.
- **`profiles.py`** refactor — `assets` as a kind-keyed dict (profile YAML format
  unchanged); `ASSET_KINDS` derived from the registry, not hardcoded.
- **`export.py`** refactor — target/op and per-runtime placement read from the
  registry; remove the literal `_target_and_op` map and `_RUNTIME_KINDS`.
- A **runtime capability model** — `RuntimeAdapter.supports(kind)`; export places
  a per-runtime kind for a runtime only if the runtime supports it.
- The **Architecture Constitution** (`catalog/rules/architecture-constitution.md`)
  — global engineering standards (the rules distilled from the design session).
- A **machine-readable checklist** (`catalog/config/constitution-checks.yaml`)
  mapping each rule to the role(s) that enforce it (planning / build / review).
- Wiring the constitution into the **planning-lead, build-lead, reviewer** agents
  (thin references — not every agent gets every rule).
- Decisions **D-008** (everything-extensible) + **D-009** (constitution layer);
  `ARCHITECTURE.md`, `ROADMAP.md`, context docs updated.

Out of scope (deferred):
- Rebuilding F-005 (hooks) and F-006 (git) — they wait on backup branches and
  return *on top of* this architecture.
- A `knowledge` primitive / project-brain index, event system, dashboard — later
  features that this core makes cheap to add.
- Any runtime/permission change beyond the capability seam (R-008 human gate).

## User stories

### Story 1 — A new asset kind needs zero core edits (priority: P1)
- **Why**: this is the whole point — Local Change + Cost-of-Change.
- **Independent test**: a test adds a throwaway catalog kind dir + a profile that
  lists it and asserts export plans a brain copy for it, with no change to
  `export.py`/`profiles.py`.
- **Acceptance**:
  1. **Given** a catalog dir `catalog/<newkind>/x.md` and a profile listing
     `<newkind>: [<newkind>/x.md]`, **when** the export is planned, **then** an
     action copies it to `.aspis/<newkind>/x.md`.
  2. **Given** that same setup, **when** the test runs, **then** it touches no
     core source file (proven by the registry being the only place kinds live).

### Story 2 — Per-runtime placement is capability-driven, not name-checked (priority: P1)
- **Why**: kills `if runtime == "claude"`; lets a future runtime opt out of a kind.
- **Independent test**: an adapter that declares it does not support `commands`
  yields no command actions for that runtime; default adapters are unchanged.
- **Acceptance**:
  1. **Given** the registry marks `agents/commands/skills` per-runtime, **when**
     export plans them, **then** each lands under every supporting runtime.
  2. **Given** an adapter whose `supports("commands")` is False, **when** export
     plans commands, **then** none are produced for that runtime.

### Story 3 — The constitution is a first-class, shipped rule asset (priority: P2)
- **Why**: standards must be reusable assets, not buried in prompts.
- **Independent test**: the base profile exports the constitution doc + checklist
  into a project's brain; the checklist parses and every entry names ≥1 role.
- **Acceptance**:
  1. **Given** the base profile, **when** a project is initialised, **then**
     `.aspis/rules/architecture-constitution.md` and the checks config are present.
  2. **Given** `constitution-checks.yaml`, **when** it is loaded, **then** every
     rule has an id, a statement, and at least one enforcing role.

### Story 4 — Planning, build, and review agents enforce it (priority: P2)
- **Why**: the rules only matter if the loop checks them.
- **Independent test**: the planning-lead, build-lead, and reviewer agent files
  reference the constitution; the reviewer's lens includes the Cost-of-Change check.
- **Acceptance**:
  1. **Given** the three agent files, **when** inspected, **then** each references
     the constitution and the subset of rules it owns.

## Requirements

- **FR-001**: `assetkinds.py` MUST expose every asset kind with its `placement`
  (`brain` | `per_runtime`) and `op` (`copy` | `render_agent` | `render_command`)
  from one source — a discovered default (`brain`/`copy`) plus a small override
  table for the rendered/per-runtime kinds.
- **FR-002**: `assetkinds.py` MUST provide `target(kind, runtime, rel)` and
  `op(kind)` (or equivalent) so `export.py` holds **no** per-kind literals.
- **FR-003**: `profiles.Profile` MUST store assets as a kind-keyed mapping while
  keeping the existing YAML profile format (top-level kind keys still load).
  `ASSET_KINDS` MUST derive from the registry, not a hand-maintained tuple.
- **FR-004**: `export.py` MUST contain no `_target_and_op` literal map and no
  `_RUNTIME_KINDS` constant; placement/op come from the registry.
- **FR-005**: `RuntimeAdapter` MUST expose `supports(kind: str) -> bool`
  (default True), and `export.py` MUST place a per-runtime kind for a runtime
  only when the adapter supports it. The existing per-asset `runtimes:` lock and
  `export_scope` behaviour MUST be preserved.
- **FR-006**: Adding a brain-copied asset kind MUST require **only** a new catalog
  dir + listing it in a profile — no core source edit (proven by a test).
- **FR-007**: `catalog/rules/architecture-constitution.md` MUST state the global
  engineering standards: the north-star/cost-of-change rule, automation-before-
  intelligence (ref R-003), the extension rules (plugin-first, single-source,
  local-change, config-over-code, discovery, capability model, no-special-cases),
  and the agent-oriented file rules.
- **FR-008**: `catalog/config/constitution-checks.yaml` MUST list each rule with
  `id`, `statement`, `enforced_by` (subset of `planning`/`build`/`review`), and a
  `review_question`.
- **FR-009**: The planning-lead, build-lead, and reviewer agent definitions MUST
  reference the constitution and the rule subset they own; other agents are
  unchanged (R-006 thin-agent style).
- **FR-010**: The base profile MUST ship the constitution doc + checks config.
- **FR-011**: `DECISIONS.md` MUST record D-008 (everything-extensible) and D-009
  (constitution as the global standards layer); `ARCHITECTURE.md` and `ROADMAP.md`
  MUST be updated (asset-kind registry + capability model; F-007 added; F-005/F-006
  marked deferred + backed up).
- **FR-012**: The full existing test suite MUST stay green; new tests cover
  Stories 1–3.

## Feature rules and style

- ASPIS code style: clean/modular/DRY, small files, data over hardcode, docstrings
  with Purpose + section spacing. Files explain themselves (agent-oriented rules).
- The registry is the **single source of truth** for asset kinds; nothing else
  enumerates them.
- No behavioural change to existing exports — this is a structural refactor with a
  new seam, proven by the unchanged suite.
- R-001 (scope), R-002 (gates first), R-003 (deterministic-first — the rule this
  feature codifies), R-006 (thin agents), R-008 (this architecture/rules change is
  human-directed — the gate is the user's explicit instruction) apply.

## Success criteria

- **SC-001**: A new brain asset kind is exported via registry + profile alone, with
  no core edit (unit-tested — Story 1).
- **SC-002**: Per-runtime placement is capability-gated; a non-supporting adapter
  drops that kind (unit-tested — Story 2).
- **SC-003**: `export.py` and `profiles.py` contain no hardcoded kind enumeration.
- **SC-004**: Constitution doc + checklist ship via the base profile and the
  checklist is well-formed (unit-tested — Story 3).
- **SC-005**: Planning-lead, build-lead, reviewer reference the constitution.
- **SC-006**: Full gate green (`ruff format --check`, `ruff check`, `pytest`).

## Dependencies

- Branches from the **F-004 baseline** (`4d5d458`); independent of the removed
  F-005/F-006.

## Resolved decisions

- Asset kinds are **discovered + overridden**, not a fixed enum (D-008).
- The constitution is a **global engineering-standards layer**, distinct from the
  operational system rules (R-001…) and shipped everywhere (D-009).
- Feature numbered **F-007**; F-005 (hooks) and F-006 (git) stay on backup
  branches and are rebuilt later on this architecture.
