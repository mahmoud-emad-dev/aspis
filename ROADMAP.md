# ASPIS — Roadmap

> Where ASPIS is, where it is going, and — just as importantly — what it
> deliberately does **not** do yet.

ASPIS is built in **six parts** that follow a user's journey: install it,
onboard a project, use it to build software, then measure, improve, and surface
that work. Each part ships a deterministic core a real user can feel before the
next is started — so the system is useful early, not only when it is "finished".

**Today, Parts 1–2 are shipped — roughly one third of the full plan.** The
current focus is making them rock-solid: the models, agents, skills, workflows,
the plan→build→review→test loop, permissions, and runtimes. Part 3 (tracing) is
next; Parts 4–6 are designed as seams but not built.

---

## North star

A deterministic software-production factory where the **cheapest sufficient
model runs correctly** — because the work is shrunk by structure: tight tasks,
rich context, conformant templates, deterministic gates, and scoped review, with
every run traced so the system can measure and improve itself.

## The foundation (cross-cutting)

Every part rides on one engineering bedrock, not a feature of its own:

- **Single source of truth** — one runtime-neutral catalog compiles into each
  runtime (`.claude/`, `.opencode/`) through per-runtime adapters. No duplicated
  truth to drift.
- **Extensibility core** — the engine grows by *adding a file*, not editing core
  code: asset kinds are a data registry and runtimes declare the kinds they
  support.
- **Architecture constitution** — a global engineering-standards layer wired into
  the planning, build, and review leads, so principles are checked, not hoped for.

---

## The six parts

### Part 1 — Install & Onboarding ✅ shipped

**Problem.** A factory is worthless if it can't be installed reliably and a new
project can't be brought to a known-good starting line.

**Proved.**
- One-command install; `aspis` runs on Windows and Linux (both CI-gated).
- Detection of installed runtimes and tools from data (`data/runtimes/*.yaml`) —
  no hardcoded runtime list.
- `init` → `bootstrap` lifecycle: empty folder → chosen runtime + profile + mode
  → rich scaffold → enriched brain → first commit → self-cleaning onboarding.
- `aspis doctor` reports a project's health in one read.

### Part 2 — The Production System ✅ shipped (now hardening)

**Problem.** *How does it actually build software, cheaply and correctly?* This
is the heart: the agents, the loop, and the deterministic walls around them.

**Proved.**
- **Roster** — a lean layered set of agents (leads + workers) with thin,
  single-responsibility prompts and a clear delegation map.
- **Skills & workflows** — the "how" lives in reusable skills; each track has a
  plan→build→review→test workflow.
- **The build loop** — `/plan → /build → /review → /test`, driven through the
  leads via a task-packet contract; double-checking is always a *different* agent
  than the builder.
- **Working modes** — `vibe` / `mvp` / `production` as data (`modes.yaml`), a
  project default, settable per request; mode is a *ceiling*, not a floor.
- **Permissions** — every agent's allowlist is the real boundary, with a golden
  test that every command an agent is told to run (and every delegate it names)
  is actually permitted.
- **Runtimes & models** — data-driven model routing: a canonical model catalog,
  per-runtime detection, and a resolver that routes each agent to an available,
  correctly-spelled model under a clear precedence.
- **Deterministic gates & hooks** — git-boundary hooks (junk clean, scope,
  secrets, commit convention) and a fire-and-forget findings trail; rules are
  data, non-blocking by default.
- **Git subsystem** — `aspis commit` is the single commit authority: stage named
  paths, compose a convention-checked message, let the hooks enforce.

**To prove (current hardening focus).** End-to-end real builds on real runtimes;
sharper per-agent context discipline; making every prose guarantee a
machine-checked one.

### Part 3 — Tracing ⏳ next

**Problem.** You cannot pick the cheapest-sufficient model, or prove quality,
without per-run cost and outcome data. Everything above currently runs *blind*.

**Planned.** One trace writer keyed by `run_id`; append-only JSONL as truth plus
a normalized store as a rebuildable lens; cost + quality measurable per
feature / agent / model. Capture can begin in parallel with Part 2 usage.

### Part 4 — Intelligence / Self-improvement 🔒 reserved

**Problem.** A factory should get better from its own history, not only from
hand edits.

**Outline.** Detect repeated patterns → propose assets → **human gate** →
bounded apply (config / scope / model-tier only — never weaken gates, tests, or
rules) → measure the effect. Reads the Part 3 store; not a rewrite of the core.

### Part 5 — Surfaces / Dashboard 🔒 reserved

**Problem.** The engine's state and evidence should be visible at a glance.

**Outline.** A project cockpit that is a thin **view over a stable read-model** of
the engine — never a fork of it. Renders blank until Part 3 feeds it, by design.

### Part 6 — Scale & Ecosystem 🔒 reserved

**Outline.** Remote/shared catalog, more runtimes and role profiles, and a
cross-project learning brain. Interfaces in earlier parts are shaped so these are
additive, not a rewrite.

---

## What ASPIS does **not** do yet

Being explicit so expectations are honest:

- **No measurement.** Model capability scores are hand-seeded; there is no tracing
  or cost/quality data yet (Part 3).
- **No self-improvement.** The system does not propose or apply changes to itself
  (Part 4).
- **No dashboard / UI.** ASPIS is a CLI plus a file-first brain (Part 5).
- **No remote catalog or cross-project learning** (Part 6).
- **Two runtimes only** — OpenCode and Claude Code. Others are added as adapters,
  not core changes.

## Open design questions

- **Project-plan track.** The deep project-level planning flow (heavier than a
  single feature) is still to be designed; for now a project decomposes into
  features.
- **Delegation depth.** Kept to ~two effective levels (a selectable lead → its
  workers); deep nesting can stall in some runtimes.
- **On-demand role profiles** (e.g. data-analyst, automation) and the
  cross-project learning brain are later layers, not now.

---

*This roadmap is the public summary. The dated decision log lives in
[`.aspis/context/DECISIONS.md`](.aspis/context/DECISIONS.md); the as-built
architecture in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).*
