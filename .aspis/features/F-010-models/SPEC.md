# F-010 — Model Intelligence Foundation · Specification

Mode: **production** — this is a load-bearing core part; built fully and correctly so all
later model work (tracing scores, cost/fallback routing, more runtimes/providers) is a
*pure addition*, never a core refactor.

> Research backing this spec (verified + seed): `.aspis/research/runtime-model-detection.md`
> (source-verified detection mechanics), `.aspis/research/model-capability-seed.md` (low-trust
> capability/cost seed), `.aspis/research/model-scores.chatgpt-raw.txt` (provenance).

## Goal

Give ASPIS a single, runtime-neutral source of truth for *models* — what each model is, what
it can do, what it costs — plus the ability to **detect** what a user actually has connected and
**resolve** every agent to the best available concrete model in the exact string its runtime
expects. Agents keep declaring a capability/tier; ASPIS decides the model. Adding a runtime,
provider, or model later is a data/plugin change, not a core change.

## Problem

Today's routing (`config/models.yaml` → `models.effective_model`) is real and tested, but it is
blind and brittle:

1. **No model knowledge.** There is no record of what a model *is* (provider, context window,
   capability, cost). Tier→id is a flat per-runtime guess with placeholder OpenCode ids that
   aren't even valid strings (`minimax-m3` vs the real `opencode-go/minimax-m3` / `minimax/MiniMax-M3`).
2. **Same model duplicated per runtime.** A model lives once per runtime column as a different
   string — a latent Single-Source-of-Truth violation that breaks the moment a second provider
   carries the same model (verified real: Opus 4.8 is `opencode/claude-opus-4-8` *and*
   `openrouter/anthropic/claude-opus-4.8`).
3. **No detection.** ASPIS cannot tell what runtime/providers/models a user has, so it cannot pick
   an *available* model or a sensible free-to-test default — it just emits a hardcoded id that may
   not exist on the user's machine.
4. **`task_size` is inert.** `modes.yaml` declares `task_size` but no code consumes it, and it is
   not informed by model capability (the "compensate for a weaker model with smaller tasks" idea).

Without this, ASPIS only works if the user manually pins valid model strings — the opposite of the
"works for any user, best available model, lowest cost" goal.

## Scope

In scope:
- **Canonical model catalog** (`src/aspis/data/catalog/config/model_catalog.yaml`) — the SSoT: each
  model once, with provider, family, context, capability scores, cost tier/pricing, hard limits,
  confidence. Seeded from the research; objective fields refreshed from detection.
- **Capability taxonomy** (`config/capabilities.yaml`) — the stable capability vocabulary +
  capability→preferred-tier seed.
- **Provider registry** (`config/providers.yaml`) — each provider: id, detection hook, preference
  order, model-string naming note.
- **Thin tier map** (`config/models.yaml`, existing) — `runtime + tier → canonical model id`,
  corrected to canonical ids (Claude via stable aliases).
- **Adapter contract extension** (`src/aspis/runtimes/{base,claude,opencode}.py`) — `detect()` and
  `model_string(canonical, inventory)` so detection + translation are per-runtime plugins.
- **Detection + inventory** — a detection orchestrator that asks each installed adapter to
  self-report, writing generated `.aspis/state/runtime_inventory.json` (gitignored, never edited).
- **Resolver** (`src/aspis/models.py`) — capability/tier → canonical → available runtime string,
  applying hard limits, with the full override hierarchy; graceful fallback when no inventory.
- **task_size = f(mode, model capability)** — make `task_size` engine-consumed.
- **CLI** — surface detection + resolution (`aspis models`, and detection wired into `aspis doctor`).
- Tests for every behaviour; `DECISIONS.md`/`ARCHITECTURE.md`/`ROADMAP.md` updated as-built.
- Regenerated `.claude/`/`.opencode/` only via dogfood, never hand-edited.

Out of scope (deferred, with their seam left open — see PLAN "Future seams"):
- **Evaluation/benchmark engine & evidence-based re-scoring** → Phase 4 (tracing) / Phase 5.
- **Cost optimizer, quota/rate-limit-aware fallback** → later; needs usage data. (Runtimes have
  native fallback we can lean on.)
- **Plan/quota/limit detection** → not exposed by either runtime natively; we detect provider
  *presence* only.
- **Detectors/adapters for absent runtimes** (cursor, gemini-cli, codex, aider) → each added as a
  plugin when actually targeted.
- **Multi-runtime "which runtime executes first"** → only relevant under a future headless commander.
- **Switching agents from tier-declaration to capability-declaration** → an R-008 flip enabled by
  this feature's data, but performed later (keep tiers now).

## User stories

### Story 1 — Detect & route to an available, correctly-spelled model (priority: P1) 🎯 MVP
- **Why first**: this is the core value — an agent file renders with a model string that actually
  exists on *this* user's machine, in the format the runtime requires.
- **Independent test**: with a fixture OpenCode `auth.json` + `opencode models` output, render an
  agent and assert the emitted model string is a real available string for a connected provider.
- **Acceptance scenarios**:
  1. **Given** OpenCode is connected with provider `opencode-go`, **when** an agent with `deep`
     tier is rendered, **then** the resolver emits a real available `opencode-go/...` (or other
     connected-provider) string for the canonical deep model — not a placeholder.
  2. **Given** Claude Code, **when** the same agent renders, **then** it emits the stable alias
     (`opus`) for the deep tier.
  3. **Given** no detection has run / runtime not installed, **when** an agent renders, **then** the
     resolver gracefully falls back to the static tier map (no crash) — works for any user.

### Story 2 — Model catalog as the single source of truth (priority: P1)
- **Why**: every later capability hangs off one canonical record per model.
- **Independent test**: a model referenced by two runtimes resolves from one catalog entry; editing
  one field changes both renders; no model string is duplicated as canonical.
- **Acceptance scenarios**:
  1. **Given** a canonical model carried by OpenCode and Claude, **when** its capability/cost is
     read, **then** it comes from one `model_catalog.yaml` entry, translated per runtime.

### Story 3 — task_size scales with mode AND model capability (priority: P2)
- **Why**: a weak model under a strict mode should get smaller tasks; a strong model under a loose
  mode can take larger ones.
- **Independent test**: `effective_task_size(mode, model)` returns a smaller size for a low-capability
  model than a frontier one under the same mode.
- **Acceptance scenarios**:
  1. **Given** `production` mode, **when** the model is `cheap`-capability vs `frontier`, **then**
     effective task size is smaller for the cheap model.

### Story 4 — Overrides for any user/project (priority: P2)
- **Why**: a user/project must be able to steer routing without touching code.
- **Independent test**: a project `models:`/`agents:` override and a global `~/.aspis` preference
  change resolution in the documented precedence.
- **Acceptance scenarios**:
  1. **Given** a project pins `reviewer` to a model id, **when** rendered, **then** that id wins
     over the tier map (existing behaviour preserved).
  2. **Given** a global preference (e.g. prefer-free), **when** resolving, **then** it is honoured
     below project config and above catalog defaults.

## Requirements

- **FR-001**: A canonical model catalog MUST define each model exactly once (provider, family,
  context, capability scores, cost tier/pricing, hard limits, confidence).
- **FR-002**: The system MUST NOT store a runtime-specific model string as the canonical id; runtime
  strings MUST be derived per `(runtime, provider)`.
- **FR-003**: Each runtime adapter MUST provide `detect()` (what providers/models are available) and
  `model_string(canonical, inventory)` (canonical → the runtime's exact string), with no
  `if runtime == "..."` in core code (Constitution #9).
- **FR-004**: Detection MUST write a generated `.aspis/state/runtime_inventory.json`, never
  hand-edited, gitignored, resolved cross-platform (Constitution #12; use `opencode debug paths` /
  documented Claude paths).
- **FR-005**: The resolver MUST map an agent's capability/tier → canonical model → an *available*
  runtime string, honouring this precedence: explicit agent pin > project config > global user
  config > catalog/tier default.
- **FR-006**: The resolver MUST degrade gracefully — with no inventory or an unknown tier it MUST
  fall back to the static tier map (today's behaviour), never crash.
- **FR-007**: Hard limits MUST be enforceable — a model whose `limits` ceiling is below a task's
  requirement MUST NOT be selected for it (bump or refuse).
- **FR-008**: `task_size` MUST be computed as a function of mode and model capability and be
  consumable by the engine/planning, not inert data.
- **FR-009**: Every existing model-resolution behaviour and test MUST keep passing (the working,
  tested router is preserved and extended, not replaced).
- **FR-010**: Agents MUST keep declaring a tier (R-007); capability data MUST exist so a later flip
  to capability-declaration is additive.
- **FR-011**: A free-to-test default MUST be selectable so a new user can run end-to-end at ~$0.

## Feature rules & style

- **R-003 / Constitution "Automation before Intelligence"**: detection/resolution are deterministic
  code, never an agent.
- **R-007 Pinned tiers**: agents declare cheap/standard/deep; no silent expensive inheritance.
- **R-008 Human gate**: model-routing/architecture decisions (PLAN "Decisions needing approval")
  need sign-off; this spec records them.
- **Constitution #2/#3/#4/#9/#12**: Plugin First, Single Source of Truth, Config over Code, No
  Special Cases, Portable by Default — the design is judged against these.
- **Generated Artifacts (#8)**: inventory + regenerated runtime dirs are generated, never edited.

## Key entities

- **Canonical model**: one record per real model — `provider`, `family`, `context_window`,
  `capabilities`/`scores` (planning, implementation, review, reasoning), `cost_tier`, pricing,
  `limits`, `confidence`.
- **Provider**: a source of models (anthropic, opencode, opencode-go, minimax, openrouter, …) with a
  detection hook and a model-string naming convention.
- **Runtime inventory**: generated per-machine snapshot — installed runtimes, connected providers,
  available model strings.
- **Tier**: cost/capability dial (cheap/standard/deep) an agent declares; resolves through the catalog.
- **Capability**: stable vocabulary (planning, architecture, implementation, review, testing,
  debugging, research, orchestration, documentation, exploration) an agent requires.

## Success criteria

- **SC-001**: Rendering an agent on a machine with OpenCode connected emits a model string present
  in that machine's `opencode models` output (no placeholder/invalid id). 
- **SC-002**: A model carried by two runtimes is defined once; no canonical id contains a provider
  prefix.
- **SC-003**: Adding a new model/provider is a data-only change; adding a new runtime is a new
  adapter (one plugin) with zero edits to detect/resolve core (Cost-of-Change ≤ 3 files).
- **SC-004**: With no inventory present, all existing resolution tests still pass (graceful fallback).
- **SC-005**: `effective_task_size` returns a strictly smaller size for a cheap-capability model than
  a frontier model under the same mode.
- **SC-006**: Full gate green on **Windows** (gate of record) and Linux; every behaviour change tested.

## Assumptions

- The dogfood user is on **OpenCode** with providers: OpenCode Zen, OpenCode Go, OpenRouter, MiniMax
  Token Plan, GitHub Copilot (verified from `opencode auth list`). Claude Code support is built for
  generality even though the dogfood machine routes through OpenCode.
- Seed capability scores are low-trust placeholders; correctness comes later from tracing.
- Objective facts (context window, pricing) are sourced from `opencode models --verbose` / models.dev
  at build time rather than trusting the seed numbers.

## Clarifications

### Session 2026-06-21
- Q: Build the lean version or the full core now? → A: **Full correct core now**, architected so the
  future is purely additive (no big refactor later).
- Q: Capability-based or tier-based agent interface? → A: **Capability-aware routing core, but keep
  the tier as the agent-facing dial now**; capability-declaration is a later additive flip.
- Q: Detect plans/quota? → A: **No** — not exposed natively; detect provider/credential *presence*.
- Q: Where does research live? → A: `.aspis/research/`.

## Open questions

- **`model:` → `tier:` agent-frontmatter rename** (carried from F-011 T-12d): the frontmatter key
  holds a tier but reads like a vendor pin. Renaming touches all 11 agents + the parser (R-008).
  Recommended yes (clarity before the catalog builds on it) — but it is the user's call; see PLAN.
