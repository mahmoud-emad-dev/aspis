# F-020 — Architecture Impact Report

> Recorded by planning: F-020 changes subsystem intent. **NOT auto-applied** — project-lead
> confirms with the owner before any subsystem file under `.aspis/architecture/subsystems/` is
> updated. (Dogfoods the F-019 architecture-memory loop.)

## Affected subsystem(s)
- **initialization** — EXISTING (extended)
- **bootstrapping** — EXISTING (extended; behavior tightened)
- **setup-workflow** — NEW (the orchestration layer that was held in F-019)
- **rules** — EXISTING/touched (bootstrap reads layers + seeds project rules)
- **models-intelligence** — seam only (consumed/reserved; not changed — F-021 owns it)

## Reason
The init→bootstrap path works mechanically but is opaque and brittle for a normal user, and it can
leave a project half-enriched on a weak/offline/failed agent. F-020 makes first-run **one guided
command** with clear hints, a read-only **pre-bootstrap resolution layer**, a bootstrap agent that
**asks rather than decides**, and a **deterministic post-bootstrap self-heal** floor.

## Summary of the architectural change
- **Current:** init = deterministic shell; bootstrap = wizard that fills slots + manifest + brain
  fill + 5 primaries + self-erase; project-lead delegates to the bootstrap agent. No formal
  pre-bootstrap layer; one-shot brittle stack; no post-heal floor; thin hints.
- **Proposed:** add a **pre-bootstrap resolution stage** (read-only: runtime/subscription/state/
  stack-confidence + rule layers → `bootstrap_state.json`); a **setup-workflow** orchestrator
  (init → onboarding → bootstrap → post-heal, resumable/skippable); **clear onboarding** with
  meaning+example per question (mode/goal/description/stack); **plan-file detect+read**; bootstrap
  agent **must confirm stack+mode with the user** (never self-decide) and may use research-lead; a
  **deterministic post-bootstrap self-heal** that guarantees the brain floor via scripts.
- **Fixed vs changed:** ALL FIXED invariants in `initialization.md` and `bootstrapping.md` are
  **preserved** (offline/deterministic init; init owns its commit; non-blocking defaults;
  delegate-not-self-run; self-erase never edits catalog bodies; enrich-from-facts-only; 5 primaries;
  zero residue). **Changed/added:** the new pre-bootstrap stage + state file; the setup-workflow
  orchestration; confidence-driven correctable stack; the deterministic post-heal floor; richer
  onboarding hints; plan-file awareness; runtime continuation + multi-runtime guidance.
- **Reconciliation note:** "post-bootstrap self-heal" does NOT violate bootstrapping FIXED #6
  ("no autonomous writes"), because it is a **deterministic restore of expected files** (the IB-4
  definition), never agent-invented content.

## Integration impact
- **models-intelligence (F-021):** pre-bootstrap produces the runtime/subscription/availability
  inventory the future model-decision engine consumes; F-020 reserves that seam and changes **no**
  model files (frozen).
- **rules subsystem:** bootstrap reads system/project/user layers and seeds project rules; later
  changes route through governance (R-008).
- **catalog-to-runtime:** new pre/post stages register on the lifecycle engine; the bootstrap gate
  + delegate continue to strip on go-live (no catalog-body edits).
- **git (F-022):** two-commit staging (init commit, bootstrap commit) is touched lightly here and
  fully owned by F-022.

## Questions needing user confirmation
1. Create the **`setup-workflow`** subsystem file now (the orchestration layer), and **extend**
   `initialization.md` + `bootstrapping.md` with the F-020 direction once you approve this SPEC?
2. Confirm the **state file** name/location: `.aspis/current/bootstrap_state.json`?
3. Confirm the **plan-file** location and the **user-rules** path (the two open questions in the SPEC).
4. Confirm F-020 mode = **production**, and the in/out scope (model engine = F-021, git = F-022)?
5. Confirm the **post-heal = deterministic-restore-only** reconciliation (no agent invention) is the intended model?
