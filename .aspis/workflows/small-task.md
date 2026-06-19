# Workflow: Small task / bug

The lightweight track for one coherent, low-risk change — no spec, no architecture.
Scaling the process to the work (CORE_LOOP §1): a typo must not get an epic's ceremony.

## When to use
A single self-contained change: a one-liner, a rename, a config tweak, a small bug.
Anything spanning many files or carrying real risk → promote to the feature track
(`plan.md`). A defect with an unclear cause → `fix.md`.

## Steps

1. **Classify** — skill `planning-intake`. Confirm this is trivial/small, not a
   feature in disguise. Pick the mode (usually the project default).
2. **One packet** — write a single `TASK_PACKET.md` (or, for a trivial one-liner, work
   directly): context, allowed files, steps, acceptance, the gate command.
3. **Build** — make the change in scope (`scope-control`); add a test if behaviour
   changes (`selective-testing`).
4. **Review** — a single pass sized to risk (`review-strategy`); escalate to the
   Reviewer only if it turns out to be cross-cutting or security-touching.
5. **Gate & commit** — run the gate; hand to the `committer`.

## Outputs
The change made, gate green, one in-scope commit. No feature directory unless the
work grows — at which point switch to `plan.md`.
