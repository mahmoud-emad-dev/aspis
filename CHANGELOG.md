# Changelog

All notable changes to ASPIS are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (pre-1.0: minor
versions may include breaking changes).

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
