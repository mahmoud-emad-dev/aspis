# Task Packet: <feature-id> / T-NN — <Short Title>

A self-contained unit a context-isolated builder can complete with nothing else.
The Build Lead enriches every `<...>` from its whole-feature context before
delegating. Fields the mode doesn't need may be marked `N/A` — never left blank.

## Identity
- **Feature**: <feature-id> — <feature title>
- **Task**: T-NN
- **Type**: <setup | test | model | service | endpoint | wiring | docs | fix>
- **Criticality**: <low | medium | high>
- **Mode / model tier**: <vibe|mvp|production> / <cheap|standard|deep>

## Context
<2–4 sentences: what exists now, what this task changes, and why.>

**Read first** (only what this task needs — from FILE_REGISTRY / CODE_MAP):
- `<path>` — <why it matters to this task>.

## Scope
Allowed files (edit ONLY these):
- `<exact/path/one>`
- `<exact/path/two>`

Forbidden:
- Anything not listed under Allowed.
- Secrets: `.env`, keys, tokens, credentials.

## Steps
1. <Precise step naming the exact file and the change.>
2. <Precise step.>

## Skeleton / pseudo-code
The shape to fill in — signatures, control flow, key data structures — so the
builder completes it rather than inventing it.
```text
<function/class signatures, the algorithm in pseudo-code, expected I/O>
```

## Dependencies & integration
- **Depends on**: <T-NN … or none> — what this consumes from them.
- **Feeds**: <T-NN … or none> — what downstream tasks take from this.

## Outputs
- <The observable artifact(s) this task produces.>

## Acceptance
Measurable done-conditions, traced to the SPEC where possible.
- [ ] <observable condition> (SPEC FR-### / SC-###).
- [ ] Only Allowed files changed.

## Tests
- [ ] <what to test — or "none: gate only" when the mode/type doesn't warrant one>.
- [ ] Tests live in the Allowed files; fail before, pass after.
- [ ] Run: `<exact test command>` before reporting done.

## Review routing
- **Needs review**: <yes | no — per criticality and the mode's build_review knob>.
- **Reviewer**: <sub-agent (default, per-task) | Reviewer lead (high criticality,
  cross-cutting, or security)>.

## Verify
```bash
<exact gate commands: format / lint / types / tests>
```

## On failure
- Never weaken or delete tests to pass.
- If blocked, or the change needs a forbidden file, STOP and report what's needed.
