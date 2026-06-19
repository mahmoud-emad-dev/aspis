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
3. **Clarify** — skill `requirement-clarification`. Resolve assumptions; ask at most
   five real questions (impact × uncertainty); record answers in the SPEC's
   Clarifications. Send genuine unknowns to the Research Lead. Mark anything still
   open as `[NEEDS CLARIFICATION]`.
4. **Spec** — skill `feature-planning` → fill `SPEC.md`: goal, scope, prioritized
   user stories (P1/P2), `FR-###`, `SC-###`, feature rules & style.
5. **Architecture** — skill `architecture-planning` → fill `PLAN.md`: approach,
   technical context, the rules gate-check, steps, risks/rollback.
6. **Tasks** — skill `task-decomposition` → fill `TASKS.md` (phases: Setup →
   Foundational → per-story tests-first → Polish; `[P]`/`[US]` markers; exact paths).
   Then run `python .aspis/scripts/planning/task_compile.py` to emit one packet per
   task into `tasks/`, and enrich each packet's rich fields from feature context.
7. **Plan review** — skill `review-strategy` + the `plan-critic` workflow: check
   cross-artifact consistency (spec↔plan↔tasks) before any build.
8. **Gate** — run `python .aspis/scripts/planning/prereq_validate.py --phase build`.
   It must pass before handing off.

## Mode overlays
- **vibe** — step 1 sets it; compress step 4 to a few SPEC bullets; **skip** steps 5
  and 7; step 6 stays coarse (large tasks). prereq-validate won't require PLAN.md.
- **mvp** — step 5 is a light note; step 7 is a self-check, not the Reviewer.
- **production** — all steps, full depth; step 7 is an independent Reviewer pass.

## Outputs
A scaffolded feature with SPEC (+ PLAN, TASKS per mode), task packets in `tasks/`, a
green prereq gate, and an active pointer.

## Handoff
Hand to the **Build Lead** (`build.md`) with the feature id and mode.
