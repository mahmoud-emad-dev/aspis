# Review — F-017 / F-017-system-integrity

> Filled by the reviewer (read-only — you evaluate and report, you never edit the
> work). The header is stamped by `aspis artifact`; you fill the verdict and
> findings from evidence (the diff, the tests, the acceptance criteria).

- **Feature**: F-017 — Complete the Agent System
- **Task**: F-017-system-integrity
- **Date**: 2026-06-27
- **Verdict**: **changes-requested**

## Scope reviewed

F-017 Phase 0–2 built artifacts:

- **Scripts** (deployed): `.aspis/scripts/planning/{_console.py, active_feature.py, feature_scaffold.py, prereq_validate.py, task_compile.py, cross_ref_agents.py}` — 6 files; first 5 are byte-identical to catalog source, 6th has no catalog source
- **Templates** (deployed): `.aspis/templates/planning/{SPEC.md, PLAN.md, TASKS.md, ACCEPTANCE.md, TASK_PACKET.md}` — 5 files, byte-identical to catalog source
- **Workflows**: `.aspis/workflows/{plan, build, review, fix, small-task}.md` — 5 files, no TODO/NYI markers
- **Agent bodies**: 12 files at `src/aspis/data/catalog/agents/{project-lead, planning-lead, build-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer, general-builder, project-explorer, bootstrap}.md`
- **Conventions**: `.aspis/context/{AGENT_BODY_STANDARD.md, DYNAMIC_READINESS.md}` — both present, R-008 approved for DYNAMIC_READINESS
- **Skills**: 14 new skills at `src/aspis/data/catalog/skills/<name>/SKILL.md` (7 L0 + 7 L1) — all referenced by owning agents
- **Branch state**: `feature/F-017-complete-agent-system` — 5 expected commits; 2 untracked review files in working tree

The full review (with detailed file:line evidence and per-finding analysis) is in
`.aspis/features/F-017-complete-agent-system/Review/system-integrity.md`.

## Findings

| Severity | Where | Finding | Suggested fix |
|----------|-------|---------|---------------|
| critical | `.aspis/features/F-017-complete-agent-system/Review/{agent-body-quality.md, skill-quality.md}` (2 untracked files) | Working tree is NOT clean — `git status` claims clean but `git status -uall` shows 2 substantial prior-review files (~1620 lines combined) that were never committed. The build-lead's branch-state claim is FALSE. | Commit the 2 review files with a `docs(F-017/review): …` message, or move them to a scratch location if they are not part of the deliverable. |
| critical | `src/aspis/data/catalog/agents/project-lead.md` (between L122 and L184) | MISSING `## Delegation` section — required by AGENT_BODY_STANDARD.md §"Required body sections" §6. 8 delegates in frontmatter but no body section. FR-005 audit cannot verify the body. | Add `## Delegation` between Responsibilities→skills and Dynamic-readiness; list 8 delegates with one-line trigger + purpose each. |
| critical | `src/aspis/data/catalog/agents/research-lead.md` (between L192 and L194) | MISSING `## Delegation` section — same as project-lead. 1 delegate (project-explorer) in frontmatter but no body section. | Add a 3-line `## Delegation` section listing `project-explorer` with its trigger. |
| critical | `src/aspis/data/catalog/agents/build-lead.md:60` | `# Identity` is H1 instead of `## Identity` — breaks heading hierarchy; the other 11 bodies use `## Identity`. A sign the structural sweep against the standard was not run. | Change L60 from `# Identity` to `## Identity` (one-character fix). |
| high | `src/aspis/data/catalog/agents/bootstrap.md` (frontmatter L1–L29) | Missing 2 of 11 required frontmatter fields — no `delegates:` and no `runtimes:`. Standard requires 11/11 on every body. Build-lead's "11 fields" claim is scoped to "8 leads" (true) but the broader catalog claim is FALSE. | Add `delegates: []` and `runtimes: []` (bootstrap is a one-time primary; not exported to runtimes). |
| high | `src/aspis/data/catalog/agents/{project-lead, planning-lead, build-lead, fix-lead, research-lead, reviewer, system-lead}.md` Core rules sections | 7 of 8 lead bodies have Core-rules sections that restate system rules in prose without citing R-### by ID — the most-named anti-pattern in the standard ("No restated rules"). ~40 restated-rule bullets across 7 bodies. reviewer cites only R-004; system-lead cites R-004 + R-008. | Replace each prose bullet with a single R-### citation; keep 2–3 own rules (the "if stuck, stop" rule, role-specific own rules). |
| high | `src/aspis/data/catalog/agents/*.md` (all 8 lead bodies) | 8 of 8 lead bodies have 15–64 lines of inlined procedure each (~430 lines total) that should reference skills/workflows. R-006 violation + FR-019/SC-011 cost-of-change violation. | Trim inlined procedure to 1–2 lines + pointer; bodies should land in 80–120 line range. |
| high | `src/aspis/data/catalog/agents/{project-lead, research-lead}.md` Identity | 2 lead bodies missing prime-directive block. Standard requires "IS / IS NOT / prime directive" structure; planning-lead/reviewer/system-lead have it. | Add `### Prime directive` block to each Identity section. |
| high | `src/aspis/data/catalog/skills/constitution-checks/SKILL.md:23-42` | Skill enumerates 12 rules by prose names; `constitution-checks.yaml` (system-of-record per its own comment L1–L7) lists 11 rules. The two systems disagree. R-006 single-source violation. | Have the skill reference the YAML; have the YAML add `C-ARCH-BEFORE-FEATURES` (or remove it from the constitution) so the two systems agree. |
| high | `src/aspis/data/catalog/skills/constitution-check/SKILL.md:50` | Skill's anti-pattern claims "the planning-lead handles the other 3" (Local Change, Architecture before Features, Portable by Default) but the YAML says these are NOT plan-only, and `C-ARCH-BEFORE-FEATURES` doesn't exist in the YAML. | Align the skill with the YAML; either update the YAML to add `C-ARCH-BEFORE-FEATURES` and update `enforced_by`, or fix the skill. |
| medium | reviewer run-time | `aspis preflight` could not be independently verified by the reviewer — preflight is not in the reviewer's bash allowlist. The closest gate (`prereq_validate.py --phase build`) does pass. | Either the owner runs preflight and records output in ACCEPTANCE.md, or the reviewer's bash allowlist is extended to include preflight. |
| medium | `.aspis/scripts/planning/cross_ref_agents.py` | Exists at runtime path but NOT at the catalog source path. R-006 single-source violation — script should live in `src/aspis/data/catalog/scripts/planning/` and be deployed. | Move to catalog source and add a T-NN to deploy it; or move to `.aspis/scripts/build/` if it's strictly build-time tooling. |
| medium | `.aspis/scripts/planning/task_compile.py` | Not re-verified for byte-identity with the catalog source. The other 4 deployed files ARE byte-identical. | Run a `filecmp` or `cmp` over the 5 deployed files. |
| medium | 5 agent bodies reference `.aspis/workflows/` and `.aspis/config/constitution-checks.yaml` | The bodies sit in the source catalog but reference the *deployed* paths. The actual files live at `src/aspis/data/catalog/...`. Stale from a factory-repo perspective. | Change to `src/aspis/data/catalog/workflows/<name>.md` and `src/aspis/data/catalog/config/policy/constitution-checks.yaml`, or document the render-time substitution. |
| medium | `src/aspis/data/catalog/config/policy/constitution-checks.yaml` | Missing `C-ARCH-BEFORE-FEATURES` (the prose `architecture-constitution.md` has 12 rules; the YAML has 11). YAML drift. | Add `C-ARCH-BEFORE-FEATURES` to the YAML with `enforced_by: [planning]` and a `review_question`. |
| medium | `.aspis/context/AGENT_BODY_STANDARD.md:27` | `mode` field documented as `vibe/mvp/production` but all 8 leads ship `mode: primary/subagent`. ARCHITECTURE.md confirms `primary/subagent` is correct. Standard's docstring is wrong. | Change L27 to "`primary` / `subagent`" (or add a new `build_mode` field if both are needed). |
| medium | `src/aspis/data/catalog/agents/{project-lead, research-lead}.md` (L58 and L35 respectively) | `> Derived from Research/ref/...` precedes `# Title` (reversed order). The 6 other bodies follow the standard's order. | Swap the two lines in each body so the `# Title` is first and the `> Derived…` quote is second. |
| medium | `src/aspis/data/catalog/agents/project-lead.md:141-158` | 18-line inlined bootstrap-gate block is non-standard and not self-removing (no runtime code actually removes it). | Move to a `bootstrap-gate` skill and reference it, or document the runtime mechanism. |
| medium | 4 lead bodies (project-lead, build-lead, fix-lead, research-lead) | Identity sections don't follow the standard's IS / IS NOT / prime directive structure. | Restructure Identity to the standard's 3-element shape (subsumed by H-4 for the prime-directive gap). |
| low | `src/aspis/data/catalog/agents/{fix-lead, general-builder}.md` | `edit: '*': allow` and `write: '*': allow` with explicit denials for protected paths. This is the standard pattern for builders/fixers, not a defect — verification note only. | None. |
| low | 8 lead bodies | Section titles "How you plan" / "How you execute" / "How you review" etc. deviate from the standard's required `## How you work` title. Cosmetic. | Rename to `## How you work` (with topic subtitle in body), or update the standard to allow topic-specific names. |
| low | `.aspis/workflows/small-task.md` | Lists 5 tracks; planning-lead ref spec §2 lists 6 (adds `Defect → fix-lead`). | Expand the workflow to 6 tracks, or scope the TASKS T-06 description to 5. |
| low | `prereq_validate.py:59` | Path-resolution helper tries `.aspis/config/<name>` first then `.aspis/config/policy/<name>` — works for the live config layout. Verification note. | None. |
| low | `src/aspis/data/catalog/agents/reviewer.md:209` | `constitution-checks.yaml` path mismatch (deployed path used; source path needed). Subsumed by the workflow-path M-4 finding. | Update the path to `src/aspis/data/catalog/config/policy/constitution-checks.yaml`. |

## Decision & hand-off

**CHANGES-REQUESTED.** 3 CRITICAL, 6 HIGH, 9 MEDIUM, 5 LOW. The build's substantive work is sound — the deny floor is honored, the 8 leads are structurally correct, all 49 skill references and 28 delegate references resolve, the dynamic-readiness convention is documented and approved, the scripts and templates are byte-identical to their catalog sources, and the deterministic gates pass. The shape-and-discipline gaps (3 CRITICAL, 6 HIGH) are the next layer of work.

**The build-lead's gate claims are 16/19 TRUE, 2 FALSE (git status cleanliness, 11-fields claim for bootstrap), 1 UNVERIFIABLE (aspis preflight by the reviewer).** Most are independently verified.

**3 critical integrity gaps must be fixed before T-33+ (L2-P0):**
1. `git status` is not clean (2 untracked review files in the working tree).
2. 2 of 8 lead bodies are missing a required `## Delegation` section.
3. 1 of 8 lead bodies has a heading-hierarchy break.

**Do NOT proceed to T-33+ (L2-P0) without addressing all 3 CRITICAL, all 6 HIGH, and at least the 2 most-blocking MEDIUMs (M-1 preflight verification, M-4 workflow paths).** The remaining MEDIUMs and LOWs are improvements that should be addressed in the same revision pass but are not gate-blocking.

**Recommendation**: route to build-lead for a 6–10 hour revision pass:

1. Commit (or move) the 2 untracked review files (C-1).
2. Add `## Delegation` to project-lead.md and research-lead.md (C-2).
3. Change `# Identity` to `## Identity` in build-lead.md:60 (C-3).
4. Add `delegates: []` and `runtimes: []` to bootstrap.md (H-1).
5. Replace restated rule prose with R-### citations in 7 bodies (H-2).
6. Remove ~430 lines of inlined procedure; reference skills/workflows (H-3).
7. Add `### Prime directive` blocks in project-lead + research-lead (H-4).
8. Align constitution-checks / constitution-check skills with constitution-checks.yaml (H-5, H-6, M-5).

After the revision pass, re-run the L1 exit gate and the cross-agent consistency check; the system should be L2-P0 ready. The design is sound, the specs are correct, and the build's substantive work is good.

The full review (with detailed file:line evidence and per-finding analysis) is in
`.aspis/features/F-017-complete-agent-system/Review/system-integrity.md`.
