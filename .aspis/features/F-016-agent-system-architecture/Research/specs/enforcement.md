# Enforcement Mode — Specification

> F-016 systemic spec. Defines enforcement boundaries, modes, and the warn→block transition.

## Purpose
Define how ASPIS enforces its rules at runtime: which violations are blocked vs warned, how enforcement is configured, and the transition path from the current warn-only state.

## Enforcement boundaries

### Runtime enforcement (Edit / Write tools)
**Target: block**
- Every Edit and Write call is intercepted at the tool boundary
- The agent's permission surface (frontmatter) is checked
- If the path is denied → BLOCK with message: "Path <path> is denied for agent <agent>. See permissions in <agent>.md frontmatter."
- If the path is allowed → ALLOW
- Enforcement is in the tool wrapper, not in the agent prompt

### Pre-commit hook enforcement
**Target: warn**
- Pre-commit hooks run before every commit
- They check: scope (allowed files), secrets, protected paths, frontmatter validity
- On violation → WARN with message and file:line evidence
- Warnings do not block the commit (unless `ASPIS_ENFORCEMENT=block` is set)
- Hook output is surfaced to the committer, who may refuse (committer discretion)

### CI enforcement
**Target: block (override)**
- In CI, `ASPIS_ENFORCEMENT=block` is set
- All pre-commit warnings become blocking errors
- A CI run with enforcement violations fails the pipeline
- This is the same hooks, same code — just with the enforcement flag

## Enforcement modes

| Mode | Runtime (Edit/Write) | Pre-commit hooks | CI |
|---|---|---|---|
| warn | Allow with warning | Warn | Warn |
| block | Block | Warn | Block |
| strict | Block | Block | Block |

Current state: warn (all boundaries).
Target state: block (runtime block, pre-commit warn, CI block).

## Transition plan
1. **Phase 1 (now)**: Document target enforcement in this spec. Keep warn as default.
2. **Phase 2 (F-016 follow-up)**: Implement runtime block for Edit/Write tools. Default remains warn; `ASPIS_ENFORCEMENT=block` opt-in.
3. **Phase 3 (future)**: Flip default to block after a probation period (e.g., 2 weeks with no false-positive reports).
4. **Phase 4 (future)**: strict mode for high-security profiles.

## CI override
```
ASPIS_ENFORCEMENT=block
```
- Set in CI pipeline configuration
- Overrides the default warn mode
- Makes pre-commit violations block the pipeline
- Does NOT affect runtime enforcement (which is always block in Phase 2+)

## Auto-fix behavior
- In `warn` mode: violations are reported; no auto-fix
- In `block` mode: violations are reported; no auto-fix (human must resolve)
- Auto-fix is a separate feature — governance subagent handles protected-path fixes after R-008 approval

## Acceptance criteria
- [ ] All 3 enforcement boundaries defined (runtime, pre-commit, CI)
- [ ] Enforcement modes table complete (warn/block/strict)
- [ ] Transition plan has clear phases with criteria
- [ ] CI override env var specified
- [ ] Auto-fix behavior documented (none in current design)
- [ ] Consistent with D-010 (hooks non-blocking by default)
- [ ] This spec is the flip side of D-010 — documents the TARGET state
