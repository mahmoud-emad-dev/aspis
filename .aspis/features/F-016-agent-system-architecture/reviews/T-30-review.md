# Review — F-016 / T-30

> Filled by the reviewer (read-only — you evaluate and report, you never edit the
> work). The header is stamped by `aspis artifact`; you fill the verdict and
> findings from evidence (the diff, the tests, the acceptance criteria).

- **Feature**: F-016 — agent system architecture
- **Task**: T-30 — Catalog structural validation
- **Date**: 2026-06-27
- **Re-review of**: `248b0aa` (changes-requested) → `f574496` (the runtimes fix)
- **Verdict**: approved-with-notes

## Scope reviewed

All 11 in-scope catalog agent files at `src/aspis/data/catalog/agents/`:

- `project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`,
  `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`,
  `committer.md`, `general-builder.md`, `project-explorer.md`

Plus the contracts that define the gate, and the fix diff:

- `.aspis/features/F-016-agent-system-architecture/SPEC.md` (FR-007, FR-010, FR-011, FR-012)
- `.aspis/features/F-016-agent-system-architecture/TASKS.md` (T-30 gate, lines 210–214; build notes, lines 7–25)
- `.aspis/features/F-016-agent-system-architecture/PLAN.md` (§Component 2, line 30)
- `git diff f574496~1 f574496` — the runtimes fix (11 files, 11 insertions, one line per file)
- `src/aspis/data/catalog/skills/` — 38 skill directories, for the "every referenced skill exists" check

`bootstrap.md` is the 12th file in the directory. It is **explicitly excluded from
T-30 scope** (TASKS.md:210–211 names "all 11" files; the previous review
REVIEW-F-016-T-30.md:28–30 confirmed the 11-count). Its missing `delegates` and
`runtimes` are tracked as a follow-up, not a T-30 blocker.

## Findings from the re-review

| Severity | Where | Finding | Suggested fix |
|----------|-------|---------|---------------|
| **high** | (resolved) `src/aspis/data/catalog/agents/*.md` (all 11 files) | **HIGH #1 from the previous review — RESOLVED.** `runtimes: []` is now present in all 11 in-scope files. Verified by: (a) `git diff f574496~1 f574496 --stat` shows 11 files changed, 11 insertions, one line per file, every insertion being `runtimes: []`; (b) `grep "^runtimes:" src/aspis/data/catalog/agents/*.md` returns exactly 11 matches, one per in-scope file (build-lead:53, committer:32, fix-lead:59, general-builder:50, planning-lead:64, project-explorer:38, project-lead:52, research-lead:30, reviewer:42, system-lead:45, test-lead:35). The empty list is the correct value — the `CatalogAgent` parser (`src/aspis/catalog.py:96`) defaults absence to all runtimes, but the gate requires the field to be present, and absence of any runtime-specific feature is the truth for all 11 agents. | None — fix is correct. |
| **high** | (resolved) the validation that produced "11/11 PASS" | **HIGH #2 from the previous review — RESOLVED.** The original "incomplete field list" that missed `runtimes` is fixed: the re-validation in this re-review explicitly checks all 11 fields required by FR-011 (`SPEC.md:75`: name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope) AND the 10 fields named in the T-30 gate (`TASKS.md:214`: name, description, mode, model, tools, permissions, delegates, skills, runtimes, export_scope). See "Acceptance walk-through" below — every required field is present in all 11 files. | None — verified. |
| medium | (deferred) `src/aspis/data/catalog/agents/planning-lead.md:42–48` | **MEDIUM #3 from the previous review — DOCUMENTED.** The 7 future L3 subagents (`clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer`) do not exist as agents. The T-30 gate's literal "every delegate exists" check is failing on these 7. The build notes (`TASKS.md:19–21`) explicitly permit this: *"Subagent roster is OUT of scope → F-017. The 'future subagents' named in the specs are NOT built here — leave them as references."* This is the owner-decided exemption; the build notes are the durable record. Not blocking T-30. | None required for T-30. The exemption is the build note. When F-017 lands, the listed subagents will exist and the gate becomes naturally true. |
| medium | `src/aspis/data/catalog/agents/system-lead.md:32` | **MEDIUM #4 from the previous review — RE-FRAMED.** The catalog has `websearch: deny` for system-lead; FR-007 (`SPEC.md:69`) implies `websearch: allow` for system-lead. This is a **SPEC/PLAN inconsistency**, not a catalog bug: the reference spec (the design source) explicitly denies websearch for system-lead, the T-23 build notes (`TASKS.md:177`) lock that as the owner decision ("websearch: deny (align with catalog intent)"), and the catalog correctly follows the design. The SPEC text is the side that's wrong. T-23 was applied as documented; the SPEC was not updated. | Open a follow-up: update FR-007 in `SPEC.md` to match the T-23 decision (system-lead `websearch: deny`, research-lead `websearch: allow`). Tracked for T-39 (`TASKS.md:275: "Update SPEC.md Clarifications section with any decisions made during build"`). Not blocking T-30. |
| low | (this re-review) `src/aspis/data/catalog/skills/` | **New note (not a previous-review finding).** Four skills are referenced in agent frontmatter but do not exist as catalog skill directories: `mode-decision` and `constitution-checks` (planning-lead.md:61, 62); `packet-validation` and `builder-selection` (build-lead.md:51, 52). The T-30 gate criterion "Every referenced skill exists in catalog" (`TASKS.md:214`) is therefore **technically failing on 4 skills**. The previous review (`REVIEW-F-016-T-30.md:49`) explicitly deferred this to **T-31** (Produce missing skills inventory), and T-31 is in the critical path (`TASKS.md:5: "T-30 → T-32..T-37 → T-38"`). This re-review follows the same pattern: deferred, not blocking. | None for T-30. T-31 will enumerate the gap and produce the missing skills. |
| low | (this re-review) `src/aspis/data/catalog/agents/bootstrap.md` | **12th file — out of T-30 scope but flagged for awareness.** `bootstrap.md` lacks `delegates` and `runtimes` fields in its frontmatter (lines 1–29). T-30 explicitly scopes itself to the 11 agent files (TASKS.md:210–211); bootstrap.md is excluded because it self-deletes post-onboarding. The previous review (`REVIEW-F-016-T-30.md:28–30`) confirmed this scope. The gap is a real follow-up — bootstrap.md renders and runs, but the catalog structural check would fail on it. | Open a follow-up task: align bootstrap.md frontmatter to the same 11-field shape, OR add a T-30.5 sub-task to the spec, OR formally note in `SPEC.md` that bootstrap.md is structurally exempt. Not blocking T-30. |
| low | (verified) `src/aspis/data/catalog/agents/committer.md:26` | **Committer isolation — VERIFIED PASS.** `grep "git commit\*": src/aspis/data/catalog/agents/*.md` returns 16 matches: 1 allow (committer.md:26), 1 deny-each in the 10 other in-scope files (research-lead lists it as deny in body table, not in bash allowlist — also correct), and 4 body-text references in build-lead, general-builder, and committer itself. The `git commit*: allow` lives only in committer.md. | None — claim verified. |
| low | (verified) `src/aspis/data/catalog/agents/reviewer.md:26–29` and `project-explorer.md:7–11` | **Read-only claim — VERIFIED PASS.** `reviewer.md` frontmatter has `edit: "*": deny` and `write: "*": deny` (lines 26–29); `project-explorer.md` frontmatter `tools:` list (lines 7–11) is `[read, grep, glob, bash]` with no `edit` or `write`. Both agents are structurally read-only. | None — claim verified. |

## Acceptance criteria walk-through

The T-30 gate (`TASKS.md:214`) is five sub-criteria. Each is evaluated against
the current state of the 11 in-scope files.

### 1. "Every frontmatter has: name, description, mode, model, tools, permissions, delegates, skills, runtimes, export_scope."

Direct read of all 11 files (and `grep "^name:"` returning 12 matches — 11 in-scope
plus bootstrap.md) confirms every required field is present in every file. The
`runtimes: []` line added by `f574496` is the only previously-missing field, and
it is now present in all 11. **PASS.**

### 2. "Every referenced skill exists in catalog."

Cross-check of all skill names in the 11 frontmatter `skills:` blocks against
`src/aspis/data/catalog/skills/` (38 directories). Four skills are referenced
but not in the catalog: `mode-decision`, `constitution-checks`,
`packet-validation`, `builder-selection`. The previous review deferred this
finding to T-31 (`TASKS.md:216`); T-31 is in the F-016 critical path
(`TASKS.md:5`). **TECHNICALLY FAILING — DEFERRED to T-31.**

### 3. "Every delegate exists."

7 future subagents are listed in `planning-lead.md:42–48` but do not exist as
agent files. The build notes (`TASKS.md:19–21`) explicitly defer them to F-017.
**TECHNICALLY FAILING — DEFERRED to F-017 (owner-decided, documented).**

### 4. "No committer in non-committer task lists."

No agent has a `task:` block in frontmatter (verified by `grep "^  task:"` — no
matches in the catalog). The `committer` appears in 3 agents' `delegates:` lists
(build-lead.md:41, fix-lead.md:49, system-lead.md:36) — the orchestrators that
hand off completed work to the single writer. This is the correct pattern
(R-004 one-writer), not a violation. **PASS.**

### 5. (FR-011, SPEC.md:75) "name, description, mode, model (tier), temperature, tools, permissions (bash + web), delegates, skills, runtimes, export_scope."

All 11 fields present in all 11 files. `temperature` was added in `04f79a8`
(committer fix) and the other 10 had it from earlier. **PASS.**

### FR-010 — "All 11 catalog agent files MUST be updated to reflect their reference specs."

Each file's body has a `> Derived from Research/ref/<name>.md` header and the
identity block matches the reference spec. Frontmatter shape is aligned. The
`websearch` discrepancy (system-lead) is a SPEC drift, not a catalog drift.
**PASS in spirit.**

### FR-012 — "Every skill referenced by an agent's body or skill allowlist MUST exist in the catalog."

Same as T-30 sub-criterion #2. **TECHNICALLY FAILING — DEFERRED to T-31.**

## Decision & hand-off

**Verdict: approved-with-notes.**

The HIGH findings from the previous review are fully resolved by `f574496`:
`runtimes: []` is now present in all 11 in-scope catalog files, the diff is
minimal and targeted (11 insertions, 1 per file, no other changes), and the
empty list is the semantically correct value for agents that do not declare
runtime-specific features. The structural frontmatter check (FR-011's 11 fields
+ T-30's 10 fields) passes on all 11 files.

The two MEDIUM findings remain, both as documented deferrals:

- **Planning-lead future subagents** — owner-decided exemption in
  `TASKS.md:19–21`, awaiting F-017.
- **System-lead `websearch: deny` vs FR-007** — SPEC drift; the catalog
  correctly follows the reference spec and T-23's owner decision. The SPEC
  needs updating (T-39 follow-up).

Two new LOW notes are added to the record:

- **4 skills referenced but not in catalog** (mode-decision,
  constitution-checks, packet-validation, builder-selection) — deferred to
  T-31.
- **bootstrap.md is the 12th file with missing `delegates` and `runtimes`** —
  out of T-30 scope, tracked as follow-up. Bootstrap is structurally exempt
  per the previous review.

None of the notes block T-30. The fix is complete, the verification is
reproducible (anyone can re-run the greps), and the path forward is clear:

1. **T-30 is done.** Mark it `[x]` in `TASKS.md:210`.
2. **T-31 unblocks.** Produce the missing-skills inventory, which closes the
   4-skill gap and gets the "every skill exists" criterion to pass naturally.
3. **T-39 unblocks.** Update `SPEC.md` Clarifications with: (a) the
   planning-lead F-017 future-subagent exemption, (b) the system-lead
   `websearch: deny` decision, (c) the bootstrap.md structural exemption.
4. **Open a new follow-up task** for bootstrap.md frontmatter alignment
   (either shape alignment or formal scope exemption).

**Route to:** committer for T-30 task completion (the build-lead has handed
off; T-30 is now review-approved).

The committer isolation claim, the read-only claim, the future-subagents
exemption, and the system-lead websearch decision are all verified by direct
read of the files — re-runnable evidence, not assertion.
