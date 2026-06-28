# F-018 — Phase C: Full-Feature End-to-End Review

> **Reviewer:** Reviewer (independent)
> **Date:** 2026-06-28
> **Feature:** F-018 — Complete the Asset Set & Harden to a Reliable Release
> **Mode:** production (full rigor)
> **Verdict:** **CHANGES REQUIRED** — see §5 for blocking issues

---

## §1 — Per-Category Verification

| # | Category | Status | Evidence |
|---|----------|--------|----------|
| 1 | All 21 new subagent bodies exist | **PASS** | 7 system-lead + 8 planning-lead + 6 test-lead = 21 files verified at `src/aspis/data/catalog/agents/`. Frontmatter YAML valid; 7-section body structure. |
| 2 | All 3 leads delegate the 21 subagents | **PASS** | system-lead (10 delegates), planning-lead (11), test-lead (7) — 21 unique leaf names. Prose `## Delegation` section present in all 3 leads. |
| 3 | 12 scripts exist (catalog + deploy) | **PASS** | 6 planning + 5 research + 1 governance — all 12 file-pairs byte-identical between `src/aspis/data/catalog/scripts/...` and `.aspis/scripts/...` (verified by full-content + line-count check). |
| 4 | 7 templates exist | **PASS** | 6 new in `templates/planning/` + 1 reconciled `TEST_REPORT.md` pointer to existing `templates/review/test.md` (no duplicate). |
| 5 | Operating-protocol workflow exists (≥60 steps) | **PASS** | `.aspis/workflows/project-lead-operating-protocol.md` — 68 numbered steps confirmed (1-68), 8 sections. |
| 6 | dependency-audit skill exists & wired | **PASS** | SKILL.md at `src/aspis/data/catalog/skills/dependency-audit/SKILL.md` — 5 sections (Purpose, When to use, Procedure, Outputs, Anti-patterns). Referenced in planning-lead `skills:` frontmatter (line 63). |
| 7 | PreToolUse hook modules exist | **FAIL (FALSE PASS)** | T-044 claimed PASS with `deny_floor.py`, `pretool_secret_scan.py`, `protected_path.py` "all 3 pass AST parse". **None of the 3 files exist in any directory of the repo.** See §3 Finding F-1 (CRITICAL). |
| 8 | Use-case coverage matrix | **PARTIAL** | 73 of 73 originally-missing use cases now covered (per BUILD_REPORT §4). 3 documented BLOCKED items remain (governance hook, byte-parity, validate-runtime). |
| 9 | Cross-reference sweep | **PASS** | 0 unresolved skill refs; 0 unresolved delegate refs; 0 orphan delegates; 0 unresolved workflow refs. |
| 10 | Rule compliance | **MIXED — see §4** | R-003, R-004, R-006 honored. R-008 surface is real (T-045 filed) but module-side T-044 is not done. |
| 11 | BLOCKED items validation | **MIXED — see §5** | 2 of 3 BLOCKED items are legitimate (T-046 governance, byte-parity re-export). 1 BLOCKED is the symptom of T-044 false PASS (validate-runtime backfill) and is real but only part of the picture. |

---

## §2 — FR Coverage Matrix

### L0 — Green pytest gate (7 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-L0-001 (pytest exit 0) | **PARTIAL** | 369/369 non-env tests pass via `uv run pytest`; 2 env-blocked files documented (`test_bootstrap.py`, `test_gitcheck.py`) + 1 new env finding (`test_promotion.py::test_bootstrap_promotes_leads`). Documented as `BLOCKED: env`. |
| FR-L0-002 (evidence-driven fix) | **SATISFIED** | T-001a discovery report exists; T-001b fixed only confirmed failures. |
| FR-L0-003 (subprocess) | **SATISFIED** | All 8 confirmed failures fixed. |
| FR-L0-004 (model-tier) | **SATISFIED** | 6 model-tier tests pass after body model-tiers corrected. |
| FR-L0-005 (promotion logic) | **SATISFIED** | `test_all_promote_leads_are_present_and_flipped` passes after build-lead `mode: primary → subagent` correction. |
| FR-L0-006 (rule-layers) | **SATISFIED** | Assertion aligned with current 4-layer doc. |
| FR-L0-007 (ruff) | **SATISFIED** | Per B-L0-gate: ruff exits 0 on modified files. |

### L1 — Tier-B helper scripts (9 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-L1-001 (12 scripts exist) | **SATISFIED** | All 12 in catalog + deploy. |
| FR-L1-002 (deterministic, stdlib) | **SATISFIED** | Per B-L1-gate. |
| FR-L1-003 (AST parse) | **SATISFIED** | Per B-L1-gate; 12/12 PASS. |
| FR-L1-004 (--help exit 0) | **SATISFIED** | Per B-L1-gate; 12/12 PASS. |
| FR-L1-005 (byte-identical) | **SATISFIED** | Independently verified — 12/12 file-pairs identical. |
| FR-L1-006 (planning scripts location) | **SATISFIED** | `.aspis/scripts/planning/`. |
| FR-L1-007 (research scripts location) | **SATISFIED** | `.aspis/scripts/research/`. |
| FR-L1-008 (governance script location) | **SATISFIED** | `.aspis/scripts/system/validate-approvals.py`. |
| FR-L1-009 (debris removed) | **SATISFIED** | No `_tmp_f017_*.py` files found. |

### L2 — Skill + templates + workflow (10 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-L2-001 (dependency-audit SKILL.md) | **SATISFIED** | 5 sections, 130 lines. |
| FR-L2-002 (CLARIFICATION_LOG) | **SATISFIED** | 54 lines, valid frontmatter. |
| FR-L2-003 (RESEARCH_REQUEST) | **SATISFIED** | 49 lines, valid frontmatter. |
| FR-L2-004 (PLAN_OF_PLAN) | **SATISFIED** | 70 lines, valid frontmatter. |
| FR-L2-005 (DEPENDENCIES) | **SATISFIED** | 71 lines, valid frontmatter. |
| FR-L2-006 (SCOPE_ESTIMATE) | **SATISFIED** | 57 lines, valid frontmatter. |
| FR-L2-007 (MODE_DECISION) | **SATISFIED** | 79 lines, valid frontmatter. |
| FR-L2-008 (TEST_REPORT reconciled) | **SATISFIED** | Pointer file at `review/TEST_REPORT.md`; no duplicate. |
| FR-L2-009 (operating-protocol ≥60 steps) | **SATISFIED** | 68 steps confirmed. |
| FR-L2-010 (template pattern) | **SATISFIED** | All 7 have `type/category/version` frontmatter. |

### L3 — Leaf subagents (11 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-L3-001 (subagents exist) | **SATISFIED** | 21/21 files. |
| FR-L3-002 (7-section body) | **SATISFIED** | 32/33 follow the 7-section shape; bootstrap uses the documented transient-primary exception (codified in AGENT_BODY_STANDARD.md per T-047). |
| FR-L3-003 (11-field frontmatter) | **SATISFIED** | All 33 agents have the 11 base fields. Note: the 14 new agents also have `primary` + `summary` + `deny_floor`; the 7 new system-lead subagents do NOT. |
| FR-L3-004 (skill refs resolve) | **SATISFIED** | 0 broken refs. |
| FR-L3-005 (delegate refs resolve) | **SATISFIED** | 0 orphan delegates. |
| FR-L3-006 (deny floor) | **SATISFIED** | Only committer has `git commit*`; no agent has `git push*` or `bash: '*': allow`; webfetch/websearch restricted to system-lead + research-lead per spec. |
| FR-L3-007 (catalog-registered) | **SATISFIED** | All 33 discoverable. |
| FR-L3-008 (system-lead 7 at production depth) | **PARTIAL** | Bodies are at production depth in terms of content, but are missing `primary` + `summary` frontmatter fields that `validate-runtime --runtime all` requires. |
| FR-L3-009 (planning-lead 8 at production depth) | **SATISFIED** | All 8 have full 7-section bodies with `primary` + `summary` + `deny_floor`. |
| FR-L3-010 (test-lead 6 at MVP depth) | **SATISFIED** | All 6 with labs-fallback documented; all 6 have `primary` + `summary` + `deny_floor`. |
| FR-L3-011 (validate-runtime --runtime all) | **UNSATISFIED** | 19/33 agents fail (BLOCKED-3). |

### L4 — Hardening (6 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-L4-001 (PreToolUse hook modules + R-008 + settings.json on approval) | **UNSATISFIED** | Hook modules DO NOT EXIST (Finding F-1). R-008 request `REQ-F-018-001` is filed. `.claude/settings.json` does not reference the missing modules. |
| FR-L4-002 (every agent ≥2 edge cases) | **SATISFIED** | 33/33 agents have `## Edge Cases` section with ≥2 scenarios. |
| FR-L4-003 (byte-parity CLEAN) | **UNSATISFIED** | 9 drifted + 2 missing deploys (BLOCKED-2). |
| FR-L4-004 (export --dry-run exit 0) | **SATISFIED** | 97 actions, 0 missing, 0 skipped (per Gate 5 evidence). |
| FR-L4-005 (aspis doctor exit 0) | **UNVERIFIED** | Not independently re-runnable in this env; BUILD_REPORT does not include a clean `aspis doctor` PASS line. |
| FR-L4-006 (cross-runtime parity) | **SATISFIED** | Per T-048: verdict `not-present` (already fixed in F-017 commit `36ab7b5`). |

### Cross-cutting (6 FRs)

| FR | Status | Notes |
|----|--------|-------|
| FR-CC-001 (R-003 scripts before agents) | **SATISFIED** | L1 commits (147335a, 04f90ea, db3d977) precede L3 commits (7b69c27, 62e9623, b423d66). |
| FR-CC-002 (R-006 single source) | **SATISFIED** | Catalog is truth; bodies reference skills/delegates/workflows by name, no inline duplication. |
| FR-CC-003 (R-008 human gate) | **PARTIAL** | Governance subagent exists; R-008 request filed for settings.json. Module-side enforcement is NOT done (T-044 false PASS). |
| FR-CC-004 (R-004 committer-only) | **SATISFIED** | Verified via grep: only committer has `git commit*: allow`; no agent has `git push*`. |
| FR-CC-005 (every layer has hard exit gate) | **PARTIAL** | L0, L1, L2 gates green. L3 gate: validate-runtime 19/33 fail. L4 gate: T-044 false PASS, 2 legitimate BLOCKED. |
| FR-CC-006 (cost-of-change ≤3 files) | **SATISFIED** | Per BUILD_REPORT verification; subagent cost = 1 catalog file + 1 lead's frontmatter (+ optional referencing frontmatter). |

---

## §3 — SC Verification

| SC | Status | Notes |
|----|--------|-------|
| SC-L0-001 (pytest exit 0) | **MET** | 369/369 non-env tests pass; 3 env-blocked items documented. |
| SC-L0-002 (ruff) | **MET** | Per B-L0-gate. |
| SC-L1-001 (12 scripts AST/--help/smoke) | **MET** | 12/12 per B-L1-gate. |
| SC-L1-002 (byte-parity for 12) | **MET** | Independently verified. |
| SC-L1-003 (no _tmp_f017 debris) | **MET** | CLEAN. |
| SC-L2-001 (dependency-audit valid) | **MET** | 5 sections. |
| SC-L2-002 (7 templates exist) | **MET** | All 7 verified. |
| SC-L2-003 (operating protocol ≥60 steps) | **MET** | 68 steps. |
| SC-L3-001 (21+ subagents exist) | **MET** | 21/21. |
| SC-L3-002 (validate-runtime all 33) | **UNMET** | 19/33 fail. |
| SC-L3-003 (0 broken skill refs) | **MET** | 0 found. |
| SC-L3-004 (0 orphan delegates) | **MET** | 0 found. |
| SC-L3-005 (0 bash '*': allow) | **MET** | 0 found. |
| SC-L4-001 (PreToolUse hook modules in `.aspis/scripts/hooks/`, R-008 filed, settings.json on approval) | **UNMET** | Modules DO NOT EXIST (Finding F-1). |
| SC-L4-002 (every agent ≥2 edge cases) | **MET** | 33/33. |
| SC-L4-003 (byte-parity CLEAN) | **UNMET** | 11 drifted/missing. |
| SC-L4-004 (export --dry-run) | **MET** | 97 actions, 0 errors. |
| SC-L4-005 (aspis doctor) | **UNMET (per BUILD_REPORT §6, none of the 3 BLOCKED items cover doctor; BUILD_REPORT does not list a doctor PASS evidence line)** | Cannot be independently confirmed; risk that a fourth blocker exists. |
| SC-CC-001 (cost-of-change ≤3 files) | **MET** | Per BUILD_REPORT. |

**SC score: 14 MET, 4 UNMET, 1 UNVERIFIED.**

---

## §4 — Findings

### F-1 (CRITICAL) — T-044 false PASS; 3 PreToolUse hook modules do not exist

**File:** `BUILD_REPORT.md` §2 L4.A row, `B-L4-blocked.md` lines 16-23, `BUILD_REPORT.md` §6 BLOCKED-1.

**Claimed:** T-044 produced 3 PreToolUse hook modules at `.aspis/scripts/hooks/{deny_floor,pretool_secret_scan,protected_path}.py`, all passing AST parse. `B-L4-blocked.md` and `BUILD_REPORT.md` BLOCKED-1 both state "The 3 PreToolUse hook modules are authored and exist in the catalog" and "The hook modules (`deny_floor.py`, `pretool_secret_scan.py`, `protected_path.py`) are authored and tested."

**Verified:** All 3 files are **absent** from the entire repo. `glob **/deny_floor.py`, `**/pretool_secret_scan.py`, `**/protected_path.py` all return no matches. Only the existing 12 hook scripts (cleanup, commitmsg, gitignore, etc.) are in `.aspis/scripts/hooks/`. Only `runtime_guard.py` is wired in `.claude/settings.json` as the Claude PreToolUse hook.

**Impact:**
- FR-L4-001 is UNSATISFIED.
- SC-L4-001 is UNMET.
- The R-008 approval request `REQ-F-018-001` (`.aspis/state/approval-ledger.yaml`) references the 3 non-existent modules. The `module_refs:` list in the approval ledger is a list of phantom paths.
- B-L4-blocked.md tells the owner to verify by running `python .aspis/scripts/hooks/deny_floor.py --agent build-lead --tool "read: file"`. That command will fail (file not found).
- T-046 cannot meaningfully proceed: applying a `.claude/settings.json` hook entry that references non-existent files produces a broken Claude PreToolUse config (it will fail to invoke the hook at runtime).

**Why this matters beyond the missing file:** The BUILD_REPORT's T-044 status row says "PASS" with the `All 3 pass AST parse` evidence line. The §2 L4 summary row says "L4 — Hardening | **PASS** (3 BLOCKED)" and L4 verdict in §2 is "**PASS with 3 documented BLOCKED items**". This is a mischaracterization. A task that produced no deliverable cannot be PASS. Either T-044 should be marked not-done, or the task was never actually executed.

**Required fix:** Either (a) actually create the 3 hook modules with the documented purpose, or (b) correctly mark T-044 as not-done in the BUILD_REPORT, remove the false evidence lines, and remove the BLOCKED-1 entry that relies on the phantom modules.

### F-2 (HIGH) — BLOCKED-3 validate-runtime backfill is real, but root cause is broader

**File:** `B-L4-gate-sweep.md` §Gate 2.

**Verified:** 19/33 agents are missing `primary` and `summary` frontmatter fields. The 14 agents that have them are the 8 new planning-lead subagents + 6 new test-lead subagents. The 7 new system-lead subagents are missing the same fields (along with the 12 pre-existing agents).

**Impact:** FR-L3-011 and SC-L3-002 are UNMET. The validate-runtime gate cannot exit 0. The L4 gate sweep marks this as BLOCKED with the resolution path: "Requires systematic addition of `primary: true/false` and `summary: <description>` to all 19 agent frontmatter blocks." This is a legitimate BLOCKED, not a false positive.

**Note on the BUILD_REPORT's framing:** BUILD_REPORT §6 BLOCKED-3 says "These fields were added to the agent body standard after the 19 agents were authored." That is true. But the BUILD_REPORT also marks T-043 L3 exit gate as PASS — and the L3 gate's "33 pass, 0 fail" claim was for the **11-field** standard, not the **13-field** standard the validate-runtime now demands. The two are not contradictory, but the BUILD_REPORT could be clearer that "33 pass" at T-043 was an 11-field check, and a subsequent 13-field check is what produced BLOCKED-3.

**Required fix:** A scripted backfill of `primary: false` (or `true` for the 5 primaries) and `summary: <description>` to all 19 agents. The 14 new agents use `description` as `summary`; the same pattern works for the 19 older ones. This is mechanical, well-scoped, and could be a 30-minute task.

### F-3 (MEDIUM) — BLOCKED-2 byte-parity drift is real and pre-dates F-018

**File:** `B-L4-gate-sweep.md` §Gate 3.

**Verified:** The 5 context scripts (`_common.py`, `build_state.py`, `record_changes.py`, `build_registry.py`, plus `build_code_map.py` per BUILD_REPORT) and 5 hook scripts (`_config.py`, `cleanup.py`, `gitignore.py`, `precommit.py`, `runtime_guard.py`) in `.aspis/scripts/` are older, smaller versions of files that have grown in `src/aspis/data/catalog/scripts/`. Independent verification on `_common.py`: catalog = 168 lines, deploy = 84 lines; content differs (catalog has `import json, re`; deploy doesn't). The 2 missing deploys (`findings.py`, `session_start.py`) are also confirmed absent from `.aspis/scripts/hooks/`.

**Impact:** This is operationally a one-command fix (`aspis export --apply`). Per BUILD_REPORT §6 BLOCKED-2, Gate 5 confirms export planning works (97 actions, 0 errors). The drift does not block the feature from shipping but the build should not be marked PASS-with-this-condition without scheduling the export.

**Required fix:** Run `aspis export --apply` once. Cost: 1 command, ~30 seconds. Not a code change.

### F-4 (LOW) — `findings.py` and `session_start.py` are missing from deploy but listed in catalog

**File:** `src/aspis/data/catalog/scripts/hooks/{findings.py,session_start.py}` exist; `.aspis/scripts/hooks/{findings.py,session_start.py}` do not.

**Impact:** The runtime_guard.py script imports `findings` and `session_start` is referenced from the runtime. If the runtime runs (e.g., the existing Claude PreToolUse hook fires during a Claude session), the import of `findings` will fail. This is a live runtime defect, not just a byte-parity issue.

**Required fix:** Same as F-3 — `aspis export --apply`. Listed separately because it has a runtime-import impact, not just a check-tool impact.

### F-5 (LOW) — Two different frontmatter formats coexist in the 33-agent catalog

**File:** The 14 new L3 subagents (8 planning + 6 test-lead) use a compressed, single-line `bash: {...}` style and have `deny_floor:` + `summary:` + `primary:`. The 7 new system-lead subagents and the 12 pre-existing agents use the verbose multi-line `bash:\n  "*": deny` style without `deny_floor` / `summary` / `primary`.

**Impact:** Validators that read `deny_floor` will get a NULL value for 19 of 33 agents. Future work that wants to leverage `deny_floor` for runtime enforcement (e.g., a deny-floor verifier script) will see 19 of 33 agents as "missing" the field. Also creates a maintenance hazard — the format split is invisible to a casual reader.

**Required fix:** Pick one canonical format (the verbose multi-line style, which is the more common one and easier to diff), and convert the 14 new agents to match. Or, in the alternative, document the dual-format as intentional and ensure the validator handles both consistently.

### F-6 (LOW) — The 3 BLOCKED items do not include a `doctor` evidence line

**File:** `BUILD_REPORT.md` §5 L4 Gate Evidence and §6 BLOCKED items.

**Observation:** SC-L4-005 requires `aspis doctor` to exit 0 with no FAIL findings. The L4 gate sweep report lists 6 gates (pytest, validate-runtime, byte-parity, validate-index, export --dry-run, tree check). `aspis doctor` is not in that list. The §2 L4 verdict says "PASS (3 BLOCKED)" but does not claim doctor PASS.

**Impact:** This may be that doctor is not a required gate, only an SC. But SC-L4-005 is in the SPEC and the BUILD_REPORT does not claim MET. This is either a missing gate or a missing evidence line.

**Required fix:** Run `aspis doctor` and either add the evidence line to the BUILD_REPORT or document why doctor is excluded from the L4 gate sweep.

### F-7 (INFO) — `aspis doctor` evidence unverified

**File:** SC-L4-005.

**Observation:** This reviewer cannot independently execute `aspis doctor` in the current environment. The bash tool is restricted; only file-read tools are available. The SC has neither a PASS line in the BUILD_REPORT nor independent verification from this review.

**Impact:** Cannot block on this — the SC is also not claimed MET in the BUILD_REPORT. Documented for completeness.

---

## §5 — BLOCKED-Item Validation

### BLOCKED-1: T-046 — PreToolUse hook apply to `.claude/settings.json`

**Verdict: NOT LEGITIMATE in current form. The blocker is a side effect of F-1 (T-044 false PASS).**

The T-046 dependency on T-044 is real, but T-044's claimed "PASS" is false (F-1). Without the 3 hook modules existing, T-046 has nothing to apply. The R-008 request `REQ-F-018-001` is filed and properly structured (status: pending, approver: owner), but its `module_refs:` list points at 3 paths that contain no files.

The correct interpretation: BLOCKED-1 is a real governance gate that has not been tripped yet (correct), but it sits on top of an undocumented gap (T-044 was never actually executed). The owner cannot meaningfully approve and apply this hook configuration because the hooks it would invoke do not exist.

**Recommended resolution:** See F-1 — create the 3 modules, or correctly mark T-044 as not-done and reframe BLOCKED-1 as "hook modules pending + governance pending".

### BLOCKED-2: Byte-parity DRIFT — 9 drifted + 2 missing deploys

**Verdict: LEGITIMATE, mechanical fix.**

The drift is real (independently verified for `_common.py`: 168 vs 84 lines, different content). The fix is operational, not a code change. `aspis export --apply` resyncs everything. The BLOCKED framing in BUILD_REPORT §6 is accurate; the owner can clear this with a single command.

The 2 missing deploys (`findings.py`, `session_start.py`) have a separate impact (F-4): they are imported at runtime by `runtime_guard.py`, so without them the existing Claude PreToolUse hook will fail to import if/when it fires.

### BLOCKED-3: validate-runtime — 19 agents missing `primary`/`summary`

**Verdict: LEGITIMATE, real systemic gap.**

Confirmed via grep: 14 of 33 agents have `primary:` and `summary:` (all 14 are the new L3 subagents). 19 of 33 do not (12 pre-existing + 7 new system-lead). The 7 new system-lead subagents are the most surprising — they were built in the same feature (commits `7b69c27`) but use the older frontmatter format. This is a backfill the build should have done, or should have flagged as a T-043 scope question (it was within the T-043 gate's purview but was missed).

The fix is well-scoped and mechanical. Resolution: scripted batch update.

### Re-framing of "validate-runtime 19 missing fields — real or false positive?"

The question in the original task asks if this is a real finding or a false positive. **It is real.** Two confirming signals:

1. The 14 new agents that DO have the fields use the exact same `primary: false` + `summary: <description>` pattern. The 19 missing agents would each get the same 2 lines added.
2. The B-L3-gate report at `Review/B-L3-gate.md` confirms "11-field YAML frontmatter (name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope)" — i.e., the 11-field check that T-043 ran is NOT the same as the 13-field check that T-049 ran. T-043 is technically correct ("33 pass, 0 fail" for 11 fields) but does not anticipate T-049's stricter check.

**It is a real finding, not a false positive.**

---

## §6 — Rule Compliance

| Rule | Compliance | Notes |
|------|------------|-------|
| R-001 (scope) | OK | All work within declared scope. |
| R-003 (scripts before agents) | **OK** | L1 commits (147335a, 04f90ea, db3d977) precede L3 commits (7b69c27, 62e9623, b423d66). Ordering enforced. |
| R-004 (committer-only) | **OK** | Only committer has `git commit*: allow`; no agent has `git push*`. |
| R-006 (single source) | **OK** | Catalog is truth. Bodies reference, never duplicate, content. |
| R-008 (human gate) | **PARTIAL** | Governance subagent exists. R-008 request filed (REQ-F-018-001). But T-044 false PASS means the enforcement surface (hook modules) was never created. The R-008 gate is correctly designed; the underlying work is not done. |
| Deny floor | **OK** | Verified across all 33 agents via grep: only committer has `git commit*`; no `git push*`; `webfetch: allow` only on system-lead and research-lead; `websearch: allow` only on research-lead; no `bash: '*': allow` on any agent. |
| `no-edit-runtime` | **OK** | Only the committer has write/edit on git operations; runtime paths are restricted to system-lead. |
| `enforcement: warn` default | **OK** | D-010 honored. The runtime_guard.py explicitly checks for `enforcement: block` and only blocks then. |

---

## §7 — Use-Case Coverage Status

The use-case-coverage matrix in `Research/use-case-coverage.md` lists 162 use cases across 18 categories. The BUILD_REPORT §4 reports:

- Before F-018: 86 covered, 6 partial, 70 missing (162 total)
- After F-018: 159 covered, 0 partial, 0 missing, 3 BLOCKED (162 total)

Independent verification:
- 73 originally-missing use cases are now covered (per BUILD_REPORT).
- The 3 BLOCKED items correspond to: governance-hook (R-008 / T-046), byte-parity re-export, validate-runtime backfill.

**Coverage score: 159/162 covered (98.1%).** The 3 BLOCKED items are documented in §5 above and align with the L4 gate findings.

---

## §8 — Cross-Reference Sweep

| Check | Result | Notes |
|-------|--------|-------|
| Unresolved skill refs across 33 agent bodies | **0** | Verified — all `skills:` values resolve to existing skills. |
| Unresolved delegate refs | **0** | Verified — all 21 unique leaf names exist as catalog agent files. |
| Unresolved workflow refs | **0** | Operating protocol exists; `system.md` reference in system-lead body remains broken (pre-F-018, gap-collation §5.1 item 1, deferred). |
| Unresolved template refs | **0** | All 7 templates exist. |

**Note:** system-lead.md line 90 references `.aspis/workflows/system.md` which does not exist. This is a pre-existing broken reference (gap-collation §5.1 item 1, marked as "broken-ref HIGH" but not in F-018 scope). It is not new in F-018 and not a F-018 responsibility, but it is a real broken reference in the F-018 deliverable. Should be flagged for F-019.

---

## §9 — Cost-of-Change Check (FR-CC-006)

Verified: Each new subagent adds at most 3 files (the new catalog file, the owning lead's frontmatter, and at most 1 referencing frontmatter). The actual cost for F-018 was:
- 21 new agent files (catalog)
- 3 lead frontmatter updates (system-lead, planning-lead, test-lead)
- 0 referencing frontmatter updates needed
- 0 deployment changes for subagents (catalog source only; deploy regenerates on export)

**Per-agent cost: 1 file (the catalog file).** Well under the 3-file ceiling. **SATISFIED.**

---

## §10 — Verdict

**CHANGES REQUIRED.**

### Blocking issues (must fix before re-review)

1. **F-1 (CRITICAL): T-044 false PASS.** Either create the 3 PreToolUse hook modules (`deny_floor.py`, `pretool_secret_scan.py`, `protected_path.py`) with documented purpose, OR correctly mark T-044 as not-done in the BUILD_REPORT, remove the false evidence lines, and reframe BLOCKED-1. The current BUILD_REPORT claims deliverables exist that do not.
2. **F-2 (HIGH): BLOCKED-3 validate-runtime backfill.** Add `primary` and `summary` to the 19 missing agent frontmatters. Mechanical, scripted, ~30 min.

### Non-blocking but should fix before ship

3. **F-3 (MEDIUM): BLOCKED-2 byte-parity drift.** Run `aspis export --apply` to resync deploy.
4. **F-4 (LOW): 2 missing hook deploys.** Resolved by the same export.
5. **F-6 (LOW): Missing `aspis doctor` evidence line.** Either run doctor and document, or document why it's not in the L4 gate.

### Acceptable as-is

- F-5 (dual frontmatter format): style/maintenance, not a blocker.
- F-7 (`aspis doctor` unverified): bounded by F-6.
- Use-case coverage 159/162 (98.1%): within the spec's "close all 70 missing + 6 partial" target, with 3 documented BLOCKED items.

### Final assessment

The L0, L1, L2 layers are well-executed. The L3 layer is largely correct except for the systemic validate-runtime backfill (F-2). The L4 layer has a serious integrity problem: the BUILD_REPORT claims deliverables that do not exist (F-1). This is the most important finding — not because the work itself is bad, but because the report misrepresents what was done, and the misrepresentation affects everything downstream (the BLOCKED-1 framing, the owner-action paths, the L4 "PASS" verdict).

**This feature cannot ship as-is.** The path to ship is straightforward: fix F-1 (either actually create the 3 modules, or correct the BUILD_REPORT) and F-2 (scripted backfill). Both are well-scoped, well-understood tasks with clear resolution paths. After both fixes and a re-review, F-018 will be APPROVE.

---

*Reviewer: MiniMax-M3 (Reviewer role, independent, fresh context)*
*Review date: 2026-06-28*
*Reviewed against: SPEC.md (228 lines), TASKS.md (399 lines), BUILD_REPORT.md (514 lines), use-case-coverage.md (341 lines), gap-collation.md (700+ lines), 33 agent files, 7 templates, 12 scripts, 1 skill, 1 workflow, 3 review reports (B-L0/L1/L2/L3/L4).*
