# Workflow: Small task / bug

The lightweight track for one coherent, low-risk change — no spec, no architecture.
Scaling the process to the work (CORE_LOOP §1): a typo must not get an epic's ceremony.

## When to use
A single self-contained change: a one-liner, a rename, a config tweak, a small bug.
Anything spanning many files or carrying real risk → promote to the feature track
(`plan.md`). A defect with an unclear cause → `fix.md`.

## Steps

1. **Classify** — skill `planning-intake`. Determine which of the 5 tracks this
   request falls into:
   - **Question** — answer directly if known; if unknown, delegate to research-lead.
     No code change needed.
   - **Trivial** — a one-liner, typo, or config tweak. Work directly; no packet.
   - **Small-task** — a single self-contained change (rename, single-file edit).
     Write one packet or work directly.
   - **Bug** — a defect report. If the cause is clear, fix here with a regression
     test. If unclear, route to **Fix Lead** (`fix.md`).
   - **Feature** — anything spanning many files or carrying real risk. Promote to
     the feature track (`plan.md`).

   Pick the mode (usually the project default). Confirm this is NOT a feature in
   disguise.
2. **One packet** — for Small-task: write a single `TASK_PACKET.md` (or, for a
   trivial one-liner or Question, work directly): context, allowed files, steps,
   acceptance, the gate command. For Bug with a clear cause: the packet includes
   the fix steps and the regression test requirement.
3. **Build** — make the change in scope (`scope-control`); add a test if behaviour
   changes (`selective-testing`).
4. **Review** — a single pass sized to risk (`review-strategy`); escalate to the
   Reviewer lead (`review.md`) only if the work turns out to be cross-cutting or
   security-touching.
5. **Gate & commit** — run the gate; hand to the `committer`.

## Outputs
The change made, gate green, one in-scope commit. No feature directory unless the
work grows — at which point switch to `plan.md`.
