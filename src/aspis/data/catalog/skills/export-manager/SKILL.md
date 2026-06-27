---
name: export-manager
description: Plan and apply a catalog-to-runtime export, handling the six DecisionKind outcomes (ADD/UNCHANGED/UNKNOWN/UPDATE/PROTECT/CONFLICT).
---

# export-manager

## Purpose
Govern the export pipeline — plan what will change, classify every live file by
DecisionKind (ADD, UNCHANGED, UNKNOWN, UPDATE, PROTECT, CONFLICT), and apply
the plan only when it is safe. The catalog is the single source of truth
(R-006); live runtime files must match it exactly. The export performs the
three-layer transform L1 (catalog) → L2 (live runtime) → L3 (prompt context),
gated by the content-hash protection engine (F-015).

## When to use
- Before every `aspis export`.
- When adding or removing agents, skills, or runtime assets.
- When the protection engine blocks a write and reports a PROTECT decision.
- During system repair, when live files have diverged from the catalog.

## Procedure
1. **Dry-run the plan** — run `aspis export --dry-run` to obtain the full plan:
   every file the export will touch, with its DecisionKind and hash.
2. **Triage CONFLICT** — for each CONFLICT, determine whether the live file was
   hand-edited (reconcile the edit back into the catalog) or whether the
   catalog itself changed. Never silently overwrite a hand-edit.
3. **Investigate UNKNOWN** — for each UNKNOWN (no snapshot entry), confirm
   provenance before letting export classify it; an untracked file is a
   CONFLICT candidate, not a blind ADD.
4. **Verify PROTECT approvals** — for each PROTECT decision, run
   `aspis governance check` and confirm R-008 human approval exists in the
   approval ledger for that path. Any unapproved PROTECT → STOP and route
   through the `governance-approval` skill.
5. **Set the gate** — only when every PROTECT has a valid, non-expired
   approval: set `ASPIS_ALLOW_PROTECTED=1`. The env var is a gate
   acknowledgment, not a permission grant.
6. **Apply** — run `aspis export` (without `--dry-run`) to execute the plan.
7. **Verify parity** — run `aspis byte-parity` and confirm every file is
   CLEAN. Any non-CLEAN result means the live runtime and the catalog are
   still divergent — do not declare the export done.

## Outputs
- Export plan: per-file DecisionKind with file paths and hashes.
- Approval verification summary: which PROTECT decisions passed
  `aspis governance check`.
- Post-export parity report from `aspis byte-parity` (expected: all CLEAN).

## Anti-patterns
- Setting `ASPIS_ALLOW_PROTECTED=1` to bypass PROTECT without a corresponding
  R-008 approval in the ledger.
- Ignoring CONFLICT decisions because "the export will fix it" — a CONFLICT
  means a hand-edit will be silently overwritten and lost.
- Running `aspis export` on a dirty working tree — uncommitted changes can
  mask CONFLICT or be clobbered by UPDATE; verify a clean tree first.
- Skipping the post-export `aspis byte-parity` check — export success is not
  proof of alignment; only a byte-parity pass is.
- Using `--force` (or any override) to write through PROTECT — there is no
  force path; the human gate is the only path.
