# Cross-Runtime Parity — Specification

> F-016 systemic spec. Defines cross-runtime parity requirements for agent file rendering.

## Purpose
Ensure that the catalog-as-single-source-of-truth produces byte-identical (or capability-equivalent) agent files across all supported runtimes. Define the byte-parity check, the Claude Code adapter fix, and the CONFLICT/PROTECT decision model.

## Supported runtimes

1. **OpenCode** — native runtime. Renders to `.opencode/agents/<agent>.md`. Full frontmatter support including `permission:` block.
2. **Claude Code** — adapter runtime. Renders to `.claude/agents/<agent>.md`. **Known bug**: `permission:` block is stripped during rendering.

## Byte-parity requirement
Every catalog agent file, when rendered for a runtime, MUST produce a file that is byte-identical to what would be produced by rendering the same catalog file for any other capability-equivalent runtime.

### Capability-equivalence
- OpenCode and Claude Code are capability-equivalent for: name, description, model, tools, delegates, skills
- They differ in: `permission:` block format (OpenCode supports structured permissions; Claude currently strips them)
- Where a runtime lacks a capability, the rendered file MUST document the gap explicitly rather than silently dropping content

## Claude Code adapter fix
The Claude Code adapter currently strips the `permission:` block. The fix:

### Target state
The adapter MUST preserve the `permission:` block in rendered agent files, translating it to Claude Code's equivalent format if different, or embedding it as a structured comment if Claude Code has no native permission format.

### Acceptance criteria for the fix
- [ ] `permission:` block appears in every Claude-rendered agent file
- [ ] Permission semantics are preserved (deny stays deny, allow stays allow)
- [ ] Claude Code agents have the same effective permission surface as OpenCode agents
- [ ] Backward-compatible: existing Claude Code setups continue to work
- [ ] Verified by `aspis byte-parity --runtime claude --agent all` returning exit 0 after fix

## Byte-parity check: `aspis byte-parity`
See the CLI verbs spec for the full interface. Key requirements:
- Renders catalog → runtime files
- Compares rendered output to live files byte-for-byte
- Reports per-file diffs
- Exit 0 = parity; exit 1 = drift

## CONFLICT / PROTECT decision handling
From F-015 protection engine: when a catalog agent file is modified and the live runtime file has uncommitted changes:

| State | Behavior |
|---|---|
| **CLEAN** (live matches catalog render) | Overwrite live with new render |
| **CONFLICT** (live has uncommitted changes) | WARN — do not overwrite. Surface diff to user. |
| **PROTECT** (live is flagged as human-edited) | BLOCK — never overwrite. Require explicit `--force` with R-008 approval. |

## Cross-runtime test
A test that proves parity:
1. Render all 11 catalog agents for OpenCode → `.opencode/agents/`
2. Render all 11 catalog agents for Claude Code → `.claude/agents/`
3. Compare: every agent's effective configuration (name, description, model, mode, tools, delegates, skills, permissions) is identical across runtimes
4. Where a runtime lacks a feature, the gap is documented, not silently dropped

## Acceptance criteria
- [ ] Both runtimes documented (OpenCode, Claude Code)
- [ ] Byte-parity requirement defined with capability-equivalence model
- [ ] Claude Code adapter fix specified with acceptance criteria
- [ ] CONFLICT/PROTECT decision table from F-015 included
- [ ] Cross-runtime test procedure specified
- [ ] `aspis byte-parity` CLI verb referenced (detailed spec in cli-verbs.md)
- [ ] Consistent with FR-021 (permission-block preservation) and FR-022 (byte-parity check)
