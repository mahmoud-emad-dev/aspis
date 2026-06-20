# F-009 — pre-publish review · HANDOFF (for the continuing agent)

You are picking up F-009 (pre-publish hardening) in the **ASPIS** repo. The user is
reviewing the project file-by-file and feeding fix points; some are built, the rest
are listed here. **Continue on the same branch `feat/F-009-prepublish-review`.**

## Session update — T-07..T-12 done (2026-06-20), gate green on WSL, tree clean

Points **7, 8, 9, 10a, 10b, 10c are now BUILT and committed** (each per-unit via `aspis commit`):
- **T-07 — Point 7** (`.gitkeep`): the reaper now counts subdirectories (a subdir-only dir
  like `.aspis/features/` is non-empty → its `.gitkeep` is stale); init won't re-plant into a
  populated dir; the two real strays removed. `scripts/hooks/cleanup.py`, `operations/init.py`.
- **T-08 — Point 9** (hooks): one hooks folder. Lifecycle engine now reads
  `.aspis/scripts/lifecycle/<event>/` (`HOOKS_DIR`); `.aspis/hooks/` removed from the skeleton.
- **T-09 — Point 10b** (templates): categorised into `templates/{planning,context,report,review}/`;
  init-only scaffolding (AGENTS/CLAUDE/gitignore/purposes.json) moved to `catalog/scaffold/` with
  `resources.scaffold()`; `assetkinds.target()` now preserves a sub-path under the kind (was
  basename-only; behaviour-preserving for flat assets).
- **T-10 — Point 8** (artifacts): `aspis artifact <build|feature|review|test|acceptance>` copies a
  template into the active feature folder, stamps fixed fields (id/title/task/date), is mode-gated
  off `modes.yaml` (vibe skips reports unless `--force`), lazy + no-overwrite. New templates under
  `report/`, `review/`, `planning/ACCEPTANCE`. build-lead + reviewer wired. D-013.
- **T-11 — Points 10a + 10c**: brain owns its hygiene via `.aspis/.gitignore` (seeded at init;
  brain entries removed from the project-root `.gitignore`); `aspis tests record|check` = a
  file-first ledger at `.aspis/index/test-ledger.json` keyed by a content fingerprint, so a passing
  test is not re-run while nothing relevant changed. `selective-testing` skill checks it first. D-014.
- **T-12 — dogfood**: regenerated this repo's `.opencode`/`.claude` from the catalog.

Templates were informed by mining the **old ASPS repo** (`../asps/templates/`) and **spec-kit**
(`../asps/local/vendor/spec-kit`) — kept the lean skeletons (BUILD_DONE_STATUS / REVIEW_REPORT
shapes, spec-kit's spec/plan/tasks separation), skipped the museum.

**Still open:** Point 2 (models), Point 3 (modes↔task-size), Point 1c (headless purpose
auto-fill) — all GATED on the user's model file; Point 5 (context consolidation) — user-led.
See sections 2 and 4 below for the model + ASPS-re-analysis detail (still valid).

## 0. Read first / ground rules

- Repo: `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS` (Windows path).
  On WSL it's `/mnt/p/AI_Empire/Projects/Agentic Software Production System/ASPIS`.
- Read `CLAUDE.md`, `.aspis/context/ASPIS_FOUNDATIONS.md` is not present here — read
  `.aspis/context/IDENTITY.md`, `ARCHITECTURE.md` (as-built), `DECISIONS.md`, and this
  feature's `SPEC.md`.
- **Gate (must be green before every commit):**
  `uv run ruff format --check . && uv run ruff check . && uv run pytest -q`
  Always `uv run ...` — bare `python` won't have the tools on PATH.
- **CROSS-PLATFORM IS A HARD RULE (constitution rule 12, C-PORTABLE).** You are on WSL
  (Linux); **Windows is the gate of record.** Everything must run on BOTH. So:
  - Self-contained scripts must call `force_utf8_stdio()` (see `scripts/context/_common.py`
    and `scripts/planning/_console.py`) before printing non-ASCII.
  - Every `subprocess.run` that reads output: pass `text=True, encoding="utf-8",
    errors="replace"`. Never rely on the platform default codec.
  - Use `pathlib`, posix-relative paths, no assumed shell. **A WSL venv breaks `uv` on
    Windows** — do not create/commit a `.venv`; let the user run the Windows gate.
  - When you can't test on Windows, ask the user to run the gate there before merge.
- **COMMITS — git history must read as fully human-authored.** NEVER add `Co-Authored-By`
  or mention Claude/Opus/Sonnet/AI/any model/tool in a commit message, branch, or body.
  (`.claude` / `.opencode` as directory names are fine.) The commit-msg hook enforces this
  and even rejects a message that *quotes* a banned phrase literally — reword if so.
- **Commit per unit** via the committer tool, e.g.:
  `uv run aspis commit <paths...> --type feat --task T-0X --title "..." --bullet "..." --bullet "..."`
  It stages only the named paths (never `-A`), composes the message, and fires the hooks.
  Subject (`type(F-009/T-0X): title`) must be ≤ 72 chars — trim the title if it rejects.
- The post-commit hook regenerates the brain indexes (FILE_REGISTRY/CODE_MAP/CURRENT_STATE/
  RECENT_CHANGES) which are **gitignored** — ignore that output; the tree stays clean.

## 1. DONE on F-009 (do not redo) — commits T-00..T-05

- **T-00** plan (SPEC + active_feature → F-009).
- **Point 1 — file-purpose registry. DONE.**
  - `scripts/context/build_registry.py`: three-layer purpose resolution. All project
    purposes live in ONE file **`.aspis/config/purposes.json`** (`files` = exact per-path;
    `names`/`patterns` = common map over built-in defaults). Authoritative for known
    meta-files (README/LICENSE/.gitignore/lockfiles/CI) whose first line is a title.
  - **`build_registry.py --check`** lists every file with no purpose and exits 1 (coverage
    gate). Repo is at 178/178 covered; uncovered files get registered in `purposes.json`.
  - Seeded at init (`operations/init.py` `_seed_authored_files`), template
    `templates/purposes.json`. AGENTS.md template documents it. Skeleton-lookup already
    existed: `build_code_map.py --scope <path>`.
- **Point 6 — active-feature integrity. DONE.** `scripts/planning/active_feature.py`
  (read/validate/set-phase) + switch-guard in `feature_scaffold.py` (refuses to overwrite
  an unfinished pointer unless `--force`); terminal phases done/merged/abandoned;
  `active_feature.py --check` validates fields/dir/phase/branch.
- **Point 4 — dual architecture. DONE.** `templates/ARCHITECTURE.md` seeded into
  `.aspis/context/ARCHITECTURE.md` (as-built truth); convention: `docs/ARCHITECTURE.md`
  (or root) = fixed INTENDED arch the planning lead reads for the next feature; as-built =
  what build-lead/reviewer compare against. Agents wired.

## 2. REMAINING — original review points

- **Point 1c — auto-fill missing purposes via a headless cheap model ("CLI commander"
  tier).** When `--check` finds a file with no purpose, a background script should call a
  cheap model **non-interactively** (no TUI) to generate the purpose and write it into
  `purposes.json` `files`. Design: a runtime-agnostic helper that reads a configured
  headless command from `.aspis/config/` (e.g. `opencode run -m <cheap-model> "<prompt>"`
  or `claude -p "<prompt>" --model <cheap-model>`), defaulting to no-op until configured.
  This is the seed of a general **headless-commander agent tier** (agents/commands meant to
  be invoked from scripts with a cheap model, not opened in a runtime). **Gated** on the
  models work below (needs the cheap-model id + the runtime's headless invocation) — design
  it now, wire the actual command once models land. Confirm approach with the user.
- **Point 2 — models. GATED on user's model knowledge.** GOOD NEWS: the routing machinery
  already exists and is exactly right — agents declare a tier (`model: cheap|standard|deep`
  in frontmatter); `config/models.yaml` maps tier→concrete id **per runtime**; projects
  override/pin in `.aspis/config/project.yaml`; resolution in `models.py` /
  `runtimes/base.py`. ONLY the concrete ids are placeholder. The Claude column is right
  (opus-4.8/sonnet-4.6/haiku-4.5). The OpenCode column is invented and needs: real ids
  with **provider-prefixed names** per the connected plan; a **free/no-subscription**
  default set so users can test; a **provider/subscription detection** step (opencode
  zen/go, minimax token, codex/openai-pro, glm, deepseek API, OpenRouter, raw API — each
  writes model names differently); optional **per-role pins** (UI vs backend vs plan).
  Wait for the user's model file, then it's mostly a `models.yaml` data edit + a detection
  script + a free-tier override.
- **Point 3 — modes ↔ task size. GATED (rides with models).** Task size = f(mode, model
  capability): vibe = larger direct tasks on a frontier model (lead builds directly, fewer
  subagents) + lighter-but-present SPEC/architecture; cheap/weaker model → medium/small
  tasks. Production = deep. Implement a real size calc once model-capability data exists.
  See `config/modes.yaml`, `task_compile.py`, `task-decomposition` skill.
- **Point 5 — context-file consolidation + identity discipline. USER-LED.** The user is
  reviewing `.aspis/context/` (CORE_LOOP, ROADMAP, IDENTITY, DECISIONS, ARCHITECTURE) for
  merges/staleness. **Do NOT merge these pre-emptively.** Execute only consolidations the
  user calls out. Keep IDENTITY short; it grows only via a strict workflow, system-agent only.

## 3. REMAINING — new points 7–10 (verified against the repo)

- **Point 7 — strip stray `.gitkeep`.** A `.gitkeep` must exist ONLY in an empty dir.
  VERIFIED stray today: `.aspis/features/.gitkeep` (5 other files), `.aspis/scripts/.gitkeep`
  (3 other files). Build a cleanup step (extend `scripts/hooks/cleanup.py` or a context
  script) that removes any `.gitkeep` from a now-non-empty dir, run it in the lifecycle
  (init/post-commit), and ensure init doesn't re-plant `.gitkeep` into populated brain dirs.
  Confirm the brain-scaffold (`_scaffold_brain`) + export aren't re-creating them.
- **Point 8 — production feature folder = complete artifacts, template-driven, lazily
  created.** A production-mode feature should be able to hold: SPEC, PLAN, TASKS,
  ACCEPTANCE, (review), per-task **packet** folders, plus **report** folders — a builder
  report per task and a reviewer/test report per task (with dates/times). BUT: agents must
  NOT hand-author these — a **tool copies the template** from `templates/` into the target
  feature folder. AND creation is **mode/model-gated**: vibe/MVP or a frontier
  planner-builder may skip reports/packet-folders; only create folders/files when actually
  needed/done. New templates needed (see point 10). Today the feature dir is just
  SPEC/PLAN/TASKS + empty `tasks/`. `feature_scaffold.py` is where the copy-tool lives.
- **Point 9 — remove the duplicate hooks dir.** VERIFIED: `.aspis/hooks/` is empty (only
  `.gitkeep`); `.aspis/scripts/hooks/` holds the real scripts. Remove `.aspis/hooks` from
  the brain skeleton (`src/aspis/data/brain.yaml` dirs list) and delete the empty dir; keep
  `.aspis/scripts/hooks/`. Check nothing references `.aspis/hooks/` (grep configs/agents).
- **Point 10 — system `.gitignore` for `.aspis/` + categorized templates + an incremental
  test ledger.**
  - (a) Add a `.gitignore` scoped to the ASPIS system's own generated artifacts (the brain
    indexes are already gitignored at root — decide whether a `.aspis/.gitignore` is cleaner).
  - (b) **Templates are flat today** (9 files in `catalog/templates/`). Organize into
    **categories/subfolders**: e.g. `templates/feature/`, `templates/planning/` (spec,
    plan, tasks, analysis-checklist, analysis-report), `templates/review/` (review
    checklist, task-review report, lead-review, testing report), `templates/report/`
    (builder/task report, feature-result report), `templates/context/`. Update
    `resources.template()` / loaders and any references (init `_write_root_files`,
    `_seed_authored_files`, `feature_scaffold.py`, tests) — `resources.template(name)`
    currently assumes a flat dir, so this touches the loader signature.
  - (c) **Incremental test ledger / cache.** Tests added while building or reviewing a
    feature accumulate into ONE file recorded with dates/times — a cache. Give the
    reviewer/tester a tool that, before running a test, checks whether it already ran with
    no relevant change (by git/file state) and returns the cached result instead of
    re-running. Avoids duplicate test runs across tasks/agents. (Design carefully; this
    overlaps the future tracing spine — keep it simple/file-first first.)

## 4. ASPS predecessor re-analysis (user asked)

ASPIS is the rebuilt successor of the older **ASPS** repo
(`P:\AI_Empire\Projects\Agentic Software Production System\ASPS`, the current shell cwd).
TASK: skim ASPS for any pattern/feature worth salvaging into ASPIS before publish
(e.g. tracing, dashboard, analyze-session loop, roster specifics) and note keepers vs
drop. Don't copy blindly — ASPIS is the clean, cross-platform, file-first line. Memory
index for ASPS history: `C:\Users\mahah\.claude\projects\...\memory\MEMORY.md`.

## 5. Suggested order for the continuing agent

1. Point 9 (delete duplicate hooks dir) — tiny, verified, self-contained.
2. Point 7 (.gitkeep cleanup script + lifecycle wiring) — self-contained.
3. Point 10b (categorize templates) — mechanical but touches the loader; do before point 8.
4. Point 8 (template-driven, lazily-created feature artifacts) — depends on 10b templates.
5. Point 10a (.aspis gitignore), 10c (test ledger) — design, confirm with user.
6. Point 1c (headless purpose auto-fill) + Points 2/3 (models) — when the user delivers the
   model knowledge.
7. Point 5 — only as the user directs.

Keep every change tested and the Windows gate green. Commit per unit with `aspis commit`.
When a sub-point completes the feature's intent, mark phase via
`uv run python .aspis/scripts/planning/active_feature.py . --set-phase <phase>`.
