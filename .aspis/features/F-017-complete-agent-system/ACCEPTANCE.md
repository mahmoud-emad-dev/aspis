# Acceptance — F-017

> The boolean closure gate for the feature: every box must be checked before the
> feature is accepted. Derive the FR/SC rows from SPEC.md. The header is stamped
> by `aspis artifact`; resolve a failing box by fixing the work, never by deleting
> the check.

- **Feature**: F-017 — Complete the Agent System
- **Date**: 2026-06-27

## R-008 Approvals

- [x] **T-08a — DYNAMIC_READINESS.md approved** (2026-06-27)
  - `.aspis/context/DYNAMIC_READINESS.md` — the three-dial model, key distinction
    (optimize path, never bar), leanest-correct-path default, future-router-ready.
    Owner approved as part of F-017 build instruction. L1 agents may now reference
    this convention in their Dynamic-readiness blocks.
- [ ] **T-32a — L1 exit gate approved** (pending — blocked on T-32 completion)

## Requirements (from SPEC)
- [ ] FR-001: 0 frontmatter skill references without a corresponding SKILL.md
- [ ] FR-002: Every agent body follows the standard shape
- [ ] FR-003: 3 planning scripts deployed and validated
- [ ] FR-004: Every agent's permission surface least-privilege with deny floor
- [ ] FR-005: Every agent's delegation section lists only existing catalog agents
- [ ] FR-006: Dynamic-readiness block present in every loop agent's body
- [ ] FR-007: 3 P0 CLI verbs implemented (validate-runtime, byte-parity, export)
- [ ] FR-008: Governance subagent blocks writes to protected paths without R-008
- [ ] FR-009: 3 leaf agents have complete bodies matching standard shape
- [ ] FR-010: Claude Code adapter preserves permission block
- [ ] FR-011: byte-parity is read-only reporter over existing pipeline
- [ ] FR-012: Every workflow file verified complete
- [ ] FR-013: 6 P1 skills authored to catalog pattern
- [ ] FR-014: 3 P1 CLI verbs implemented
- [ ] FR-015: 4 P2 skills authored to catalog pattern
- [ ] FR-016: Every agent body cites system rules by ID only
- [ ] FR-017: Agent-body standard and dynamic-readiness documented in .aspis/context/
- [ ] FR-018: No asset content duplicated across agent bodies (R-006)
- [ ] FR-019: Cost-of-change for adding new agent/skill ≤ 3 files

## Success criteria (from SPEC)
- [ ] SC-001: 0 frontmatter skill references without corresponding SKILL.md
- [ ] SC-002: Core loop runs end-to-end on cheap+standard models
- [ ] SC-003: `aspis validate-runtime --runtime all` exits 0
- [ ] SC-004: `aspis byte-parity --dry-run` reports catalog self-consistency CLEAN
- [ ] SC-005: `aspis export --dry-run` exits 0
- [ ] SC-006: Every agent body passes agent-body standard check
- [ ] SC-007: Write to protected path blocked without R-008 approval
- [ ] SC-008: 0 agents have `bash: '*': allow`
- [ ] SC-009: All 24 in-scope missing skills have valid SKILL.md files
- [ ] SC-010: All 5 workflows verified complete — no TODO markers
- [ ] SC-011: Cost-of-change test: new agent/skill ≤ 3 files
- [ ] SC-012: Every lead agent's dynamic-readiness block references 3 dials

## Gates
- [ ] Deterministic gate green on every supported OS
- [ ] Changes stayed inside F-017's scope
- [ ] No secrets, no junk files committed

## Sign-off
- **Verdict**: not-yet
- **Notes**: Phase 0 complete. Phase 1 in progress. Owner approved DYNAMIC_READINESS.md
  at T-08a (2026-06-27). L1 exit gate approval pending at T-32a.
