# Missing CLI Verbs — Specification

> F-016 systemic spec. Defines 6 missing CLI verbs for the `aspis` command.

## Purpose
Specify the interface, priority, and expected output for 6 CLI verbs referenced by agent specs that are not yet implemented.

## Verb: validate-runtime

### Purpose
Structural frontmatter validation for all rendered agent files. Checks that every rendered agent file (in `.opencode/agents/` and `.claude/agents/`) has all required frontmatter fields matching the catalog source.

### Priority: P0

### Interface
```
aspis validate-runtime [--runtime opencode|claude|all] [--check <field>]
```

### Expected output
- Exit 0: all rendered files pass
- Exit 1: one or more files fail
- Output: per-file pass/fail with missing/invalid fields listed
- `--check delegates` validates only the delegates field
- `--check permissions` validates only permissions

### Agent that calls it
- system-lead (system validation)
- reviewer (pre-review gate)
- build-lead (pre-build gate)

## Verb: validate-index

### Purpose
Registry consistency check. Validates that `.aspis/index/FILE_REGISTRY.yaml` accurately reflects the current tree — no missing files, no stale entries, no path mismatches.

### Priority: P1

### Interface
```
aspis validate-index [--fix]
```

### Expected output
- Exit 0: registry matches tree
- Exit 1: discrepancies found
- Output: list of discrepancies with file:expected vs registry:actual
- `--fix` regenerates the registry to match the tree

### Agent that calls it
- system-lead (system health)
- project-explorer (before trusting the index)

## Verb: byte-parity

### Purpose
Cross-runtime byte-parity check. Proves that the catalog regenerates live runtime files byte-for-byte — no drift, no adapter corruption.

### Priority: P0

### Interface
```
aspis byte-parity [--runtime opencode|claude] [--agent <name>]
```

### Expected output
- Exit 0: all rendered files match catalog source byte-for-byte
- Exit 1: drift detected
- Output: per-file diff (what changed between catalog render and live file)
- `--agent <name>` checks only one agent
- Handles CONFLICT/PROTECT decisions from F-015 protection engine

### Agent that calls it
- system-lead (system health, cross-runtime parity)
- reviewer (pre-acceptance gate)

## Verb: drift

### Purpose
Frontmatter field drift detection. Compares catalog frontmatter fields against rendered runtime files and reports any field that has drifted.

### Priority: P1

### Interface
```
aspis drift [--field <name>] [--runtime opencode|claude]
```

### Expected output
- Exit 0: no drift
- Exit 1: drift found
- Output: per-field per-agent drift report with catalog-value vs runtime-value
- `--field model` checks only model field drift
- `--field delegates` checks only delegates field drift

### Agent that calls it
- system-lead (system repair — detect and flag drift)
- fix-lead (before diagnosing a runtime issue)

## Verb: export

### Purpose
Catalog-to-runtime export with protection engine. Renders catalog agent files to runtime-specific agent files, applying the protection engine (scope boundaries, permission enforcement).

### Priority: P0

### Interface
```
aspis export [--runtime opencode|claude|all] [--agent <name>] [--dry-run] [--check]
```

### Expected output
- Exit 0: export successful
- Exit 1: export failed (protection engine blocked, or rendering error)
- `--dry-run` shows what WOULD be written without writing
- `--check` validates rendered output without writing (same as dry-run but exit 1 on changes)
- Protection engine applies: scope boundaries, permission enforcement, forbidden-path removal

### Agent that calls it
- system-lead (asset authoring — primary caller)
- build-lead (after catalog updates — re-render agents)

## Verb: governance

### Purpose
R-008 human approval workflow. The CLI interface for the governance subagent — request, approve, audit, revoke protected-path changes.

### Priority: P1

### Interface
```
aspis governance <subcommand> [options]
  request  --path <path> [--reason <reason>]
  approve  --id <request-id> --scope <paths>
  audit    [--since <date>] [--path <path>]
  revoke   --id <approval-id>
  check    --path <path>
  ledger   [--format yaml|json]
```

### Expected output
- `request`: prints request ID and instructions for human approval
- `approve`: records approval in ledger, prints confirmation
- `audit`: prints matching approval records
- `revoke`: marks approval as revoked, prints confirmation
- `check`: prints "ALLOWED" or "BLOCKED: <reason>" for the given path
- `ledger`: prints full approval ledger

### Agent that calls it
- governance subagent (primary)
- system-lead (system repair — request rule changes)
- project-lead (project governance — request scope changes)

## Priority summary

| Verb | Priority | Category |
|---|---|---|
| validate-runtime | P0 | Validation gate |
| byte-parity | P0 | Cross-runtime parity |
| export | P0 | Asset authoring |
| governance | P1 | Human approval (R-008) |
| validate-index | P1 | System health |
| drift | P1 | System health |

## Acceptance criteria
- [ ] All 6 verbs specified with: purpose, priority, interface signature, expected output
- [ ] Every verb has at least one agent that calls it
- [ ] Exit codes are specified (0 = success, non-zero = failure/meaning)
- [ ] P0 verbs are the ones needed for the core loop to validate
- [ ] P1 verbs are operational enhancements
- [ ] Consistent with system-lead reference spec §System Health and §Validation
- [ ] Interface signatures are consistent with existing `aspis` CLI style
