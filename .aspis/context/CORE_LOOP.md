# ASPIS — The Core Loop (plan → build → review)

The design of the system's working cycle, synthesized from the older repo's
planning-kit (P0–P9), spec-kit's spec→plan→tasks→implement discipline, and the
architecture analysis. This is the blueprint for Phase 3; it names what exists and
what we still build. Status: **design — mode knobs pending user sign-off (§3).**

## 1. First principle — scale the process to the work

Deterministic-first applies to the *process itself*: not every request earns the
full pipeline. Classify first, then take the lightest path that is still safe.
Over-planning a typo and under-planning a feature are both failures.

## 2. Request classification — the first decision

The Project Lead routes; the Planning Lead sizes. Every request lands in a **track**:

| Track | Trigger | Path |
|---|---|---|
| **Question** | advice, "how/where/why" | Answer from project intelligence. No plan, no branch. |
| **Trivial** | typo, rename, one-line, config | No plan. Readiness → change → gate → commit. |
| **Small task / bug** | one coherent change, low risk | One **task packet** only (no spec/arch). Build → review → commit; bugs go via Fix Lead. |
| **Feature** | new capability, multiple files | Full feature lifecycle (§4), sized by mode. |
| **Project plan** | new project / big initiative | Project-level planning (identity, architecture, roadmap) → decomposed into features. |

A deterministic helper can *suggest* the track from signals (files touched, scope,
keywords); the lead confirms. Classification is the `planning-intake` skill's job.

## 3. Modes — the rigor dial (PROPOSED — confirm before building)

Modes are orthogonal to track: a feature can be built vibe, MVP, or production.
Mode sets *how much ceremony*. Default is **production**.

| Knob | Vibe | MVP | Production |
|---|---|---|---|
| Spec | goal + a few bullets | stories + acceptance | full SPEC.md |
| Architecture | skipped | light note | full PLAN.md |
| Task size | large | medium | small, packetized |
| Plan review | none | self-check | independent (Reviewer) |
| Test depth | build gate only | core paths | tests-as-spec, full |
| Docs | none | minimal | complete |
| Promotable? | no (throwaway) | yes → production | — |

These knobs become a **`modes.yaml` data file** the Planning Lead reads — adding a
mode or tuning a knob never touches code. (Open question: does vibe skip review
entirely, or keep a one-pass sanity check? — §11.)

## 4. Planning phases (feature track)

Lean adaptation of P0–P9 + spec-kit. Each phase has a prerequisite and an
artifact; phases compress or drop by mode (§3). Skills in `()` already exist.

- **P0 Intake & classify** (`planning-intake`) → track, complexity, mode, plan depth.
- **P1 Context & clarify** (`requirement-clarification`) → resolved assumptions +
  the few real questions; request research from the Research Lead for true unknowns.
- **P2 Spec** (`feature-planning` → `SPEC.md`) → goal, scope, behavior (GWT), numbered
  requirements, measurable acceptance. *[vibe: compress to a few bullets]*
- **P3 Architecture** (`architecture-planning` → `PLAN.md`) → approach, components,
  steps+gates, risks. *[vibe: skip; MVP: light]*
- **P4 Tasks & packets** (`task-decomposition` → `TASKS.md` + `TASK_PACKET.md`) →
  phase-organized (Setup → Foundational → per-story → Polish), dependency-ordered,
  `[P]`-parallel-marked, sized to mode. Each packet self-contained for a cheap builder.
- **P5 Plan review** (Reviewer + a `plan-critic` step) → consistency across
  spec↔plan↔tasks, gaps, missing acceptance, before any build. *[vibe: skip; MVP: self-check]*

Spec-kit's lesson, adopted: **prerequisite gating** — no plan without a spec, no
tasks without a plan, no build without tasks. Strict in production, relaxed in vibe.

## 5. Build loop (Build Lead)

readiness (`build-readiness`) → validate packet → enrich + delegate to
`general-builder` → selective test (`selective-testing`) → review per the plan's
strategy → hand to `committer` → track progress → verify completion against
acceptance. Rejections route to a builder or the Fix Lead. (All skills exist.)

## 6. Review loop (Reviewer)

strategy/ depth by risk+mode (`review-strategy`) → evaluate the in-scope quality
dimensions (`quality-review`) → verdict: approve / approve-with-notes / changes-
required / rejected (`acceptance-decision`) → route the fix. (All skills exist.)

## 7. What each case needs — have vs. build

| Asset | Have | Build (Phase 3) |
|---|---|---|
| Skills | all planning/build/review skills | a `plan-critic` review step |
| Templates | SPEC, PLAN, TASKS, TASK_PACKET | `modes.yaml`; optional project-plan template |
| Scripts | context (registry/code-map/state) | **feature-scaffold** (dir+branch+copy templates), **task-compile** (TASKS→packets), **prereq-validate** (phase gating) |
| Commands | — | `/plan` `/build` `/review` `/system` `/status` |
| Workflows | — | one workflow doc per track, and the mode overlays |
| Subagents | leads + workers | none new (extract only when a pattern repeats) |
| Validation | the gate (ruff+pytest) | prereq-validate + plan-critic |
| Hooks | — | **deferred** (not wiring runtime/aspis hooks yet) |

## 8. Phase-3 build units (ordered, each finishable)

Build incrementally through the live loop; each is its own commit:

1. **`modes.yaml`** + `planning-intake` reads it (the rigor dial as data).
2. **feature-scaffold script** — create `.aspis/features/<id>/`, branch, copy the
   mode's templates; deterministic (spec-kit `create-new-feature.sh` pattern).
3. **prereq-validate script** — enforce phase order per mode; used as a gate.
4. **task-compile script** — TASKS.md → per-task packets (old `task_compiler` pattern).
5. **workflow docs** (catalog assets) — one per track + mode overlays; what each
   lead follows.
6. **commands** — `/plan /build /review /system /status` (thin entry points to the leads).
7. **`plan-critic`** — the Reviewer's pre-build plan check.
8. **wire** — leads reference the new scripts/workflows; update profile + tests.

## 9. Outside-the-system pre-planning (context, not built)

Per the user's workflow: idea → market/validation → PRD → initial architecture are
done *outside* (e.g. with ChatGPT) for cost reasons, producing an initial PRD +
architecture the in-system Planning Lead then revises against project rules, stack,
and current code. ASPIS consumes those as inputs; it does not rebuild them yet.

## 10. Principles carried through the loop

Determinism is the cost lever (rich packets → cheap builders succeed). Evidence is
the currency (each phase emits an artifact the next consumes). Tests are spec.
One writer; only the committer commits. Human gate for rules/architecture/security.

## 11. Open decisions (need user sign-off)

- **Mode knobs (§3 table)** — confirm or adjust; especially whether **vibe skips
  review** entirely.
- **Command names** — `/plan /build /review /system /status` (or different).
- **Project-plan track depth** — how heavy the project-level planning is vs. just
  decomposing into features.
