<!-- ASPIS:REVIEW:START -->
# F-017 — Architecture & Constitution Compliance Review

> **Reviewer:** Reviewer (independent quality authority)
> **Lens:** Architecture consistency and constitution compliance
> **Date:** 2026-06-27
> **Method:** Read SPEC.md, PLAN.md, TASKS.md, the handoff (`local/temp/F-017-handoff.md`),
> the 12-point architecture constitution (`rules/architecture-constitution.md`), the system
> rules (R-001–R-010), the constitution-checks index (`config/policy/constitution-checks.yaml`),
> the as-built architecture (`context/ARCHITECTURE.md`), the durable decisions (D-001…D-018),
> the F-016 review (its own `Review/architecture-constitution.md`), the F-016 skills inventory
> (the 25-skill gap list), and the existing 12 catalog agent bodies at
> `src/aspis/data/catalog/agents/*.md` (the F-016 starting state). Cross-artifact consistency
> walked edge-by-edge; each FR-###, SC-###, and owner decision traced to its T-NN; each
> "Decisions needing approval" item traced to the gate that approves it.
>
> **Verdict:** **CHANGES REQUIRED** — the plan is broadly sound and faithfully encodes the
> handoff, but it has three internal self-contradictions in the SPEC/PLAN/TASKS counts, one
> new-directory placement that violates C-DISCOVERY and C-PLUGIN-FIRST, and one load-bearing
> R-008 process gap. None of these is hard to fix; all are pinpointed with file:line.

---

## Summary

| Dimension | Result |
|---|---|
| Architecture constitution (prose — 12 rules) | 12/12 design intent followed; **1 SPEC/PLAN/TASKS count contradiction (M-1); 1 new-directory placement (H-3)** |
| System rules (R-001…R-010) | 9/10 followed; **R-008 human gate has a process gap (M-1)**; R-006 / R-003 / R-004 / R-007 honored |
| Cross-artifact consistency (SPEC ↔ PLAN ↔ TASKS) | **3 self-contradictions (H-1, H-2, M-3)** + the SPEC's own internal webfetch contradiction (H-4) |
| Owner decisions encoded faithfully | 5/5 handoff decisions carried; **3 "Decisions needing approval" items lack an explicit owner-gate task (M-1)** |
| Layered architecture (L0→L1→L2-P0→L2-P1) | Sound; **L2-P0 ordering vs. Claude adapter fix has a subtle risk (M-2)** |
| Dynamic-readiness block in body standard | Correctly captured; convention document + body block + 3 dials + leanest-correct-path default all present |
| Cost-of-change (C-COST) test | Plan claims ≤ 3; **verifies for the case shown, but the bootstrap-promotion edge case is not modeled (M-5)** |
| Plugin-first / Single-source / No-special-case | Two new risks: **`src/aspis/cli/` parallel location (H-3)**; Claude adapter fix wording (M-2) |
| Delegation / permission floor | R-004 + universal-deny-floor + `webfetch`/`websearch` floor match handoff and current code **on the 3rd try** (H-4) |
| FR / SC traceability | 19 FRs and 12 SCs trace to tasks **with gaps** (M-4) |
| **Findings** | **0 CRITICAL, 4 HIGH, 8 MEDIUM, 4 LOW** |
| **Verdict** | **CHANGES REQUIRED** |

---

## CRITICAL findings

> None. The plan's deliverable (the agent system) is sound; the deliverable's *specification*
> has count contradictions that the planning lead must reconcile before any build, but the
> build itself is not at risk of producing a wrong system. The T-32 L1 owner gate and the
> T-40/T-56 systemic gates will catch most runtime drift; the issues below are *pre-build
> specification hygiene* issues, not build-stoppers.

---

## HIGH findings

### H-1 — PLAN §Component 4 says "Six P0 skills" but lists seven (count contradiction)

- **Where:** `PLAN.md:89` (Component 4) — *"Six P0 skills that are prerequisites for the
  core loop, authored to the catalog pattern:"* — followed by a 7-row table at
  `PLAN.md:91–99` (mode-decision, recontextualization, constitution-checks,
  constitution-check, evidence-validation, packet-validation, builder-selection). The Step
  table at `PLAN.md:224` says **"6 files"** for the same step. The TASKS at `TASKS.md:41–47`
  (T-09…T-15) author **7** skills, and the Phase 1 checkpoint at `TASKS.md:49` says
  *"7 shared P0 skills authored to catalog pattern."* The TASKS task summary at
  `TASKS.md:193` agrees: *"Conventions + 7 shared skills authored."*
- **Rule violated:** C-SINGLE-SOURCE (Constitution #3, "Every fact has exactly one owner")
  and the system-rules doctrine that a SPEC is the single source of truth — three artifacts
  (PLAN, TASKS step table, TASKS checkpoint) all assert a different count of the same fact.
  The plan's "Complexity tracking" section (PLAN §287) says "No gate-check violations" —
  this contradiction is exactly the kind of self-inconsistency the gate is supposed to catch.
- **Why it matters:** F-016's prior review (its own `Review/architecture-constitution.md`,
  C-1 and C-3) called out *exactly* this kind of "three sources of truth" defect. A build
  author following the PLAN §Component 4 heading will author 6 skills and stop, missing
  `evidence-validation` (T-13). A build author following the table or TASKS will author 7
  and the T-09…T-15 / T-31 cross-check will pass. The plan must pick one.
- **Severity:** HIGH — the count is a load-bearing fact for SC-009 (25 missing skills
  authored) and SC-001 (0 broken skill refs). A wrong count is a wrong gate target.
- **Recommended fix:** Reconcile the count to **7** (which matches F-016's inventory
  P0-skills list of 13 minus the 6 L1-only P0 skills, giving 7 L0 shared P0 skills). Edit:
  - `PLAN.md:89` — change "Six P0 skills" → "Seven P0 skills".
  - `PLAN.md:224` — change "6 files" → "7 files" and the rest of the row accordingly.
  - Optionally, add a one-line note in the table that the F-016 inventory is the source.
- **Evidence:** `PLAN.md:89` (heading "Six P0 skills"), `PLAN.md:91–99` (7-row table),
  `PLAN.md:224` (Step 5 says 6 files), `TASKS.md:41–47` (7 tasks T-09..T-15),
  `TASKS.md:49` (checkpoint says 7), `TASKS.md:193` (Phase 1 row says 7),
  `F-016/Research/skills/inventory.md:75–93` (13 P0 skills in F-016 inventory),
  `F-016/Review/architecture-constitution.md:35–80` (C-1 / C-3 — same defect class, prior).

### H-2 — PLAN §Component 10 says "P1 skills (7)" but TASKS Phase 4 has 6 (count contradiction)

- **Where:** `PLAN.md:205` — *"**P1 skills (7)**: byte-parity-checker, export-manager,
  finding-format, model-router, runtime-author, scope-compliance, session-continuation —
  each a `catalog/skills/<name>/SKILL.md` file."* The list contains 7 names. The TASKS at
  `TASKS.md:122–128` (Phase 4 P1 Skills) lists **6 tasks** T-41…T-46 (byte-parity-checker,
  export-manager, finding-format, model-router, runtime-author, scope-compliance) —
  `session-continuation` is in **L1** at `TASKS.md:58` (T-16, Phase 2). The Step table at
  `PLAN.md:244` says **"7 files"** for the same step. The TASKS task summary at
  `TASKS.md:196` says *"12 remaining skills + P1 verbs + edge cases"* (which equals 6
  P1 + 5 P2 + 1 carry-over from L1 = 12, not 7+5=12).
- **Rule violated:** C-SINGLE-SOURCE — same defect class as H-1. The Step table says 7
  P1 skills in L2-P1; the TASKS Phase 4 has 6; PLAN §Component 10 lists 7 names but one
  is in L1; the task summary says 12 (which is the right number for the work but
  mis-explains the breakdown).
- **Why it matters:** A build author following PLAN §Component 10 will create a 7th P1
  skill `session-continuation` in Phase 4 and conflict with T-16 in Phase 2. SC-009 ("All
  25 missing skills…have valid SKILL.md") is at risk of being read as "25 unique" or "25
  + duplicates" depending on which artifact is consulted.
- **Severity:** HIGH — direct risk of authoring the same skill twice, or skipping it.
- **Recommended fix:** Reconcile to **6 P1 skills in Phase 4** (the TASKS Phase 4 reality)
  and add a sentence in PLAN §Component 10 clarifying that `session-continuation` is built
  in L1 (T-16) not L2-P1:
  - `PLAN.md:205` — change "**P1 skills (7)**" → "**P1 skills (6 in L2-P1 + 1 in L1)**"
    and split the list, with `session-continuation` annotated "→ built in L1, T-16".
  - `PLAN.md:244` — change "7 files" → "6 files".
  - The total stays 12 (6 P1 + 5 P2 + 1 P1 in L1), but the breakdown is now honest.
- **Evidence:** `PLAN.md:205` (heading "P1 skills (7)"), `PLAN.md:244` (Step 25 says 7
  files), `TASKS.md:58` (T-16 session-continuation in L1), `TASKS.md:122–128` (6 P1
  tasks in Phase 4), `F-016/Research/skills/inventory.md:95–104` (7 P1 skills, with
  session-continuation listed as P1 per F-016's ref-spec priority mapping).

### H-3 — New CLI verb location `src/aspis/cli/` violates the existing `src/aspis/commands/` pattern (C-DISCOVERY, C-PLUGIN-FIRST, C-LOCAL-CHANGE)

- **Where:** `PLAN.md:11` (Storage/interfaces) — *"CLI verbs as new `src/aspis/cli/`
  modules"*; `PLAN.md:13` (Project type/structure) — *"new `src/aspis/cli/`"*;
  `PLAN.md:146` (Component 7) — *"implemented as deterministic Python scripts under
  `src/aspis/cli/`"*. TASKS Phase 3 places all 6 new verbs in `src/aspis/cli/`:
  - `TASKS.md:100` — `src/aspis/cli/validate_runtime.py`
  - `TASKS.md:101` — `src/aspis/cli/byte_parity.py`
  - `TASKS.md:102` — `src/aspis/cli/export.py`
  - `TASKS.md:105` — `src/aspis/cli/governance.py`
  - `TASKS.md:138` — `src/aspis/cli/validate_index.py`
  - `TASKS.md:139` — `src/aspis/cli/drift.py`

  The existing pattern is **`src/aspis/commands/<verb>.py`** registered via
  `src/aspis/commands/__init__.py`'s `COMMAND_MODULES` tuple (see
  `src/aspis/commands/__init__.py:30–46`). The CLI entry point at `src/aspis/cli.py:47–56`
  already loops over `COMMAND_MODULES` and *"never needs to change when a verb is added"* —
  so the discoverable, single-source-of-registration pattern is **`src/aspis/commands/` +
  one tuple entry**, not a new directory.

- **Rule violated:**
  - **C-DISCOVERY** (Constitution #7) — *"Load plugins/kinds by convention; no
    hand-maintained `REGISTRY = [...]`."* Adding a new directory `src/aspis/cli/` means
    the CLI entry point needs a *second* registration mechanism, OR the new directory
    must be picked up by the existing `cli.py` (which currently does not). Either way,
    the registration is no longer single-source.
  - **C-PLUGIN-FIRST** (Constitution #2) — *"Anything that will grow (profiles, agents,
    skills, runtimes, asset kinds, templates) is a plugin; the core never names a
    concrete one."* A new sibling directory to `commands/` is the core naming a concrete
    second location.
  - **C-LOCAL-CHANGE** (Constitution #1) — *"add a feature by creating files, not editing
    many."* The right pattern is one new file in `src/aspis/commands/<verb>.py` plus a
    one-line addition to `COMMAND_MODULES` in `__init__.py` — 2 files, not a new
    directory. The plan is creating a new location, which is the *opposite* of local
    change.

- **Why it matters:** F-016 D-008 (asset kinds are data) and D-015 (runtime identity lives
  on the adapter) both push the codebase toward *one* mechanism per kind of thing.
  Adding a parallel `src/aspis/cli/` location reverses that trajectory for command
  registration. The `__init__.py:1–7` comment is explicit: *"To add a command: create
  the module, then add it to `COMMAND_MODULES` below. The CLI entry point
  (:mod:`aspis.cli`) loops over this tuple, so it never needs to change when a verb is
  added."* The plan is ignoring that contract. There is also a *name collision* risk:
  `src/aspis/cli.py` (the file, the entry point) vs `src/aspis/cli/` (a new directory).
  Python's import system will let this slide, but it is confusing for any agent or
  human reader.

- **Severity:** HIGH — this is a foundational architecture decision that, once encoded in
  the catalog and exported to runtime projects, will be expensive to undo. A future
  `aspis models --apply` will not magically rehome 6 files. Cost-of-change for "now"
  is small; cost-of-change after F-017 ships is large.

- **Recommended fix:** Place all 6 new CLI verb modules in `src/aspis/commands/` and add
  their import + tuple entry to `src/aspis/commands/__init__.py`:
  - `TASKS.md:100` — change `src/aspis/cli/validate_runtime.py` → `src/aspis/commands/validate_runtime.py`
  - `TASKS.md:101` — `src/aspis/commands/byte_parity.py`
  - `TASKS.md:102` — `src/aspis/commands/export.py`
  - `TASKS.md:105` — `src/aspis/commands/governance.py`
  - `TASKS.md:138` — `src/aspis/commands/validate_index.py`
  - `TASKS.md:139` — `src/aspis/commands/drift.py`
  - Add to `src/aspis/commands/__init__.py:30–46`: import each new module and append to
    `COMMAND_MODULES`.
  - Update `PLAN.md:11, 13, 146, 147, 148, 149` to say `src/aspis/commands/` not
    `src/aspis/cli/`.
  - T-33, T-34, T-35, T-36, T-52, T-53, T-54 task descriptions get a 1-line addition:
    "Add to `COMMAND_MODULES` in `src/aspis/commands/__init__.py`."

- **Evidence:** `src/aspis/commands/__init__.py:1–46` (the existing pattern and its
  comment), `src/aspis/cli.py:1–74` (entry point loops over `COMMAND_MODULES` and
  explicitly says it "never changes when a verb is added"), `PLAN.md:11, 13, 146`,
  `TASKS.md:100, 101, 102, 105, 138, 139`. Constitution checks at
  `config/policy/constitution-checks.yaml:47–50` (C-DISCOVERY enforced_by: build, review),
  `:27–30` (C-PLUGIN-FIRST), `:22–25` (C-LOCAL-CHANGE).

### H-4 — SPEC is internally inconsistent on the `webfetch` universal-deny floor (C-SINGLE-SOURCE)

- **Where:** `SPEC.md:50` (Story 2 acceptance scenario 3) — *"every deny floor is honored
  (`git commit*` committer-only, `git push*` none, `webfetch`/`websearch` research-lead-only)
  and no agent has `bash: '*': allow`."* `SPEC.md:77` (FR-004) — *"Every agent's
  permission surface MUST be least-privilege with the universal deny floor (`git commit*`
  committer-only, `git push*` none, `webfetch`/`websearch` research-lead-only, no
  `bash: '*': allow`)."* `SPEC.md:105` (Permissions paragraph) — *"Universal deny floor:
  `git commit*` committer-only, `git push*` none, `webfetch` research-lead + system-lead
  only, `websearch` research-lead-only. No agent has `bash: '*': allow`."*

  Three statements in the same SPEC disagree. The handoff at `local/temp/F-017-handoff.md:178`
  encodes: *"`webfetch` system-lead + research-lead, `websearch` research-lead-only"* — which
  matches the current code at `src/aspis/data/catalog/agents/system-lead.md:31` (webfetch:
  allow) and `src/aspis/data/catalog/agents/research-lead.md:23` (webfetch: allow) and
  the only `websearch: allow` on research-lead. The TASKS at `TASKS.md:75` (T-25
  system-lead: *"webfetch: allow, websearch: deny"*) and `TASKS.md:86` (T-30 research-lead:
  *"webfetch`/`websearch` allow"*) and `TASKS.md:89` (T-31 sweep: *"research-lead-only
  `webfetch`/`websearch`"*) are also internally inconsistent: T-25 and T-30 give the
  handoff's correct floor, T-31 reverts to the wrong "research-lead-only" claim.

- **Rule violated:** **C-SINGLE-SOURCE** (Constitution #3) — *the SPEC is supposed to be
  the truth for acceptance; the handoff is supposed to be the truth for the owner's
  decisions; TASKS is supposed to be the truth for build order.* All three disagree on
  the same load-bearing fact. This is the *exact* defect class F-016's review called out
  as C-2 (the F-016 SPEC's FR-007 websearch contradiction, fixed in T-39). F-017 is
  inheriting and re-introducing the same defect.

- **Why it matters:** SC-007 says *"A write attempt to any protected path
  (`rules/**`, ...)* **is blocked without R-008 approval"** — that part is fine. SC-008
  says *"0 agents have `bash: '*': allow`"* — that part is fine. The webfetch floor is
  not its own SC, but it is a *load-bearing acceptance scenario* (Story 2 / Scenario 3)
  and a *formal requirement* (FR-004). A literal reader of the SPEC will run a validate
  pass that fails the actual current code (system-lead has `webfetch: allow`, which
  SPEC line 50/77 forbids but line 105 allows and the handoff and the current code
  endorse). Either the SPEC lines 50/77 are wrong (and the build must allow system-lead
  `webfetch: allow` — which T-25 already does) OR SPEC line 105 is wrong (and T-25
  becomes non-compliant with the SPEC). The TASKS line 89 reinforces the wrong
  reading.

- **Severity:** HIGH — three documents disagree, two contradict the current code on
  a load-bearing permission, and the TASKS sweep task (T-31) is written against the
  wrong rule. F-016 fixed the same kind of defect in T-39. F-017 must not re-introduce it.

- **Recommended fix:** Pick the handoff's wording as canonical (matches current code and
  T-25/T-30 reality) and update the SPEC and TASKS to match:
  - `SPEC.md:50` — change *"`webfetch`/`websearch` research-lead-only"* → *"`webfetch`
    system-lead + research-lead only, `websearch` research-lead-only"*.
  - `SPEC.md:77` (FR-004) — same edit.
  - `TASKS.md:89` (T-31 sweep) — change *"`research-lead-only` `webfetch`/`websearch`"*
    → *"`webfetch` system-lead + research-lead only, `websearch` research-lead-only"*.
  - The TASKS T-25 (system-lead: `webfetch: allow, websearch: deny`) and T-30
    (research-lead: `webfetch: allow, websearch: allow`) are correct as-is and align
    with the handoff.

- **Evidence:** `SPEC.md:50, 77, 105` (three different wordings),
  `local/temp/F-017-handoff.md:178` (the owner decision), `TASKS.md:75, 86, 89` (T-25,
  T-30, T-31 contradictions), `src/aspis/data/catalog/agents/system-lead.md:31–32`
  (current code: webfetch allow, websearch deny), `src/aspis/data/catalog/agents/research-lead.md:22–23`
  (current code: both allow),
  `F-016/Review/architecture-constitution.md:52–63` (the same defect class on F-016's
  FR-007, fixed in T-39).

---

## MEDIUM findings

### M-1 — "Decisions needing approval" (3 load-bearing architectural choices) have no explicit owner-gate task before they're baked in (R-008)

- **Where:** `PLAN.md:289–292` lists three load-bearing decisions that need owner
  approval: *(1) governance subagent design (protected-paths set, approval ledger path);
  (2) Claude Code adapter fix scope; (3) dynamic-readiness convention.* The TASKS has
  exactly one explicit owner-review checkpoint: **T-32** (L1 EXIT GATE) at `TASKS.md:90`
  ("HARD STOP — owner reviews before L2 begins"). But the decisions are baked into
  work *before* T-32:
  - **Dynamic-readiness convention** — T-08 (`TASKS.md:40`) authors the convention
    document. By T-32, T-09…T-15 (7 shared P0 skills) and T-16…T-30 (15 lead-body
    tasks) will have *referenced* the document. If the owner rejects the document at
    T-32, all 22+ downstream tasks need rework.
  - **Governance subagent design** — T-36 (`TASKS.md:105`) is in L2-P0 *after* T-32.
    The protected-paths set is encoded in T-36, so this is OK — T-32 is the right gate.
  - **Claude Code adapter fix** — T-35 (`TASKS.md:102`) is in L2-P0 *after* T-32. OK.

  The dynamic-readiness convention is the one baked-in-before-the-gate. The plan's
  "Decisions needing approval" entry for it says *"Owner approves the convention
  document at L0 before L1 agents bake it in."* — but no task enforces that. T-08
  authors; T-09 starts authoring skills that may reference it; T-16 starts authoring
  agents that *definitely* reference it. There is no owner checkpoint between T-08
  and T-09.

- **Rule violated:** **R-008 (Human gate)** — *"Architecture, rules, permissions,
  security posture, and model-routing changes require human approval."* The
  dynamic-readiness convention changes how every agent behaves; that is an
  architecture-level decision. R-008 is named in the SPEC (`SPEC.md:101`) and in
  the handoff (`handoff.md:173`), and the plan claims a gate check at `PLAN.md:22` —
  but the actual sequencing of TASKS does not realize it for the dynamic-readiness
  decision.

- **Why it matters:** R-008 is the load-bearing safety rule. If the convention is
  approved at T-32 *after* 22 tasks have cited it, the "approval" is a retroactive
  rubber-stamp, not a gate. That is the exact failure mode R-008 is designed to
  prevent. The other two "Decisions needing approval" (governance, Claude adapter)
  are correctly sequenced to T-32; only the dynamic-readiness one is early.

- **Severity:** MEDIUM — the convention is small enough that a "best interpretation
  then validate at T-32" pattern works in practice, but the plan as written does not
  match the rule it claims to satisfy. The plan's own §"Decisions needing approval"
  narrative is *clearer* about the rule than the TASKS is about its enforcement.

- **Recommended fix:** Add a checkpoint between T-08 and T-09. Options:
  - (a) Add a T-08a *"Owner approves dynamic-readiness convention document"* task
    with acceptance *"plan-lead or project-lead confirms the owner has signed off
    on `.aspis/context/DYNAMIC_READINESS.md`; record the approval in
    `.aspis/state/approval-ledger.yaml` via `aspis governance request/approve`."*
    Hard-blocks T-09…T-15. The approval-ledger is a T-36 concern, so for T-08a use
    a free-text acknowledgment in RECENT_CHANGES.md or a temporary hand-written
    note.
  - (b) Move the dynamic-readiness section of T-08 to after T-32 (i.e. to L2-P0 or
    L2-P1) and have the L0 skills and L1 bodies bake the convention in *only after*
    owner approval. Larger rework.
  - (a) is the cheaper fix; the plan should pick (a).

- **Evidence:** `PLAN.md:289–292` (the three "Decisions needing approval"),
  `TASKS.md:40` (T-08 authors the document), `TASKS.md:41–47` (T-09..T-15 start
  authoring immediately after), `TASKS.md:58–86` (T-16..T-30 author lead bodies
  that bake in the convention), `TASKS.md:90` (T-32 — the only owner gate),
  `local/temp/F-017-handoff.md:50` (the decision is to bake it in), `system-rules.md:101–103`
  (R-008 text), `SPEC.md:101` (R-008 named in feature rules).

### M-2 — Claude Code adapter fix wording is capability-flavored but the location is not pinned to the adapter (C-NO-SPECIAL-CASE risk)

- **Where:** `PLAN.md:161` (Component 7) — *"The `export` verb (and `byte-parity`)
  must handle the Claude Code adapter's `permission:` block stripping bug. Fix: render
  the `permission:` block into the Claude agent file — either as Claude's native
  format or as a structured YAML comment block that preserves deny/allow semantics.
  The fix lives in the adapter code (if it exists) or in the export verb's Claude
  render path."* The conditional *"if it exists"* is the risk: if the fix lives in
  `byte_parity.py` / `export.py` (the new commands under `src/aspis/commands/` after
  H-3 is applied), the code may be a `if adapter_name == "claude":` check.

- **Rule violated:** **C-NO-SPECIAL-CASE** (Constitution #9) — *"never `if runtime ==
  "x"` / `if profile == "y"`. Use abstractions and **capability checks**
  (`runtime.supports(kind)`)."* D-008 (asset kinds are data) and D-015 (runtime
  identity lives on the adapter) both push this: the Claude Code adapter is the
  single source of "what Claude can render" and "where its file lives." A
  permission-block fix belongs on the adapter as a `render_permission_block(perm)`
  method (or equivalent), and the export verb calls it generically. The plan
  *describes* the right pattern but does not *enforce* it.

- **Why it matters:** F-016's review (H-2 in `F-016/Review/architecture-constitution.md`)
  flagged the same concern: *"the asymmetry between runtimes is exactly the kind of
  special case the constitution prohibits."* The fix is a T-35 deliverable; if it is
  implemented as a special-case in the export verb, it will be exported to every
  runtime project (D-007) and become a permanent part of the system.

- **Severity:** MEDIUM — the *risk* of a special case is high; the *probability* is
  low (the build author will likely follow the adapter pattern from D-015). The
  plan should make the right location a hard requirement, not a conditional.

- **Recommended fix:** Pin the fix to the adapter layer:
  - `PLAN.md:161` — replace *"The fix lives in the adapter code (if it exists) or
    in the export verb's Claude render path."* with *"The fix lives on the Claude
    Code adapter as a `render_permission_block(permissions: dict) -> str` method
    (or equivalent) and is called generically by the export verb. No special
    casing in the verb itself; the adapter is the single source of Claude's
    permission-block rendering."*
  - T-35 acceptance — add: *"verify the new code has no `if adapter == "claude"`
    or `if runtime == "claude"` literal; verify the call site uses
    `runtime_adapter.render_permission_block(...)`."*

- **Evidence:** `PLAN.md:161` (the fix wording), `context/ARCHITECTURE.md:25–48`
  (D-008 + D-015 adapter contract), `config/policy/constitution-checks.yaml:42–45`
  (C-NO-SPECIAL-CASE enforced_by: build, review), `F-016/Review/architecture-constitution.md:96–99`
  (H-2 — the same concern, prior).

### M-3 — SPEC's own numbered rule list and the constitution's rule list disagree on count (C-SINGLE-SOURCE at the rule-document level)

- **Where:** `TASKS.md:43` (T-11 description) — *"audit a PLAN against the **12
  architecture-constitution rules**"*; `TASKS.md:44` (T-12 description) — *"apply the
  **9 reviewer-owned** architecture-constitution checks"*; `SPEC.md:74, 75, 76, ...`
  (FR-### text) does not pin a number, but `SPEC.md:101` says *"the architecture
  constitution"* without a number. The 12-point constitution has the count split
  described in F-016's own review (C-1 in `F-016/Review/architecture-constitution.md`):
  prose declares 12 extension rules, the YAML index at
  `config/policy/constitution-checks.yaml:11–65` has 11 (with 2 not in the prose),
  and the F-016 reviewer's verification list was a 12-rule set picked from a
  different combination of sources. So when F-017 says *"12 architecture-constitution
  rules"* (T-11) it is naming a count that does not exist as a single source.
- **Rule violated:** **C-SINGLE-SOURCE** — *the same defect class as F-016's
  review C-1/C-3 (constitution prose ↔ YAML drift).* F-017's plan inherits the
  drift and bakes it into TASKS.
- **Why it matters:** SC-001 (0 broken skill refs) and SC-006 (every agent passes
  the body standard check) are evaluated by a future reviewer; the
  constitution-check skill (T-12) will count rules; T-11 (constitution-checks
  skill) will emit a `CONSTITUTION_CHECK.md` report. If they count different
  rules, the gate is unverifiable.
- **Severity:** MEDIUM — the drift is a known F-016 follow-up; F-017 should
  inherit the cleanest count and add a follow-up to reconcile the three sources.
- **Recommended fix:** Either:
  - (a) Update T-11 and T-12 to use the F-016 reviewer's 12-rule list as the
    canonical set (per F-016 review C-3, recommended fix #1) and add a T-08b /
    T-09 / T-11 sub-task that pins the canonical list, OR
  - (b) Cite the constitution-checks YAML as the source of truth and update
    T-11/T-12 to use the YAML count (currently 11).
  - The plan should at least add a note that the constitution-check skill will
    read the YAML index (per `constitution-checks.yaml:1–7` preamble: *"the
    planning, build, and review agents load the rules they own"*), not a hand-
    counted number.

- **Evidence:** `TASKS.md:43, 44` (T-11 / T-12 use "12" and "9" without source
  citation), `rules/architecture-constitution.md:51–76` (prose 12),
  `config/policy/constitution-checks.yaml:11–65` (YAML 11),
  `F-016/Review/architecture-constitution.md:35–80` (C-1, C-3 — the prior finding).

### M-4 — Some FRs and SCs are not directly traceable to a single T-NN (FR/SC traceability)

- **Where:**
  - `SPEC.md:81` (FR-008) — *"The governance subagent MUST block writes to
    protected paths without R-008 approval and maintain an append-only approval
    ledger."* — T-36 (`TASKS.md:105`) covers the script, but the *append-only*
    property is not a separate acceptance bullet. A future T-36 builder could
    write a non-append-only ledger and pass T-36's acceptance.
  - `SPEC.md:89` (FR-016) — *"Every agent body MUST cite system rules by ID only
    (R-001, R-004, etc.), not restate them."* — T-17 through T-30 (lead bodies)
    and T-37 through T-39 (leaf bodies) all *verify against standard*, but
    no task explicitly enforces the "no restate" rule. The agent-body standard
    (T-07) is the carrier; T-07's checklist must include the no-restate rule
    and T-17…T-39 must verify it. The plan says T-07 will include the rule
    (`PLAN.md:57` cites by ID only) but does not require T-17…T-39 to *check*
    against it explicitly.
  - `SPEC.md:93` (FR-018) — *"No asset content (skill procedure, rule text,
    workflow step) MUST be duplicated across agent bodies. Agents reference
    by name/path only (R-006)."* — T-31 (cross-agent consistency sweep) is the
    closest task, but its acceptance is on delegates and skill refs, not on
    "no body inlines skill procedure text." A body that pastes a 5-line excerpt
    from a skill into its "How you work" would pass T-31.
  - `SPEC.md:120` (SC-011) — *"The cost-of-change test passes: adding a
    hypothetical new agent requires changes to ≤ 3 files."* — T-56 (final
    sweep) is the only carrier. SC-011 should be evaluated by an explicit
    "add a hypothetical new agent and count the files" task, or at least a
    documented scenario in the build report. As written, SC-011 is a
    documentation check, not a test.
  - `SPEC.md:122` (SC-012) — *"Every lead agent's dynamic-readiness block
    references the 3 dials (mode, task kind/scope, model capability) and
    encodes the 'leanest correct path' default."* — covered by T-08 + T-17…T-30
    collectively, but no single task *checks* the dial names appear.

- **Rule violated:** plan-critic procedure step 1 (*"Every `FR-###` and user story
  maps to at least one task. Flag requirements with no task (under-built) and
  tasks that serve no requirement (scope creep)."*) and step 2 (*"Every success
  criterion is observable and has a task or test that proves it."*).
- **Severity:** MEDIUM — not a stop-the-build, but the spec-to-task traceability
  is weaker than F-016's (per `F-016/Review/architecture-constitution.md` which
  verified every FR/SC against a T-NN).
- **Recommended fix:** Either (a) add acceptance bullets to existing T-NNs that
  pin the FR/SC, or (b) add a new T-NN to T-31 / T-56 that explicitly checks
  the "no restate," "no duplicate," and "3-file cost-of-change" properties.
  Option (a) is cheaper. The TASKS template format already supports additional
  acceptance text.

- **Evidence:** `SPEC.md:81, 89, 93, 120, 122` (the FRs / SCs),
  `TASKS.md:105, 89, 152, 17–30, 37–39` (the tasks).

### M-5 — Cost-of-change claim (≤ 3 files) does not model the bootstrap-promotion edge case

- **Where:** `PLAN.md:49` — *"Adding a hypothetical new agent after F-017 = 1 new
  catalog file + 1 entry in the lead's delegates + (optional) 1 new skill = ≤ 3
  files."* The claim is correct for a *new leaf* (e.g., a new `general-builder-2`):
  1 catalog + 1 parent's delegates = 2. It is correct for a *new P1 skill*: 1
  catalog + 1 owning agent's frontmatter = 2. It is *not* modeled for a *new
  lead* (e.g., adding a new primary lead between planning and build):
  - 1 new catalog file
  - 1 entry in `project-lead`'s `delegates:` (project-lead delegates to all
    leads per `src/aspis/data/catalog/agents/project-lead.md:33–41`)
  - 1 entry in `bootstrap.md` if the new lead is promoted to primary per D-004
    ("bootstrap promotes system, planning, build, and reviewer")
  - 1 entry in `modes.yaml` or other config files
  - 1 entry in any lead that needs the new lead as a delegate
  - = 4–5 files
- **Rule violated:** **C-COST** (Constitution's north-star rule). 4–5 files is
  "warning" territory (5–10), not "healthy" (1–3).
- **Why it matters:** SC-011 is the SC. If a future new lead crosses 3 files
  and the SPEC says it must be ≤ 3, the gate fails. The plan's claim is
  inaccurate for that case.
- **Severity:** MEDIUM — the plan's example is the easy case (a new leaf); the
  hard case (a new lead) is not modeled. The plan should either (a) narrow the
  claim to "new leaf agent or skill," or (b) add a follow-up that hardens
  bootstrap's promotion set as data (per D-004's intent) so a new lead is
  data-driven, not a hand edit.
- **Recommended fix:**
  - `PLAN.md:49` — change *"Adding a hypothetical new agent after F-017 = 1 new
    catalog file + 1 entry in the lead's delegates + (optional) 1 new skill =
    ≤ 3 files."* → *"Adding a new leaf agent or a new skill after F-017 ≤ 3
    files. Adding a new primary lead is out of F-017's scope (D-004 makes that
    a bootstrap/modes change); a follow-up to data-drive bootstrap's promotion
    set is the next step."*
  - T-25 (system-lead finalize) or T-22 (catalog-validator) — add a sub-bullet:
    *"Verify that `bootstrap.md` and `modes.yaml` are data-driven, not hand-
    edited, so a new lead does not cross 3 files (C-COST)."*

- **Evidence:** `PLAN.md:49` (the claim), `src/aspis/data/catalog/agents/project-lead.md:33–41`
  (project-lead's 8 delegates), `context/DECISIONS.md:23–25` (D-004 — bootstrap
  promotion), `src/aspis/data/catalog/agents/bootstrap.md` (the promotion set),
  `config/policy/constitution-checks.yaml:12–15` (C-COST).

### M-6 — `aspis preflight` / `prereq_validate.py` is in two permission allowlists with subtly different scopes (D-002 risk)

- **Where:** `src/aspis/data/catalog/agents/build-lead.md:21, 23` allows
  `aspis preflight*` and `aspis context*`; `src/aspis/data/catalog/agents/fix-lead.md:19`
  allows `aspis preflight*` only; `src/aspis/data/catalog/agents/system-lead.md:19`
  allows `aspis *` (broad). The PLAN and TASKS do not call out the broad `aspis *`
  allow on system-lead as a risk — system-lead is the only lead with an
  unrestricted `aspis *` pattern.
- **Rule violated:** **R-001** (least-privilege), and arguably **FR-004** (*"no
  agent has `bash: '*': allow"`* — system-lead does not have `bash: '*': allow`
  but does have `aspis *` allow, which is a similar blast radius). Constitution
  #1 (Local Change) is *not* violated, but the spirit of least-privilege is
  blurred.
- **Why it matters:** The plan's T-25 (system-lead finalize) says *"named bash
  allowlist NOT `*`"* — that is `bash:`, not the `aspis *` pattern. The plan
  is silent on the `aspis *` pattern. D-002 (one catalog, per-runtime adapters)
  pushes `aspis *` as the right pattern for system-lead (it owns the runtime
  and must call all `aspis` verbs), but the plan's R-001 / FR-004 verification
  in T-31 only checks `bash: '*': allow`, not the `aspis *` pattern. T-31 will
  pass on system-lead even if the `aspis *` pattern is too broad for some
  future design.
- **Severity:** MEDIUM — current design is sound; the plan's sweep is too
  narrow to detect future drift.
- **Recommended fix:** Extend T-31 to also check the `aspis *` pattern and
  document the system-lead exception explicitly: *"system-lead's `aspis *` is
  by design (D-002; system-lead owns the runtime and must call all `aspis`
  verbs); every other lead's bash allowlist must enumerate `aspis` verbs
  explicitly."*
- **Evidence:** `src/aspis/data/catalog/agents/system-lead.md:19` (`aspis *`),
  `src/aspis/data/catalog/agents/build-lead.md:21, 23` (named verbs only),
  `src/aspis/data/catalog/agents/fix-lead.md:19` (named verb only),
  `TASKS.md:89` (T-31 — sweeps `bash: '*': allow` only, not `aspis *`),
  `context/DECISIONS.md:11–14` (D-002 — one catalog).

### M-7 — Workflow verification (T-02..T-06) and skill authoring (T-09..T-15) are listed as `[P]` but T-01 (deploy scripts) is the unblocker; the dependency is implicit (M-7)

- **Where:** `TASKS.md:25` (T-01) is the only task not marked `[P]` in Phase 0.
  T-02..T-06 are `[P]` and can run in parallel. T-07 (agent-body standard) in
  Phase 1 is also not marked `[P]` but T-08 (dynamic-readiness) is not `[P]`
  either (T-08 is the convention that T-09..T-15 reference). T-09..T-15 are
  marked `[P]`. The dependency is implicit: T-09..T-15 reference the dynamic-
  readiness convention from T-08, and T-08 establishes it. The TASKS format
  is correct, but the implementation strategy at `TASKS.md:160–166` says
  *"L0-first"* and *"L1 parallel"* without making the **strict ordering of
  T-07 → T-08 → T-09..T-15** explicit.
- **Rule violated:** plan-critic procedure step 4 (*"Phases respect
  dependencies"*) — soft violation; the dependencies are encoded in the
  phase boundaries, but a fast build author may not see them.
- **Severity:** MEDIUM — the work is correct; the *description* is mildly
  under-specified.
- **Recommended fix:** Add a one-line "Implementation strategy" addition at
  `TASKS.md:160` clarifying: *"T-07 and T-08 are sequential (the standard
  is the contract; the convention is the substrate); T-09..T-15 depend on
  T-08 (skills may reference the convention)."*
- **Evidence:** `TASKS.md:25, 39, 40, 41–47, 160–166`,
  `PLAN.md:216–248` (Step table).

### M-8 — Plan does not pin how it verifies the F-016 baseline is R-006-compliant before F-017 builds on it (M-8)

- **Where:** `SPEC.md:136` (Assumptions) — *"The 11 thin catalog agent bodies
  from F-016 are the starting point for finalization, not a rewrite."* The
  F-016 commit log shows `457d0c4 refactor(F-016): thin lead agent bodies to
  single-source per R-006` (2026-06-27, after the F-016 merge), so the
  baseline is *known* to be R-006-clean. But the plan does not name this
  verification step.
- **Rule violated:** R-006 thin-agent rule (verification gap, not violation).
- **Severity:** MEDIUM — the work is fine; the audit trail is missing.
- **Recommended fix:** Add a T-07 sub-bullet: *"T-07 acceptance includes
  verifying the F-016 baseline (11 thin bodies) is R-006-clean by reading
  the F-016 commit `457d0c4` and confirming the bodies' R-006 status. If
  the bodies are NOT R-006-clean, T-07 must note the gaps and T-17..T-30
  must close them."*
- **Evidence:** `SPEC.md:136` (assumption),
  `git log --oneline | grep 457d0c4` (the F-016 R-006 commit),
  `F-016/BUILD_REPORT.md` (F-016 build report should confirm).

---

## LOW findings

### L-1 — FR-003 / SPEC says "3 planning scripts" but the source directory has 5 files (helpers included)

- **Where:** `SPEC.md:76` (FR-003) — *"The 3 planning scripts MUST be deployed
  from `src/aspis/data/catalog/scripts/planning/` to `.aspis/scripts/planning/`"*;
  `PLAN.md:75` (Component 3) — *"Source: `src/aspis/data/catalog/scripts/planning/`
  (4 files: `_console.py`, `feature_scaffold.py`, `task_compile.py`,
  `prereq_validate.py`, `active_feature.py`)"* — the parenthetical says "4 files"
  but lists 5 names. The actual directory has 5 `.py` files plus `__pycache__/`:
  `_console.py` (helper), `active_feature.py` (helper), `feature_scaffold.py`
  (P1 user-facing), `task_compile.py` (P6 user-facing), `prereq_validate.py`
  (P8 user-facing).
- **Why it matters:** The "3" in FR-003 is the count of user-facing scripts
  (the deployment target of the F-016 spec); the "5" is the file count to
  deploy. PLAN §Component 3 should be explicit that all 5 files deploy
  (helpers included) and the count discrepancy is resolved.
- **Recommended fix:** `PLAN.md:75` — change *"4 files"* → *"5 files (3 user-
  facing + 2 helpers)"* and add: *"`_console.py` and `active_feature.py` are
  helpers imported by the user-facing scripts; they ship together."*
- **Severity:** LOW — T-01 (`TASKS.md:25`) already deploys all 5 files; the
  prose count is the only thing wrong.
- **Evidence:** `SPEC.md:76` (FR-003), `PLAN.md:75` (Component 3),
  `TASKS.md:25` (T-01 deploys 5 files), `src/aspis/data/catalog/scripts/planning/`
  (actual directory).

### L-2 — L0 cost-of-change claim (1 new catalog + 1 delegates + 1 skill = 3) overstates for shared skills

- **Where:** `PLAN.md:49` (also). For a skill referenced by 2 agents (e.g.,
  `mode-decision` is owned by planning-lead *and* project-lead, per F-016
  inventory), the cost-of-change is 1 new catalog + 2 frontmatter entries =
  3 files. For a skill referenced by 3+ agents (none planned in F-017, but
  possible in the future), it crosses 3.
- **Recommended fix:** Pin the claim to "shared by ≤ 2 agents" or note that
  a follow-up (skill-allowlist-from-data) is the path to keeping shared-skill
  cost at 2.
- **Severity:** LOW — the plan's example is a single-owner skill; the
  shared case is uncommon but real (the inventory already has `mode-decision`).
- **Evidence:** `PLAN.md:49`, `F-016/Research/skills/inventory.md:75–93`
  (`mode-decision` is P0, owned by planning-lead + project-lead).

### L-3 — T-08 dynamic-readiness convention author and owner sign-off (M-1 expansion) is not in the implementation strategy

- **Where:** `TASKS.md:160–166` (Implementation strategy) — five bullets: L0-first,
  L1 parallel, HARD GATE after L1, L2-P0 before L2-P1, P1/P2 skills parallel.
  No bullet for the "T-08 owner sign-off before T-09" sequencing (see M-1).
- **Recommended fix:** Add a bullet: *"T-08 must be owner-approved (recorded in
  RECENT_CHANGES or the approval ledger) before T-09..T-15 (shared P0 skills)
  start; the dynamic-readiness convention is referenced by every later skill
  and every lead body."*
- **Severity:** LOW — M-1 is the architectural finding; L-3 is the documentation
  cleanup.
- **Evidence:** `TASKS.md:160–166`, M-1 above.

### L-4 — T-56 final acceptance sweep is the only carrier of SC-001 through SC-012 (L-4)

- **Where:** `TASKS.md:152` (T-56) is a single task that "Verif[ies] SC-001
  through SC-012 from SPEC." 12 success criteria in one task is a wide
  net; if a future builder skips a SC the gate is silent.
- **Recommended fix:** Either expand T-56 to a sub-checklist (preferred —
  one sub-bullet per SC), or add T-56a…T-56l for the 12 SCs. Expanding T-56
  is cheaper.
- **Severity:** LOW — T-56 is the right place; it just needs a checklist.
- **Evidence:** `TASKS.md:152`, `SPEC.md:118–122` (the 12 SCs).

---

## Owner-decision compliance (the 5 locked decisions + 3 clarifications)

| # | Owner decision (handoff) | Plan location | Compliant? |
|---|---|---|---|
| 1 | "Build shape = layered by depth, agent-by-agent within each layer" | `PLAN.md:26–47` (Layered design L0→L3); `TASKS.md:13–18` (Phase 0→5) | ✅ Yes — 4 explicit layers, dependency direction encoded, L0 first. |
| 2 | "Use subagents to re-read the F-016 artifacts cheaply" | Implicit — `PLAN.md:10` lists F-016 artifacts as key dependencies; `TASKS.md:25` deploys `project-explorer` and `research-lead` per `TASKS.md:69, 86` (existing) | ✅ Yes — `project-explorer` is in every lead's delegates; `research-lead` is in planning-lead's, build-lead's, and reviewer's. |
| 3 | "Dynamic smarts = design-now, wire-to-existing" | `PLAN.md:62–71` (Component 2 — Dynamic-readiness convention); `TASKS.md:40` (T-08); `SPEC.md:79` (FR-006); `SPEC.md:122` (SC-012) | ✅ Yes — three dials (mode, task kind/scope, model capability) are named; leanest-correct-path default is named; "future router engine can drive these dials" is in `PLAN.md:69`. |
| 4 | "Default behavior to encode everywhere — the leanest *correct* path, not less quality" | `SPEC.md:79` (FR-006 — "leanest correct path" default); `PLAN.md:67` (Component 2 — "the leanest-correct-path default"); `TASKS.md:40` (T-08) | ✅ Yes — the default is named in three places. The T-08 owner sign-off (M-1) is the only weak spot. |
| 5 | "R-006 / single source is non-negotiable" | `SPEC.md:75, 93, 97, 100` (FR-002, FR-018, "thin agents, single source" rule, R-006 cited); `PLAN.md:55–57` (Component 1 — "thin-agent rule, cite-don't-restate rule"); `TASKS.md:39` (T-07 — agent-body standard) | ✅ Yes — six separate citations; T-07 is the carrier of the standard, T-17..T-30 verify against it. M-3 + M-4 are the weak spots (constitution rule count, FR-016 enforcement). |
| 6 | "L2 vs L3 boundary" (clarification Q1 → A) | `SPEC.md:146` (Clarifications Q1 → A: L2 P0 = 3 P0 CLI verbs + governance; L2 P1 = 3 P1 CLI verbs + remaining P1 skills; L3 deferred to F-018) | ✅ Yes — encoded faithfully. |
| 7 | "First milestone = L1 exit gate" (clarification Q2 → A) | `TASKS.md:90` (T-32 — "HARD STOP — owner reviews before L2 begins. Do NOT roll into T-33."); `PLAN.md:142` (Component 6 — L1 exit gate); `SPEC.md:153` (Open questions — "None remaining") | ✅ Yes — T-32 is the hard gate. M-1 (dynamic-readiness sign-off timing) is the only weak spot. |
| 8 | "Live runtime regeneration deferred" (clarification Q3 → A) | `SPEC.md:29` (Out of scope — "Live runtime auto-regeneration… owner runs `aspis export` manually after F-017 lands"); `PLAN.md:19` (R-001 — "No edits to `.opencode/` or `.claude/` (owner runs export manually)") | ✅ Yes — explicitly out of scope. |

**Owner-decision compliance: 8/8 decisions faithfully encoded, with 2 weak spots
(M-1 dynamic-readiness sign-off timing; M-3 + M-4 the constitution rule count and
R-006 enforcement).**

---

## Architecture constitution gate-check (the 12 rules)

| # | Rule | Plan status | Notes |
|---|---|---|---|
| 1 | Local Change | ✅ followed | New catalog files, edits to existing thin bodies. **H-3 is a violation** (new `src/aspis/cli/` directory instead of editing `src/aspis/commands/__init__.py`'s `COMMAND_MODULES` tuple). |
| 2 | Plugin First | ⚠️ risk | The new CLI directory is the risk; see H-3. Everything else is plugin-shaped (skills, templates, workflows, agents, verbs are all "kinds"). |
| 3 | Single Source of Truth | ⚠️ 3 contradictions | **H-1** (6 vs 7 P0 skills), **H-2** (7 vs 6 P1 skills), **H-4** (webfetch floor in 3 wordings). Plus **M-3** (constitution rule count is 11 / 12 / 12-of-a-different-set, per F-016 review C-1/C-3). The plan inherits F-016's C-SINGLE-SOURCE issues and adds new ones. |
| 4 | Configuration over Code | ✅ followed | `modes.yaml`, `models.yaml`, `constitution-checks.yaml` are data; the plan does not add `if mode == "x"` chains. |
| 5 | Core is Stable | ✅ followed | No core Python edits planned except a possible Claude adapter fix (`PLAN.md:14, 161`), which is the only planned edit. T-35 should confirm "fix in the adapter, not in core" (see M-2). |
| 6 | Dependency Direction | ✅ followed | Plugins → core, never the reverse. The new CLI directory (H-3) would not violate this directly, but it does establish a sibling that future core code might depend on. |
| 7 | Discovery over Registration | ⚠️ H-3 | The new directory requires a new registration mechanism. The existing `COMMAND_MODULES` is *already* a hand-maintained tuple (per `__init__.py:30–46`), so discovery is already imperfect — but adding a parallel location makes it worse. |
| 8 | Generated Artifacts | ✅ followed | No hand-maintained generated output. `RECENT_CHANGES.md` is updated by T-56 but is a brain artifact, not a generated index. |
| 9 | No Special Cases | ⚠️ M-2 | The Claude adapter fix wording is capability-flavored but not pinned to the adapter. F-016's review H-2 flagged the same concern. |
| 10 | Consistency over Cleverness | ✅ followed | The plan is boring and predictable. No clever pattern; just standard shapes. |
| 11 | Architecture before Features | ✅ followed | The agent-body standard (T-07) and dynamic-readiness convention (T-08) are the contract; the agents (T-17..T-30) build to them. L0 is foundational. |
| 12 | Portable by Default | ✅ followed | Stdlib-only scripts (`TASKS.md:159` — "all CLI verbs are stdlib-only, no third-party imports"); UTF-8 stdio is a pre-existing convention enforced by `src/aspis/cli.py:27–39`. No OS-specific code introduced. |

**Constitution gate-check: 9/12 clean, 3 with findings (1 H-3, 1 H-4, 1 M-2; M-3 and
M-4 are sub-findings of H-1/H-2). The C-SINGLE-SOURCE drift from F-016 is the
dominant theme.**

---

## System-rules gate-check (R-001..R-010)

| Rule | Plan status | Notes |
|---|---|---|
| R-001 Scope | ✅ followed | R-001 verification at `PLAN.md:19`; `TASKS.md` only touches the named paths. |
| R-002 Gates first | ✅ followed | Every layer has a gate (T-01 scripts, T-06 workflows, T-15 skills, T-31 cross-agent, T-32 L1 end-to-end, T-40 L2-P0, T-56 final). |
| R-003 Deterministic-first | ✅ followed | Scripts before agents; the 6 CLI verbs and the governance script are deterministic Python. SC-002 says no deep models required. |
| R-004 One writer | ✅ followed | committer-only `git commit*` enforced in T-37; T-31 sweep checks. |
| R-005 Tests-as-spec | ✅ followed | Skills have Anti-patterns + Outputs (T-07 standard); CLI verbs have `--help` + dry-run; end-to-end loop is the integration test. |
| R-006 Thin agents, single source | ⚠️ **M-3 + M-4** | T-17..T-30 verify against standard (T-07) but the "no restate, no duplicate" check is not explicit. M-4 pinpoints the FR-016 / FR-018 enforcement gap. |
| R-007 Pinned models | ✅ followed | All 12 agents have a `model:` tier in their existing frontmatter. T-17..T-30 verify. |
| R-008 Human gate | ⚠️ **M-1** | T-32 is the only explicit owner gate. The 3 "Decisions needing approval" are sequenced correctly for governance (T-36) and Claude adapter (T-35), but the dynamic-readiness convention (T-08) is baked in before T-32. The plan's narrative is clearer about R-008 than the TASKS. |
| R-009 Trace and learn | ✅ followed | T-56 updates `RECENT_CHANGES.md`; review reports go to `Review/`; commit convention is in place (D-011). |
| R-010 Delegate with purpose | ✅ followed | Subagent work (project-explorer, research-lead) is encoded in every lead's `delegates:`; leaf agents have `delegates: []`. |

**System-rules gate-check: 8/10 clean, 2 with findings (M-1 R-008, M-3/M-4 R-006).**

---

## Verdict

**CHANGES REQUIRED.**

The plan is sound and faithfully encodes the handoff, the as-built architecture, and the
owner's locked decisions. The layered L0→L3 design, the dynamic-readiness convention, the
single-source posture, the deterministic-first verb set, and the F-016 baseline are all
correctly captured. But the plan has three count contradictions in the SPEC/PLAN/TASKS
itself (H-1, H-2, H-4) that *must* be reconciled before any build, one foundational
architecture decision (H-3: the new `src/aspis/cli/` directory) that violates
C-DISCOVERY / C-PLUGIN-FIRST / C-LOCAL-CHANGE and should be redirected to the existing
`src/aspis/commands/` pattern, one R-008 process gap (M-1: the dynamic-readiness
convention is baked in before the only owner gate), and a handful of MEDIUM / LOW
findings that are tractable in a single planning pass.

### Required changes (must fix before build)

1. **H-1** — Reconcile the L0 P0 skill count to **7** in PLAN.md (heading, step table)
   and TASKS.md. The TASKS already says 7; the PLAN is the outlier.
2. **H-2** — Reconcile the L2-P1 P1 skill count to **6** in PLAN.md (with
   `session-continuation` annotated "→ built in L1, T-16") and TASKS.md. The TASKS
   Phase 4 already has 6; the PLAN is the outlier.
3. **H-3** — Move all 6 new CLI verb modules from `src/aspis/cli/` to
   `src/aspis/commands/` and add to `COMMAND_MODULES` in `__init__.py`. This is a
   foundational fix; the cost-of-change *now* is small (8 file paths + 1 import + 1
   tuple entry); the cost-of-change *after* F-017 ships is large.
4. **H-4** — Reconcile the SPEC's webfetch floor to the handoff's wording
   ("`webfetch` system-lead + research-lead only, `websearch` research-lead-only") in
   SPEC.md lines 50, 77, 105 and TASKS.md line 89. F-016 fixed the same defect in T-39;
   F-017 must not re-introduce it.
5. **M-1** — Add an owner sign-off task between T-08 (dynamic-readiness convention) and
   T-09..T-15 (skills that reference it). The owner approves the convention document
   *before* it is baked into 7 skills and 15 agent-body tasks. (Cheapest fix: a T-08a
   owner-approval task with a `RECENT_CHANGES.md` entry as the carrier until T-36
   ships the approval-ledger mechanism.)

### Recommended changes (improves the plan; not strictly required)

6. **M-2** — Pin the Claude adapter fix to the adapter layer (capability-driven,
   no `if runtime == "claude"`). T-35 acceptance should verify.
7. **M-3** — Reconcile the "12 architecture-constitution rules" wording in T-11 / T-12
   to a single source (the F-016 reviewer's canonical 12-rule set, or the YAML's 11).
8. **M-4** — Add explicit acceptance bullets to T-17..T-30, T-31, T-36, T-56 for the
   FR-016 / FR-018 / SC-011 / SC-012 properties that are currently under-pinned.
9. **M-5** — Narrow the cost-of-change claim in PLAN.md:49 to "new leaf agent or new
   skill" and add a follow-up to make bootstrap's promotion set data-driven.
10. **M-6** — Extend T-31 to also check the `aspis *` pattern on system-lead (D-002
    intent) and document the exception.
11. **L-1** — Fix the "4 files" / "5 files" count in PLAN.md:75.
12. **L-4** — Expand T-56 to a sub-checklist of SC-001..SC-012.

### Routing

These are pre-build specification hygiene issues. They route to **planning-lead** for
SPEC.md / PLAN.md / TASKS.md corrections, and to the **build lead** (when the plan
is re-approved) for H-3's `src/aspis/commands/` redirection. None of the findings
implies a redesign; all are pinpointed with file:line and a recommended fix.
After the 5 required changes, this plan is APPROVE-WITH-CONDITIONS-ready for the
T-32 L1 owner review gate (which itself is the M-1 enforcement for the dynamic-
readiness decision once T-08 is approved).
<!-- ASPIS:REVIEW:END -->
