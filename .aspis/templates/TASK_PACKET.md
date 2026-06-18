# Build Packet: <feature-id> / T-NN — <Short Title>

A self-contained unit an executor can complete with no other context.

## Background
<2–4 sentences: what exists, what this unit changes, and why.>

## Objective
<One sentence: the exact change to make.>

## Allowed files (edit ONLY these)
- `<exact/path/one>`
- `<exact/path/two>`

## Forbidden
- Anything not listed under Allowed.
- Secrets: `.env`, keys, tokens, credentials.

## Steps
1. <Precise step with the exact file and what to change.>
2. <Precise step.>

## Inputs / examples
```text
<signatures, expected strings, sample input/output>
```

## Tests
- [ ] Tests are in the Allowed files above.
- [ ] Tests fail before implementation, pass after.
- [ ] Run: `<exact test command>` before reporting done.

## Done when
- [ ] <observable condition>.
- [ ] Only Allowed files changed.

## Verify
```bash
<exact gate commands: lint / format / types / tests>
```

## On failure
- Never weaken or delete tests to pass.
- If blocked, or the change needs a forbidden file, STOP and report what's needed.
