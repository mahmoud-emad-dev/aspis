---
type: template
category: planning
version: 1.0
---

# Clarification Log — <feature-id>

> Record every clarification Q&A during planning so assumptions are traceable,
> decisions are dated, and the plan reviewer can see what was resolved vs. what
> was guessed. One entry per question.

---

## Question <N>

- **Question**: <The exact question asked — keep it verbatim, not paraphrased.>
- **Asked by**: <Role — planning-lead, reviewer, build-lead, etc.>
- **Asked on**: <YYYY-MM-DD>
- **Answered by**: <Role or name — project-lead, user, SME, etc.>
- **Answer**: <The resolution — verbatim if possible, summarized if the answer
  was conversational.>
- **Impact on plan**: <What changed as a result — scope added/removed, a task
  split, a dependency reclassified, a mode change, or "none — confirmed
  assumption.">
- **Resolution date**: <YYYY-MM-DD>

---

## Example

### Question 1

- **Question**: Does the export need to support both OpenCode and Claude in the
  MVP, or can Claude be deferred to a follow-up?
- **Asked by**: planning-lead
- **Asked on**: 2026-06-01
- **Answered by**: project-lead
- **Answer**: Both runtimes must ship in the MVP — Claude is the primary runtime
  for this team. OpenCode can be partial (agents only, no hooks) if needed.
- **Impact on plan**: Added cross-runtime parity task (T-048); moved Claude
  adapter from P2 to P0.
- **Resolution date**: 2026-06-01

---

## Template usage

1. Copy this file to `<feature-folder>/Clarifications/CLARIFICATION_LOG.md`.
2. Append one entry per question, following the format above.
3. Reference the log from SPEC.md's `## Clarifications` section with a link
   (e.g. `See full log: Clarifications/CLARIFICATION_LOG.md`).
4. Each session's questions get their own session header if multiple sessions
   are involved; keep newest session first.
