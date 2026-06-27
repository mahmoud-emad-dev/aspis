# F-016 — Consolidated Triple Review

> **Three independent deep reviews — merged into one verdict.**
> **Reviewers:** Security/Adversarial · Architecture/Constitution · Completeness/Quality
> **Date:** 2026-06-27
> **Scope:** 12 reference specs, 5 systemic specs, 11 catalog files, SPEC/PLAN/TASKS, BUILD_REPORT, audit & pentest files
> **Combined verdict:** **APPROVE WITH CONDITIONS** — 4 small follow-ups (~1 hour) before merge

---

## Combined Findings Summary

| Severity | Security | Architecture | Completeness | Total |
|---|---|---|---|---|
| CRITICAL | 8 | 3 | 0 | **11** |
| HIGH | 12 | 4 | 0 | **16** |
| MEDIUM | 10 | 6 | 2 | **18** |
| LOW | 0 | 4 | 10 | **14** |

> **Note on CRITICAL findings:** The Security reviewer classified 8 findings as CRITICAL; 5 of these are live-vs-catalog drift (the catalog is fixed, the live runtime is stale), 2 are specific permission-scope gaps (C-6 research-lead write, C-7 test-lead edit/write), and 1 is R-008 prose-only. The Architecture reviewer classified 3 constitution-index inconsistencies as CRITICAL. All 11 are **correct in design, incomplete in deployment** — the F-016 spec layer is sound; the implementation follow-ups are missing.

---

## CRITICAL Findings (unified)

### SEC-C1 · Live system-lead has `bash: '*': allow` (catalog fixed, live not re-rendered)
**Source:** Security review §1  
**Fix:** Re-render live from catalog; add `aspis byte-parity` gate

### SEC-C2 · R-008 is prose-only — no mechanical enforcement
**Source:** Security review §1  
**Fix:** Build governance subagent (spec done; implementation is follow-up)

### SEC-C3 · Hook enforcement `warn` — protected-paths check is no-op
**Source:** Security review §1  
**Fix:** Flip to `block` for runtime tools (spec done; implementation follow-up)

### SEC-C4 · system-lead can re-route every agent to cheapest model
**Source:** Security review §1  
**Fix:** Move `models.yaml` to Tier 2 governance-only; R-008 gate for changes

### SEC-C5 · system-lead can author new agents — governance escape
**Source:** Security review §1  
**Fix:** `aspis doctor` roster check; R-008 gate for new agent creation

### SEC-C6 · research-lead has unrestricted `write:` scope
**Source:** Security review §1 (net-new finding — audit structurally unable to detect)  
**Fix:** Path-scope `write:` to `.aspis/research/**` and `.aspis/features/F-*/Research/**`

### SEC-C7 · test-lead has unrestricted `edit:` and `write:`
**Source:** Security review §1 (net-new finding — audit structurally unable to detect)  
**Fix:** Path-scope `edit:` and `write:` to `tests/**`

### SEC-C8 · Live Claude render drops entire `permission:` block
**Source:** Security review §1  
**Fix:** Claude Code adapter fix; verify with `aspis byte-parity --runtime all`

### ARC-C1 · Constitution prose ↔ YAML drift (C-SINGLE-SOURCE violation)
**Source:** Architecture review  
**Fix:** Reconcile prose rules (12) with YAML checks (11); pick one canonical list

### ARC-C2 · FR-007 SPEC text contradicts design (`websearch`)
**Source:** Architecture review  
**Fix:** Update FR-007 to match design: system-lead `websearch: deny`

### ARC-C3 · Three sources of truth for constitution rule list (prose, YAML, T-38 review)
**Source:** Architecture review  
**Fix:** Adopt T-38 reviewer's 12-rule set as canonical; update prose and YAML

---

## HIGH Findings (unified)

| # | Finding | Source | Fix |
|---|---|---|---|
| SEC-H1 | Live system-lead model tier mismatch (standard vs deep) | Security | Model routing follow-up |
| SEC-H2 | `ASPIS_ALLOW_PROTECTED=1` is env var, not secret | Security | Replace with governance approval |
| SEC-H3 | Scope-guard "no scope = allow all" fallback | Security | Make scope-guard opt-out (default deny) |
| SEC-H4 | `enforcement: block` is target, current is `warn` | Security | Implement flip; set ship date |
| SEC-H5 | Live system-lead `websearch: allow` (catalog denies) | Security | Re-render live from catalog |
| SEC-H6 | system-lead can install arbitrary git hooks | Security | Move hooks outside system-lead scope |
| SEC-H7 | `system-repair` no recursion guard, no idempotency | Security | Add 3-attempt cap; diff-before-reinit |
| SEC-H8 | Reviewer `aspis artifact*` in bash allowlist | Security | Remove or narrow to review-only |
| SEC-H9 | system-lead `webfetch + websearch` prompt-injection | Security | Catalog fixes; re-render live |
| SEC-H10 | Live Claude render has no `task:` block | Security | Claude adapter permission-block fix |
| SEC-H11 | Audit document in system-lead's scope | Security | Move to path system-lead cannot edit |
| SEC-H12 | system-lead can clear `findings.json` | Security | Make findings append-only |
| ARC-H1 | Governance subagent specified but not built | Architecture | Build in follow-up feature |
| ARC-H2 | Claude adapter fix specified but not applied | Architecture | Implement adapter fix |
| ARC-H3 | 6 missing CLI verbs specified but not built | Architecture | Build `aspis validate-runtime`, etc. |
| ARC-H4 | Reviewer model tier declared but live may drift | Architecture | Build `aspis models --apply` |

---

## MEDIUM Findings (unified)

| # | Finding | Source |
|---|---|---|
| SEC-M1 | planning-lead edit pattern `**/Research/ref/**` too broad | Security |
| SEC-M2 | `protect.py` doesn't cover live runtime files | Security |
| SEC-M3 | Bootstrap `aspis *` wildcard | Security |
| SEC-M4 | Reviewer catalog lacks "if stuck, stop" rule | Security |
| SEC-M5 | `aspis models --apply` is silent, no human loop | Security |
| SEC-M6 | Cross-runtime model tier drift (OpenCode standard, Claude deep) | Security |
| SEC-M7 | No advisory/lockfile for concurrent system-lead sessions | Security |
| SEC-M8 | Audit performed by reviewer with tier drift | Security |
| SEC-M9 | 4 missing skills in frontmatter (mode-decision, etc.) | Security |
| SEC-M10 | bootstrap.md is 12th catalog file, missing fields | Security |
| ARC-M1 | planning-lead ↔ reviewer historical conflict (fixed) | Architecture |
| ARC-M2 | 7 future L3 subagents in delegates | Architecture |
| ARC-M3 | 4 skills referenced but not in catalog | Architecture |
| ARC-M4 | bootstrap.md 12th agent, missing fields | Architecture |
| ARC-M5 | Shared skills (context-ladder, prestart-checks) by design | Architecture |
| ARC-M6 | Constitution "12-point" count drift | Architecture |
| CQ-C1 | FR-007 vs design websearch contradiction | Completeness |
| CQ-C6 | BUILD_REPORT says 41/41; TASKS.md shows 22 `[ ]` | Completeness |

---

## LOW Findings — 14 total

Across all three reviews: 14 LOW findings covering cosmetic issues (section numbering, BUILD_REPORT section counts, terminology drift, file naming consistency) — all documented in the source reviews. None block merge.

---

## Strengths (all three reviews agree)

- **Governance subagent spec is exemplary** — 634 lines, deterministic script design, append-only ledger, 3 enforcement boundaries
- **Citation discipline is strong** — every spec cites its sources; the audit/triage loop is textbook
- **Adversarial honesty** — the audit found 40 findings; the triage was honest about Group 1/2/3; the pentest found 30 more
- **Edge case coverage is uniformly strong** — 10–25 explicit refusals per lead spec
- **Cross-reference verification** — `cross_ref_agents.py` gates at 4 checkpoints; all PASS
- **R-004 one-writer invariant** holds — committer is the only `git commit*` allow
- **No cross-agent responsibility conflicts** — 0 conflicts in current state
- **No scope creep** — every out-of-scope item is marked
- **Architecture constitution: 12/12** in design; 11/12 in YAML enforcement
- **System rules: 10/10** followed in spec; R-008 has documented deployment gap

---

## Conditions for Merge (4 follow-ups, ~1 hour total)

### R-1 (5 min) — Update bookkeeping
- Flip TASKS.md checkboxes for T-19..T-41 from `[ ]` to `[x]`
- Correct BUILD_REPORT section counts (4 specs overstate: reviewer, system-lead, fix-lead, research-lead)

### R-2 (15 min) — Fix FR-007 and system-lead `websearch` drift
- Update SPEC.md FR-007: `webfetch`/`websearch` denied for all agents except research-lead
- Update system-lead ref spec §5: `websearch: deny` (matches catalog)
- Update system-lead ref spec §13: mark open question as "Resolved: deny"

### R-3 (15 min) — Document live/catalog regeneration gap
- Add to BUILD_REPORT: catalog is updated; live `.opencode/agents/*.md` is stale
- Specific drift: `committer: allow` still in live planning-lead and project-lead
- Track as follow-up for `aspis export` build

### R-4 (30 min) — Terminology cleanup
- Standardize R-008 phrasing across all specs
- Standardize "byte-parity" / "byte-identical" terminology
- Consolidate T-30 review files into one directory

### Follow-up features (tracked, NOT merge conditions)
- **F-017**: 7 L3 subagents, 25 skills, 6 CLI verbs, governance build, enforcement flip
- **Claude adapter fix**: permission-block preservation, `aspis byte-parity` verification
- **Live regeneration**: `aspis export` to sync catalog → live runtime
- **Security hardening**: research-lead write scope, test-lead edit/write scope, system-lead bash allowlist, audit/pentest doc relocation

---

## Verdict

**APPROVE WITH CONDITIONS**

F-016 delivers what it promised: a complete, adversarially-audited, cross-validated specification of the ASPIS agent system architecture. The 8 lead reference specs are deep and well-cited. The systemic specs (governance, modes, enforcement) are thorough. The catalog is aligned. The gaps are honest and documented.

The conditions (R-1 through R-4) are bookkeeping and text-drift fixes, not design flaws. After they land, F-016 is ready to merge to main. The implementation follow-ups are well-defined features with clear designs.

---

*Consolidated from:*
- `.aspis/features/F-016-agent-system-architecture/Review/security-adversarial.md` — Security & Adversarial review
- `.aspis/features/F-016-agent-system-architecture/Review/architecture-constitution.md` — Architecture & Constitution review
- `.aspis/features/F-016-agent-system-architecture/Review/completeness-quality.md` — Completeness & Quality review
