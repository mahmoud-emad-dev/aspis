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
