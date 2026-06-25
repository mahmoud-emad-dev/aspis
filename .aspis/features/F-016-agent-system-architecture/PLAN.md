# F-016 — Implementation Plan

> Mode hints: **vibe** → skip this file. **mvp** → Summary + Technical context +
> Steps, a light note. **production** → the whole template.

## Summary
<The approach in a few sentences: the primary requirement from the SPEC and how it
will be built.>

## Technical context
- **Language / version**: <e.g. Python 3.11 — or N/A>
- **Key dependencies**: <or N/A>
- **Storage / interfaces**: <or N/A>
- **Testing**: <e.g. pytest — or N/A>
- **Project type / structure**: <where new files live and why>
- **Constraints**: <performance, compatibility, scale — or N/A>

## Gate check
The plan must clear the project's rules before any build (remove rows that don't
apply; justify any exception in Complexity below).
- [ ] **R-001 Scope** — changes stay within the SPEC's in-scope paths.
- [ ] **R-002 Gates** — the deterministic gate (format/lint/types/tests) is the bar.
- [ ] **R-005 Tests-as-spec** — behaviour is pinned by tests, not prose.
- [ ] **R-009 Human gate** — rules/architecture/security changes are flagged below.

## Components
<Components, data flow, interfaces, and integration points.>

## Steps
| Step | Files | Gate |
|------|-------|------|
| 1. <step> | `<path>` | `<deterministic check>` |
| 2. <step> | `<path>` | `<deterministic check>` |

## Verification
Run before declaring done:
```bash
<lint / format / types / tests / scope check>
```

## Risks & rollback
- **Risk**: <risk> → <mitigation>.
- **Rollback**: <how to undo this feature if it fails>.

## Complexity tracking
Fill ONLY if a gate-check row is violated and the complexity is justified.

| Violation | Why needed | Simpler alternative rejected because |
|-----------|-----------|--------------------------------------|
| <what> | <why> | <why not the simpler way> |

## Decisions needing approval
- <Load-bearing architecture decision a human must sign off (R-009) — remove if none.>
