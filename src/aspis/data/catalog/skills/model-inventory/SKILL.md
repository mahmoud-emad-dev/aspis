---
name: model-inventory
description: Cross-reference `model_catalog.yaml` against live provider offerings via `aspis models --available`, surfacing STALE / MISSING / IN-USE-STALE model entries to keep model routing accurate.
---

# model-inventory

## Purpose

Model providers (OpenAI, Anthropic, etc.) add and deprecate models continuously.
`model_catalog.yaml` is ASPIS's canonical inventory (Tier 3 reference data,
D-016), but it can drift from what providers actually offer. This skill detects
that drift — surfacing catalog entries for models that no longer exist, and
models the provider exposes that are not yet catalogued. Keeps model routing
honest.

## When to use

- During system health checks (alongside `drift-detector`).
- Before any model-routing change — R-008 territory.
- When an agent reports "model not found" or "model not supported" errors.
- As periodic maintenance — providers deprecate models monthly.

## Procedure

1. **Query live provider offerings** with `aspis models --available`. Reads
   `providers.yaml`, hits each provider's models endpoint when API keys are
   configured, and emits the union of currently offered model ids.
2. **Read the canonical inventory** — `model_catalog.yaml`. Every entry has
   a canonical id, provider, and adapter mapping.
3. **Cross-reference catalog → provider.** For each catalog entry, verify the
   model still appears in the provider's current list. Flag any miss as STALE.
4. **Cross-reference provider → catalog.** For each model the provider offers
   that is absent from the catalog, flag as MISSING (candidates for addition).
5. **Identify IN-USE-STALE.** For each STALE entry, search agent model
   routing (`agent-models.yaml`, per-agent pins, `models.yaml` defaults).
   If any active agent references a STALE canonical id, escalate its status
   to IN-USE-STALE — these will fail at runtime and are blocking.
6. **Emit the report.** Per-model status with the affected agents (if any)
   and an overall verdict: FRESH (no findings) or STALE (any STALE /
   IN-USE-STALE).

## Outputs

- Per-model status: STALE (in catalog, not available), MISSING (available, not
  catalogued), IN-USE-STALE (referenced by an active agent but unavailable).
- List of agents affected by each IN-USE-STALE entry.
- Overall health: FRESH or STALE.
- Findings only — does not edit `model_catalog.yaml`. The owner resolves
  drift via `aspis models --sync` (preview) then `--apply` (write).

## Anti-patterns

- **Trusting the catalog blindly.** Providers deprecate without notice; the
  catalog is reference data, not truth. Always re-verify with `--available`.
- **Hand-editing `model_catalog.yaml`.** Use `aspis models --sync --apply` so
  additions, retirements, and the audit trail stay consistent.
- **Ignoring IN-USE-STALE.** A STALE entry nobody references is a cleanup
  task; a STALE entry an active agent depends on is a runtime failure waiting
  to happen. Triage them separately.
- **Running the check once.** Providers ship new models and deprecations every
  month — the inventory is a moving target, not a one-time audit. Schedule it.
