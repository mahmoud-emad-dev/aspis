---
name: lead-routing
description: Use to select the single specialist lead that owns a classified request, with the reason and a suggested workflow — and to keep routing within the model (no worker calls, no lead-to-lead chains).
---

# Lead Routing

## Purpose

Send each request to the one lead that owns it, so work is done by its rightful
specialist and the project stays coordinated.

## When to use

After `request-classification`, when the request needs delegation rather than a
direct answer.

## Procedure

1. Map the request type to its owning lead:
   - planning / spec / clarify → `planning-lead`
   - build / implement → `build-lead`
   - review / quality / acceptance → `reviewer`
   - fix / regression / gate failure → `fix-lead`
   - tests / coverage → `test-lead`
   - research / docs / feasibility → `research-lead`
   - runtime / agents / skills / rules / templates → `system-lead`
2. For `mixed` work, route to the lead that owns the **first** step and note the
   likely next leads — do not pre-commit the whole chain.
3. Escalate to human approval for architecture, security, or model-routing changes.

## Outputs

- Target lead
- Routing reason (one line)
- Suggested workflow (the likely sequence, not a fixed script)

## Anti-patterns

- Routing to a worker directly, or chaining lead → lead → lead — each lead fans
  out to its own workers.
- Sending a system/runtime/rules change anywhere but `system-lead`.
- Forcing a fixed sequence when the request only needs one lead.
