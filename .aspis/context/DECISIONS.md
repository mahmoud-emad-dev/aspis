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
