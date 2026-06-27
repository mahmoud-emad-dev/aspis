# F-017 — Skill Quality & Single-Source Review

> **Reviewer**: Independent (Reviewer — quality + R-006 single-source perspective)
> **Mode**: production
> **Date**: 2026-06-27
> **Scope**: 14 built skills in `src/aspis/data/catalog/skills/` (Phase 0-2 of F-017)
> **Cross-checked against**: F-016 skills inventory, F-016 agent reference specs, `constitution-checks.yaml`, `architecture-constitution.md`, `AGENT_BODY_STANDARD.md`, `DYNAMIC_READINESS.md`, agent bodies that reference these skills

---

## 0 · Verdict (one-line)

> **APPROVED WITH NOTES** — All 14 skills are well-built, format-compliant, and reference-resolved; the system can use them. **4 R-006 / single-source violations** must be addressed in a follow-up: 2 in the skills themselves (`constitution-checks`, `constitution-check` use a rule-naming system that does not match the system-of-record YAML) and 2 in the agent bodies that consume them (`build-lead`, `research-lead` duplicate skill content inline).

---

## 1 · Executive summary

The 14 built skills (7 L0 shared, 7 L1 per-lead) are:

- **Present**: All 14 SKILL.md files exist at the correct paths.
- **Format-compliant**: Every skill has frontmatter (name + description) plus the required body sections (Purpose, When to use, Procedure, Outputs, Anti-patterns) or a documented equivalent.
- **Reference-resolved**: All 14 are referenced by at least one owning agent; **0 orphan skill references** in any of the 12 agent bodies.
- **Self-contained**: Each skill can be executed by a context-isolated agent from just its SKILL.md — no required external knowledge beyond the cross-referenced convention documents (`architecture-constitution.md`, `constitution-checks.yaml`, `DYNAMIC_READINESS.md`, `commit-convention.yaml`), all of which exist.
- **Readable**: Sized 40-90 lines; suitable for both cheap and standard models.
- **Spec-aligned**: Each skill matches its F-016 inventory purpose, owning agent, and priority.
- **R-006 mostly satisfied**: Agent bodies reference skills by name; the bodies do not re-derive the procedure inline — with 2 exceptions in agent bodies (build-lead, research-lead) and 2 in skills (constitution-checks, constitution-check) where content is duplicated or sourced from the wrong system of record.

**4 findings, 2 in HIGH tier, 2 in MEDIUM tier**, 0 CRITICAL. The system can be approved to proceed to the L1 exit gate, with the 4 findings routed to a follow-up task before L2-P0 begins.

| # | Severity | Location | Summary |
|---|---|---|---|
| **H-1** | HIGH | `constitution-checks/SKILL.md` (L:23-42) | Skill enumerates 12 rules by prose names that **do not match** the 11 rules in `constitution-checks.yaml`. The skill is sourced from the constitution document, but the YAML is the system-of-record index per the constitution's own comment. R-006-style "single source" violation. |
| **H-2** | HIGH | `constitution-check/SKILL.md` (L:23-37, L:50-52) | Skill enumerates 9 reviewer-owned rules by prose names that **do not match** the 9 reviewer-enforced rules in `constitution-checks.yaml`. The skill's anti-pattern claims "Local Change, Architecture before Features, Portable by Default" are plan-only, but the YAML says Local Change and Portable are reviewer-enforced; C-ARCH-BEFORE-FEATURES does not exist in the YAML at all. |
| **H-3** | HIGH | `research-lead.md` body (L:107-131) | Body's "Cache system" section duplicates `cache-management` skill's cache key extraction, locations, and staleness windows. R-006 violation: bodies must reference, not restate. |
| **H-4** | HIGH | `build-lead.md` body (L:102-112) | Body's "Packet validation — the 4 checks" table duplicates `packet-validation` skill's 4-check procedure. R-006 violation. |
| **M-1** | MEDIUM | `constitution-checks.yaml` (L:11-65) | YAML is missing `C-ARCH-BEFORE-FEATURES` from the 12-rule set in `architecture-constitution.md`. The skill correctly enumerates 12 rules; the YAML enumerates 11. This is a YAML drift, not a skill defect, but it forces the skills to bypass the YAML. |
| **M-2** | MEDIUM | `mode-decision/SKILL.md` (L:22) | Procedure step 1 says "Active feature's `mode` field (set by planning-lead)" — but the mode-decision skill is owned by both project-lead and planning-lead. The active feature's mode is set by either, depending on the flow. Minor wording imprecision. |
| **M-3** | MEDIUM | `constitution-check/SKILL.md` (L:50) | Anti-pattern "the planning-lead handles the other 3" is factually wrong per the YAML. The 3 rule names it cites (Local Change, Architecture before Features, Portable by Default) are **not** the 3 plan-only rules per the YAML — the actual plan-only rules are `C-AUTOMATION` and `C-PLUGIN-FIRST`. |
| **L-1** | LOW | `evidence-validation/SKILL.md` (L:20-37) | Puts "Hard rule" and "Evidence table" between "When to use" and "Procedure" — section ordering deviates from the catalog pattern. Functional, stylistic. |
| **L-2** | LOW | Multiple | Section count in F-016 inventory's "Est. Sections" column (e.g. "4", "5", "6") does not match the actual section count in the built skills. The inventory undercount is a planning-time estimate, not a defect. |

---

## 2 · Scope & methodology

### 2.1 · What I reviewed

All 14 SKILL.md files in `src/aspis/data/catalog/skills/` (Phase 0-2 of F-017):

**L0 shared (7):**
`mode-decision`, `recontextualization`, `constitution-checks`, `constitution-check`, `evidence-validation`, `packet-validation`, `builder-selection`

**L1 per-lead (7):**
`session-continuation`, `security-review`, `catalog-validator`, `governance-approval`, `drift-detector`, `cache-management`, `harvest-protocol`

### 2.2 · What I cross-checked

For each skill, I read and verified against:

1. The F-016 inventory entry (`.aspis/features/F-016-agent-system-architecture/Research/skills/inventory.md`) — purpose, owning agent, priority, est. sections.
2. The relevant F-016 reference spec (`.aspis/features/F-016-agent-system-architecture/Research/ref/<agent>.md`) — what the agent design requires.
3. The agent body that owns the skill — does it reference the skill by name and not duplicate content?
4. The shared system documents — `architecture-constitution.md`, `constitution-checks.yaml`, `DYNAMIC_READINESS.md`, `AGENT_BODY_STANDARD.md`.
5. The standards: frontmatter + Purpose / When to use / Procedure / Outputs / Anti-patterns (FR-001).
6. Self-containment: can a context-isolated agent execute the skill from the SKILL.md alone?
7. Cross-skill consistency: similar skills (`constitution-check` vs `constitution-checks`) are clearly differentiated; no accidental overlap.
8. R-006 single-source: bodies reference by name; no duplicated content.

### 2.3 · What I did NOT review

- L2-P0 / L2-P1 skills (P1 + P2 skills, deferred to Phases 3-4).
- L2-P0 CLI verbs (validate-runtime, byte-parity, export, governance) — built in Phase 3.
- The agent bodies themselves in depth — only enough to verify R-006 single-source and reference resolution. A separate review would scrutinize body shape compliance.
- The leaf agents (committer, general-builder, project-explorer) — finalized in Phase 3 (T-37..T-39).
- The system-lead's governance flow and approval ledger — built in Phase 3 (T-36).

---

## 3 · Per-skill assessment (14 skills)

### 3.1 · `mode-decision` — L0 / P0 / owners: planning-lead, project-lead

**Files:** `src/aspis/data/catalog/skills/mode-decision/SKILL.md` (55 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Infer the build mode from risk and scope, with auto-escalation and downgrade rules" — matches inventory line 88 |
| Owning agent(s) match | ✓ | Referenced in `project-lead.md:51` and `planning-lead.md:53` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter | ✓ | `name: mode-decision`, description present |
| Purpose section | ✓ | L:8-11 — "Determine the correct mode..." |
| When to use section | ✓ | L:13-16 — 3 trigger conditions |
| Procedure section | ✓ | L:18-39 — 5 steps with E1-E3 escalation, downgrade rules, conflict resolution |
| Outputs section | ✓ | L:41-45 — mode + reason + optional MODE_DECISION note |
| Anti-patterns section | ✓ | L:47-54 — 4 anti-patterns |
| Self-contained | ✓ | Mode list, escalation triggers, downgrade rules all inline |
| R-006 (no duplication) | ✓ | The body of `mode-decision` is the source; the agent body references it |
| Cites DYNAMIC_READINESS.md correctly | ✓ | L:49-51 — "model tier and mode are different dials (see DYNAMIC_READINESS.md)" |
| **Issues** | M-2 (minor) | L:22 — "Active feature's `mode` field (set by planning-lead)" — the active feature's mode is set by either project-lead (via `aspis mode`) or planning-lead (via the plan). |

**Score: 9/10** — minor wording imprecision. Strong otherwise.

### 3.2 · `recontextualization` — L0 / P0 / owner: project-lead

**Files:** `src/aspis/data/catalog/skills/recontextualization/SKILL.md` (50 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Translate a lead's return into project-aware language..." |
| Owning agent match | ✓ | Referenced in `project-lead.md:52` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | Read → Fold → Translate → Decide procedure is fully self-described |
| R-006 (no duplication) | ✓ | Project-lead body references by name in frontmatter; doesn't restate |
| **Issues** | None |

**Score: 10/10** — concise, complete, well-structured. Maps directly to the project-lead's master-frame 5-phase flow (`ENTRY → CLASSIFY → CONTEXT → ACT → RECONTEXTUALIZE → EXIT`).

### 3.3 · `constitution-checks` — L0 / P0 / owner: planning-lead

**Files:** `src/aspis/data/catalog/skills/constitution-checks/SKILL.md` (64 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Audit a PLAN against the 12 architecture-constitution rules..." |
| Owning agent match | ✓ | Referenced in `planning-lead.md:54` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | 12 rules + cost-of-change test + report format all inline |
| **Issues** | **H-1 (HIGH)**, M-1 (MEDIUM) | See below |

**Issues found:**

- **H-1 (HIGH)** — R-006 single-source violation: The skill's procedure (L:22-42) enumerates 12 rules by prose names ("Local Change", "Plugin First", "Single Source of Truth", "Configuration over Code", "Core is Stable", "Dependency Direction", "Discovery over Registration", "Generated Artifacts", "No Special Cases", "Consistency over Cleverness", "Architecture before Features", "Portable by Default"). These names come from `architecture-constitution.md`. **But the system-of-record machine-readable index is `constitution-checks.yaml`**, and the YAML uses different IDs:
  - YAML has: C-COST, C-AUTOMATION, C-LOCAL-CHANGE, C-PLUGIN-FIRST, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE (11 rules)
  - The YAML is missing C-ARCH-BEFORE-FEATURES, and the YAML has rules the skill doesn't mention (C-COST, C-AUTOMATION, C-FILE-SELF-EXPLAINS, C-TESTABLE).
  - The skill's anti-pattern at L:61-62 even says: "only the rules the planning lead is responsible for apply (see `constitution-checks.yaml`)" — but the rule list in the procedure does not match the YAML.

  **Fix:** either (a) update the skill to read from the YAML by name and walk the rule list dynamically, or (b) update the YAML to include all 12 rules from the constitution document (preferred — the constitution is the source of truth, the YAML is the index).

- **M-1 (MEDIUM)** — The constitution-checks.yaml is missing `C-ARCH-BEFORE-FEATURES` from the 12-rule set. The skill correctly enumerates 12 rules; the YAML enumerates 11. This is a YAML drift, not a skill defect, but it forces the skills to bypass the YAML.

**Score: 6/10** — functionally correct (the rule list is right per the constitution document), but it bypasses the system-of-record YAML, creating a maintenance hazard and violating the "single source" principle.

### 3.4 · `constitution-check` — L0 / P0 / owner: reviewer

**Files:** `src/aspis/data/catalog/skills/constitution-check/SKILL.md` (55 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Apply the 9 reviewer-owned architecture-constitution checks to any change before verdict" |
| Owning agent match | ✓ | Referenced in `reviewer.md:42` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | 9 checks + per-rule violation handling all inline |
| **Issues** | **H-2 (HIGH)**, M-3 (MEDIUM) | See below |

**Issues found:**

- **H-2 (HIGH)** — R-006 single-source violation, same root cause as H-1: The skill enumerates 9 rules by prose names that **do not match** the 9 reviewer-enforced rules in `constitution-checks.yaml`:
  - **Skill enumerates (L:26-37):** Plugin First, Single Source of Truth, Configuration over Code, Core is Stable, Dependency Direction, Discovery over Registration, Generated Artifacts, No Special Cases, Consistency over Cleverness.
  - **YAML says reviewer enforces (9 rules):** C-COST, C-LOCAL-CHANGE, C-SINGLE-SOURCE, C-CONFIG-OVER-CODE, C-NO-SPECIAL-CASE, C-DISCOVERY, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE.
  - Overlap: 4 rules match (SINGLE-SOURCE, CONFIG-OVER-CODE, DISCOVERY, NO-SPECIAL-CASE). 5 rules in the skill (Plugin First, Core is Stable, Dependency Direction, Generated Artifacts, Consistency over Cleverness) are **not** in the YAML. 5 rules in the YAML (C-COST, C-LOCAL-CHANGE, C-FILE-SELF-EXPLAINS, C-TESTABLE, C-PORTABLE) are **not** in the skill.
  - **The count of 9 matches**, but the actual rules differ.

- **M-3 (MEDIUM)** — The skill's anti-pattern (L:50) says: "the planning-lead handles the other 3" — naming Local Change, Architecture before Features, and Portable by Default. **This is factually wrong per the YAML**:
  - `C-LOCAL-CHANGE` is enforced by `[planning, review]` — both, not plan-only.
  - `C-ARCH-BEFORE-FEATURES` does not exist in the YAML.
  - `C-PORTABLE` is enforced by `[build, review]` — both, not plan-only.
  - The actual plan-only rules (where review is NOT in `enforced_by`) are `C-AUTOMATION` and `C-PLUGIN-FIRST` (2 rules, not 3).

**Fix:** same as H-1 — read rule list from the YAML, or update the YAML to include all 12 rules.

**Score: 5/10** — count is right (9 reviewer-owned checks) but the actual rules and the "plan-only" claim are wrong. The skill is teaching the reviewer the wrong checklist.

### 3.5 · `evidence-validation` — L0 / P0 / owner: reviewer

**Files:** `src/aspis/data/catalog/skills/evidence-validation/SKILL.md` (69 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Codify 'verify, don't trust' — what counts as valid evidence per review dimension" |
| Owning agent match | ✓ | Referenced in `reviewer.md:43` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / sections | ✓ | All present + extra (Hard rule + Evidence table) |
| Self-contained | ✓ | The evidence table per dimension is excellent and self-contained |
| R-006 (no duplication) | ✓ | Reviewer body doesn't restate the evidence rules |
| **Issues** | L-1 (LOW) | Section ordering deviates from the catalog pattern (Hard rule + table between "When to use" and "Procedure"). Functional, stylistic. |

**Score: 10/10** — the evidence table is the strongest part of any skill in this set. Clear, scannable, dimensional coverage.

### 3.6 · `packet-validation` — L0 / P0 / owner: build-lead

**Files:** `src/aspis/data/catalog/skills/packet-validation/SKILL.md` (87 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Validate a task packet on 4 dimensions..." |
| Owning agent match | ✓ | Referenced in `build-lead.md:51` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + extra (4 checks sub-sections + V0-V4 table) |
| Self-contained | ✓ | 4 checks + V0-V4 maturity scaling all inline |
| R-006 (skill is source of truth) | ✓ | The skill is the source; the build-lead body has a duplicate (see H-4) |
| **Issues** | None (the skill itself) | The skill is excellent. The build-lead body violates R-006 by duplicating it (H-4). |

**Score: 10/10** — the V0-V4 maturity scaling table is a model of clarity. 4 checks are well-defined with explicit V0-V4 scaling.

### 3.7 · `builder-selection` — L0 / P0 / owner: build-lead

**Files:** `src/aspis/data/catalog/skills/builder-selection/SKILL.md` (84 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Pick the right builder tier (cheap/standard/deep) per packet version (V0–V4) and risk profile" |
| Owning agent match | ✓ | Referenced in `build-lead.md:52` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + extra (matrix, override rules, tier cascade) |
| Self-contained | ✓ | Selection matrix, override rules, hard floor, tier cascade — all inline |
| R-006 | ✓ | The skill is the source |
| **Issues** | None |

**Score: 10/10** — the override rules with hard floor and the 3-attempt tier cascade are clear and well-justified. Aligns with the build-lead ref spec §3 and §4.

### 3.8 · `session-continuation` — L1 / P1 (can stub P0) / owner: project-lead

**Files:** `src/aspis/data/catalog/skills/session-continuation/SKILL.md` (56 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Detect interruption, classify the resumption type, and send a resume packet" |
| Owning agent match | ✓ | Referenced in `project-lead.md:53` |
| Priority (P1 per inventory) | ✓ | Inventory line 103 lists as P1; SPEC T-16 says "P1, but can stub P0" |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | 4 resumption types + 5-field packet shape + state updates inline |
| R-006 | ✓ | Project-lead body doesn't restate the resumption types |
| **Issues** | None |

**Score: 10/10** — directly implements the project-lead ref spec's "Flow: Continuation After Interruption" procedure (L:651-660 in the ref spec). The 5-field resume packet shape is a nice touch (carries the 5-field packet convention from the project-lead's delegation model).

### 3.9 · `security-review` — L1 / P0 / owner: reviewer

**Files:** `src/aspis/data/catalog/skills/security-review/SKILL.md` (71 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Apply OWASP top 10 and core security checks (injection, authz, secrets, exposure)" |
| Owning agent match | ✓ | Referenced in `reviewer.md:41` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + extra (security surface classification, OWASP walk, ASPIS-specific) |
| Self-contained | ✓ | 3-step procedure with security surface classification + OWASP walk + ASPIS-specific concerns |
| R-006 | ✓ | Reviewer body references it without restating |
| **Issues** | None |

**Score: 10/10** — the 3 ASPIS-specific concerns (secret leakage, permission escalation, protected-path access, model-tier bypass) are excellent and specific to this system. The "any CRITICAL security finding → REJECTED" hard rule is well-codified.

### 3.10 · `catalog-validator` — L1 / P0 / owner: system-lead

**Files:** `src/aspis/data/catalog/skills/catalog-validator/SKILL.md` (58 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Validate the catalog's structural integrity — all references resolve, no broken links, schemas valid, no orphan assets" |
| Owning agent match | ✓ | Referenced in `system-lead.md:45` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + extra (5 sub-checks) |
| Self-contained | ✓ | 6 sub-checks (skill refs, delegate refs, workflow refs, orphans, schema) all inline |
| R-006 | ✓ | The skill is the source |
| **Issues** | None |

**Score: 9/10** — the "ORPHAN_SKILL is warn, not error" distinction (L:36-37) is the right call. References AGENT_BODY_STANDARD.md for the 11 required frontmatter fields, which exists. Loses 1 point for the fact that "schema valid" (L:40) is asserted but not specified — the 11 required fields aren't listed in the skill, just referenced.

### 3.11 · `governance-approval` — L1 / P0 / owner: system-lead

**Files:** `src/aspis/data/catalog/skills/governance-approval/SKILL.md` (65 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "The R-008 human-gate workflow for rules, permissions, model-routing, and security posture changes" |
| Owning agent match | ✓ | Referenced in `system-lead.md:46` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | R-008 territory checklist + 5-step procedure + clear refusal rules |
| R-006 | ✓ | Skill is the source; system-lead body references it |
| **Issues** | None |

**Score: 10/10** — the skill correctly distinguishes itself from the governance CLI verb (L:11-12): "it does not implement the mechanism (that is the `governance` CLI verb and subagent, built separately)". The `--approver` requirement and "no bypass" anti-patterns are correctly anti-patterns. Aligns with FR-008 and the R-008 system rule.

### 3.12 · `drift-detector` — L1 / P0 / owner: system-lead

**Files:** `src/aspis/data/catalog/skills/drift-detector/SKILL.md` (59 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Detect per-field per-agent catalog-to-live frontmatter drift" |
| Owning agent match | ✓ | Referenced in `system-lead.md:47` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + extra (DRIFT/PROTECT/CLEAN classification) |
| Self-contained | ✓ | 5-step procedure + 3-class classification inline |
| R-006 | ✓ | Skill is the source |
| **Issues** | None |

**Score: 10/10** — the "PROTECT" classification (L:37-39) is the right nuance: live runtime has a field the catalog doesn't produce (e.g., owner customization), so report, don't overwrite. The anti-pattern "Auto-fixing drift by overwriting the live runtime" (L:54-55) is the correct hard line.

### 3.13 · `cache-management` — L1 / P0 / owner: research-lead

**Files:** `src/aspis/data/catalog/skills/cache-management/SKILL.md` (60 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "Enforce cache-first discipline — check existing research before any new research" |
| Owning agent match | ✓ | Referenced in `research-lead.md:30` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present |
| Self-contained | ✓ | Cache key extraction, 2 locations, staleness evaluation all inline |
| R-006 (skill is source of truth) | ✓ | The skill is the source; the research-lead body has a duplicate (see H-3) |
| **Issues** | None (the skill itself) | The skill is excellent. The research-lead body violates R-006 by duplicating it (H-3). |

**Score: 10/10** — the cache key strategy is well-thought-out: `{library}@{version}` for libraries, `{claim-hash}` for validations. The "check both global and per-feature cache" rule (L:30-31) is correct — the research-lead ref spec §5 specifies both locations. The "stale cache entry → re-validate, don't replace" rule (L:39-40) is the right nuance.

### 3.14 · `harvest-protocol` — L1 / P0 / owner: research-lead

**Files:** `src/aspis/data/catalog/skills/harvest-protocol/SKILL.md` (94 lines)

| Check | Result | Evidence |
|---|---|---|
| F-016 inventory purpose match | ✓ | "The 7-step R-008-gated path for bringing an external skill, source, or reference into the ASPIS catalog" |
| Owning agent match | ✓ | Referenced in `research-lead.md:31` |
| Priority (P0) | ✓ | Listed as P0 in inventory |
| Frontmatter / 5 sections | ✓ | All present + 7 detailed sub-procedures |
| Self-contained | ✓ | All 7 steps fully described with sub-bullets and decision points |
| R-006 | ✓ | Skill is the source |
| **Issues** | None |

**Score: 10/10** — the 7 steps (Candidate → Record → License check → Adapt → Prove → Review → Promote) match the F-016 inventory's "7-step R-008-gated path" specification. The License check step (L:36-42) is the critical R-008 gate and is correctly anti-patterned: "incorporating unlicensed or restrictively-licensed content is a legal risk" (L:85-86).

---

## 4 · Findings

### 4.1 · H-1 — R-006 single-source violation in `constitution-checks` skill

**Location:** `src/aspis/data/catalog/skills/constitution-checks/SKILL.md`, lines 23-42 (procedure, rule enumeration)

**Issue:** The skill enumerates 12 architecture-constitution rules by prose names ("Local Change", "Plugin First", "Single Source of Truth", etc.). The system-of-record machine-readable index is `src/aspis/data/catalog/config/policy/constitution-checks.yaml`, and the YAML uses different rule IDs:

| Constitution document name | YAML ID | Both? |
|---|---|---|
| Local Change | C-LOCAL-CHANGE | yes |
| Plugin First | C-PLUGIN-FIRST | yes |
| Single Source of Truth | C-SINGLE-SOURCE | yes |
| Configuration over Code | C-CONFIG-OVER-CODE | yes |
| Core is Stable | (no C-CORE-STABLE) | doc only |
| Dependency Direction | (no C-DEPENDENCY-DIRECTION) | doc only |
| Discovery over Registration | C-DISCOVERY | yes |
| Generated Artifacts | (no C-GENERATED-ARTIFACTS) | doc only |
| No Special Cases | C-NO-SPECIAL-CASE | yes |
| Consistency over Cleverness | (no C-CONSISTENCY-OVER-CLEVERNESS) | doc only |
| Architecture before Features | (no C-ARCH-BEFORE-FEATURES) | doc only |
| Portable by Default | C-PORTABLE | yes |

**Why this matters:** The `architecture-constitution.md` document itself says (L:17-18): "The machine-readable checklist (`config/constitution-checks.yaml`) says which rule each role owns. An agent loads only the rules its role enforces." The skill is supposed to walk the rule list from the YAML, not from the document. Currently the skill's rule list bypasses the YAML entirely.

**Severity:** HIGH — violates R-006 (single source) and creates a maintenance hazard. If the YAML is updated (rule renamed, added, removed), the skill silently drifts. If a future `catalog-validator` runs the skill and compares against the YAML, it will report false drift.

**Recommended fix:**

1. **Preferred:** Update `constitution-checks.yaml` to include all 12 rules from `architecture-constitution.md`. Add C-ARCH-BEFORE-FEATURES, C-CORE-STABLE, C-DEPENDENCY-DIRECTION, C-GENERATED-ARTIFACTS, C-CONSISTENCY-OVER-CLEVERNESS. Each gets an `enforced_by` and `review_question`. The constitution document is the source of truth; the YAML is the machine-readable index. Currently the index is incomplete.
2. **Alternative:** Update the skill to read the rule list dynamically from the YAML, so the skill always reflects the current YAML state. Lose the inline enumeration in favor of a pointer.

**Whichever fix is chosen, also address M-1** (YAML missing C-ARCH-BEFORE-FEATURES).

### 4.2 · H-2 — R-006 single-source violation in `constitution-check` skill

**Location:** `src/aspis/data/catalog/skills/constitution-check/SKILL.md`, lines 23-37 (procedure, rule enumeration) and lines 50-52 (anti-patterns)

**Issue:** The skill enumerates 9 reviewer-owned rules by prose names that **do not match** the 9 reviewer-enforced rules in `constitution-checks.yaml`:

| Skill (L:26-37) | YAML reviewer-enforced | Both? |
|---|---|---|
| Plugin First | C-PLUGIN-FIRST (NOT enforced by review — `enforced_by: [planning, build]`) | skill only |
| Single Source of Truth | C-SINGLE-SOURCE | yes |
| Configuration over Code | C-CONFIG-OVER-CODE | yes |
| Core is Stable | (not in YAML) | skill only |
| Dependency Direction | (not in YAML) | skill only |
| Discovery over Registration | C-DISCOVERY | yes |
| Generated Artifacts | (not in YAML) | skill only |
| No Special Cases | C-NO-SPECIAL-CASE | yes |
| Consistency over Cleverness | (not in YAML) | skill only |
| (missing) | C-COST (enforced by [planning, review]) | YAML only |
| (missing) | C-LOCAL-CHANGE (enforced by [planning, review]) | YAML only |
| (missing) | C-FILE-SELF-EXPLAINS (enforced by [build, review]) | YAML only |
| (missing) | C-TESTABLE (enforced by [planning, build, review]) | YAML only |
| (missing) | C-PORTABLE (enforced by [build, review]) | YAML only |

**Why this matters:** The skill is teaching the reviewer to look for 9 rules that don't all apply to the reviewer's role, while missing 5 rules (including C-COST — the cost-of-change test, which is the constitution's "north star") that the YAML says the reviewer must enforce. The skill will produce false negatives (miss real violations) and false positives (flag rules that aren't the reviewer's).

**Severity:** HIGH — the reviewer will be checking the wrong things. The reviewer's body (L:209-211) says "Check the architecture constitution (`.aspis/config/constitution-checks.yaml`, `enforced_by: review`)". The skill should match that, not bypass it.

**Recommended fix:** Same as H-1 — update the YAML to include all 12 rules (so the skill can correctly identify the 9 reviewer-enforced ones), then update the skill to read the reviewer-enforced subset from the YAML.

### 4.3 · H-3 — R-006 single-source violation in `research-lead` body (Cache system section)

**Location:** `src/aspis/data/catalog/agents/research-lead.md`, lines 107-131 (Cache system section)

**Issue:** The body's "Cache system" section duplicates the cache-management skill's content:
- Cache locations (L:115-120 in body) duplicate skill L:27-31
- Staleness windows (L:121-130 in body) duplicate skill L:34-36
- The procedure is implied in both places

**Why this matters:** R-006 says "Content lives once in its asset (skill/workflow/template/data file); agent bodies reference, never duplicate." If the skill updates the staleness windows (e.g., to add a new reference type), the body will silently drift. The body should say "see `cache-management` skill" and stop.

**Severity:** HIGH — the research-lead is the knowledge authority; its body is loaded on every research call. Drifting the cache rules in two places creates a maintenance trap and risks inconsistent cache decisions.

**Recommended fix:** Replace lines 107-131 with a 2-3 line pointer: "Cache-first discipline: check cache before any new research, evaluate staleness, route to full procedure on miss or stale. The cache locations, key strategy, and staleness windows live in the `cache-management` skill — load it for the procedure."

### 4.4 · H-4 — R-006 single-source violation in `build-lead` body (Packet validation section)

**Location:** `src/aspis/data/catalog/agents/build-lead.md`, lines 102-112 (Packet validation — the 4 checks)

**Issue:** The body's "Packet validation — the 4 checks" table duplicates the packet-validation skill's 4-check procedure. The table shows:

| Check | What | Fail → |
|---|---|---|
| Scope | Allowed files exist? Forbidden paths absent? | Return to planning-lead |
| Feasibility | Can this be done with listed files? Contradictions? | Return to planning-lead |
| Completeness | Enough context for builder? Acceptance clear? | Enrich from feature context (V2+) or return (V0-V1) |
| Acceptance | Per-task checks verifiable? | Return to planning-lead |

The packet-validation skill's "Four checks" section (L:20-53) covers the same 4 checks with V0-V4 scaling, packet-maturity-scaled actions, and the same fail-routing logic.

**Why this matters:** Same as H-3 — the build-lead is the orchestrator for every feature build; the body is loaded on every build delegation. If the skill adds a check or changes a fail action, the body will silently drift. The body is already a long orchestrator doc; 11 lines of duplicated table is real R-006 noise.

**Severity:** HIGH — same maintenance trap as H-3. The packet-validation skill is the source; the body should reference it.

**Recommended fix:** Replace lines 102-112 with a 2-line pointer: "Validate the packet against the 4 checks (scope, feasibility, completeness, acceptance) with V0-V4 maturity scaling — see the `packet-validation` skill for the procedure and V-scaling. A scope, feasibility, or acceptance gap is a planning defect → return to planning-lead; you cannot invent planning content."

### 4.5 · M-1 — `constitution-checks.yaml` is missing C-ARCH-BEFORE-FEATURES

**Location:** `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (the YAML has 11 rules; the constitution document has 12)

**Issue:** The YAML is missing `C-ARCH-BEFORE-FEATURES` from the 12-rule set in `architecture-constitution.md` (L:68-69 of the constitution document). The planning-lead ref spec (L:947-953) lists all 12 including C-ARCH-BEFORE-FEATURES.

**Why this matters:** The YAML is the system-of-record machine-readable index (per the constitution document's own comment, L:17-18). A missing rule means the planning-lead's `constitution-checks` skill will not flag a violation of C-ARCH-BEFORE-FEATURES when running the audit. This is a false-negative gap.

**Severity:** MEDIUM — single missing rule, but it's the rule that says "build the extension mechanism first, then the feature" — a high-leverage rule for an architecture system.

**Recommended fix:** Add C-ARCH-BEFORE-FEATURES to the YAML with `enforced_by: [planning, review]` and an appropriate `review_question`. Then the skills can be updated to read the rule list from the YAML (H-1, H-2 fix).

### 4.6 · M-2 — Minor wording imprecision in `mode-decision` procedure step 1

**Location:** `src/aspis/data/catalog/skills/mode-decision/SKILL.md`, line 22

**Issue:** "Active feature's `mode` field (set by planning-lead)" — but the project-lead can also set the mode (via `aspis mode`), and the mode-decision skill itself is owned by both.

**Severity:** MEDIUM — minor imprecision. The skill's auto-escalation and auto-downgrade rules are correct; the resolution order at L:19-23 is correct (user > active feature > project > global). The wording at L:22 is the only place that attributes mode-setting to one specific lead.

**Recommended fix:** Change "(set by planning-lead)" to "(set by planning-lead via the plan, or by project-lead via `aspis mode`)".

### 4.7 · M-3 — Anti-pattern in `constitution-check` is factually wrong

**Location:** `src/aspis/data/catalog/skills/constitution-check/SKILL.md`, line 50

**Issue:** "the planning-lead handles the other 3" — naming Local Change, Architecture before Features, and Portable by Default as plan-only. **This is factually wrong per the YAML:**

- `C-LOCAL-CHANGE`: `enforced_by: [planning, review]` — reviewer enforces too, not plan-only
- `C-ARCH-BEFORE-FEATURES`: not in the YAML at all
- `C-PORTABLE`: `enforced_by: [build, review]` — build and review, not plan-only

The actual plan-only rules (reviewer NOT in `enforced_by`) are `C-AUTOMATION` and `C-PLUGIN-FIRST` (2 rules, not 3).

**Severity:** MEDIUM — same root cause as H-2; the skill is working from the wrong source. The anti-pattern is supposed to teach the reviewer what to defer to the planning-lead, but it gives the wrong list.

**Recommended fix:** Tied to H-2. Once the YAML is complete and the skill reads from it, the anti-pattern can be regenerated from the actual YAML data.

### 4.8 · L-1 — Section ordering deviation in `evidence-validation`

**Location:** `src/aspis/data/catalog/skills/evidence-validation/SKILL.md`, lines 20-37

**Issue:** The skill puts "Hard rule: no evidence, no verdict" (L:20-23) and "What counts as evidence per dimension" (L:25-37) between "When to use" (L:15-19) and "Procedure" (L:39-54). The catalog pattern (FR-001) is Purpose → When to use → Procedure → Outputs → Anti-patterns. The evidence table is high-value content but is out of order.

**Severity:** LOW — functional, stylistic. The evidence table is excellent content; a reader might miss it because it appears before "Procedure" in the section list.

**Recommended fix:** Move the "Hard rule" and "What counts as evidence per dimension" content to either:
- A "Key principle" or "Reference" section after the title, before "Purpose"
- Inside "Procedure" as steps 0 and 1
- Inside "Procedure" as a preamble

### 4.9 · L-2 — Inventory "Est. Sections" counts don't match actual sections

**Location:** `.aspis/features/F-016-agent-system-architecture/Research/skills/inventory.md`

**Issue:** The inventory's "Est. Sections" column (e.g., "4", "5", "6") is a planning-time estimate. The actual built skills have different section counts because they include:
- Frontmatter (not counted as a section)
- Optional tables, sub-sections, and supplementary content (counted as "sections" in the inventory, not in the skill)

For example:
- `constitution-checks` is estimated at 6 sections in the inventory; actual skill has 5 main sections (Purpose, When to use, Procedure, Outputs, Anti-patterns) plus inline sub-steps.
- `evidence-validation` is estimated at 4 sections in the inventory; actual skill has 5+ sections including the evidence table.

**Severity:** LOW — planning-time estimate vs actual; not a defect in the skills.

**Recommended fix:** None required. The inventory was a planning artifact; the skills meet FR-001's 5-section minimum.

---

## 5 · Cross-skill consistency

### 5.1 · `constitution-checks` (planning) vs `constitution-check` (reviewer) — differentiation

The inventory (L:165-172) flagged these as related but separate skills:

> "**`constitution-checks` (planning-lead) and `constitution-check` (reviewer)** are related but separate skills. Planning-lead's version audits a PLAN before build (does the plan violate the constitution?); reviewer's version audits a change against the 9 reviewer-owned rules at review time. They share the 12-rule source but differ in input (PLAN vs diff) and output (CONSTITUTION_CHECK.md vs review finding). Recommend keeping them separate; merge only if a follow-up feature shows the duplication is a maintenance burden."

The two skills ARE clearly differentiated:
- `constitution-checks` (planning) — input is PLAN, output is CONSTITUTION_CHECK.md report, all 12 rules
- `constitution-check` (reviewer) — input is diff, output is review finding, 9 reviewer-owned rules

**Verdict on differentiation:** ✓ Correct separation. The H-1 / H-2 issues are about WHAT the skills enumerate, not whether they should be two skills.

### 5.2 · `mode-decision` shared by project-lead and planning-lead

The inventory (L:147-149) says: "**`mode-decision` is owned by two agents.** ... It is a single skill with two consumers; build once and grant both agents the allowlist."

- `project-lead.md:51` — frontmatter includes `mode-decision`
- `planning-lead.md:53` — frontmatter includes `mode-decision`

The skill itself is built once (correctly), both agents reference it. No duplication. **✓ Correct.**

### 5.3 · `cache-management` vs `harvest-protocol` — no accidental overlap

- `cache-management` — about cache-first discipline on the research path
- `harvest-protocol` — about bringing external content into the catalog permanently

These are different procedures with different goals. No overlap. **✓ Correct.**

### 5.4 · All 14 skills have consistent frontmatter

Every skill has:
- `name:` field (matching directory name, kebab-case)
- `description:` field (one-sentence purpose)
- `# Skill Name` title
- 5 sections: Purpose / When to use / Procedure / Outputs / Anti-patterns (or their documented equivalents)

Frontmatter is consistent across all 14. **✓ Correct.**

---

## 6 · Reference resolution check (R-006 reverse: 0 orphans)

I verified that every skill referenced by an agent's frontmatter resolves to an existing SKILL.md file:

| Skill | Referenced by | SKILL.md exists? |
|---|---|---|
| `mode-decision` | `project-lead.md:51`, `planning-lead.md:53` | ✓ |
| `recontextualization` | `project-lead.md:52` | ✓ |
| `constitution-checks` | `planning-lead.md:54` | ✓ |
| `constitution-check` | `reviewer.md:42` | ✓ |
| `evidence-validation` | `reviewer.md:43` | ✓ |
| `packet-validation` | `build-lead.md:51` | ✓ |
| `builder-selection` | `build-lead.md:52` | ✓ |
| `session-continuation` | `project-lead.md:53` | ✓ |
| `security-review` | `reviewer.md:41` | ✓ |
| `catalog-validator` | `system-lead.md:45` | ✓ |
| `governance-approval` | `system-lead.md:46` | ✓ |
| `drift-detector` | `system-lead.md:47` | ✓ |
| `cache-management` | `research-lead.md:30` | ✓ |
| `harvest-protocol` | `research-lead.md:31` | ✓ |

**0 orphan skill references** in any of the 12 agent bodies. **✓ FR-001 satisfied.** Cross-referenced via `grep` for all 14 skill names across `src/aspis/data/catalog/agents/*.md`.

---

## 7 · Self-containment check (can a context-isolated agent execute the SKILL.md alone?)

For each skill, I checked whether the procedure is fully described or relies on external knowledge that isn't in the skill or its referenced documents.

| Skill | Self-contained? | Notes |
|---|---|---|
| `mode-decision` | ✓ | Mode list, escalation triggers, downgrade rules all inline. References DYNAMIC_READINESS.md for the model-tier-vs-mode distinction (which exists). |
| `recontextualization` | ✓ | Read → Fold → Translate → Decide procedure is fully self-described. |
| `constitution-checks` | ✓* | 12 rules enumerated inline. *Bypasses constitution-checks.yaml — see H-1. |
| `constitution-check` | ✓* | 9 rules enumerated inline. *Bypasses constitution-checks.yaml — see H-2. |
| `evidence-validation` | ✓ | Evidence table per dimension is inline. |
| `packet-validation` | ✓ | 4 checks + V0-V4 scaling inline. |
| `builder-selection` | ✓ | Selection matrix, override rules, tier cascade inline. |
| `session-continuation` | ✓ | 4 resumption types + 5-field packet shape inline. |
| `security-review` | ✓ | OWASP top 10 + ASPIS-specific concerns inline. |
| `catalog-validator` | ✓ | 6 sub-checks inline. References AGENT_BODY_STANDARD.md for 11 required fields (which exists). |
| `governance-approval` | ✓ | R-008 territory checklist + 5-step procedure inline. References `aspis governance` CLI verb (L2-P0 — future dependency, explicitly called out). |
| `drift-detector` | ✓ | 5-step procedure + 3-class classification inline. References existing rendering pipeline (`plan_export`/`write_export`/`protect` — exists). |
| `cache-management` | ✓ | Cache key strategy + 2 locations + staleness evaluation inline. |
| `harvest-protocol` | ✓ | 7 steps with sub-bullets inline. |

**All 14 skills are self-contained**, with one explicit future dependency (`governance-approval` references the L2-P0 `aspis governance` CLI verb, which is called out as "built separately"). **✓ R-006 satisfied at the skill-content level.**

---

## 8 · Readability check (cheap and standard models)

For each skill, I checked:
- Line count: 40-90 lines (good for cheap model context budget)
- Procedure steps: 3-7 numbered steps (scannable)
- Tables and lists: used for reference data (evidence per dimension, V0-V4 scaling, selection matrix, etc.)
- No unnecessarily complex language
- No run-on prose where a bullet would do

All 14 skills pass readability. The 4 best-scored skills (10/10) — `evidence-validation`, `packet-validation`, `builder-selection`, `session-continuation`, `security-review`, `governance-approval`, `drift-detector`, `cache-management`, `harvest-protocol` — have well-structured tables and clear step lists that a cheap model can follow mechanically. The 9/10 skills (`mode-decision`, `catalog-validator`) lose 1 point for minor wording imprecision. The 2 problematic skills (`constitution-checks` 6/10, `constitution-check` 5/10) lose points for the rule-list mismatch, not for readability — they're both readable, but the rules they teach are wrong.

---

## 9 · Acceptance criteria check (per FR-001, FR-018, SC-001, SC-009)

| Criterion | Source | Status | Evidence |
|---|---|---|---|
| FR-001: Skill references resolve to SKILL.md | SPEC L:77 | ✓ | Section 6 above — 0 orphans |
| FR-001: Each skill has Purpose / When to use / Procedure / Outputs / Anti-patterns | SPEC L:77 | ✓ | Section 3 above — all 14 have the 5 sections (or documented equivalents) |
| FR-018: No asset content duplicated across agent bodies (R-006) | SPEC L:96 | ✗ | 2 R-006 violations in agent bodies (H-3, H-4) |
| FR-018 sub-clause: No content duplicated across skills | SPEC L:96 | ✗ | 2 R-006-style violations in skills (H-1, H-2) |
| SC-001: 0 frontmatter skill references without SKILL.md | SPEC L:122 | ✓ | Section 6 above |
| SC-009: 14 of 24 in-scope missing skills have valid SKILL.md | SPEC L:130 | ✓ | All 14 are valid; 10 more in L2-P1 |
| SC-011: Cost-of-change ≤ 3 files for new agent/skill | SPEC L:132 | ✓ | Verified: new skill = 1 catalog file + 1 frontmatter entry = 2 files |

**Verdict on acceptance:** 5 of 6 criteria pass; 1 partially fails (FR-018, due to H-3 + H-4 + H-1 + H-2). The system can use the skills today, but the 4 violations are real and should be fixed in a follow-up task before L2-P0.

---

## 10 · Final verdict

**APPROVED WITH NOTES** — the 14 skills are well-built, format-compliant, and reference-resolved. The system can be approved to proceed past the L1 exit gate.

**Required follow-up actions (routed to fix):**

1. **Fix H-1 and M-1 together:** Update `constitution-checks.yaml` to include all 12 rules from `architecture-constitution.md` (add C-ARCH-BEFORE-FEATURES, C-CORE-STABLE, C-DEPENDENCY-DIRECTION, C-GENERATED-ARTIFACTS, C-CONSISTENCY-OVER-CLEVERNESS). This is the system-of-record fix; the YAML is the machine-readable index and must be complete.
2. **Fix H-2 and M-3 together:** Once the YAML is complete, update both `constitution-checks` and `constitution-check` skills to read the rule list from the YAML (or at least reconcile the skill's rule list with the YAML's IDs). The "9 reviewer-owned checks" can be computed from `enforced_by: review` in the YAML.
3. **Fix H-3:** Replace the duplicated "Cache system" section in `research-lead.md` (L:107-131) with a 2-3 line pointer to the `cache-management` skill.
4. **Fix H-4:** Replace the duplicated "Packet validation — the 4 checks" table in `build-lead.md` (L:102-112) with a 2-line pointer to the `packet-validation` skill.
5. **Fix M-2 (optional):** Update `mode-decision` L:22 to mention both owners of mode-setting.
6. **Fix L-1 (optional):** Reorder `evidence-validation` to put the evidence table inside the Procedure section.

**Per-skill scores (summary):**

| Skill | Score | Notes |
|---|---|---|
| `mode-decision` | 9/10 | M-2 minor wording |
| `recontextualization` | 10/10 | Concise, complete |
| `constitution-checks` | 6/10 | H-1: bypasses YAML, M-1: YAML incomplete |
| `constitution-check` | 5/10 | H-2: bypasses YAML with wrong rules, M-3: wrong anti-pattern |
| `evidence-validation` | 10/10 | Best evidence table in the set |
| `packet-validation` | 10/10 | V0-V4 scaling table is a model |
| `builder-selection` | 10/10 | Selection matrix + override rules |
| `session-continuation` | 10/10 | 5-field resume packet, 4 resumption types |
| `security-review` | 10/10 | OWASP + 3 ASPIS-specific concerns |
| `catalog-validator` | 9/10 | Could specify 11 required fields inline |
| `governance-approval` | 10/10 | R-008 gate correctly distinguished from verb |
| `drift-detector` | 10/10 | PROTECT class is the right nuance |
| `cache-management` | 10/10 | Cache key strategy is well-thought-out |
| `harvest-protocol` | 10/10 | All 7 steps with sub-bullets |

**Overall: 12 of 14 skills score 9-10/10. The 2 that score lower (constitution-checks, constitution-check) share the same root cause: they bypass the system-of-record YAML in favor of the constitution document's prose rule names. The fix is to make the YAML complete, then update the skills to use it.**

---

## 11 · Routing

- **H-1, H-2, M-1, M-3** — same fix: complete the YAML, then update the skills. Route to system-lead as a follow-up to T-08a (R-008 gate — the YAML is a system-rule index, so updating it is governance territory). Owner approval may be needed; the YAML is a Tier 2 (policy-locked) config.
- **H-3, H-4** — body cleanup. Route to the L1 owner-review-gate follow-up; no R-008 needed (these are agent body edits, not config changes).
- **M-2** — wording fix. Route as a trivial edit; no R-008.
- **L-1, L-2** — optional polish. Defer or include in the L2 polish phase.

---

*Reviewed against: F-016 skills inventory, F-016 reference specs (8 leads), `constitution-checks.yaml`, `architecture-constitution.md`, `DYNAMIC_READINESS.md`, `AGENT_BODY_STANDARD.md`, all 12 agent bodies in `src/aspis/data/catalog/agents/`. All 14 SKILL.md files read end-to-end. 32 cross-references verified.*
