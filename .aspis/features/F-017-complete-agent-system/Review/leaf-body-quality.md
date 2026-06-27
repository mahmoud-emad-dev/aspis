# F-017 — Leaf Body Quality Review (L2-P0)

> **Reviewer**: Reviewer (independent)
> **Date**: 2026-06-27
> **Scope**: F-017 T-37..T-39 — 3 leaf agent bodies (committer, general-builder, project-explorer)
> **Perspective**: Leaf body quality — THIN, contract-conformant, R-006 disciplined
> **Verdict**: **APPROVED WITH NOTES** — 0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW

---

## Executive summary

The 3 L2-P0 leaf bodies (T-37, T-38, T-39) are a **substantial improvement** over the
L1 lead bodies reviewed in `.aspis/features/F-017-complete-agent-system/Review/agent-body-quality.md`.
The build-lead team has clearly internalized the L1 thinning lesson: every leaf is
**genuinely thin** (77–120 lines, well inside the cost-of-change budget), every leaf
has **all 7 required sections in order**, every leaf has **all 11 required frontmatter
fields**, every leaf is **read-only or scope-bounded by frontmatter**, every leaf
honors the **deny floor**, and every leaf is **faithful to its F-016 reference spec**.

| Body | Lines | Frontmatter | Sections | Restated rules | Inlined procedure | Verdict |
|---|---|---|---|---|---|---|
| `committer.md` | **77** | 11/11 ✓ | 7/7 ✓ | 0 / 2 ✗ clean | 0 / 0 ✓ clean | **clean** |
| `general-builder.md` | **120** | 11/11 ✓ | 7/7 ✓ | **3 / 4** ✗ restated | 0 / 0 ✓ clean | **M-1** |
| `project-explorer.md` | **85** | 11/11 ✓ | 7/7 ✓ | 2 / 2 (compact) ⚠ | 0 / 0 ✓ clean | **M-2 (style) + L-1..L-4** |

**Score per body (out of 100):**
- `committer.md` — **96 / 100** (clean; minor cosmetic notes)
- `general-builder.md` — **88 / 100** (clean shape; one R-006 partial violation in Core rules)
- `project-explorer.md` — **92 / 100** (clean shape; compact R-006 hints, minor styling)

**Comparison to L1 thinned bodies** (the standard the L1 review set):

| Body class | L1 thinned range | L2-P0 leaves | Direction |
|---|---|---|---|
| Leads (8) | 120–177 lines | — | baseline |
| Leaves (3) | — | **77–120 lines** | **better** (target met) |

The L1 review's "**80–120 line** range (thin) and the cost-of-change test continues to
pass" (L1 review §8) is **fully met** for the leaves — every leaf is at or below the
L1 lower bound, with committer at **77 lines** and project-explorer at **85 lines**,
both well below the thinness target. The build-lead team learned from the L1 thinning
pass.

**Cross-cutting verdict**: APPROVED WITH NOTES. The HIGH-severity rule-restatement
pattern the L1 review flagged in reviewer (H-6) and system-lead (H-7) **does not recur
in the committer or project-explorer**, and is **present only in general-builder** at
a lower severity (3 of 4 R-### have brief parenthetical restatements, not full
prose paragraphs). T-40 (L2-P0 integration check) can proceed; the 3 MEDIUM and 4 LOW
findings are clean-up items for the polish pass.

---

## 1 · Per-body check

### 1.1 · committer — `src/aspis/data/catalog/agents/committer.md` (77 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter 11/11 fields | ✓ | L1–L33 — name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope all present |
| Title line order | ✓ | L35 `# Committer` first, L36 `> Derived from Research/ref/committer.md` second |
| Identity 2–4 lines, IS/IS NOT, prime | ✓ | L38–L42 — 2 paragraphs (4 lines): IS ("single git writer"), IS NOT (in-line "not a builder, not a reviewer, not a pusher, not an amender, not a fixer, not a planner"), prime directive ("the ONE writer invariant (R-004)") |
| How you work 1–2 lines + pointer | ✓ | L44–L46 — 1 line natural-language + pointer to skills |
| Core rules cite R-###, own rules brief | ✓ | L48–L57 — 8 bullets: R-004, R-008 cited; 6 own rules; no restated rule prose |
| Responsibilities→skills complete | ✓ | L59–L65 — 3 rows, all map to existing skills (clean-tree-precondition, commit-message, commit-splitting) |
| Delegation | ✓ | L67–L69 — "None — the committer is a leaf agent (L3). No task block, no subagents, no delegation." |
| Dynamic-readiness block + reference | ✓ | L71–L77 — references `.aspis/context/DYNAMIC_READINESS.md`; 3 dials (mode, task kind, model tier) + leanest-correct-path default; 6 lines |
| Inline procedure (R-006) | ✓ | 0 lines inlined; all procedures reference skills by name |
| Skill refs resolve to SKILL.md | ✓ | 3/3 resolve (verified by glob: `clean-tree-precondition`, `commit-message`, `commit-splitting` SKILL.md files exist) |
| Delegate list empty (leaf) | ✓ | L12 `delegates: []` |
| Permission surface — `git commit*: allow` only here | ✓ | L26 `"git commit*": allow` — **only** leaf with this; builder L26 has `git commit*: deny`; explorer L21 has `git commit*: deny` |
| Deny floor honored | ✓ | L20 `*: deny`, L27 `git push*: deny`, L28–L29 `webfetch: deny`, `websearch: deny`, L30–L31 `edit: deny`, `write: deny` |
| Cost-of-change ≤ 3 files | ✓ | body + 2 unique skills (commit-message, commit-splitting) + 1 shared (clean-tree-precondition) = 3 unique files |
| `git add*` allow + comment | ✓ | L25 `"git add*": allow # guarded fallback (only when aspis is genuinely unavailable)` — matches F-016 ref spec L104–L105 |
| `tools` set has no `edit`/`write` | ✓ | L13–L17: `read`, `grep`, `glob`, `bash` only |

**Findings**: L-3 only.

### 1.2 · general-builder — `src/aspis/data/catalog/agents/general-builder.md` (120 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter 11/11 fields | ✓ | L1–L51 — name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope all present |
| Title line order | ✓ | L53 `# General Builder` first, L55 `> Derived from Research/ref/general-builder.md` second |
| Identity IS/IS NOT/prime directive | ✓ (expanded form) | L57–L82 — preamble L57–L61, IS L63–L70 (6 bullets), IS NOT L72–L75 (2 bullets), prime directive L77–L81 |
| How you work 1–2 lines + pointer | ✓ (4 lines, slightly over) | L83–L86 — 2 lines of procedure + pointer to `.aspis/workflows/small-task.md` |
| Core rules cite R-###, own rules brief | ✗ | L88–L98 — 4 R-### cited, **3 of 4 have full parenthetical restatements** (R-001, R-004, R-005); see M-1 |
| Responsibilities→skills complete | ✓ | L100–L105 — 2 rows (prestart-checks, clean-tree-precondition), both resolve |
| Delegation | ✓ | L107–L110 — "None — the general-builder is a leaf agent (L3). No `task:` block, no subagents, no delegation to the Reviewer, Committer, or another builder." |
| Dynamic-readiness block + reference | ✓ | L112–L120 — references DYNAMIC_READINESS.md; 3 dials (model, task, mode) + default; 6 lines |
| Inline procedure (R-006) | ✓ | 0 lines inlined; all procedures reference skills by name |
| Skill refs resolve to SKILL.md | ✓ | 2/2 resolve (prestart-checks, clean-tree-precondition) |
| Delegate list empty (leaf) | ✓ | L46 `delegates: []` |
| Permission surface — `edit`/`write` path-scoped | ✓ | L28–L43 — `edit` and `write` blocks have `*: allow` with 6 specific `*: deny` entries (rules/**, .aspis/rules/**, .claude/settings.json, .opencode/agents/**, **/permissions*.yaml, .aspis/current/active_feature.json); matches F-016 ref spec L120–L127 |
| Deny floor honored | ✓ | L17 `*: deny`, L26 `git commit*: deny`, L27 `git push*: deny`, L44–L45 webfetch/websearch deny |
| Cost-of-change ≤ 3 files | ✓ | body + 0 unique skills (prestart-checks shared with build-lead; clean-tree-precondition shared with committer) = 1 file |
| R-004 (no commit) | ✓ | L26 `git commit*: deny` |
| R-008 (no push) | ✓ | L27 `git push*: deny` |
| Turn cap own rule | ✓ | L97 **Own — turn cap**: soft 8, hard 16 |

**Findings**: M-1, M-3, L-4.

### 1.3 · project-explorer — `src/aspis/data/catalog/agents/project-explorer.md` (85 lines)

| Check | Status | Evidence |
|---|---|---|
| Frontmatter 11/11 fields | ✓ | L1–L39 — name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope all present |
| Title line order | ✓ | L41 `# Project Explorer` first, L43 `> Derived from Research/ref/project-explorer.md` second |
| Identity 2–4 lines, IS/IS NOT, prime | ✓ | L45–L49 — 2 paragraphs (4 lines): IS ("shared read-only helper"), IS NOT (in-line "Not a builder, planner, reviewer, researcher, committer, fixer, delegator, or expander"), prime directive ("the leaf + read-only invariant") |
| How you work 1–2 lines + pointer | ✓ | L51–L53 — 1 line procedure + pointer |
| Core rules cite R-###, own rules brief | ⚠ | L55–L65 — 2 R-### cited (R-001, R-004) with brief parenthetical context; 7 own rules; see L-1 |
| Responsibilities→skills complete | ✓ | L67–L72 — 2 rows, both procedural (no skill, matches ref spec §2) |
| Delegation | ✓ | L74–L76 — "None — the project-explorer is a leaf agent (L3). No task block, no subagents, no delegation." |
| Dynamic-readiness block + reference | ✓ | L78–L85 — references DYNAMIC_READINESS.md; 3 dials (model, task, mode) + default; 8 lines (slightly over 3–6 budget) |
| Inline procedure (R-006) | ✓ | 0 lines inlined; the 1-line procedure in How-you-work is a brief natural-language summary, not a duplicate of any skill content |
| Skill refs resolve | ✓ | L36 `skills: []` — **0 skill refs**; the body is procedural per ref spec §2 ("0 named skills") |
| Delegate list empty (leaf) | ✓ | L35 `delegates: []` |
| Permission surface — read-only (no edit/write tools) | ✓ | L8–L11 `tools:` has only `read`, `grep`, `glob`, `bash`; **no `edit`, no `write`**; explicit `git add*`, `git reset*`, `git clean*`, `git stash*`, `git checkout*`, `git rebase*`, `git amend*` denials in bash block L23–L29 |
| Deny floor honored | ✓ | L13 `*: deny`, L21 `git commit*: deny`, L22 `git push*: deny`, L33 `webfetch: deny`, L34 `websearch: deny` |
| Cost-of-change ≤ 3 files | ✓ | body + 0 unique skills = 1 file |
| R-004 read-only (no commit/push/add) | ✓ | L21–L29 all tree-mutating git commands explicitly denied |

**Findings**: M-2, L-1, L-2, L-4.

---

## 2 · Thinning comparison (vs L1 lead bodies)

The L1 review's "Cost-of-change impact" section (L1 review §8) said: "the bodies
should land in the **80–120 line** range (thin) and the cost-of-change test continues
to pass." The L1 leads landed in **120–255 lines** (overshot). The 3 L2-P0 leaves
land at **77, 85, 120 lines** — **on or below target**. The build-lead team **learned
from the L1 thinning pass**.

| Body | Lines | Inline procedure | Restated rules | R-006 compliant? |
|---|---|---|---|---|
| L1 leads (range) | 120–255 | 30–80 lines per body | 0–7 R-### per body | ✗ (all 8) |
| **L2-P0 leaves (range)** | **77–120** | **0 lines** | **0–3 R-### per body** | **✓ (2 of 3)** |

**Reading**: the 3 leaves are R-006 compliant at the **procedure level** (no inlined
workflow content) and R-006 compliant at the **rule-restatement level** in 2 of 3
bodies. Only general-builder's Core rules has a partial restatement pattern (3 of 4
R-### with brief parenthetical restatements); the L1 reviewer and system-lead had
this pattern with 7 of 8 and 6 of 8 missing citations respectively — **substantially
worse** than the general-builder's case.

---

## 3 · F-016 reference spec faithfulness

Cross-checked each leaf body against its F-016 reference spec
(`.aspis/features/F-016-agent-system-architecture/Research/ref/<agent>.md`):

| Body | Faithful to F-016 ref? | Notes |
|---|---|---|
| `committer.md` | ✓ | 3 skills (ref §2) all referenced; permission surface (ref §3) — bash allowlist exactly matches; deny floor (ref §3) — `git push*`, `webfetch`, `websearch`, `edit`, `write` all denied; no `edit`/`write` tools; no task delegation; model `cheap` (ref §4). The `git add*` "guarded fallback" matches ref §3 C3 use case exactly. |
| `general-builder.md` | ✓ | 2 skills (ref §2: prestart-checks, clean-tree-precondition) all referenced; permission surface (ref §3) — bash allowlist matches (pytest*, uv run pytest*, ruff check*, python .aspis/scripts/context/*, git status/diff/log, aspis preflight*); edit/write path-scoped with all 6 deny entries from ref §3; bash deny for git commit/push matches; turn cap (ref §5: 8/16) recorded in own rule L97; model `cheap` (ref §4 default). |
| `project-explorer.md` | ✓ | 0 skills (ref §2: "**0 named skills** — its work is procedural") — `skills: []` is correct; permission surface (ref §3) — bash allowlist matches (python[3] .aspis/scripts/context/*, git status/log/diff, aspis preflight*); all 7 git mutators explicitly denied; no edit/write tools; webfetch/websearch denied; "not found" honesty (ref §5 C1) and "not an exploration question" (ref §5 C2) both in Core rules; model `cheap` (ref §4); no task delegation. |

**Summary**: all 3 bodies are **substantively faithful** to F-016. No role drift.
The bodies preserve the design intent, the permission surface, the skill mapping,
the model tier, and the role boundaries. No missing use cases from ref §5.

---

## 4 · Frontmatter cross-check (all 11 fields)

| Field | committer | general-builder | project-explorer |
|---|---|---|---|
| `name` | `committer` ✓ | `general-builder` ✓ | `project-explorer` ✓ |
| `description` | one-sentence role ✓ | one-sentence role ✓ | one-sentence role ✓ |
| `mode` | `subagent` ✓ | `subagent` ✓ | `subagent` ✓ |
| `model` | `cheap` ✓ | `cheap` ✓ | `cheap` ✓ |
| `temperature` | `0.1` ✓ | `0.1` ✓ | `0.1` ✓ |
| `tools` | read,grep,glob,bash ✓ (4) | read,grep,glob,edit,write,bash ✓ (6) | read,grep,glob,bash ✓ (4) |
| `permissions` | bash+webfetch+websearch+edit+write ✓ | bash+edit+write+webfetch+websearch ✓ | bash+webfetch+websearch ✓ |
| `delegates` | `[]` ✓ | `[]` ✓ | `[]` ✓ |
| `skills` | 3 ✓ (committer skills) | 2 ✓ (builder skills) | `[]` ✓ (procedural) |
| `runtimes` | `[]` ✓ | `[]` ✓ | `[]` ✓ |
| `export_scope` | `full` ✓ | `full` ✓ | `full` ✓ |

**Result**: 11/11 on all 3 leaves. Total: **33/33 frontmatter fields** present and
correct. The `model: cheap` is consistent across all 3 leaves — every lead-type body
in L1 has `model: standard`; every leaf has `model: cheap` per the L1 review's
"Cheap by default" pattern (build-lead ref spec L185–L192; reviewer ref spec L148–
L170; F-016 ref §4 each leaf). The leaves are **correctly tiered**.

---

## 5 · Permission surface — per-leaf allow / deny matrix

### 5.1 committer — `committer.md:18-31`

| Tool | Pattern | Verdict | Ref spec match |
|---|---|---|---|
| bash | `*: deny` | ✓ deny floor | ref L99-108 |
| bash | `git status*: allow` | ✓ | ref L100 |
| bash | `git diff*: allow` | ✓ | ref L101 |
| bash | `git log*: allow` | ✓ | ref L102 |
| bash | `aspis commit*: allow` | ✓ primary | ref L105 |
| bash | `git add*: allow # guarded fallback` | ✓ ref L104-105 | matches |
| bash | `git commit*: allow` | ✓ **only agent with this** | ref L104 |
| bash | `git push*: deny` | ✓ R-008 | ref L113 |
| webfetch | `deny` | ✓ | ref L117 |
| websearch | `deny` | ✓ | ref L117 |
| edit | `deny` | ✓ | ref L118 |
| write | `deny` | ✓ | ref L118 |

**Result**: 12/12 permission lines correct; committer is the **only agent with
`git commit*: allow`** in the catalog (verified by grep across `src/aspis/data/catalog/agents/*.md`).

### 5.2 general-builder — `general-builder.md:15-46`

| Tool | Pattern | Verdict | Ref spec match |
|---|---|---|---|
| bash | `*: deny` | ✓ | ref L132-141 |
| bash | `pytest*: allow` | ✓ | ref L134 |
| bash | `uv run pytest*: allow` | ✓ | ref L135 |
| bash | `ruff check*: allow` | ✓ | ref L136 |
| bash | `python .aspis/scripts/context/*: allow` | ✓ | ref L137 |
| bash | `git status*: allow` | ✓ | ref L138 |
| bash | `git diff*: allow` | ✓ | ref L139 |
| bash | `git log*: allow` | ✓ | ref L140 |
| bash | `aspis preflight*: allow` | ✓ | ref L141 |
| bash | `git commit*: deny` | ✓ R-004 | ref L145 |
| bash | `git push*: deny` | ✓ R-008 | ref L146 |
| edit | `*: allow` + 6 denies | ✓ path-scoped | ref L120-127 |
| write | `*: allow` + 6 denies | ✓ path-scoped | ref L120-127 |
| webfetch | `deny` | ✓ | ref L152 |
| websearch | `deny` | ✓ | ref L152 |

**Result**: 15/15 permission lines correct; **R-004 honored** (no commit), **R-008
honored** (no push), **edit/write path-scoped** to packet.allowed with all 6
forbidden-paths from ref L122-127 explicitly denied.

### 5.3 project-explorer — `project-explorer.md:12-34`

| Tool | Pattern | Verdict | Ref spec match |
|---|---|---|---|
| tools | read, grep, glob, bash (no edit, no write) | ✓ R-004 read-only | ref L109-113 |
| bash | `*: deny` | ✓ | ref L116-125 |
| bash | `python .aspis/scripts/context/*: allow` | ✓ | ref L118 |
| bash | `python3 .aspis/scripts/context/*: allow` | ✓ | ref L118 |
| bash | `git status*: allow` | ✓ | ref L120 |
| bash | `git log*: allow` | ✓ | ref L121 |
| bash | `git diff*: allow` | ✓ | ref L122 |
| bash | `aspis preflight*: allow` | ✓ | ref L123 |
| bash | `git commit*: deny` | ✓ R-004 | ref L128 |
| bash | `git push*: deny` | ✓ R-008 | ref L129 |
| bash | `git add*: deny` | ✓ explicit | ref L131 |
| bash | `git reset*: deny` | ✓ | ref L131 |
| bash | `git clean*: deny` | ✓ | ref L131 |
| bash | `git stash*: deny` | ✓ | ref L131 |
| bash | `git checkout*: deny` | ✓ | ref L131 |
| bash | `git rebase*: deny` | ✓ | ref L131 |
| bash | `git amend*: deny` | ✓ | ref L131 |
| bash | `pip install*: deny` | ✓ | ref L133 |
| bash | `npm install*: deny` | ✓ | ref L133 |
| bash | `make install*: deny` | ✓ | ref L133 |
| webfetch | `deny` | ✓ | ref L132 |
| websearch | `deny` | ✓ | ref L132 |

**Result**: 22/22 permission lines correct; **read-only by tool set** (no edit, no
write in tools list), **R-004 honored** (no commit, no add, no reset, no clean,
no stash, no checkout, no rebase, no amend), **R-008 honored** (no push), **all
install commands denied** (ref L133).

### 5.4 Cross-body deny-floor check

| Pattern | committer | general-builder | project-explorer | Required |
|---|---|---|---|---|
| `git commit*: allow` | ✓ (the only one) | ✗ (deny) | ✗ (deny) | committer-only ✓ |
| `git push*: deny` | ✓ | ✓ | ✓ | none ✓ |
| `webfetch: deny` | ✓ | ✓ | ✓ | system-lead + research-lead only ✓ |
| `websearch: deny` | ✓ | ✓ | ✓ | research-lead only ✓ |
| `edit: deny / not in tools` | ✓ (deny) | allow path-scoped | ✓ (not in tools) | scope-controlled ✓ |
| `write: deny / not in tools` | ✓ (deny) | allow path-scoped | ✓ (not in tools) | scope-controlled ✓ |
| No `bash: '*': allow` | ✓ | ✓ | ✓ | never ✓ |

**Result**: the **deny floor is honored across all 3 leaves** with no exceptions.
The user's checklist question — "git commit*: committer-only, denied on builder +
explorer?" — is verified:
- committer L26: `git commit*: allow` ✓
- general-builder L26: `git commit*: deny` ✓
- project-explorer L21: `git commit*: deny` ✓

---

## 6 · Findings (severity-ordered, with file:line evidence)

### CRITICAL (0)

None.

### HIGH (0)

None. The L1 review's HIGH-severity R-006 rule-restatement pattern (H-6 reviewer,
H-7 system-lead) **does not recur in the committer or project-explorer**, and the
general-builder's restatement is **brief parenthetical, not full prose paragraphs** —
so downgraded to MEDIUM (M-1).

### MEDIUM (3)

#### M-1 · general-builder.md:88-98 — Core rules restate 3 of 4 R-### in parentheticals

**File**: `src/aspis/data/catalog/agents/general-builder.md:88–98`
**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §4 Core rules
— "A bullet list of system rules cited by ID only... never restate what the rule says."
§"Forbidden patterns" — "**No restated rules**: never write 'R-001 means scope control —
don't touch forbidden files.' Write only 'R-001' and let the system rules speak for
themselves."

**Evidence** (file:line):

```
90: - R-001 (scope control — stay in packet's allowed files)
91: - R-004 (one writer — never commit)
92: - R-005 (tests-as-spec — never weaken or delete a test)
93: - R-008 (human-gated push)
```

R-001's system-rule text: "Change only the files your task or role allows. Never touch
forbidden paths or secrets." (system-rules.md L73)
R-004's system-rule text: "One writer per branch. Reviewers are read-only. Only the
committer creates commits; no agent commits its own work." (system-rules.md L85)
R-005's system-rule text: "Tests are part of the specification. Behaviour changes need
tests; fixes need a regression test. Never weaken or delete a test to make a gate pass."
(system-rules.md L89)

The general-builder's L90–L92 each paraphrase the system rule in the parenthetical,
which is **exactly the anti-pattern the standard's "Forbidden patterns" calls out by
name** ("R-001 means scope control — don't touch forbidden files" is the standard's
example; the body uses "R-001 (scope control — stay in packet's allowed files)" with
the same shape).

**Why it matters**: SC-006 says "every agent body passes agent-body standard check";
this fails the standard's content-level check. The build team is **inconsistent** —
L1 leads (build-lead L99-105, reviewer L100-107, test-lead L84-89) and the committer
(L50-51) cite R-### by ID only with no parens; only general-builder and project-explorer
add parenthetical context. The standard's "Cite, don't restate" is the load-bearing
rule for cost-of-change.

**Severity rationale**: downgraded from HIGH to MEDIUM because (a) **all 4 R-### are
cited** (the L1 reviewer/system-lead HIGH was for missing citations, not for brief
restatements), (b) the restatements are **brief parentheticals, not full prose
paragraphs**, and (c) the project-explorer's compact hints are a milder form of the
same pattern (L-1).

**Fix**: replace L90–L92 with bare R-### citations:
```
- R-001
- R-004
- R-005
- R-008
```
Keep L93 as-is (already terse) and the 5 own rules (L94-98).

**Severity**: MEDIUM.

#### M-2 · 3 leaves — Identity style inconsistency (2 terse, 1 expanded)

**Files**:
- `committer.md:38-42` — 4 lines, 2-paragraph terse form (IS, IS NOT, prime)
- `project-explorer.md:45-49` — 4 lines, 2-paragraph terse form (IS, IS NOT, prime)
- `general-builder.md:57-82` — 26 lines, expanded form (preamble + IS sub-section +
  IS NOT sub-section + prime sub-section)

**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §2 Identity
— "2–4 lines establishing what the agent IS and what it IS NOT, plus its prime
directive." The standard's **upper bound is 4 lines**; the general-builder's Identity
is 26 lines.

**Why it matters**: the 3 leaves are **internally inconsistent**. Two of three use
the terse form that meets the standard's 2-4 line budget; one of three uses the
expanded form that matches the L1 lead pattern (build-lead.md:60-88 = 29 lines,
reviewer.md:52-80 = 29 lines). The build team picked **two different style guides**
for the 3 leaves.

**Fix (one of two)**:
- **Option A (compress general-builder)**: collapse general-builder Identity to 4
  lines in the committer/project-explorer style. Move the 6 IS bullets and 2 IS-NOT
  bullets into the "What it IS" / "What it IS NOT" sub-sections of the L1 leads'
  prime-directive pattern **OR** drop them entirely as restated content.
- **Option B (expand committer and project-explorer)**: add full IS / IS NOT / prime
  sub-sections to committer and project-explorer, matching general-builder and the
  L1 leads. More readable but adds ~20 lines to each.

**Recommendation**: Option A. The terse 4-line Identity already covers IS / IS NOT /
prime for all 3 leaves; the expanded IS/IS NOT sub-sections add **detail** but not
**information the prime directive doesn't already convey**. The terse form passes
the standard's budget; the expanded form does not. Consistency is the goal.

**Severity**: MEDIUM (stylistic; the bodies are individually compliant, but the
inconsistency is a sign the build team did not enforce a single style across the 3
leaves).

#### M-3 · 2 of 3 leaves — workflow path references use `.aspis/workflows/` (deployed path)

**Files**:
- `general-builder.md:86` — `See .aspis/workflows/small-task.md.`
- `project-explorer.md:53` — `See .aspis/workflows/small-task.md.`

**Standard violation**: AGENT_BODY_STANDARD.md §"Principles" L16-18 — "**No dead
references**: every delegate, skill, workflow, and template the body names must exist."

**Evidence**: the bodies reference `.aspis/workflows/small-task.md`, but in this
factory repo the workflow lives at `src/aspis/data/catalog/workflows/small-task.md`
(verified by glob — the `.aspis/workflows/` directory does not exist in this repo;
it would exist in a target project after `aspis export`).

**Why it matters**: this is the **same L-2 finding** the L1 review flagged in 4 of 8
L1 bodies. The 2 L2-P0 leaves perpetuate the pattern. From a factory-repo perspective
the path is stale; from a deployed-project perspective it is correct.

**Fix**: change both references to `src/aspis/data/catalog/workflows/small-task.md`
(factory-repo perspective) — or document a render-time substitution rule. The
cleaner fix is to use the catalog source path.

**Severity**: MEDIUM (subsumes the L1 review's L-2 for the leaf bodies; not gate-blocking
because the file does exist, just at a different prefix).

### LOW (4)

#### L-1 · project-explorer.md:55-65 — Core rules add compact parenthetical context to R-###

**File**: `src/aspis/data/catalog/agents/project-explorer.md:55-65`
**Standard violation**: same as M-1 (R-006 partial). Less severe than M-1 because
the parentheticals are **operational hints** ("stay scoped to the question", "no
edit/write tools; no tree mutation"), not full rule restatements.

**Evidence**:
```
57: - R-001 — scope control (stay scoped to the question)
58: - R-004 — read-only (no edit/write tools; no tree mutation)
```

The R-001 rule is "Change only the files your task or role allows. Never touch
forbidden paths or secrets." The hint "stay scoped to the question" is **how the
explorer applies the rule to its read-only role** — a legitimate operational
application, not a verbatim restatement. Same logic for R-004.

**Why it matters**: the standard's example of restatement is "R-001 means scope
control — don't touch forbidden files" — which is the **rule's name + paraphrase**.
The project-explorer's hints are **the rule's name + application**. Borderline.

**Fix**: optionally replace with bare R-### citations to match the L1 leads and the
committer:
```
- R-001
- R-004
```

**Severity**: LOW (borderline R-006; not a clear violation; consistent with
M-1's fix direction).

#### L-2 · project-explorer.md:53 — workflow pointer to `small-task.md` is a stretch

**File**: `src/aspis/data/catalog/agents/project-explorer.md:53`
**Standard violation**: AGENT_BODY_STANDARD.md §"Principles" L16-18 — "No dead
references."

**Evidence**: the body says "Orient from FILE_REGISTRY.yaml and CODE_MAP.md → targeted
grep/glob → open only needed files → return compact findings. See `.aspis/workflows/small-task.md`."
The `small-task.md` workflow describes **how to implement a small task** (Classify →
One packet → Build → Review → Gate & commit) — not how to do a read-only repo
exploration. The file at `src/aspis/data/catalog/workflows/small-task.md` does
**resolve**, so this is not a dead reference, but the **semantic match is poor**.

**Why it matters**: a runtime agent following this pointer will find a workflow
about implementing a small task, not about exploring. The pointer is more of a
"the explorer is also narrow work" hint than a true procedure reference.

**Fix**: either (a) add a dedicated `explore.md` workflow at
`src/aspis/data/catalog/workflows/explore.md` and point there, or (b) replace the
pointer with a single line that says "no workflow — see the procedural steps in
§How you work."

**Severity**: LOW (file resolves; semantic match is poor; not gate-blocking).

#### L-3 · committer.md:44-46 — How you work pointer omits 1 of 3 skills

**File**: `src/aspis/data/catalog/agents/committer.md:44-46`
**Standard violation**: AGENT_BODY_STANDARD.md §"How you work" — "1-2 lines of
natural-language procedure plus a pointer to the workflow."

**Evidence**: L44-46 reads:
```
Confirm exact scope → stage named paths → compose conventional message → commit →
read hook output. See the `commit-message` and `commit-splitting` skills.
```

The committer's frontmatter L8-11 lists 3 skills: `clean-tree-precondition`,
`commit-message`, `commit-splitting`. The pointer names only 2 of 3. The
`clean-tree-precondition` skill is **implicit** in the "Confirm exact scope" step
but not named.

**Why it matters**: not a violation of any standard rule (the "How you work"
section is 1-2 lines + a pointer; it does not have to list every skill). Just an
**incomplete pointer** that could lead a runtime agent to miss the clean-tree check.

**Fix**: append `clean-tree-precondition` to the pointer, or rewrite as
"See the 3 frontmatter skills."

**Severity**: LOW (pointer is functional; the missing skill is implicit in the
procedure summary; not gate-blocking).

#### L-4 · 3 leaves — Dynamic-readiness dial order is inconsistent

**Files**:
- `committer.md:73-77` — order: mode, task kind, model tier
- `general-builder.md:114-120` — order: model, task kind, mode
- `project-explorer.md:80-85` — order: model, task kind, mode

**Standard violation**: AGENT_BODY_STANDARD.md §"Required body sections" §7
Dynamic-readiness — "One short block (3-6 lines) applying the three dynamic-readiness
dials to this agent's work. References `.aspis/context/DYNAMIC_READINESS.md`."

**Evidence**: DYNAMIC_READINESS.md L17 names the 3 dials in order: **1. Mode, 2. Task
kind/scope, 3. Model capability**. The committer follows this order. The other 2
leaves use **model-first** order. The convention document provides a reference
template (L92-105) that also uses **mode → task → model** order.

**Why it matters**: the standard says "**References `.aspis/context/DYNAMIC_READINESS.md`**"
but does not explicitly mandate the dial order. The convention document's reference
template does. The L1 leads also vary in order (build-lead L131-138 uses
mode→task→model; reviewer L136-143 uses mode→task→model; test-lead L110-117 uses
mode→task→model). So **the L1 leads are consistent with the convention's order**,
and the 2 L2-P0 leaves are inconsistent with both the convention and the L1 leads.

**Fix**: reorder the dials in general-builder and project-explorer to
mode → task kind → model tier. One-line edit per body.

**Severity**: LOW (stylistic; content is correct; order is the only issue).

---

## 7 · Cost-of-change verification (per standard §"Checklist" L111)

> [ ] Cost-of-change for this agent's asset set ≤ 3 files (the body, any skill it
>      uniquely owns, and at most one referencing agent's frontmatter)

| Body | Body | Unique skills | Shared skills | Total unique | ≤ 3? |
|---|---|---|---|---|---|
| committer | `committer.md` | commit-message, commit-splitting (2) | clean-tree-precondition (1) | 3 | ✓ |
| general-builder | `general-builder.md` | (none) | prestart-checks (1), clean-tree-precondition (1) | 1 | ✓ |
| project-explorer | `project-explorer.md` | (none) | (none) | 1 | ✓ |

**Result**: all 3 leaves pass the cost-of-change test with margin. The committer
touches 3 files at most (body + 2 unique skills); the builder and explorer touch
1 file each. **SC-011 verified for all 3 leaves.**

---

## 8 · R-006 single-source check (the load-bearing standard rule)

The R-006 rule is: "An agent instruction holds identity, rules, and skill references;
the intelligence lives in skills. State each fact once and reference it — don't
duplicate rules, procedures, or assets."

| Check | committer | general-builder | project-explorer |
|---|---|---|---|
| Zero inlined procedure | ✓ 0 lines | ✓ 0 lines | ✓ 0 lines |
| Zero restated R-### in prose | ✓ clean | ✗ 3 of 4 (M-1) | ⚠ 2 of 2 compact (L-1) |
| Zero duplicated workflow content | ✓ | ✓ | ✓ (file resolves) |
| Skills referenced by name not inlined | ✓ | ✓ | ✓ (procedural) |
| `commit-convention.yaml` referenced (not inlined) | ✓ L54 | n/a | n/a |
| F-016 ref spec referenced (not inlined) | ✓ L36 | ✓ L55 | ✓ L43 |

**R-006 verdict**: 2 of 3 leaves fully compliant; 1 of 3 (general-builder) has a
partial restatement in Core rules (M-1); 1 of 3 (project-explorer) has a compact
borderline form (L-1). **The build team is on the right track** — the major
R-006 violation that the L1 review flagged (inlined procedure in 8 of 8 L1 bodies)
is **completely absent** in the leaves.

---

## 9 · What the build did well

1. **Thin from the start**. The 3 leaves are 77–120 lines. The L1 review's target
   range was 80–120. Every leaf is at or below the target. The build team **learned
   from the L1 thinning pass** — committer is 77 lines, well below the target.
2. **No inlined procedure**. R-006's "no duplicated content" rule is honored at the
   procedure level in all 3 leaves. This is the **single largest improvement** over
   the L1 leads, which inlined 30–80 lines of procedure per body.
3. **All 11 frontmatter fields present**. 33/33 across the 3 leaves. No missing
   fields, no typos, no out-of-band values.
4. **All 7 body sections present, in order**. 21/21 sections across the 3 leaves.
   No missing sections (the L1 review flagged 2 missing Delegation sections and 1
   missing How-you-work section in L1; the leaves have **none** missing).
5. **All skill and workflow references resolve**. 5/5 leaf skill refs resolve to
   existing SKILL.md files; 2/2 workflow refs resolve to existing workflow files
   (modulo the path-prefix issue in M-3).
6. **Deny floor honored across all 3 leaves**. No `bash: '*': allow`. `git push*`
   denied on all 3. `webfetch` / `websearch` denied on all 3. `git commit*`
   allowed **only on the committer** — denied on builder and explorer.
7. **Permission surfaces match F-016 ref spec**. The bash allowlist for each leaf
   is a **direct subset** of its ref spec's bash allowlist. The edit/write path
   scopes on general-builder match the ref spec's allowed/denied tables.
8. **Identity matches F-016 ref spec**. Every leaf's Identity section uses the
   "leaf + read-only" or "single git writer" or "disposable executor" framing
   from its ref spec.
9. **No task delegation in any leaf**. All 3 have `delegates: []` and a
   `## Delegation` section stating "None — the X is a leaf agent (L3)."
10. **Model tier `cheap` on all 3 leaves**. Consistent with F-016 ref §4 (all 3
    leaves have "Cheap" as their model tier).
11. **runtimes: [] on all 3 leaves**. L1 leads use `runtimes: [opencode, claude]`;
    leaves are runtime-agnostic (the runtime injects them per deployment).
12. **export_scope: full on all 3 leaves**. Consistent with L1 leads.
13. **Cost-of-change test passes** for all 3 leaves. The standard's L111 checklist
    item is verified: 1–3 files per leaf, well within the budget.

---

## 10 · Verdict

**APPROVED WITH NOTES** — 0 CRITICAL, 0 HIGH, 3 MEDIUM, 4 LOW.

The 3 L2-P0 leaf bodies (committer, general-builder, project-explorer) are
**substantively complete and R-006 compliant at the procedure level**. They are
**genuinely thin** (77–120 lines, all below the L1 lower bound). They have **all
7 standard sections in order, all 11 frontmatter fields, correct delegation
(none), correct permission surfaces, correct deny floor, and faithful
implementation of the F-016 reference specs**.

The **build team learned from the L1 thinning pass**:
- No inlined procedure in any of the 3 leaves (vs. 8 of 8 L1 leads)
- No missing Delegation sections (vs. 2 of 8 L1 leads)
- No missing How-you-work sections (vs. 2 of 8 L1 leads)
- No restated workflow content (vs. 8 of 8 L1 leads)
- Bodies land in the 77–120 line range (target met; L1 leads overshot at 120–255)

The 3 MEDIUM findings (general-builder's Core rules restatements, Identity style
inconsistency, workflow path references) and 4 LOW findings (compact R-### hints,
imprecise workflow pointer, incomplete skill pointer, dial order inconsistency) are
**stylistic improvements** that the polish pass (T-55) should address. None of
them are gate-blocking for L2-P0 closure (T-40).

**Recommendation**: proceed to **T-40** (L2-P0 integration check). The 3 MEDIUM
and 4 LOW findings are queued for the polish pass (T-55) or for the next iteration
of the bodies. The general-builder's M-1 is the **single most important clean-up
item** because it touches a load-bearing rule (R-006) and the standard's forbidden
pattern by name; it is a 1-line fix.

**Do NOT proceed to L2-P1 (T-41+) without addressing at least M-1** — the L1
review's verdict (§10) was that the rule-restatement pattern in reviewer (H-6) and
system-lead (H-7) is HIGH-severity; general-builder's M-1 is the same pattern at
lower severity (only 3 of 4 R-### restated, all brief) but should be cleaned up
before L2-P1 begins so the polish pass (T-55) finds a clean baseline.

---

## Files reviewed

- `src/aspis/data/catalog/agents/committer.md` (77 lines)
- `src/aspis/data/catalog/agents/general-builder.md` (120 lines)
- `src/aspis/data/catalog/agents/project-explorer.md` (85 lines)
- `.aspis/context/AGENT_BODY_STANDARD.md` (112 lines) — the contract
- `.aspis/context/DYNAMIC_READINESS.md` (130 lines) — the convention
- `.aspis/rules/system-rules.md` (114 lines — R-001..R-010) — the rules cited
- `.aspis/features/F-016-agent-system-architecture/Research/ref/committer.md` (229 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/general-builder.md` (296 lines)
- `.aspis/features/F-016-agent-system-architecture/Research/ref/project-explorer.md` (254 lines)
- `.aspis/features/F-017-complete-agent-system/Review/agent-body-quality.md` (949 lines, prior L1 review — for comparison)
- `src/aspis/data/catalog/workflows/small-task.md` (40 lines) — workflow pointer target
- `src/aspis/data/catalog/skills/clean-tree-precondition/SKILL.md` — referenced
- `src/aspis/data/catalog/skills/prestart-checks/SKILL.md` — referenced
- `src/aspis/data/catalog/skills/commit-message/SKILL.md` — referenced
- `src/aspis/data/catalog/skills/commit-splitting/SKILL.md` — referenced
- All 12 agent bodies in `src/aspis/data/catalog/agents/*.md` — for the `git commit*: allow` cross-check (committer is the only one)
