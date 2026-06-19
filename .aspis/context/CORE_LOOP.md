# ASPIS — The Core Loop (plan → build → review)

The design of the system's working cycle, synthesized from the older repo's
planning-kit, spec-kit's spec→plan→tasks→implement discipline, and the
architecture analysis. This is the blueprint for Phase 3; it names what exists and
what we still build. Status: **decisions locked (§3, §12) — building.**

## 1. First principle — scale the process to the work

Deterministic-first applies to the *process itself*: not every request earns the
full pipeline. Classify first, then take the lightest path that is still safe.
Over-planning a typo and under-planning a feature are both failures.

And **delegate only when delegation adds value** (architecture analysis): a small
task goes Project Lead → Build Lead with no worker; only larger implementation work
spawns a sub-builder. Workers are optional tools, not mandatory hops.

## 2. Request classification — the first decision

The Project Lead routes; the Planning Lead sizes. Every request lands in a **track**:

| Track | Trigger | Path |
|---|---|---|
| **Question** | advice, "how/where/why" | Answer from project intelligence. No plan, no branch. |
| **Trivial** | typo, rename, one-line, config | No plan. Readiness → change → gate → commit. |
| **Small task / bug** | one coherent change, low risk | One **task packet** only (no spec/arch). Build → review → commit; bugs go via Fix Lead. |
| **Feature** | new capability, multiple files | Full feature lifecycle (§4), sized by mode. |
| **Project plan** | new project / big initiative | Project-level planning → decomposed into features. Deeper than a feature; its core workflow is designed later (§12). |

A deterministic helper can *suggest* the track from signals (files touched, scope,
keywords); the lead confirms. Classification is the `planning-intake` skill's job.

## 3. Modes — the rigor dial (LOCKED)

Modes are orthogonal to track: a feature can be built vibe, MVP, or production.
Mode sets *how much ceremony*. Default is **production**. The knobs live in a
data file (`modes.yaml`) the Planning Lead reads — adding a mode or tuning a knob
never touches code.

**Mode is a ceiling, not a floor.** The track (chosen by size/complexity, §2) sets
the *path*; the mode tunes the rigor *on that path*. A small change in production mode
still takes the small-task path — production demands a test and a review there, but
never forces a full spec+architecture onto a one-file edit. Real simplicity collapses
phases even under production; real risk resists vibe. Resolution of *which* mode:
request > active feature > project default (`.aspis/config/project.yaml`) > `modes.yaml`.

| Knob | Vibe | MVP | Production |
|---|---|---|---|
| Spec | goal + a few bullets | stories + acceptance | full SPEC.md |
| Architecture | skipped | light note | full PLAN.md |
| Task size | large | medium | small, packetized |
| Plan review | none | self-check | independent (Reviewer + plan-critic) |
| Build review | **light — single pass, key checks only** | per-task, standard | per-task, full multi-lens |
| Test depth | build gate only | core paths | tests-as-spec, full |
| Docs | none | minimal | complete |
| Promotable? | no (throwaway) | yes → production | — |

**Vibe is not "no review"** — it gets ONE light pass that checks the few things
that matter (does it run, is it in scope, no obvious breakage), not the full deep
multi-analysis review MVP/production get. Review is a dial, not a switch.

## 4. Planning phases (feature track)

Lean adaptation of the old planning-kit + spec-kit. Each phase has a prerequisite
and an artifact; phases compress or drop by mode (§3). Skills in `()` already exist.

- **P0 Intake & classify** (`planning-intake`, reads `modes.yaml`) → track, complexity, mode, plan depth.
- **P1 Context & clarify** (`requirement-clarification`) → resolved assumptions +
  the few real questions (max 5, by impact×uncertainty); request research from the
  Research Lead for true unknowns. Unresolved items become `[NEEDS CLARIFICATION]`.
- **P2 Spec** (`feature-planning` → `SPEC.md`) → goal, scope, prioritized user
  stories (P1/P2/P3) with Given/When/Then, numbered `FR-###` requirements,
  measurable `SC-###` success criteria, assumptions, feature rules/style.
  *[vibe: compress to a few bullets]*
- **P3 Architecture** (`architecture-planning` → `PLAN.md`) → approach, technical
  context, components, steps+gates, risks, rollback. *[vibe: skip; MVP: light note]*
- **P4 Tasks & packets** (`task-decomposition` → `TASKS.md` + per-task packets) →
  phase-organized (Setup → Foundational → per-story → Polish), dependency-ordered,
  `[P]`-parallel-marked, tests-first within a story, sized to mode. `task-compile`
  then emits one self-contained packet per task (§5).
- **P5 Plan review** (Reviewer + `plan-critic`) → cross-artifact consistency
  (spec↔plan↔tasks), gaps, missing acceptance, before any build.
  *[vibe: skip; MVP: self-check]*

Spec-kit's lesson, adopted: **prerequisite gating** — no plan without a spec, no
tasks without a plan, no build without tasks. Strict in production, relaxed in vibe;
enforced by the `prereq-validate` script (§7).

## 5. The task packet — the contract for a context-isolated builder

The packet is the heart of the loop. Per the analysis, L3 workers exist for
**context isolation**: the Build Lead holds the whole-feature context and hands each
task to a *fresh, context-less* sub-builder via a packet so complete the builder
needs nothing else. That lets one Build Lead drive 10–20 tasks without exhausting its
own window, each task built at full focus. The packet's richness *is* the cost lever.

One packet per task, written to `.aspis/features/<id>/tasks/T-NN.md`, carrying:

- **Identity** — feature id, task id, short title, task **type** (setup / test /
  model / service / endpoint / wiring / docs / fix), criticality (low/med/high),
  and the mode + model tier it's sized for.
- **Context** — 2–4 sentences: what exists, what this changes, why. Plus the
  **reference files** to read first (from FILE_REGISTRY / CODE_MAP) — not the whole
  repo, just what this task needs.
- **Scope** — allowed files (edit ONLY these) and forbidden (everything else +
  secrets). The scope guard (R-001).
- **Steps** — precise, ordered, each naming the exact file and change.
- **Skeleton / pseudo-code** — the shape of the code to write (signatures, control
  flow, key data structures) so the builder fills in, not invents.
- **Dependencies & integration** — which tasks must precede this, what it consumes
  from them, what downstream tasks consume from it.
- **Outputs** — the observable artifacts this task produces.
- **Acceptance** — the measurable done-conditions (tied to SPEC FR-###/SC-###).
- **Tests** — what to test, red→green, the exact command; or "none — gate only"
  when the mode/type doesn't warrant a test.
- **Review routing** — does this task need review, and by whom: a **sub-agent
  reviewer** (default, per-task, context-isolated) or escalate to the **Reviewer
  lead** (high criticality / cross-cutting / security). Set by criticality + mode.
- **Verify** — the exact gate commands. **On failure** — never weaken tests; stop
  and report what's needed.

The Build Lead enriches each packet from its whole-feature context before delegating;
the builder executes only its packet; a reviewer (sub-agent or lead, per the packet)
checks it; the committer commits. Rejections route back to a builder or the Fix Lead.

## 6. Build loop (Build Lead)

readiness (`build-readiness`) → validate packet (`prereq-validate`) → enrich +
delegate to `general-builder` (only when it adds value; small tasks done directly) →
selective test (`selective-testing`) → review per the packet's routing (§5) → hand to
`committer` → track progress → verify completion against acceptance. (All skills exist.)

## 7. Review loop (Reviewer)

strategy/depth by risk+mode (`review-strategy`) → evaluate the in-scope quality
dimensions (`quality-review`) → verdict: approve / approve-with-notes / changes-
required / rejected (`acceptance-decision`) → route the fix. Vibe collapses this to a
single light pass (§3). (All skills exist.)

## 8. What each case needs — have vs. build

| Asset | Have | Build (Phase 3) |
|---|---|---|
| Skills | all planning/build/review skills | `plan-critic` review step; teach `planning-intake` to read `modes.yaml` |
| Templates | SPEC, PLAN, TASKS, TASK_PACKET (lean) | enrich all four to the schemas above; add `modes.yaml`; ACCEPTANCE |
| Scripts | context (registry/code-map/state) | **feature-scaffold**, **task-compile**, **prereq-validate** |
| Commands | — | `/plan` `/build` `/review` `/system` `/status` |
| Workflows | — | one markdown workflow doc per track, with mode overlays |
| Subagents | leads + workers | none new (extract only when a pattern repeats) |
| Validation | the gate (ruff+pytest) | prereq-validate + plan-critic |
| Hooks | — | **deferred** (not wiring runtime/aspis hooks yet) |

## 9. Workflow docs — steps as data, not improvisation

Each track gets a **markdown workflow doc** (a catalog asset) the lead follows
step-by-step, with mode overlays naming which phases compress or drop. This is how we
stop agents from hallucinating or skipping steps: the procedure is written down and
versioned, beside the skills, and the deterministic scripts do the mechanical parts
(scaffold, compile, validate) so the model only does judgment.

## 10. Phase-3 build units (ordered, each finishable)

Build incrementally through the live loop; each is its own commit:

1. **`modes.yaml`** + `planning-intake` reads it (the rigor dial as data).
2. **Enrich the templates** — SPEC / PLAN / TASKS / TASK_PACKET to the §2–§5 schemas.
3. **feature-scaffold script** — create `.aspis/features/<id>/`, branch, copy the
   mode's templates, write `active_feature.json` (old `planning_setup` pattern, lean).
4. **task-compile script** — TASKS.md → per-task packets under `tasks/`.
5. **prereq-validate script** — enforce phase order per mode; used as a gate.
6. **workflow docs** — one per track + mode overlays.
7. **commands** — `/plan /build /review /system /status` (thin entry points to leads).
8. **`plan-critic`** — the Reviewer's pre-build cross-artifact plan check.
9. **wire** — leads reference the new scripts/workflows; update profile + tests.

## 11. Outside-the-system pre-planning (context, not built)

Per the user's workflow: idea → market/validation → PRD → initial architecture are
done *outside* (e.g. with ChatGPT) for cost reasons, producing an initial PRD +
architecture the in-system Planning Lead then revises against project rules, stack,
and current code. ASPIS consumes those as inputs; it does not rebuild them yet.

## 12. Principles carried through the loop

Determinism is the cost lever (rich packets → cheap builders succeed). Workers are
context isolation (the Build Lead keeps focus; tasks run fresh). Evidence is the
currency (each phase emits an artifact the next consumes). Tests are spec. One writer;
only the committer commits. Human gate for rules/architecture/security.

**Locked (this branch):** vibe keeps a light single-pass review (§3); commands are
`/plan /build /review /system /status`. **Deferred:** the project-plan track's deep
core workflow (heavier than a feature) is designed in a later pass; for now it
decomposes into features.
