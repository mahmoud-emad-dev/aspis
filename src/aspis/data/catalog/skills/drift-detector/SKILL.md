---
name: drift-detector
description: Detect per-field per-agent catalog-to-live frontmatter drift and report with file:line evidence.
---

# drift-detector

## Purpose
Detect when a live runtime agent's frontmatter (in `.opencode/agents/` or
`.claude/agents/`) differs from its catalog source (`catalog/agents/`). Drift
means the live runtime is out of sync with the single source of truth — a
correctness and security risk, since the catalog may declare least-privilege
permissions that the live runtime doesn't enforce (or vice versa).

## When to use
- At step 6 of the system-lead's post-change validation sequence (`aspis drift`).
- Before any `aspis export` to confirm catalog→live alignment.
- After any manual edit to a live runtime file (which should never happen, but
  drift detection catches it when it does).
- As a periodic health check on the runtime.

## Procedure
1. **Render the expected runtime** from the catalog agent using the same
   rendering pipeline that `aspis export` uses (the `plan_export`/`write_export`
   pipeline). Do NOT reimplement rendering — call the existing pipeline.
2. **Read the live runtime** from `.opencode/agents/<name>.md` (or the Claude
   equivalent at `.claude/agents/<name>.md`).
3. **Compare field by field:**
   - For each frontmatter field (name, description, mode, model, temperature,
     tools, permissions, delegates, skills, runtimes, export_scope), compare
     the catalog-rendered value with the live value.
   - For list fields (tools, delegates, skills), compare as sets — order doesn't
     matter, but presence does.
4. **Classify each difference:**
   - **DRIFT**: the live value differs from the catalog. The live runtime is
     stale and needs re-export.
   - **PROTECT**: the live runtime has a field the catalog doesn't produce (e.g.
     a custom permission the owner added manually). This may be intentional
     owner customization — report, don't overwrite.
   - **CLEAN**: the fields match exactly.
5. **Emit the report** — per-agent, per-field status (CLEAN / DRIFT / PROTECT)
   with the specific differing values. Exit 0 when no DRIFT is found; exit 1
   when any agent has DRIFT.

## Outputs
- A drift report: per-agent, per-field status with specific differences.
- Exit code 0 (no drift) or 1 (drift detected).
- The report is informational — it does not auto-correct drift. The owner runs
  `aspis export` to reconcile.

## Anti-patterns
- Comparing fields that aren't supposed to match — the Claude adapter translates
  fields (e.g. `tools:` list format differs between OpenCode and Claude). Drift
  detection must compare the *adapter-translated* expected output against the
  live runtime, not the raw catalog.
- Auto-fixing drift by overwriting the live runtime — the owner may have
  intentional customizations. Report the drift; let the owner decide.
- Skipping drift detection because "I just exported" — export can fail silently
  or the owner might have edited the live runtime afterward. Always check.
