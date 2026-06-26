# F-016 Research — System Lead: Configuration & Runtime Management

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Phase:** research
> **Compiled:** 2026-06-26 · **Sources verified through:** 2026-06-26
> **Scope:** the complete configuration and runtime-management system the
> system-lead owns. Every file, every command, every drift point.

This is the spec the system-lead's `config-management`, `system-validation`,
and `system-repair` skills consume. It is grounded in the live files in
`.aspis/config/` and the scripts under `.aspis/scripts/`. Anything the
code does not yet do is flagged **MISSING**.

---

## 0 · Source map (so the spec is auditable)

| Source | Path | Why it matters |
|---|---|---|
| Live agent (OpenCode frontmatter) | `.opencode/agents/system-lead.md` | The truth system-lead ships with |
| Local agent spec (with gaps) | `local/agents/system-lead.md` | The fuller description; flag drift |
| Tier-1 config | `.aspis/config/{project,models,agent-models}.yaml`, `purposes.json` | User-editable routing & registry data |
| Tier-2 policy | `.aspis/config/policy/{modes,hooks,constitution-checks,commit-convention,capabilities,agent-capabilities}.yaml` | System behaviour, rarely edited |
| Tier-3 reference | `.aspis/config/reference/{providers,model_catalog}.yaml`, `.runtime-inventory.json` | Machine data, do not edit |
| Decisions spine | `.aspis/context/DECISIONS.md` (D-001 … D-019) | Why each design is the way it is |
| Rules | `.aspis/rules/system-rules.md` (R-001 … R-009), `.aspis/rules/architecture-constitution.md` | The non-negotiables |
| Hook scripts | `.aspis/scripts/hooks/{precommit,commitmsg,postcommit,secret_scan,scope,cleanup,gitignore,install,runtime_guard,_config,_git}.py` | What actually runs at the boundary |
| Git helper | `.aspis/scripts/git/compose.py` | The single commit-message builder |
| Brain context | `.aspis/scripts/context/{build_state,build_registry,build_code_map,record_changes,update,_common}.py` | The refresh pipeline |
| Agent architecture | `local/AGENT-SYSTEM-ARCHITECTURE.md` (synthesis) | The plan→build→review contract |
| System-agent research | `.aspis/features/F-016-agent-system-architecture/Research/system-agent-tooling.md` | Prior research, this spec builds on it |
| Old ASPS vision | `local/ASPS/.asps/context/ASPS_OVERVIEW.md` | Origin story; some terminology carried over |
| File registry | `.aspis/index/FILE_REGISTRY.yaml` | Every file and its purpose (used to detect orphans) |

**Versioned by the catalog** (D-016): canonical model ids are pinned in
`reference/model_catalog.yaml`; a `.runtime-inventory.json` is captured
each `aspis models --sync`; the inventory is git-ignored, the catalog is not.

---

## 1 · CONFIGURATION FILES — complete map

The system-lead owns the **whole** `.aspis/config/` tree (D-003: "the only
lead permitted to modify protected system areas"). Every file in the tree
falls into one of three tiers, and the rule for editing it is encoded in its
tier.

### 1.1 Tier 1 — `project.yaml`, `models.yaml`, `agent-models.yaml`, `purposes.json`

These are user-editable. Touching them is normal product work; touching the
*meaning* of one of them is a system-lead job.

#### `project.yaml`

| Aspect | Value |
|---|---|
| Path | `.aspis/config/project.yaml` |
| Format | YAML |
| Purpose | Per-project overrides for **build mode** and **model routing**; everything below the global `models.yaml` tier map |
| Read by | `aspis models --apply` (resolver), planning-lead's `planning-intake` (reads `mode`) |
| Written by | human (via editor) or `aspis init`/`aspis models --apply` (programmatically); system-lead authors under a `/SYS` scope, committer commits |
| R-008 gated? | **Yes** — changes to a project's mode or to model routing for *this project* are routing changes (R-008). The file itself is editable; the *intent* needs approval. |
| Validation | `aspis models` (syntax + resolution), `aspis validate-runtime` (registry consistency) |
| Drift detection | `aspis models --sync` regenerates `agent-models.yaml`; if the regenerated file differs, that's drift. `aspis doctor` flags stale inventory. |

Precedence (most-specific wins), per the header comment in the live file:

```
runtimes.<runtime>.agents.<name>      # one agent, one runtime  (most specific)
agents.<name>                         # one agent, every runtime
runtimes.<runtime>.models.<tier>      # a tier, one runtime
models.<runtime>.<tier>               # (flat form, same as above)
config/models.yaml                    # the global tier map
```

A value may be a **TIER** (`cheap` / `standard` / `deep`) or a **concrete
model id** — either a canonical catalog id (`deepseek-v4-pro`,
`minimax-m3`, `glm-5.1`) or a runtime-native alias (`opus`, `sonnet`,
`haiku`). Detection translates a canonical id to the connected
provider's exact string.

#### `models.yaml`

| Aspect | Value |
|---|---|
| Path | `.aspis/config/models.yaml` |
| Format | YAML |
| Purpose | The **global** `runtime → tier → canonical model id` map. The default `project.yaml` falls back to. |
| Read by | resolver on every `aspis models --apply`; documented in `config/README.md` as "the file you change to move *all* agents on that tier" |
| Written by | system-lead (under `/SYS` scope); the `aspis` CLI does not auto-write it — that's the difference between **global** and **project** |
| R-008 gated? | **Yes** — global routing changes. R-008 says "no automated rewrites" of routing. |
| Validation | `aspis models` validates all four canonical ids exist in `reference/model_catalog.yaml` |
| Drift detection | `aspis models --available` lists every detected model; if `models.yaml` names a model the user no longer has, the resolver falls back to the closest available (and reports a warning). |

#### `agent-models.yaml`

| Aspect | Value |
|---|---|
| Path | `.aspis/config/agent-models.yaml` |
| Format | YAML |
| Purpose | Per-`{runtime, capability, agent}` overrides. The "fine-grained" layer; the file you open when one agent is mis-routed. |
| Read by | resolver (most-specific) → `aspis models --apply` bakes the resolved id into the live agent file's `model:` frontmatter |
| Written by | **Generated** by `aspis models --sync` from `reference/model_catalog.yaml` × `policy/agent-capabilities.yaml` × `policy/capabilities.yaml` × `.runtime-inventory.json`; then **human-edited** for pin overrides; then system-lead commits under `/SYS` |
| R-008 gated? | **No** when the sync regenerates the default block; **Yes** when the human pins override a tier pin on a single agent (that is a routing decision per agent). |
| Validation | Every agent's resolved model must be in `model_catalog.yaml` AND in `.runtime-inventory.json`; otherwise `aspis models --apply` fails with the missing id. |
| Drift detection | `aspis models --sync` re-detects and writes a fresh `agent-models.yaml`; a `git diff` on the file shows the live drift. |

The file carries a "ranked menu" comment block at the top — every model's
score per capability — so the user has evidence for the pick and can
override with confidence.

#### `purposes.json`

| Aspect | Value |
|---|---|
| Path | `.aspis/config/purposes.json` |
| Format | JSON |
| Purpose | File-purpose registry: `files` (exact relpath → purpose), `names` (basename → purpose), `patterns` (glob → purpose). Extends/overrides the built-in defaults. |
| Read by | `.aspis/scripts/context/build_registry.py` to build `.aspis/index/FILE_REGISTRY.yaml` |
| Written by | human (rarely) or `build_registry.py --check` will print gaps the user fills in. |
| R-008 gated? | **No** — purpose strings are advisory, not protected. |
| Validation | JSON well-formed; gaps detected by `build_registry.py --check` |
| Drift detection | Re-running `build_registry.py` is deterministic; if a file has no purpose and isn't in any of the three maps, the registry is missing data, not the file is wrong. |

### 1.2 Tier 2 — `policy/`

Rarely edited. Changing one is a **policy change**, and policy changes are
the kind of change R-008 protects. Every file in `policy/` is data; the
machine reads it; nobody touches the code to add a rule.

#### `policy/modes.yaml`

| Aspect | Value |
|---|---|
| Purpose | The build modes (`vibe` / `mvp` / `production`) and each one's eight knobs (`spec`, `architecture`, `task_size`, `plan_review`, `build_review`, `test_depth`, `docs`, `promotable`). The "rigor dial" referenced in the architecture doc. |
| Read by | planning-lead (P0, `planning-intake` skill) picks the mode; every other skill reads the knobs for that mode |
| Written by | system-lead (R-008 — adding a new mode is a system-design change) |
| R-008 gated? | **Yes** — adding a new mode; changing a knob is also R-008 (knobs gate the whole loop). |

#### `policy/capabilities.yaml`

| Aspect | Value |
|---|---|
| Purpose | The capability taxonomy (10 capabilities today: `planning`, `architecture`, `review`, `orchestration`, `research`, `implementation`, `testing`, `debugging`, `documentation`, `exploration`) and each one's `{preferred_tier, scored_by}`. |
| Read by | `aspis models --sync` (ranks models per capability) |
| Written by | system-lead (R-008 — adding a new capability reshapes routing) |
| R-008 gated? | **Yes** — capability vocabulary is the routing contract. |

#### `policy/agent-capabilities.yaml`

| Aspect | Value |
|---|---|
| Purpose | Maps each agent name to its primary capability (11 agents, one line each). |
| Read by | resolver (decides which score dimension to rank by for this agent) |
| Written by | system-lead (or planning-lead on a new agent) |
| R-008 gated? | **No** — re-classifying an existing agent's primary capability is data, not routing. **Yes** if the change is "this agent should run on a more expensive model than its tier allows" (cross-tier escape). |

#### `policy/hooks.yaml`

| Aspect | Value |
|---|---|
| Purpose | The deterministic rule data: `secrets` (regex patterns), `junk` (ghost-file prefixes/suffixes, kept names, skip-dirs), `protected_paths` (R-008/R-009 gated paths), `enforcement` (`warn` / `block`). |
| Read by | all hooks under `.aspis/scripts/hooks/` via `hooks/_config.py` |
| Written by | system-lead (R-008 — adding a new protected path or a new secret regex is a security-posture change) |
| R-008 gated? | **Yes** — `protected_paths` is the R-008 list. `secrets` and `enforcement` are policy too. |
| Validation | `python .aspis/scripts/hooks/secret_scan.py --self-test` proves the regexes still match. |
| Drift detection | `aspis doctor` checks the live `.git/hooks/` files match the canonical wrappers generated by `install.py`; mismatch is drift. |

#### `policy/commit-convention.yaml`

| Aspect | Value |
|---|---|
| Purpose | The single source for ASPIS commit style: `types`, `scope` (feature/task/plan_task/system), `subject` (max length 72), `body` (advisory), `branch` (advisory), `forbid_attribution`, `attribution_models`, `autofix`, `skip_marker`. |
| Read by | `.aspis/scripts/hooks/commitmsg.py` (validation) + `.aspis/scripts/git/compose.py` (composition) — **the same file in two places**, no second copy |
| Written by | system-lead (R-008 — commit convention is a system policy) |
| R-008 gated? | **Yes** — changing the message grammar changes the project history. |

#### `policy/constitution-checks.yaml`

| Aspect | Value |
|---|---|
| Purpose | A structured index of `rules/architecture-constitution.md` for agents. Each check has `{id, statement, enforced_by, review_question}`. `enforced_by ∈ {planning, build, review}`. |
| Read by | planning-lead, build-lead, reviewer (each loads only the rows it owns) |
| Written by | system-lead (R-008 — adding a check changes the engineering-standards layer) |
| R-008 gated? | **Yes** — this is a constitutional change. |

### 1.3 Tier 3 — `reference/` (do not edit)

Machine data. The system reads these; humans do not touch them.

#### `reference/providers.yaml`

The provider registry. One entry per provider (`anthropic`, `opencode-go`,
`opencode`, `minimax`, `openrouter`, `github-copilot`). Each has
`runtimes`, `detect` (`auth_json` / `claude_settings`), `prefer` (lower =
preferred), `naming` (how a canonical id becomes this provider's model
string).

| Aspect | Value |
|---|---|
| Read by | the resolver's `model_string()` function; `--available` (provider detection) |
| Written by | system-lead (R-008 — provider semantics are part of the routing contract) |
| R-008 gated? | **Yes** — adding a new provider or changing a naming rule. |

#### `reference/model_catalog.yaml`

The catalog. One entry per **canonical** model id (`claude-opus-4-8`,
`minimax-m3`, `deepseek-v4-pro`, `mimo-v2.5`, etc., 25+ entries). Each has
`provider`, `family`, `context_window`, `scores` (per capability 1-10,
seeds), `cost_tier` (`cheap`/`standard`/`deep`/`frontier`), `pricing`
(USD/1M tokens), `limits` (max task complexity), `confidence`
(`low`/`medium`/`high`). `free_to_test` provides four tier defaults for
brand-new users on free models.

| Aspect | Value |
|---|---|
| Read by | resolver; the "ranked menu" generator at the top of `agent-models.yaml` |
| Written by | system-lead (R-008 — model scores affect every routing decision) |
| R-008 gated? | **Yes** — changing a score or pricing is a routing-impact change. |

#### `reference/.runtime-inventory.json` (and root copy)

The detected runtime inventory: which runtimes are installed, which
providers they expose, which models they expose. **Git-ignored.** The
file lives at the root (`.aspis/config/.runtime-inventory.json`) and
also in `reference/` (`.aspis/config/reference/.runtime-inventory.json`)
— a known drift (see §2.4 below).

### 1.4 Validation: what checks that the tree is well-formed?

| Check | Tool | What it covers |
|---|---|---|
| YAML/JSON well-formed | `python -c "import yaml; yaml.safe_load(open(p))"` (or `json.load`) | every file in the tree |
| Schema (key presence) | `aspis models` (for routing tree) | every tier + agent + agent-capability resolves |
| Index consistency | `python .aspis/scripts/context/build_registry.py` | every file in the repo has a purpose; every purpose maps to a real file |
| Reference integrity | resolver | every `models.yaml` / `agent-models.yaml` id exists in `model_catalog.yaml`; every catalog model has a provider in `providers.yaml`; every `model_string()` translation matches a real string in `.runtime-inventory.json` |
| Policy presence | `policy/hooks.yaml` validator (TBD) | every required section (`secrets`, `junk`, `protected_paths`, `enforcement`) is present (even if empty) |

### 1.5 Drift detection: live vs catalog vs machine

Three sources of truth, three drift checks:

1. **`agent-models.yaml` vs `model_catalog.yaml`** — every id in the override
   file must exist in the catalog. The resolver does this; `aspis models`
   prints any orphans.
2. **`models.yaml` vs `model_catalog.yaml`** — same check at the tier map
   level. The `free_to_test` section is a known escape hatch with
   intentional orphans (free-only models not in the catalog).
3. **`.runtime-inventory.json` vs catalog** — the inventory is what the
   user *actually* has, and the catalog is what the system *thinks* the
   user has. If they disagree, `aspis models --apply` will pick a model
   the user cannot reach. The resolver must always resolve against the
   inventory, not the catalog.

A complete drift check is a single `aspis doctor` (see §5.3).

---

## 2 · MODEL ROUTING SYSTEM

The resolver is the function `resolve_model(agent, runtime, tier=None) →
canonical_id → runtime_specific_string`. Two transformation steps:

1. **Tier → canonical id**: `models.yaml` / `agent-models.yaml` /
   `project.yaml` precedence, ending in a canonical id (e.g.
   `claude-sonnet-4-6`).
2. **Canonical id → runtime string**: the runtime adapter's
   `model_string(canonical, provider_inventory)` consults
   `reference/providers.yaml` and the inventory, picks the preferred
   provider that has the model, and returns the exact string
   (e.g. `opencode-go/minimax-m3`, `minimax/MiniMax-M3`, or the Claude
   alias `sonnet`).

### 2.1 `models.yaml`: the global tier map

```yaml
opencode:
  cheap:    deepseek-v4-flash
  standard: minimax-m3
  deep:     deepseek-v4-pro
claude:
  cheap:    claude-haiku-4-5
  standard: claude-sonnet-4-6
  deep:     claude-opus-4-8
```

A value is **always a canonical id** (per the file's own header comment
"Values MUST be catalog ids"). The runtime adapter translates.

### 2.2 `agent-models.yaml`: per-(runtime, capability) + per-(runtime, agent) overrides

Two surfaces in one file:

```yaml
runtimes:
  claude:
    by_capability:
      planning:  claude-sonnet-4-6
      review:    claude-sonnet-4-6
      ...
    agents:
      # reviewer: claude-sonnet-4-6    # per-agent pin overrides capability
```

Resolution order (most-specific wins, both within a single file):

```
agents.<name>           (per-agent pin, highest)
by_capability.<cap>     (per-capability)
config/models.yaml.<runtime>.<tier>   (fall through)
```

`project.yaml` then layers above the whole file (per-project overrides
come after the global).

### 2.3 Resolution algorithm (the spec the system-lead owns)

```
function resolve(agent, runtime):
    # 1. Per-project, per-(runtime, agent) pin
    v = project.yaml.runtimes[runtime].agents[agent]
    if v: return resolve_value(v, runtime)

    # 2. Per-project, all-runtimes pin
    v = project.yaml.agents[agent]
    if v: return resolve_value(v, runtime)

    # 3. Per-(runtime, agent) pin
    v = agent_models.yaml.runtimes[runtime].agents[agent]
    if v: return resolve_value(v, runtime)

    # 4. Per-capability pick
    cap = agent_capabilities.yaml.agents[agent]
    v = agent_models.yaml.runtimes[runtime].by_capability[cap]
    if v: return resolve_value(v, runtime)

    # 5. Tier fallback
    tier = project.yaml.models[runtime][tier]   # may be None
            or models.yaml[runtime][tier]
    return resolve_value(tier, runtime)

function resolve_value(v, runtime):
    if v in {cheap, standard, deep}:
        v = models.yaml[runtime][v]
    # v is now a canonical id
    return runtime_adapter.model_string(v, runtime, inventory, providers.yaml)
```

### 2.4 Provider detection and fallback

Provider detection runs in `aspis models --available`:

1. For each provider in `providers.yaml` whose `runtimes` includes `runtime`,
   check the `detect` method (`auth_json` for OpenCode, `claude_settings`
   for Claude). The result is a presence boolean.
2. Enumerate models for the present providers via the runtime's native
   listing (`opencode models` + `opencode auth list`; `~/.claude` config
   for Claude aliases).
3. Write the result to `.aspis/config/.runtime-inventory.json` (git-ignored).

**Fallback at resolution time**:
- A canonical id may be available on several providers (e.g.
  `claude-opus-4-8` via `opencode`, `opencode-go`, `openrouter`,
  `github-copilot`). The `prefer` rank in `providers.yaml` orders them.
  `opencode-go` (prefer=1) wins over `opencode` (prefer=2) wins over
  `openrouter` (prefer=4) when all are present.
- If the preferred provider is **not present** (no auth), the next-best
  present provider is used.
- If **no provider** in the inventory has the canonical id, the resolver
  fails loud at `--apply` time. At read time (e.g. `aspis models`), the
  resolver prints a clear "model not available" warning with the
  inventory to help the user fix `models.yaml` or `project.yaml`.

### 2.5 Model tier change procedure (R-008 gated)

Three classes of model change, each with a different gate:

| Change | Who decides | Gate |
|---|---|---|
| Add a new canonical model to `model_catalog.yaml` (new model id, new scores) | system-lead | R-008 (model routing change) — human approves scores/pricing/confidence |
| Edit an existing row's `scores` / `pricing` / `limits` / `confidence` | system-lead | R-008 (re-scoring changes routing) |
| Change a tier pin in `models.yaml` (cheap/standard/deep → another canonical id) | system-lead | R-008 (global tier change) |
| Per-project tier override in `project.yaml.models.<runtime>.<tier>` | project-lead + system-lead | R-008 (project routing) — system-lead validates the catalog still has the id |
| Per-agent pin in `agent-models.yaml` (or `project.yaml.agents`) | project-lead + system-lead | **NOT** R-008 if the pin keeps the agent in its existing cost tier; **YES** if it crosses tier (e.g. moving a `cheap` agent to a `frontier` model) |
| Add a new capability / re-classify an agent's capability | system-lead | R-008 (capability vocab change) |
| Add a new provider in `providers.yaml` | system-lead | R-008 (routing contract change) |

**The audit trail**: every change to a config file goes through git.
A `/SYS` scope on the commit signals "system-lead governed this; not a
product commit". `git log --grep '/SYS'` gives the full audit.

### 2.6 Model drift detection

Three places drift can hide:

1. **Catalog vs reality** — a `model_catalog.yaml` row claims a model
   exists with these scores; the user no longer has it. Detected by
   `aspis models --sync` (writes a fresh inventory; the diff against
   the catalog is the drift).
2. **Inventory staleness** — the inventory is the last `--sync` snapshot;
   if the user re-authenticates or buys a new plan, the inventory is
   stale until the next `--sync`. The `generated:` timestamp in the
   inventory file is the freshness signal. `aspis doctor` flags
   inventories older than the user's most-recent login change.
3. **`agent-models.yaml` vs the live agent's `model:` frontmatter** —
   if the user edits `agent-models.yaml` and forgets `aspis models
   --apply`, the live agents are still running the old model. This is
   the **most dangerous drift** because the user thinks the new model
   is live. Mitigations:
   - `aspis models` prints a "MISMATCH" line if any live agent's
     `model:` field disagrees with the resolver.
   - The README warns explicitly: "After editing `agent-models.yaml`,
     `project.yaml`, or `models.yaml`, run `aspis models --apply`".
   - `aspis doctor` checks live-vs-resolved parity across all live
     agents.

---

## 3 · RUNTIME EXPORT SYSTEM

The export system is the system-lead's "compiler" — it takes the runtime-
neutral **catalog** (the source of truth) and renders it into the runtime
directories `.opencode/` and `.claude/`. D-002/D-008 ground this:
"per-runtime adapters translate and **drop** what a runtime can't express
— they never error, and we never hand-write per-runtime asset files."

### 3.1 The three-layer transform

```
L1  CATALOG  (runtime-neutral markdown; the truth)
            ↓  export(adapter=opencode|claude, profile=...)
L2  LIVE RUNTIME  (`.opencode/`, `.claude/`)
            ↓  runtime reads
L3  PROMPT CONTEXT  (what the LLM actually sees)
```

The brain (`.aspis/`) is a separate fourth layer (durable, tool-neutral,
D-003) — not part of the export pipeline, but the source the catalog
itself is *authored from*.

### 3.2 How agents are rendered

The runtime adapter pattern (D-008): `RuntimeAdapter.supports(kind)` says
which asset kinds a runtime can express; `emit_runtime_hooks(adapter)`
writes the hook wiring to the runtime's fixed location. The same catalog
asset is rendered to OpenCode or Claude by **translation**, not by
duplication.

| Catalog asset kind | OpenCode rendering | Claude rendering |
|---|---|---|
| `agent` (markdown with frontmatter) | `.opencode/agents/<name>.md` with `mode:`, `model:`, `permission:`, `skill:` frontmatter | `.claude/agents/<name>.md` (or as a sub-agent definition) |
| `skill` (directory with `SKILL.md`) | `.opencode/skills/<name>/SKILL.md` (+ bundled scripts/resources) | `.claude/skills/<name>/SKILL.md` |
| `command` | `.opencode/command/<name>.md` | `.claude/commands/<name>.md` |
| `template` | reference only — included by a skill/agent when invoked | reference only |
| `hook` | `.opencode/plugin/<name>.ts` (per D-010) or `tool.execute.before` | `.claude/settings.json` `PreToolUse` (per D-010) |
| `script` | same path on disk, called by a command/hook | same path on disk, called by a command/hook |

Every kind declares its `placement` and `write_op` in
`assetkinds.py` (D-008). The exporter reads that registry — no
`if runtime == "claude"` branching anywhere.

### 3.3 Byte-parity verification

The "moat" (ASPS overview §9): **the catalog regenerates live exactly**.
A byte-parity check is `byte-equal(catalog-render(catalog), live)` for
every asset kind. The procedure:

1. `aspis export --dry-run` — write the rendered output to a temp dir
   (or a `--to` flag) instead of the live dir.
2. For every file the catalog would produce, compare the rendered bytes
   to the live file's bytes.
3. Report any `MISMATCH (live → would-render-as)` with the diff.
4. **No mismatch** = the live dir is in sync with the catalog; safe to
   commit the catalog update.
5. **Mismatch** = either the catalog has changed (a re-export is needed)
   or the live dir has been hand-edited (a drift problem; the exporter
   refuses to clobber hand-edits without `--force` or, for protected
   areas, R-008 approval).

The protection engine (`protect.py`, F-015) hashes every live file; the
exporter checks the hash before overwriting. Protected assets
(`rules/**`, `.claude/settings.json`, R-008 paths) require a recorded
human approval to overwrite.

### 3.4 Partial export (single agent / single skill)

`aspis export <asset-path>` — render one asset. The exporter:

1. Resolves the asset's kind from `assetkinds.py`.
2. Asks the active runtime adapter(s) whether they support the kind.
3. For each supporting runtime, renders to the live path.
4. Runs the byte-parity check (now narrow: one file per runtime).
5. Reports success/failure.

This is the day-to-day loop during development: edit a catalog asset,
re-render one, validate, hand to committer.

### 3.5 Full export (all assets)

`aspis export` (no args) — render every catalog asset to every supporting
runtime. The flow:

1. Enumerate the catalog (the resolver-driven view of every asset).
2. For each `{asset, runtime}` pair, render.
3. Run the full byte-parity check.
4. Report a per-`(kind, runtime)` summary.
5. Exit non-zero if any render fails parity (unless `--force` is set).

The full export is what `aspis init` and `aspis bootstrap` use, and
what `aspis doctor` calls when invoked with `--reconcile`.

### 3.6 Export validation

Beyond byte parity, the exporter validates:

| Check | What it catches |
|---|---|
| Frontmatter parses | every `agents/*.md` is valid YAML frontmatter |
| Every `skill:` reference resolves | no `skill: foo` where `foo` isn't in `.opencode/skills/` |
| Every `task:` reference resolves | no `task: reviewer` where `reviewer` isn't an agent id |
| Every `permission:` shape matches the runtime's grammar | a Claude `permission: bash: { "git commit*": "deny" }` is fine; an OpenCode one must use the glob-list form |
| `model:` resolves to a live model | the canonical id is in the inventory after `--sync` |
| No orphan asset in live | if a file is in `.opencode/agents/` but not in the catalog, flag it (the catalog is the truth) |
| No missing asset in live | if the catalog says "render this" and the file isn't in live, that's drift; the exporter will (re)write it |

### 3.7 Protected asset handling

The F-015 protection engine (referenced by the architecture doc and
visible in the recent-changes feed) is the gate. Every export pass
computes a content hash of every live file *before* writing; the new
write is allowed only when:

- The file is unprotected, **or**
- The file is protected AND the user has recorded a human approval
  (`ASPIS_ALLOW_PROTECTED=1` plus an approval entry in
  `.aspis/approvals/<id>.md`), **or**
- The file is protected AND the new content hash matches the recorded
  hash (idempotent re-export — the exporter is "writing what was
  already there" and the protection engine lets it through).

This is the defense-in-depth for R-008-protected paths: the exporter
itself cannot rewrite a `rules/**` file by accident, and an LLM agent
that *tries* to (via `edit` / `write`) hits the same gate at the tool
boundary.

---

## 4 · HOOK SYSTEM MANAGEMENT

The hooks are the "deterministic substrate" the architecture doc talks
about. D-010 ground: two surfaces (git commit boundary + per-runtime
tool boundary), one shared core under `.aspis/scripts/hooks/`, data-driven
rules, **non-blocking by default**.

### 4.1 The two surfaces

| Surface | Where it fires | Scripts |
|---|---|---|
| **Git commit boundary** | `.git/hooks/{pre-commit,commit-msg,post-commit}` | `precommit.py`, `commitmsg.py`, `postcommit.py` (each a thin entry point; the real work is in shared modules) |
| **Runtime tool boundary** | Claude: `.claude/settings.json` `PreToolUse`; OpenCode: `tool.execute.before` plugin | `runtime_guard.py` (shared logic), with adapter-emitted wiring |

Both surfaces import the **same** `.aspis/scripts/hooks/` modules; the
rules in `policy/hooks.yaml` are read by both. There is no second copy.

### 4.2 Pre-commit hook — scope, secrets, junk, protected paths

The `precommit.py` entry point orchestrates the check order:

1. **`scope.py`** — reads `.aspis/current/active_feature.json` (if any) and
   the feature's `feature.yaml` (`scope.allowed` / `scope.forbidden`).
   Compares staged files against both lists. *Failure modes*:
   - Out-of-allowed → block.
   - In-forbidden → block.
   - Feature not set on a non-lifecycle commit → warn.
2. **`secret_scan.py`** — runs every regex in `policy/hooks.yaml.secrets`
   against ADDED lines in the staged diff. *Failure*: block.
3. **`cleanup.py` (junk guard)** — for every staged file, check the
   basename against `policy/hooks.yaml.junk` (`ghost_prefixes`,
   `ghost_suffixes`, `keep`, `skip_dirs`). A shell-redirect ghost file
   (`=2.5`, `:w`, `foo,`) is **deleted** in `warn` mode (auto-fix) and
   **blocked** in `block` mode.
4. **`gitignore.py`** — for the staged `path/to/.gitignore`, validate
   that common Python/Node noise patterns are present (sourced from the
   cached Toptal gitignore templates). Auto-add missing sections.
5. **`policy/hooks.yaml.protected_paths`** — staged change to a
   protected path requires the env var `ASPIS_ALLOW_PROTECTED=1`. This
   is the R-008 gate at the *file* level (the R-008 gate at the
   *change* level is the human approval recorded in
   `.aspis/approvals/`).
6. **Auto-fixes** (warn mode only): run `ruff format` and `ruff check
   --fix` on the staged content; re-stage the result. Never in `block`
   mode (the commit is then on the human to fix).

**Enforcement switch** (one switch, no code change):

```yaml
# .aspis/config/hooks.yaml
enforcement: warn       # never blocks (default; safe to ship)
enforcement: block      # turns every check into a hard wall
```

In `warn` mode, all the safety checks **report**; the only auto-fixes
are the safe ones (junk removal, gitignore patch, ruff format). The
`block` mode is for environments where the policy is enforced by the
runtime (pre-commit CI, signed-commit policy).

### 4.3 Commit-msg hook — convention validation

`commitmsg.py` reads `policy/commit-convention.yaml` and validates the
single source of truth. Machine-enforced keys:

- `types` — title prefix must be in `[feat, fix, refactor, docs, chore,
  test, style, perf]`.
- `subject.max_length` — title must be ≤ 72 characters.
- `forbid_attribution` — substring match (case-insensitive) against
  `["co-authored-by", "generated with", "generated by ai", "written by
  ai", "ai-generated", "🤖"]`.
- `attribution_models` — substring match (only in an attribution
  *context*; the bare directories `.claude` / `.opencode` stay
  valid).
- `autofix.attribution` — strip forbidden-attribution lines, keeping
  history human-authored (non-blocking repair).
- `skip_marker` — `Commit-Style: skip` on its own line bypasses
  convention checks for that one commit (escape hatch; the hook
  removes the trailer and logs it).

Advisory keys (`subject.pattern`, `subject.imperative`, `body.bullets`,
`body.tasks_trailer`, `branch` shape) are documented but not
machine-checked. History is the auditor.

The same `validate()` function is used by `.aspis/scripts/git/compose.py`
so the committer can preview a composed message *before* the commit —
**one validation function, two callers, no second copy** (D-011).

### 4.4 Post-commit hook — trace, context refresh

`postcommit.py` runs after the commit lands:

1. **Trace** — append a JSONL line to `.aspis/traces/raw/<date>.jsonl`
   (or `<run_id>.jsonl` for F-016's run-keyed scheme). The line carries
   `{commit_sha, files_changed, scope, author, run_id, ...}`.
2. **Context refresh** — call `build_state.py` + `record_changes.py`
   to update `.aspis/context/CURRENT_STATE.md` and
   `.aspis/context/RECENT_CHANGES.md` (D-012 — these are
   *untracked*; they live as working tree, regenerated on demand).
3. **Index refresh** (D-012) — call `build_registry.py` and
   `build_code_map.py` to refresh the untracked indexes.

The post-commit hook is **never blocking** (it always exits 0 after
logging the trace). If the brain refresh fails, the trace is still
written; the user sees a "context stale" warning on the next `aspis
doctor`.

### 4.5 Runtime hooks — PreToolUse, PostToolUse

D-010: "Runtime wiring is adapter-emitted and capability-gated
(`RuntimeAdapter.emit_runtime_hooks`)". Each runtime owns its file's
fixed location:

| Runtime | File | Where it lives |
|---|---|---|
| OpenCode | `scope-guard.ts` plugin | `.opencode/plugins/scope-guard.ts` (or the catalog source) |
| Claude | `settings.json` `PreToolUse` block | `.claude/settings.json` |

The same logic in `.aspis/scripts/hooks/runtime_guard.py` is invoked
from both. The Claude wiring is **rebuilt on every export** (the
adapter writes the `PreToolUse` block referencing the Python script
path); the OpenCode wiring is a TypeScript plugin the exporter copies
from the catalog (the TS plugin shells out to the Python script for
parity — the regex logic lives in Python and is shell-Python-parity
tested).

The runtime hook checks:
- **Scope**: every `write` / `edit` is checked against
  `active_feature.json.feature.yaml.scope.allowed` /
  `scope.forbidden`. The Python script in `.aspis/scripts/hooks/scope.py`
  does the check.
- **Protected paths**: same R-008 gate as pre-commit.
- **Tool allowlist**: the runtime hook can refuse a tool call that
  isn't in the agent's `permission:` (defense in depth — the
  permission block is the *intent*; the hook is the *enforcement*).

### 4.6 Hook installation and verification

`install.py` writes three thin bash wrappers into `.git/hooks/`:

```bash
#!/usr/bin/env bash
# Managed by ASPIS — regenerated by install.py.
exec "<python>" "<entry>" "$@"
```

Idempotent. Re-running rewrites identical wrappers.

`aspis doctor` verifies:

- All three wrappers exist and are executable.
- Each wrapper's `<python>` and `<entry>` paths still resolve.
- The Python entry points parse and import without error.

`aspis doctor --fix` re-runs `install.py` to repair drift.

### 4.7 Hook policy management — `policy/hooks.yaml`

Adding a new rule is **data, not code**. To add a new secret pattern:

```yaml
# .aspis/config/policy/hooks.yaml
secrets:
  - "AKIA[0-9A-Z]{16}"
  - "<new pattern>"     # add a line, commit under /SYS
```

The hooks degrade to a no-op for any section left empty.

### 4.8 Enforcement mode — warn vs block

`enforcement: warn` is the project default (and the only mode that
auto-fixes; "safe to ship to others"). `enforcement: block` flips the
same checks into hard walls. The switch is the **only** knob to
toggle; the rest of the data is unchanged.

| Mode | Auto-fixes | Blocks? | Use case |
|---|---|---|---|
| `warn` | yes (junk, gitignore, ruff format) | no (everything is reported) | public repos, contributors |
| `block` | no (commit is on the human) | yes (all checks hard-wall) | CI gates, signed commits, strict policy |

A per-repo CI workflow can override the mode for PR builds without
touching the file (env var `ASPIS_ENFORCEMENT=block`).

### 4.9 Shell-Python parity testing

A rule enforced by a hook cannot be skipped by an LLM. The way that
property is preserved: every shell wrapper **delegates to Python** for
the actual rule. The Python module is the source of truth; the shell
wrapper is just a launcher. The test:

```python
# tests/test_hook_parity.py
def test_secrets_match_in_python_and_shell():
    python_results = python_secret_scan(diff)
    shell_results = subprocess.check_output(["bash", wrapper, "--self-test"])
    assert python_results == shell_results
```

`secret_scan.py --self-test` runs the regex against a fixture diff
and prints a JSON result; the Python test then re-runs the same
fixture in-process and asserts equality. If the two diverge, the hook
is wrong, the test fails, and the human-gate (PR review) catches it.

### 4.10 Inventory of the 11 hook scripts (live)

| Script | Purpose |
|---|---|
| `precommit.py` | Orchestrates the pre-commit checks |
| `commitmsg.py` | Validates commit message against `commit-convention.yaml` |
| `postcommit.py` | Trace + context refresh |
| `secret_scan.py` | Regex secret scan against staged diff |
| `scope.py` | Active-feature scope guard (allowed/forbidden) |
| `cleanup.py` | Junk-file guard (ghost prefixes/suffixes) |
| `gitignore.py` | `.gitignore` validation + auto-patch (Python/Node templates) |
| `runtime_guard.py` | Runtime PreToolUse logic (shared with `scope.py`) |
| `install.py` | Write the three bash wrappers into `.git/hooks/` |
| `_config.py` | Single config loader (one place that reads `hooks.yaml` and `commit-convention.yaml`) |
| `_git.py` | Shared git helpers (`repo_root`, staged-file enumeration) |

---

## 5 · VALIDATION SYSTEM

The validation system is the "5 deterministic surfaces" the architecture
references. Each command is a thin entry point over shared
implementations; each one is **non-blocking in `warn` mode by default**
and becomes a hard wall when the project opts in.

### 5.1 `aspis validate-runtime` — what it checks, how it works

| Check | Implementation |
|---|---|
| Every `.opencode/agents/*.md` and `.claude/agents/*.md` has parseable frontmatter | `yaml.safe_load` on each |
| Every frontmatter declares `mode:`, `model:` (or inherits from resolver), and at least one skill | schema check |
| Every `skill:` reference resolves to a real `.opencode/skills/<name>/SKILL.md` (or `.claude/...`) | `pathlib.exists` |
| Every `task:` reference resolves to a real agent id | registry lookup |
| Every `model:` value resolves through the resolver (catalog → inventory) | resolver call |
| The Claude `permission:` shape matches Claude's grammar; the OpenCode one matches OpenCode's | per-runtime schema |
| The `.claude/settings.json` `PreToolUse` block is present and well-formed | JSON schema |
| The `.opencode/plugins/scope-guard.ts` exists and is a symlink (or copy) of the catalog source | byte check |

**Exits non-zero on any structural issue.** Print a per-file
`OK / FAIL / WARN` table.

### 5.2 `aspis validate-index` — registry consistency

`python .aspis/scripts/context/build_registry.py --check`:

- Every file in the repo is registered (in `FILE_REGISTRY.yaml` or in
  the built-in default patterns or in `purposes.json`).
- Every purpose string is non-empty.
- The YAML is well-formed.
- **Gaps** (a file with no purpose) are listed — the user fills them
  into `purposes.json` or accepts the registry's best-effort default.

### 5.3 `aspis doctor` — full health check

A roll-up that runs every validator in sequence and prints a one-page
report:

| Section | Source | What it shows |
|---|---|---|
| **Brain** | `CURRENT_STATE.md` exists, `RECENT_CHANGES.md` is fresh | the brain is regenerable |
| **Indexes** | `FILE_REGISTRY.yaml`, `CODE_MAP.md` exist and are recent | the indexes are regenerable |
| **Config tree** | every YAML/JSON in `.aspis/config/` parses | the config tree is well-formed |
| **Models** | `aspis models` (resolver check) | every tier + agent + capability resolves to an available model |
| **Inventory** | `.aspis/config/.runtime-inventory.json` age | if the inventory is older than N days, warn |
| **Live agents** | the resolver output for every live agent | "MISMATCH" lines for any agent whose live `model:` doesn't match the resolver |
| **Runtime hooks** | `.git/hooks/{pre-commit,commit-msg,post-commit}` present and `aspis doctor --fix`-able | hooks are installed and match the canonical wrappers |
| **Protected assets** | hash check on `rules/**`, `.claude/settings.json`, `permissions*.yaml` | no protected file is silently different from the last approved version |
| **Permissions** | every agent's `permission:` block matches the policy (R-008 list, `git commit*` denied, `git push*` denied) | permissions are policy-compliant |
| **Drift** | catalog → inventory diff; catalog → live diff; inventory age | anything that's drifted is listed with the drift direction |

`aspis doctor` is **the cockpit command**. The architecture doc's
"Day 0 — install: `aspis doctor` reports 0 FAIL" is its first run.

### 5.4 `aspis preflight` — pre-task gate

A pre-build health check, faster and narrower than `aspis doctor`. What
it does:

1. Confirm clean state (`git status` clean; brain indexes are fresh).
2. Confirm the active feature is set (or warn on a bare `aspis
   preflight` with no feature).
3. Confirm scope is set in the feature's `feature.yaml` (`allowed` /
   `forbidden` populated).
4. Run the scope guard on the *staged* files (if any).
5. Confirm gates are runnable (pytest, ruff, mypy — whatever the
   feature's `gates.yaml` declares).

`aspis preflight` is what `build-lead` and `fix-lead` run before
delegating; its job is to catch the "you forgot to set scope" /
"the test runner is missing" class of bug before the work starts.

### 5.5 Byte-parity validation

See §3.3. The export's `--check` flag runs the full byte-equality
comparison and exits non-zero on any mismatch.

### 5.6 Permission audit

A separate pass that walks every live agent's `permission:` block and
checks it against the canonical policy:

- `git commit*` is `deny` for every agent except `committer`.
- `git push*` is `deny` for every agent.
- `webfetch` / `websearch` are `deny` by default; allow only for
  `system-lead` and `research-lead`.
- Reviewer is read-only (`edit: deny`, `write: deny`).
- R-008-protected paths appear in no agent's `permission:` allow list
  (they can only be edited through the R-008 gate).

This is the audit the system-lead runs after every change to
`agent-models.yaml` or to any agent's frontmatter.

### 5.7 Drift detection

Five classes of drift, five commands:

| Drift | Command |
|---|---|
| Catalog → inventory (models the user no longer has) | `aspis models --sync` (writes new inventory) |
| Inventory age (stale) | `aspis doctor` (age in the Models section) |
| Live agent `model:` vs resolver | `aspis models` (prints MISMATCH) |
| Catalog → live (hand-edited live file) | `aspis export --check` (byte-parity) |
| Protected asset hash drift | `aspis doctor --fix` (re-records the approval if the change is sanctioned) |

### 5.8 Missing validation: what should exist but doesn't

| Missing | Severity | Why it matters |
|---|---|---|
| `aspis validate-skills` — every `SKILL.md` has parseable frontmatter with `name` + `description` (≤64 / ≤1024 chars per Anthropic convention) | medium | the live skill format is markdown + frontmatter, but no automated check enforces the Anthropic Skills shape (D-006: "an agent loads only the layer relevant to its work") |
| `aspis validate-agents` — every agent's `description:` is third-person and names *both* what and when (Anthropic convention) | medium | agent discoverability depends on the description; a weak description means the routing LLM can't pick the right agent |
| `aspis validate-decisions` — every `DECISIONS.md` entry has a date and a stable id (D-NNN), and the id is referenced from the file(s) it grounds | low | the decisions spine is the audit log; format drift is silent until someone needs the audit |
| `aspis validate-constitution` — every code change in the last N commits has a constitution check it was reviewed against (auto-discover from `constitution-checks.yaml`) | low | the constitution is the engineering-standards layer (D-009); without an automated check, the standard rots |
| `aspis validate-trace` — every commit has a trace line in `.aspis/traces/raw/`; the trace line references the commit sha | medium | D-011: "no silent runs"; without an automated check, the trace can silently gap |
| `aspis validate-approvals` — every R-008 protected-path change has a corresponding entry in `.aspis/approvals/` | **HIGH** | R-008 is the human gate; the approval ledger is the *evidence*; without an automated check, the gate is honor-system |
| `aspis validate-parity` — shell hooks delegate to the same Python as `--self-test` (see §4.9) | medium | the "no LLM in the pipeline" property is the whole point of the deterministic substrate; a silent divergence breaks the moat |
| `aspis validate-profiles` — every profile inherits `base.yaml`; no circular inheritance; every named asset exists in the catalog | low | profiles are a future concept but the schema is being designed (D-005) — the validator should be ready when the first profile lands |

---

## 6 · PROFILE SYSTEM

A profile is a **data** file (YAML) that selects which catalog assets a
project receives. Per the architecture doc: "the current system has one
profile (`base.yaml`); future profiles for python, data-science,
full-stack, etc. are data files, not code."

### 6.1 `base.yaml` — minimum for every project

The `base.yaml` profile is the **base layer** every project inherits
implicitly. It contains:

- The 5 primary agents (`project-lead`, `planning-lead`, `build-lead`,
  `reviewer`, `system-lead`).
- The 6 subagent leads (`fix-lead`, `test-lead`, `research-lead`,
  `committer`, `general-builder`, `project-explorer`).
- The core skills (`prestart-checks`, `context-ladder`, `request-
  classification`, `commit-message`, `system-awareness`, etc.).
- The mode default (`production`).
- The hook bundle (pre-commit, commit-msg, post-commit; the policy
  files are inherited by every project).

A project never *omits* `base.yaml`; it only *adds* profiles on top.

### 6.2 Specialized profiles

| Profile | Adds | Removes |
|---|---|---|
| `python-cli.yaml` | `python-builder`, `pytest-runner`, `ruff-fixer`; `mypy`; Python `.gitignore`; pytest gate; ruff gate | — |
| `full-stack.yaml` | `frontend-builder`, `api-builder`; TypeScript `.gitignore`; npm gate; Playwright gate | — |
| `data-science.yaml` | `notebook-builder`, `pandas-toolkit`; Jupyter hook; data-output reviewer | — |

Each profile declares its *additions* and *removals* as data:

```yaml
# profiles/python-cli.yaml
extends: base
adds:
  agents: [python-builder]
  skills: [pytest-patterns, python-style]
  tools: [pytest, ruff, mypy]
  templates: [SPEC.python, PLAN.python]
  hooks: [pytest-pre-commit, ruff-pre-commit]
  gates: [pytest, ruff, mypy]
removes: []
```

A profile never re-declares what `base` already provides; it layers.

### 6.3 Profile inheritance and merging

- **Single inheritance** (`extends: <name>`) — one parent profile.
- **Multi-inheritance** (TBD) — `extends: [base, python-cli]` would
  merge both. **Decision pending** (the architecture doc hints at
  multi; the schema isn't yet locked).
- **Merge rules**:
  - `adds` is concatenated.
  - `removes` is applied **after** the parent's `adds`.
  - For scalar conflicts (two parents add the same agent with
    different settings), the **more specific** (the inheritor) wins;
    a warning is printed on conflict.
- **No circular inheritance** — the validator detects cycles and
  fails loud.

### 6.4 Profile-based export filtering

The exporter reads the **active profile stack** (base + project
profiles) and renders only what the stack declares. The flow:

1. Read the active profile stack from
   `.aspis/config/profiles.yaml` (the project's "this is what I am").
2. Resolve the inheritance chain to a flat list of `adds` / `removes`.
3. For each catalog asset, ask: is it in the final list?
   - **Yes** → render to every supporting runtime.
   - **No** → skip (and delete the corresponding live file if it
     exists, after a `byte-equal(live, would-render-as-empty)` check).
4. Run the byte-parity check on the rendered set only.

The result: a "data-science" project never inherits the
`frontend-builder` agent; a "python-cli" project never inherits the
`notebook-builder`. Each project gets a small, coherent runtime.

### 6.5 Profile validation

`aspis validate-profiles` (TBD — see §5.8):

- Every profile has a unique name.
- Every `extends` target exists.
- No circular inheritance.
- Every `adds.<kind>` name exists in the catalog.
- Every `removes.<kind>` name exists in the catalog.
- The final resolved list is non-empty (a project always has at least
  the base agents).
- The final resolved list is consistent (no two profiles add the same
  asset with conflicting settings).

### 6.6 Profile selection at init time

`aspis init --profile <name>`:

1. Detect the project's stack (look for `pyproject.toml`,
   `package.json`, `requirements.txt`, `*.ipynb`, etc.).
2. Suggest one or more profiles based on the stack detection.
3. On confirmation, write `.aspis/config/profiles.yaml` with the
   resolved stack.
4. Run `aspis export` to render the live runtime from the stack.
5. Run `aspis doctor` to confirm 0 FAIL.

`aspis init --write` is the path the architecture doc describes for
"Day 1 — start a project." The bootstrap step that follows promotes
4 agents to primary, then the bootstrap package self-deletes (D-004).

### 6.7 Open profile design questions (for system-lead to settle)

These are the gaps the architecture doc flags; the system-lead owns
their resolution:

| Question | Decision owner | Status |
|---|---|---|
| Multi-inheritance allowed? | system-lead (R-008) | parked; the schema doesn't forbid it, the validator does |
| Are profiles part of the project repo or in the catalog? | system-lead | leaning **catalog** (a profile is reusable across many projects of the same shape; tracking it in the catalog is the C-SINGLE-SOURCE way) |
| Can a project edit an inherited profile? | system-lead | **no** — edit the catalog and bump the version; the project overrides via its own `adds` |
| Profile version pinning | system-lead | **yes** — the project pins `python-cli@1.2` in `profiles.yaml`; a project never silently drifts when the profile is updated |
| What happens to a project's runtime when a profile version moves? | system-lead | `aspis doctor` flags drift; the user runs `aspis export` to re-render; no auto-upgrade (the project chooses) |

---

## 7 · Gaps and known drift (the system-lead's "what to fix next")

This is the spec the system-lead's `system-repair` skill consumes.
Everything in this section is **current state** (verified against the
live files).

### 7.1 Drift in the rule numbering (R-008 vs R-009)

**Where**: `local/ASPS/AGENTS.md`, `local/ASPS/.asps/context/ASPS_OVERVIEW.md`,
and the **live** `.aspis/config/policy/hooks.yaml` all reference
"R-009" as the human gate for protected paths.

**What's right** (per `.aspis/rules/system-rules.md`):
- **R-008** — *Human gate*: architecture, rules, permissions, security
  posture, model-routing changes.
- **R-009** — *Trace and learn*.

**Fix**: update `hooks.yaml`'s header comment to read "R-008 protected
paths" (the existing system-lead and architecture doc all use R-008).
The ASPS-local docs (gitignored) can stay as historical reference.

### 7.2 Duplicate `.runtime-inventory.json`

**Where**: `.aspis/config/.runtime-inventory.json` (root of config) and
`.aspis/config/reference/.runtime-inventory.json` (in `reference/`).
Both have the same `generated:` timestamp and (modulo the absent
github-copilot row in the root version) almost-identical content.

**Fix**: keep one canonical location. Recommendation: **root** (the
inventory is a *working* state, git-ignored; the `reference/` directory
is for *catalog* data, not generated state). Delete
`reference/.runtime-inventory.json` and update the README to point at
the root path.

### 7.3 `websearch: allow` drift on `system-lead`

**Where**: `.opencode/agents/system-lead.md` allows `websearch`; the
local spec (`local/agents/system-lead.md`) calls this out as drift
("`websearch: allow` (live) vs `deny` (catalog)").

**Fix**: per the R-008 catalog, the system-lead is the
"executive owner of the runtime and operating infrastructure" and
needs to look up official runtime docs (F-016 research §2
establishes this); the local spec notes the catalog likely
intends `deny` for catalog-time and `allow` for live-time. The
fix is **policy clarification in the system-lead's
`config-management` skill** — when to allow websearch (research,
patch validation) and when to deny (committing, exporting). The
skill body should resolve this; the frontmatter stays `allow` for
now.

### 7.4 `task:` allowlist in system-lead frontmatter

**Where**: live frontmatter allows `reviewer` and `committer` in
`task:`; local spec notes these as "likely catalog gaps to close."

**Fix**: the live system *does* delegate to reviewer (for system-
change validation) and committer (because system-lead never
commits). The catalog simply needs the same line. Add to the
catalog after R-008 review of the full set of allowed
subordinates (currently: `project-explorer`, `reviewer`,
`committer`).

### 7.5 Model tier for system-lead

**Where**: live is `standard` (`opencode-go/minimax-m3`); the
local spec notes "architecture may intend deep for system-
critical changes."

**Fix**: when the catalog re-publishes the system-lead, decide
deep vs standard. The `system-validation` and `system-repair`
skills would benefit from a deep-tier fallback for
high-stakes system work; the standard tier is fine for
day-to-day (adding a skill, fixing a typo). R-008 to decide.

### 7.6 `governance` subagent

**Where**: the local spec and the architecture doc both reference
a future `governance` subagent — the *only* agent allowed to edit
`rules/**` and `profiles/defaults.yaml`, always R-008-gated. It
does not yet exist.

**Fix**: the system-lead currently holds the governance role
itself (R-008 enforcement in its own rules, not a separate
agent). Extract `governance` when the system grows past ~7
system leads (the threshold Cursor uses for "extract a role").
Today, the system-lead carries it; tomorrow, it's a subagent.

### 7.7 `asps-opencode-author` / `asps-claude-author` subagents

**Where**: same — future subagents for "one asset, one runtime"
authoring. They are referenced in the local spec as a parking
spot for when the system-lead's authoring load justifies
extraction.

**Fix**: extract when more than ~30% of system-lead's day is
single-runtime authoring. Today, the system-lead authors
runtime-neutral catalog assets and the adapter translates (D-002,
D-008); the extraction is *not* yet justified.

### 7.8 Missing validators (see §5.8)

The eight validators in §5.8 are the spec for the next
`F-018+`-style hardening feature. Two are high-priority:

- **`validate-approvals`** (R-008 ledger) — without this, the
  human gate is honor-system.
- **`validate-trace`** (every commit has a trace line) — D-011
  promise; automated check is the only way to enforce.

The rest are medium/low and can wait for the next refactor.

### 7.9 Profile spec is in design, not code

**Where**: the architecture doc sketches the profile system
(`base.yaml` + specialized profiles + profile-based export
filtering) but the schema, the inheritance semantics, the
versioning, and the `profiles.yaml` location are all **design-
stage**, not implementation. The `base.yaml` profile does not
yet exist on disk.

**Fix**: this is the F-016/next "Profile System" feature
specification. The system-lead owns the design; the build-
lead owns the implementation; the reviewer owns the audit.
R-008 to add a profile kind (it's a routing decision in a
sense — it changes the export surface).

---

## 8 · Glossary of the system-lead's vocabulary

| Term | Meaning |
|---|---|
| **Catalog** | The runtime-neutral markdown + YAML source of truth. Adapters translate. |
| **Live runtime** | `.opencode/`, `.claude/` — generated, disposable. Throwaway. |
| **Brain** | `.aspis/` — durable, tool-neutral. Permanent. The other leads' home. |
| **Tier** | `cheap` / `standard` / `deep` — a cost budget for an agent. |
| **Capability** | A *kind of work* (planning, review, debugging, etc.). The routing seam. |
| **Canonical id** | A model id with no runtime prefix (e.g. `claude-opus-4-8`). Provider-neutral. |
| **Provider** | A model source (anthropic, opencode, opencode-go, minimax, openrouter, github-copilot). |
| **Inventory** | The detected set of runtimes, providers, and models. Generated, git-ignored. |
| **Resolver** | `resolve_model(agent, runtime)` → canonical id → runtime string. |
| **Adapter** | `RuntimeAdapter` — one per runtime (OpenCode, Claude). Owns the translation. |
| **Export** | Catalog → live runtime. The exporter is the system-lead's compiler. |
| **Byte parity** | The live file equals the rendered-catalog file byte-for-byte. |
| **Protected asset** | A file the exporter will not overwrite without an R-008 approval. |
| **Hook** | A script that runs at a boundary (git commit, tool use). Deterministic, no LLM. |
| **Enforcement** | `warn` (report) or `block` (hard wall). One switch. |
| **Drift** | Any of: catalog ↔ inventory, inventory age, live ↔ resolver, live ↔ catalog, protected hash. |
| **Dr. command** | `aspis doctor` — the full health check. |
| **Profile** | A YAML data file that selects which catalog assets a project gets. |
| **Approval ledger** | `.aspis/approvals/<id>.md` — the recorded R-008 sign-off. |
| **Moat** | The byte-parity guarantee: the catalog regenerates live exactly. |
| **R-008** | The human gate. Architecture, rules, permissions, security, model-routing. |
| **/SYS scope** | The commit convention marker for a system-lead-governed change. |

---

*Built from the live config tree (2026-06-26) and the F-016 architecture
synthesis. For the architecture rationale, see `local/AGENT-SYSTEM-ARCHITECTURE.md`.
For the system-agent research, see
`.aspis/features/F-016-agent-system-architecture/Research/system-agent-tooling.md`.
For the rules that ground this spec, see `.aspis/rules/system-rules.md` (R-001 …
R-009) and `.aspis/rules/architecture-constitution.md`.*
