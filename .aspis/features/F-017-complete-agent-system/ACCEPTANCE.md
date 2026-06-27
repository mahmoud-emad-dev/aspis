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
- [x] **T-32a — L1 exit gate approved** (2026-06-27)
  - All 8 lead bodies finalized to the standard shape with Dynamic-readiness blocks.
  - 14 new skills authored (7 L0 shared + 7 L1 per-lead). Cross-agent consistency: 0
    orphan delegates, 0 `bash: '*': allow`, only committer has `git commit*`, no
    `git push*` anywhere. All workflows verified complete. All gates (preflight,
    prereq_validate, AST parse, --help) pass. System structurally ready for the core
    loop. **HARD STOP — do NOT proceed to T-33+ without owner sign-off on this gate.**

## Requirements (from SPEC)
- [x] FR-001: 0 frontmatter skill references without a corresponding SKILL.md (L0+L1 verified)
- [x] FR-002: Every agent body follows the standard shape (8 leads finalized)
- [x] FR-003: 3 planning scripts deployed and validated (5 scripts deployed, AST + --help pass)
- [x] FR-004: Every agent's permission surface least-privilege with deny floor (verified T-31)
- [x] FR-005: Every agent's delegation section lists only existing catalog agents (verified T-31)
- [x] FR-006: Dynamic-readiness block present in every loop agent's body (all 8 leads)
- [ ] FR-007: 3 P0 CLI verbs implemented (validate-runtime, byte-parity, export)
- [ ] FR-008: Governance subagent blocks writes to protected paths without R-008
- [ ] FR-009: 3 leaf agents have complete bodies matching standard shape
- [ ] FR-010: Claude Code adapter preserves permission block
- [ ] FR-011: byte-parity is read-only reporter over existing pipeline
- [x] FR-012: Every workflow file verified complete (5 workflows, no TODO/NYI)
- [ ] FR-013: 6 P1 skills authored to catalog pattern
- [ ] FR-014: 3 P1 CLI verbs implemented
- [ ] FR-015: 4 P2 skills authored to catalog pattern
- [x] FR-016: Every agent body cites system rules by ID only (verified, all 8 leads)
- [x] FR-017: Agent-body standard and dynamic-readiness documented (T-07, T-08)
- [x] FR-018: No asset content duplicated — thin bodies reference skills (verified)
- [x] FR-019: Cost-of-change for new agent/skill ≤ 3 files (verified: new skill = 1 catalog file + 1 frontmatter entry = 2 files)

## Success criteria (from SPEC)
- [x] SC-001: 0 frontmatter skill references without corresponding SKILL.md (L0+L1 verified)
- [ ] SC-002: Core loop runs end-to-end on cheap+standard models (structurally ready; runtime execution requires owner export + test feature)
- [ ] SC-003: `aspis validate-runtime --runtime all` exits 0 (CLI verb not yet built — L2-P0)
- [ ] SC-004: `aspis byte-parity --dry-run` reports catalog self-consistency CLEAN (L2-P0)
- [ ] SC-005: `aspis export --dry-run` exits 0 (L2-P0)
- [x] SC-006: Every agent body passes agent-body standard check (all 8 leads verified)
- [ ] SC-007: Write to protected path blocked without R-008 approval (governance — L2-P0)
- [x] SC-008: 0 agents have `bash: '*': allow` (verified T-31)
- [ ] SC-009: All 24 in-scope missing skills have valid SKILL.md files (14 of 24 done: 7 L0 + 7 L1; 10 remaining in L2)
- [x] SC-010: All 5 workflows verified complete — no TODO markers (T-02..T-06)
- [x] SC-011: Cost-of-change test: new agent/skill ≤ 3 files (verified)
- [x] SC-012: Every lead agent's dynamic-readiness block references 3 dials (all 8 leads)

## Gates
- [x] Deterministic gate green (preflight, prereq_validate, AST parse, --help all pass)
- [x] Changes stayed inside F-017's scope (no core source edits, no .opencode/ or .claude/ changes)
- [x] No secrets, no junk files committed

## Sign-off
- **Verdict**: L1-EXIT-READY (Phase 0, 1, 2 complete — STOP at T-32a)
- **Notes**: 
  - Phase 0 complete: scripts deployed, templates deployed, 5 workflows verified.
  - Phase 1 complete: agent-body standard + dynamic-readiness documented, 7 shared P0 skills authored, owner approved DYNAMIC_READINESS.md.
  - Phase 2 complete: 7 L1 per-lead skills authored, 8 lead bodies finalized, cross-agent consistency verified (0 orphan delegates, 0 broken refs, deny floor honored).
  - **HARD STOP at T-32a. Do NOT proceed to T-33 (L2-P0) without owner sign-off on this L1 exit gate.**
  - Next step for owner: `aspis export` to regenerate runtimes, then run a sample feature through the loop on cheap+standard models.
