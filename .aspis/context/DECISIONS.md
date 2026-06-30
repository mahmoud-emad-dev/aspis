# ASPIS — Decisions

Durable, dated decisions. Append-only; each is the *why* behind something the code
can't explain. Changing one needs a human gate (R-008).

## D-001 — Clean OSS rebuild (2026-06-18)
ASPIS is a clean, publishable rebuild of the older ASPS repo, ported feature by
feature. Bias to lean: avoid the old repo's hardcoding and over-engineering. Keep
what is proven; rebuild it simply.

## D-002 — One catalog, per-runtime adapters (2026-06-18)
A single runtime-neutral catalog (the superset) is the source of truth. Per-runtime
adapters translate and **drop** what a runtime can't express — they never error,
and we never hand-write per-runtime asset files.

## D-003 — Brain vs runtime split (2026-06-18)
A managed project has `.aspis/` (portable, tool-neutral brain) and generated
runtime dirs (`.opencode/`, `.claude/`). The brain is durable; runtime is
rebuildable. The System Lead owns the runtime and protected brain areas; other
leads own the shared brain.

## D-004 — Subagent-by-default + promotion (2026-06-18)
Every agent ships `mode: subagent`; only the Project Lead is primary. Bootstrap
promotes system, planning, build, and reviewer leads to primary → exactly five
primaries. Support leads and workers stay subagents.

## D-005 — Deterministic-first, build-by-need (2026-06-18)
Solve needs with the cheapest mechanism (code → agent → skill → template →
workflow). Build an asset only when a real need appears — no speculative
machinery. (Rejected the secondary spec's pre-built management/registration/audit
skills for this reason.)

## D-006 — Three rule layers (2026-06-18)
Rules live in three scopes — **system** (ours, ship everywhere), **project**
(per-project source of truth), **user** (the user's global learned rules). The
System Lead validates user rules and extracts the project-relevant subset; only
valid rules take effect. An agent loads only the layer relevant to its work.

## D-007 — ASPIS dogfoods itself (2026-06-18)
This factory repo is a live ASPIS project (`.aspis/` + `.opencode/` + `.claude/`).
Subsequent features run through the live planning → build → review loop, so the
catalog is proven by using it.

## D-008 — Everything extensible: asset kinds are data, runtimes declare capability (2026-06-19)
Adding an asset kind must not edit the core. Asset kinds live in one registry
(`assetkinds.py`): any kind a profile names defaults to a brain copy, and only the
rendered/per-runtime kinds carry an override — so a new brain kind (e.g. a future
`knowledge`) is purely additive. Runtimes declare what they accept via
`RuntimeAdapter.supports(kind)`; `export.py` reads placement, write op, and
per-runtime gating from the registry + capability, never from a name check
(`if runtime == "claude"` is banned). Cost-of-change for a new kind/runtime/profile
is ~0 core files. This replaced the F-005 "guards" design, where one kind forced
edits across six core files; F-005/F-006 are backed up and rebuilt on this base.

## D-009 — The architecture constitution is the global engineering-standards layer (2026-06-19)
Beyond the three operational rule layers (system/project/user, D-006), there is a
global engineering-standards layer: `rules/architecture-constitution.md` — how code
and assets are *designed* (cost-of-change, plugin-first, single-source, local-change,
no special cases, capability checks, self-explaining files). It ships everywhere and
governs ASPIS itself. A machine-readable checklist (`config/constitution-checks.yaml`)
maps each rule to the role that enforces it; the planning lead designs to it, the
build lead builds to it, the reviewer checks against it. Standards are a reusable
asset, not prompt text.

## D-010 — Hooks are two deterministic surfaces over one shared core, non-blocking by default (2026-06-20)
Hooks fire at two boundaries: the git **commit boundary** (`pre-commit`, `commit-msg`,
`post-commit`) and the per-runtime **tool-use boundary** (Claude `settings.json`
`PreToolUse`, OpenCode `tool.execute.before`). The scope decision, secret scan, junk
rules, and gitignore logic live once under `.aspis/scripts/hooks/`; both surfaces
import them — no LLM in the pipeline. Rules are data in `config/hooks.yaml`.
**Non-blocking by default**: `enforcement: warn` auto-fixes what it safely can (clean
junk + stale `.gitkeep`, `ruff format`/`--fix` staged code, re-stage) and only reports
scope/secret/protected/message issues, so the project is safe to ship to others; a
single `enforcement: block` switch turns the same checks into hard walls once runtime
blocking is designed — no code change. Git hooks install into `.git/hooks/` (logic
stays version-controlled in `.aspis/scripts/hooks/`); we did **not** add a parallel
`.aspis/githooks/`. Runtime wiring is **adapter-emitted** and capability-gated
(`RuntimeAdapter.emit_runtime_hooks`, D-002): each runtime owns its file's fixed
location. `.gitignore` is sourced from the canonical Toptal API with an offline cache.
Commit scope is optional so repo-lifecycle commits (init/bootstrap) need no feature id.
This replaced the old F-005 "guards" (preserved on `backup/F-005-guards`).

## D-011 — The committer is the single commit authority; it commits through `aspis commit` (2026-06-20)
The git subsystem (F-007) is the **authoring side over the F-006 hooks**. The committer
is the only agent that commits, and it commits through **`aspis commit`**: stage the
explicitly named paths (**never `git add -A`**), compose the message with
`scripts/git/compose.py`, then run `git commit` so the hooks enforce automatically.
The split is **the agent composes, the tool builds the message, the hooks enforce** —
`pre-commit` auto-fixes + checks, `commit-msg` validates the convention, `post-commit`
refreshes the brain. The message rules live once in `commit-convention.yaml` (F-005);
`compose.py` applies them by reusing F-006's `commitmsg.validate`, so there is no second
copy. Three skills ship the human "how" — commit-message, commit-splitting,
clean-tree-precondition. Pushing, PRs, worktrees, and conflict resolution are deferred.
This replaced the old F-006 git cut (preserved on `backup/F-006-git`).

## D-012 — Generated brain indexes are untracked; attribution is matched by phrase (2026-06-20)
Two v0 (F-008) cleanups. (1) The generated brain indexes — `CURRENT_STATE.md`,
`RECENT_CHANGES.md`, `CODE_MAP.md`, `FILE_REGISTRY.yaml` — are **not tracked** in Git.
They are derived artifacts (constitution rule 8, Generated Artifacts), regenerated on
demand / post-commit, so the working tree stays clean after every commit instead of
churning. The init `.gitignore` template ignores them; durable context (DECISIONS,
ARCHITECTURE, ROADMAP, rules) stays tracked. (2) The commit-message attribution check
matches **attribution phrases and credited model names** (`Co-Authored-By`,
"generated with", "by/with <model>", "<model>-generated", 🤖) rather than the bare token
`claude`, so a commit may legitimately name the `.claude` / `.opencode` runtime
directories. Rules stay data in `commit-convention.yaml` (`forbid_attribution` +
`attribution_models`). Also v0: CI runs the gate on a Windows + Linux matrix
(rule 12 / C-PORTABLE), and the README + `docs/QUICKSTART.md` + `docs/FIRST-BUILD.md`
onboard a newcomer. Model routing, OpenCode provider detection, the research subagent,
real-env A/B testing, and tracing are deferred to the post-F-007 backlog.

## D-013 — Feature artifacts are template-driven, tool-created, and mode-gated (2026-06-20)
Agents never hand-author the *shape* of an output. Every feature artifact — the planning
set (SPEC/PLAN/TASKS/TASK_PACKET/ACCEPTANCE), build/feature reports, and review/test
reports — has a template under `catalog/templates/<category>/`, and `aspis artifact <kind>`
copies it into the active feature's folder with the deterministic fields stamped (feature
id + title, task, date), leaving the body for the agent to fill with real results. This
kills format hallucination and saves tokens (one command vs. re-deriving the layout).
Creation is **lazy and mode-gated**: the tool reads the active feature's mode and the
`modes.yaml` knobs (`docs`, `build_review`, `test_depth`), so a lean mode (e.g. `vibe`)
writes no reports unless `--force` — only the artifacts a mode earns are created. Templates
are organised by output purpose (`planning/`, `context/`, `report/`, `review/`); init-only
scaffolding (`AGENTS.md`, `CLAUDE.md`, `gitignore`, `purposes.json`) lives apart in
`catalog/scaffold/` because project agents never author it (D-012 split, refined here).

## D-014 — The brain owns its hygiene; a file-first test ledger skips unchanged re-runs (2026-06-20)
Two related cleanups. (1) **Brain gitignore.** The brain's generated indexes, caches, and
traces are ignored by `.aspis/.gitignore` (paths relative to `.aspis/`), seeded at init —
not scattered through the project-root `.gitignore`. Things that change together live
together: brain hygiene lives with the brain, the root `.gitignore` keeps only project/stack
ignores. (2) **Test ledger.** `aspis tests record|check` keeps a file-first ledger at
`.aspis/index/test-ledger.json` (a local cache, gitignored): a result is stored against a
content **fingerprint** of the files a run covered, keyed by scope (default: active feature).
Before testing, an agent runs `aspis tests check <files>` — a `cached: pass` (fingerprint
unchanged) means reuse the result and skip the run; `stale` means a covered file changed (or
the last run failed) and tests must run, then `record`. The `selective-testing` skill makes
this its first step, so reviewers/tasks stop re-running tests that nothing relevant changed.
Deliberately simple; richer per-run history is the future tracing spine, not this.

## D-015 — Runtime identity lives on the adapter; one source of "which runtimes exist" (2026-06-20)
A runtime's identity — its on-disk dir (`.claude`), its root-guide file (`CLAUDE.md`),
and whether it expresses an agent `mode` — belongs to its adapter, not to scattered
literals. The `RuntimeAdapter` contract gains `runtime_dir` (property, default
`.<name>`), `root_guide` (`str | None`), and `supports_mode` (`bool`); the registry
exposes `runtime_dirs()` and `mode_runtime()`. `detect.py`, `assetkinds.py`, and
`promotion.py` now ask the adapter instead of rebuilding `f".{runtime}"`; init emits a
root guide for any runtime that declares one (no `if "claude"`); lead promotion targets
`mode_runtime()` (no `_MODE_RUNTIME = "opencode"`). We named the capability
**`supports_mode`**, not `promotable`, to avoid colliding with `modes.yaml`'s unrelated
`promotable` knob (whether a *mode's* output can graduate to production). The dead third
source of runtimes — `constants.RUNTIMES` / `settings.runtimes`, which no engine code
read — is removed; the real sources stay **profiles** (which runtimes a project targets)
and **`available_runtimes()`** (auto-discovery of registered adapters). Net: adding or
renaming a runtime is a one-file change, upholding D-008's cost-of-change discipline.

## D-016 — A canonical model catalog is the source of truth; runtime strings are derived (2026-06-21)
A model is defined **once** in `catalog/config/model_catalog.yaml` by a canonical,
provider-neutral id (`minimax-m3`, `claude-opus-4-8`) carrying its facts (provider,
context, capability scores, cost tier, pricing, hard limits, confidence). The *string a
runtime uses* is derived from that id per runtime/provider — the same model is spelled
`opencode-go/minimax-m3`, `minimax/MiniMax-M3`, `openrouter/anthropic/claude-opus-4.8`, or
the Claude alias `opus`. So the `RuntimeAdapter` contract gains `detect()` (what the runtime
offers on this machine — a `RuntimeInventory` of connected providers + available model
strings, or `None` when absent) and `model_string(canonical_id, inventory)` (canonical →
the runtime's exact string, matched against the detected strings; identity by default). The
registry adds `detect_all()`. No core code name-checks a runtime (Constitution #9); a new
runtime is a new adapter, a new model/provider is a data row (#2/#3/#4). The tier map
(`models.yaml`) now holds canonical ids only — a cross-check test forbids drift from the
catalog. `scores`/`confidence` are seeded low and are the field the tracing spine (Phase 4)
later fills — the seam is open, no schema change required.

## D-017 — One resolver routes tier→canonical→runtime string; tier stays the agent dial (2026-06-21)
`models.resolve()` is the single routing engine the adapters call at render. It applies the
full precedence **per-(runtime,agent) pin > per-agent pin > per-(runtime,capability) >
per-capability > project/global tier override > tier map**, then translates the canonical id
into the runtime's exact string via the adapter's `model_string()` against the detected
inventory. With no translate/inventory it returns the canonical id — byte-identical to today's
output — so detection is optional and the system works for any user (FR-006/FR-009). Agents
keep declaring a **tier** (cheap/standard/deep), preserving R-007; capability-aware selection
(`by_capability`) is an additive override layer over the same resolver, not a re-architecture.
The original `effective_model()` is kept intact (its callers/tests unchanged).

**Scope correction (2026-06-21):** hard-`limits` enforcement (FR-007) and `task_size` shaping
(FR-008) are **NOT** applied at render — render does not know the task, so they are a
run-time/dispatch concern. They are **deferred to task dispatch** (the headless-commander /
tracing phase), where a concrete task and its complexity exist. The earlier render-time
implementations were removed as dead code; the catalog still carries `limits` for that future
consumer.

## D-018 — Detection records provider *presence*, never plan/quota or secrets (2026-06-21)
`detect()` answers "what can this machine actually run," not "what plan is the user on" —
because no runtime exposes plan/quota/rate-limit natively (verified). For **OpenCode** it
reads the connected providers from `auth.json` — the **keys only** (`anthropic`,
`opencode-go`, …), never the secret values — resolving the path the XDG way
(`$XDG_DATA_HOME` or `~/.local/share/opencode`; on Windows that is
`%USERPROFILE%\.local\share`, NOT `%APPDATA%` — a verified landmine), and lists available
`provider/model` strings from `opencode models` (only when the binary is present). For
**Claude** it reads the presence of `~/.claude/settings.json` (no secrets) and reports the
durable alias set (`opus`/`sonnet`/`haiku`/`fable`) — aliases, not dated ids, because they
survive model bumps. Both are **cross-platform, env-overridable for testing, and never
raise** — any failure returns `None`/`()` so the resolver degrades to today's tier map
(FR-004/FR-006, Constitution #12). `model_string()` then matches a canonical id against the
detected strings, preferring the lowest-`prefer`-rank *connected* provider (`providers.yaml`),
so routing only ever emits a string the machine can run; with no inventory it is the identity.

## D-019 — Architecture Memory: per-subsystem intent, file-first, updated through a confirmed planning loop (2026-06-29)
A project keeps the *intent* of each subsystem — why it exists, what it owns, what it must
never own, how it integrates, what it guarantees, and how it evolved — as one living markdown
file per subsystem under `.aspis/architecture/subsystems/` (with an advisory `INDEX.md`), so no
future session reconstructs design intent from code, git, or lost chats. It is distinct from the
as-built `ARCHITECTURE.md` (technical shape), `DECISIONS.md` (dated point decisions), planning
artifacts (future work), and `CURRENT_STATE.md` (live status) — it holds *intent*, which none of
them do. The file format is a lean 7 sections; only the **template** is cataloged
(`templates/context/subsystem.md`) — subsystem *instance* files are per-project brain content,
scaffolded by the dedicated `aspis subsystem new|index` verb (not `aspis artifact`, which is
feature-scoped). Updates run through a **mode-gated planning loop** owned by the project-lead via
the `architecture-memory` skill, with planning-lead as detector/consumer: Impact Analysis (pre-plan)
→ read-before-design → record `ARCHITECTURE_IMPACT.md` (`aspis artifact architecture-impact`) →
**explicit user confirmation** → dated, append-only update → post-review verification against approved
intent. The trigger is planning, never git/commits. Gating reuses the existing `architecture` knob
(vibe = read-only, mvp = collapsed, production = full) — it never blocks, slows, or hangs light-mode
work. Grounded in proven patterns (Memory Bank, arc42 building-block view, ADR) and the documented
anti-drift levers (named owner, docs-as-code in-repo, recorded-artifact-on-change, in-workflow);
deliberately no DB, daemon, git hook, auto-update, required-section gate, or new agent. Built as
**F-019** (the number formerly noted for "models", which moves to a later feature).

## D-020 — Init/bootstrap is one guided flow: independent operations, a thin workflow, a deterministic floor (2026-06-29)
First-run is **one command with guided follow-through**, not a sequence the user must memorise.
The shape is two layers: **operations** stay independent (init builds the complete offline shell;
bootstrap personalises + activates) and a thin **setup-workflow** sequences them (post-init decision
screen → onboarding → bootstrap), skippable and resumable. A read-only **pre-bootstrap resolution**
stage (`operations/pre_bootstrap.py`) gathers the truth once into `.aspis/current/bootstrap_state.json`
— a six-state machine (empty/existing-code/initialized-not-onboarded/incomplete-aspis/legacy-aspis/
bootstrapped), runtime inventory (reused, not duplicated), **stack + confidence**, rule layers, and
plan-file detection — which bootstrap then consumes rather than re-deriving. Onboarding is **clear**
(meaning + example + default per question; the three modes explained). The **bootstrap agent asks and
confirms — it never decides stack or mode itself**; it reads the plan file and the system/project/user
rule layers, and may use **research-lead** for "latest/best stack" instead of inventing one. Stack is
**not one-shot** (`aspis stack` corrects it any time). A deterministic **post-heal** (`aspis heal`,
reusing `bootstrap.readiness`) guarantees the brain floor — context, registry, gitignore — when an
agent is weak/offline/failed: **restore of expected files only, never invention** (upholds the
no-autonomous-write rule). All FIXED invariants from the `initialization`/`bootstrapping` subsystem
files are preserved. Models are untouched (the model **decision engine** is F-021; git re-arch is
F-022). Built as **F-020**.

## D-021 — Init chooses the runtime with the user and seeds a lead model floor before the TUI (2026-06-30)
Two additions to init, both upholding init's offline/deterministic core. **(1) Runtime selection is
the user's choice, never a guess.** When no `--runtime` is pinned, the CLI front-end
(`commands/init.py` + `operations/runtime_select.py`) detects which *supported* runtimes are
installed and offers a TTY multi-select menu (one or more). With none installed, init **never
installs anything**: it shows the OpenCode install URL/command and only proceeds with OpenCode as the
default after the user confirms. Headless/CI (no TTY) keeps the profile default. The prompt lives in
the front-end; `init_core` stays non-interactive (it just receives the resolved runtime list).
**(2) A lead model floor is set before export.** First-contact quality depends on the leads
(`project-lead`, `bootstrap`, the other `*-lead`s) not starting on a weak free model, so init seeds a
temporary per-runtime floor into the project's `project.yaml` (the override layer below
`agent-models.yaml`, so it never shadows the user's own routing) **before** the export renders the
agents — in place before the user ever opens the runtime TUI or runs bootstrap. Temporary policy
(`operations/model_defaults.py`): Claude → `claude-sonnet-4-6`, OpenCode → `opencode-go/deepseek-v4-pro`.
This writes **only the project file, never the catalog** (the catalog model map stays frozen); the
full subscription-aware "best available within budget" selection is **F-021**, which replaces the
static floor. `aspis models --sync` preserves these pins; the user can change any of them. Built as
**F-020 (continuation)**.
