# Subsystem: initialization

- **Status:** active
- **Created:** 2026-06-29   **Last reviewed:** 2026-06-29
- **One-liner:** `aspis init` — the deterministic, offline operation that turns a folder into a structurally complete (but not yet live) ASPIS project.

## Why it exists (problem)
A project needs its full file-first skeleton — runtime assets, the `.aspis/` brain, scripts,
hooks, root guides, git — before any agent or AI touches it. Initialization must be **purely
deterministic**: if the user disconnects from the internet right after `aspis init`, the project
is still valid and complete. It deliberately does *no* AI work and asks (almost) nothing — that
is bootstrapping's job. Splitting the two is what keeps init reproducible, testable, and safe to
run anywhere (CI, automation, offline).

## Responsibilities & boundaries
- **Owns:** export the profile's catalog assets to the runtime dirs + brain; scaffold the
  `.aspis/` brain (placeholders for the index/context files); ship helper scripts; write the
  root guides (`AGENTS.md`, `CLAUDE.md`) with bootstrap-fill slots; `git init` + install git
  hooks + make init's **own** first commit (only ASPIS files, never sweeping user code);
  produce a structurally complete project that validates offline.
- **Does NOT own:** any AI/enrichment or question-asking beyond flags (bootstrapping); making
  the project *live* (bootstrapping); model `--apply`/export resync (models-intelligence);
  understanding existing code deeply (import). Init never depends on a network or a runtime.

## Current behaviour (FIXED vs OPEN)
Runs on the lifecycle engine as **pre-init hooks → `init_core` → post-init hooks**
(`operations/init.py`). `init_core`: (0) **seed the lead model floor** into the project's
`agent-models.yaml` *before* export, so the rendered agents already carry a capable model
(`operations/model_defaults.py`); (1) `plan_export`/`write_export` the profile's assets
(profile defaults to `base`, which ships **both** opencode + claude; the CLI narrows it to the
runtime(s) the user chose); (2) scaffold brain; (3) ship scripts; (4) seed authored files;
(5) write root files; (6) `git init`; (7) install git hooks; (8) commit the scaffold. It records
`project_mode` (new/empty vs existing-code) because the two follow different downstream workflows.
No runtime-specific logic lives in the core (D-002/D-015); placement/op come from the asset-kind
registry (D-008).

**Runtime selection** is a CLI-front-end concern (`commands/init.py` + `operations/runtime_select.py`),
never the deterministic core: when the user passes no `--runtime` and is on a TTY, init detects which
*supported* runtimes are installed and shows a multi-select menu (one or more). If none is installed,
init **never installs anything** — it prints the OpenCode install URL/command and only proceeds with
OpenCode as the default after the user confirms. Headless/CI (no TTY) keeps the profile default. The
core still just receives a resolved runtime list, so it stays non-interactive.
- **FIXED (must not break):** init is **offline + deterministic** (`initializer`'s old contract:
  "offline only, no network, no secrets"); the project is **structurally complete after init**
  (valid even with no internet, before bootstrap); **init owns its own first commit** (ASPIS files
  only — never sweeps the user's existing code, D-011-style staging); init does **no AI**; the
  **core blocks on no prompt** (any prompting lives in the CLI front-end and is TTY-gated, never in
  `init_core`); **init never installs a runtime, and never picks a runtime the user did not choose
  or pin** (menu on a TTY, profile default headless); the **lead model floor is set before the
  export renders the agents** (so it is in place before the runtime TUI/bootstrap), and seeding it
  **only writes the project's `agent-models.yaml`, never the catalog** (the catalog model map stays
  frozen until F-021).
- **OPEN (free to evolve):** the temporary floor *policy* (which leads, which model per runtime) —
  F-021 replaces the static map with subscription-aware "best available within budget" selection;
  formal named pre-init/post-init extension points; the "installer-feel" UX; brain content rendered
  from template files vs Python (the old IB-1 gap).

## Integrations
- **Feeds → bootstrapping**, which consumes the skeleton init produces (slots, manifest-less
  state, promoted-pending agents). **catalog-to-runtime** is the engine init drives (export +
  adapters). **profiles** decide *which* assets ship. **models-intelligence** supplies the
  tier→string at render (currently frozen — do NOT `export`/`models --apply` until that feature).
  **hooks** are installed here. A change to the export engine, profiles, or asset-kinds ripples
  directly into init's output.

## System contracts (guarantees)
After a successful `aspis init`: the runtime dirs (`.opencode/`, `.claude/`) and the `.aspis/`
brain exist and are materialized from the catalog; helper scripts + git hooks are installed;
there is a clean first commit of *only* ASPIS files (user code untouched); the project is
**structurally valid offline** but **not yet live** (no manifest — bootstrap pending); the root
guides carry the bootstrap-fill slots and the (self-stripping) bootstrap gate.

## Future direction (F-020 — re-arch of init & bootstrap; the new vision, not yet built)
Reshape into the **two-layer model**: init becomes an **Operation** (Before → Core → After),
independent of others; a separate **Workflow** layer orchestrates `init → onboarding → (pre-)import
→ bootstrap → ready` so the user normally runs only `aspis init` and is guided the rest of the way
(continue / skip / exit), never needing to remember `bootstrap`/`import`/`models sync`/`runtime
apply`. Add deterministic **Pre-Import discovery** (OS, shell, Python, git, runtimes + versions +
providers + models, project/stack with confidence, existing planning/docs, repo history, tree
cleanliness — read-only). Add a **runtime detection + recommendation menu** (why this runtime →
provider → model), **resume** of an interrupted init, and **installer-feel UX**. Reserve seams
(don't build the platform now): a `CatalogSource` interface (local|remote), named pre/post
extension points, an OS-aware global store, brain-from-templates + a conformance validator. Keep
init offline/deterministic at its core regardless.

## Changelog (append-only, newest last; ARCHITECTURE changes only)
- 2026-06-30 — F-020 (continuation): **runtime detection + selection** and a **lead model floor**
  landed on init. (1) When no `--runtime` is pinned, the CLI front-end detects installed supported
  runtimes and offers a TTY multi-select menu; with none installed it points at OpenCode and asks
  before defaulting — init never installs a runtime and never auto-picks one the user didn't choose.
  The deterministic core is unchanged (it just receives the resolved list). (2) init seeds a
  temporary per-runtime lead model floor (`project-lead`/`bootstrap`/leads → `claude-sonnet-4-6` on
  Claude, `opencode-go/deepseek-v4-pro` on OpenCode) into the project's `project.yaml` **before**
  export, so the leads render with a capable model *before* the user opens the runtime TUI or runs
  bootstrap (first-contact quality). Writes only the project file — the catalog model map stays
  frozen; the full subscription-aware "best available" engine is F-021. New code:
  `operations/runtime_select.py`, `operations/model_defaults.py`; CLI `commands/init.py`. See D-021.
- 2026-06-29 — F-020 started (init/bootstrap UX re-arch). Confirmed direction extending init:
  guided post-init decision screen + automatic follow-through (orchestrated by the new
  `setup-workflow`); a read-only **pre-bootstrap resolution** stage runs after init; and init's
  export must be **complete + current** — every selected agent/skill/instruction/template/script
  exported, none missing or outdated (owner mandate). FIXED invariants unchanged. See
  `.aspis/features/F-020-init-bootstrap-ux/`.
- 2026-06-29 — Intent recorded (F-019) as the baseline before the F-020 init/bootstrap re-arch.
  Captures: original ASPS vision (REFACTOR-ANALYSIS §IB / I1–I12), as-built `operations/init.py`,
  and the new two-layer Operations/Workflow direction. FIXED invariants above are the
  don't-break contract for F-020. Recent fix landed pre-F-019: `base.yaml` now ships both
  runtimes so `init` deploys `.opencode` + `.claude` (was opencode-only).- 2026-06-30 — F-022 (git separation): init now writes the product `.gitignore` shields
  (`.aspis/` + each runtime dir) and, on a fresh project, `git init`s the brain shadow repo at
  `.aspis/` before a **routed** first commit (brain → `.aspis/.git`, root guides → product repo,
  runtime dirs → neither). See the new `git` subsystem; FIXED init invariants preserved.
