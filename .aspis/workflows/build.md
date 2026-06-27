# Workflow: Build a feature

The Build Lead's spine. The Build Lead holds the whole-feature context and drives one
packet at a time; workers stay context-isolated. Delegate only when it adds value.

## When to use
A planned feature with task packets in `.aspis/features/F-NNN-slug/tasks/`.

## Prerequisites
`prereq_validate.py --phase build` passes. Read the SPEC, PLAN, and the active pointer.

## Steps

1. **Verify readiness** — skill `build-readiness`. Run `aspis preflight` and
   `prereq_validate.py --phase build`. Confirm the branch is clean, the feature is
   active, and packets exist.
2. **Sync context** — skill `context-ladder`. Load SPEC, PLAN, ARCHITECTURE, and
   the task list. Establish feature awareness before delegating any work.
3. **Validate packet** — skill `packet-validation`. Check each packet for 4 things:
   scope (allowed files correct), feasibility (achievable with available tools),
   completeness (steps + acceptance defined), acceptance (verifiable done-conditions).
   V0–V1 failing packets → return to planning; V2 enrich; V3–V4 accept. If a packet
   is thin, enrich its rich fields (context, refs, skeleton, acceptance, review
   routing) from feature context before delegating.
4. **Order the work** — skill `task-orchestration`. Walk packets in dependency order;
   run `[P]` tasks in parallel only when they touch different files.
5. **Per task:**
   a. **Delegate or do** — small/low-risk (V0–V1) task: make the change directly.
      Larger (V2+) task: delegate to `general-builder` with *only* its packet
      (context isolation). Builders have a soft 8-turn cap, hard 16-turn cap. On
      builder failure, escalate through the tier cascade: assigned tier → same tier
      focused → escalate one tier → STOP at 3 attempts.
   b. **Scope** — skill `scope-control`. Touch only the packet's allowed files
      (R-001). No architecture drift, no gold-plating.
   c. **Test** — skill `selective-testing`. Run only the tests the change actually
      affects; classify failures (flaky/regression/pre-existing); record evidence.
      Pre-checks: `git status` + `ruff check --diff`.
   d. **Review** — per the packet's **review routing**: a sub-agent reviewer by
      default; escalate to the **Reviewer lead** (`review.md`) for high-criticality,
      cross-cutting, or security tasks. Verdict handling: approved → commit;
      approved-with-notes → apply + commit; changes-required → revise (max 3
      rejections per task); rejected → STOP, escalate to project-lead.
   e. **Commit** — hand the approved, gate-green change to the `committer` (the only
      git writer). Never commit yourself.
6. **Track & verify** — mark the task done; when all packets are done, verify the
   result against the SPEC's acceptance (`SC-###`). Rejections route back to a builder
   or the **Fix Lead** (`fix.md`). On the 3rd rejection, write REVIEW_NEEDED and
   escalate to the project-lead.

## Mode overlays
- **vibe** — step 5d is one light pass; `test_depth: gate` (the build gate only).
- **mvp** — standard per-task review; core-path tests.
- **production** — full multi-lens review; tests-as-spec. Step 3 (packet validation)
  runs the full 4-check protocol.

## Outputs
All packets complete, gate green, acceptance met, each change committed in scope.

## Handoff
Hand to the **Reviewer** for the feature-level acceptance decision, or report done.
