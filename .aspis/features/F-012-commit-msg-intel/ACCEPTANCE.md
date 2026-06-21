# Acceptance — F-012

> The boolean closure gate for the feature: every box must be checked before the
> feature is accepted. Resolve a failing box by fixing the work, never by deleting
> the check.

- **Feature**: F-012 — Commit-message intelligence
- **Date**: 2026-06-21

## Requirements (from SPEC)
- [ ] FR-001 — the commit-msg hook removes forbidden attribution and lets the commit proceed (exit 0).
- [ ] FR-002 — the hook reports each auto-fix it applied on stderr.
- [ ] FR-003 — a clean message is byte-unchanged; `.claude`/`.opencode` domain mentions are preserved.
- [ ] FR-004 — auto-fix is data-driven from the convention / `hooks.yaml` (no inline rules).
- [ ] FR-005 — a project can disable any auto-fix and exempt one commit via the `Commit-Style: skip` token; exemptions are logged.
- [ ] FR-006 — a history audit lists every violating commit with its violations and a totals summary, read-only.
- [ ] FR-007 — a history fix is human-invoked, creates a backup ref, and leaves commit content byte-identical.
- [ ] FR-009 — behaviour is identical on Windows and Linux (UTF-8 message I/O).
- [ ] FR-008 — *deferred to F-013 (learnable style); not gated here.*

## Success criteria (from SPEC)
- [ ] SC-001 — the 2026-06-21 attribution class of defect cannot reach a commit silently; it is auto-removed with a visible notice and no extra developer step.
- [ ] SC-002 — `aspis commits --audit` gives a one-command pass/fail audit of the whole history.
- [ ] SC-003 — auto-fix behaviour and a commit exemption are changeable purely by editing config.
- [ ] SC-004 — the deterministic gate (ruff + pytest) stays green on both OSes, with new behaviour covered by red→green tests.

## Gates
- [ ] Deterministic gate green (ruff + pytest) on Windows and Linux
- [ ] Changes stayed inside the feature's scope (hook, its config, the `commits` verb, the doctor check, tests)
- [ ] No secrets, no junk files committed
- [ ] Shipped `.aspis/scripts/hooks/commitmsg.py` == catalog (export parity)

## Sign-off
- **Verdict**: not-yet (planning complete; build pending)
- **Notes**: Story 4 (learnable style) deferred to F-013. `aspis commits --fix` history rewrite is human-invoked only.
