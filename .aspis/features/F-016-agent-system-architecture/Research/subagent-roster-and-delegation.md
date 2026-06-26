# F-016 — Subagent Roster & Delegation Model (design decision)

> Captured from the system owner's direction. This records WHAT to build and the
> delegation philosophy behind it. It does not itself build anything — it is the
> input to planning the build (see "Execution path" at the end).

## Decision

For each lead agent, build everything it genuinely needs to work well: its
**skills, assets, scripts, and its subagents** (each with their own skills).
Build what is **needed and load-bearing** — not a speculative org chart
(honours R-003). The roster below is the bounded "needed" set.

## Why subagents — the delegation philosophy

- A lead runs on a **higher-capability (costly) model**; its context window is
  precious and must stay clean.
- The **bulk of work is mechanical or context-heavy**: reading many files,
  running tools, drafting file contents, simple checks. This should go to a
  **cheap-model, specialised subagent** given a clear, scoped packet.
- The subagent **absorbs the noisy read/execution work** and returns only a
  **summary / report / written file** — keeping the lead's context clean and the
  cost low. A cheap model, well-scoped, does this correctly.
- The lead **reserves its higher model for judgment**: critical decisions,
  careful/critical review, synthesis, and anything needing full cross-context.

## When a lead does it ITSELF vs delegates

Declared **per lead** (driven by its skills/tools/scripts), and varying by the
**model in play** and **task criticality**:

- **Do it itself** when: the task is genuinely simple *and* needs the lead's own
  full context; or it is a critical judgment the higher model must own; or the
  context-handoff cost would exceed the work.
- **Delegate** when: the work is mechanical, context-heavy, parallelisable, or
  specialised, and can be packaged as a clear scoped task a cheap model can do.
- **Don't** delegate trivially (no paying context-switch cost for something the
  lead can just do); **don't** fill the lead's context with raw tool output a
  subagent could have digested first.

## Roster (build what's needed)

| Lead | Subagents | Purpose |
|------|-----------|---------|
| **general (shared)** | 2+ | Reusable helpers any lead calls for consistent, quality mechanical work (e.g. context-feeder, context-summarizer) |
| **research-lead** | 3+ | codebase-explorer · docs-fetcher · web-researcher (+ cache-manager) |
| **planning-lead** | 2–3 | clarify · task-decomposer · constitution-checker |
| **reviewer** | 2–3 | cheap-model sub-reviewer for simple/little checks + parallel multi-perspective cheap reviews; the reviewer lead (higher model) keeps critical/diff review |
| **fix-lead** | 1–2 | general-fix · general-inspect |
| **test-lead** | 1–2 | test-author (stack testers later) |
| **system-lead** | 3+ **(deferred — not now)** | runtime-validator · drift-auditor · permission-auditor etc. |

## Principle to encode — proposed R-010 "Delegate with purpose"

> A lead pushes mechanical and context-heavy work to a cheap, scoped subagent and
> keeps its own (higher) model for judgment and critical review. Don't delegate
> trivial work that costs more to hand off than to do; don't fill the lead's
> context with raw tool output a subagent can digest into a summary.

(Stated once as a system rule; each lead spec then carries a short, lead-specific
"I do myself / I delegate" section — different per lead, so not duplication.)

## Execution path (important)

This is **feature-sized**: ~12 subagents + their skills/scripts + per-lead
delegation sections + catalog files. To stay practical (not giant/rigid) it
should be **planned then built through the normal loop** — each subagent real,
tested, catalog-correct — as either an expansion of F-016's scope or a dedicated
follow-up (F-017). It should not be improvised by hand.
