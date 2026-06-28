---
name: session-continuation
description: Detect interruption, classify the resumption type, and send a resume packet so the project-lead continues a session without losing context.
---

# session-continuation

## Purpose
When a session is interrupted (crash, timeout, user pause, context overflow),
classify what happened and produce a resume packet so the project-lead — or the
next agent in the chain — can pick up where it left off without re-doing work
or losing state.

## When to use
- At the start of every new session (the project-lead checks for a prior session).
- When a delegate times out or crashes mid-task.
- When the project-lead detects an interrupted workflow and needs to resume.

## Procedure
1. **Detect interruption** — check for signals of a prior session:
   - Active feature pointer with `phase` not in terminal state
   - Open task packets with `[~]` (in-progress) markers in TASKS.md
   - Uncommitted changes in `git status` that match the active feature's scope
   - A REVIEW_NEEDED artifact from a capped delegate
2. **Classify resumption type:**
   - **Pause** — user explicitly paused; work is clean and checkpointed. Resume
     from the next task in the sequence.
   - **Crash** — unexpected termination; work may be in an unknown state. Check
     git status and last task marker; re-run the gate to assess.
   - **Timeout** — delegate exceeded turn cap; the task packet has a REVIEW_NEEDED
     or partial result. Escalate or re-delegate with tighter scope.
   - **Left** — delegate returned but project-lead didn't process the result.
     Recontextualize the return and decide the next action.
3. **Build the resume packet** — produce a 5-field packet (INTENT · CONTEXT ·
   CONSTRAINTS · REFERENCES · EXPECTED OUTCOME) that:
   - States what was in progress (feature, task, phase)
   - Summarizes what's known from the last checkpoint
   - Identifies what needs to happen next
   - Flags any blockers or degraded state
4. **Set the resume point** — update the active feature's phase and the task
   markers to reflect the current position so the next session starts clean.

## Outputs
- A resume packet ready for the project-lead or the owning lead.
- Classified interruption type with the appropriate action.
- Updated feature/task state so the next session knows where it is.

## Anti-patterns
- Restarting from scratch without checking for prior session state — wastes work
  and creates duplicate artifacts.
- Assuming a crash didn't corrupt state — always run `aspis preflight` and the
  gate before resuming after a crash.
- Treating a timeout the same as a crash — a timeout means the delegate hit its
  cap, which is a different recovery path (escalate or re-delegate, not just re-run).
- Skipping the resume packet — the next agent needs context; don't expect it to
  derive the state from raw project files.
