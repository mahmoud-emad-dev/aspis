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
(`operations/init.py`). `init_core`: (1) `plan_export`/`write_export` the profile's assets
(profile defaults to `base`, which ships **both** opencode + claude — `init` narrows to detected
runtimes, falling back to the full list); (2) scaffold brain; (3) ship scripts; (4) seed authored
files; (5) write root files; (6) `git init`; (7) install git hooks; (8) commit the scaffold. It
records `project_mode` (new/empty vs existing-code) because the two follow different downstream
workflows. No runtime-specific logic lives in the core (D-002/D-015); placement/op come from the
asset-kind registry (D-008).
- **FIXED (must not break):** init is **offline + deterministic** (`initializer`'s old contract:
  "offline only, no network, no secrets"); the project is **structurally complete after init**
  (valid even with no internet, before bootstrap); **init owns its own first commit** (ASPIS files
  only — never sweeps the user's existing code, D-011-style staging); init does **no AI** and
  blocks on **no prompt**; both runtimes ship by default.
- **OPEN (free to evolve):** the post-init step that launches guided onboarding; a runtime
  detection menu when none is detected; formal named pre-init/post-init extension points; the
  "installer-feel" UX; brain content rendered from template files vs Python (the old IB-1 gap).

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
  runtimes so `init` deploys `.opencode` + `.claude` (was opencode-only).
