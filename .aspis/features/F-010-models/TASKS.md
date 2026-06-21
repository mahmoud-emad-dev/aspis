# F-010 — Tasks

Sequenced, dependency-ordered. Each task ends with tests + a green gate (Windows is the gate of
record) + one atomic `aspis commit`. Re-verify each `file:symbol` before editing — the resolver code
moves. Two builders may work in parallel where `[P]` marks independent files; respect phase barriers.

Format: `T-NN [P?] [US?] — description (file paths)`.

## Phase 1 — Data foundation (catalog as SSoT). Blocked by: T-00 plan.

- **T-01 [P] [US2] — Canonical model catalog.** Create
  `src/aspis/data/catalog/config/model_catalog.yaml` — one entry per model, seeded from
  `.aspis/research/model-capability-seed.md`: `provider, family, context_window, scores{planning,
  implementation,review,reasoning}, cost_tier, pricing{in,out}, limits, confidence`. Header states it
  is the SSoT and that objective fields are refreshed from `opencode models --verbose`. **Done when:**
  yaml loads; a schema test asserts required keys + that no canonical id contains `/` (FR-001/FR-002).

- **T-02 [P] — Capability taxonomy.** Create `config/capabilities.yaml`: the stable capability list
  (planning, architecture, implementation, review, testing, debugging, research, orchestration,
  documentation, exploration) + a `capability → preferred tier` seed map (from the SPEC table /
  research). **Done when:** loads; test asserts every preferred tier is a real tier.

- **T-03 [P] — Provider registry.** Create `config/providers.yaml`: `providers.<id>:{detect, prefer,
  naming}` for the verified providers (anthropic, opencode, opencode-go, openrouter, minimax,
  github-copilot). Document the model-string naming per provider from
  `.aspis/research/runtime-model-detection.md`. **Done when:** loads; covered by a schema test.

- **T-04 — Correct the thin tier map.** Edit `config/models.yaml` so Claude tiers use stable aliases
  (`cheap: haiku`, `standard: sonnet`, `deep: opus`) and OpenCode tiers reference **canonical ids**
  (translated at render, T-09). **Done when:** existing `test_models.py` resolution tests still pass
  (FR-009). Dogfood-copy all four catalog config files to live `.aspis/config/` (matches F-011 T-06).

**Checkpoint:** the catalog + taxonomy + registry exist and load; tier map valid.

## Phase 2 — Foundational engine (blocking; all stories depend on it).

- **T-05 [US2] — Extend the adapter contract.** In `runtimes/base.py` add `detect() ->
  RuntimeInventory | None` (default `None`) and `model_string(canonical_id, inventory) -> str`
  (default: documented naming / identity). Define a small `RuntimeInventory` dataclass (installed,
  providers, available model strings). No `if runtime == "..."` in core (FR-003, Constitution #9).
  Add `detect_all()` to `runtimes/__init__.py`. Unit-test the contract members. Record **D-016** in
  `DECISIONS.md` + ARCHITECTURE adapter section (as F-011 did for D-015).

- **T-06 [US1] — OpenCode + Claude detection.** Implement `detect()` on `opencode.py` (read
  `auth.json` at the path from `opencode debug paths`/XDG; parse `opencode models` for available
  `provider/model` strings) and `claude.py` (read `~/.claude/settings.json`; known aliases). Implement
  `model_string()` for each (match canonical → an available detected string for a preferred connected
  provider; fall back to naming convention). Cross-platform, UTF-8, all failures → `None`/empty, never
  raise (FR-004/#12). Tests use **fixtures** (sample `auth.json`, `opencode models` text,
  `settings.json`) — no live runtime. Record **D-018**.

- **T-07 [US1] — Detection orchestrator + inventory.** New `src/aspis/inventory.py`:
  `build_inventory(root)` iterates `detect_all()` and writes generated
  `.aspis/state/runtime_inventory.json`; `load_inventory(root)` reads it (absent → `None`). Add
  `state/` to `.aspis/.gitignore`. Tests: build from fixtures → expected JSON; load when absent →
  graceful `None` (FR-006).

- **T-08 [US2] — Resolver + limits + precedence.** Extend `models.py`: `resolve(agent, runtime, *,
  project_config, inventory)` — tier→canonical (`models.yaml`/catalog) → `model_string()` vs
  inventory; enforce `limits` (FR-007); precedence **agent pin > project > global `~/.aspis` >
  catalog/tier** (FR-005); **fall back to existing `effective_model`** when inventory/catalog absent
  (FR-006/FR-009). Keep `effective_model` + its tests intact. Record **D-017**. Tests: full precedence
  matrix + fallback.

**Checkpoint:** detection writes a real inventory; resolver returns available strings with graceful fallback.

## Phase 3 — Story slices.

### US1 — Detect & route (P1) 🎯 MVP
- **T-09 [US1] — Wire adapters' render through the resolver.** In `claude.py`/`opencode.py`
  `render_agent`, load inventory once and call `resolve(...)` instead of bare `_resolve_model`.
  **Done when:** with the OpenCode fixture, a `deep` agent renders a real connected-provider string
  (e.g. `opencode-go/...`); Claude renders `opus`; with no inventory, output equals today's tier map
  (SC-001/SC-004). Existing render tests pass.
- **T-10 [US1] — CLI surface.** Add `aspis models` (per runtime: tier → resolved string + detected
  inventory) and call `build_inventory()` from `aspis doctor`. Test the command output.

### US3 — task_size = f(mode, capability) (P2)
- **T-11 [US3] — Effective task sizing.** Add `effective_task_size(mode, canonical_id)` to `models.py`
  (combine `modes.yaml` `task_size` with the catalog capability band). Wire the consumer
  (`scripts/planning/prereq_validate.py` or the planning skill reference). Test: cheap-capability <
  frontier under the same mode (SC-005, FR-008).

### US4 — Overrides (P2)
- **T-12 [US4] — Global + project overrides.** Ensure `resolve` honours a global `~/.aspis/config`
  preference layer below project config (project pin already works). Test the precedence (FR-005).

## Phase 4 — Decisions, docs, dogfood, polish.

- **T-13 — Record decisions & architecture.** Finalize D-016/D-017/D-018 in `DECISIONS.md`; update
  `.aspis/context/ARCHITECTURE.md` (new "Model intelligence" section) and add the **F-010 phase to
  `ROADMAP.md`** (Phase ~3.7). Note the future seams.
- **T-14 — `model:` → `tier:` rename (R-008, ONLY if user-approved).** If approved: rename the
  frontmatter key across all 11 agents + the parser (`catalog.py:parse_agent`) + tests, dogfood-
  regenerate. If not: leave a flagged note; catalog treats `model:` as a tier. **Confirm before doing.**
- **T-15 — Dogfood-regenerate + full gate sweep.** Regenerate `.claude`/`.opencode` from the catalog
  (never hand-edit); run the full gate green on Windows. Update `RECENT_CHANGES`/registry via the
  post-commit hook.

## Dependencies & execution order

- Phase 1 (data) and the Phase-2 contract (T-05) can start together; T-06/T-07 need T-05; T-08 needs
  T-05+T-01/T-02/T-04; T-09 needs T-08+T-06/T-07; T-10/T-11/T-12 need T-08; Phase 4 last.
- `[P]` tasks (T-01/T-02/T-03) touch different files — safe to parallelize across the two builders.
- Within a task: tests before/with implementation; never weaken a test to pass.

## Implementation strategy

- **MVP first**: Phase 1 + Phase 2 + US1 (T-09/T-10) — detection→available-string routing working,
  then validate before US3/US4.
- **Two-builder split** (you + the Windows Claude): one takes the data+catalog+resolver track
  (T-01,T-02,T-04,T-08), the other the adapter+detection track (T-03,T-05,T-06,T-07); converge at T-09.
  Coordinate on `models.py` (shared) — sequence T-08 before T-09.
- Commit per task via `aspis commit` (explicit paths, no `-A`, no AI attribution); gate green first.

## Build packets

`task-compile` turns each task into a self-contained packet at
`.aspis/features/F-010-models/tasks/T-NN.md` from `.aspis/templates/planning/TASK_PACKET.md` at build
start. (Detailed enough to execute directly in the meantime, matching the F-011 pattern.)

## Definition of done

All tasks committed per unit; full gate green on Windows + Linux; SC-001…SC-006 met; D-016/D-017/D-018
recorded; ROADMAP updated. Set the feature phase to `review`, then `merged` after the user confirms.
