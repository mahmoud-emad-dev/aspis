# ASPIS — Roadmap

Where the system is going and where it is now. Phases are ordered; each ships
deterministic core before intelligence. Adapted from the older ASPS refactor plan.

## North star

A deterministic software-production factory where the **cheapest sufficient model
runs correctly** because the work is shrunk by structure: tight tasks, rich
context, conformant templates, deterministic gates, and scoped review — with every
run traced so the system measures and improves itself.

## Phases

- **Phase 0 — Engine spine.** ✅ Done. Catalog superset + per-runtime adapters,
  profiles, `init`/`bootstrap` lifecycle, deterministic gate, brain scaffold,
  context scripts (registry, code-map, state).
- **Phase 1 — Lead roster.** ✅ Done. 11 agents (5 primaries + support + workers),
  their skills and plan templates, subagent-by-default + bootstrap promotion.
- **Phase 2 — Live factory + governance.** ◐ In progress. Dogfood (ASPIS runs on
  itself); foundation docs (identity, architecture, decisions, this roadmap);
  system rules + the three rule layers.
- **Phase 3 — Default production system.** ⏳ Next. The live planning → build →
  review → test loop driven through the leads, with **working modes**
  (vibe / MVP / production), a command surface (`/plan` `/build` `/review`
  `/system` `/status`), and the planning deterministic tools (feature scaffold,
  task compile).
- **Phase 4 — Tracing spine.** ⏳ Reserved. One writer keyed by `run_id`,
  append-only JSONL truth, a normalized store; cost + quality measurable per
  feature/agent/model. (Capture runs in parallel with Phase 3.)
- **Phase 5 — Self-improvement.** ⏳ Reserved. Detect repeated patterns → propose
  assets → human gate → bounded apply (config/scope/model-tier only, never weaken
  gates/tests/rules) → measure effect.
- **Phase 6 — Surfaces.** ⏳ Reserved. A cockpit dashboard that is a thin view over
  a stable read-model of the engine — never a fork of it.

## Open design items (resolve before they're built)

- **Working-mode mechanics.** Direction is set (vibe = throwaway, MVP = promotable,
  production = default/cheapest-correct) but the concrete knobs are undecided —
  settle with the user before Phase 3 wires them.
- **Delegation depth.** Keep to ~two effective levels (a directly-selectable lead →
  its workers); deep nesting can stall in some runtimes. The five promoted primaries
  exist precisely so flows stay shallow.
- **On-demand profiles** (role profiles like data-analyst, automation) and a global
  cross-project learning brain — both later layers, not now.
