---
name: recontextualization
description: Translate a lead agent's return into project-aware language and decide the next action.
---

# recontextualization

## Purpose
When a lead agent returns to the project-lead with a result, question, or blocker,
translate its domain-specific output into project-level context and decide what
happens next — so the project-lead stays the single orchestrator without needing
deep domain knowledge of every lead's internals.

## When to use
- After any lead agent (planning-lead, build-lead, reviewer, fix-lead, test-lead,
  system-lead, research-lead) returns a result to the project-lead.
- When the project-lead receives a REVIEW_NEEDED or FIX_REPORT escalation.
- When a lead reports a blocker it cannot resolve in scope.

## Procedure
1. **Read** — ingest the lead's return payload (status, artifacts, verdict,
   findings, blockers). Don't re-analyze the work; trust the lead's expertise.
2. **Fold** — map the lead's domain-specific terms into project-level concepts:
   - `changes-required` from reviewer → "build not yet acceptable"
   - `cannot-reproduce` from fix-lead → "need more environment info"
   - `3-attempt cap hit` → "escalation needed"
   - `REVIEW_NEEDED` → "decision needed from project-lead"
3. **Translate** — extract the action the project-lead must take:
   - Approve and advance → hand to the next lead in the loop
   - Request revision → route back to the same lead with specific feedback
   - Escalate → flag for human review (R-008) or defer to system-lead
   - Pause → the feature is blocked; document why, set state
4. **Decide** — apply the project's prioritization and the mode's rigor to choose
   the next step. Production mode → full follow-through; vibe mode → accept
   reasonable risk.

## Outputs
- A project-level decision: advance, revise, escalate, or pause.
- Updated feature state if the decision changes the active phase.
- A brief recontextualized summary for the owner or for continuation in the next
  session.

## Anti-patterns
- Re-doing the lead's analysis — trust the specialist's output; your job is
  routing and prioritization, not re-validation.
- Ignoring a lead's escalation — if a lead says "blocked," treat it as a real
  block until resolved.
- Translating without reading — skim the lead's return at minimum before deciding.
- Making every decision yourself — escalate genuinely blocking or risky decisions
  to the human owner (R-008).
