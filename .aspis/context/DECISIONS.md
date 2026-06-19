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
