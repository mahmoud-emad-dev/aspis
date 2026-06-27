# F-016 — Build Report

> Agent System Architecture — complete specification of all 11 ASPIS agents plus systemic infrastructure.

## Feature Status: COMPLETE ✅

- **Phase**: Build complete
- **Tasks**: 41/41 complete (T-01 through T-41)
- **Review verdict**: APPROVED with notes (T-38 final acceptance review; 0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW)
- **Cross-reference gate**: PASS (T-40, 12/12 specs, 0 HIGH, 0 MEDIUM findings)
- **Commits**: 48 commits on `feature/F-016-agent-system-architecture`
- **Working tree**: clean at start of T-41

## Artifacts Produced

### Reference Specs (12 files in `.aspis/features/F-016-agent-system-architecture/Research/ref/`)

| # | Agent | Type | Sections |
|---|---|---|---|
| 1 | project-lead | Lead (L1) | 16 |
| 2 | planning-lead | Lead (L1) | 17 |
| 3 | build-lead | Lead (L1) | 16 |
| 4 | reviewer | Support (L2) | 16 |
| 5 | system-lead | Support (L2) | 16 |
| 6 | fix-lead | Support (L2) | 16 |
| 7 | test-lead | Support (L2) | 12 |
| 8 | research-lead | Support (L2) | 14 |
| 9 | committer | Leaf (L3) | 6 |
| 10 | general-builder | Leaf (L3) | 6 |
| 11 | project-explorer | Leaf (L3) | 6 |
| 12 | governance | Systemic | 7 |

### Systemic Specs (5 files in `.aspis/features/F-016-agent-system-architecture/Research/specs/`)

1. `modes.yaml` — modes config specification (3 modes × 8 knobs)
2. `enforcement.md` — enforcement mode spec (3 boundaries, transition plan)
3. `planning-scripts.md` — planning scripts deployment spec (3 scripts)
4. `cli-verbs.md` — missing CLI verbs spec (6 verbs)
5. `cross-runtime.md` — cross-runtime parity spec (Claude adapter fix + byte-parity)

### Skills Inventory

- `.aspis/features/F-016-agent-system-architecture/Research/skills/inventory.md` —
  63 skills total, 38 existing, 25 missing (13 P0, 7 P1, 5 P2)

### Catalog Agent Files (11 in-scope files in `src/aspis/data/catalog/agents/`)

All 11 catalog files updated with frontmatter aligned to reference specs. All pass structural validation (T-30 approved-with-notes after the `runtimes` field fix in `f574496`).

- 8 leads: `project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`, `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`
- 3 leaves: `committer.md`, `general-builder.md`, `project-explorer.md`

`bootstrap.md` (12th file in the directory) is **explicitly excluded from F-016 scope** — it is a one-time onboarding agent that self-deletes; its missing `delegates`/`runtimes` are tracked as a follow-up.

### Audit Artifacts (2 files in `Research/audit/`)

- `findings-1.md` — T-03 adversarial audit (7 CRITICAL + 13 HIGH + 14 MEDIUM + 5 LOW = 39 unique findings)
- `findings-triage.md` — T-04 owner-decided Group 1/2/3 disposition

### Feature Documents

- `SPEC.md` — feature specification (FR-001 through FR-028; 12 SCs)
- `PLAN.md` — implementation plan (13 steps)
- `TASKS.md` — task breakdown (41 tasks)
- `BUILD_REPORT.md` — this file

## Gate Results

| Gate | Task | Result |
|---|---|---|
| Research verification | T-01 | 14/14 files accessible |
| Cross-reference tool | T-02 | `cross_ref_agents.py` built |
| Adversarial audit | T-03 | 39 findings (7 CRITICAL + 13 HIGH + 14 MEDIUM + 5 LOW), triaged |
| Findings resolved | T-04 | 10 Group-1 fixes applied to lead specs |
| Cross-ref: leads | T-05 | PASS — 0 HIGH, 0 MEDIUM |
| Lead specs locked | T-06..T-13 | All 8 locked |
| Cross-ref: all 11 | T-14 | PASS — gate green (US1 checkpoint) |
| Leaf specs produced | T-15..T-17 | 3 leaf specs |
| Cross-ref: leaves | T-18 | PASS — gate green |
| Catalog files updated | T-19..T-29 | 11 files aligned to ref specs |
| Catalog validation | T-30 | Approved-with-notes (after `runtimes` field fix in `f574496`) |
| Skills inventory | T-31 | 25 missing skills identified with P0/P1/P2 priority |
| Governance spec | T-32 | 7 sections, R-008 compliant |
| modes.yaml spec | T-33 | 3 modes × 8 knobs |
| Enforcement spec | T-34 | 3 boundaries, transition plan |
| Planning scripts spec | T-35 | 3 scripts with validation |
| CLI verbs spec | T-36 | 6 verbs specified |
| Cross-runtime spec | T-37 | Claude adapter permission-block preservation + byte-parity spec |
| Final acceptance review | T-38 | APPROVED with notes (0 CRITICAL, 0 HIGH) |
| SPEC clarifications | T-39 | 7 build decisions documented in `SPEC.md` Clarifications |
| Final cross-reference | T-40 | PASS (12/12 specs, 0 HIGH, 0 MEDIUM) |
| Build report & handoff | T-41 | This file |

## Success Criteria Verification

| SC | Description | Status |
|---|---|---|
| SC-001 | 11 agent specs pass adversarial review (0 CRITICAL, 0 HIGH unresolved) | ✅ PASS |
| SC-002 | Cross-agent consistency (0 overlap, 0 orphaned edges) | ✅ PASS |
| SC-003 | 11 catalog files frontmatter-aligned with ref specs | ✅ PASS |
| SC-004 | 25 missing skills specified with purpose/owner/priority (T-31 inventory) | ✅ PASS |
| SC-005 | 6 missing CLI verbs specified with purpose/priority (T-36 spec) | ✅ PASS |
| SC-006 | Governance spec R-008 compliant | ✅ PASS |
| SC-007 | modes.yaml spec complete (all 8 knobs per mode) | ✅ PASS |
| SC-008 | Enforcement mode spec passes security review | ✅ PASS |
| SC-009 | 3 planning scripts have deployment specifications | ✅ PASS |
| SC-010 | Claude adapter permission-block preservation specified (T-37) | ✅ PASS |
| SC-011 | PLAN/TASKS ready for handoff (28 FRs → ≥1 task each) | ✅ PASS |
| SC-012 | Cost-of-change ≤5 files to add a new agent (catalog + profile + SPEC + PLAN + TASKS) | ✅ PASS |

**T-38 review summary** (from `REVIEW-F-016-T-38.md`):

| Dimension | Result |
|---|---|
| Architecture constitution (12 rules) | 12/12 PASS |
| System rules (R-001…R-010) | 10/10 PASS |
| Cross-agent consistency | 0 overlapping responsibilities, 0 orphaned edges (7 F-017-deferred exceptions annotated) |
| Permission surface | 11/11 correct; R-004 and R-008 invariants hold |
| Model tier consistency | All 11 agents declare a tier; standard default for leads, cheap for leaves |
| Frontmatter completeness | 11/11 fields × 11/11 files |
| FR → task coverage | 28/28 FRs mapped to ≥1 task |
| SC → verification coverage | 12/12 SCs verified with evidence |
| **Findings** | **0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW** |
| **Verdict** | **APPROVED with notes** |

## Open Follow-ups

1. **F-017** — Build the 7 future L3 subagents referenced in `planning-lead` (`clarify`,
   `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`,
   `scope-estimator`, `research-request-writer`).
2. **Skills build** — Author 25 SKILL.md files from the T-31 inventory
   (13 P0, 7 P1, 5 P2).
3. **CLI build** — Implement the 6 CLI verbs from the T-36 spec
   (`validate-runtime`, `validate-index`, `byte-parity`, `drift`, `export`, `governance`).
4. **Claude adapter fix** — Implement permission-block preservation from the T-37 spec
   (5 acceptance criteria in `cross-runtime.md`).
5. **`bootstrap.md`** — Add missing `delegates` and `runtimes` fields
   (out of F-016 scope; transient onboarding agent).
6. **FR-007 wording** — Update to match system-lead `websearch: deny`
   (the catalog and reference spec are correct; only the SPEC text is wrong).
7. **Enforcement flip** — Execute the warn→block transition plan from the T-34 spec.
8. **Governance build** — Implement the governance subagent as a deterministic script
   (R-008 enforcement at runtime).

## Build-Phase Clarifications (T-39)

Seven decisions made during build, captured in `SPEC.md` Clarifications:

1. **Skills count** — SPEC said "30+ missing skills"; actual T-31 count is 25
   (13 P0, 7 P1, 5 P2). The 38 existing + 25 missing = 63 total referenced.
2. **System-lead websearch** — FR-007 says `websearch: allow` for system-lead,
   but T-23 catalog + ref spec intentionally set `websearch: deny`.
   FR-007 wording is wrong; catalog and ref spec are correct.
3. **Planning-lead future subagents** — 7 L3 subagents are intentional references
   for F-017; the catalog file marks them as future.
4. **`bootstrap.md`** — 12th catalog file; outside F-016 scope.
5. **Skills deferred** — 25 missing skills are specified in T-31 inventory;
   authoring is a follow-up.
6. **Claude Code adapter** — permission-block preservation specified in T-37
   with 5 acceptance criteria; adapter fix is a follow-up.
7. **CLI verbs** — 6 verbs specified in T-36; building them is a follow-up.
   T-30's catalog structural check was performed manually since the CLI does not
   yet exist.

## Branch & Commit Info

- **Branch**: `feature/F-016-agent-system-architecture`
- **Base**: main (last pre-F-016 commit: `ce9d036 docs(F-015): close feature`)
- **Commits on this branch for F-016**: **48** (`8d9f007` … `6f4be1c`)
- **Commit message style**: conventional commits with `(F-016/...)` scope
- **All 41 tasks committed** with conventional messages

## Handoff

F-016 is ready for merge review. All artifacts are on the feature branch.
The spec-plan-tasks triplet is complete. The catalog files are updated.
The reviewer approved the final acceptance review (T-38, APPROVED with notes;
0 CRITICAL, 0 HIGH).

**Next step**: Merge `feature/F-016-agent-system-architecture` to main,
then take up one of the open follow-ups — F-017 (subagent roster), skills build,
CLI verbs build, or Claude adapter fix.
