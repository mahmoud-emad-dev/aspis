# Acceptance — <feature-id>

> The boolean closure gate for the feature: every box must be checked before the
> feature is accepted. Derive the FR/SC rows from SPEC.md. The header is stamped
> by `aspis artifact`; resolve a failing box by fixing the work, never by deleting
> the check.

- **Feature**: <feature-id> — <Feature Title>
- **Date**: <date>

## Requirements (from SPEC)
- [ ] <FR-001 — restate the requirement and confirm it is met>

## Success criteria (from SPEC)
- [ ] <SC-001 — the measurable outcome, confirmed>

## Gates
- [ ] Deterministic gate green (ruff + pytest) on every supported OS
- [ ] Changes stayed inside the feature's scope
- [ ] No secrets, no junk files committed

## Sign-off
- **Verdict**: <accepted | not-yet>
- **Notes**: <anything the reviewer flagged.>
