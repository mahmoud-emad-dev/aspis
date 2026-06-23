# Changelog

All notable changes to ASPIS are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (pre-1.0: minor
versions may include breaking changes).

## [0.1.0b3.dev0] — unreleased

System hardening (in development on `feat/F-014-system-hardening`): deterministic guarantees,
correct per-agent permissions, scoped context, and fire-and-forget guards.

### Added
- `aspis preflight` (pre-task clean-tree + branch gate), `aspis context` (one-call fresh hot
  context), `aspis findings` (list/resolve guard findings).
- Skills: `prestart-checks`, `context-ladder`, `config-management`, `project-health`.
- Golden tests: every command **and** every delegate an agent uses must be permitted/real.

### Changed
- The committer can run `aspis commit` (the demo_win2 root cause); runtime hooks bake a working
  interpreter so the scope-guard fires on Windows.
- Guards are **fire-and-forget**: no per-tool-call hook; findings are advisory in warn mode; scope
  is checked at the git boundary, which emits findings.
- project-lead is locked to detect-and-route; the build mode is its one direct change.

## [0.1.0b2] — 2026-06-22

Second beta — install, first-run onboarding, and runtime/model correctness.

### Added
- **Self-cleaning bootstrap onboarding** — a transient `bootstrap` agent + skill +
  workflow ship into a project, take it from exported to live in one turn, then
  **remove themselves** once it is bootstrapped. A first-run gate routes any
  un-bootstrapped project through it.
- **Bootstrap proves the git subsystem** — a throwaway probe commit exercises the
  hooks (junk clean, stale `.gitkeep` reap, attribution strip) and rolls back.
- **Bootstrap gates** — doctor + readiness (brain files filled) + validation (config
  & agents parse) + structure (no stray folders); it self-cleans only when green.
- **Runtimes discovered from data** — `data/runtimes/*.yaml` declare detection,
  capabilities (mode, subagent depth, exportable) and run command; `doctor` lists
  them with capabilities. No hardcoded runtime list.
- **`aspis models --apply`** — re-renders the live runtime agents from
  `agent-models.yaml` + `project.yaml`, so a model edit becomes active without a
  re-init (the model is baked into each agent file at export). `--sync --apply`
  refreshes then applies; the generated file now points users to this step.

### Changed
- **Tiered `.aspis/config/`** — a clear three-tier layout so it's obvious what to edit:
  the few you change stay flat (`project.yaml`, `models.yaml`, `agent-models.yaml`),
  seldom-touched policy moves to `config/policy/` (modes, capabilities, hooks,
  commit-convention, constitution-checks), machine data to `config/reference/`
  (model_catalog, providers). A new `config/README.md` explains each file and the
  commands. The config resolver finds a file by bare name across tiers, so a legacy
  flat layout still works.
- **Canonical `.aspis/` structure** — folders are either filled at bootstrap or
  created on demand; no empty `.gitkeep`-only or stray `state/` folders.
- **Model defaults are free, valid, runtime-agnostic** — OpenCode defaults to free
  Zen models (valid `provider/model`); agents use tiers, so a claude-only user's
  onboarding runs on haiku. Full model config now exports, project-overridable.
- **Nature-based gitignores** — root baseline (OS/secrets) + brain hygiene by file
  nature (generated/state ignored, source/durable tracked); offline-first gitignore.
- `bootstrap`/`init` commits are scoped to ASPIS paths (never sweep user code).

### Fixed
- `install.ps1` Python-version detection on Windows (PowerShell quote-stripping).
- `purposes.json` is now self-documenting (layers + worked examples).
- Agent re-render passed the whole `{runtime: inventory}` map (not this runtime's
  entry) into model translation, raising `AttributeError` whenever a detected
  inventory existed (e.g. after `aspis models --sync`). Now selects the runtime entry.

## [0.1.0b1] — 2026-06-21

First public **beta**. ASPIS is a file-first, deterministic agentic software factory:
one runtime-neutral catalog of agents/skills/templates compiles into per-runtime
projects (Claude Code, OpenCode), and a small `aspis` CLI drives the lifecycle.

### Added
- **`aspis` CLI** — `init`, `bootstrap`, `status`, `mode`, `models`, `doctor`,
  `gitignore`, `commit`, `artifact`, `testledger`. Single entry point, pure-Python,
  no runtime dependencies.
- **Catalog → runtime compiler** — one neutral catalog (`src/aspis/data/catalog/`)
  renders to `.claude/` and `.opencode/` via per-runtime adapters; adding a runtime is
  a new adapter, adding an asset is a new file.
- **Profiles** — data-driven asset selection; a project takes only what it declares.
- **Deterministic hooks** — git boundary (pre-commit / commit-msg / post-commit) and a
  runtime tool-use guard; rules are data, non-blocking by default.
- **Git subsystem** — `aspis commit` is the single commit authority: stages named paths,
  composes a convention-checked message, and lets the hooks enforce.
- **Model intelligence (F-010)** — a canonical `model_catalog.yaml` (one entry per model,
  with capability scores, cost, limits); per-runtime **detection** of the connected
  providers/models (OpenCode `auth.json` + `opencode models`, Claude settings); a single
  **resolver** that routes each agent to an available, correctly-spelled model.
  - **Flexible overrides**: per-(runtime, agent) pins and a **`by_capability`** layer that
    configures a 50-agent roster in ~10 lines.
  - `aspis models` (resolution view), `aspis models --available` (the menu),
    `aspis models --sync` (generates the editable `agent-models.yaml` with per-capability
    picks), and **drift detection** in `aspis doctor` (warns when connected plans change).
- **Cross-platform** — Windows and Linux are both supported and CI-gated; UTF-8 stdio,
  `pathlib`, and OS-aware subprocess handling throughout.
- **Docs** — README, QUICKSTART, FIRST-BUILD, INSTALL; SECURITY and CONTRIBUTING.

### Known limitations (beta)
- **Tracing & self-improvement** (Phase 4/5) are not built yet, so model capability
  **scores are hand-seeded** and refined only by future usage data. Hard-limit and
  task-size enforcement are deferred to the run-time/dispatch phase (D-017).
- The dual-runtime dogfood (`.claude` / `.opencode`) is kept in sync by regeneration.
- End-to-end "agent builds a real feature on a real runtime" is the focus of ongoing
  install + usage testing.

[0.1.0b1]: https://github.com/mahmoud-emad-dev/aspis/releases/tag/v0.1.0b1
