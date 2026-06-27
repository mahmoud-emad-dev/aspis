# F-016 Audit — Triage for Decision

> Companion to `findings-1.md` (the full T-03 audit, 40 findings).
> Purpose: let the system owner judge each finding **one by one**, fast.
> Lens: the new doctrine — *a real defect raises cost-of-change, breaks a gate,
> causes wrong/unsafe behaviour, or makes the system harder to understand/run.
> A missing box-ticking section is NOT a defect.*
>
> How to use: read the "Plain meaning" + my "Call". In the **Your call** column
> write `fix` / `skip` / `later` (or just tell me the IDs you disagree with).

---

## Owner decisions — LOCKED (T-04 work order)

Recorded from the owner's annotations. **Cross-cutting intent that overrides the
raw audit wording:** (1) the **catalog is the target** — fix the design in the
catalog; the owner's *live* runtime is a personal/custom setup and is NOT the
truth to chase; (2) every fix is **iterative, not final** — set what a clear,
minimal role needs to work now; refine with real usage later; (3) keep each
agent's role **clear and minimal (role + skills + assets)** so even a standard/
cheap model succeeds; differentiate **do-it-myself vs delegate-to-subagent**.

**Group 1 — all FIX, with these refinements:**
- **B-6 (system-lead):** Keep "only lead that may modify runtime/protected files,"
  but state it acts **only through aspis tools/commands (never raw direct edits)**
  and is **scoped to `.aspis/`**. Remove the free self-edit/hook-disable framing;
  those route through governed tools (+ R-008 where required). Note project-lead
  may **read only some** runtime files, not all. (Specialised subagents take the
  dangerous ops later.)
- **F-3 + A-1 (reviewer, research-lead tiers):** Declare both **standard by
  default, deeper when the task warrants**; tier resolves against user preference
  + available models. Full capability-scoring is a **future feature** — keep simple.
- **C-7 (reviewer drift):** Set the **catalog** tier per design (standard/deep);
  **ignore the live custom model** (personal setup). Model scoring = future feature.
- **D-6 (system-lead bash):** Replace the `*` wildcard with the **named commands
  it actually needs now**; accept it's iterative; move dangerous ops to subagents later.
- **B-5 (research-lead write/edit):** **KEEP write:allow + edit:deny — it's
  intentional.** Research writes NEW files (to `<feature>/Research/` or
  `.aspis/research/` by kind), doesn't edit existing. Just **document the rationale**
  in the permission section. (Do not add edit.)
- **B-1 (planning-lead):** Remove `plan-critic`/`review-strategy` from planning-lead's
  owned/added skills; it **consumes** plan-review via the reviewer.
- **B-2 (reviewer 12-vs-6):** Handler's discretion — label the 6 as a v2 extension
  so the count is unambiguous.
- **D-9 (reviewer):** Remove `aspis artifact test` (read-only; test-lead stamps).
- **A-4 + A-5:** Add the one-line "if stuck, stop — don't guess" to research-lead + reviewer.
- **C-6 (planning-lead):** Fix in the **catalog** (remove committer from the
  task-list); live file deferred. Goal = accurate catalog that follows the design.

**Group 2 — dispositions:**
- **E-4/F-9:** Keep as a prompt/instruction rule now; defer runtime enforcement.
- **F-8:** Defer; when built, make the scope "real needed." ("Enforcement work" =
  the later warn→block + scope-guard hardening.)
- **C-5/F-4:** Skip per-spec duplication; but ensure each agent's design is correct on its own.
- **E-5/E-6/E-9/E-10:** Subagent roster — per lead, the subagents it genuinely
  needs + complete that lead's skills with the new subagents' skills; clear minimal
  roles. Tracked in `subagent-roster-and-delegation.md`.
- **F-5:** Skills inventory (T-31) must list the **real needed** skills per lead/subagent.

**Group 3 — SKIP all** (no owner override; conformance-only).

---

## Group 1 — FIX (concrete defects; I recommend fixing in T-04)

These change behaviour, safety, or cause a real contradiction.

| ID | Where | Plain meaning | Why it's real | My call | Your call |
|----|-------|---------------|---------------|---------|-----------|
| B-6 | system-lead | Says it's "the ONLY lead that may modify runtime files" but also admits it can edit its own agent file / committer's permissions / disable hooks | A self-modification hole in the most powerful agent — real safety contradiction | **fix** | |
| F-3 + A-1 | reviewer, research-lead | These two agents never declare their model tier (every other agent does) | The reviewer judges everything; not knowing its model is a real R-007 gap | **fix** | |
| C-7 | reviewer | Reviewer's model is drifted: live = cheap, config = deep | The quality gate may be running on the wrong (cheap) model | **fix** (same cluster as tiers) | |
| D-6 | system-lead | bash = "allow all except git commit/push" — a wildcard | Most dangerous agent has the widest shell surface; injection = full compromise | **fix** (name the commands) | |
| B-5 | research-lead | `write: allow` but `edit: deny` — contradictory | It must update its own reference files; deny-edit forces delete-and-recreate | **fix** | |
| B-1 | planning-lead | Lists `plan-critic`/`review-strategy` as both "reviewer's skills" AND "add to planning-lead" | Spec contradicts itself on who owns the skill | **fix** (remove from planning-lead) | |
| B-2 | reviewer | Says plan-critic has 12 checks, then says "6 missing" | Reader can't tell the truth without re-reading | **fix** (label the 6 as v2) | |
| D-9 | reviewer | Allowed to run `aspis artifact test` (stamp a TEST_REPORT) | Reviewer is read-only; stamping test artifacts is test-lead's job | **fix** (remove the line) | |
| A-4 + A-5 | research-lead, reviewer | Missing the universal "if stuck, stop — don't guess" rule | Cheap, real guardrail every other agent has; both touch error-prone work | **fix** (1 line each) | |
| C-6 | planning-lead | `committer` still in the live task-list (should be removed) | A real live drift — but fix it during the catalog phase, not now | **fix at catalog step** | |

## Group 2 — YOUR CALL (real, but the fix is bigger or needs a decision)

These aren't box-ticking, but "fixing" means building something or making a policy choice.

| ID | Where | Plain meaning | The decision | My lean | Your call |
|----|-------|---------------|--------------|---------|-----------|
| E-4 / F-9 | build-lead | "Don't call committer without review approval" is only a prompt instruction, not enforced by code | Build a hook that checks a review verdict exists before commit? Or accept the prompt rule? | defer to the enforcement work (don't build now) | |
| F-8 | build-lead | `active_feature.json` has no `scope` field, so the scope-guard is a no-op | Add the scope field + guard now, or with the enforcement work? | defer to enforcement work | |
| C-5 / F-4 | all specs | Enforcement mode (warn vs block) is only written in system-lead | It IS specified where it's owned. Copy a line into all 8, or leave it owned in one place? | leave it owned in one place (skip) | |
| E-5/E-6/E-9/E-10 | reviewer, research-lead, planning-lead, fix-lead | "Future subagents" referenced but not designed | This is the **subagent roster** question — answered separately | see subagent decision | |
| F-5 | all specs | 30+ proposed new skills, scattered, some duplicated | This is literally task **T-31** (skills inventory) — already planned | skip here (T-31 owns it) | |

## Group 3 — SKIP (conformance-only; not defects by the doctrine)

Recommend NOT doing these — they make 8 already-large specs bigger/more rigid without changing behaviour. (Tell me if you want any promoted.)

| ID | Where | What the audit wants | Why I'd skip |
|----|-------|----------------------|--------------|
| A-2, A-6 | test-lead | Add a separate "Error Handling matrix" (it has Escalation) | Same info, different heading |
| A-3 | research-lead | Fix section numbering 9→11 | Cosmetic; trivial if touched in passing |
| A-7 | fix-lead | Move error handling into a matrix | Info already present in lifecycle |
| A-8, A-9 | research-lead, test-lead | Add a formal "Delegation Map" table | Delegation already stated |
| B-3, B-4 | system-lead, fix-lead, test-lead | Add a "Constitution Compliance" section | Box-ticking; rules apply by role, not by recital |
| B-7 | all | Add a "C-PORTABLE" note to each bash list | That's a script rule, not a spec rule |
| C-1, C-2, C-3, C-4 | fix/test/research/reviewer | Add tables citing all 9 R-rules | Pure recital; R-006 says state once, don't duplicate |
| C-8 | all | Add an R-009 trace-format to every spec | Conformance; no behaviour change |
| D-5, D-7 | all, fix-lead | Standardise bash-table formatting | Style, not defect (the D-6 wildcard is the only real one) |
| E-1, E-2 | 4 agents each | "context-ladder" / "confirm clean state" claimed by several | Shared skills are fine; each operates at its own level |

---

## Summary

- **Fix now:** ~10 findings (Group 1), all concrete — safety, model tier, permission, self-contradiction. Small, targeted edits.
- **Your call:** 5 (Group 2) — mostly "build later with the enforcement work" or covered elsewhere.
- **Skip:** ~20 (Group 3) — conformance-only; doing them is the over-engineering risk.

Net: T-04 becomes a **focused ~10-edit pass**, not a 40-item rewrite. That keeps the specs lean and the direction practical.
