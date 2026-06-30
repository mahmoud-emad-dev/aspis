# Workflow: Plan a feature

The Planning Lead's spine for the **feature** track. Follow the steps in order; each
names the skill that does the thinking, the script that does the mechanics, and the
artifact it produces. Do not skip a step silently — compress or drop it only where a
mode overlay says so. See `.aspis/context/CORE_LOOP.md` for the why.

## When to use
A new capability spanning multiple files. (Trivial/small work → `small-task.md`;
whole new project → decompose into features first.)

## Prerequisites
The request, and read-first context: `CURRENT_STATE.md`, `FILE_REGISTRY.yaml`, and the
project rules. Nothing else yet.

## Steps

1. **Intake & classify** — skill `planning-intake`. Read `.aspis/config/modes.yaml`,
   confirm the track is *feature*, pick the **mode**, and state the plan-of-plan in
   one or two lines (track, mode, artifacts).
2. **Scaffold** — run `python .aspis/scripts/planning/feature_scaffold.py --name "<goal>"
   --mode <mode>`. This creates `.aspis/features/F-NNN-slug/`, copies SPEC/PLAN/TASKS,
   writes the active pointer, and creates the branch.
3. **Context** — skills `prestart-checks` + `context-ladder`. Run `aspis preflight` to
   confirm the branch is clean. Load context in levels per the ladder: L1 hot state
   first, then the existing architecture, then deeper research. Stop loading as soon as
   you have enough to act.
4. **Clarify** — skill `requirement-clarification`. Resolve assumptions; ask at most
   five real questions (impact × uncertainty); record answers in the SPEC's
   Clarifications. Send genuine unknowns to the Research Lead. Mark anything still
   open as `[NEEDS CLARIFICATION]`.
5. **Spec** — skill `feature-planning` → fill `SPEC.md`: goal, scope, prioritized
   user stories (P1/P2), `FR-###`, `SC-###`, feature rules & style. Apply the 12
   quality standards (S-01…S-12): one-sentence goal, explicit scope, FR→task
   traceability, SC→verification, sequenced deps, ≤3 files/task, named tests,
   constitution compliance, review strategy, no unresolved clarifications, no stubs,
   plan as a file.
6. **Architecture** — skill `architecture-planning` → fill `PLAN.md`: approach,
   technical context, the rules gate-check, steps, risks/rollback. Auto-escalate
   mode if the scope warrants it (E1 protected paths → ≥MVP; E2 architecture/security
   → production; E3 10+ files → production).
7. **Tasks** — skill `task-decomposition` → fill `TASKS.md` (phases: Setup →
   Foundational → per-story tests-first → Polish; `[P]`/`[US]` markers; exact paths).
   Then run `python .aspis/scripts/planning/task_compile.py` to emit one packet per
   task into `tasks/`, and enrich each packet's rich fields from feature context.
8. **Plan review** — skill `review-strategy` + the `plan-critic` workflow: check
   cross-artifact consistency (spec↔plan↔tasks) before any build. In production
   mode this must be an independent Reviewer pass, not a self-check.
9. **Gate** — run `python .aspis/scripts/planning/prereq_validate.py --phase build`.
   It must pass before handing off.

## Architecture Memory (architectural change only) — skill `architecture-memory`
A project's per-subsystem *intent* lives in `.aspis/architecture/subsystems/`. When the
work touches a subsystem, **read** its file during step 3 and design with it (honor what is
marked FIXED). If the plan changes a subsystem's responsibilities, boundaries, lifecycle,
integrations, or contracts — or adds/removes one — **record** an `ARCHITECTURE_IMPACT.md`
(`aspis artifact architecture-impact`) alongside step 6 and return it to the project-lead,
who confirms it with the user before any subsystem file is written. You detect and record;
you never edit or confirm intent. Mode-gated by the `architecture` knob (below).

## Mode overlays
- **vibe** — step 1 sets it; compress step 5 to a few SPEC bullets; **skip** steps 3
  (Context), 6 (Architecture), and 8 (Plan review); step 7 stays coarse (large tasks).
  prereq-validate won't require PLAN.md. Architecture Memory is read-only orientation — no
  impact report, no gate.
- **mvp** — step 6 is a light note; step 8 is a self-check, not the Reviewer. Architecture
  Memory is collapsed: record + return an impact report only when intent actually changes.
- **production** — all steps, full depth; step 8 is an independent Reviewer pass. Architecture
  Memory runs the full loop (analyse → read → record → confirm → verify).

## Outputs
A scaffolded feature with SPEC (+ PLAN, TASKS per mode), task packets in `tasks/`, a
green prereq gate, and an active pointer.

## Handoff
Hand to the **Build Lead** (`build.md`) with the feature id and mode.
