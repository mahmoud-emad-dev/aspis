# ASPIS — Architecture

**As-built**, kept lean — what ASPIS actually is today, and the contract build and
review compare against. For the stable design intent (the *why* and target shape that
planning reads), see [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md). When the
architecture changes, update this file first, record the decision in `DECISIONS.md`,
then change the code.

## Three layers

1. **Factory repo** (this repo) — where the product is developed. Everything here
   is product: the engine, the catalog, the tests.
2. **Global install** — the `aspis` CLI and engine installed on a machine.
3. **Target project** — a project ASPIS manages. It receives two things:
   - `.aspis/` — the **portable brain** (context, index, features, templates,
     scripts, rules, etc). Tool-neutral; the durable memory.
   - `.opencode/` · `.claude/` — **generated runtime** assets for each AI coding
     tool. Replaceable; rebuilt from the catalog.

## Catalog → runtime (the core mechanism)

One **runtime-neutral catalog** under `src/aspis/data/catalog/` is the single
source. Each asset is a superset (richer than any one runtime). A per-runtime
**adapter** translates an asset and emits only what that runtime supports,
silently dropping the rest — it never errors. So OpenCode gets a `permission`
block and `mode`; Claude gets a `tools` list and no `mode`.

Selection is data: **profiles** list which catalog assets a project receives.
`init` plans the export (dry-run) and writes it; nothing about *which* assets
ship is hard-coded.

**Asset kinds are data, not an enum (D-008).** One registry (`assetkinds.py`) is
the single source for how each kind is placed: any kind a profile names defaults
to a brain copy, and only the rendered/per-runtime kinds (`agents`, `commands`,
`skills`) carry an override. So adding a new brain kind is purely additive — drop
a `catalog/<kind>/` dir and list it in a profile, with **no core edit**. Whether a
runtime accepts a kind is the adapter's `supports(kind)` **capability**, so export
never name-checks a runtime. Cost-of-change for a new kind, runtime, or profile is
~0 core files — the discipline the architecture constitution enforces.

**Runtime identity is the adapter's, never a literal (D-015).** The adapter is the
single source of a runtime's on-disk dir (`runtime_dir`, e.g. `.claude`), its root-guide
file (`root_guide`, e.g. `CLAUDE.md`, or `None`), and whether it expresses an agent
`mode` (`supports_mode`). `detect.py`, `assetkinds.py`, and `promotion.py` ask the
adapter; init emits a root guide for any runtime that declares one; lead promotion
targets `runtimes.mode_runtime()`. "Which runtimes exist" has one source — **profiles**
(targets) + **`available_runtimes()`** (discovery); there is no `constants.RUNTIMES`.

## Model intelligence

**Models are canonical; runtime strings are derived (D-016).** A model is defined once in
`catalog/config/model_catalog.yaml` by a provider-neutral canonical id with its facts
(provider, context, capability scores, cost tier, hard limits, confidence).
`capabilities.yaml` (capability→tier) + `providers.yaml` (provider naming/preference) carry
the taxonomy; `models.yaml` maps tier→canonical id only — a cross-check test forbids drift.

**Detection is per-runtime and records presence, not plan/quota (D-018).** Each adapter's
`detect()` returns a `RuntimeInventory` of connected providers + available model strings, or
`None` when the runtime is absent — OpenCode reads `auth.json` keys (never secret values) and
`opencode models`; Claude reads `settings.json` presence and the durable alias set. The
registry's `detect_all()` orchestrator (via `inventory.build_inventory`) writes generated
`.aspis/state/runtime_inventory.json` (gitignored). All probes are cross-platform and never
raise (Constitution #12); a Windows `.CMD` shim is run through the shell.

**One resolver routes; tier stays the agent dial (D-017).** `models.resolve()` applies the
precedence **agent pin > project > global `~/.aspis` > tier map** to a canonical id, bounds it
by the catalog's hard `limits` (escalating to the cheapest model that clears a task), then
calls the adapter's `model_string()` against the inventory to emit the exact runtime string.
With no inventory it returns the canonical id — byte-identical to today's render, so the
committed dogfood stays reproducible and any user works without detection. `task_size` is now
`effective_task_size(mode, model)`; `aspis models` surfaces the resolution and `aspis doctor`
refreshes the inventory. Capability scores carry a `confidence` — the seam the Phase-4 tracing
spine fills. No core change is needed to add a model/provider (data) or a runtime (a new adapter).

## Agents

- **Agent = thin instruction + skills.** The instruction holds identity, rules,
  and skill references; the intelligence lives in skills (R-006).
- **Roster:** Project Lead (entry/intelligence), Planning, Build, Reviewer, System
  (primaries); Research, Test, Fix (support); General Builder + Committer (workers);
  Project Explorer (read-only helper).
- **Modes & cost:** every agent has a pinned model tier (cheap/standard/deep).
  Leads reason (deep), workers execute (cheap/standard).
- **Promotion:** every agent ships `mode: subagent`; only the Project Lead is
  primary. Bootstrap promotes four leads (system, planning, build, reviewer) →
  exactly five primaries.

## Ownership boundary

The **System Lead** is the only lead that may modify the runtime (`.opencode/`,
`.claude/`) and protected brain areas. The other leads own the shared brain
(context, features, plans, reports). This keeps the operating layer governed.

## Context pyramid

Agents retrieve knowledge on demand instead of holding it all:
`FILE_REGISTRY.yaml` (locate) → `CODE_MAP.md` (understand a file without reading it)
→ `CURRENT_STATE.md` + `RECENT_CHANGES.md` (live state). All generated by the
context scripts under `.aspis/scripts/context/`.

## Quality

Deterministic gates (`ruff format`, `ruff check`, `pytest`) are the bar (R-002).
Tests are spec (R-005). One writer per branch; only the committer commits (R-004).

## Hooks

Two deterministic surfaces (no LLM) over one shared core in `.aspis/scripts/hooks/`,
driven by data in `config/hooks.yaml` (D-010). The git **commit boundary**
(`pre-commit`/`commit-msg`/`post-commit`, installed in `.git/hooks/`) and the
per-runtime **tool-use boundary** (Claude `settings.json`, OpenCode plugin, adapter-
emitted) share one scope/secret/junk/gitignore implementation. They are **non-blocking
by default** (`enforcement: warn`): auto-fix what is safe and report the rest; one
`enforcement: block` switch turns the same checks into walls. They never run the suite.

## Git

One commit authority. The **committer** is the only agent that commits, and it commits
through **`aspis commit`** (D-011): stage the explicitly named paths (never `-A`),
compose the message with `scripts/git/compose.py`, then `git commit` so the F-006 hooks
fire. The split is **agent composes · tool builds the message · hooks enforce** —
`pre-commit` auto-fixes and checks, `commit-msg` validates the convention, `post-commit`
refreshes the brain. The message rules live once in `commit-convention.yaml`; the
composer reuses the hook's validator, so there is a single source. Pushing, PRs, and
worktrees are deferred.

## Load-bearing principles

Four ideas the whole design rests on:

1. **Determinism is the cost lever.** Shrink what the model must figure out — tight
   task, rich context, conformant template — and the cheapest model is correct.
2. **Evidence is the currency.** Each phase emits a report/result tied to a commit;
   later actors *consume* it instead of redoing work.
3. **Machine-checked invariants hold; prose-asserted ones rot.** Every "X must match
   Y" becomes a test or generated code, never a doc promise.
4. **Capture now, derive later.** Record the useful trace cheaply now; the
   intelligence that reads it comes later — reserve the seam, don't build the far
   layer early.
