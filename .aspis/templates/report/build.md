# Build report — <feature-id> / <task-id>

> Filled by the builder after a task is built and the gate is green. The header
> fields are stamped by `aspis artifact`; you fill the rest from real results —
> never invent a format, and never report green without the gate output.

- **Feature**: <feature-id> — <Feature Title>
- **Task**: <task-id>
- **Date**: <date>
- **Status**: <done | blocked>

## What changed
<The files touched and what each change does — what and why, not a diff.>

## Tests (red → green)
<The test(s) that prove the behaviour: what failed first, what passes now.>

## Gate
<The deterministic gate result — ruff + pytest — pasted, not summarised.>

## Notes / hand-off
<Anything the reviewer or next task needs: follow-ups, blockers, decisions.>
