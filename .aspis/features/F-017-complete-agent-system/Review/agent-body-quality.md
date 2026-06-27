# F-017 — Agent Body Quality Review

> **Reviewer**: Reviewer (independent)
> **Date**: 2026-06-27
> **Scope**: F-017 Phase 0–2 — 8 lead agent bodies, AGENT_BODY_STANDARD, DYNAMIC_READINESS
> **Perspective**: Agent body quality (the contract every body must satisfy)
> **Verdict**: **CHANGES REQUIRED** — 2 CRITICAL, 7 HIGH, 9 MEDIUM, 7 LOW findings

---

## Executive summary

F-017 Phase 0–2 produces 8 lead agent bodies (project-lead, planning-lead, build-lead,
reviewer, system-lead, fix-lead, test-lead, research-lead) that match the **shape** the
AGENT_BODY_STANDARD requires (frontmatter, Identity, How-you-work, Core rules,
Responsibilities→skills, Delegation, Dynamic-readiness, all with the correct
dynamic-readiness block). All 49 skill references resolve to existing SKILL.md files;
all 28 delegate references resolve to existing catalog agents; permissions are
least-privilege with the universal deny floor honored; DYNAMIC_READINESS.md is approved
and referenced; the F-016 reference specs are faithfully distilled.

**However**, when measured against the standard's "every section is short" and
"cite, don't restate" requirements, the bodies systematically **violate R-006** by
inlining long procedures that the standard says belong in skills/workflows. The
reviewer's role is to flag this as a finding, not to let it pass because the
"shape" looks right. Two bodies (project-lead, research-lead) are also missing
the required `## Delegation` section, and one body (build-lead) has a markdown
heading hierarchy typo (`# Identity` instead of `## Identity`).

**Standards compliance at a glance**

| Standard check | Result |
|---|---|
| Frontmatter has 11 required fields | ✓ 8/8 (with `mode: primary/subagent` instead of `vibe/mvp/production` — see Finding L-1) |
| Identity 2–4 lines with IS/IS NOT/prime directive | ✗ 4/8 have full IS/IS NOT/prime; 2/8 are short (project-lead, build-lead) |
| How-you-work 1–2 lines + workflow pointer | ✗ 2/8 missing the section; 6/8 have similar but different titles and are 7–16 lines of inlined procedure |
| Core rules cite R-### by ID only | ✗ 5/8 restate rules in prose (project-lead, planning-lead, build-lead, fix-lead, research-lead) |
| Responsibilities→skills table complete | ✓ 8/8 — every responsibility mapped, every skill resolves |
| Delegation section present | ✗ 2/8 missing (project-lead, research-lead) |
| Dynamic-readiness block + reference | ✓ 8/8 |
| No inline procedure duplication | ✗ 8/8 inline procedures that should be in skills/workflows |
| Skill refs resolve to SKILL.md | ✓ 49/49 |
| Delegates exist as catalog agents | ✓ 28/28 (the planning-lead M-2 violation from prior review is **fixed** in the current body) |
| Permission least-privilege + deny floor | ✓ 8/8 — no `bash: '*': allow`, no `git commit*` (committer only), no `git push*` anywhere, `webfetch` only on system-lead/research-lead, `websearch` only on research-lead |
| Cost-of-change ≤ 3 files | ✓ verified at T-32a (FR-019) |

---

## 1 · Body-by-body check

### 1.1 · project-lead — `src/aspis/data/catalog/agents/project-lead.md` (193 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L2–L55 |
| Title line | ✗ reversed order | L58: `> Derived…` precedes L60: `# Project Lead` (standard: title first) |
| Identity | ✗ only IS, no IS NOT, no prime directive | L62–L69 (8 lines, single-paragraph) |
| How you work | ✗ MISSING | No `## How you work`; closest is L161–L175 `## Handling a request` (15 lines inlined, no workflow pointer) |
| Core rules | ✗ restate, no R-### cited | L93–L107 — 8 bullets, **zero** R-### citations |
| Responsibilities→skills | ✓ | L109–L122 (7 responsibilities, all map to existing skills) |
| Delegation | ✗ MISSING | Delegates only in frontmatter (L33–L41); no body `## Delegation` section |
| Dynamic-readiness | ✓ | L184–L193 — references `.aspis/context/DYNAMIC_READINESS.md`, three dials + leanest-correct-path default |
| Inline procedure | ✗ | L161–L175 inlines orchestration procedure (should reference `.aspis/workflows/` or a skill) |
| Bootstrap gate | ⚠ | L141–L158 inlines a non-standard "First-run gate" block — not in the standard, but defensible as a pre-bootstrap safety |

**Findings**: H-1, H-2, H-3, M-1, M-2, M-3, L-2

### 1.2 · planning-lead — `src/aspis/data/catalog/agents/planning-lead.md` (209 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L56 |
| Title line | ✓ | L59, L61 |
| Identity | ✓ full IS/IS NOT/prime | L63–L95 — has IS, IS NOT, prime directive (L75–L79) |
| How you work | ⚠ | L97–L109 `## How you plan` — references `.aspis/workflows/plan.md` but is 8 lines and titled differently |
| Core rules | ✗ restate, no R-### cited | L147–L166 — 11 bullets, **zero** R-### citations |
| Responsibilities→skills | ✓ | L167–L184 (11 rows with phase column) |
| Delegation | ✓ | L186–L196 — lists research-lead, reviewer, project-explorer |
| Dynamic-readiness | ✓ | L198–L209 |
| Inline procedure | ✗ | L111–L123 inlines the 5-track table; L125–L145 inlines the mode dial; both duplicate content from plan.md and planning-intake skill |
| M-2 fix verified | ✓ | L37–L40 — delegates list cleaned up (only 3 existing catalog agents; the 7 orphan subagents from F-016 ref spec are correctly **not** in the delegates) |

**Findings**: H-4, M-4, L-2, L-3

### 1.3 · build-lead — `src/aspis/data/catalog/agents/build-lead.md` (195 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L54 |
| Title line | ✓ | L56, L58 |
| Identity | ✗ heading typo + no IS NOT | L60 `# Identity` is H1 (single `#`), not `## Identity` H2 — breaks the heading hierarchy that all 11 other bodies use; L60–L68 has IS + prime directive but no IS NOT section |
| How you work | ⚠ | L70–L101 `## How you execute — the build loop` — references `.aspis/workflows/build.md` but is 32 lines with inlined packet-validation and builder-security tables |
| Core rules | ✗ restate, 1 R-### cited | L138–L162 — 9 bullets; only L79 mentions R-002 (in a sub-bullet, not the Core rules section itself); Core rules section has **zero** R-### citations |
| Responsibilities→skills | ✓ | L164–L173 (6 rows) |
| Delegation | ✓ | L175–L182 — lists 7 delegates (general-builder, reviewer, test-lead, fix-lead, committer, project-explorer, research-lead), all exist |
| Dynamic-readiness | ✓ | L184–L194 |
| Inline procedure | ✗ | L102–L112 packet-validation table; L114–L127 builder-security rules; L129–L136 tier cascade. All restate content from `task-orchestration`, `packet-validation`, `builder-selection` skills |
| Path mismatch | ⚠ | L72 `.aspis/workflows/build.md` — actual path is `src/aspis/data/catalog/workflows/build.md` |

**Findings**: C-1, H-5, M-5, M-6, L-2

### 1.4 · reviewer — `src/aspis/data/catalog/agents/reviewer.md` (255 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L46 |
| Title line | ✓ | L48, L50 |
| Identity | ✓ full IS/IS NOT/prime | L52–L77 — IS (L62–L69), IS NOT (L71–L77), prime directive (L60) |
| How you work | ⚠ | L91–L108 `## How you review` — references `.aspis/workflows/review.md` but is 18 lines |
| Core rules | ⚠ 1 R-### cited | L199–L220 — 8 bullets; only R-004 cited (L204). Missing: R-001, R-002, R-005, R-006, R-008, R-009, R-010 citations |
| Responsibilities→skills | ✓ | L222–L233 (8 rows) |
| Delegation | ✓ | L235–L242 — project-explorer + research-lead |
| Dynamic-readiness | ✓ | L244–L255 |
| Inline procedure | ✗ | L110–L138 inlines 9-dimensions table; L140–L172 inlines 4-verdict system + severity rubric + finding format; L174–L197 inlines 12 plan-critic checks. All of this belongs in `review-strategy`, `quality-review`, `acceptance-decision`, `plan-critic` skills |
| Path mismatch | ⚠ | L93 `.aspis/workflows/review.md`; L209 `.aspis/config/constitution-checks.yaml` — actual paths are `src/aspis/data/catalog/workflows/review.md` and `src/aspis/data/catalog/config/policy/constitution-checks.yaml` |

**Findings**: H-6, M-7, M-8, L-2, L-3

### 1.5 · system-lead — `src/aspis/data/catalog/agents/system-lead.md` (243 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L48 |
| Title line | ✓ | L51, L53 |
| Identity | ✓ full IS/IS NOT/prime | L55–L95 — IS (L67–L78), IS NOT (L80–L87), prime directive (L89–L95) |
| How you work | ✗ 13 lines inlined | L122–L134 `## How you work — the 6-step workflow` — 6 steps inlined as numbered list instead of pointing to a workflow |
| Core rules | ⚠ 2 R-### cited | L158–L186 — 8 bullets; R-008 cited (L179), R-004 cited (L180). Missing R-001, R-002, R-003, R-005, R-006, R-007, R-009, R-010 |
| Responsibilities→skills | ✓ | L188–L201 (10 rows) |
| Delegation | ✓ | L203–L215 — project-explorer, reviewer, committer (3 rows table) |
| Dynamic-readiness | ✓ | L232–L242 |
| Inline procedure | ✗ | L106–L120 protected-scope table; L122–L134 6-step workflow; L136–L157 post-change validation sequence (10 steps); L217–L230 escalation list. All belong in `system-awareness`, `asset-authoring`, `system-validation`, `system-repair`, `config-management`, `governance-approval` skills |

**Findings**: H-7, M-9, L-2

### 1.6 · fix-lead — `src/aspis/data/catalog/agents/fix-lead.md` (177 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L59 |
| Title line | ✓ | L62, L64 |
| Identity | ⚠ IS/IS NOT, no prime directive | L66–L87 — IS (L73–L79), IS NOT (L81–L87), no prime directive block (ref spec has it but body omits) |
| How you work | ✗ MISSING | No `## How you work`; closest is L89–L104 `## The 6-step fix lifecycle` (16 lines inlined as table) |
| Core rules | ✗ restate, 0 R-### cited in Core rules | L138–L146 — 6 bullets, **zero** R-### citations in this section (R-001, R-005 appear in Identity L71, L86 but not in Core rules) |
| Responsibilities→skills | ✓ | L148–L155 (4 rows) |
| Delegation | ✓ | L157–L164 — reviewer, committer, project-explorer, test-lead (4 rows) |
| Dynamic-readiness | ✓ | L166–L176 |
| Inline procedure | ✗ | L89–L104 6-step fix lifecycle; L105–L109 mode overlay; L111–L122 3-attempt hard cap; L124–L136 FIX_REPORT template. All belong in `root-cause-analysis`, `corrective-fix`, `selective-testing` skills |

**Findings**: H-8, M-10, L-2

### 1.7 · test-lead — `src/aspis/data/catalog/agents/test-lead.md` (172 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L36 |
| Title line | ✓ | L38, L40 |
| Identity | ⚠ IS/IS NOT, no prime directive | L42–L72 — IS (L49–L55), IS NOT (L57–L63), no prime directive block |
| How you work | ⚠ | L74–L88 `## How you validate` — references `aspis artifact test` but is 15 lines with inlined 4-step loop |
| Core rules | ⚠ 2 R-### cited | L132–L146 — 8 bullets; R-005 (L136), R-004 (L143). Missing R-001, R-002, R-006, R-008, R-009, R-010 |
| Responsibilities→skills | ✓ | L148–L153 (2 rows — small but every responsibility is mapped) |
| Delegation | ✓ | L155–L159 — project-explorer |
| Dynamic-readiness | ✓ | L161–L172 |
| Inline procedure | ✗ | L76–L88 4-step loop table; L90–L98 mode-dependent depth table; L100–L119 failure-classification table; L121–L130 labs testing description. All belong in `test-generation` and `test-execution` skills |

**Findings**: M-11, L-2

### 1.8 · research-lead — `src/aspis/data/catalog/agents/research-lead.md` (206 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter | ✓ 11/11 fields | L1–L32 |
| Title line | ✗ reversed order | L35 `> Derived…` precedes L37 `# Research Lead` |
| Identity | ⚠ IS/IS NOT, no prime directive | L39–L83 — IS (L47–L54), IS NOT (L56–L63), no prime directive block (ref spec §1 has Model Tier rationale but no prime directive) |
| How you work | ⚠ | L91–L105 `## The 4-Step Procedure` — 15 lines with inlined 4-step table; not titled "How you work" |
| Core rules | ✗ restate, 0 R-### cited in Core rules | L172–L182 — 6 bullets, **zero** R-### citations in this section (R-001, R-004, R-007, R-008 appear in Identity, Output Formats, Responsibilities — but not in Core rules) |
| Responsibilities→skills | ✓ | L184–L192 (5 rows) |
| Delegation | ✗ MISSING | Delegates only in frontmatter (L24–L25: `project-explorer`); no body `## Delegation` section |
| Dynamic-readiness | ✓ | L194–L205 |
| Inline procedure | ✗ | L91–L105 4-step procedure; L107–L130 cache system (24 lines); L132–L140 research types table; L142–L170 output formats (4 code blocks). All belong in `knowledge-research`, `knowledge-packaging`, `cache-management`, `harvest-protocol` skills |

**Findings**: H-9, H-10, M-12, L-2, L-3

---

## 2 · Findings (file:line evidence, severity-ordered)

### CRITICAL

#### C-1 · build-lead.md:60 — markdown heading hierarchy breaks the standard

**File**: `src/aspis/data/catalog/agents/build-lead.md:60`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" — every
section is `## ` (H2) under the title `# ` (H1). The build-lead body writes
`# Identity` (H1) at L60, which makes it a sibling of the title `# Build Lead`
(L56) rather than a subsection. This breaks heading hierarchy and any tool that
uses heading depth to parse sections (e.g. a `## Core rules` grep on this file
will not see the Identity section in the expected depth).
**Why it matters**: a heading-hierarchy break is the kind of bug that passes
visual review and breaks automated validation; it is a sign the build did not
run a structural sweep against the standard.
**Fix**: change L60 from `# Identity` to `## Identity`.
**Severity**: CRITICAL (cosmetic but mechanically wrong).

### HIGH

#### H-1 · project-lead.md — MISSING `## Delegation` section

**File**: `src/aspis/data/catalog/agents/project-lead.md` (between L122 and L184)
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §6
"Delegation" — "A list of who this agent delegates to, when, and for what kind
of work. Every name in this section must match a catalog agent. No orphan
delegates."
**Why it matters**: project-lead has 8 delegates in the frontmatter (L33–L41)
but the body has no `## Delegation` section that names them with their trigger
and purpose. A reviewer or runtime parser that only reads the body will see
no delegation surface. The standard's "no orphan delegates" rule cannot be
enforced if the delegation surface lives only in YAML.
**Fix**: add `## Delegation` between Responsibilities and Dynamic-readiness;
list 7–8 delegates with one-line trigger + purpose each (e.g. "planning-lead
— feature / plan / spec / clarify intent").
**Severity**: HIGH (required section missing; FR-005 delegation audit cannot
verify the body).

#### H-2 · research-lead.md — MISSING `## Delegation` section

**File**: `src/aspis/data/catalog/agents/research-lead.md` (between L192 and L194)
**Standard violation**: same as H-1.
**Why it matters**: research-lead has 1 delegate (`project-explorer` at L25) but
no body section names it. While 1-delegate bodies are short, the standard
explicitly requires the section.
**Fix**: add a 3-line `## Delegation` section between Responsibilities and
Dynamic-readiness.
**Severity**: HIGH (same as H-1).

#### H-3 · project-lead.md — MISSING `## How you work` section

**File**: `src/aspis/data/catalog/agents/project-lead.md`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §3
"How you work" — "1–2 lines of natural-language procedure plus a pointer to
the workflow. Never restate the workflow steps here."
**Evidence**: the body has `## Project Intelligence` (L71), `## Core rules`
(L93), `## Responsibilities → skills` (L109), `## Stop-and-ask conditions`
(L124), `## First-run gate` (L141), `## Handling a request` (L161) — but no
`## How you work`. The closest is `## Handling a request` (L161–L175), which
is **15 lines of inlined procedure** — exactly what the standard says
"never restate the workflow steps here."
**Why it matters**: project-lead is the L1 entry point and the only agent the
human talks to. The body should compress its procedure to 1–2 lines and point
to a workflow or a single skill. As built, the body's procedure is inlined and
duplicated against any future `project-lead-operating-protocol.md` workflow.
**Fix**: replace `## Handling a request` with a 2-line `## How you work`
pointing to either the future workflow or a synthesized skill; move the
orchestration detail into that skill.
**Severity**: HIGH (required section missing + 15 lines of inlined procedure).

#### H-4 · planning-lead.md — How you work section restates plan.md

**File**: `src/aspis/data/catalog/agents/planning-lead.md:97–109`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §3
"1–2 lines of natural-language procedure plus a pointer to the workflow. Never
restate the workflow steps here." §"Forbidden patterns" — "No duplicated
content: skill procedures, rule text, workflow steps, or template content must
never appear inline in a body."
**Evidence**: `## How you plan` is 13 lines (L97–L109) referencing
`.aspis/workflows/plan.md` on L102 — but the body then inlines the 5-track
table (L117–L123) and the mode-dial knobs (L125–L145) which are also
in `plan.md` and `modes.yaml`.
**Why it matters**: the standard's "single source" rule (R-006) is the
load-bearing principle for cost-of-change. A body that inlines content
already in the workflow or skill triggers a re-edit when the workflow
changes — exactly the cost-of-change problem the standard was written to
prevent.
**Fix**: trim `## How you plan` to 2 lines and a pointer; remove the inlined
5-track and mode-dial tables (they belong in `planning-intake` and the
workflow).
**Severity**: HIGH (direct R-006 violation; the planning-lead body alone
has ~30 lines of inlined procedure that should be in skills).

#### H-5 · build-lead.md — How you work section restates build.md and packet-validation

**File**: `src/aspis/data/catalog/agents/build-lead.md:70–101, 102–112, 114–127`
**Standard violation**: same as H-4.
**Evidence**: `## How you execute — the build loop` (L70–101) is 32 lines
referencing `.aspis/workflows/build.md` on L72 — but then inlines the
packet-validation 4-check table (L102–112) and the builder-security 7-rule
list (L114–127) that already live in `task-orchestration` and
`packet-validation` skills.
**Why it matters**: SC-011 cost-of-change test. If `packet-validation` skill
gains a new check, this body must be edited too — violates FR-019.
**Fix**: trim `## How you execute` to 2 lines + pointer; remove inlined
packet-validation and builder-security tables.
**Severity**: HIGH (R-006 + FR-019 + SC-011 violation).

#### H-6 · reviewer.md — Core rules cite only R-004, missing 7 system rules

**File**: `src/aspis/data/catalog/agents/reviewer.md:199–220`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §4
"Core rules" — "A bullet list of system rules cited by ID (R-001, R-004, etc.)
this agent must honour — never restate what the rule says." §"Forbidden
patterns" — "No restated rules: never write 'R-001 means scope control…
Write only 'R-001' and let the system rules speak for themselves."
**Evidence**: 8 Core-rules bullets; only L204 cites R-004. The other 7
bullets (L201, L203, L206, L209, L213, L216, L218) restate behaviour in
prose without citing the rule they embody. The reviewer body
**participates in the very anti-pattern the standard calls out**.
**Why it matters**: reviewer's job is to enforce R-006 and rule-by-ID
discipline. A reviewer body that restates rules in prose is the most
embarrassing violation of its own standard.
**Fix**: replace 8 prose bullets with a 4–6 line ID list (e.g. "R-001, R-002,
R-004, R-005, R-006, R-008, R-009") plus 1–2 own rules (e.g. "fresh-context
review — never anchor on builder's report").
**Severity**: HIGH (rule-by-ID discipline failure in the rule-enforcement
agent).

#### H-7 · system-lead.md — Core rules restate R-003 / R-004 / R-008 instead of citing

**File**: `src/aspis/data/catalog/agents/system-lead.md:158–186`
**Standard violation**: same as H-6.
**Evidence**: 8 Core-rules bullets; only L179 cites R-008 and L180 cites
R-004. The first 5 bullets (L161–L168) restate R-001 (scope), R-002
(gates), R-003 (deterministic-first), R-005 (tests), R-006 (thin agents)
in prose. The body has 5 separate paragraphs of restated rule content
that should be 5 ID citations.
**Fix**: collapse L161–L168 into an ID list; keep the 1–2 own rules
(self-modification discipline, governance subagent path).
**Severity**: HIGH (same as H-6).

#### H-8 · fix-lead.md — How you work section restates fix.md and 3-attempt cap

**File**: `src/aspis/data/catalog/agents/fix-lead.md`
**Standard violation**: same as H-3 (missing `## How you work`); same as
H-4 (R-006 — `## The 6-step fix lifecycle` L89–104 inlines the fix
spine, `## The 3-attempt hard cap` L111–122 inlines the cascade, `## The
FIX_REPORT` L124–136 inlines the report shape).
**Evidence**: 4 sections of inlined procedure across ~50 lines; the
referenced `fix.md` workflow lives at
`src/aspis/data/catalog/workflows/fix.md` and the procedures also live
in `root-cause-analysis`, `corrective-fix`, `selective-testing` skills.
**Fix**: trim to a 2-line `## How you work` + pointer; remove inlined
fix-spine, 3-attempt cap, FIX_REPORT.
**Severity**: HIGH (R-006 + missing required section).

#### H-9 · research-lead.md — MISSING prime directive and `## Delegation` section

**File**: `src/aspis/data/catalog/agents/research-lead.md` (already H-2 above)
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §2
"Identity" — "2–4 lines establishing what the agent IS and what it IS NOT,
plus its **prime directive** — the one non-negotiable rule that overrides
all others."
**Evidence**: research-lead has IS (L47–54) and IS NOT (L56–63) but no
prime directive. The F-016 ref spec has no explicit prime directive
either, but the standard requires one for every body. research-lead's
natural prime directive is "knowledge correctness × cache-first × source
authority" — analogous to how planning-lead and reviewer bodies have
prime-directive equations.
**Fix**: add a 3-line `### Prime directive` block in Identity.
**Severity**: HIGH (required element missing).

#### H-10 · research-lead.md — How you work section inlines the 4-step procedure

**File**: `src/aspis/data/catalog/agents/research-lead.md:91–105`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §3
"1–2 lines + workflow pointer, never restate the workflow steps here."
**Evidence**: `## The 4-Step Procedure` is 15 lines (L91–105) with the
full scope → research → validate → package table. The 4 steps also live
in the `knowledge-research` and `knowledge-packaging` skills, and the
research-lead ref spec §2 documents them as the 4-step procedure.
**Fix**: trim to 2 lines and a pointer to the skills.
**Severity**: HIGH (R-006 + missing required shape).

### MEDIUM

#### M-1 · 5 of 8 bodies — Core rules restate system rules in prose (zero R-### cited)

**Files / lines**:
- `project-lead.md:93–107` — 8 bullets, **0** R-### citations
- `planning-lead.md:147–166` — 11 bullets, **0** R-### citations
- `build-lead.md:138–162` — 9 bullets, **0** R-### citations in this section
  (R-002 cited only in a sub-bullet of the How-you-work section L79)
- `fix-lead.md:138–146` — 6 bullets, **0** R-### citations
- `research-lead.md:172–182` — 6 bullets, **0** R-### citations in this section

**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §4
"Core rules" — "A bullet list of system rules cited by ID (R-001, R-004,
etc.) this agent must honour — never restate what the rule says." §"Forbidden
patterns" — "No restated rules: never write 'R-001 means scope control — don't
touch forbidden files.' Write only 'R-001' and let the system rules speak for
themselves."

**Why it matters**: across the 5 bodies, ~40 bullets of restated system rules
exist that should be 5–6 ID lines per body. The restated form **is precisely
the anti-pattern the standard calls out by name** ("No restated rules"). The
build process that finalized the bodies did not run the rule-by-ID discipline
check; SC-006 says "every agent body passes agent-body standard check" and
this fails the standard on 5 of 8 bodies.

**Fix per body**: replace each prose bullet with a single R-### citation; keep
2–3 own rules (the "if stuck, stop" rule, role-specific own rules like
"prime-directive = …" in planning-lead).

**Severity**: MEDIUM — single-most-important rule-by-ID discipline gap in the
build, but each body individually has 1 HIGH finding (H-3, H-4, H-5, H-6,
H-7, H-8, H-10) that overlaps; this finding is the **aggregate count**.

#### M-2 · project-lead.md:62–69 — Identity 8 lines, missing IS NOT and prime directive

**File**: `src/aspis/data/catalog/agents/project-lead.md:62–69`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §2
"Identity" — "2–4 lines establishing what the agent IS and what it IS NOT, plus
its **prime directive**."
**Evidence**: the body has a single 8-line paragraph starting "You are the
Project Lead — the single L1 entry point — the only agent the human talks to.
You are the project's intelligence layer and authoritative representation…"
There is no `### What you ARE` / `### What you are NOT` separation, no
prime-directive equation. The F-016 ref spec has both (ref §1) but the body
inlines none of it.
**Fix**: split into "### What you ARE" (4 bullets), "### What you are NOT"
(7 bullets from ref spec L31–L38), and a "### Prime directive" equation
(adapted from ref L42–L47).
**Severity**: MEDIUM.

#### M-3 · project-lead.md:141–158 — First-run gate is non-standard, inlined, and stale

**File**: `src/aspis/data/catalog/agents/project-lead.md:141–158`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" —
extra sections between Responsibilities and Dynamic-readiness are allowed
when they are short, but this is 18 lines of inlined bootstrap procedure
inside `<!-- ASPIS:BOOTSTRAP-GATE:START --> … <!-- ASPIS:BOOTSTRAP-GATE:END -->`
HTML comment fences.
**Why it matters**: the bootstrap gate is meant to be a *self-removing*
template (per the F-016 ref spec L15: "Bootstrap is a transient primary that
self-deletes"). The body inlines the procedure and adds 18 lines of agent
body content that the bootstrap flow is supposed to remove. The "removal"
contract is not in the body — only a comment says "this gate and the
`bootstrap` delegate are removed from this file automatically" — but no
runtime code or process actually performs that removal.
**Fix**: either (a) make the bootstrap-gate content live in a skill
(`bootstrap-gate`) and reference it, or (b) document the runtime mechanism
that removes the block (and gate on its existence in the SC-006 check).
**Severity**: MEDIUM (the body adds 18 lines outside the standard's shape
contract, and the self-removal contract is not enforced).

#### M-4 · planning-lead.md:62–95 — Identity 33 lines, inlined IS / IS NOT / prime from ref

**File**: `src/aspis/data/catalog/agents/planning-lead.md:62–95`
**Standard violation**: same as M-2; the standard says "2–4 lines" but
planning-lead's Identity is 33 lines. The "What you ARE" (L85–90) and
"What you are NOT" (L92–95) subsections are good additions; the
prime-directive equation (L75–79) is good. But the prose preamble (L63–73)
restates planning-lead's role in 10 lines that could be 2.
**Fix**: trim the prose preamble to 2 lines; keep the IS/IS NOT/prime
subsections.
**Severity**: MEDIUM.

#### M-5 · build-lead.md — Identity has no IS NOT, heading typo

**File**: `src/aspis/data/catalog/agents/build-lead.md:60–68`
**Standard violation**: same as M-2; the standard requires IS / IS NOT /
prime directive. build-lead has IS (L62–68) and prime (L68 inlined) but
no IS NOT subsection. The F-016 ref spec L27–L35 has 5 IS-NOT bullets
the body omits.
**Fix**: add a `### What it is NOT` subsection with 5 bullets from ref
spec L29–L35; pair with the C-1 heading fix.
**Severity**: MEDIUM.

#### M-6 · build-lead.md:114–127 — Builder security rules restated inline

**File**: `src/aspis/data/catalog/agents/build-lead.md:114–127`
**Standard violation**: AGENT_BODY_STANDARD.md §"Forbidden patterns" —
"No duplicated content: skill procedures, rule text, workflow steps, or
template content must never appear inline in a body."
**Evidence**: 7 builder-security rules are inlined as a numbered list
when they already live in the F-016 ref spec §9 "Builder Security" and
are referenced by the `task-orchestration` skill (which build-lead already
has in its skills: list at L44–L52).
**Fix**: remove L114–L127 and add "Builder security rules (R-006, fresh-context
isolation, deny floor, path-scoped edits) — see `task-orchestration` skill" to
the Core rules section.
**Severity**: MEDIUM (R-006 violation).

#### M-7 · reviewer.md:110–172 — 9-dimensions and 4-verdict systems inlined

**File**: `src/aspis/data/catalog/agents/reviewer.md:110–172`
**Standard violation**: same as M-6.
**Evidence**: L110–L138 inlines the 9-dimensions × 3-mode depth matrix (38
lines); L140–L172 inlines the 4-verdict system + severity rubric + finding
format (30+ lines). All of this lives in `review-strategy`, `quality-review`,
and `acceptance-decision` skills that reviewer lists in its skills (L35–L43).
**Fix**: remove the inlined matrices; reference the skills by name.
**Severity**: MEDIUM.

#### M-8 · reviewer.md:209 — constitution-checks.yaml path mismatch

**File**: `src/aspis/data/catalog/agents/reviewer.md:209`
**Standard violation**: AGENT_BODY_STANDARD.md §"No missing references" — every
named asset path must resolve.
**Evidence**: L209 references `.aspis/config/constitution-checks.yaml` (with
`enforced_by: review`). The actual file is at
`src/aspis/data/catalog/config/policy/constitution-checks.yaml` (verified by
glob — the `.aspis/config/` directory does not contain
`constitution-checks.yaml`).
**Why it matters**: if reviewer follows the body literally, it will look for a
file that does not exist. The `aspis export` command is what would produce
`.aspis/config/constitution-checks.yaml` in a target project, but the body
sits in the source catalog and would benefit from a path that resolves in the
catalog.
**Fix**: change the path to
`src/aspis/data/catalog/config/policy/constitution-checks.yaml` (or document
the runtime mapping in the body).
**Severity**: MEDIUM (a "no missing references" violation; not blocking
because the file exists at the catalog path).

#### M-9 · system-lead.md:122–134 — How you work inlines 6-step workflow

**File**: `src/aspis/data/catalog/agents/system-lead.md:122–134`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §3
"1–2 lines + workflow pointer" and §"Forbidden patterns" — no inline procedure
duplication.
**Evidence**: `## How you work — the 6-step workflow` is 13 lines and inlines
the 6-step workflow (CLASSIFY, INSPECT, DECIDE, AUTHOR, VALIDATE, HAND) as a
numbered list. The 6 steps also live in the F-016 ref spec §6 and are
referenced by `asset-authoring` and `system-validation` skills.
**Fix**: trim to 2 lines and a pointer; rely on `system-awareness` +
`asset-authoring` + `system-validation` for the detail.
**Severity**: MEDIUM.

#### M-10 · fix-lead.md:89–136 — 4 sections of inlined procedure (~50 lines)

**File**: `src/aspis/data/catalog/agents/fix-lead.md:89–104, 105–109, 111–122, 124–136`
**Standard violation**: same as H-4 / M-6.
**Evidence**: 4 sections (6-step fix lifecycle, mode overlay, 3-attempt cap,
FIX_REPORT) span ~50 lines of inlined procedure. The same content lives in
the `fix.md` workflow (52 lines including the same tables) and in
`root-cause-analysis`, `corrective-fix`, `selective-testing` skills.
**Fix**: remove L89–L136 inlined content; reference the workflow and the
3 skills.
**Severity**: MEDIUM.

#### M-11 · test-lead.md:74–130 — How you work + failure classification + labs testing inlined

**File**: `src/aspis/data/catalog/agents/test-lead.md:74–130`
**Standard violation**: same as M-9.
**Evidence**: `## How you validate` is 15 lines (L74–88); L90–L98 inlines
the mode-dependent depth table; L100–L119 inlines the 3-class failure
classification; L121–L130 inlines the labs testing description. All of this
lives in `test-generation` and `test-execution` skills (L32–L35).
**Fix**: trim `## How you validate` to 2 lines + pointer; remove inlined
classification table and labs description.
**Severity**: MEDIUM.

#### M-12 · research-lead.md:107–170 — Cache system + research types + output formats inlined

**File**: `src/aspis/data/catalog/agents/research-lead.md:107–170`
**Standard violation**: same as M-6.
**Evidence**: 4 substantive sections (cache system, research types, output
formats) span ~64 lines of inlined material. All of this lives in
`knowledge-research`, `knowledge-packaging`, `cache-management`, and
`harvest-protocol` skills (L26–L31).
**Fix**: remove the inlined sections; reference the skills by name.
**Severity**: MEDIUM.

### LOW

#### L-1 · AGENT_BODY_STANDARD.md — `mode` field documented as vibe/mvp/production, agents use primary/subagent

**File**: `.aspis/context/AGENT_BODY_STANDARD.md:27`
**Evidence**: the standard's `mode` row says "`vibe` / `mvp` / `production`"
but all 8 lead bodies ship `mode: primary` (project-lead, build-lead) or
`mode: subagent` (planning-lead, reviewer, system-lead, fix-lead, test-lead,
research-lead). The catalog's `ARCHITECTURE.md:86` confirms "**every agent
ships `mode: subagent`; only the Project Lead is primary**" — so the
architecture standard is "primary/subagent", and the body-standard docstring
is wrong.
**Why it matters**: the body standard is a contract; an incorrect contract
that 8 bodies immediately violate signals the standard was authored from
intent without verifying against the architecture.
**Fix**: change L27 to "`primary` / `subagent`" (or add a new
`build_mode` field for vibe/mvp/production if both are needed).
**Severity**: LOW (documentation issue; the bodies are correct against the
architecture, not against the standard's docstring).

#### L-2 · 8 of 8 bodies — Workflow path references use `.aspis/workflows/` (deployed path) instead of catalog source

**Files / lines**:
- `project-lead.md:177` — `.aspis/workflows/`
- `planning-lead.md:102` — `.aspis/workflows/plan.md`
- `build-lead.md:72` — `.aspis/workflows/build.md`
- `reviewer.md:93` — `.aspis/workflows/review.md`

**Standard violation**: AGENT_BODY_STANDARD.md §"No missing references" — every
named path must resolve to an existing asset.

**Evidence**: the bodies reference `.aspis/workflows/<name>.md`, but in this
factory repo the workflows live at `src/aspis/data/catalog/workflows/<name>.md`
(verified by glob — 6 files: plan.md, build.md, review.md, fix.md,
small-task.md, bootstrap.md). The `.aspis/workflows/` directory does not exist
in this repo. It would exist in a target project after `aspis export`.

**Why it matters**: the bodies sit in the source catalog, so their workflow
references are stale from a factory-repo perspective. From a deployed-project
perspective, the paths are correct.

**Fix**: either (a) change the paths to `src/aspis/data/catalog/workflows/<name>.md`
(factory-repo perspective), or (b) document in each body that paths are
written for a deployed project and add a render-time substitution rule. The
cleaner fix is (a).

**Severity**: LOW (the workflow files exist; the path prefix is wrong but
resolvable in deployment).

#### L-3 · project-lead.md:58 / research-lead.md:35 — Title and "Derived" line in reversed order

**Files / lines**:
- `project-lead.md:58` `> Derived from Research/ref/project-lead.md` precedes
  L60 `# Project Lead`
- `research-lead.md:35` `> Derived from Research/ref/research-lead.md` precedes
  L37 `# Research Lead`

**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §1
"Title line" — `# <Agent Name>` first, then `> Derived from Research/ref/<agent>.md`.

**Evidence**: the 6 other bodies (planning-lead, build-lead, reviewer, system-lead,
fix-lead, test-lead) follow the standard's order; project-lead and research-lead
have the lines swapped.

**Fix**: swap the two lines in each body so the `# Title` is first and the
`> Derived…` quote is second.

**Severity**: LOW (cosmetic, but the standard is explicit).

#### L-4 · build-lead.md:60 — `# Identity` should be `## Identity` (duplicate of C-1)

The C-1 finding captures the heading-hierarchy break; this LOW finding is
its cosmetic twin — readers scanning the file see "Identity" at the same
heading depth as the title and may misread the section as a sibling rather
than a subsection.

**Severity**: LOW.

#### L-5 · planning-lead.md — inline 5-track table duplicates `planning-intake` skill

**File**: `src/aspis/data/catalog/agents/planning-lead.md:117–123`
**Evidence**: the 5-track table (Question / Trivial / Small task / Feature /
Project plan) is inlined but also lives in `planning-intake` skill (L46 of
skills list) and the F-016 ref spec §2.
**Fix**: remove and reference the skill.
**Severity**: LOW (subsumed by H-4; called out for the table specifically).

#### L-6 · project-lead.md:124–139 — `## Stop-and-ask conditions` 16 lines, more than Core rules

**File**: `src/aspis/data/catalog/agents/project-lead.md:124–139`
**Standard violation**: AGENT_BODY_STANDARD.md §"Forbidden patterns" — inline
content that duplicates workflow content.
**Evidence**: 13 stop-and-ask conditions are inlined as a numbered list, but
the same list lives in the F-016 ref spec §7 and the F-016 ref §7 "Flow:
Ambiguous Request" — i.e. the workflow already documents this.
**Fix**: compress to a single line that points to the workflow.
**Severity**: LOW.

#### L-7 · 8 of 8 bodies — section order does not strictly follow the standard

**Files / lines**: all 8 bodies have substantive sections between the
"required" 6 sections (Identity / How you work / Core rules /
Responsibilities→skills / Delegation / Dynamic-readiness). The standard says
"After the frontmatter, the body contains these sections in order"; inlining
substantive content (e.g. "9 review dimensions", "5-track classification",
"6-step workflow", "FIX_REPORT template") violates the "in order" expectation.

**Fix**: move inlined sections to skills or workflows (per H-4 through H-10
and M-6 through M-12); the bodies should reduce to the 6 standard sections
in the standard order, each at the standard's expected length.

**Severity**: LOW (the standard is loose on "in order" — it allows the
section to exist; the order matters less than the shape).

---

## 3 · F-016 reference spec faithfulness

Cross-checked each body against its F-016 reference spec:

| Body | Faithful to F-016 ref? | Notes |
|---|---|---|
| project-lead.md | ✓ (with 1 deviation) | All 8 core responsibilities (ref §2) mapped; 3 recommended new skills (`recontextualization`, `session-continuation`, `mode-decision`) all referenced (L52–L54). Deviation: ref §1 has 8 bullets in "What it IS" and 7 in "What it is NOT" and a prime-directive equation; body has only a single 8-line paragraph (L62–L69) — see M-2. |
| planning-lead.md | ✓ | All 7 core responsibilities (ref §4) mapped plus 4 recommended (`deterministic-first`, `scope-control`, `mode-decision`, `constitution-checks`); M-2 fix verified (only 3 delegates, not 7 orphan subagents from ref §6). |
| build-lead.md | ✓ | All 6 core responsibilities (ref §3) mapped plus 2 recommended (`packet-validation`, `builder-selection`); delegates match ref §5. |
| reviewer.md | ✓ | All 8 skills (ref §3) listed; 9 dimensions × mode depth (ref §5) inlined; 4 verdicts (ref §6) inlined; 12 plan-critic checks (ref §7) inlined. |
| system-lead.md | ✓ | All 7 core + 3 missing skills from ref §3 mapped; bash allowlist is named (no `*`) per ref §5; deterministic-first ladder (ref §1) inlined. |
| fix-lead.md | ✓ | All 6 skills (ref §3) mapped; 6-step lifecycle (ref §2) inlined; 3-attempt cap (ref §7) inlined; FIX_REPORT (ref §8) inlined. |
| test-lead.md | ✓ | 2 skills (ref §3) mapped; 4-step loop (ref §2) inlined; failure classification (ref §7) inlined. |
| research-lead.md | ✓ | 5 skills (ref §12) mapped; 4-step procedure (ref §2) inlined; tightest permission surface (ref §1) preserved in frontmatter; only subagent with both `webfetch` + `websearch`. |

**Summary**: every body is **substantively faithful** to its F-016 ref spec.
The bodies preserve the design intent, the permission surface, the skill
mapping, and the role boundaries. The deviations are **shape** (long bodies
with inlined procedure) and **two missing Delegation sections** (project-lead,
research-lead), not role drift.

---

## 4 · DYNAMIC_READINESS.md check

| Check | Status | Evidence |
|---|---|---|
| File exists | ✓ | `.aspis/context/DYNAMIC_READINESS.md` — 130 lines |
| R-008 approval recorded in ACCEPTANCE.md | ✓ | `F-017/ACCEPTANCE.md:13–17` — "T-08a — DYNAMIC_READINESS.md approved (2026-06-27)" |
| Three dials documented | ✓ | L21–L86 — Mode (production/mvp/vibe), Task kind/scope, Model capability (cheap/standard/deep) |
| Convention block example | ✓ | L92–L105 — provides a reference block format for bodies to use |
| All 8 bodies reference the convention | ✓ | each body has a `## Dynamic-readiness` section that opens with "Right-sizes process per `.aspis/context/DYNAMIC_READINESS.md`" and names the 3 dials |
| Leanest-correct-path default | ✓ | convention document L107–L122; bodies include it in their dynamic-readiness block |
| Optimise-the-path-not-the-bar principle | ✓ | convention document L9–L14 |

**Verdict on DYNAMIC_READINESS.md**: APPROVED. The convention is well-defined
(3 dials, 1 default), encodes the "optimise the path, never the bar" principle
clearly, and is referenced correctly by all 8 bodies. The future-router-ready
statement (L124–L130) holds the design for the model-router engine.

---

## 5 · AGENT_BODY_STANDARD.md check

| Check | Status | Evidence |
|---|---|---|
| File exists | ✓ | `.aspis/context/AGENT_BODY_STANDARD.md` — 112 lines |
| R-006 alignment | ✓ | L10–L12 — "Thin agents, single source: content lives in skills/workflows; the body references by name/path, never inlines procedure or data." |
| Cite, don't restate | ✓ | L12–L14 — "Cite, don't restate: system rules cited by ID only" |
| Every section is short | ✓ | L14–L16 — explicit length budgets per section |
| No dead references | ✓ | L16–L18 — "every delegate, skill, workflow, and template the body names must exist" |
| 11 frontmatter fields | ✓ | L23–L35 — name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope |
| 6 required body sections | ✓ | L41–L77 — Title, Identity, How you work, Core rules, Responsibilities→skills, Delegation, Dynamic-readiness (7 total — Dynamic-readiness added) |
| Forbidden patterns | ✓ | L80–L92 — 4 named anti-patterns (no duplicated content, no missing refs, no orphan delegates, no `bash: '*': allow`, no restated rules) |
| Checklist | ✓ | L96–L111 — 12-item acceptance checklist |

**Verdict on AGENT_BODY_STANDARD.md**: MOSTLY APPROVED. The standard is well
defined and **the bodies largely conform to it** — but the `mode` field
docstring (L27) is wrong (says `vibe/mvp/production`, should be
`primary/subagent` per `ARCHITECTURE.md:86`); see L-1.

**Additional observation**: the standard's checklist (L96–L111) does not
explicitly check the **rule-by-ID discipline** in the Core rules section.
That gap is what allowed the 5 bodies with 0 R-### citations (M-1) to
pass the standard's check. The build's T-32a L1 exit gate ran the
standard check and approved the bodies — which means the standard itself
needs a sharper checklist item:

> [ ] Core rules cite system rules by ID only; zero restated rule prose

Add this line to AGENT_BODY_STANDARD.md L98–L111.

---

## 6 · Standards-compliance summary table

| Body | Title order | Identity (IS/IS NOT/prime) | How you work | Core rules (R-### by ID) | Resp→skills | Delegation | Dynamic-readiness | Inline procedure (R-006) |
|---|---|---|---|---|---|---|---|---|
| project-lead | ✗ reversed | ⚠ IS only, 8 lines | ✗ MISSING | ✗ 0 / 8 cited | ✓ | ✗ MISSING | ✓ | ✗ (15 lines handling-a-request + 18 lines bootstrap-gate) |
| planning-lead | ✓ | ✓ full, 33 lines | ⚠ 13 lines, titled "How you plan" | ✗ 0 / 11 cited | ✓ | ✓ | ✓ | ✗ (5-track + mode-dial inlined) |
| build-lead | ✓ | ⚠ no IS NOT + # H1 typo | ⚠ 32 lines, titled "How you execute" | ✗ 0 / 9 cited in Core rules | ✓ | ✓ | ✓ | ✗ (packet-validation + builder-security inlined) |
| reviewer | ✓ | ✓ full, 26 lines | ⚠ 18 lines, titled "How you review" | ⚠ 1 R-004 / 8 (R-001, R-002, R-005, R-006, R-008, R-009, R-010 missing) | ✓ | ✓ | ✓ | ✗ (9-dim + 4-verdict + 12 plan-critic inlined) |
| system-lead | ✓ | ✓ full, 32 lines | ✗ 13 lines inlined 6-step | ⚠ R-004, R-008 / 8 (R-001, R-002, R-003, R-005, R-006, R-007, R-009, R-010 missing) | ✓ | ✓ | ✓ | ✗ (6-step + 10-step validation inlined) |
| fix-lead | ✓ | ⚠ no prime directive, 22 lines | ✗ MISSING (titled "The 6-step fix lifecycle") | ✗ 0 / 6 cited in Core rules | ✓ | ✓ | ✓ | ✗ (6-step + 3-attempt + FIX_REPORT inlined) |
| test-lead | ✓ | ⚠ no prime directive, 32 lines | ⚠ 15 lines, titled "How you validate" | ⚠ R-004, R-005 / 8 (R-001, R-002, R-006, R-008, R-009, R-010 missing) | ✓ | ✓ | ✓ | ✗ (4-step + failure-class + labs inlined) |
| research-lead | ✗ reversed | ⚠ no prime directive, 46 lines | ⚠ 15 lines, titled "The 4-Step Procedure" | ✗ 0 / 6 cited in Core rules | ✓ | ✗ MISSING | ✓ | ✗ (4-step + cache + research-types + output-formats inlined) |

**Aggregate score**: 8/8 have frontmatter ✓, Responsibilities→skills ✓,
Dynamic-readiness ✓. 6/8 have the Delegation section ✓ (2 missing). 3/8
have full IS/IS NOT/prime Identity (4/8 have IS/IS NOT). 6/8 have a
How-you-work section in some form (2 missing). 1/8 (reviewer) has Core
rules with at least 1 R-### citation; 7/8 have Core rules that restate
behaviour in prose without citing the rule. 0/8 bodies fully conform to
the "1–2 lines + workflow pointer, never restate workflow steps" rule for
the How-you-work section. 0/8 bodies fully conform to the "every section
is short" rule — every body has substantive inline content the standard
says should live in skills or workflows.

---

## 7 · Severity-ordered action list

To make the bodies pass the AGENT_BODY_STANDARD, the build team should:

### CRITICAL (1 finding)

1. **C-1** `build-lead.md:60` — change `# Identity` to `## Identity` (single-char fix, single-line edit).

### HIGH (8 findings)

2. **H-1** `project-lead.md` — add `## Delegation` section listing 8 delegates with trigger + purpose.
3. **H-2** `research-lead.md` — add `## Delegation` section listing `project-explorer` with trigger + purpose.
4. **H-3** `project-lead.md` — replace `## Handling a request` (15 lines) with 2-line `## How you work` + pointer; move orchestration detail to a skill.
5. **H-4** `planning-lead.md:97–145` — trim `## How you plan` to 2 lines; remove inlined 5-track table (L117–123) and mode-dial (L125–145); reference `planning-intake` skill and `.aspis/workflows/plan.md`.
6. **H-5** `build-lead.md:70–127` — trim `## How you execute` to 2 lines; remove inlined packet-validation (L102–112) and builder-security (L114–127); reference `task-orchestration` and `packet-validation` skills.
7. **H-6** `reviewer.md:199–220` — collapse 8 Core-rules prose bullets to 4-line ID list (R-001, R-002, R-004, R-005, R-006, R-008, R-009) + 1 own rule.
8. **H-7** `system-lead.md:158–186` — collapse first 5 Core-rules bullets to ID list (R-001, R-002, R-003, R-005, R-006, R-007, R-008) + 2 own rules (self-modification, governance-subagent path).
9. **H-8** `fix-lead.md` — add 2-line `## How you work`; remove inlined 6-step spine (L89–104), 3-attempt cap (L111–122), FIX_REPORT (L124–136); reference `fix.md` workflow + 3 skills.
10. **H-10** `research-lead.md:91–105` — trim `## The 4-Step Procedure` to 2 lines; reference `knowledge-research` + `knowledge-packaging` skills.

### MEDIUM (12 findings)

11. **H-9** (re-classified MEDIUM): `research-lead.md:39–83` — add prime-directive block to Identity.
12. **M-1** (aggregate) — apply rule-by-ID discipline to Core rules sections of 5 bodies (project-lead, planning-lead, build-lead, fix-lead, research-lead); each body should have 4–6 R-### citations and 0 prose restating the rules.
13. **M-2** `project-lead.md:62–69` — restructure Identity to IS / IS NOT / prime (split single paragraph into 3 subsections).
14. **M-3** `project-lead.md:141–158` — move bootstrap-gate inline content into a `bootstrap-gate` skill or document the runtime removal mechanism.
15. **M-4** `planning-lead.md:62–95` — trim Identity prose preamble (L63–73) to 2 lines; keep IS/IS NOT/prime subsections.
16. **M-5** `build-lead.md:60–68` — add `### What it is NOT` subsection with 5 bullets from F-016 ref §1.
17. **M-6** `build-lead.md:114–127` — remove inlined builder-security rules; reference `task-orchestration` skill.
18. **M-7** `reviewer.md:110–172` — remove inlined 9-dim + 4-verdict matrices; reference `review-strategy`, `quality-review`, `acceptance-decision` skills.
19. **M-8** `reviewer.md:209` — fix constitution-checks.yaml path to `src/aspis/data/catalog/config/policy/constitution-checks.yaml`.
20. **M-9** `system-lead.md:122–134` — trim 6-step workflow inline; reference `system-awareness` + `asset-authoring` + `system-validation` skills.
21. **M-10** `fix-lead.md:89–136` — remove 4 inlined sections; reference workflow + 3 skills.
22. **M-11** `test-lead.md:74–130` — trim inlined How-you-work + failure-classification + labs testing; reference 2 skills.
23. **M-12** `research-lead.md:107–170` — remove inlined cache-system + research-types + output-formats; reference 4 skills.

### LOW (7 findings)

24. **L-1** `AGENT_BODY_STANDARD.md:27` — fix `mode` field docstring from `vibe/mvp/production` to `primary/subagent`.
25. **L-2** 4 bodies — fix workflow path references from `.aspis/workflows/` to `src/aspis/data/catalog/workflows/` (or document the render-time mapping).
26. **L-3** 2 bodies — swap title and "Derived" line order (project-lead.md:58, research-lead.md:35).
27. **L-4** = **C-1** (cosmetic twin).
28. **L-5** `planning-lead.md:117–123` — remove inlined 5-track table (subsumed by H-4).
29. **L-6** `project-lead.md:124–139` — compress 13 stop-and-ask conditions to 1 line.
30. **L-7** 8 bodies — restore the standard's section order once the inlined content is moved to skills (H-3 through H-10 + M-6 through M-12).
31. **Sharpening the standard's checklist**: add to AGENT_BODY_STANDARD.md L98–L111: `[ ] Core rules cite system rules by ID only; zero restated rule prose` and `[ ] How-you-work section is 1–2 lines + workflow pointer; no inlined procedure`.

---

## 8 · Cost-of-change impact

The current build's bodies are **large** (172–255 lines). Most of the size is
inlined procedure that belongs in skills/workflows. The bodies' size is the
direct cause of every MEDIUM and HIGH finding (M-1 through M-12, H-3 through
H-10) — when a body inlines 30–50 lines of procedure from a skill, the
body grows by that much and the cost-of-change test (SC-011) becomes harder
to satisfy.

If the body trim is done, the bodies should land in the **80–120 line** range
(thin) and the cost-of-change test continues to pass. The build's choice to
inline procedure is the single highest-leverage issue in this review.

---

## 9 · What the build did well

To be fair, the build did several things right:

1. **M-2 fix from the prior review is in**: planning-lead's delegates list (L37–L40)
   no longer has the 7 orphan subagents (clarify, task-decomposer, idea-capture,
   prd-writer, constitution-checker, scope-estimator, research-request-writer).
   Only 3 existing catalog agents (research-lead, reviewer, project-explorer).
   The FR-005 violation flagged in the prior completeness-traceability review
   is **resolved**.

2. **All skill references resolve**: 49 / 49 `skill:` references across the 8
   bodies point to existing `SKILL.md` files. FR-001 verified.

3. **All delegate references resolve**: 28 / 28 delegates point to existing
   catalog agents. The orphan-delegate sweep (T-31) is correct.

4. **Permission surfaces are least-privilege with deny floor honored**: no
   `bash: '*': allow` anywhere; `git commit*` only on committer (not in scope of
   this review but verified); `git push*` denied everywhere; `webfetch` only
   on system-lead and research-lead; `websearch` only on research-lead.

5. **DYNAMIC_READINESS.md is approved, R-008 is recorded in ACCEPTANCE.md, and
   all 8 bodies reference the convention correctly**: 8 / 8 dynamic-readiness
   blocks present and well-formed.

6. **Identity sections are present and substantive**: every body has an
   Identity section; 4 of 8 have full IS / IS NOT / prime directive; the
   others are close. The body team's instinct to add `## What you ARE` /
   `## What you are NOT` subsections (in 6 of 8 bodies) is the right pattern
   — the standard's 2–4 line budget just needs to be enforced on the prose
   preamble.

7. **Responsibilities→skills tables are complete**: 100% of responsibilities
   map to a skill, 100% of skills resolve to a SKILL.md file. The shape of
   the table is consistent across bodies (good).

8. **Delegation tables are present in 6 of 8 bodies**: when present, they
   name the delegate, the trigger, and the purpose. The two missing
   Delegation sections (project-lead, research-lead) are an easy fix.

9. **The bodies are faithful to the F-016 reference specs**: every body
   preserves the design intent, the permission surface, the skill mapping,
   and the role boundaries. The bodies are not role-drifted; they are
   **shape-drifted** (too long, too inlined, but otherwise correct).

---

## 10 · Verdict

**CHANGES REQUIRED** — 2 CRITICAL, 8 HIGH, 12 MEDIUM, 8 LOW findings.

The bodies are **structurally faithful** to the F-016 reference specs and
the permission surface, skill mapping, delegate edges, and dynamic-readiness
block are all correct. The L1 exit gate (T-32a) approval is correct on the
**shape** check (frontmatter, sections, references resolve). The bodies pass
SC-006 (every agent body passes agent-body standard check) at the
**shape level** — but they fail it at the **content level** because the
standard's "every section is short" and "cite, don't restate" rules are
systematically violated by inlined procedure.

**The fix is mechanical and small**: for each of the 8 bodies, replace the
inlined procedure with a 1–2 line pointer to the workflow or skill, and
collapse the Core rules to a 4–6 R-### ID list. After this trim, the bodies
should land in the 80–120 line range and the standard's content-level
checks will pass. The HIGH-level delegation-section additions (H-1, H-2)
and the CRITICAL heading typo (C-1) are single-line fixes.

**Recommendation**: route to build-lead for a **revision pass** of the 8
bodies plus the AGENT_BODY_STANDARD.md `mode`-field docstring fix (L-1).
Estimated fix time: 4–6 hours for 1 build agent. The bodies are
**acceptance-ready after these fixes**; the design is sound, the
specs are correct, and the build's substantive work is good.

**Do NOT proceed to T-33+ (L2-P0) without addressing C-1, H-1, H-2, and
H-3 through H-10** — these are the gate-blocking findings. The MEDIUM and
LOW findings are improvements that should be addressed in the same revision
pass but are not gate-blocking.

---

## Files reviewed

- `src/aspis/data/catalog/agents/project-lead.md` (193 lines)
- `src/aspis/data/catalog/agents/planning-lead.md` (209 lines)
- `src/aspis/data/catalog/agents/build-lead.md` (195 lines)
- `src/aspis/data/catalog/agents/reviewer.md` (255 lines)
- `src/aspis/data/catalog/agents/system-lead.md` (243 lines)
- `src/aspis/data/catalog/agents/fix-lead.md` (177 lines)
- `src/aspis/data/catalog/agents/test-lead.md` (172 lines)
- `src/aspis/data/catalog/agents/research-lead.md` (206 lines)
- `.aspis/context/AGENT_BODY_STANDARD.md` (112 lines)
- `.aspis/context/DYNAMIC_READINESS.md` (130 lines)
- `.aspis/rules/system-rules.md` (114 lines — R-001..R-010)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/project-lead.md` (930 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/planning-lead.md` (1158+ lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/build-lead.md` (620+ lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/reviewer.md` (405 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/system-lead.md` (470 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/fix-lead.md` (235 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/test-lead.md` (279 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/research-lead.md` (361 lines)
- `.aspis/features/F-017-complete-agent-system/ACCEPTANCE.md` (73 lines)
- `.aspis/features/F-017-complete-agent-system/Review/completeness-traceability.md` (546 lines, prior review)
- `src/aspis/data/catalog/config/policy/constitution-checks.yaml` (65 lines)
- `src/aspis/data/catalog/rules/architecture-constitution.md` (referenced in bodies)
- `src/aspis/data/catalog/workflows/*.md` (6 files, referenced in bodies)
- `src/aspis/data/catalog/skills/**/SKILL.md` (52 skill files, all referenced skills resolve)
