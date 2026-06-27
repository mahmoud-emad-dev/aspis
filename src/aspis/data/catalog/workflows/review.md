# Workflow: Review a change

The Reviewer's spine — the independent quality authority. Used per-task on escalation
from the Build Lead, and for the feature-level acceptance decision.

## When to use
A change, branch, or completed feature needs an independent quality verdict.

## Prerequisites
The diff/branch, the SPEC (acceptance criteria), and the active mode.

## Steps

1. **Strategy** — skill `review-strategy`. Set the depth from risk + mode. Choose
   which of the 9 review dimensions to evaluate and how deep:
   | # | Dimension     | Type      | Vibe  | MVP      | Production |
   |---|---------------|-----------|-------|----------|------------|
   | 1 | Correctness   | LLM+det   | Skip  | Standard | Full       |
   | 2 | Scope         | Det+LLM   | Light | Standard | Full       |
   | 3 | Architecture  | LLM+const | Skip  | Standard | Full       |
   | 4 | Maintainability | LLM     | Skip  | Light    | Standard   |
   | 5 | Reliability   | LLM+det   | Light | Standard | Full       |
   | 6 | Security      | Mixed     | Skip  | Standard | Full       |
   | 7 | Performance   | LLM       | Skip  | Light    | Standard   |
   | 8 | Standards     | Det       | Light | Standard | Full       |
   | 9 | Documentation | LLM       | Skip  | Light    | Standard   |
2. **Evaluate** — skill `quality-review`. Walk each in-scope dimension against the
   SPEC's `FR-###`/`SC-###` and the project rules. Stay read-only (no edit/write
   tools); cite every finding with `file:line` evidence. **Hard rule: no evidence,
   no verdict.** Every finding must point to a specific line or observable artifact.
   Format findings as: `file:line — what's wrong — why — severity — suggested fix
   — evidence`.
3. **Decide** — skill `acceptance-decision`. Apply the severity rubric:
   - **CRITICAL** (security vuln, data loss, R-008 violation) → single = REJECTED
   - **HIGH** (correctness bug, scope violation, broken gate) → single =
     CHANGES-REQUIRED
   - **MEDIUM** (edge case, doc gap) → blocking by default
   - **LOW** (style, typo) → never blocking
   
   Verdict:
   - **approved**: 0 CRITICAL, 0 HIGH, 0 unresolved MEDIUM-blocking; all SC-### met
   - **approved-with-notes**: 0 CRITICAL, 0 HIGH; ≥1 MEDIUM-non-blocking or LOW
   - **changes-required**: ≥1 HIGH or MEDIUM-blocking; approach is sound
   - **rejected**: ≥1 CRITICAL or approach fundamentally wrong
4. **Route** — approve → committer/done; changes-required → back to a builder (max 3
   rejections per task, then escalate to project-lead); rejected with a defect →
   **Fix Lead** (`fix.md`); rejected with a fundamental flaw → planning-lead or the
   R-008 human gate.

## Mode overlays
- **vibe** — one light pass: does it run, is it in scope, anything obviously broken.
  Not the full multi-dimension review.
- **mvp** — standard depth on the changed surface.
- **production** — full multi-lens review; every acceptance criterion checked.

## Outputs
A written verdict with reasons and routed follow-ups.
