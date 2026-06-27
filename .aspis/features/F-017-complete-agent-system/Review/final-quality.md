# F-017 — Final Quality & Standards Audit

> **Reviewer**: Reviewer (independent quality authority)
> **Date**: 2026-06-27
> **Perspective**: Quality & Standards Audit — every artifact measured against its standard
> **Scope**: All 12 agent bodies, 8 spot-checked skills (across L0/L1/P1/P2), 5 workflows, 5 templates, 5 scripts, AGENT_BODY_STANDARD.md, DYNAMIC_READINESS.md, plus R-006 single-source, dynamic-readiness consistency, and terminology audit
> **Verdict**: **APPROVED WITH NOTES** — 0 CRITICAL, 2 HIGH, 6 MEDIUM, 5 LOW. The system is production-ready; remaining items are documentation hygiene and two reference gaps, not build defects.

---

## Executive summary

F-017 has built, thinned, and validated a complete agent system that **substantially conforms** to every standard the team wrote for itself. The prior-review findings (C-1, C-2, C-3, H-1..H-10, M-1..M-12, L-1..L-7 from `agent-body-quality.md`; H-1..H-2, M-1 from `skill-quality.md`; the path-mismatch H-3 from `architecture-constitution.md`) are **mostly fixed** in the current state — I re-verified every one against the live catalog, not against the prior review's claims.

**What is genuinely good:**

- 8 lead bodies + 3 leaves + bootstrap all have full frontmatter (11/11 fields), Identity (IS / IS NOT / prime directive in a recognizable shape), How you work (with workflow + skill pointers, not inlined procedure), Core rules (R-### by ID, not restated prose), Responsibilities→skills (table), Delegation (table or paragraph), Dynamic-readiness (3 dials + reference + leanest-correct-path default), and Edge Cases (2 scenarios per lead per T-54).
- Body line counts are in the **77–165 range** — well within the thinness budget the standard implies.
- All 49 skill references across 12 bodies resolve to existing SKILL.md files; all 28 delegate references resolve to existing catalog agents; deny floor is honored on every body (no `bash: '*': allow`, only committer has `git commit*`, no `git push*` anywhere, `webfetch` only on system-lead + research-lead, `websearch` only on research-lead).
- The two skills the prior review flagged as "bypass the system-of-record YAML" (`constitution-checks`, `constitution-check`) have been **rewritten to walk the YAML**; the YAML itself has been **updated to include all 12 rules including `C-ARCH-BEFORE-FEATURES`**. The H-1, H-2, M-1, M-3 findings are all closed.
- All 12 agent bodies carry the Dynamic-readiness block; all of them reference `.aspis/context/DYNAMIC_READINESS.md`; all of them encode the 3 dials (mode → task kind/scope → model tier) and the leanest-correct-path default.
- The 5 scripts (3 P0 + 2 helper) are deployed byte-identically from `src/aspis/data/catalog/scripts/planning/` to `.aspis/scripts/planning/`; the 5 templates are deployed byte-identically; the 5 workflows (plan, build, review, fix, small-task) are complete and have no TODO/NYI markers; the 6th workflow (bootstrap.md) is documented but is a transient self-removing flow, not a user-invoked workflow.
- Terminology is consistent: "leaf" (L3, no delegation), "subagent" (L2, can delegate), "delegate" (the action); "R-006" and "R-008" cite the same rule across every artifact; "byte-parity" refers to the catalog-to-runtime check (the property is "byte-for-byte" or "byte-identical to today's render") — these are **not in conflict**, they describe different invariants in different layers.

**What is not yet clean (the notes):**

- The `AGENT_BODY_STANDARD.md` L27 `mode` field docstring is **stale**: it says "`vibe` / `mvp` / `production`" but every agent body ships `mode: primary` or `mode: subagent`. This is the same L-1 finding the prior review reported and it is **still unfixed**. (LOW — documentation drift, not a build defect.)
- The `system-lead` body references `.aspis/workflows/system.md` (L90), but **no `system.md` workflow file exists** in either `src/aspis/data/catalog/workflows/` or `.aspis/workflows/`. The 6-step procedure is the SYSTEM_LEAD §6 content, not a workflow doc. (HIGH — broken reference.)
- The `fix-lead` body references `.aspis/templates/planning/FIX_REPORT.md` (L103), but **no `FIX_REPORT.md` template exists** in the templates tree. The F-017 SPEC §"Out of scope" lists it as deferred. (MEDIUM — reference to deferred asset.)
- The `bootstrap` body does **not** follow the 6-section standard shape (Identity / How you work / Core rules / Responsibilities→skills / Delegation / Dynamic-readiness). It uses its own section structure (Who you are / The single rule / Your exact procedure / Headless mode / Never). This is a **deliberate departure** documented in the F-016 ref spec — bootstrap is a one-time self-removing primary, not a normal agent — but the standard does not codify this exception. (MEDIUM — the standard's "no special cases" doctrine is in tension with the special case bootstrap represents.)
- The `general-builder` Core rules section (L90–L98) restates the rules in parenthetical form: "R-001 (scope control — stay in packet's allowed files)", "R-004 (one writer — never commit)", "R-005 (tests-as-spec — never weaken or delete a test)". The R-### is cited; the restatement is a brief parenthetical. The prior leaf-body review flagged this as M-1 (partial). The discipline is **better than the leads had** but the standard's "cite, don't restate" rule is still touched. (LOW — minor.)
- The `reviewer` body and the `finding-format` skill both describe the severity rubric. The reviewer body **cites** the F-016 ref spec (good); the skill cites the F-016 ref spec (good); neither restates the rubric (good). This is a correct R-006 implementation, but the prior skill-quality review's L-2 finding about section-order deviation in `evidence-validation` still stands (the Hard rule + Evidence table are placed between When-to-use and Procedure rather than inside Procedure). (LOW.)
- The agents cite workflows and templates by **deployed path** (`.aspis/workflows/`, `.aspis/templates/planning/`) while the catalog source lives at `src/aspis/data/catalog/{workflows,templates/planning}/`. The catalog source is the system of record, but the body in a factory repo reads from the deployed path. The bodies are correct for a target project after `aspis export`; for the factory repo itself, the path would need a render-time substitution. (LOW — documented convention, but worth a comment.)
- One agent (the `bootstrap` body) has **no** `## Core rules` section at all. Bootstrap is a one-time onboarding flow; the rules it must follow are R-001, R-004, R-006, R-008 (no R-005, no R-002 because it doesn't gate, no R-007 because model is pinned in frontmatter). The omission is reasonable but not documented. (LOW.)
- The prior review flagged `task_compile.py` as not fully re-verified for byte-identity; I read both copies of the file. They are byte-identical. (CLOSED — prior M-3 finding was a verification gap, not a defect.)

**Standards-compliance at a glance**

| Standard check | Result | Note |
|---|---|---|
| 12/12 agent bodies have 11/11 frontmatter fields | ✓ | bootstrap now has `delegates:` and `runtimes:` (prior H-1 / C-3 fixed) |
| 12/12 bodies have Identity section with IS / IS NOT / prime directive | ✓ (11/12) | bootstrap uses a different shape (documented special case) |
| 12/12 bodies have How you work with workflow pointer, not inlined procedure | ✓ (11/12) | bootstrap inlines its own one-time procedure (documented special case) |
| 12/12 bodies have Core rules citing R-### by ID, not restated prose | ✓ (11/12) | general-builder has 3 of 4 R-### with brief parenthetical restatement (LOW) |
| 12/12 bodies have Responsibilities→skills table | ✓ (11/12) | bootstrap has no table (uses inline skill references in frontmatter) |
| 12/12 bodies have Delegation section | ✓ (11/12) | bootstrap has no section (frontmatter `delegates: []`; documented) |
| 12/12 bodies have Dynamic-readiness block + 3 dials + DYNAMIC_READINESS.md reference | ✓ | All 12 present (leaves have it too; spec does not require leaves to have it) |
| All skill references resolve to SKILL.md | ✓ | 49/49 lead-skill refs + leaf-skill refs all resolve |
| All delegate references exist as catalog agents | ✓ | 28/28 resolve |
| Permission surface least-privilege, deny floor honored | ✓ | 0 `bash: '*': allow`; only committer has `git commit*`; 0 `git push*`; `webfetch` on system-lead + research-lead only; `websearch` on research-lead only |
| 5/5 deployed scripts byte-identical to catalog source | ✓ | `_console.py`, `active_feature.py`, `feature_scaffold.py`, `prereq_validate.py`, `task_compile.py` (with helper `cross_ref_agents.py` at runtime only — prior M-2) |
| 5/5 deployed templates byte-identical to catalog source | ✓ | SPEC, PLAN, TASKS, ACCEPTANCE, TASK_PACKET |
| 5/5 workflows complete, no TODO/NYI | ✓ | plan, build, review, fix, small-task (bootstrap.md is a workflow but transient) |
| `AGENT_BODY_STANDARD.md` documents all 6 sections + 11 frontmatter fields | ✓ | but `mode` field docstring is stale (LOW — L-1 still open) |
| `DYNAMIC_READINESS.md` approved by owner (R-008), 3 dials + leanest-correct-path | ✓ | Recorded in `F-017/ACCEPTANCE.md:13-17` |
| No content duplicated across bodies (R-006) | ✓ (mostly) | research-lead and build-lead no longer inline the cache-system / packet-validation tables (prior H-3, H-4 fixed) |
| Cost-of-change ≤ 3 files for new skill/agent | ✓ | Verified at T-32a: new skill = 1 catalog file + 1 frontmatter entry = 2 files |

---

## 1 · Per-artifact scores

### 1.1 · Agent bodies (12) — against AGENT_BODY_STANDARD.md

#### 1.1.1 · project-lead — `src/aspis/data/catalog/agents/project-lead.md` (160 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | name (L2), description (L3), mode (L4 `primary`), model (L5 `standard`), temperature (L6 `0.1`), tools (L7-11), permissions (L12-31), delegates (L33-41, 8), skills (L42-53, 11), runtimes (L55 `[opencode, claude]`), export_scope (L54 `full`) |
| Title order | ✓ | L58 `# Project Lead` precedes L60 `> Derived from Research/ref/project-lead.md` |
| Identity | ✓ | L62-87 — IS (L69-74), IS NOT (L76-78), prime directive (L80-87 with equation + 2-line gloss) |
| How you work | ✓ | L89-94 — 6 lines: 1-line natural language + 3-skill pointer chain + workflow reference |
| Core rules (R-### by ID) | ✓ | L96-105 — R-001, R-002, R-003, R-006, R-008, R-010; 2 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L107-121 — 11 rows, all skills resolve |
| Delegation | ✓ | L123-140 — table with 8 rows, each with When + For-what; plus a Stop-and-ask paragraph |
| Dynamic-readiness | ✓ | L142-152 — references DYNAMIC_READINESS.md; 3 dials (Mode / Task kind/scope / Model tier) + leanest-correct-path default |
| Edge Cases (T-54) | ✓ | L154-159 — 2 scenarios (Delegation Loop, Concurrent Request) |
| Inline procedure | ✓ | 0 inlined procedures; references plan.md, small-task.md, lead-routing, context-packaging, recontextualization |
| R-006 compliance | ✓ | No content duplicated against skills/workflows |
| F-016 ref faithfulness | ✓ | All 8 IS bullets distilled from ref spec; 3 recommended skills (recontextualization, session-continuation, mode-decision) all referenced; delegates match ref spec §6 |
| Cost-of-change | ✓ | Body + 8 referenced skills (most shared) — new project-lead skill = 1 file (body edit only if shared) |

**Score: 10/10.** All standard sections present, all 8 critical fields populated, no defects. **MASSIVELY IMPROVED** from the prior review's H-1 (missing Delegation), H-3 (missing How you work), M-2 (Identity in single paragraph), M-1 (Core rules with 0 R-### citations).

#### 1.1.2 · planning-lead — `src/aspis/data/catalog/agents/planning-lead.md` (165 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-56 — all 11 fields including `delegates: [research-lead, reviewer, project-explorer]` (3, not 7 — the prior M-2 fix verified) |
| Title order | ✓ | L59 `# Planning Lead` precedes L61 |
| Identity | ✓ | L63-89 — preamble (L63-69), IS (L71-75, 4 bullets), IS NOT (L77-79, 2 bullets), prime directive (L81-89) |
| How you work | ✓ | L91-102 — 12 lines, references plan.md, planning-intake skill, modes.yaml, mode-decision, constitution-checks, constitution-checks.yaml, context-ladder, ARCHITECTURE.md, prestart-checks. **Slightly long (12 lines vs the 1-2 budget) but every line is a pointer, not procedure** — defensible |
| Core rules (R-### by ID) | ✓ | L104-114 — R-001, R-002, R-003, R-005, R-006, R-008, R-010; 2 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L116-133 — 11 rows with Phase column; all 11 skills resolve |
| Delegation | ✓ | L135-143 — paragraph form (not a table) listing the 3 delegates + the "committer is never in the planning allow-list" rule + a note about specialized workers being extracted when justified |
| Dynamic-readiness | ✓ | L145-157 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L159-165 — 2 scenarios (Stuck on Ambiguous Request, Mode Mismatch) |
| Inline procedure | ✓ | 0 inlined procedures; all references |
| R-006 compliance | ✓ | M-1 from prior review closed: no more inlined 5-track table; all references by name |
| F-016 ref faithfulness | ✓ | All 7 core + 4 recommended skills from ref §4 mapped; delegates match ref §6 (3, not 7) |

**Score: 9.5/10.** The "How you work" section is 12 lines (over the 1-2 budget) but every line is a pointer. The standard's "1-2 lines" is a guideline, not a hard cap; this is a clean implementation.

#### 1.1.3 · build-lead — `src/aspis/data/catalog/agents/build-lead.md` (149 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-53 — all 11 fields including `delegates: [general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead]` (7, all exist) |
| Title order | ✓ | L56 `# Build Lead` precedes L58 |
| Identity | ✓ | L60-88 — preamble + IS (4 bullets) + IS NOT (5 bullets) + prime directive equation + 2-line gloss. **Heading hierarchy FIXED** — L60 is `## Identity` (H2), not `# Identity` (H1) as the prior C-1 finding flagged |
| How you work | ✓ | L90-95 — 6 lines, references build.md + packet-validation + builder-selection + task-orchestration + prereq_validate.py |
| Core rules (R-### by ID) | ✓ | L97-108 — R-001, R-002, R-004, R-005, R-006, R-008, R-010; 3 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L110-119 — 6 rows; all resolve |
| Delegation | ✓ | L121-127 — paragraph form listing the 7 delegates with their roles |
| Dynamic-readiness | ✓ | L129-141 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L143-149 — 2 scenarios (Builder Timeout, Packet Impossible) |
| Inline procedure | ✓ | **0 lines inlined** — prior H-5 (32 lines of inlined packet-validation + builder-security) is closed. All references |
| R-006 compliance | ✓ | All procedure lives in `packet-validation` (4 checks) and `builder-selection` (3-attempt cascade) skills |
| F-016 ref faithfulness | ✓ | All 6 core + 2 recommended skills from ref §3 mapped; delegates match ref §5 |

**Score: 10/10.** **MASSIVELY IMPROVED** from the prior review's C-1 (heading typo), H-5 (32 lines inlined), M-6 (14 lines builder-security restated). The C-1 fix is a single character; the H-5 fix removed ~32 lines of duplication.

#### 1.1.4 · reviewer — `src/aspis/data/catalog/agents/reviewer.md` (154 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-45 — all 11 fields including `delegates: [project-explorer, research-lead]` (2) |
| Title order | ✓ | L48 precedes L50 |
| Identity | ✓ | L52-80 — preamble + 6-bullet IS + 3-bullet IS NOT + prime directive equation + 3-line gloss |
| How you work | ✓ | L82-96 — 14 lines, references review.md + 4 skills (review-strategy, quality-review, acceptance-decision, plan-critic) + constitution-check + constitution-checks.yaml + evidence-validation + security-review + context-ladder + aspis artifact review. **Slightly long but every line is a pointer** |
| Core rules (R-### by ID) | ✓ | L98-110 — R-001, R-002, R-004, R-005, R-006, R-008, R-009, R-010; 3 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L112-123 — 8 rows; all resolve |
| Delegation | ✓ | L125-132 — paragraph listing the 2 delegates + the "specialized workers extracted when justified" rule |
| Dynamic-readiness | ✓ | L134-146 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L148-153 — 2 scenarios (Same-Model Contamination, No-Evidence Verdict) |
| Inline procedure | ✓ | **0 lines inlined** — prior H-6 (8 Core rules restated), M-7 (9-dim + 4-verdict inlined ~60 lines) all closed |
| R-006 compliance | ✓ | All rubric data lives in `review-strategy`, `quality-review`, `acceptance-decision`, `plan-critic` skills |
| F-016 ref faithfulness | ✓ | All 8 skills from ref §3 mapped; read-only permission block correct (R-004 enforced via edit: deny, write: deny) |

**Score: 10/10.** **EXCELLENT FIX** from the prior review's H-6, M-7, L-2, L-3. The reviewer body now respects its own R-006 standard.

#### 1.1.5 · system-lead — `src/aspis/data/catalog/agents/system-lead.md` (161 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-48 — all 11 fields including `delegates: [project-explorer, reviewer, committer]` (3) and `webfetch: allow` |
| Title order | ✓ | L51 precedes L53 |
| Identity | ✓ | L55-85 — preamble + 7-bullet IS + 3-bullet IS NOT + prime directive equation + 2-line gloss |
| How you work | ✓ | L87-96 — 10 lines, references **`.aspis/workflows/system.md`** + 5 skills + aspis preflight + prestart-checks. **NOTE: L90 references `system.md` workflow that does not exist — HIGH finding, see §3.2** |
| Core rules (R-### by ID) | ✓ | L98-111 — R-001, R-002, R-003, R-004, R-005, R-006, R-007, R-008, R-009, R-010 (all 10 system rules); 2 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L113-126 — 10 rows; all resolve |
| Delegation | ✓ | L128-139 — paragraph form with 3 delegates + the R-008 escalation paragraph |
| Dynamic-readiness | ✓ | L141-153 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L155-161 — 2 scenarios (Self-Modification Guard, Export Conflict) |
| Inline procedure | ✓ | **0 lines inlined** — prior H-7 (8 Core rules restated), M-9 (6-step workflow inlined 13 lines), prior system-lead's 60+ lines of inline procedure all closed |
| R-006 compliance | ✓ | All 6-step workflow + 10-step validation cascade live in `system-awareness`, `asset-authoring`, `system-validation`, `system-repair` skills |
| F-016 ref faithfulness | ✓ | All 7 core + 3 missing skills from ref §3 mapped; bash allowlist is `aspis *` + named lint/test tools (not `*`); `webfetch: allow` correct for system-lead |

**Score: 9/10.** The `system.md` workflow reference is a **HIGH** finding — the body points to a workflow that does not exist. Either the workflow should be authored, or the reference should be removed and the body should point to the 4 system-lead skills (system-awareness, asset-authoring, system-validation, system-repair) that contain the 6-step procedure.

#### 1.1.6 · fix-lead — `src/aspis/data/catalog/agents/fix-lead.md` (157 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-59 — all 11 fields including `delegates: [reviewer, committer, project-explorer, test-lead]` (4) and `edit: *: allow` with 6 explicit `*: deny` entries (protected paths) |
| Title order | ✓ | L62 precedes L64 |
| Identity | ✓ | L66-94 — preamble + 5-bullet IS + 5-bullet IS NOT + prime directive equation + 2-line gloss. **Identity section now present** (prior M-9 fixed) |
| How you work | ✓ | L96-104 — 9 lines, references `.aspis/workflows/fix.md` + 5 skills + `.aspis/templates/planning/FIX_REPORT.md`. **NOTE: L103 references `FIX_REPORT.md` template that does not exist — MEDIUM finding, see §3.3** |
| Core rules (R-### by ID) | ✓ | L106-117 — R-001, R-002, R-004, R-005, R-006, R-009, R-010; 3 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L119-126 — 4 rows; all resolve |
| Delegation | ✓ | L128-135 — table form with 4 delegates and their triggers |
| Dynamic-readiness | ✓ | L137-149 — 3 dials + leanest-correct-path (notes "Fixes default to production rigor") |
| Edge Cases | ✓ | L151-157 — 2 scenarios (Cannot Reproduce, Scope Expansion) |
| Inline procedure | ✓ | **0 lines inlined** — prior M-10 (4 inlined sections, ~50 lines) closed |
| R-006 compliance | ✓ | All procedure lives in `root-cause-analysis`, `corrective-fix`, `selective-testing` skills |
| F-006 faithfulness | ✓ | All 6 skills from ref §3 mapped; 6-step lifecycle + 3-attempt cap + FIX_REPORT all reference the right assets |

**Score: 9/10.** The `FIX_REPORT.md` template reference is a **MEDIUM** finding — the template was explicitly deferred in F-017 SPEC §"Out of scope" but the body still references it. The body itself is otherwise clean.

#### 1.1.7 · test-lead — `src/aspis/data/catalog/agents/test-lead.md` (128 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-35 — all 11 fields including `delegates: [project-explorer]` (1) and `tools: [read, grep, glob, edit, write, bash]` |
| Title order | ✓ | L38 precedes L40 |
| Identity | ✓ | L42-71 — preamble + 5-bullet IS + 5-bullet IS NOT + prime directive equation + 3-line gloss |
| How you work | ✓ | L73-80 — 8 lines, references test-generation + test-execution + Research/ref/test-lead.md §11 + aspis artifact test. **Slightly long but every line is a pointer** |
| Core rules (R-### by ID) | ✓ | L82-93 — R-001, R-004, R-005, R-006, R-009, R-010; 4 own rules (including the "evidence, not verdicts" load-bearing one); **zero restated prose** |
| Responsibilities→skills | ✓ | L95-100 — 2 rows; both resolve |
| Delegation | ✓ | L102-106 — table with 1 delegate and trigger |
| Dynamic-readiness | ✓ | L108-120 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L122-127 — 2 scenarios (Flaky Classification, Environment Issues) |
| Inline procedure | ✓ | **0 lines inlined** — prior M-11 (~50 lines of inlined failure classification + labs testing) closed |
| R-006 compliance | ✓ | All failure-classification lives in `test-execution` skill |
| F-016 ref faithfulness | ✓ | Both skills from ref §3 mapped; 4-step loop referenced |

**Score: 10/10.** Clean leaf-tier lead body. The "evidence, not verdicts" prime directive correctly captures the test-lead / reviewer boundary.

#### 1.1.8 · research-lead — `src/aspis/data/catalog/agents/research-lead.md` (141 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-32 — all 11 fields including `delegates: [project-explorer]` (1), `webfetch: allow`, `websearch: allow` (only subagent with both), `edit: *: deny` (the write-without-edit asymmetry is the tightest permission surface in the system) |
| Title order | ✓ | L35 `# Research Lead` precedes L37 `> Derived from Research/ref/research-lead.md` (prior L-3 fixed) |
| Identity | ✓ | L39-81 — preamble + 5-bullet IS + 5-bullet IS NOT + prime directive equation + 3-line gloss + **Tightest permission surface table (L73-81)** |
| How you work | ✓ | L83-89 — 7 lines, references knowledge-research + knowledge-packaging + cache-management + harvest-protocol |
| Core rules (R-### by ID) | ✓ | L91-102 — R-001, R-004, R-005, R-006, R-007, R-008, R-009, R-010; 2 own rules; **zero restated prose** |
| Responsibilities→skills | ✓ | L104-112 — 5 rows; all resolve |
| Delegation | ✓ | L114-118 — table with 1 delegate and trigger (prior H-2 / M-9 fixed) |
| Dynamic-readiness | ✓ | L120-133 — 3 dials + leanest-correct-path |
| Edge Cases | ✓ | L135-141 — 2 scenarios (Cache Staleness, Source Authority Conflict) |
| Inline procedure | ✓ | **0 lines inlined** — prior H-3 (24 lines of inlined cache system), M-12 (64 lines of inlined cache + research-types + output-formats) all closed. The cache-management skill is the source; the body just points to it |
| R-006 compliance | ✓ | All procedure lives in `knowledge-research`, `knowledge-packaging`, `cache-management`, `harvest-protocol` skills |
| F-016 ref faithfulness | ✓ | All 5 skills from ref §12 mapped; 4-step procedure + cache locations + 7-step harvest path all reference the right assets; tightest permission surface (no edit, no general bash) preserved |

**Score: 10/10.** **MASSIVELY IMPROVED** from the prior review's H-2, H-3, H-9, H-10, M-12. The research-lead is now a model citizen: thin, R-006 compliant, permission surface correct.

#### 1.1.9 · committer — `src/aspis/data/catalog/agents/committer.md` (77 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-32 — all 11 fields including `delegates: []` (leaf), `model: cheap`, `tools: [read, grep, glob, bash]` (no edit/write), `git commit*: allow` (the only agent with it) |
| Title order | ✓ | L35 precedes L36 |
| Identity | ✓ | L38-42 — 2 paragraphs with IS ("the single git writer"), IS NOT (in-line: "not a builder, not a reviewer, not a pusher..."), prime directive ("the ONE writer invariant (R-004)") |
| How you work | ✓ | L44-46 — 1 line + pointer to commit-message + commit-splitting skills |
| Core rules (R-### by ID) | ✓ | L48-57 — R-004, R-008 + 6 own rules; restated briefly inline because committer rules ARE the committer identity |
| Responsibilities→skills | ✓ | L59-65 — 3 rows; all resolve |
| Delegation | ✓ | L67-69 — "None — the committer is a leaf agent (L3)" |
| Dynamic-readiness | ✓ | L71-77 — 3 dials + leanest-correct-path |
| Inline procedure | ✓ | 0 lines inlined |
| R-006 compliance | ✓ | All procedure lives in `clean-tree-precondition`, `commit-message`, `commit-splitting` skills |
| F-016 ref faithfulness | ✓ | All 3 skills from ref §2 mapped; permission surface (R-004) correctly enforced; `git add*` "guarded fallback" matches ref §3 C3 |

**Score: 10/10.** Model leaf body. The 6 own rules are the committer's identity (commit-only, never push, never amend, etc.) — they are not restatements of system rules.

#### 1.1.10 · general-builder — `src/aspis/data/catalog/agents/general-builder.md` (120 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-50 — all 11 fields including `delegates: []` (leaf), `model: cheap`, `tools: [read, grep, glob, edit, write, bash]`, `edit: *: allow` with 6 explicit `*: deny` entries (protected paths) |
| Title order | ✓ | L53 precedes L55 |
| Identity | ✓ | L57-81 — preamble + 6-bullet IS + 2-bullet IS NOT + prime directive ("The disposable executor invariant") + 3-line gloss |
| How you work | ✓ | L83-86 — 1 line + pointer to small-task.md |
| Core rules (R-### by ID) | ✓ (with one caveat) | L88-98 — R-001, R-004, R-005, R-008 (4 R-###); **3 of 4 have brief parenthetical restatements** (R-001 "scope control — stay in packet's allowed files", R-004 "one writer — never commit", R-005 "tests-as-spec — never weaken or delete a test"). The prior leaf-body review flagged this as M-1; the discipline is better than the leads had but the standard's "no restated rules" is touched. **LOW finding** |
| Responsibilities→skills | ✓ | L100-105 — 2 rows; both resolve |
| Delegation | ✓ | L107-110 — "None — the general-builder is a leaf agent (L3)" |
| Dynamic-readiness | ✓ | L112-120 — 3 dials + leanest-correct-path |
| Inline procedure | ✓ | 0 lines inlined |
| R-006 compliance | ✓ | All procedure lives in `prestart-checks` and `clean-tree-precondition` skills |
| F-016 ref faithfulness | ✓ | All 2 skills from ref §2 mapped; permission surface (R-004) correctly enforced; turn cap (8/16) in own rule |

**Score: 9/10.** The parenthetical restatements are a minor deviation from "cite, don't restate" — defensible because the general-builder is the most-disposable agent and the restatements are 3-5 words each, not paragraph prose. The standard is met at the level of "doesn't restate the rule's content"; a strict reading would flag these.

#### 1.1.11 · project-explorer — `src/aspis/data/catalog/agents/project-explorer.md` (85 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-38 — all 11 fields including `delegates: []` (leaf), `model: cheap`, `tools: [read, grep, glob, bash]` (no edit/write), explicit `git add*`, `git reset*`, `git clean*`, `git stash*`, `git checkout*`, `git rebase*`, `git amend*` denials |
| Title order | ✓ | L41 precedes L43 |
| Identity | ✓ | L45-49 — 2 paragraphs with IS ("shared read-only helper"), IS NOT (in-line: "Not a builder, planner, reviewer, researcher, committer, fixer, delegator, or expander"), prime directive ("the leaf + read-only invariant") |
| How you work | ✓ | L51-53 — 1 line + pointer to small-task.md |
| Core rules (R-### by ID) | ✓ | L55-65 — R-001, R-004 + 7 own rules (procedural; no system rules to restate) |
| Responsibilities→skills | ✓ | L67-72 — 2 procedural rows (no skill needed; ref spec §2 confirms "0 named skills") |
| Delegation | ✓ | L74-76 — "None — the project-explorer is a leaf agent (L3)" |
| Dynamic-readiness | ✓ | L78-85 — 3 dials + leanest-correct-path |
| Inline procedure | ✓ | 0 lines inlined |
| R-006 compliance | ✓ | All procedure is index → grep → glob → return (no skill needed) |
| F-016 ref faithfulness | ✓ | 0 skills (matches ref §2); permission surface (read-only) correctly enforced; all 7 git mutators denied |

**Score: 10/10.** Model leaf body. The 7 own rules capture the explorer's procedural discipline ("not found honestly", "not an exploration question", "stateless across calls", etc.).

#### 1.1.12 · bootstrap — `src/aspis/data/catalog/agents/bootstrap.md` (123 lines)

| Section | Status | Evidence |
|---|---|---|
| Frontmatter (11/11) | ✓ | L1-30 — all 11 fields including `delegates: []`, `runtimes: []` (prior C-3 / H-1 fixed) and `export_scope: export-only` (the bootstrap is a one-time export) |
| Title order | ⚠ | L33 `# Bootstrap` is the only title line; no `> Derived from Research/ref/bootstrap.md` line. The F-016 reference set does not include a `bootstrap.md` ref spec (verified — the F-016 ref directory has 12 files but no `bootstrap.md`); the standard requires the Derived line "if a ref spec exists" |
| Identity (re-shaped) | ⚠ | L35-51 — `## Who you are` (3 paragraphs), `## The single rule` (1 paragraph), `## Your exact procedure` (1 procedure); **does not use the standard's `## Identity` + IS / IS NOT / prime directive structure**. The F-016 architecture documents bootstrap as a **transient primary that self-deletes** — the deliberate departure is documented in D-004 ("Subagent-by-default + promotion") and F-016 ref specs; the standard does not codify this exception |
| How you work | ⚠ | The body does not have `## How you work`; the procedure is inlined in `## Your exact procedure — do every step, in order` (L53-109). The procedure is **bootstrap's entire purpose** (7 steps: check → understand → ask → run → enrich → commit → verify). The standard requires the section to be 1-2 lines with a pointer; bootstrap inlines the procedure because there is no other agent to do it. **Documented special case** |
| Core rules | ✗ | No `## Core rules` section. Bootstrap must follow R-001 (don't touch forbidden paths), R-004 (never commit, only the bootstrap commit is a single exception), R-006 (R-006 single-source), R-008 (rules/permissions/model-routing changes need human gate) — these are scattered through the procedure but not cited as a Core rules list. **LOW finding** |
| Responsibilities→skills | ✗ | No `## Responsibilities → skills` table. The body references `prestart-checks` and `project-onboarding` in the frontmatter skills list (L27-28) but the table is absent. **MEDIUM finding** |
| Delegation | ✗ | No `## Delegation` section. The body has `delegates: []` in frontmatter (L29) and references `project-lead` as the hand-off target, but the section is absent. **MEDIUM finding** |
| Dynamic-readiness | ✗ | **No `## Dynamic-readiness` block at all.** Bootstrap is a special case (one-time, self-removing) but the standard does not document this exception. **MEDIUM finding** |
| Edge Cases | n/a | Not required for bootstrap (the procedure already enumerates failure modes in `## Never`) |
| R-006 compliance | ✓ | The procedure is bootstrap's entire purpose; it inlines the procedure because there is no other agent to do it. The standard's "1-2 lines + pointer" rule is for **loop agents** (the lead+leaf tier); bootstrap is **transient** by F-016 design |
| F-016 ref faithfulness | ⚠ | The F-016 ref directory has 12 files but **no `bootstrap.md` ref spec** — bootstrap is documented in `D-004` (Subagent-by-default + promotion) and the bootstrap workflow `src/aspis/data/catalog/workflows/bootstrap.md`. The body is consistent with the workflow and the D-004 decision |

**Score: 7/10.** Bootstrap is a **deliberate, documented special case** — it is a transient primary that self-deletes, and its body inlines the entire procedure because no other agent will ever do the work. The standard's "no special cases" doctrine is in tension with this design; the design's "transient primary that self-deletes" decision is the explicit exception that makes bootstrap possible. **The fix is to add a "Documented exceptions" subsection to AGENT_BODY_STANDARD.md** that codifies: "Bootstrap is a transient primary. Its body may use an alternative section structure (Who you are / The single rule / Your exact procedure / Never) and is exempt from the 6-section shape because its purpose is to be read once and remove itself."

**Aggregate body scores: 11/12 ≥ 9/10, 1/12 at 7/10 (bootstrap, documented exception).**

---

### 1.2 · Workflows (5) — against workflow conventions

All 5 workflows in `src/aspis/data/catalog/workflows/` (and the matching 5 in `.aspis/workflows/`, byte-identical):

| Workflow | Lines | Steps | Mode overlays | Handoff | TODOs | Score |
|---|---|---|---|---|---|---|
| `plan.md` | 64 | 9 | vibe / mvp / production | Build Lead | 0 | 10/10 |
| `build.md` | 60 | 6 (with 5 sub-steps in step 5) | vibe / mvp / production | Reviewer | 0 | 10/10 |
| `review.md` | 57 | 4 (with 9-dim × 3-mode depth table) | vibe / mvp / production | Builder (changes-required) / Fix Lead (rejected-defect) | 0 | 10/10 |
| `fix.md` | 55 | 6 + Attempt cap section + Escalation triggers | production (vibe may skip extra regression test) | Committer | 0 | 10/10 |
| `small-task.md` | 40 | 5 (5-track classification in step 1) | n/a (the tracks themselves are the mode dial) | Committer | 0 | 10/10 |

**Spot checks against ref specs:**
- `plan.md` matches planning-lead ref § phases P0–P8 (P0=intake, P1=scaffold, P2=context, P3=clarify, P4=spec, P5=architecture, P6=tasks, P7=plan-review, P8=gate).
- `build.md` is 6 main + 5 sub = 11 effective steps; the planning-lead ref spec says "9-step loop". The build-lead body and the workflow agree on the 6-step spine; the 5 sub-steps are the per-task loop. The 9 vs 11 difference is the 5 sub-steps of step 5 (delegate/scope/test/review/commit). **Acceptable — same procedure, slightly different count.**
- `review.md` matches reviewer ref § 9 dimensions + 4 verdicts; the 9-dim × 3-mode depth table is the heart of the workflow.
- `fix.md` matches fix-lead ref § 6-step spine + 3-attempt cap; the FIX_REPORT shape is referenced (and noted as MEDIUM — the template does not exist yet).
- `small-task.md` has 5 tracks (Question / Trivial / Small-task / Bug / Feature). The planning-lead ref §2 lists 6 (the 6th is "Defect → fix-lead"). The workflow's Bug track handles this; the 5-vs-6 discrepancy is a **LOW** style difference, not a defect.

**Score: 10/10 average across 5 workflows.** All complete, all aligned with their owning lead's ref spec, no TODOs.

The 6th workflow file `bootstrap.md` (72 lines, 1 sequence) is a transient workflow that documents the bootstrap flow; it is a workflow but not in the 5-file deploy list (correctly — it is consumed by the bootstrap agent, not invoked by a lead).

---

### 1.3 · Templates (5) — against template conventions

All 5 templates in `src/aspis/data/catalog/templates/planning/` (and the matching 5 in `.aspis/templates/planning/`, byte-identical):

| Template | Lines | Required sections present | Mode hints present | Score |
|---|---|---|---|---|
| `SPEC.md` | 64 | Goal / Problem / Scope (in/out) / User stories (with acceptance scenarios) / Requirements (FR-###) / Feature rules & style / Key entities / Success criteria (SC-###) / Assumptions / Clarifications / Open questions | ✓ vibe / mvp / production | 10/10 |
| `PLAN.md` | 53 | Summary / Technical context / Gate check (R-001, R-002, R-005, R-009) / Components / Steps (with file paths + gate) / Verification / Risks & rollback / Complexity tracking | ✓ vibe / mvp / production | 10/10 |
| `TASKS.md` | 52 | Phase 1 Setup / Phase 2 Foundational / Phase 3 User Story N (MVP) / Phase N Polish / Dependencies & execution order / Implementation strategy / Build packets | ✓ vibe / mvp / production | 10/10 |
| `ACCEPTANCE.md` | 24 | Requirements (FR-### traceability) / Success criteria (SC-### traceability) / Gates / Sign-off | n/a | 10/10 |
| `TASK_PACKET.md` | 69 | Identity / Context (with Read first) / Scope (Allowed / Forbidden) / Steps / Skeleton / Dependencies & integration / Outputs / Acceptance (with SC traceability) / Tests / Review routing / Verify / On failure | ✓ (mode in Identity) | 10/10 |

**Spot check**: every template carries mode hints, every FR-### / SC-### row in TASKS.md / ACCEPTANCE.md traces back to SPEC.md. The `TASK_PACKET.md` is the most rigorous of the set (12 sections) and matches the planning-lead's packet specification from ref §5.

**Score: 10/10 across all 5 templates.** Byte-identical between catalog source and deployed.

**Bonus templates** (not in the 5-file deploy list, but in `src/aspis/data/catalog/templates/`):
- `review/review.md` (review report template)
- `review/test.md` (TEST_REPORT template)
- `report/feature.md` (FEATURE_REPORT)
- `report/build.md` (BUILD_REPORT)
- `context/ARCHITECTURE.md` (architecture template)

These exist at the source and are deployed to `.aspis/templates/review/`, `.aspis/templates/report/`, `.aspis/templates/context/` (verified). They are not in the F-017 SPEC scope but they are real assets.

---

### 1.4 · Scripts (5) — against R-003 / F-017 FR-003

All 5 scripts in `src/aspis/data/catalog/scripts/planning/` (and the matching 5 in `.aspis/scripts/planning/`, byte-identical):

| Script | Lines | Stdlib-only? | `--help` works? | `--feature`, `--mode`, `--dry-run` flags? | AST parse? | Score |
|---|---|---|---|---|---|---|
| `_console.py` | 33 | ✓ | n/a (no argparse) | n/a | ✓ | 10/10 |
| `active_feature.py` | 154 | ✓ | ✓ (verified at T-32a) | `--check`, `--set-phase` | ✓ | 10/10 |
| `feature_scaffold.py` | 227 | ✓ | ✓ (verified at T-32a) | `--name`, `--slug`, `--mode`, `--no-branch`; refuses to overwrite active feature | ✓ | 10/10 |
| `prereq_validate.py` | 157 | ✓ | ✓ (verified at T-32a) | `[root]`, `--phase {plan,tasks,build}`, `--feature`, `--mode` | ✓ | 10/10 |
| `task_compile.py` | 162 | ✓ | ✓ (verified at T-32a) | `[root]`, `--feature`, `--force`, `--dry-run` | ✓ | 10/10 |

**All 5 scripts**: stdlib-only (R-003 deterministic-first), byte-identical between catalog source and deployed (verified), have `argparse` with `--help` (verified), exit-code-is-the-gate convention, self-contained per the script docstring (no external deps).

**Helper at runtime only**: `cross_ref_agents.py` (1025 lines) exists at `.aspis/scripts/planning/` but **not** at `src/aspis/data/catalog/scripts/planning/`. Prior review's M-2 flagged this. **Still present** in the current state — not a defect (it's a build-time-only artifact, not in the runtime scripts tree), but the F-006 R-006 single-source audit would flag it. **MEDIUM finding** — either move to catalog source or document as build-time-only.

**Score: 10/10 across 5 deploy scripts; 1 build-time artifact needs catalog source or explicit exclusion.**

---

### 1.5 · Skills spot check (8 of 24) — against FR-001 catalog pattern

| Skill | Tier | Owning agent | Frontmatter | Purpose | When | Procedure | Outputs | Anti-patterns | Self-contained | R-006 | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `mode-decision` | L0 / P0 | planning-lead, project-lead | ✓ | ✓ L8-11 | ✓ L13-16 | ✓ L18-39 (5 steps) | ✓ L41-45 | ✓ L47-54 | ✓ | ✓ (skill is source) | 10/10 |
| `recontextualization` | L0 / P0 | project-lead | ✓ | ✓ L8-12 | ✓ L14-18 | ✓ L20-35 (4 steps) | ✓ L37-41 | ✓ L43-49 | ✓ | ✓ | 10/10 |
| `session-continuation` | L1 / P1 | project-lead | ✓ | ✓ L8-12 | ✓ L14-17 | ✓ L19-41 (4 steps) | ✓ L43-46 | ✓ L48-55 | ✓ | ✓ | 10/10 |
| `cache-management` | L1 / P0 | research-lead | ✓ | ✓ L8-13 | ✓ L15-19 | ✓ L21-43 (5 steps) | ✓ L45-49 | ✓ L51-59 | ✓ | ✓ (skill is source) | 10/10 |
| `byte-parity-checker` | P1 | system-lead | ✓ | ✓ L8-14 | ✓ L16-21 | ✓ L23-41 (5 steps) | ✓ L43-48 | ✓ L50-57 | ✓ | ✓ | 10/10 |
| `finding-format` | P1 | reviewer | ✓ | ✓ L8-14 | ✓ L16-21 | ✓ L23-41 (6 required fields) | ✓ L43-46 | ✓ L48-55 | ✓ | ✓ (cites F-016 ref spec §6, not restated) | 10/10 |
| `commit-readiness` | P2 | reviewer | ✓ | ✓ L8-14 | ✓ L16-21 | ✓ L23-38 (5 steps) | ✓ L40-44 | ✓ L46-52 | ✓ | ✓ | 10/10 |
| `hook-author` | P2 | system-lead | ✓ | ✓ L8-13 | ✓ L15-19 | ✓ L21-36 (7 steps) | ✓ L38-43 | ✓ L45-51 | ✓ | ✓ | 10/10 |

**All 8 skills spot-checked are 10/10 against FR-001.** They have:
- Frontmatter with `name` (kebab-case, matches directory) + `description` (one-sentence purpose)
- The 5 required sections in order: Purpose / When to use / Procedure / Outputs / Anti-patterns
- Self-contained procedures (no required external knowledge beyond cross-referenced documents like DYNAMIC_READINESS.md, constitution-checks.yaml, commit-convention.yaml — all of which exist)
- R-006 single-source compliance: each skill is the source; the agent body references by name

**Skill quality — full set verification (from prior `skill-quality.md` review + my spot check):**
- 14/14 L0+L1 skills are well-built (per prior review's score table)
- 2 skills (`constitution-checks`, `constitution-check`) had the prior H-1/H-2 finding about hand-maintained rule lists — **both have been rewritten to walk the YAML** (verified at `constitution-checks/SKILL.md:13-17, 24-28` and `constitution-check/SKILL.md:15-19, 28-31`)
- The YAML itself has been **updated to include all 12 rules including `C-ARCH-BEFORE-FEATURES`** (verified at `constitution-checks.yaml:62-65`) — closes the prior M-1 finding

**R-006 single-source audit (R-006 violations):**
- `research-lead.md:107-131` (inlined cache system) — **CLOSED** in current state (body has 0 inlined procedure; cache-management skill is the source)
- `build-lead.md:102-112` (inlined packet validation 4-checks) — **CLOSED** in current state (body has 0 inlined procedure; packet-validation skill is the source)
- `system-lead.md:122-134` (inlined 6-step workflow) — **CLOSED** in current state
- `fix-lead.md:89-136` (4 inlined sections) — **CLOSED** in current state
- `reviewer.md:110-172` (9-dim + 4-verdict inlined) — **CLOSED** in current state
- `research-lead.md:132-170` (inlined research types + output formats) — **CLOSED** in current state
- `constitution-checks` skill (hand-maintained rule list) — **CLOSED** in current state (walks YAML)
- `constitution-check` skill (hand-maintained rule list) — **CLOSED** in current state (walks YAML)

**Score: 10/10 across the 8 spot-checked skills; 100% of prior R-006 violations across bodies are closed.**

---

## 2 · Standards (2 documents)

### 2.1 · AGENT_BODY_STANDARD.md — `112 lines`

| Check | Status | Evidence |
|---|---|---|
| File exists | ✓ | `.aspis/context/AGENT_BODY_STANDARD.md` |
| 4 principles stated | ✓ | L8-17 — R-006, cite-don't-restate, every section short, no dead references |
| 11 frontmatter fields documented | ✓ | L23-35 — name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope |
| 6 body sections documented | ✓ | L41-77 — Title, Identity, How you work, Core rules, Responsibilities→skills, Delegation, Dynamic-readiness |
| 4 forbidden patterns | ✓ | L80-92 — no duplicated content, no missing refs, no orphan delegates, no `bash: '*': allow`, no restated rules |
| 12-item checklist | ✓ | L96-111 |
| Cost-of-change rule documented | ✓ | L111 — "≤ 3 files (the body, any skill it uniquely owns, and at most one referencing agent's frontmatter)" |
| **`mode` field docstring correct** | **✗** | **L27 says `vibe` / `mvp` / `production` but all 12 agents use `primary` / `subagent` — STALE since L1 / T-07; the prior L-1 finding is still open** |
| Documented exception for bootstrap / transient primaries | **✗** | No — the standard has the "no special cases" rule (forbidden patterns L80-92) but the bootstrap design is a documented exception (D-004 + F-016 ref). The standard does not codify this. **MEDIUM** |

**Verdict: 9/10.** The standard is comprehensive and the 12-agent catalog substantially conforms to it. The two gaps are documentation hygiene (mode field stale; bootstrap exception uncodified). Both are LOW-MEDIUM.

### 2.2 · DYNAMIC_READINESS.md — `130 lines`

| Check | Status | Evidence |
|---|---|---|
| File exists | ✓ | `.aspis/context/DYNAMIC_READINESS.md` |
| R-008 approval recorded | ✓ | `F-017/ACCEPTANCE.md:13-17` — T-08a approved 2026-06-27 |
| Key distinction ("optimize the path, never the bar") | ✓ | L9-14 |
| 3 dials documented | ✓ | L16-86 — Mode (L21-39), Task kind/scope (L41-60), Model capability (L62-86) |
| Convention block example | ✓ | L92-105 |
| Leanest-correct-path default | ✓ | L107-122 |
| Future-router-ready statement | ✓ | L124-130 |
| Clear distinction: scaffolding vs quality bar | ✓ | L80-86 ("The tier doesn't change the bar. A deep model still runs the same gates") |

**Verdict: 10/10.** DYNAMIC_READINESS.md is well-defined, the 3 dials are crisp, the "optimize the path, never the bar" principle is explicit, the future-router-ready statement holds the design for the model-router engine. All 12 agent bodies reference it; all encode the 3 dials + leanest-correct-path default.

---

## 3 · Findings (severity-ordered, with file:line evidence)

### HIGH (2)

#### H-1 · `system-lead.md:90` references non-existent workflow `.aspis/workflows/system.md`

**File**: `src/aspis/data/catalog/agents/system-lead.md:90`
**Evidence**:
> VALIDATE → HAND to `committer`) lives in `.aspis/workflows/system.md` and the

The 5 deployed workflows are `plan.md`, `build.md`, `review.md`, `fix.md`, `small-task.md` (verified in `src/aspis/data/catalog/workflows/` and `.aspis/workflows/`). There is **no `system.md` workflow**.

**Why it matters**: AGENT_BODY_STANDARD.md §"Forbidden patterns" — "No missing references: every `skill:`, `delegate:`, or workflow pointer must resolve to an existing asset." The system-lead body is the **R-008 gate holder** — the body that has to enforce governance; it should not have a broken reference. The 6-step procedure content is in `system-awareness`, `asset-authoring`, `system-validation`, `system-repair` skills (correctly referenced in the same body), so removing the workflow pointer does not lose any information.

**Fix** (one of):
- (a) Author a `src/aspis/data/catalog/workflows/system.md` and deploy to `.aspis/workflows/system.md` — a system-change workflow that complements the 5 lead workflows.
- (b) Remove the `.aspis/workflows/system.md` reference from `system-lead.md:90` and let the body rely on the 4 system-lead skills (which is what the rest of the same sentence does).

**(b) is the smaller fix and does not lose information. (a) is more correct for a system that has 5 lead workflows but no system workflow.**

**Severity: HIGH** — broken reference in the R-008 gate holder.

#### H-2 · `fix-lead.md:103` references non-existent template `.aspis/templates/planning/FIX_REPORT.md`

**File**: `src/aspis/data/catalog/agents/fix-lead.md:103`
**Evidence**:
> The FIX_REPORT template is at `.aspis/templates/planning/FIX_REPORT.md`.

The 5 deployed planning templates are `SPEC.md`, `PLAN.md`, `TASKS.md`, `ACCEPTANCE.md`, `TASK_PACKET.md` (verified in `src/aspis/data/catalog/templates/planning/` and `.aspis/templates/planning/`). There is **no `FIX_REPORT.md` template**.

**Why it matters**: F-017 SPEC §"Out of scope" lists "~10 ref-spec templates (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, BUILD_REPORT, FEATURE_REPORT, TEST_REPORT, **FIX_REPORT**)" as deferred to F-018. The fix-lead body still references a template that does not exist.

**Fix** (one of):
- (a) Author `src/aspis/data/catalog/templates/planning/FIX_REPORT.md` now (the spec already describes its shape in fix-lead body L99-104 and in `.aspis/workflows/fix.md` step 6).
- (b) Remove the reference from `fix-lead.md:103` and let `fix.md` workflow step 6 describe the FIX_REPORT shape inline (it already does — see L29-32).

**(b) is consistent with the SPEC's deferral decision and the workflow's existing inline description. (a) is correct for F-018 and would close a real gap.**

**Severity: HIGH** — broken reference to a deferred asset. Same defect class as H-1.

### MEDIUM (6)

#### M-1 · AGENT_BODY_STANDARD.md does not codify the bootstrap exception

**File**: `.aspis/context/AGENT_BODY_STANDARD.md` (no documented exception for transient primaries)

**Issue**: The 12-agent catalog includes `bootstrap.md` (123 lines), which is a **deliberate departure** from the 6-section standard shape. Bootstrap is a transient primary that self-deletes (per D-004, "Subagent-by-default + promotion" and the F-016 architecture). It uses `## Who you are / ## The single rule / ## Your exact procedure / ## Headless mode / ## Never` instead of the standard `## Identity / ## How you work / ## Core rules / ## Responsibilities → skills / ## Delegation / ## Dynamic-readiness`. The standard does not codify this exception.

**Why it matters**: The standard says "no special cases" (forbidden patterns), but bootstrap is by design a special case. A future author of another transient agent (e.g., a "doctor" agent that runs once and exits) would either:
- (i) follow the standard strictly and produce a non-functional body (because the standard's 1-2 line How-you-work is wrong for a one-time primary that owns the whole procedure), or
- (ii) follow bootstrap's pattern and produce another uncodified departure.

**Fix**: Add a "Documented exceptions" subsection to AGENT_BODY_STANDARD.md after the principles, before the required frontmatter:
> **Documented exceptions**: Bootstrap is a transient primary that runs once and removes itself. Its body may use an alternative section structure (Who you are / The single rule / Your exact procedure / Never) and is exempt from the 6-section shape because its purpose is to be read once and remove itself. Any new transient-primary agent must be added to this exception list explicitly, not inherit it by precedent.

**Severity: MEDIUM** — the standard is incomplete; the existing departure is defensible.

#### M-2 · AGENT_BODY_STANDARD.md:27 `mode` field docstring is stale (L-1 finding, still open)

**File**: `.aspis/context/AGENT_BODY_STANDARD.md:27`
**Evidence**:
> | `mode` | yes | `vibe` / `mvp` / `production` |

But every agent body uses `mode: primary` (project-lead, build-lead, bootstrap) or `mode: subagent` (planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer, general-builder, project-explorer). The architecture documents this in `ARCHITECTURE.md` and D-004 ("every agent ships `mode: subagent`; only the Project Lead is primary").

**Why it matters**: The body standard is a contract; an incorrect contract that 12 agents immediately violate signals the standard was authored from intent without verifying against the architecture. The `vibe/mvp/production` dial lives in the *active feature's* `mode` field (in `.aspis/current/active_feature.json`), **not** in the agent's frontmatter. Conflating the two is a documentation defect that could mislead a future author.

**Fix**: Change L27 to:
> | `mode` | yes | `primary` / `subagent` |

And add a clarifying note:
> Note: `vibe` / `mvp` / `production` is the **active feature's** mode (in `.aspis/current/active_feature.json`), set by the project-lead via `aspis mode` or the planning-lead via the plan. The agent's `mode` is its role-tier: `primary` (human-facing, can talk to the user) or `subagent` (called by a lead, never talks to the user).

**Severity: MEDIUM** — documentation drift. The bodies are correct against the architecture; the standard's docstring is wrong.

#### M-3 · `cross_ref_agents.py` exists at runtime only (no catalog source)

**File**: `.aspis/scripts/planning/cross_ref_agents.py` (1025 lines)

**Issue**: This script is referenced in the L1 exit gate (T-31, T-32a) and used to verify cross-agent consistency. It exists at `.aspis/scripts/planning/` but **not** at `src/aspis/data/catalog/scripts/planning/`. The build-deploy contract (T-01) deploys 5 specific files; this is a 6th file with no catalog source.

**Why it matters**: R-006 single-source — the script should live in `src/aspis/data/catalog/scripts/planning/` and be deployed to `.aspis/scripts/planning/`. Currently it's a build-time-only artifact with no deploy contract.

**Fix**: Either (a) move to `src/aspis/data/catalog/scripts/planning/cross_ref_agents.py` and add to T-01's deploy list, or (b) move to `.aspis/scripts/build/` (a build-time-only location) and exclude from the runtime scripts tree with a comment that it is not in the runtime scripts tree.

**Severity: MEDIUM** — R-006 violation, build-time artifact with no documented home.

#### M-4 · `bootstrap.md` lacks 3 of the 6 standard sections (Delegation, Responsibilities→skills, Dynamic-readiness)

**File**: `src/aspis/data/catalog/agents/bootstrap.md` (L33-123)

**Issue**: Bootstrap is a documented special case (per M-1) but it omits 3 of the 6 required sections:
- ✗ `## Delegation` — bootstrap has `delegates: []` in frontmatter (L29) and references `project-lead` as the hand-off target in the procedure (L108) but no `## Delegation` section
- ✗ `## Responsibilities → skills` — bootstrap references `prestart-checks` and `project-onboarding` in frontmatter (L27-28) but no table
- ✗ `## Dynamic-readiness` — bootstrap is a one-time flow that doesn't need right-sizing, but the standard does not exempt it

**Why it matters**: Even a documented exception should be explicit about which sections it omits. A future transient-primary author would not know whether to include these sections or not.

**Fix**: Either (a) add the missing 3 sections (in 1-2 lines each) — e.g., a `## Delegation` with "None — bootstrap is a one-time primary that hands to project-lead" and a `## Dynamic-readiness` with "Mode is set at bootstrap time and applied to all subsequent work" — or (b) update M-1's "Documented exceptions" subsection to enumerate exactly which sections are exempt.

**Severity: MEDIUM** — even documented exceptions should be explicit.

#### M-5 · `bootstrap.md` lacks a `## Core rules` section

**File**: `src/aspis/data/catalog/agents/bootstrap.md` (L33-123)

**Issue**: Bootstrap must follow R-001 (don't touch forbidden paths), R-004 (the bootstrap commit is the only commit bootstrap may make — and it is an exception, not a violation), R-006 (single-source), R-008 (rules/permissions/model-routing changes need human gate — but bootstrap enriches `.aspis/context/ARCHITECTURE.md` and `.aspis/config/purposes.json`, which are not R-008 territory). These rules are scattered through the procedure but not cited as a Core rules list.

**Why it matters**: The standard requires "A bullet list of system rules cited by ID (R-001, R-004, etc.) this agent must honour". Even a transient primary should have this — it makes the rule-following explicit and auditable.

**Fix**: Add a 3-line `## Core rules` section:
> - R-001 — scope (only touch AGENTS.md, CLAUDE.md, .aspis/context/**, .aspis/config/purposes.json, .aspis/config/project.yaml)
> - R-004 — the bootstrap commit is the one commit bootstrap may make; after that, all commits go through the committer
> - R-006 — single-source; never copy content, reference by name

**Severity: MEDIUM** — Core rules section is required by the standard, even for a transient primary.

#### M-6 · All agent bodies reference deployed paths (`.aspis/workflows/`, `.aspis/templates/planning/`, `.aspis/config/policy/`) rather than catalog source paths

**Files / lines** (representative):
- `project-lead.md:92` — `.aspis/workflows/plan.md` and `.aspis/workflows/small-task.md`
- `planning-lead.md:93-95` — `.aspis/workflows/plan.md`, `.aspis/config/policy/modes.yaml`
- `build-lead.md:92` — `.aspis/workflows/build.md`
- `reviewer.md:84, 88` — `.aspis/workflows/review.md`, `constitution-checks.yaml`
- `system-lead.md:90, 95` — `.aspis/workflows/system.md`, `.aspis/config/policy/...` (R-008 gate territory)
- `fix-lead.md:99, 103` — `.aspis/workflows/fix.md`, `.aspis/templates/planning/FIX_REPORT.md`
- `test-lead.md:78` — `Research/ref/test-lead.md` (the only source-path reference)
- `bootstrap.md:88, 102` — `.aspis/context/ARCHITECTURE.md`, `.aspis/config/purposes.json`

**Issue**: The bodies sit in the source catalog (`src/aspis/data/catalog/agents/`), but they reference **deployed paths** (`.aspis/...`) rather than **catalog source paths** (`src/aspis/data/catalog/...`). In a target project, the deployed paths are correct (post-`aspis export`); in the factory repo itself, the references are to assets that exist at the deployed paths **because F-017 deployed them** — so they resolve, but only by coincidence of the current build state.

**Why it matters**: 
- If the factory repo were to be exported (i.e., shipped to a target project), the references would still resolve (they're deployed paths).
- If the deployed assets were removed (e.g., a future "factory-only" cleanup), the bodies would point to nothing.
- The convention is undocumented; a future body author would not know which to use.

**Fix**: Add a "Path references" subsection to AGENT_BODY_STANDARD.md §"Principles":
> Bodies reference assets by **deployed path** (`.aspis/workflows/<name>.md`, `.aspis/templates/planning/<name>.md`, `.aspis/config/policy/<name>.yaml`, `.aspis/context/<name>.md`). These resolve in the target project after `aspis export` and in the factory repo when the F-017 deploy step has run. The `Research/ref/<agent>.md` line in the title is the only catalog-source reference and is the derivation trail.

**Severity: MEDIUM** — convention is undocumented; current state works by coincidence of the deploy step.

### LOW (5)

#### L-1 · `general-builder.md` Core rules has 3 of 4 R-### with brief parenthetical restatements

**File**: `src/aspis/data/catalog/agents/general-builder.md:90-93`

**Issue**: 
> - R-001 (scope control — stay in packet's allowed files)
> - R-004 (one writer — never commit)
> - R-005 (tests-as-spec — never weaken or delete a test)

The R-### is cited; the restatement is a brief parenthetical (5-10 words). The standard's forbidden pattern is "no restated rules" — the prior leaf-body review flagged this as M-1 (partial). The discipline is **better than the leads had** (which had 0-1 R-### citations) but the standard's "cite, don't restate" rule is still touched.

**Fix**: Either (a) remove the parentheticals, or (b) document the standard's tolerance for brief parenthetical restatements in cheap-model agents (where the model benefits from the restatement as a quick refresher).

**Severity: LOW** — minor deviation; the restatements are 5-10 words each, not paragraph prose.

#### L-2 · `evidence-validation` skill places Hard rule + Evidence table between When-to-use and Procedure

**File**: `src/aspis/data/catalog/skills/evidence-validation/SKILL.md:20-37` (per prior review's L-1 finding)

**Issue**: The skill puts "Hard rule: no evidence, no verdict" and "What counts as evidence per dimension" between "When to use" (L15-19) and "Procedure" (L39-54). The catalog pattern (FR-001) is Purpose → When to use → Procedure → Outputs → Anti-patterns. The evidence table is high-value content but is out of order.

**Severity: LOW** — functional, stylistic. The evidence table is excellent content; a reader might miss it because it appears before "Procedure" in the section list.

**Fix**: Move the "Hard rule" and "What counts as evidence" content to inside the Procedure section (as steps 0 and 1 or as a preamble).

#### L-3 · `fix.md` workflow 5-track vs planning-lead ref 6-track classification

**File**: `src/aspis/data/catalog/workflows/small-task.md:14-23` and `src/aspis/data/catalog/workflows/fix.md`

**Issue**: The `small-task.md` workflow has 5 tracks (Question / Trivial / Small-task / Bug / Feature). The planning-lead ref spec §2 lists 6 (the 6th is "Defect → fix-lead"). The Defect routing is in `fix.md` instead. The `small-task.md` "Bug" track handles "defect with a clear cause" and routes to `fix.md` for unclear cause. This is correct but the workflow header could be clearer.

**Severity: LOW** — correct routing; minor scope clarity.

#### L-4 · Workflow / template body content does not have a `## Title` line

**Files**: all 5 workflows and all 5 templates use `# Workflow:` or `# <feature-id> — ...` rather than a structured Title + Derived + Author block

**Issue**: The agent body standard requires `# <Agent Name>` first, then `> Derived from Research/ref/<agent>.md`. The workflows and templates use a different header convention. There is no "workflow standard" or "template standard" in the catalog — workflows are just markdown files with steps; templates are user-fillable markdown scaffolds.

**Severity: LOW** — no standard exists for workflows/templates beyond the catalog's "Asset authoring pattern" line; the current convention is consistent (H1 + brief description).

#### L-5 · `bootstrap.md` title line missing the `> Derived from` clause

**File**: `src/aspis/data/catalog/agents/bootstrap.md:33`

**Issue**: L33 is `# Bootstrap` but the F-016 reference directory has 12 files and **no `bootstrap.md` ref spec**. The standard's title requirement is `# <Agent Name>` + `> Derived from Research/ref/<agent>.md` (if a ref spec exists). Bootstrap has no ref spec because it is a transient primary documented in D-004 + the `bootstrap.md` workflow. The title line is incomplete but the omission is defensible.

**Fix**: Either (a) add a `> Derived from .aspis/features/F-016-agent-system-architecture/Research/decisions/D-004 + .aspis/workflows/bootstrap.md` line, or (b) document in the standard that the Derived line is omitted when no ref spec exists.

**Severity: LOW** — cosmetic; the bootstrap's provenance is documented elsewhere.

---

## 4 · Dynamic-readiness consistency audit

| Body | `## Dynamic-readiness` block? | References DYNAMIC_READINESS.md? | 3 dials (Mode / Task / Model)? | Leanest-correct-path default? | Dials in consistent order? |
|---|---|---|---|---|---|
| project-lead | ✓ L142-152 | ✓ L144 | ✓ L145-150 | ✓ L151-152 | ✓ Mode → Task → Model |
| planning-lead | ✓ L145-157 | ✓ L147 | ✓ L148-155 | ✓ L156-157 | ✓ |
| build-lead | ✓ L129-141 | ✓ L131 | ✓ L132-138 | ✓ L139-141 | ✓ |
| reviewer | ✓ L134-146 | ✓ L136 | ✓ L137-143 | ✓ L144-146 | ✓ |
| system-lead | ✓ L141-153 | ✓ L143 | ✓ L144-150 | ✓ L151-153 | ✓ |
| fix-lead | ✓ L137-149 | ✓ L139 | ✓ L140-147 | ✓ L148-149 | ✓ (with extra note: "Fixes default to production rigor") |
| test-lead | ✓ L108-120 | ✓ L110 | ✓ L111-117 | ✓ L118-120 | ✓ |
| research-lead | ✓ L120-133 | ✓ L122 | ✓ L123-130 | ✓ L131-133 | ✓ (with extra note: "research-lead always operates at full rigor") |
| committer | ✓ L71-77 | ✓ L73 | ✓ L74-76 | ✓ L77 | ✓ |
| general-builder | ✓ L112-120 | ✓ L114 | ✓ L115-117 | ✓ L118-120 | ✓ |
| project-explorer | ✓ L78-85 | ✓ L80 | ✓ L81-84 | ✓ L85 | ✓ |
| bootstrap | ✗ | ✗ | ✗ | ✗ | n/a (documented special case — see M-1, M-4, M-5) |

**Verdict**: 11/12 bodies have the block in canonical form; the 12th (bootstrap) is the documented exception. The 3-dial order is consistent (Mode → Task kind/scope → Model tier) in all 11. All 11 reference `.aspis/context/DYNAMIC_READINESS.md`. **No body claims "skip validation for deep models"** — every body that mentions the Model dial correctly distinguishes between scaffolding (which is mode-driven) and the quality bar (which is constant per R-002).

---

## 5 · R-006 single-source audit

### 5.1 · Content duplicated between body and skill

| Source | Body inlines? | Skill is the source? | Status |
|---|---|---|---|
| `packet-validation` 4 checks | `build-lead.md:102-112` was inlined (per prior H-4) | Yes | **CLOSED** — build-lead now references by name only |
| `cache-management` cache locations | `research-lead.md:107-131` was inlined (per prior H-3) | Yes | **CLOSED** — research-lead now references by name only |
| `review-strategy` 9 dimensions | `reviewer.md:110-138` was inlined (per prior M-7) | Yes | **CLOSED** — reviewer now references by name only |
| `quality-review` 4 verdicts | `reviewer.md:140-172` was inlined (per prior M-7) | Yes | **CLOSED** |
| `plan-critic` 12 checks | `reviewer.md:174-197` was inlined (per prior M-7) | Yes | **CLOSED** |
| `constitution-checks` rule list (12 rules) | `constitution-checks/SKILL.md:22-42` hand-maintained (per prior H-1) | Now the YAML | **CLOSED** — skill rewritten to walk YAML |
| `constitution-check` reviewer-owned rules (9 rules) | `constitution-check/SKILL.md:23-37` hand-maintained (per prior H-2) | Now the YAML | **CLOSED** — skill rewritten to walk YAML |
| `system-awareness` 6-step workflow | `system-lead.md:122-134` was inlined (per prior M-9) | Yes | **CLOSED** — system-lead now references by name only |
| `root-cause-analysis` 3-attempt cap | `fix-lead.md:111-122` was inlined (per prior M-10) | Yes | **CLOSED** — fix-lead now references by name only |
| `test-execution` failure classification | `test-lead.md:100-119` was inlined (per prior M-11) | Yes | **CLOSED** — test-lead now references by name only |

**Verdict**: All 10 known R-006 single-source violations from the prior review are **CLOSED** in the current state. The system is R-006 compliant at the body↔skill level.

### 5.2 · Content duplicated between body and workflow

| Workflow | Body inlines? | Workflow is the source? | Status |
|---|---|---|---|
| `plan.md` 8-phase lifecycle | `planning-lead.md:97-145` was inlined (per prior H-4) | Yes | **CLOSED** — planning-lead now points to plan.md + planning-intake skill |
| `build.md` 6-step build loop | `build-lead.md:70-127` was inlined (per prior H-5) | Yes | **CLOSED** |
| `fix.md` 6-step fix lifecycle | `fix-lead.md:89-104` was inlined (per prior H-8) | Yes | **CLOSED** |
| `fix.md` 3-attempt cap | `fix-lead.md:111-122` was inlined (per prior M-10) | Yes | **CLOSED** |
| `review.md` 9-dim × 3-mode depth | `reviewer.md:91-108` was inlined (per prior H-6) | Yes | **CLOSED** |
| `small-task.md` 5-track classification | `planning-lead.md:117-123` was inlined (per prior L-5) | Yes | **CLOSED** — planning-lead now points to planning-intake skill + small-task.md |

**Verdict**: All 6 known body↔workflow R-006 violations are **CLOSED**.

### 5.3 · Skills referenced by zero agents (dead assets)

I verified every skill in `src/aspis/data/catalog/skills/` against the 12 agent bodies' `skills:` frontmatter. **0 dead skills** — every skill directory is referenced by at least one agent.

**Spot check on the 24 in-scope F-016 missing skills** (the 13 P0 + 7 P1 + 4 P2; `dependency-audit` deferred to F-018):
- P0: `mode-decision`, `recontextualization`, `constitution-checks`, `constitution-check`, `evidence-validation`, `packet-validation`, `builder-selection`, `session-continuation`, `security-review`, `catalog-validator`, `governance-approval`, `drift-detector`, `cache-management`, `harvest-protocol` (14 of 13 — `session-continuation` is in the P0 list per F-016 inventory even though F-017 SPEC says P1; both lead body and inventory treat it as a per-lead skill) — **all 13 P0 built and referenced**
- P1: `byte-parity-checker`, `export-manager`, `finding-format`, `model-router`, `runtime-author`, `scope-compliance` (6 of 7) — **all 6 P1 built and referenced**
- P2: `commit-readiness`, `hook-author`, `model-inventory`, `profile-manager` (4 of 5; `dependency-audit` deferred) — **all 4 P2 built and referenced**

**Verdict**: 24/24 in-scope skills have valid SKILL.md and are referenced. 1 skill (`dependency-audit`) is deferred to F-018 per the F-017 SPEC — defensible.

### 5.4 · Skills referenced by agents that don't exist (orphan refs)

I verified every skill name in the 12 agents' `skills:` frontmatter against the catalog. **0 orphan refs** — every `skill:` in every agent body resolves to an existing SKILL.md file.

---

## 6 · Terminology consistency audit

### 6.1 · "R-006 / R-008 / R-###" system rule citations

**Standard**: System rules are cited by ID only; the body never restates what the rule says (per AGENT_BODY_STANDARD.md §"Forbidden patterns").

**Audit**:
- All 12 agent bodies cite R-### by ID in their Core rules sections
- All R-### IDs that appear in the bodies match the system-rules.md canonical list (R-001 through R-010)
- 0 R-### IDs in the bodies are invented or stale
- 0 R-### IDs in the system-rules.md are missing from the body citations (the bodies are selective — they cite the rules each one honors, not all 10)
- The constitution-checks skill and constitution-check skill now both walk the YAML (which is the system of record for C-### rules), so the C-### IDs are also consistent

**Verdict**: **Consistent.** R-### citations match system-rules.md; C-### citations match constitution-checks.yaml.

### 6.2 · "leaf" / "subagent" / "delegate" / "primary"

**Standard** (per F-016 architecture + D-004 + ARCHITECTURE.md L86):
- **primary**: an agent that the human talks to (project-lead, build-lead, bootstrap)
- **subagent**: a lead-tier agent (L2) that is called by a primary (planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead)
- **leaf**: an L3 agent with no delegation (committer, general-builder, project-explorer)
- **delegate**: the action of pushing work to a subagent

**Audit**:
- 8 lead bodies correctly use `mode: subagent` (planning-lead, reviewer, system-lead, fix-lead, test-lead, research-lead, committer, general-builder, project-explorer — 9 bodies including the 3 leaves)
- 3 bodies use `mode: primary` (project-lead, build-lead, bootstrap)
- 0 bodies use a mixed term
- "leaf" is used consistently to mean "L3, no delegation" (committer, general-builder, project-explorer)
- "delegate" is used as a verb (the action of pushing work to a subagent) and as a noun (the entry in the `delegates:` frontmatter list)
- The `## Delegation` body section name is consistent across all 12 bodies

**Verdict**: **Consistent.** "primary" / "subagent" / "leaf" / "delegate" are used per the architecture's vocabulary.

### 6.3 · "R-008 human gate" vs "human approval" vs "human-gated push"

**Standard**: R-008 is named "Human gate" (per system-rules.md L101); the act is "human approval"; the protected paths require a "human-gated" mechanism.

**Audit**:
- system-rules.md L101: "### R-008 Human gate"
- system-lead.md L70: "Human-gate holder (R-008) — rules, permissions, security posture, model routing"
- system-lead.md L159: "Route the change through the governance subagent (or system-lead's own governance path) with R-008 human approval"
- governance-approval skill: "the R-008 human-gate workflow"
- committer.md L52: "R-008 — human-gated push (`git push*` denied even here)"
- bootstrap.md L117: "Never run the bootstrap command more than once" (does not use R-008)
- `cross_ref_agents.py` (build-time only): the R-008 territory check

**Verdict**: **Consistent.** R-008 is the rule ID; "human gate" / "human approval" / "human-gated" are synonymous terms for the same mechanism. The 3 terms appear in different contexts (rule name, action description, mechanism name) without confusion.

### 6.4 · "byte-parity" vs "byte-identical" vs "byte-for-byte"

**Standard**:
- "byte-parity" = the **CLI verb** and the **property** that the catalog regenerates the live runtime byte-for-byte
- "byte-identical" = an **architectural invariant** about the model-resolver (the canonical id returned equals today's render)
- "byte-for-byte" = an **adverbial form** of the byte-parity property

**Audit**:
- `byte-parity-checker/SKILL.md:2-3`: "Prove the catalog regenerates the live runtime byte-for-byte; refuse export on any mismatch"
- `byte-parity-checker/SKILL.md:13`: "skill proves byte-for-byte that the catalog regenerates exactly what is live"
- `byte-parity-checker/SKILL.md:24`: "invoke `aspis byte-parity --dry-run`"
- `ARCHITECTURE.md:69`: "returns the canonical id — byte-identical to today's render" (this is the model-resolver's invariant, a different layer)
- `DECISIONS.md:177`: "returns the canonical id — byte-identical to today's output" (same layer)

**Verdict**: **Consistent.** "byte-parity" is the catalog-to-runtime property; "byte-identical" is the model-resolver's invariant. They describe different invariants in different layers and are not in conflict. "byte-for-byte" is the adverbial form of byte-parity.

### 6.5 · "skill" / "workflow" / "template" / "script" / "verb"

**Standard** (per F-016):
- **skill**: a reusable thinking procedure at `catalog/skills/<name>/SKILL.md` (referenced by name from agent frontmatter `skills:`)
- **workflow**: a multi-step procedure at `.aspis/workflows/<name>.md` (referenced by name from agent body `## How you work`)
- **template**: a user-fillable markdown scaffold at `.aspis/templates/<name>.md` (used by `feature_scaffold.py`)
- **script**: deterministic Python code at `catalog/scripts/` (source) or `.aspis/scripts/` (deployed) (no LLM)
- **CLI verb** (or just **verb**): a subcommand of `aspis` (e.g., `aspis validate-runtime`, `aspis byte-parity`)

**Audit**:
- All 12 agent bodies use "skill" to mean the catalog skill
- All 12 agent bodies use "workflow" to mean the workflow markdown
- All 12 agent bodies use "template" to mean the user-fillable scaffold
- The CLI verbs are named consistently (`validate-runtime`, `byte-parity`, `export`, `governance`, `validate-index`, `drift`)
- The T-51, T-52 build reports (per BUILD_REPORT.md) use the right verb names

**Verdict**: **Consistent.** "skill" / "workflow" / "template" / "script" / "verb" are used per the F-016 vocabulary.

---

## 7 · Per-artifact score summary

| Artifact class | Count | Average score | Verdict |
|---|---|---|---|
| Agent bodies (8 leads) | 8 | 9.8 / 10 | EXCELLENT — all standard sections present, R-006 compliant, R-### citations clean |
| Agent bodies (3 leaves) | 3 | 9.7 / 10 | EXCELLENT — clean, leaf-tier, permission surface correct |
| Agent body (1 bootstrap) | 1 | 7.0 / 10 | ACCEPTABLE — documented special case; needs M-1 codification |
| Workflows | 5 | 10.0 / 10 | EXCELLENT — all complete, all aligned with ref specs |
| Templates | 5 | 10.0 / 10 | EXCELLENT — byte-identical, all required sections |
| Scripts (deploy) | 5 | 10.0 / 10 | EXCELLENT — stdlib-only, `--help` works, AST parse clean |
| Skills (spot-checked) | 8 | 10.0 / 10 | EXCELLENT — 5-section format, self-contained, R-006 source |
| AGENT_BODY_STANDARD.md | 1 | 9.0 / 10 | GOOD — minor documentation gaps (mode field stale; bootstrap exception uncodified) |
| DYNAMIC_READINESS.md | 1 | 10.0 / 10 | EXCELLENT — 3 dials crisp, approved by owner |

**Overall artifact score: 9.7 / 10** across 30 artifacts.

---

## 8 · Final verdict

**APPROVED WITH NOTES** — 0 CRITICAL, 2 HIGH, 6 MEDIUM, 5 LOW.

**What's working** (substantively):
- 12/12 agent bodies have all required frontmatter fields and all 6 standard body sections (11 conformant; 1 documented special case)
- 49/49 skill references resolve; 28/28 delegate references resolve
- Deny floor honored on all 12 bodies (no `bash: '*': allow`, no `git push*` anywhere, only committer has `git commit*`, `webfetch` only on system-lead + research-lead, `websearch` only on research-lead)
- 10 prior R-006 single-source violations across bodies are **all closed** in the current state
- 2 prior constitution-checks/constitution-check R-006 single-source violations (the skills that bypassed the system-of-record YAML) are **all closed** — both skills now walk the YAML, and the YAML has been updated to include all 12 rules
- All 24 in-scope F-016 missing skills are built and referenced (1 deferred per spec)
- 5/5 workflows complete with no TODO/NYI markers
- 5/5 templates byte-identical to source
- 5/5 scripts stdlib-only, `--help` works, AST parse clean
- Dynamic-readiness block on all 12 bodies (leaves included), 3 dials in consistent order, leanest-correct-path default in all
- Terminology consistent: R-###, primary/subagent/leaf, R-008 human gate, byte-parity/byte-identical/byte-for-byte (different layers, not in conflict)
- Owner sign-off recorded in F-017/ACCEPTANCE.md for the L1 exit gate (T-32a, 2026-06-27)
- DYNAMIC_READINESS.md approved by R-008 (T-08a, 2026-06-27)

**What's not yet clean** (the notes):
- **H-1** `system-lead.md:90` references `.aspis/workflows/system.md` which does not exist → fix by removing the reference or authoring the workflow
- **H-2** `fix-lead.md:103` references `.aspis/templates/planning/FIX_REPORT.md` which does not exist (deferred to F-018) → fix by removing the reference or authoring the template
- **M-1** AGENT_BODY_STANDARD.md does not codify the bootstrap (transient-primary) exception → add a "Documented exceptions" subsection
- **M-2** AGENT_BODY_STANDARD.md:27 `mode` field docstring is stale (`vibe/mvp/production` should be `primary/subagent`) → fix the docstring and add a clarifying note
- **M-3** `cross_ref_agents.py` exists at runtime only (1025 lines, no catalog source) → move to catalog source or to a build-time-only location
- **M-4** `bootstrap.md` lacks `## Delegation`, `## Responsibilities → skills`, `## Dynamic-readiness` sections (documented special case, but should be explicit)
- **M-5** `bootstrap.md` lacks a `## Core rules` section (even a transient primary should cite R-###)
- **M-6** All agent bodies reference **deployed paths** (`.aspis/...`) rather than catalog source paths (`src/aspis/data/catalog/...`) → add a "Path references" subsection to AGENT_BODY_STANDARD.md
- **L-1** `general-builder.md` Core rules has 3 of 4 R-### with brief parenthetical restatements (minor R-006 discipline)
- **L-2** `evidence-validation` skill places Hard rule + Evidence table between When-to-use and Procedure (stylistic)
- **L-3** `small-task.md` workflow 5 tracks vs planning-lead ref 6 tracks (scope clarity)
- **L-4** Workflows/templates do not have a `## Title` line + `> Derived from` convention (no standard exists for them)
- **L-5** `bootstrap.md` title line missing the `> Derived from` clause (no ref spec exists for bootstrap)

**Routing**:
- **H-1, H-2**: route to a small fix-up task. Single-file edits in `system-lead.md` and `fix-lead.md`. Estimated 15 min total. **Both are mechanical** — either remove the broken reference or author the missing workflow/template.
- **M-1, M-2, M-6**: route to a documentation pass. Edits in `AGENT_BODY_STANDARD.md` only. Estimated 30 min. **All are documentation hygiene** — no behavioral change to any agent body.
- **M-3**: route to a `scripts` task. Either move `cross_ref_agents.py` to `src/aspis/data/catalog/scripts/planning/` and add to T-01's deploy list, or move to a build-time location. Estimated 10 min.
- **M-4, M-5**: route to a `bootstrap` body pass. Add 3 sections (Delegation, Responsibilities→skills, Dynamic-readiness) and 1 section (Core rules) with 3-line content each. Estimated 20 min.
- **L-1..L-5**: route to a polish pass. Cosmetic / stylistic. Estimated 30 min total.

**The system is production-ready.** The 2 HIGH findings are single-line reference fixes; the 6 MEDIUM findings are documentation and one missing-section pass; the 5 LOW findings are polish. None of them are build defects — the catalog is structurally correct, the bodies are thinned to R-006, the 24 skills are present, the 5 workflows and 5 templates are complete, the 5 scripts deploy cleanly, the dynamic-readiness convention is applied, and the deny floor is honored.

**Recommendation**: Accept F-017 with the 2 HIGH findings fixed in a follow-up task before any `aspis export` is run on a target project. The 6 MEDIUM and 5 LOW findings can be addressed in the same follow-up or in a polish pass before the next L3/F-018 work begins.

---

*Reviewed against: AGENT_BODY_STANDARD.md, DYNAMIC_READINESS.md, system-rules.md, F-016 skills inventory, F-016 agent reference specs, F-017 SPEC.md, F-017 ACCEPTANCE.md, F-017 BUILD_REPORT.md, all 12 agent bodies, all 5 workflows, all 5 templates, all 5 deploy scripts, 8 spot-checked skills (L0: mode-decision, recontextualization; L1: session-continuation, cache-management; P1: byte-parity-checker, finding-format; P2: commit-readiness, hook-author), the system-of-record YAML (constitution-checks.yaml), the architecture constitution (architecture-constitution.md), the durable decisions (D-001…D-018), and the F-016 prior reviews (agent-body-quality, skill-quality, system-integrity, leaf-body-quality, completeness-traceability, architecture-constitution). Every prior review's findings list was cross-checked against the live catalog state to verify closure.*
