---
name: governance-approval
description: The R-008 human-gate workflow for rules, permissions, model-routing, and security posture changes — never an automated rewrite.
---

# governance-approval

## Purpose
Enforce R-008 (human gate) for all changes to rules, permissions, model routing,
and security posture. This skill describes the *workflow* the system-lead follows
when a change requires human approval — it does not implement the mechanism (that
is the `governance` CLI verb and subagent, built separately).

## When to use
- Before any change to `rules/**` or `.aspis/rules/**`.
- Before any change to `**/permissions*.yaml` or `.claude/settings.json`.
- Before any change to `.opencode/agents/**` or `.claude/agents/**`.
- Before any change to model routing (tier escalation, model pinning, global
  tier defaults).
- Before any change to the security posture (protection engine config,
  capability grants).
- When the 3-attempt cap is hit and a REVIEW_NEEDED requires human judgment.

## Procedure
1. **Detect R-008 territory** — before making any system change, check whether
   the change touches an R-008-gated path or category:
   - **Rules**: `rules/**`, `.aspis/rules/**`
   - **Permissions**: `**/permissions*.yaml`, `.claude/settings.json`
   - **Runtime agents**: `.opencode/agents/**`, `.claude/agents/**`
   - **Model routing**: any change crossing tier boundaries or modifying global
     tier defaults
   - **Security posture**: protection engine config, capability grants
   - **Self-modification**: any change to the system-lead's own agent file or
     the committer's permissions
2. **If R-008 territory → STOP.** Do not proceed with the change. Instead:
   - Run `aspis governance request --paths <paths> --reason "<why this change is needed>"`
     to record the intent in the approval ledger.
   - Report to the project-lead (or directly to the human owner) that R-008
     approval is required, citing the specific paths and the reason.
   - **Wait.** Do not make the change until the human runs `aspis governance
     approve <request-id> --approver <name>`.
3. **If approved** — the approval ledger has an active, non-expired, non-revoked
   entry for the paths. Proceed with the change under the approval's scope.
4. **If denied or expired** — the change is blocked. Do not work around the gate.
   Do not use `--force`. Do not use an env-var override. There is no bypass.
5. **Post-change** — after the change is committed, the approval remains in the
   ledger as an audit record. No cleanup needed.

## Outputs
- A governance request recorded in `.aspis/state/approval-ledger.yaml` (via the
  `aspis governance request` command).
- A clear report to the delegating lead or human owner: what needs approval, why,
  and the request ID to use for the `approve` command.

## Anti-patterns
- Proceeding without checking R-008 territory — "I'll ask for forgiveness later"
  is not how R-008 works. The governance subagent blocks the write; there is no
  forgiveness path.
- Treating R-008 as optional because "this is an emergency" — emergency changes
  still follow the gate. The human can approve quickly, but the gate is never
  skipped.
- Using a broad glob-approval (`--glob-approval`) for convenience — pattern-level
  approval is a dangerous extension that requires explicit confirmation.
- Writing the change before approval and asking for retroactive sign-off — the
  approval must exist before the write, not after.
