# F-006 Hooks — Handoff (continue exactly from here)

You are continuing the **ASPIS** OSS rebuild. This doc carries everything needed to
finish F-006 and move on. Read it fully, then execute the remaining tasks.

## Where & what
- Repo (the rebuild): `/mnt/p/ai_empire/projects/Agentic Software Production System/ASPIS`.
  The shell cwd may reset to the OLD `…/asps` repo — always `cd` to the ASPIS path above.
- ASPIS is a file-first agentic software factory; its product is the catalog
  (`src/aspis/data/catalog/`) + the `aspis` CLI. The OLD `…/asps` repo is the messy
  original, used only for reference.
- Toolchain: `uv`, hatchling, pydantic, pyyaml, ruff, pytest. **No mypy.**
  Gate: `uv run ruff format --check . && uv run ruff check . && uv run pytest -q`
  (ruff line-length = **100**). Currently **110 tests green**.

## Hard constraints (never violate)
1. **Git history must read as fully human-authored.** NEVER add `Co-Authored-By` or
   mention Claude/Opus/Sonnet/AI/any model/tool in commit messages, branches, or bodies.
   ("Claude"/"OpenCode" as runtime *names inside files* are fine domain vocabulary.)
2. **Commit convention** (`commit-convention.yaml`): `type(F-NNN[/T-NN | /T-NN..T-MM]): title`
   + ~5 human bullet lines, end multi-task commits with a `Tasks: …` trailer. Scope is
   OPTIONAL for repo-lifecycle commits (init/bootstrap → `chore: …`). Branch `type/F-NNN-slug`.
3. **Create/edit files with the editor tools, never shell redirection** (`>`/heredoc) — it
   spawns junk files at the repo root.
4. **Lean, data-driven, DRY, small files**; new behaviour = new files; one change = one file.
5. **Propose → agree → build** is the user's default, BUT for F-006/F-007 the user said
   "build it direct, don't wait me" and "MVP/fast, large tasks, no task packets."

## Current state
- Branch: `feat/F-006-hooks` (off `main`, which is `F-004 → F-005` merge `392f17f`).
- Commits done: `T-00` plan, `T-01` shared core, `T-02` runtime guard, `T-03` non-blocking
  + CLI + init-arms-hooks, `T-05` tests, `T-06` docs (D-010 + ARCHITECTURE + ROADMAP).
  **Remaining: T-04 (dogfood regenerate), then the F-006 merge.**
- The OLD F-005 guards live on `backup/F-005-guards`; old git on `backup/F-006-git`.

## Numbering (already done — context only)
The extensibility core was renumbered F-007→**F-005** and merged after F-004. Sequence is
now `F-004 → F-005 (extensibility) → F-006 (hooks, this) → F-007 (git subsystem, next)`.

## F-006 design (what was built)
**Two deterministic surfaces over one shared core, NON-BLOCKING by default.**
- Logic lives once in `src/aspis/data/catalog/scripts/hooks/` (ships to `.aspis/scripts/hooks/`):
  `_git.py`, `_config.py`, `scope.py`, `secret_scan.py`, `commitmsg.py`, `cleanup.py`
  (junk + stale `.gitkeep`), `gitignore.py` (Toptal API + offline cache in `ignore/`),
  `precommit.py`, `postcommit.py`, `runtime_guard.py`, `install.py`.
- Rules are DATA in `src/aspis/data/catalog/config/hooks.yaml` (secrets, junk, protected
  paths, and the `enforcement` switch).
- **`enforcement: warn` (default) NEVER blocks** — pre-commit auto-fixes (clean junk, ruff
  format/--fix staged py when the project configures ruff, re-stage) then only *reports*
  scope/secret/protected; commit-msg and runtime_guard report too. Flip `enforcement: block`
  in hooks.yaml to turn the same checks into hard walls — no code change. (User: runtime
  blocking is a LATER design; ship safe now.)
- Git hooks install into `.git/hooks/` via `install.py` (thin bash wrappers bound to the
  installing interpreter); `init` runs it. NOT `core.hooksPath`, NOT `.aspis/githooks/`.
- Runtime scope-guard is **adapter-emitted**: `RuntimeAdapter.emit_runtime_hooks` (base
  returns `[]`); Claude → `.claude/settings.json`, OpenCode → `.opencode/plugins/scope-guard.ts`
  (sources in `catalog/runtime-hooks/<runtime>/`). `write_export` calls it per runtime.
- Commit scope is OPTIONAL (lifecycle commits); bootstrap commits set
  `ASPIS_ALLOW_PROTECTED=1` (genesis commit ships the R-009 files).

## REMAINING TASKS

### T-04 — Regenerate ASPIS's own runtime + arm its git hooks (dogfood)
Goal: ASPIS carries its own hooks config + scripts in `.aspis/`, and `.git/hooks` is armed.
1. Re-export the runtime from the catalog (same engine `init` uses, but skip init's root-file
   rewrite). A proven one-off script exists at the scratchpad path
   `…/scratchpad/reexport.py` (it calls `write_export(plan_export(catalog, base.model_copy(
   update={"runtimes":["opencode","claude"]})), root, force=True, write=True)` then
   `promote_leads(root, write=True)`). If absent, recreate it. Run it against the ASPIS root.
   - This will also create `.claude/settings.json` and `.opencode/plugins/scope-guard.ts`
     (new), and ship `.aspis/scripts/hooks/*` + `.aspis/config/hooks.yaml`.
2. Ship the hooks logic to `.aspis/` too: the reexport handles catalog assets, but the
   `scripts/` group ships via `init`'s `_ship_scripts`, not `write_export`. Simplest: run
   `uv run python -c "from aspis.operations.init import _ship_scripts; ..."` OR just copy
   `src/aspis/data/catalog/scripts/hooks/` → `.aspis/scripts/hooks/` with the editor/Bash
   `cp` (it's generated runtime, copying is fine), and `.aspis/config/hooks.yaml`.
3. Install ASPIS's own git hooks: `uv run python .aspis/scripts/hooks/install.py "$PWD"`.
   Verify `.git/hooks/pre-commit` exists and points at the venv python.
4. **Do NOT clobber `AGENTS.md`/`CLAUDE.md`** (bootstrap-filled). Verify with `git status`.
5. Clean any `__pycache__` that running scripts created under `src/aspis/data/catalog/`
   (`find src/aspis/data/catalog -name __pycache__ -type d -exec rm -rf {} +`).
6. **Gotcha — committing `.claude/settings.json` is an R-009 protected path.** Your own
   pre-commit (now armed, but `warn` mode) won't block it; it will only warn. Fine. Commit:
   `chore(F-006/T-04): regenerate runtime + arm git hooks so ASPIS runs its own hooks`.
   Keep the diff honest (it may also resync pre-existing runtime drift — that's legitimate
   per the Generated-Artifacts principle; say so in the body).
7. Run the gate; commit.

### T-06 — Docs (the why) — ✅ DONE
D-010 appended to DECISIONS.md, ARCHITECTURE.md gained a "Hooks" section, ROADMAP Phase
3.5 marked ✅ Done, TASKS boxes checked. (Reference content below, for context.)
1. `.aspis/context/DECISIONS.md` — append **D-010** (date 2026-06-20). Content:
   - Hooks are TWO deterministic surfaces (git-commit boundary + per-runtime tool-use
     boundary) over ONE shared core; no LLM in the pipeline.
   - **Non-blocking by default** (`enforcement: warn`) — auto-fix + report; one data switch
     flips to `block` once runtime blocking is designed. Rationale: ship-safe to others.
   - Git hooks install into `.git/hooks/` (logic in `.aspis/scripts/hooks/`), NOT a parallel
     `.aspis/githooks/`. Runtime wiring is adapter-emitted + capability-gated (D-002).
   - `.gitignore` sourced from the canonical Toptal API with an offline cache.
   - Commit scope is optional for lifecycle commits. Replaced the old F-005 guards.
2. `.aspis/context/ARCHITECTURE.md` — add a short "Hooks layer" paragraph (two boundaries,
   shared core, warn-default, data rules in `config/hooks.yaml`).
3. `.aspis/context/ROADMAP.md` — Phase 3.5 (F-006): mark ✅ Done on merge.
4. Update `.aspis/features/F-006-hooks/TASKS.md` checkboxes (T-01..T-06 → `[x]`).
5. Gate; commit `docs(F-006/T-06): record D-010 + hooks layer + roadmap`.

### After F-006 — merge, then F-007
1. Merge F-006 to main (user's normal flow): `git checkout main && git merge --no-ff
   feat/F-006-hooks -m "Merge feature F-006: deterministic hooks"`. Gate on main.
2. **F-007 = git subsystem** (the next feature; user owns the final design — confirm with
   them first). From research: the committer agent is the single commit authority, composes
   messages per `commit-convention.yaml`, stages explicit paths (no `-A`), and the hooks are
   the automatic wall (pre = validate/fix, commit-msg = convention, post = auto-refresh);
   split agent-role vs. automatic. The user said earlier they'd hand a final git spec —
   ASK before building F-007.
3. The user wants to PUBLISH to GitHub (v0 = the working loop + hooks + git). No remote yet;
   creating it / making it public is the user's action.

## Process reminders
- Commit per task/span with the convention; gate green before each commit.
- Run long gates in the background and poll the output file for `passed|failed`.
- Keep the user in the loop at decision points; they value agreeing per part (except where
  they said "build direct").
- Memory dir (auto-loaded each session):
  `/home/phoenix99/.claude/projects/-mnt-p-ai-empire-projects-Agentic-Software-Production-System-asps/memory/`
  — update `aspis-hooks-and-git-direction.md` and MEMORY.md when F-006 merges.
