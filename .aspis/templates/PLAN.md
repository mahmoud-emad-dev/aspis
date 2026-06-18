# <feature-id> — Implementation Plan

## Approach
<The strategy in a few sentences, referencing the SPEC slices it delivers.>

## Technical context
- **Language / version**: <e.g. Python 3.11 — or N/A>
- **Key dependencies**: <or N/A>
- **Storage / interfaces**: <or N/A>
- **Where new files live**: <structure decision and why>

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

## Decisions needing approval
- <Load-bearing architecture decision a human must sign off — remove if none.>
