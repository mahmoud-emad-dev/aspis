---
name: task-orchestration
description: Use to drive a feature's tasks to completion — validate each packet, select and enrich a builder, delegate execution, coordinate review, track progress, and verify completion. The Build Lead's core execution loop; worker success depends on the context quality you provide.
---

# Task Orchestration

## Purpose

Move planned tasks into completed, reviewed software by coordinating disposable
workers well. The lead holds the feature context; each worker gets exactly what it
needs to execute one task correctly.

## When to use

Throughout implementation, once readiness is confirmed — for every task in the plan.

## Procedure

1. **Validate the packet.** Before running a task, confirm its scope, file list,
   acceptance, and feasibility. You are the final execution gate — fix or return a
   weak packet rather than running it.
2. **Select the builder.** The general builder handles most work; choose a
   specialized builder only when its expertise clearly helps.
3. **Enrich context.** Hand the worker the packet plus scope, relevant files,
   dependencies, constraints, acceptance, and test/review requirements.
4. **Delegate and collect.** The worker implements, tests its change, and returns a
   report (files changed, tests run, deviations, risks). Workers are disposable and
   do not own feature state.
5. **Coordinate review.** Route the change through the review path the plan
   specifies (worker, lead, or escalated); send rejections back for a fix.
6. **Track progress.** Update task/feature state as each task lands; keep an
   accurate picture of what's done.
7. **Verify completion.** The feature is done only when all tasks, required reviews,
   tests, and evidence check out — confirm it yourself.

## Outputs

- Completed, reviewed tasks with build evidence, and current progress records.

## Anti-patterns

- Running an under-specified packet instead of strengthening it first.
- Thin context that sets the worker up to guess and fail.
- Trusting a worker's "done" without verifying against acceptance.
- Letting workers commit or own feature state.
