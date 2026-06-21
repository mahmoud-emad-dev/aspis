# Acceptance — F-012

> The boolean closure gate for the feature: every box must be checked before the
> feature is accepted. Resolve a failing box by fixing the work, never by deleting
> the check.

- **Feature**: F-012 — Commit-message intelligence
- **Date**: 2026-06-21

## Requirements (from SPEC)
- [x] FR-001 — the commit-msg hook removes forbidden attribution and lets the commit proceed (exit 0).
- [x] FR-002 — the hook reports each auto-fix it applied on stderr.
- [x] FR-003 — a clean message is byte-unchanged; `.claude`/`.opencode` domain mentions are preserved.
- [x] FR-004 — auto-fix is data-driven from the convention / `hooks.yaml` (no inline rules).
- [x] FR-005 — a project can disable any auto-fix and exempt one commit via the `Commit-Style: skip` token; exemptions are logged.
- [x] FR-006 — a history audit lists every violating commit with its violations and a totals summary, read-only.
- [x] FR-007 — a history fix is human-invoked, creates a backup ref, and leaves commit content byte-identical.
- [x] FR-009 — behaviour is identical on Windows and Linux (UTF-8 message I/O).
- [x] FR-008 — *deferred to F-013 (learnable style); not gated here.*

## Success criteria (from SPEC)
- [x] SC-001 — the 2026-06-21 attribution class of defect cannot reach a commit silently; it is auto-removed with a visible notice and no extra developer step.
- [x] SC-002 — `aspis commits --audit` gives a one-command pass/fail audit of the whole history.
- [x] SC-003 — auto-fix behaviour and a commit exemption are changeable purely by editing config.
- [x] SC-004 — the deterministic gate (ruff + pytest) stays green on both OSes, with new behaviour covered by red→green tests.

## Gates
- [x] Deterministic gate green (ruff + pytest) on Windows and Linux
- [x] Changes stayed inside the feature's scope (hook, its config, the `commits` verb, the doctor check, tests)
- [x] No secrets, no junk files committed
- [x] Shipped `.aspis/scripts/hooks/commitmsg.py` == catalog (export parity)

## Sign-off
- **Verdict**: accepted (build complete; gate green, 231 tests; auto-fix dogfooded live)
- **Notes**: Story 4 (learnable style) deferred to F-013. `aspis commits --fix` history
  rewrite is human-invoked only. The escape hatch is an exact-line `Commit-Style: skip`
  marker (a prose mention does not trigger it). Audit surfaced 23 pre-existing
  over-length subjects in old history (advisory; not auto-fixable).
