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
