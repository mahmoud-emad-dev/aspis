# Workflow: Build a feature

The Build Lead's spine. The Build Lead holds the whole-feature context and drives one
packet at a time; workers stay context-isolated. Delegate only when it adds value.

## When to use
A planned feature with task packets in `.aspis/features/F-NNN-slug/tasks/`.

## Prerequisites
`prereq_validate.py --phase build` passes. Read the SPEC, PLAN, and the active pointer.

## Steps

1. **Readiness** — skill `build-readiness`. Confirm the branch, the gate command, and
   that packets exist. If a packet is thin, enrich its rich fields (context, refs,
   skeleton, acceptance, review routing) from feature context before delegating.
2. **Order the work** — skill `task-orchestration`. Walk packets in dependency order;
   run `[P]` tasks in parallel only when they touch different files.
3. **Per task:**
   a. **Delegate or do** — small/low-risk task: make the change directly. Larger task:
      delegate to `general-builder` with *only* its packet (context isolation).
   b. **Scope** — skill `scope-control`. Touch only the packet's allowed files (R-001).
   c. **Test** — skill `selective-testing` per the packet's test line and the mode's
      `test_depth`.
   d. **Review** — per the packet's **review routing**: a sub-agent reviewer by
      default; escalate to the **Reviewer lead** (`review.md`) for high-criticality,
      cross-cutting, or security tasks. Vibe collapses this to one light pass.
   e. **Commit** — hand the approved change to the `committer` (the only git writer).
      Never commit yourself.
4. **Track & verify** — mark the task done; when all packets are done, verify the
   result against the SPEC's acceptance (`SC-###`). Rejections route back to a builder
   or the **Fix Lead** (`fix.md`).

## Mode overlays
- **vibe** — step 3d is one light pass; `test_depth: gate` (the build gate only).
- **mvp** — standard per-task review; core-path tests.
- **production** — full multi-lens review; tests-as-spec.

## Outputs
All packets complete, gate green, acceptance met, each change committed in scope.

## Handoff
Hand to the **Reviewer** for the feature-level acceptance decision, or report done.
