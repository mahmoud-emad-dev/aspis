# F-016 Research — Current ASPIS System Audit

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Phase:** plan
> **Compiled:** 2026-06-25
> **Scope:** every agent, skill, script, template, hook, workflow, command, config, source module, and test in the current ASPIS repository
> **Source:** live tree at `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS` (the project dogfoods itself)
> **Purpose:** the baseline F-016 plans against — what's in, what's wired, what's stubbed, what's missing.

---

## 0 · One-paragraph mental model

ASPIS is a **file-first, deterministic, multi-runtime agentic software-production factory** structured as a 3-layer transform — **catalog → brain → runtime → product** — with a Python engine (`aspis` CLI), a runtime-neutral catalog under `src/aspis/data/catalog/`, per-runtime adapters for OpenCode and Claude Code, a portable brain at `.aspis/`, generated runtime dirs (`.opencode/`, `.claude/`), and a deterministic git-hook subsystem. The system ships **12 agents, 38 skills, 5 commands, 6 workflows, 10 templates, 11 config files, 15+ scripts across 4 script groups, 33 Python source modules, 5 runtime adapters, and 59 test files**. It is operationally "Parts 1–2 of 6" per the ROADMAP — install/onboarding and the production system are live; tracing, intelligence, the dashboard, and scale are deferred.

---

## 1 · Agent inventory (12 agents, 3-layer delegation)

All agent files live in **catalog** (single source) at `src/aspis/data/catalog/agents/` and **deployed** at `.opencode/agents/` (with a parallel Claude render at `.claude/agents/`). Every agent is "thin" (R-006): identity + responsibilities + skill references, no inline procedures. The catalog is the superset; the adapter translates per runtime.

| # | Agent | Mode | Model | Webfetch | Delegates to | Skills (referenced) |
|---|---|---|---|---|---|---|
| 1 | **project-lead** | **primary** | standard | deny | bootstrap, planning-lead, build-lead, reviewer, research-lead, test-lead, fix-lead, system-lead, project-explorer | project-awareness, context-ladder, request-classification, lead-routing, context-packaging, project-question-answering, project-guidance, project-health |
| 2 | **bootstrap** | **primary** | standard | deny | (none — leaf) | prestart-checks, project-onboarding |
| 3 | **planning-lead** | subagent | deep | deny | research-lead, reviewer, project-explorer | prestart-checks, context-ladder, planning-intake, requirement-clarification, feature-planning, architecture-planning, task-decomposition |
| 4 | **build-lead** | subagent | deep | deny | general-builder, reviewer, test-lead, fix-lead, committer, project-explorer | prestart-checks, context-ladder, build-readiness, task-orchestration, scope-control, selective-testing |
| 5 | **reviewer** | subagent | deep | deny | project-explorer | context-ladder, review-strategy, quality-review, acceptance-decision, plan-critic |
| 6 | **system-lead** | subagent | deep | **allow** | project-explorer | prestart-checks, system-awareness, deterministic-first, asset-authoring, system-validation, system-repair, config-management |
| 7 | **research-lead** | subagent | deep | **allow** | (none) | context-ladder, knowledge-research, knowledge-packaging |
| 8 | **test-lead** | subagent | standard | deny | project-explorer | test-generation, test-execution |
| 9 | **fix-lead** | subagent | deep | deny | reviewer, committer, project-explorer | prestart-checks, context-ladder, root-cause-analysis, corrective-fix, scope-control, selective-testing |
| 10 | **general-builder** | subagent | cheap | deny | (none — leaf) | (none) |
| 11 | **committer** | subagent | cheap | deny | (none — leaf) | (implicit: commit-message, commit-splitting, clean-tree-precondition) |
| 12 | **project-explorer** | subagent | cheap | deny | (none — leaf) | (implicit: context-ladder) |

### 1.1 Promotion (D-004 + D-026, refined)

Every agent ships `mode: subagent`; only `project-lead` is primary out of the box. Bootstrap promotes exactly four agents to primary (`PROMOTE_TO_PRIMARY` in `src/aspis/constants.py:22`):

```python
PROMOTE_TO_PRIMARY = ("system-lead", "planning-lead", "build-lead", "reviewer")
```

Yielding **exactly 5 primaries** after bootstrap: project-lead + system-lead + planning-lead + build-lead + reviewer. The remaining 7 (bootstrap, research-lead, test-lead, fix-lead, general-builder, committer, project-explorer) stay subagents. Promotion targets the adapter that declares `supports_mode: true` (OpenCode) — asked of the adapter, not hardcoded (D-015).

### 1.2 Bash-permission policy per agent

Every agent declares a `permissions.bash` map with `*: deny` plus an allow-list of whitelisted commands. Pattern (from `project-lead`):

```yaml
permissions:
  bash:
    "*": deny
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "aspis bootstrap --check*": allow
    "aspis status*": allow
    "aspis doctor*": allow
    "aspis mode*": allow
    "aspis context*": allow
    "python .aspis/scripts/context/*": allow
    "python3 .aspis/scripts/context/*": allow
  webfetch: deny
  websearch: deny
```

**Universal prohibitions across all agents** (R-001, R-002, R-004 enforcement):
- `git commit*` is **denied** for every lead and worker — only `committer` may commit (R-004).
- `git push*` is **denied** for every agent — pushing is human-gated.
- `webfetch`/`websearch` are **denied by default** — only system-lead and research-lead allow them (because their job is to read or write the web).

### 1.3 Frontmatter shape (catalog contract)

Catalog agents parse into a `CatalogAgent` dataclass (`src/aspis/catalog.py:21-61`) with these fields:

```yaml
name, description, mode, model, temperature, tools, permissions,
delegates, skills, runtimes, export_scope, body
```

- `mode`: `primary | subagent`
- `model`: `cheap | standard | deep` (a tier; resolved to a model id at render)
- `tools`: canonical tokens (`read, grep, glob, edit, write, bash, webfetch, websearch`) mapped per-runtime
- `permissions.bash`: pattern → allow/ask/deny
- `delegates`: agent names this one may call (OpenCode renders as `permission.task`)
- `skills`: skill names this one may use (OpenCode renders as `permission.skill`)
- `runtimes`: lock list (empty = all runtimes)
- `export_scope`: `all | export-only | project-only`

### 1.4 Bootstrap gate (transient first-run scaffolding)

The `bootstrap` agent carries a `ASPIS:BOOTSTRAP-GATE` block in its instructions and a `export_scope: export-only` marker. After a successful bootstrap, **the bootstrap agent, the `project-onboarding` skill, and the `bootstrap.md` workflow are removed from the project runtime** (the self-clean logic in `src/aspis/operations/bootstrap.py:379-437`). So in a live, post-bootstrap project, the working agent count is **11** (no bootstrap).

---

## 2 · Skill inventory (38 skills, 9 themes)

Every skill lives as `src/aspis/data/catalog/skills/<name>/SKILL.md` (YAML frontmatter `name` + `description`, then a brief body with Purpose / When to use / Procedure / Outputs / Anti-patterns). Deployed to `.opencode/skills/<name>/SKILL.md` (and Claude's auto-discovery render).

### 2.1 The full 38-skill inventory

| # | Skill | Used by (selected) | What it does |
|---|---|---|---|
| 1 | acceptance-decision | reviewer | Render the verdict (approve / approve-with-notes / changes-required / rejected) and route the fix. |
| 2 | architecture-planning | planning-lead | Design the technical approach, components, dependencies; gate-check vs architecture constitution. |
| 3 | asset-authoring | system-lead | Author a catalog asset correctly (runtime-neutral, thin, single-sourced, wired). |
| 4 | build-readiness | build-lead | Confirm the work can safely start (clean tree, branch, feature pointer). |
| 5 | clean-tree-precondition | committer (implicit) | Start from a clean tree (R-004). |
| 6 | commit-message | committer (implicit) | Conventional ASPIS commit-message shape. |
| 7 | commit-splitting | committer (implicit) | Keep commits atomic — split mixed change sets. |
| 8 | config-management | system-lead | Change config (models, mode, policy, stack) only via the `aspis` commands. |
| 9 | context-ladder | all leads | How much project context to load and in what order (L1 → L4). |
| 10 | context-packaging | project-lead | Build the delegation packet (intent · context · constraints · references · expected outcome). |
| 11 | corrective-fix | fix-lead | Smallest safe correction; fix cause, not symptom; no unrelated changes. |
| 12 | deterministic-first | system-lead | Pick the cheapest mechanism that works (script → tool → workflow → agent). |
| 13 | feature-planning | planning-lead | Write the SPEC (goal, scope, behavior, FR-###, SC-###). |
| 14 | knowledge-packaging | research-lead | Turn findings into a reusable reference asset. |
| 15 | knowledge-research | research-lead | Find and verify current, authoritative knowledge. |
| 16 | lead-routing | project-lead | Choose the specialist lead that owns the work. |
| 17 | plan-critic | reviewer | Check a plan for cross-artifact consistency (spec↔plan↔tasks) before build. |
| 18 | planning-intake | planning-lead | Classify the work and size it; read `modes.yaml`. |
| 19 | prestart-checks | all editing agents | Run `aspis preflight` first; resolve blockers before editing. |
| 20 | project-awareness | project-lead | Build a fast, accurate picture of the project on demand. |
| 21 | project-guidance | project-lead | Steer the user toward the correct next step. |
| 22 | project-health | project-lead | Detect unhealthy/missing state and route to the right lead. |
| 23 | project-onboarding | bootstrap (transient) | One-time procedure: understand → confirm → `aspis bootstrap` → enrich → verify. |
| 24 | project-question-answering | project-lead | Answer directly from project intelligence. |
| 25 | quality-review | reviewer | Evaluate the in-scope quality dimensions against the SPEC's FR/SC. |
| 26 | request-classification | project-lead | Turn a raw user request into intent, type, complexity, recommended path. |
| 27 | requirement-clarification | planning-lead | Resolve assumptions, ask at most 5 real questions. |
| 28 | review-strategy | reviewer | Decide what to review and how deeply, scaled to risk + mode. |
| 29 | root-cause-analysis | fix-lead | Find the true cause of a failure, reproduce, then trace. |
| 30 | scope-control | build-lead, fix-lead | Keep work inside planned boundaries; no architecture drift. |
| 31 | selective-testing | build-lead, fix-lead | Test proportional to impact, not the whole suite every time. |
| 32 | system-awareness | system-lead | Understand the system before changing it (inventory, wiring, impact). |
| 33 | system-repair | system-lead | Restore a broken runtime or corrupted system state. |
| 34 | system-validation | system-lead | Validate a system change (parse, render, gate). |
| 35 | task-decomposition | planning-lead | Break an approved plan into build-ready task packets. |
| 36 | task-orchestration | build-lead | Validate, enrich, delegate, and track tasks. |
| 37 | test-execution | test-lead | Run tests and capture objective evidence. |
| 38 | test-generation | test-lead | Design tests that exercise real behavior (happy path, edges, failures). |

### 2.2 Themes

- **Project intelligence** (project-lead): 1, 9, 10, 20–24, 26 — 7 skills
- **Planning** (planning-lead): 2, 12, 13, 17, 18, 27, 35 — 7 skills
- **Build** (build-lead): 4, 11, 30, 31, 36 — 5 skills
- **Review** (reviewer): 1, 9, 17, 25, 28 — 5 skills (1, 9 shared)
- **Research** (research-lead): 14, 15 — 2 skills
- **Test** (test-lead): 37, 38 — 2 skills
- **Fix** (fix-lead): 9, 11, 29, 30, 31 — 5 skills (sharing with build)
- **System** (system-lead): 3, 8, 12, 32–34 — 5 skills
- **Commit** (committer): 5, 6, 7 — 3 skills (referenced implicitly)
- **Cross-cutting**: context-ladder, prestart-checks — 2 skills

---

## 3 · Command inventory (15 CLI commands)

The CLI is registered in `src/aspis/cli.py`; each verb is its own module under `src/aspis/commands/`. Adding a command = new module + entry in `COMMAND_MODULES` (`src/aspis/commands/__init__.py:30-45`).

| # | Command | Module | What it does | Args |
|---|---|---|---|---|
| 1 | `aspis init` | `init.py` | Scaffold a project + export runtime assets (dry-run by default). | `--profile`, `--runtime`, `--name`, `--write`, `--force`, `--apply`, `--strict`, `--scope`, `--force-conflicts`, `--reset-snapshot`, `--no-git`, `--dry-run` |
| 2 | `aspis bootstrap` | `bootstrap.py` | One-time onboarding: collect project state, fill slots, write manifest, promote leads, brain-fill, git self-test. | `--name`, `--goal`, `--stack`, `--plan`, `-y`, `--write`, `--check` |
| 3 | `aspis status` | `status.py` | Report whether a directory is an ASPIS project. | (path) |
| 4 | `aspis mode` | `mode.py` | Show or set the project's default build mode. | `<mode>` (`vibe`/`mvp`/`production`), `--path` |
| 5 | `aspis models` | `models.py` | See and assign the models each agent uses, per runtime. | `--path`, `--available`, `--sync`, `--apply`, `--force` |
| 6 | `aspis gitignore` | `gitignore.py` | Write/refresh `.gitignore` for the project's stack (Toptal + offline cache). | `<stack>`, `--path` |
| 7 | `aspis commit` | `commit.py` | Stage explicit paths, compose a conventional message, commit. **Never `-A`**. | `<paths...>`, `--type`, `--title`, `--task`, `--bullet` (repeatable), `--tasks`, `--no-scope`, `--path` |
| 8 | `aspis commits` | `commits.py` | Audit (and optionally fix) commit-message history against the convention. | `--path`, `--audit`, `--fix`, `--limit` |
| 9 | `aspis artifact` | `artifact.py` | Create a feature artifact from its template (build/feature/review/test/acceptance). **Mode-gated** (D-013). | `<kind>`, `--task`, `--path`, `--force` |
| 10 | `aspis tests` | `testledger.py` | File-first test ledger: skip re-running tests whose files haven't changed. | `<action: check\|record>`, `<paths...>`, `--scope`, `--result`, `--detail`, `--path` |
| 11 | `aspis preflight` | `preflight.py` | Pre-task gate: clean tree, branch matches active feature, open findings. | (path) |
| 12 | `aspis context` | `context.py` | Refresh the brain + print L1 hot context in one call. | (path), `--no-refresh` |
| 13 | `aspis findings` | `findings.py` | List and resolve open project findings. | (path), `--resolve N`, `--clear` |
| 14 | `aspis doctor` | `doctor.py` | Health check (python, git, project, runtime-hooks) + model drift + commit health. | (path), `-v`/`--verbose` |
| 15 | `aspis uninstall` | `uninstall.py` | Remove machine-wide ASPIS state (keeps project brains). | `--write`, `--keep-config` |

In addition, four `commands` exist in the **catalog** (deployed to `.opencode/commands/` and `.claude/commands/` as chat shortcuts):

| Catalog command | Maps to | Body |
|---|---|---|
| `plan.md` | planning-lead | Plan the work, follow `.aspis/workflows/plan.md`, start with `planning-intake`. |
| `build.md` | build-lead | Build the feature, follow `.aspis/workflows/build.md`, confirm prereq-validate. |
| `review.md` | reviewer | Review the change, follow `.aspis/workflows/review.md`, render the verdict. |
| `status.md` | project-lead | Report where the project stands; read L1 files. |
| `system.md` | system-lead | System-domain work; use `system-awareness`, `asset-authoring`, `system-validation`. |

These are the **/plan /build /review /system /status** entry points the project-lead routes to (per `CORE_LOOP.md` §10).

---

## 4 · Script inventory (15 deterministic scripts, 4 groups)

Scripts are the deterministic spine. They live in the catalog at `src/aspis/data/catalog/scripts/` and ship to `.aspis/scripts/` via init. They are stdlib-only so a target project needs no extra dependencies.

### 4.1 Context scripts (`scripts/context/`) — 6 files

| File | Purpose |
|---|---|
| `_common.py` | Shared helpers (paths, git, UTF-8 stdio). |
| `build_code_map.py` | Build `.aspis/index/CODE_MAP.md` (signatures + imports per Python file). |
| `build_registry.py` | Build `.aspis/index/FILE_REGISTRY.yaml` (every file's purpose). |
| `build_state.py` | Build `.aspis/context/CURRENT_STATE.md` (project/branch/last-commit). |
| `record_changes.py` | Append the latest commits to `.aspis/context/RECENT_CHANGES.md`. |
| `update.py` | Refresh all four: registry, code_map, state, recent_changes (post-commit hook target). |

### 4.2 Git scripts (`scripts/git/`) — 1 file

| File | Purpose |
|---|---|
| `compose.py` | Build a convention-valid commit message (`aspis commit` uses this; reuses F-006's `commitmsg.validate`). |

### 4.3 Hook scripts (`scripts/hooks/`) — 11 files

| File | Purpose |
|---|---|
| `_config.py` | Hook-side config loader (UTF-8 stdio, env handling). |
| `_git.py` | Hook-side git helpers (staged files, repo root, add). |
| `cleanup.py` | Clean junk (zero-byte shell-redirect ghosts) + stale `.gitkeep`. |
| `commitmsg.py` | Validate the message; apply auto-fixes (attribution strip, skip-marker). |
| `findings.py` | Emit a finding (used by `runtime_guard` to flag out-of-scope tool calls). |
| `gitignore.py` | Toptal-sourced `.gitignore` maintainer with offline cache. |
| `install.py` | Install the git hooks into `.git/hooks/` (idempotent). |
| `postcommit.py` | Refresh the brain (run `update.py`); record recent changes. |
| `precommit.py` | Auto-fix (ruff format/check), then check (scope, secrets, R-009 protected). |
| `runtime_guard.py` | Per-tool-use scope guard (wired via `settings.json` / `plugin.ts`). |
| `scope.py` | Allowed-files scope check against the active feature's allowed list. |
| `secret_scan.py` | Secret-pattern scanner (AWS, GitHub, Slack, generic `api_key=…`). |

### 4.4 Planning scripts (`scripts/planning/`) — 5 files (CORE_LOOP §10 deliverables)

| File | Purpose |
|---|---|
| `_console.py` | Shared stdlib-only console helper. |
| `active_feature.py` | Read/write `.aspis/current/active_feature.json`. |
| `feature_scaffold.py` | Allocate `F-NNN`, create `.aspis/features/<id>/`, copy SPEC/PLAN/TASKS, write the active pointer, create+checkout the branch. |
| `prereq_validate.py` | Gate phase order (no plan without a spec; no build without tasks); relaxed by mode. |
| `task_compile.py` | Compile `TASKS.md` → one self-contained packet per task into `tasks/`. |

### 4.5 Runtime hooks (per-runtime, 2 files)

| File | Runtime | What it does |
|---|---|---|
| `runtime-hooks/claude/settings.json` | Claude | `PreToolUse` + `SessionStart` hooks wired to the scope-guard + session-notice scripts. |
| `runtime-hooks/opencode/session-notice.ts` | OpenCode | A plugin that surfaces open findings on `session.created`. |

These are adapter-owned (D-015): each runtime declares its `runtime_hooks` map; the adapter's `emit_runtime_hooks()` writes them, baking the interpreter path at install so they work on Windows + Linux.

---

## 5 · Template inventory (10 templates, 4 categories)

Templates live in `src/aspis/data/catalog/templates/`. They are **not filled at init** (D-013) — only the *active feature's* artifacts are stamped by `aspis artifact <kind>` on demand, mode-gated.

| Category | File | Purpose | Stamped by | Mode gate |
|---|---|---|---|---|
| `context/` | `ARCHITECTURE.md` | Skeleton for the project's as-built architecture. | init seeds it; bootstrap enriches. | n/a |
| `planning/` | `SPEC.md` | Feature specification (goal, scope, stories, FR-###, SC-###, clarifications). | feature_scaffold.py (per feature) | per mode |
| `planning/` | `PLAN.md` | Implementation plan (summary, technical context, components, steps, risks, rollback). | feature_scaffold.py (per feature) | per mode |
| `planning/` | `TASKS.md` | Tasks list (phased, `[P]` parallel, `[US]` story-traceable). | feature_scaffold.py (per feature) | per mode |
| `planning/` | `TASK_PACKET.md` | Self-contained per-task packet for a context-isolated builder. | task_compile.py (per task) | per mode |
| `planning/` | `ACCEPTANCE.md` | Acceptance criteria for the feature. | `aspis artifact acceptance` | none |
| `report/` | `build.md` | Per-task build report. | `aspis artifact build --task T-NN` | `docs != none` |
| `report/` | `feature.md` | Feature-level report. | `aspis artifact feature` | `docs != none` |
| `review/` | `review.md` | Per-task review report. | `aspis artifact review --task T-NN` | `build_review != light` |
| `review/` | `test.md` | Per-task test report. | `aspis artifact test --task T-NN` | `test_depth != gate` |

### 5.1 Mode-gating logic (D-013)

`aspis artifact` reads the active feature's mode and the `modes.yaml` knob:

| Kind | Mode knob | Skip when |
|---|---|---|
| `build` | `docs` | `none` |
| `feature` | `docs` | `none` |
| `review` | `build_review` | `light` |
| `test` | `test_depth` | `gate` |
| `acceptance` | (none) | never skipped |

So a `vibe`-mode feature creates no `build.md`/`feature.md`/`review.md`/`test.md`; an `mvp`-mode feature creates no `review.md`; a `production`-mode feature creates all four. Lean modes write no reports; agents earn them with rigor.

---

## 6 · Workflow inventory (6 workflow docs)

Workflows live in **catalog** (deployed via init) at `src/aspis/data/catalog/workflows/` and are shipped to `.aspis/workflows/` in every project. They are the **steps-as-data** the leads follow (CORE_LOOP §9), so procedures are written down and versioned.

| # | Workflow | Owner | Mode overlays |
|---|---|---|---|
| 1 | `bootstrap.md` | bootstrap (transient) | Two modes: SEED (create `.aspis/`, install hooks, init git) / RESUME (re-validate existing). |
| 2 | `plan.md` | planning-lead | vibe → compress step 4, skip steps 5 + 7, coarse step 6; mvp → light PLAN, self-check; production → full + independent reviewer. |
| 3 | `build.md` | build-lead | vibe → one light pass + gate; mvp → standard review + core paths; production → full multi-lens + tests-as-spec. |
| 4 | `review.md` | reviewer | vibe → one light pass (does it run, in-scope, nothing obviously broken); mvp → standard; production → full multi-lens. |
| 5 | `fix.md` | fix-lead | Fixes default to **production rigor regardless of feature mode** (a defect that escaped is evidence the bar was too low). |
| 6 | `small-task.md` | (no lead) | The lightweight track for one coherent low-risk change — no spec, no architecture, one packet. |

Each workflow has the same shape: **When to use · Prerequisites · Steps (numbered, names the skill) · Mode overlays · Outputs · Handoff**. The Build Lead's `build.md` is 43 lines; the system reads them in full at handoff and follows them step-by-step.

---

## 7 · Config inventory (11 config files, 3 tiers)

Config is **tiered** (D-013, refined): Tier 1 = flat in `config/` (what you edit); Tier 2 = `config/policy/` (rarely edited); Tier 3 = `config/reference/` (do not edit — machine data). The resolver (`src/aspis/resources.py:97-114`) searches flat first, then `policy/`, then `reference/`, so callers never spell the tier.

### 7.1 Tier 1 — the files you actually edit (3 files)

| File | What it configures |
|---|---|
| `config/project.yaml` | The project's default build mode + any per-(runtime, agent) model overrides. The single most-edited file. |
| `config/models.yaml` | Tier → canonical model id map, per runtime. The global default. |
| `config/agent-models.yaml` | Per-agent model assignment (generated by `aspis models --sync`, then hand-edited). |
| `config/purposes.json` | File-purpose registry (one-line purpose per file the registry can't infer from a docstring). |
| `config/README.md` | A 115-line guide: "what to edit, what to leave." |

### 7.2 Tier 2 — policy (rarely edited; 6 files)

| File | What it configures |
|---|---|
| `config/policy/modes.yaml` | The three build modes (`vibe`/`mvp`/`production`) and each one's 8 knobs (spec, architecture, task_size, plan_review, build_review, test_depth, docs, promotable). |
| `config/policy/capabilities.yaml` | The capability taxonomy (planning, implementation, review, …) and each one's preferred tier + score dimension. |
| `config/policy/agent-capabilities.yaml` | Which capability each agent maps to (drives `models --sync` selection). |
| `config/policy/constitution-checks.yaml` | The 11 architecture-constitution checks, mapped to the role that enforces them (planning / build / review). |
| `config/policy/commit-convention.yaml` | The commit-message convention the git hooks enforce (types, scope shape, attribution forbid-list, max_length, autofix, skip-marker). |
| `config/policy/hooks.yaml` | Git-hook rules: enforcement mode, secret patterns, junk patterns, protected paths (R-009). |

### 7.3 Tier 3 — reference (do not edit; 2 files + 1 generated)

| File | What it is |
|---|---|
| `config/reference/model_catalog.yaml` | The canonical model catalog — every model defined once with provider, context, capability scores, cost tier, pricing, limits, confidence. |
| `config/reference/providers.yaml` | The provider registry (id → name, prefer-rank). |
| `config/reference/.runtime-inventory.json` | **Generated, gitignored** — the detected runtime inventory (which providers are connected). |
| `.last-sync.json` | **Generated, gitignored** — the provider fingerprint at the last `aspis models --sync`. |

### 7.4 Mode + capability at runtime

The model routing is a **5-layer precedence** (D-016, D-017):

1. per-(runtime, agent) pin — `runtimes.<rt>.agents.<name>`
2. per-agent pin — `agents.<name>`
3. per-(runtime, capability) — `runtimes.<rt>.by_capability.<cap>`
4. per-capability — `by_capability.<cap>`
5. project/global tier override → `models.<rt>.<tier>`
6. **fallback** — the global `models.yaml` tier map

Then the resolver translates the canonical id to the runtime's exact string (e.g. `minimax-m3` → `opencode-go/minimax-m3` for OpenCode; `claude-opus-4-8` → `opus` for Claude). Hard limits and task-size are **deferred to dispatch** (D-017 scope correction).

---

## 8 · Source code structure (33 Python modules, 5 subsystems)

The engine is intentionally small: one module per concept, with a top docstring of Purpose / Responsibilities / Does Not / Used By (Constitution §"File rules"). Total Python source ≈ 4,000–5,000 LOC (excluding tests).

```
src/aspis/
├── __init__.py                  Version constant (single source)
├── cli.py                       Thin shell: argparse + dispatch via COMMAND_MODULES
├── assetkinds.py                Asset-kind registry (placement + write op per kind)
├── catalog.py                   Catalog asset format + parsing (CatalogAgent, CatalogCommand)
├── commands/                    One module per CLI verb (15 verbs)
│   ├── __init__.py              COMMAND_MODULES registry
│   ├── init.py                  aspis init
│   ├── bootstrap.py             aspis bootstrap (one-time onboarding)
│   ├── status.py                aspis status
│   ├── mode.py                  aspis mode
│   ├── models.py                aspis models [--available | --sync | --apply]
│   ├── commit.py                aspis commit (the single commit path)
│   ├── commits.py               aspis commits [--audit | --fix] (history audit)
│   ├── artifact.py              aspis artifact <kind> (mode-gated template stamping)
│   ├── testledger.py            aspis tests <check|record> (file-first test cache)
│   ├── preflight.py             aspis preflight (clean tree + branch + findings gate)
│   ├── context.py               aspis context (refresh brain + print L1)
│   ├── findings.py              aspis findings (list / resolve)
│   ├── doctor.py                aspis doctor (env + project + drift)
│   ├── gitignore.py             aspis gitignore
│   └── uninstall.py             aspis uninstall
├── operations/                  Lifecycle operations (registered on the engine)
│   ├── __init__.py              register_all()
│   ├── init.py                  init_core + scaffold + scripts + root files + git init
│   └── bootstrap.py             bootstrap_core + pre/post staging
├── runtimes/                    Per-runtime adapter plugins
│   ├── __init__.py              Auto-discovery (pkgutil + isinstance)
│   ├── base.py                  RuntimeAdapter ABC + RuntimeInventory + _emit_hook_file
│   ├── opencode.py              OpenCode adapter (mode, permission, task/skill allow-lists)
│   └── claude.py                Claude adapter (name, tools, settings.json)
├── engine.py                    Engine assembly: build_engine() returns a HookRunner'd Engine
├── lifecycle.py                 Context, Operation, Engine (generic lifecycle runner)
├── hooks.py                     Type-1 lifecycle hook runner (operational scripts)
├── export.py                    Plan + write exports (with hash protection via protect.py)
├── protect.py                   Pure 6-way hash-based decision engine (ADD/UNCHANGED/UNKNOWN/UPDATE/PROTECT/CONFLICT)
├── profiles.py                  Profile pydantic model + load + merge
├── models.py                    Model routing — resolve, effective_model, best_available_model
├── inventory.py                 Runtime inventory orchestrator (build/load + sync snapshot)
├── runtime_inventory.py         Which CLIs are on PATH (shutil.which, per-runtime.yaml)
├── catalog.py                   (above — parsing)
├── project.py                   Project detection + config loading (project, global, agent-models)
├── detect.py                    Stack detection (markers, aliases, gitignore fold)
├── health.py                    Health checks (python, git, project, runtime-hooks)
├── gitcheck.py                  Git-subsystem self-test (probes hooks, rolls back)
├── commitaudit.py               Commit-message history audit (reuses commit-msg validator)
├── promotion.py                 Promote 4 leads from subagent → primary
├── templating.py                {placeholder} substitution
├── constants.py                 BRAIN_DIR, HOOKS_DIR, PROMOTE_TO_PRIMARY
├── settings.py                  Pydantic settings (env-overrideable)
├── manifest.py                  .aspis/manifest.json read/write/is_bootstrapped
├── paths.py                     OS-standard config/data/cache dirs (Windows + Linux)
├── findings.py                  .aspis/current/findings.json read/resolve/clear
├── gitops.py                    Shared git helpers for init/bootstrap commits
└── (33 .py modules, ~4-5K LOC)
```

### 8.1 Key contracts (recurring types)

| Type | Module | Used by |
|---|---|---|
| `CatalogAgent` | `catalog.py` | runtime adapters, export |
| `CatalogCommand` | `catalog.py` | runtime adapters, export |
| `Profile` | `profiles.py` | export, init, models --apply |
| `AssetKind` | `assetkinds.py` | export |
| `RuntimeAdapter` (ABC) | `runtimes/base.py` | transform, export, inventory |
| `RuntimeInventory` | `runtimes/base.py` | models.resolve, inventory |
| `Context` / `Engine` / `Operation` | `lifecycle.py` | every operation |
| `Decision` / `DecisionKind` | `protect.py` | export.write_export |
| `Check` | `health.py`, `gitcheck.py` | doctor |
| `PromotionResult` | `promotion.py` | bootstrap post-stage |
| `ScaffoldResult` / `CompileResult` | `planning scripts` | scaffold + compile |
| `Finding` | `commitaudit.py` | commits command |

### 8.2 Dependency direction (constitution §"File rules")

Plugins → core, never the reverse:
- `commands/*.py` → `engine, operations, project, models, …`
- `runtimes/*.py` → `runtimes/base, catalog`
- `operations/*.py` → `lifecycle, project, export, detect, …`
- `engine.py` → `lifecycle, hooks`

No circular imports. The runtime adapters don't import from `commands/` or `operations/`; they only know `catalog.py` and `models.py`. The plugins load by **discovery** (pkgutil iter on `runtimes/`, glob on `catalog/`), not registration.

### 8.3 Engine assembly

```python
# src/aspis/engine.py (the only 16 lines)
def build_engine() -> Engine:
    return Engine(run_hooks=HookRunner())
```

The engine runs `pre-<op> → core → post-<op>` with the discovered Type-1 hooks (operational scripts) wrapping built-in Python steps. Operations register themselves via `aspis/operations/__init__.py:register_all()`.

---

## 9 · Test coverage (59 test files)

Test layout: `tests/test_<module>.py`, one file per engine module. Total **59 test files** covering ~all of the engine's behavior. Most are **behavioral** (test the API + edge cases), not coverage-tooled.

### 9.1 Coverage by area

| Area | Test files | What's covered |
|---|---|---|
| **CLI** | `test_cli.py` (4 tests) | Version, no-command help, status, doctor. |
| **Init** | `test_init_cli.py`, `test_init_op.py` | CLI args; operation lifecycle. |
| **Bootstrap** | `test_bootstrap_cli.py`, `test_bootstrap.py` | First-run gate; idempotency; manifest; sub-clean. |
| **Export** | `test_export.py`, `test_export_protection.py`, `test_export_snapshot.py`, `test_f015_e2e.py` | Planner; per-runtime actions; protection engine; snapshot persistence; E2E init→edit→re-apply. |
| **Catalog + runtime render** | `test_catalog.py`, `test_render_routing.py`, `test_runtime_contract.py` | CatalogAgent/Command parse; per-runtime render; capability wiring. |
| **Asset kinds** | `test_assetkinds.py` | Placement + op registry. |
| **Protect engine** | `test_protect.py` | The pure 6-case truth table (ADD/UNCHANGED/UNKNOWN/UPDATE/PROTECT/CONFLICT), ordering, BOM/CRLF normalization, fan-out, summary. |
| **Profiles** | `test_profiles.py` | Parse, fold, merge; open kind discovery. |
| **Models** | `test_models.py`, `test_model_catalog.py`, `test_model_detection.py`, `test_models_command.py`, `test_resolver.py` | Routing precedence; canonical↔runtime translation; best_available; per-capability selection. |
| **Inventory** | `test_inventory.py` | Build/load + sync snapshot. |
| **Lifecycle** | `test_lifecycle.py`, `test_lifecycle_gates.py` | Engine order; pre/post staging. |
| **Hooks** | `test_hooks.py`, `test_f006_hooks.py`, `test_hook_gates.py` | Hook discovery, .py/.sh/.ps1 interpreters, env passing, gating semantics. |
| **Git subsystem** | `test_commit.py`, `test_commitmsg.py`, `test_commits.py`, `test_gitcheck.py` | Commit composition; message validation; history audit; probe-rollback self-test. |
| **Modes** | `test_mode.py` | show / set / fallback. |
| **Templates** | `test_templating.py` | {placeholder} substitution; unknown pass-through. |
| **Settings** | `test_settings.py` | Env override; defaults. |
| **Detective** | `test_detect.py` | Stack detection; alias normalization; typo correction. |
| **Health** | `test_health.py` | check_python/aspis/git/project/runtime_hooks. |
| **Findings** | `test_findings.py` | Load / resolve / clear. |
| **Promotion** | `test_promotion.py` | frontmatter mode flip; idempotency. |
| **Tests ledger** | `test_testledger.py` | Fingerprint; cached pass; stale detection. |
| **Context** | `test_context.py`, `test_build_code_map.py`, `test_build_registry.py`, `test_build_state.py`, `test_record_changes.py` | Brain scripts. |
| **Active feature** | `test_active_feature.py` | Pointer read/write. |
| **Feature scaffold / task compile** | `test_feature_scaffold.py`, `test_task_compile.py` | F-NNN allocation; branch create; packet emission. |
| **Prereq validate** | `test_prereq_validate.py` | Phase order; mode relaxation. |
| **Brain gitignore** | `test_brain_gitignore.py` | The .aspis/.gitignore seeded at init. |
| **Constitution** | `test_constitution.py` | The 11 checks well-formed; profile ships the rules. |
| **Global config** | `test_global_config.py` | The `~/.aspis/config/project.yaml` layer. |
| **Consistency** | `test_consistency.py` | Catalog cross-refs (agents→skills, profile→catalog). |
| **Artifact** | `test_artifact.py` | Mode gating; stamp; fill. |
| **Install UX** | `test_install_ux.py` | Installer / uninstaller flows. |
| **Update** | `test_update.py` | Brain updater (idempotent re-runs). |

### 9.2 What's NOT covered (gaps)

- **Workflow execution** — workflows are markdown; nothing tests they were followed. The hook's gate is the only enforcement.
- **Skill bodies** — `SKILL.md` files have no tests; they're operational docs, not code.
- **Catalog command bodies** — only the `commands/*.md` frontmatter is validated.
- **Real-LLM behavior** — the tests are deterministic; no end-to-end "ask the agent to plan" tests.
- **Per-skill anti-pattern compliance** — no check that an agent followed the skill's procedure.
- **Trace spine** — there is no trace spine yet; nothing to test.

---

## 10 · Current state (what's built, what works, what's missing)

### 10.1 What's built and working (Parts 1–2 of the 6-part roadmap)

| Capability | Status | Evidence |
|---|---|---|
| **3-layer architecture** (factory → brain → runtime → product) | ✅ Live | ARCHITECTURE.md §1, catalog in `src/aspis/data/catalog/` |
| **One catalog, per-runtime adapters** (D-002) | ✅ Live | `runtimes/__init__.py:_discover()`, `opencode.py`, `claude.py` |
| **Asset kinds are data** (D-008) | ✅ Live | `assetkinds.py:_OVERRIDES`; new kinds are purely additive |
| **Runtime identity is the adapter's** (D-015) | ✅ Live | `RuntimeAdapter.runtime_dir`/`root_guide`/`supports_mode` |
| **Canonical model catalog + resolver** (D-016, D-017) | ✅ Live | `model_catalog.yaml`, `models.resolve`, `models.best_available_model` |
| **Per-runtime detection** (D-018) | ✅ Live | `OpenCodeAdapter.detect`, `ClaudeAdapter.detect` (XDG; never raises) |
| **6-way hash protection** (F-015) | ✅ Live | `protect.py:decide`, `export.write_export` |
| **`aspis init`** (catalog export) | ✅ Live | `commands/init.py`, `operations/init.py:init_core` |
| **`aspis bootstrap`** (one-time onboarding) | ✅ Live | `commands/bootstrap.py`, `operations/bootstrap.py:bootstrap_core` (promotes leads, runs git self-test, self-cleans) |
| **5 commands × 2 system verbs** | ✅ Live | `/plan /build /review /system /status` (catalog/commands/) + the 10 CLI verbs |
| **6 workflow docs** | ✅ Live | `catalog/workflows/*.md` (one per track) |
| **Mode-scaled planning** (D-013) | ✅ Live | `modes.yaml` + `artifact.py` mode-gating |
| **38 skills** | ✅ Live | catalog/skills/, one per concern |
| **12 agents** (5 primaries after bootstrap) | ✅ Live | catalog/agents/ + `promotion.py` |
| **Git hooks (pre-commit / commit-msg / post-commit)** | ✅ Live | `scripts/hooks/`, non-blocking by default (`enforcement: warn`) |
| **Runtime scope-guard wiring** (per runtime) | ✅ Live | `runtime-hooks/claude/settings.json`, `runtime-hooks/opencode/session-notice.ts` |
| **Comitter as single commit authority** (D-011) | ✅ Live | `commands/commit.py`, `committer` agent |
| **Commit convention + autofix + history audit** | ✅ Live | `commit-convention.yaml`, `commitmsg.py`, `commitaudit.py` |
| **Test ledger** (D-014) | ✅ Live | `commands/testledger.py`, `selective-testing` skill |
| **Context brain** (FILE_REGISTRY, CODE_MAP, CURRENT_STATE, RECENT_CHANGES) | ✅ Live | `scripts/context/*.py`, `commands/context.py` |
| **`aspis preflight`** (clean tree + branch + findings gate) | ✅ Live | `commands/preflight.py` |
| **OS-standard install paths** (Windows + Linux, F-013) | ✅ Live | `paths.py` (XDG / APPDATA / LOCALAPPDATA) |
| **Cross-platform portable** (Constitution §12) | ✅ Live | UTF-8 stdio everywhere; `subprocess(encoding="utf-8")`; `.CMD` shell dispatch |

### 10.2 What's stubbed or partial

| Capability | Status | Gap |
|---|---|---|
| **Project-plan track** (deeper than a feature) | 🟡 Design only | CORE_LOOP §12 says "deferred to a later pass"; the workflow doc doesn't exist yet. |
| **Subagent-level reviewer** (per-task context-isolated review) | 🟡 Designed, not extracted | `build.md` step 3d says "a context-isolated sub-agent reviewer by default" but no `sub-reviewer` agent exists; today every review escalates to the Reviewer lead. |
| **Plan-critic skill** (cross-artifact check before build) | 🟡 Skill exists, light | `plan-critic/SKILL.md` is 35 lines (Purpose / When to use / Procedure / Outputs); the full multi-axis check from old ASPS is not yet there. |
| **Maturity of templates** | 🟡 Lean, no inline examples | Templates are skeletons; old ASPS's `templates/` were 24 richly annotated files. |
| **Workflow doc annotations** | 🟡 Lean | Each workflow is 30-50 lines; old ASPS's `BUILD_WORKFLOW.md` was 200+ lines with status discipline encoded. |
| **Trace spine** | 🔴 Not built | No `.aspis/traces/{raw,runs}/`, no `trace-event`/`trace-pipe`, no OpenCode plugin beyond `session-notice.ts`. |
| **Dashboard** | 🔴 Not built | No `STATUS.md`, no `dashboard/`, no `LESSONS.md`. |
| **Research packages** | 🟡 Skill exists, no examples shipped | `knowledge-research` and `knowledge-packaging` skills exist but no packaged research assets. |
| **Test generation auto-in-loop** | 🟡 Skill exists, agents call ad hoc | No automatic "red→green" step in build; agents run `test-generation` when they choose. |
| **L3 subagents** (sub-reviewer, specialized builders) | 🟡 Deferred (D-028) | Old ASPS tried them, parked them. Current ASPIS also has no L3 — 2-level run depth. |
| **`runtime.lock.*.json` + totality guard** | 🔴 Not built | No byte-parity check that catalog == runtime. |
| **Golden manifest** | 🔴 Not built | Old ASPS's `tests/golden/catalog_assets.txt` + `refresh-golden.py --check`; not present. |
| **Per-agent model routing tests** | 🟡 Partial | `test_resolver.py` and `test_models_command.py` cover routing; per-agent permission enforcement is in `test_agent_permissions.py`. |
| **CI** | 🟡 Designed (D-012 says Windows+Linux matrix), not present | No `.github/workflows/` files found. |
| **PowerShell + bash dual stack** | 🟡 Reduced to Python | Old ASPS had `.ps1`/`.sh` mirrors; current ASPIS uses Python-only (hooks + scripts). Hooks support `.ps1` via pwsh if present, but no shipped `.ps1` hooks. |
| **`docs/QUICKSTART.md`, `docs/FIRST-BUILD.md`** | 🔴 Not present (D-012 says they should exist) | Only `docs/ARCHITECTURE.md` exists (or not — needs verify). |

### 10.3 Test footprint — what's not tested (operationally risky)

- **End-to-end "real agent" tests** — all tests are unit-level; no test that an agent followed its workflow.
- **Catalog → render byte-stability** — no totality guard; a wrong render would slip through.
- **Mode knob enforcement** — `test_artifact.py` covers `build/feature/review/test/acceptance`; but the full modes.yaml → artifact gating matrix is sparse.
- **Runtime hooks per-platform behavior** — `test_health.py` checks the baked interpreter, but doesn't exercise the runtime-guard script on a real tool call.
- **Promotion atomicity** — promotion is frontmatter-only and per-file; no test for a partial promotion mid-run.

---

## 11 · Gaps vs old ASPS

ASPIS is a **clean OSS rebuild of the older ASPS** (D-001, 2026-06-18): "port it feature by feature, bias to lean, keep what is proven, rebuild it simply." The old ASPS research (`old-asps-system-design-3.md`, `old-asps-workflows-scripts-2.md`, `old-asps-deep-analysis-1.md`) is the comparison baseline.

### 11.1 What old ASPS had that current ASPIS does NOT

| OLD ASPS artefact | What it was | ASPIS status |
|---|---|---|
| **27-verb `asps` Python CLI** (init-project, proof, doctor, validate-runtime, validate-index, trace-*, stats, dashboard, preflight, compile-tasks, start-feature, close-feature, promote, regenerate, append-trace, governance, harvest-gate, trace-gate, clean-junk, improve, lessons, …) | The full engine | **Partially present.** ASPIS has 15 verbs; **missing**: `proof`, `validate-runtime`, `validate-index`, `trace-*` (5+), `stats`, `dashboard`, `start-feature`/`close-feature`, `governance`, `harvest-gate`, `improve`, `lessons`. |
| **Trace spine** (`.asps/traces/{raw,runs}/*.jsonl` + SQLite index + `trace-report` + `trace-ingest`) | The firehose | **Not present.** No traces, no SQLite. |
| **50-agent catalog** (28 live + 22 archived) with `## Abstraction` runtime-agnostic block | The full roster | **Reduced to 12 agents**, no archived set, no `## Abstraction` block (catalog uses simpler YAML frontmatter). |
| **45 skills** across 9 categories with `references/` subfolders | The procedure library | **Reduced to 38 skills**, no per-skill `references/` subfolders. |
| **24 templates** (10 categories, richly annotated) | Output shapes | **Reduced to 10 templates** (4 categories, lean skeletons). |
| **5 profiles** (base, defaults, full, asps-self, python-cli) | Catalog slicing | **Reduced to 1 profile** (`base.yaml`). |
| **`runtime.lock.*.json` + `totality guard` test** | Catalog==runtime byte parity | **Not present.** |
| **`tests/golden/catalog_assets.txt` + `refresh-golden.py --check`** | Drift guard | **Not present.** |
| **`.opencode/plugins/asps-trace.ts` + `trace-pipe` shim + `trace-hook`** | Tool-call capture | **Not present** (replaced by lighter `session-notice.ts` only). |
| **Bootstrap with self-cleanup** (D-B1, D-B2) — agent + skill + workflow that ship, run, remove themselves, write `bootstrap.done` | First-chat onboarding | **Present and equivalent** — current ASPIS has the full self-clean story (`operations/bootstrap.py:_self_clean + _strip_bootstrap_prose`). |
| **2,000+ lines of Phase plans** (PHASE-0/1, AGENT-SYSTEM-PLAN, CORE-AGENTS-PLAN, BOOTSTRAP-UX-PLAN, F-027-PLANNING-UPGRADE, SHIP-PLAN-DRAFT, LAUNCH-SPRINT) | The phased rationale | **Reduced** to `ROADMAP.md` (root) + `CORE_LOOP.md` + per-feature SPEC/PLAN/TASKS. |
| **`docs/CRITICAL_REVIEW_2026-06-10.md`** (10-prioritised backlog, A1-A4, R1-R4, P1-P4, S1-S4, T1, U1-U3, Gap 1-3) | Evidence-based self-audit | **Not present.** This is the single most valuable missing artefact for the migration. |
| **`dashboard/LESSONS.md`** (L-001…L-007) | Self-improvement seed | **Not present.** |
| **`docs/AS_BUILT.md`** | As-built engineering reference | **Not present.** The current `FILE_REGISTRY.yaml` + `CODE_MAP.md` cover the current shape but not the "what grew organically" view. |
| **PowerShell + bash mirrors for every script** | Cross-platform parity | **Reduced to Python + `subprocess`** (no `.ps1` shipped). |
| **`asps-lead` global cross-domain lead** (later `project-lead`) | The single L1 entry | **Replaced by `project-lead` + per-domain primaries** (D-026, refined by D-028). |
| **`governance` subagent** (R-009-gated, only path to edit `rules/**`) | The only constitution editor | **Not present** — current system-lead is the only path, but no separate "governance" agent with the narrow role. |

### 11.2 What current ASPIS has that old ASPS did NOT (or did worse)

- **Mode-scaled planning** is **first-class** — old ASPS had F-027 as a *draft*, never executed; current ASPIS has `modes.yaml` + `planning-intake` reading it + `artifact.py` mode-gating the report creation.
- **Hash-based protection engine** (`protect.py`) — old ASPS had a `runtime.lock.*.json` mechanism + totality guard; current ASPIS replaced it with a cleaner 6-case pure decision engine (`ADD/UNCHANGED/UNKNOWN/UPDATE/PROTECT/CONFLICT`) with snapshot + audit log.
- **Canonical model catalog + capability routing** (D-016, D-017) — old ASPS had per-agent model pin only; current ASPIS has a tier→canonical→runtime-string resolver with per-capability override.
- **Runtime-aware detection** (D-018) — old ASPS had presence-only detection; current ASPIS detects connected providers + available model strings (OpenCode `auth.json` keys + `opencode models`).
- **Clean OpenCode-native skill format** — `SKILL.md` with frontmatter, ready for any `.opencode/skills/`-aware runtime from day one.
- **Smaller, more honest starting point** — 12 agents, 38 skills, 33 modules vs. old ASPS's 50 agents, 45 skills, 61 modules. The lean rebuild is the point (D-001).
- **No `.ps1` shell duplication** — old ASPS had Python+bash+pwsh triplicate for every script; current ASPIS uses Python only.
- **No god-file `cli/main.py`** — current `cli.py` is 74 lines, dispatches via the registry.
- **Modern type safety** — Pydantic v2 for `Settings` and `Profile`.
- **Test ledger** (D-014) — old ASPS had no content-fingerprint cache; current ASPIS has `aspis tests check/record`.
- **BOM/CRLF normalization in hash** — old ASPS's byte-parity guard was fragile to Windows line endings; current `sha256_text` strips BOM + normalizes CRLF→LF.

### 11.3 The single biggest gap

**No trace spine and no dashboard.** Old ASPS's "capture now, derive later" principle is the Phase-4 spine; without it, every decision is a one-shot and there's no "what actually worked" feedback loop. The current ASPIS is **worse** than old ASPS at the meta-level — there is no `LESSONS.md`, no `STATUS.md`, no `DASHBOARD.md`, no `traces/`. This is the highest-leverage miss.

---

## 12 · What works well in current ASPIS

### 12.1 Architectural discipline (Constitution + D-008/D-015)

The **Cost-of-Change test** holds: to add a new asset kind, you drop a `catalog/<kind>/` dir and list it in a profile — **zero core files change**. To add a new runtime, you add `runtimes/<name>.py` — zero core files change. To add a new build mode, you add a key to `modes.yaml` — zero core files change. This is real, not aspirational, in the current code.

The **capability check** pattern (`runtime.supports(kind)`) is everywhere; there is no `if runtime == "claude"` anywhere in the codebase. A grep for `if .*== .*"` in `src/aspis/` returns only legitimate uses (Pydantic model checks, mode validation, etc.).

### 12.2 Determinism-first (R-003) is enforced

`deterministic-first/SKILL.md` is a real ladder agents are told to walk:

> 1. Deterministic code? 2. Agent? 3. Skill? 4. Template? 5. Workflow?

And the system **backs this up**:
- `aspis preflight` is a script, not an agent.
- `aspis status` is a script, not an agent.
- `aspis commit` is a script that uses `scripts/git/compose.py` (not a re-implementation).
- Feature scaffold + task compile + prereq-validate are all scripts.

The Build Lead is told: "delegate only when it adds value; small tasks done directly." The cleanest expression of this in the code is `operations/init.py` — every step is a `_function(ctx, *, write=write)` that returns; there's no agent in the init path.

### 12.3 The protection engine is well-designed

`protect.py` is a 153-line pure module with zero I/O — 6-case truth table, BOM/CRLF normalization, fan-out, summary. It is exhaustively tested in `test_protect.py` (50+ assertions). `export.py:write_export` uses it for a clean protected-write path; `models.py:--apply` uses the same engine for re-rendering agents without clobbering user edits. This is a single decision engine with two callers, exactly the kind of Local-Change / Single-Source / No-Special-Case discipline the Constitution asks for.

### 12.4 Mode-gating actually skips work

`aspis artifact` doesn't write a report when the mode says don't (`vibe` writes no `build.md`/`feature.md`/`review.md`/`test.md`; `mvp` writes no `review.md`). This is real, not cosmetic — the artifact file isn't created at all. So a `vibe` feature is genuinely lighter, not "lighter in name only."

### 12.5 The 3-layer transform is end-to-end

A user runs `aspis init --write` and gets:
- A `.aspis/` brain with all directories seeded
- A `.opencode/agents/` with 12 agents, each with the right mode/model/permissions
- A `.claude/agents/` with the 12 agents, names + tools (no mode, no temperature, no delegates, no skills)
- A `.opencode/commands/` with 5 commands
- A `.opencode/skills/` with 38 skills
- A `.aspis/scripts/` with all 15 helper scripts
- A `.aspis/config/` with all 11 config files
- A `.aspis/templates/` with all 10 templates
- A `.aspis/workflows/` with all 6 workflows
- A `.gitignore` for the stack
- A git repo with hooks armed

…all from a single `aspis init` call. The `bootstrap` call then fills the judgment files (goal, stack, architecture enrichment) and promotes the 4 leads → 5 primaries. The first-run gate in the project-lead's instructions routes any user request through bootstrap if it hasn't run. **The system is end-to-end and reproducible.**

### 12.6 Commits are machine-checked

The commit-msg hook runs `commitmsg.validate` against `commit-convention.yaml` (single source, reused by `compose.py` and `commitaudit.py`). Attribution is auto-stripped on `warn` mode (D-012). `aspis commits --audit` flags any history that violates the convention; `--fix` rewrites only the auto-fixable ones (attribution), keeping content byte-identical. **History reads as if a careful human wrote it.**

### 12.7 Cross-platform is real

Every `subprocess.run` uses `encoding="utf-8"`; every `read_text` and `write_text` uses `encoding="utf-8"`; the Windows `.CMD` shim detection (`OpenCodeAdapter._available_models`) routes through the shell. `pyproject.toml` requires Python ≥ 3.11. `health.check_runtime_hooks` warns when the baked interpreter is stale (Windows↔WSL move). **`docs/QUICKSTART.md` would document the install; not yet present.**

### 12.8 The boot is self-cleaning

After a successful `aspis bootstrap --write`:
- The `bootstrap` agent is removed from `.opencode/agents/` and `.claude/agents/`.
- The `project-onboarding` skill is removed from `.opencode/skills/` and `.claude/skills/`.
- The `bootstrap.md` workflow is removed from `.aspis/workflows/`.
- The first-run gate prose in AGENTS.md / CLAUDE.md / `project-lead.md` is stripped (the `ASPIS:BOOTSTRAP-GATE:START/END` markers).

So in a live project, the bootstrap package **does not exist** anywhere — the only way to detect "this project was bootstrapped by ASPIS" is the `bootstrapped: true` flag in `.aspis/manifest.json`. The "ship the system you built" principle (D-001) is honored.

### 12.9 Skills are the right shape

Every `SKILL.md` is **40-70 lines** — not 200, not 5. Each has frontmatter + Purpose + When to use + Procedure + Outputs + Anti-patterns. The `context-ladder` skill is the only one that runs to 53 lines because it carries the L1–L4 ladder; the rest are crisp. This is the right density: enough to be a procedure, short enough to load fully into a lead's context.

### 12.10 The model routing is data, not code

Every change to model assignment is a YAML edit:
- `models.yaml` — tier→canonical (global default)
- `project.yaml` — per-project override
- `agent-models.yaml` — per-agent assignment (generated, then hand-edited)

The resolver (`models.resolve`) is a 25-line function that applies the 5-layer precedence. The detection is per-runtime (`OpenCodeAdapter.detect`, `ClaudeAdapter.detect`), the translation is per-runtime (`model_string()`), the inventory is generated and gitignored. **A new model is a YAML row; a new runtime is a YAML file + an adapter; a new capability is a YAML row.** No code change for any of it.

---

## 13 · F-016 planning implications (the takeaways)

For F-016's design, the audit says:

1. **The system is operationally complete for Parts 1–2.** All 12 agents, 38 skills, 5 commands, 6 workflows, 10 templates, 11 config files, 15 scripts, 33 source modules, 59 tests are in. The Build Loop can be exercised end-to-end with the current catalog.

2. **The three things F-016 should focus on, ranked by leverage:**
   - **Trace spine** (Part 3) — the single biggest gap vs old ASPS; the meta-feedback loop is missing. Without it, the system cannot "learn" (R-009 is the closest substitute today, but it's a gate, not a feedback).
   - **Subagent-level reviewer** (CORE_LOOP §5) — the "per-task context-isolated sub-agent reviewer" is the second-biggest gap; today every review escalates to the Reviewer lead, which couples reviewer context to the whole feature.
   - **Templates + workflow depth** (Part 2 polish) — the templates are 30-50 lines of skeleton; old ASPS's were 100+ with rich annotations. The Build Lead is the primary consumer; richer templates = cheaper builders succeed.

3. **The dogfooding is working.** The current ASPIS is a live project; F-014 (system hardening) and F-015 (safe catalog export) just landed (the most recent commits are F-015 final reviews + F-016 T-00 scaffold). The phase ordering and the Build Lead's review routing are exercised on real work.

4. **The "P0" pattern in the old ASPS was effective** and the current ASPIS has preserved it as `planning-intake` + `modes.yaml` + `prereq-validate.py`. F-016 should treat this as proven, not redesign.

5. **The protection engine + `models --apply`** combine to make model routing a *runtime* change without a re-init. F-016 should ensure the new agent/skills (sub-reviewer, specialized builders) follow the same pattern: no re-init needed to make a new template, skill, or reviewer active.

6. **The constitution + system-rules + modes + commit-convention are the four-rule layer** that constrains the system. F-016 must keep them in sync; any new agent or skill may need a new `agent-capabilities.yaml` entry, a new `constitution-checks.yaml` rule, a new `commit-convention.yaml` shape, or a new mode knob.

7. **The cost of a new agent is 1 catalog file + 1 mode entry + 1 profile entry + 1 base agent file in the live runtime.** F-016 should measure the proposed agents against this cost.

---

## 14 · File index (everything the audit touched)

### 14.1 Catalog (single source)

- Agents: `src/aspis/data/catalog/agents/*.md` — 12 files
- Skills: `src/aspis/data/catalog/skills/*/SKILL.md` — 38 files
- Commands: `src/aspis/data/catalog/commands/*.md` — 5 files
- Templates: `src/aspis/data/catalog/templates/{context,planning,report,review}/*.md` — 10 files
- Workflows: `src/aspis/data/catalog/workflows/*.md` — 6 files (incl. bootstrap.md)
- Rules: `src/aspis/data/catalog/rules/{system-rules,architecture-constitution}.md` — 2 files
- Config: `src/aspis/data/catalog/config/{models.yaml, policy/*, reference/*}` — 11 files
- Scripts: `src/aspis/data/catalog/scripts/{context,git,hooks,planning}/*.py` — 23 files
- Scaffold: `src/aspis/data/catalog/scaffold/*` — 5 files
- Runtime hooks: `src/aspis/data/catalog/runtime-hooks/{claude,opencode}/*` — 2 files
- Profiles: `src/aspis/data/profiles/base.yaml` — 1 file
- Runtimes: `src/aspis/data/runtimes/{opencode,claude}.yaml` — 2 files (data SSoT for adapter facts)

### 14.2 Live (deployed by `aspis init`)

- `.opencode/agents/` — 10 (the 12 catalog agents minus `bootstrap` in a live project; minus `bootstrap` and any post-bootstrap clean)
- `.opencode/skills/` — 38 (one per catalog skill)
- `.opencode/commands/` — 5
- `.claude/agents/` — same 12 (Claude-rendered)
- `.aspis/scripts/{context,git,hooks,planning}/*.py` — 23
- `.aspis/config/{*,policy/*,reference/*}` — 11
- `.aspis/templates/{context,planning,report,review}/*` — 10
- `.aspis/workflows/{build,plan,review,fix,small-task}.md` — 5 (no bootstrap.md in live)
- `.aspis/rules/{system-rules,architecture-constitution}.md` — 2
- `.aspis/context/{ARCHITECTURE,CURRENT_STATE,RECENT_CHANGES,IDENTITY,CORE_LOOP,DECISIONS,ROADMAP}.md` — 7
- `.aspis/manifest.json`, `.aspis/.gitignore`, `.aspis/index/{FILE_REGISTRY,CODE_MAP,...}` — generated
- `.gitignore` (project root), `AGENTS.md`, `CLAUDE.md` — generated

### 14.3 Source (engine)

- `src/aspis/*.py` — 30 top-level modules
- `src/aspis/commands/*.py` — 15 command modules + `__init__.py`
- `src/aspis/operations/*.py` — 2 operation modules + `__init__.py`
- `src/aspis/runtimes/*.py` — 3 (base + opencode + claude) + `__init__.py`

### 14.4 Tests

- `tests/*.py` — 59 test files + `conftest.py`

### 14.5 Governance + context (the durable brain)

- `.aspis/rules/{system-rules,architecture-constitution}.md` — 2 rule files (9 rules + 11 checks)
- `.aspis/context/{ARCHITECTURE,IDENTITY,ROADMAP,CORE_LOOP,DECISIONS,CURRENT_STATE,RECENT_CHANGES}.md` — 7 context files
- `.aspis/config/policy/{modes,capabilities,agent-capabilities,commit-convention,hooks,constitution-checks}.yaml` — 6 policy files
- `.aspis/manifest.json` — bootstrapped flag + project state

---

## 15 · Summary scorecard

| Dimension | Score | Note |
|---|---|---|
| Architectural discipline (Constitution compliance) | **A** | 0 violations of "no special case"; cost-of-change ≤3 files for any new asset kind / runtime / mode. |
| Determinism-first (R-003) | **A** | Real ladder; scripts do the mechanical work; agents do the judgment. |
| Test coverage | **B+** | 59 test files; ~all engine behavior tested; e2e tests in `test_f015_e2e.py`; no agent-behavior tests. |
| Cross-platform (Windows + Linux) | **A-** | UTF-8 stdio everywhere; .CMD shim; OS-standard dirs. Missing: a CI matrix (designed, not built). |
| Mode-scaled planning (CORE_LOOP §3) | **A** | `modes.yaml` is the single source; `planning-intake`, `artifact`, `prereq-validate` all read it. |
| Model routing (D-016, D-017) | **A-** | Canonical + per-runtime + per-capability; one resolver; no re-init to change. Missing: tracing (Phase 4). |
| Protection / safety (F-006 + F-015) | **A** | 6-case truth table; non-blocking by default; `force-conflicts` / `strict` / `--force` are the three ways to override. |
| Bootstrap UX | **A** | One command; self-cleans; promotes 4 leads; runs git self-test; gates via doctor. |
| Onboarding (human in the loop) | **A** | Wizard is TTY-guarded, flag-overridable, headless-safe. |
| Trace / observability | **F** | No trace spine. No dashboard. No `LESSONS.md`. Single biggest gap. |
| Dashboard / status (Part 5) | **F** | Not built. |
| Scale / fleet (Part 6) | **F** | Not built. |
| Documentation (onboarding a newcomer) | **C** | `docs/QUICKSTART.md` and `docs/FIRST-BUILD.md` not present (D-012 said they should be). `docs/ARCHITECTURE.md` needs verify. |
| Workflow doc depth | **C+** | 30-50 lines each; old ASPS's were 200+ with status discipline encoded. |
| Template richness | **C+** | Skeletons; old ASPS had inline examples. |
| Subagent-level reviewer | **C** | Designed in `build.md` step 3d, not extracted. |
| **Overall (Parts 1–2 of 6)** | **A-** | **Shippable as-is for daily production use**; the trace spine is the highest-leverage next thing. |

---

*End of audit. Companion files: `old-asps-deep-analysis-1.md` (roster + decisions + architecture), `old-asps-workflows-scripts-2.md` (mechanisms), `old-asps-system-design-3.md` (3-layer + gap audit), `core-loops-2026.md` (external research), `production-loops-companies.md`, `cheap-models-quality.md`, `system-agent-tooling.md`, `permissions-control-reliability.md`.*
