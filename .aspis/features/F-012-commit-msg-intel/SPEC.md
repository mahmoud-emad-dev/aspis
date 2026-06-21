# F-012 — Commit-message intelligence · Specification

> Mode: **production**. The commit-message convention is already the single
> source of truth (`commit-convention.yaml`); this feature makes it *self-healing,
> auditable, configurable, and learnable* — without ever blocking the developer.

## Goal
Make commit-message quality maintain itself: the system **auto-repairs** the
common, unambiguous violations at commit time (foremost, forbidden AI
attribution) without interrupting the commit, **audits and fixes** drift across
existing history on demand, lets each project **configure** which repairs apply
and exempt the rare commit, and can **learn** a project's preferred style and
propose it back into the convention.

## Problem
Today the commit-msg hook only *warns*: `hooks.yaml` ships `enforcement: warn`,
so the hook detected `Co-Authored-By:` attribution on `2026-06-21` (commit
`7be2669`) and **let it through** — polluting history that the convention
promises is "human-authored." The two safe responses are both missing:
- Hard-blocking would stop the developer's flow — explicitly *not* wanted.
- Auto-repair (strip the bad lines, keep going) does not exist.

There is also no way to **audit history** for past violations, no **per-project
auto-fix policy** or **escape hatch**, and style is edit-only — the system cannot
**learn** a user's preferred conventions. The convention is data (good), but it
is passive.

## Scope
In scope:
- `src/aspis/data/catalog/scripts/hooks/commitmsg.py` — non-blocking auto-fix step
  (and its shipped copy under `.aspis/scripts/hooks/`).
- `src/aspis/data/catalog/config/commit-convention.yaml` + `hooks.yaml` — new
  `autofix` policy and a per-commit escape-hatch token (data, not code).
- A history audit surface: extend `aspis doctor` and/or a dedicated
  `aspis commits` verb to scan all commit messages and report/fix violations.
- A sys-lead **skill** (Layer-3 authoring) that detects/learns a project's
  commit style and proposes edits to `commit-convention.yaml`.
- Tests for every behaviour (red→green, R-005).

Out of scope:
- Making `enforcement: block` the default (rejected — must not block flow).
- **Automatically** rewriting already-published history without explicit consent
  (history rewrites stay human-gated, with a backup ref).
- Non-git VCS; commit *content* review (this is message-only).
- The model/tier system (F-010) — unrelated.

## User stories
Prioritized, each independently testable. P1 is the MVP slice.

### Story 1 — Non-blocking auto-fix at commit time (priority: P1)
- **Why this priority**: directly closes the incident that motivated the feature;
  every future commit is protected with zero workflow friction.
- **Independent test**: feed the hook a message containing `Co-Authored-By:` (and
  a credited-model line); assert the written message has those lines removed, the
  hook exits 0, and it reports what it stripped.
- **Acceptance scenarios**:
  1. **Given** a commit message with a forbidden-attribution line, **when** the
     commit-msg hook runs, **then** the offending line(s) are removed, the commit
     proceeds (exit 0), and an `auto-fix: removed …` notice is printed.
  2. **Given** a message with no violations, **when** the hook runs, **then** the
     message is byte-unchanged and the hook is silent.
  3. **Given** a message that mentions `.claude`/`.opencode` as domain vocabulary,
     **when** the hook runs, **then** nothing is stripped (context-aware, not a
     bare-token match — preserves the F-008 behaviour).

### Story 2 — Audit & fix history on demand (priority: P2)
- **Why this priority**: lets a maintainer prove the whole history is clean (the
  question that started this feature) and repair drift deliberately.
- **Independent test**: in a repo with a known-bad historical message, run the
  audit; assert it lists the offending commit(s) and the specific violations.
- **Acceptance scenarios**:
  1. **Given** a repo with past violations, **when** the audit runs, **then** it
     reports each offending commit with its violations and a clean exit summary.
  2. **Given** the maintainer opts into a fix, **when** the fix runs, **then** it
     creates a backup ref first and rewrites only the flagged messages, leaving
     content byte-identical.

### Story 3 — Configurable auto-fix policy + escape hatch (priority: P3)
- **Why this priority**: respects project autonomy and the rare legitimate
  exception, per R-007 (config over code).
- **Independent test**: set a project policy disabling a given auto-fix; assert
  the hook honours it. Add the escape-hatch token to a message; assert it is left
  untouched and the use is recorded.
- **Acceptance scenarios**:
  1. **Given** `autofix.attribution: false` in the project config, **when** the
     hook runs on an attribution message, **then** it warns but does not strip.
  2. **Given** a message carrying the documented skip token, **when** the hook
     runs, **then** the message passes unmodified (rare, logged).

### Story 4 — Learnable / settable style (priority: P4) — DEFERRED to F-013
> **Decision (2026-06-21):** out of scope for F-012; ships as a follow-up once
> Stories 1–3 are proven. Kept here for traceability.
- **Why this priority**: the long-tail "system follows the user's style" goal;
  valuable but depends on Stories 1–3 existing first.
- **Independent test**: given a sample of a project's commits, the skill produces
  a proposed `commit-convention.yaml` diff that a human approves.
- **Acceptance scenarios**:
  1. **Given** a project's commit history and its global/project rules, **when**
     the sys-lead style skill runs, **then** it proposes a convention update
     (types, scope grammar, subject limit, attribution policy) for human approval —
     it never edits the convention unattended (R-009 spirit).

## Requirements
Traceable; `[NEEDS CLARIFICATION]` marks anything unresolved.

- **FR-001**: The commit-msg hook MUST remove unambiguous forbidden attribution
  (the `forbid_attribution` tokens and credited-model patterns) from the message
  and then allow the commit to proceed (exit 0) — auto-fix, not block.
- **FR-002**: The hook MUST report each auto-fix it applied on stderr, naming the
  removed content.
- **FR-003**: The hook MUST NOT alter a message that has no violations (byte-stable)
  and MUST preserve the existing context-aware allowance for `.claude`/`.opencode`
  domain mentions (F-008).
- **FR-004**: Auto-fix MUST be data-driven from the convention/`hooks.yaml`
  (R-007) — adding/removing a rule is editing config, not code.
- **FR-005**: The project MAY disable any individual auto-fix and MAY exempt a
  single commit via a documented escape-hatch token; exemptions MUST be rare and
  recorded.
- **FR-006**: The system MUST provide a history audit that lists every commit
  whose message violates the convention, with the specific violations, and a
  clean/total summary, runnable without modifying anything.
- **FR-007**: A history *fix* MUST be explicit (human-invoked), MUST create a
  backup ref before rewriting, and MUST leave commit *content* byte-identical.
- **FR-008**: A sys-lead skill MUST be able to propose (never silently apply)
  updates to `commit-convention.yaml` learned from the project's history and
  rules, for human approval.
- **FR-009**: All behaviour MUST work identically on Windows and Linux (C-PORTABLE),
  with UTF-8 message I/O.

## Feature rules & style
- **R-007 config-over-code**: every rule stays in `commit-convention.yaml` /
  `hooks.yaml`; the hook adds no inline rules.
- **R-009 spirit**: convention/policy changes and any history rewrite are
  human-gated; the skill proposes, a human approves.
- **F-007 single-writer git**: history fixes go through the committer discipline,
  never `-A`, with a backup ref (the recovery pattern already used this session).
- **C-PORTABLE**: UTF-8 stdio, pathlib, no shell assumptions; Windows = gate of record.
- **Determinism**: the auto-fix and audit are pure functions of (message, convention).

## Key entities
- **Convention** (`commit-convention.yaml`): the SSoT — types, scope grammar,
  subject limit, attribution blocklist; gains an `autofix` policy block.
- **Auto-fix**: a pure transform `(message, convention) -> (cleaned, [repairs])`.
- **Audit report**: per-commit `{hash, subject, [violations]}` + totals.
- **Style proposal**: a proposed convention diff produced by the sys-lead skill.

## Success criteria
- **SC-001**: The `2026-06-21` attribution class of defect cannot reach a commit
  silently again — it is auto-removed with a visible notice, with no extra step
  for the developer.
- **SC-002**: A maintainer can, in one command, get a pass/fail audit of the
  entire commit history against the convention.
- **SC-003**: A project can change auto-fix behaviour and exempt a commit purely
  by editing config — no code change.
- **SC-004**: The gate (ruff + pytest, both OSes) stays green; new behaviour is
  covered by red→green tests.

## Assumptions
- Auto-fix targets only *unambiguous* repairs (attribution lines); subject/scope
  style stays advisory (warn), not auto-rewritten, to avoid changing intent.
- The history *audit* ships first/independently; automated history *fixing* is
  opt-in and may land later within this feature or be deferred.

## Clarifications
### Session 2026-06-21
- Q: Block or auto-fix? → A: **Auto-fix, non-blocking** — never interrupt the
  developer's flow; only a minimal, fast intervention.
- Q: Scope of F-012? → A: **Stories 1–3** (auto-fix, history audit/fix,
  configurable policy + escape hatch). **Story 4 (learnable style) is deferred to
  F-013.**
- Q: Where does the history scan live? → A: **`aspis doctor` reports** (a
  read-only history check); **a new `aspis commits --audit/--fix` verb** does the
  heavier scan and the human-gated rewrite.
- Q: Escape-hatch token? → A: default to a `Commit-Style: skip` trailer; the hook
  passes the message unmodified and prints a one-line "exemption used" notice
  (revisit spelling in PLAN if it collides).

## Open questions
- None blocking. (Story 4 spec carried for F-013; escape-hatch spelling may be
  refined during build.)
