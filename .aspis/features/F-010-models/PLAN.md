# F-010 — Implementation Plan

## Summary

Build a runtime-neutral **model intelligence** layer on top of the existing (working, tested)
`models.effective_model` router. One canonical catalog defines each model once; each runtime adapter
gains `detect()` + `model_string()` so detection and per-`(runtime,provider)` translation are
plugins, not core branches; a resolver maps an agent's capability/tier → canonical model → an
*available* runtime string with graceful fallback; and `task_size` becomes a function of mode ×
model capability. Agents keep declaring a tier. The design's whole job is to make every later model
feature (tracing scores, cost/fallback, new runtimes/providers) a data/plugin add — never a refactor.

## Technical context

- **Language / version**: Python 3.11+ (matches repo).
- **Key dependencies**: PyYAML (already used), stdlib `subprocess`/`json`/`pathlib`. No new deps.
- **Storage / interfaces**: catalog YAML under `src/aspis/data/catalog/config/`; generated
  `.aspis/state/runtime_inventory.json`; reads OpenCode `auth.json` + `opencode` CLI, Claude
  `~/.claude/settings.json`.
- **Testing**: pytest, with fixtures for `auth.json` / `opencode models` output / `settings.json`
  so detection is tested without a live runtime.
- **Project type / structure**: engine in `src/aspis/`; data in the catalog; per-runtime logic on
  the adapters (extends the F-011 contract). Live `.aspis/config/` copies are dogfood-regenerated.
- **Constraints**: cross-platform (Constitution #12) — never assume a path/codec; resolve OpenCode
  paths via `opencode debug paths`, Claude via documented `~/.claude` paths. Must not regress the
  existing resolution tests.

## Gate check

- [x] **R-001 Scope** — changes stay within SPEC in-scope paths.
- [x] **R-002 Gates** — `ruff format --check`, `ruff check`, `pytest` are the bar; green on Windows.
- [x] **R-005 Tests-as-spec** — detection, resolution, limits, task-sizing pinned by tests.
- [x] **R-009 Human gate** — model-routing/architecture decisions flagged in "Decisions needing approval".

## Components

**Data (catalog — `src/aspis/data/catalog/config/`)**
- `model_catalog.yaml` — **SSoT**. `models.<canonical-id>: {provider, family, context_window,
  scores:{planning,implementation,review,reasoning}, cost_tier, pricing:{in,out}, limits, confidence}`.
  Seeded from `.aspis/research/model-capability-seed.md`; objective fields refreshed from detection.
- `capabilities.yaml` — capability vocabulary + `capability → preferred tier` seed.
- `providers.yaml` — `providers.<id>: {detect, prefer, naming}` (registry + preference order).
- `models.yaml` *(existing, kept thin)* — `runtime → tier → canonical id`. Corrected: Claude uses
  aliases (`deep: opus`), OpenCode uses canonical ids (translated at render).

**Adapter contract (`src/aspis/runtimes/`)** — extends the F-011 `RuntimeAdapter`:
- `detect() -> RuntimeInventory | None` — is this runtime installed? which providers/models are
  available? (OpenCode: read `auth.json` + parse `opencode models`; Claude: read `settings.json` +
  known aliases). Returns `None` when not installed.
- `model_string(canonical_id, inventory) -> str` — translate a canonical id into the exact string
  this runtime/provider wants, by **matching against the detected available strings** (not building
  by a fragile rule); falls back to a documented naming convention if no inventory.
- Claude/OpenCode implement both; the registry exposes `detect_all()`.

**Detection orchestrator (`src/aspis/inventory.py` — new)**
- `build_inventory(root) -> Inventory`: iterate installed adapters' `detect()`, merge, write
  `.aspis/state/runtime_inventory.json` (generated, gitignored). `load_inventory(root)`: read it
  (returns empty/None if absent → graceful fallback).

**Resolver (`src/aspis/models.py` — extend existing `effective_model`)**
- `resolve(agent, runtime, *, project_config, inventory) -> str`: tier (or capability→tier via
  `capabilities.yaml`) → canonical id (via `models.yaml`/catalog) → `model_string(...)` against the
  inventory; apply `limits`; honour precedence **agent pin > project > global ~/.aspis > catalog/tier**;
  **fall back** to today's `effective_model` path when inventory/catalog absent (FR-006/FR-009).
- `effective_task_size(mode, canonical_id) -> str`: combine `modes.yaml` `task_size` with the
  model's capability band → effective size (FR-008).

**CLI (`src/aspis/commands/`)**
- `aspis models` — show, per runtime, each tier → resolved model string + the detected inventory
  (diagnosis). `aspis doctor` — run `build_inventory()` so detection happens at a natural touchpoint.

**Wiring** — `claude.py`/`opencode.py` `render_agent` call the resolver (load inventory once) instead
of the bare `_resolve_model`; existing tier→id behaviour preserved when no inventory.

## Data flow

```
agent frontmatter (tier)            modes.yaml (task_size)
        │                                   │
        ▼                                   ▼
   capabilities.yaml ── tier ──► models.yaml ──► canonical id ──► model_catalog.yaml (facts/limits)
                                                      │
                                runtime_inventory.json (detected available strings)
                                                      │
                              adapter.model_string(canonical, inventory)
                                                      ▼
                          concrete runtime string written into the rendered agent
                          (opencode-go/minimax-m3 · minimax/MiniMax-M3 · opus · …)
```

## Steps

| Step | Files | Gate |
|------|-------|------|
| 1. Catalog + taxonomy + provider registry (data, seeded) | `data/catalog/config/{model_catalog,capabilities,providers}.yaml` | yaml loads; schema test |
| 2. Correct thin tier map to canonical ids/aliases | `data/catalog/config/models.yaml` | existing resolution tests pass |
| 3. Adapter contract: `detect()` + `model_string()` | `runtimes/{base,claude,opencode}.py` | unit tests per member |
| 4. Detection orchestrator + inventory (gitignored) | `inventory.py`, `.aspis/.gitignore` | detection tests w/ fixtures |
| 5. Resolver + limits + precedence (extend `effective_model`) | `models.py` | resolution + fallback tests |
| 6. `effective_task_size(mode, model)` | `models.py` (or `sizing.py`) | sizing test |
| 7. CLI: `aspis models` + detect in `doctor` | `commands/models.py`, `commands/doctor*` | CLI test |
| 8. Wire adapters' render through the resolver | `runtimes/{claude,opencode}.py` | render tests: real strings |
| 9. Record D-016..D-018; ARCHITECTURE + ROADMAP; dogfood-regenerate | `.aspis/context/**`, `.claude/**`, `.opencode/**` | full gate |

## Verification

```bash
.venv/bin/ruff format --check . && .venv/bin/ruff check . && .venv/bin/pytest -q
# plus a manual smoke on the dogfood machine:
opencode auth list && opencode models | head     # confirms detection inputs
.venv/bin/aspis models                            # shows resolved tier→model per runtime
```

## Risks & rollback

- **Risk**: seed scores/pricing are wrong → **Mitigation**: tag `confidence`, refresh objective
  fields from `opencode models --verbose`; scores are advisory until tracing (Phase 4/5).
- **Risk**: detection fragile across OS/versions → **Mitigation**: resolve paths via `opencode debug
  paths`; wrap all detection so failure yields *no inventory* (graceful fallback), never an error.
- **Risk**: regressing the working router → **Mitigation**: FR-009 — keep `effective_model` and its
  tests; the resolver wraps/extends it, fallback path is the old path.
- **Risk**: over-build (the 11-layer trap) → **Mitigation**: out-of-scope list is enforced; only the
  seams (not the end-features) are built now.
- **Rollback**: the feature is additive — new files + extended functions behind fallback. Reverting
  the branch restores the static tier map unchanged.

## Future seams (built open now, filled later — no core change required)

- **Tracing scores** (Phase 4): writes into `model_catalog.yaml` `scores`/`confidence` — fields exist.
- **Self-improvement re-scoring** (Phase 5): re-tunes those scores within bounds.
- **Cost optimizer / quota-aware fallback**: a pluggable *selection strategy* in the resolver; today
  one strategy (capability+tier+availability). Runtimes' native fallback (Claude `--fallback-model`)
  can be leaned on first.
- **New runtime** (gemini-cli/codex/cursor): a new adapter implementing `detect()`/`model_string()` —
  discovery already finds it; zero core edits.
- **New provider/model**: a `providers.yaml` / `model_catalog.yaml` entry — data only.
- **Capability-declaration agents**: the resolver already routes by capability; flipping the agent
  frontmatter is a later additive change reading `capabilities.yaml`.

## Decisions needing approval (R-008 — record in DECISIONS.md during build)

- **D-016 — Canonical model catalog is the SSoT; runtime strings are derived per (runtime,provider).**
  No canonical id carries a provider prefix; translation lives on the adapter.
- **D-017 — Capability-aware routing core, tier kept as the agent dial.** R-007 preserved; agents
  declare a tier; capability data exists for a later additive flip.
- **D-018 — Detection scope = provider/credential presence, not plan/quota** (not natively exposed);
  output is a generated, gitignored inventory; cost/quota-aware routing deferred.
- **Open (user's call): `model:` → `tier:` agent-frontmatter rename** — recommended (clarity before
  the catalog builds on it; touches 11 agents + parser). If approved it becomes T-11; if not, leave a
  flagged note and the catalog treats `model:` as a tier.
