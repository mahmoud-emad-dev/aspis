---
name: feature-planning
description: Use to write the specification for a feature — the goal, the problem, what is in and out of scope, the observable behavior, and measurable acceptance criteria. Produces the spec other agents build and test against, from the SPEC template.
---

# Feature Planning

## Purpose

Capture *what* will be built and *how success is measured*, technology-agnostic and
unambiguous, so building and review have a single shared source of intent.

## When to use

Once the request is classified and clarified, before architecture and tasks.

## Procedure

1. **State the goal and problem.** One or two sentences each: the outcome, and why
   it's needed now.
2. **Define scope.** What this delivers and, explicitly, what it does *not* —
   including deferred ideas.
3. **Describe behavior.** Given/When/Then scenarios for each slice, prioritized.
4. **Write requirements.** Numbered, testable statements of what the system must do.
5. **Set acceptance.** Measurable, technology-agnostic success criteria — the
   checkable conditions for "done."
6. **Record assumptions and open questions** carried from clarification.

Fill the `.aspis/templates/planning/SPEC.md` template; keep it free of implementation detail
(that belongs in the architecture).

## Outputs

- A completed spec with scope, behavior, requirements, and measurable acceptance.

## Anti-patterns

- Mixing implementation design into the spec.
- Acceptance criteria that can't be objectively checked.
- Silent scope — omitting what is deliberately *not* included.
