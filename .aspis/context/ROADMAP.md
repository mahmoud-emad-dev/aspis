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
- **Phase 3 — Default production system.** ✅ Done. The plan → build → review loop
  driven through the leads: the task-packet contract, **working modes** as data
  (`modes.yaml`, vibe/MVP/production with a project default in `project.yaml`,
  settable via `aspis mode`, `/plan --mode`, or inferred by the Project Lead), the
  `/plan /build /review /system /status` commands, the planning scripts
  (feature-scaffold, task-compile, prereq-validate), workflow docs per track, the
  `plan-critic` check, data-driven model routing (project override + per-agent pin),
  and a catalog consistency guard. Mode is a *ceiling*, not a floor.
- **Phase 3.4 — Extensibility core + constitution (F-007).** ◐ In progress. Make
  the engine grow by adding files, not editing core: asset kinds are a data registry
  (a new kind defaults to a brain copy, zero core edits) and runtimes declare a
  `supports(kind)` capability instead of being name-checked (D-008). Ship the
  architecture constitution — the global engineering-standards layer — and wire it
  into the planning, build, and review leads (D-009). Done before more features so
  the next ones are drop-ins.
- **Phase 3.5 — Deterministic hooks (F-005).** ⏳ Deferred, rebuilt on F-007. A first
  cut shipped runtime "guards" but was overengineered (one kind forced edits across
  six core files); it is preserved on `backup/F-005-guards` and rebuilt as real
  **hooks** on the new asset-kind + capability core. Goal unchanged: enforce
  scope-guard, protect-paths, commit-discipline, gate-before-done, and prereq-gating
  as walls the model can't cross — turning R-001/R-002/R-004 into machine-checked
  invariants.
- **Phase 3.6 — Git subsystem (F-006).** ⏳ Deferred, design owned by the user. A
  first cut is preserved on `backup/F-006-git`; the full git system (hooks vs. a
  committer-triggered commit tool, the pre/on-commit/post split, agent-role vs.
  automatic) is specified later and rebuilt on the F-007 core.
- **Phase 4 — Tracing spine.** ⏳ Reserved. One writer keyed by `run_id`,
  append-only JSONL truth, a normalized store; cost + quality measurable per
  feature/agent/model. (Capture runs in parallel with Phase 3.)
- **Phase 5 — Self-improvement.** ⏳ Reserved. Detect repeated patterns → propose
  assets → human gate → bounded apply (config/scope/model-tier only, never weaken
  gates/tests/rules) → measure effect.
- **Phase 6 — Surfaces.** ⏳ Reserved. A cockpit dashboard that is a thin view over
  a stable read-model of the engine — never a fork of it.

## Open design items (resolve before they're built)

- **Working-mode mechanics.** ✅ Resolved. Knobs live in `modes.yaml`; vibe keeps a
  light single-pass review; mode is a ceiling not a floor; resolution is request >
  active feature > project default > `modes.yaml`.
- **Project-plan track.** The deep project-level planning flow (heavier than a
  feature) is still to be designed; for now a project decomposes into features.
- **Delegation depth.** Keep to ~two effective levels (a directly-selectable lead →
  its workers); deep nesting can stall in some runtimes. The five promoted primaries
  exist precisely so flows stay shallow.
- **On-demand profiles** (role profiles like data-analyst, automation) and a global
  cross-project learning brain — both later layers, not now.
