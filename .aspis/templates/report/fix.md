# Fix report — <feature-id> / <fix-id>

> Filled by the fix-lead after the root cause is corrected and the gate is
> green. The header fields are stamped by `aspis artifact`; you fill the rest
> from real results — never invent a format, and never report green without the
> gate output.

- **Feature / area**: <feature-id or affected area>
- **Fix**: <fix-id>
- **Date**: <date>
- **Status**: <fixed | escalated (REVIEW_NEEDED)>

## Symptom
<What was observed failing — the report, error, or regression as it presented.>

## Reproduction
<The minimal steps/test that reproduce the failure red, before the fix.>

## Root cause
<The true cause, not the symptom — why the code behaved this way.>

## The fix
<The smallest safe change that corrects the root cause, and the files touched.>

## Verification (red → green)
<The test that failed first and now passes, plus the regression check that
proves nothing adjacent broke. Gate output (ruff + pytest) pasted, not summarised.>

## Notes / hand-off
<Attempt count if escalated, follow-ups, or decisions the reviewer needs.>
