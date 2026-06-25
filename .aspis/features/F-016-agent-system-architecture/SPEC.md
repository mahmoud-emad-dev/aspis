# F-016 — agent system architecture · Specification

> Mode hints: **vibe** → keep Goal + Scope + a few requirement bullets, drop the
> rest. **mvp** → stories + acceptance. **production** → the whole template.

## Goal
<One or two sentences: the outcome this feature delivers.>

## Problem
<Why this is needed now — what is missing or broken without it.>

## Scope
In scope:
- <path or capability>

Out of scope:
- <What this deliberately does NOT do — forbidden paths and deferred ideas.>

## User stories
Prioritized, each independently testable. P1 is the MVP slice.

### Story 1 — <title> (priority: P1)
- **Why this priority**: <the value this delivers and why it comes first.>
- **Independent test**: <how this story is verified on its own.>
- **Acceptance scenarios**:
  1. **Given** <state>, **when** <action>, **then** <expected outcome>.

### Story 2 — <title> (priority: P2)
- **Why this priority**: <...>
- **Independent test**: <...>
- **Acceptance scenarios**:
  1. **Given** <state>, **when** <action>, **then** <expected outcome>.

## Requirements
Numbered so tasks and acceptance can trace to them. Mark anything unresolved with
`[NEEDS CLARIFICATION: question]` instead of guessing.

- **FR-001**: The system MUST <requirement>.
- **FR-002**: The system MUST <requirement>.

## Feature rules & style
Project rules and conventions this feature must honour (naming, structure, patterns,
the relevant SYSTEM_RULES R-###). The builder follows these without re-deriving them.
- <rule or convention this feature must follow.>

## Key entities (if applicable)
- **<Entity>**: <what it is, its key attributes and relationships.>

## Success criteria
Measurable and technology-agnostic — the bar acceptance checks against.
- **SC-001**: <observable, measurable outcome>.
- **SC-002**: <observable, measurable outcome>.

## Assumptions
- <Reasonable default chosen where the request was silent.>

## Clarifications
Resolved questions, newest session first. Each becomes a fixed decision.

### Session <YYYY-MM-DD>
- Q: <question> → A: <answer>.

## Open questions
- <Human decision still needed — remove when none remain.>
