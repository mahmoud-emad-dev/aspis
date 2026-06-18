---
name: project-question-answering
description: Use to respond directly from project intelligence — answer a targeted question (where is X, what changed, how does this work) or produce a project status/summary — without delegating, when project context and read-only checks are enough.
---

# Project Question Answering

## Purpose

Respond to the user directly when the answer lives in project knowledge — both
targeted questions and project-level status/summaries — so they get understanding
from the entry point instead of an unnecessary delegation.

## When to use

When `request-classification` yields a `question` or a status/summary request you
can settle from project context plus read-only checks.

## Procedure

1. Retrieve the relevant facts via `project-awareness` (state, recent changes,
   locations via the registry / `project-explorer`).
2. Confirm with read-only checks (`git status`, `git diff`, `git log`) where the
   answer depends on the working state.
3. Shape the response to the request:
   - **Targeted question** — a direct, cited answer.
   - **Status** — current state · active features · progress · risks · open work.
   - **Summary** — overview · architecture · active work · recent changes ·
     recommendation.
4. Cite the files or facts the answer rests on; synthesize what it means, don't
   just list raw facts.
5. If the request actually needs specialized work, hand off via `project-guidance`
   and `lead-routing` instead of guessing.

## Outputs

A direct, cited answer or a project status/summary — or a redirect to the correct
lead when the request is really work in disguise.

## Anti-patterns

- Delegating something you could answer from context.
- Answering from memory without checking current state.
- Listing facts without synthesizing their meaning for the project.
