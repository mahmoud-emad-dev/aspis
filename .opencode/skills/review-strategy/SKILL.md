---
name: review-strategy
description: Use at the start of a review to decide its scope and depth — what to evaluate and how hard, scaled to the risk, complexity, and mode of the change. Focuses review effort where it matters instead of reviewing everything the same way.
---

# Review Strategy

## Purpose

Spend review effort where risk lives. A one-line config change and a new auth flow
should not get the same scrutiny; the strategy decides depth before evaluation
begins.

## When to use

First, when a review is requested, before evaluating quality.

## Procedure

1. **Identify the artifact and stage.** Plan, task, implementation, or whole
   feature — and where in the lifecycle it sits.
2. **Read the risk.** Complexity, blast radius, security exposure, and the mode
   (production demands more than vibe).
3. **Pick the dimensions.** Choose which of correctness, scope, architecture,
   maintainability, reliability, security, performance, standards, and documentation
   actually apply to this change.
4. **Set the depth.** Decide how deep each dimension goes and what evidence you'll
   demand (diff read, test run, reproduction).

## Outputs

- A review plan: the dimensions in scope and the depth for each.

## Anti-patterns

- Reviewing every change with identical depth regardless of risk.
- Skipping security/architecture on a change that clearly affects them.
- Deep-diving low-risk changes while rushing high-risk ones.
