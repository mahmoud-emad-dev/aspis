---
name: task-decomposition
description: Use to break an approved plan into build-ready work — sequenced, dependency-ordered, appropriately sized task packets, each self-contained enough for an executor to implement, plus the execution, review, and testing strategy. Produces the TASKS list and per-task packets the Build Lead executes.
---

# Task Decomposition

## Purpose

Convert the plan into the units of work that get built. Each task is sized so an
executor — often a cheaper model — can complete it correctly from the packet
alone, in the right order, with the right checks.

## When to use

After the spec and architecture are settled, as the final planning step before
handoff to the Build Lead.

## Procedure

1. **Decompose.** Break the plan into tasks scoped to one coherent change each;
   size to complexity, risk, and mode.
2. **Sequence.** Order by dependency; mark which tasks can run in parallel.
3. **Write packets.** For each task, fill `.asps/templates/TASK_PACKET.md`: objective,
   allowed files, steps, inputs, tests, and observable "done when" acceptance — so
   it stands alone without the rest of the plan.
4. **Set strategy.** Define the execution order, the review level per task (worker
   vs lead), and the testing depth — scaled to risk.
5. Record the task list in `.asps/templates/TASKS.md`.

## Outputs

- A sequenced task list and self-contained task packets, with execution/review/
  testing strategy, ready for the Build Lead.

## Anti-patterns

- Tasks too large to execute safely or too vague to execute without guessing.
- Packets that assume context the executor won't have.
- Ignoring dependencies, or serializing work that could run in parallel.
- Leaving review and testing depth undefined.
