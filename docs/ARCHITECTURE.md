# ASPIS — Architecture (intended)

The stable design intent — the *why* and the target shape ASPIS is built toward. It
changes rarely. For what actually exists today (the as-built contract that build and
review compare against), see [`.aspis/context/ARCHITECTURE.md`](../.aspis/context/ARCHITECTURE.md).

## The bet

> Quality = model capability × task clarity × test strength × review discipline

Instead of hoping a frontier model gets it right, ASPIS engineers clarity, determinism,
tests, and review so the *cheapest sufficient* model produces production-grade software —
repeatably, not once.

## Three layers

1. **Factory repo** — where ASPIS itself is developed (engine, catalog, tests).
2. **Global install** — the `aspis` CLI and engine on a machine.
3. **Target project** — a project ASPIS manages. It receives a tool-neutral `.aspis/`
   brain (the durable memory) and generated per-runtime assets (`.claude/`, `.opencode/`,
   …) that are rebuilt from the catalog.

## Design principles (the load-bearing ideas)

- **Runtime-neutral catalog, per-runtime adapters.** One superset source; each adapter
  emits only what its runtime supports and never errors. No runtime is hard-coded.
- **Deterministic-first.** Prefer the cheapest mechanism that solves a need — code before
  an agent. Determinism is the cost lever: shrink what the model must figure out.
- **Agent = thin instruction + skills.** Identity and rules in the instruction; the
  intelligence lives in reusable skills.
- **Evidence is the currency.** Each phase emits a report/result tied to a commit; later
  actors consume it instead of redoing the work.
- **Machine-checked invariants hold; prose-asserted ones rot.** Every "X must match Y"
  becomes a test or generated code, not a doc promise.
- **Capture now, derive later.** Reserve the seam for future intelligence; don't build the
  far layer early.

## Governance

A lead roster plans → builds → reviews under deterministic gates (ruff + pytest) and a
single commit authority. Only the System Lead may change the generated runtime and
protected areas.

## Direction

Ordered phases: engine spine → lead roster → live factory + governance → default
production system → **tracing spine** → **self-improvement** → **surfaces (dashboard)**.
The later phases are reserved seams, not yet built — see [`ROADMAP.md`](../.aspis/context/ROADMAP.md)
for live status.
