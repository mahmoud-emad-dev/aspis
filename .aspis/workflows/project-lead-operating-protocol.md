# project-lead-operating-protocol

> The project-lead's operating procedure — the master orchestration loop that
> routes work to the right lead, enforces gates, handles human approvals, and
> closes sessions cleanly. Every step is numbered; stop-and-ask points are
> marked with ⏸️ STOP-AND-ASK.

---

## §1 — Session Start

**Purpose:** Establish a known, safe baseline before any work begins. Never
operate from a stale or dirty state.

1. **Read CURRENT_STATE.md.** Load the live project state — branch, last commit,
   active feature. This is the one-file baseline; everything else derives from it.
   *Output:* known project state (branch, commit, feature, mode).

2. **Read RECENT_CHANGES.md.** Know what changed since the last session — new
   commits, merged features, gate results. Prevents re-solving solved problems.
   *Output:* change awareness (last 15 commits, recent merges, gate outcomes).

3. **Read active_feature.json.** Identify the active feature ID, its branch,
   current phase, and build mode. If no active feature is set, this is a
   free-form session — skip feature-specific context.
   *Output:* active feature context (or "none — free-form session").

4. **Run `git status`.** Confirm the working tree is clean or contains only
   expected untracked files (feature artifacts, generated brain files). A dirty
   tree with modified tracked files is a blocker — resolve before proceeding.
   *Output:* tree state (clean / dirty-with-expected / dirty-blocker).

5. **Run `aspis preflight`.** Deterministic pre-start gate — checks clean tree,
   correct branch, no unresolved guard findings. Exit 0 = ready; non-zero = blocked.
   *Output:* go/no-go verdict.
   > ⏸️ **STOP-AND-ASK #1 — Preflight fails with a blocker you cannot resolve.**
   > Cause: uncommitted work from another session, wrong branch, or guard findings
   > requiring owner action. Present the blocker to the user with the exact
   > `aspis findings` output and ask: "Resolve this blocker before we proceed.
   > Options: (a) commit/stash the work, (b) switch branch, (c) resolve findings,
   > (d) explain why this is expected." Do not proceed without resolution.

6. **Check for pending governance requests.** Scan `.aspis/approvals/` for any
   R-008 requests awaiting owner approval. These block protected-path changes
   and may gate the session.
   *Output:* pending approvals list (request IDs, paths, timestamps).

7. **Check for BLOCKED items from prior sessions.** Review TASKS.md or handover
   notes for tasks stuck on external dependencies, env issues, or human gates.
   These may have resolved since the last session.
   *Output:* blocked items inventory (task ID, blocker, age).

8. **Review session handover notes** (if this is a continuation). The prior
   session's handover notes contain: what was completed, what's in progress,
   what's blocked, and what needs attention next. Pick up exactly where the
   notes left off.
   *Output:* continuation context loaded.

9. **Assess overall session health.** Aggregate: git state, preflight result,
   pending approvals, blocked items, and handover status. Produce a one-line
   health verdict: "READY — all gates green" or "DEGRADED — N blocked items, M
   pending approvals."
   *Output:* session health snapshot.

---

## §2 — Request Triage

**Purpose:** Classify every incoming request, select the right lead, and package
the context they need. Misclassification here wastes the whole session.

10. **Capture the incoming request verbatim.** Do not paraphrase, summarize, or
    interpret. The raw request is the reference point for classification and for
    the lead that receives it.
    *Output:* raw request text captured.

11. **Classify request intent.** Map to one of: `feature-plan` (new feature to
    plan), `feature-build` (approved plan to build), `bug-fix` (defect report),
    `research-question` (knowledge gap), `status-report` (project health query),
    `mode-change` (change build mode), `system-change` (config or infrastructure
    change), `emergency-rollback` (revert to known good), `unknown-request`
    (ambiguous or novel), or `stuck-agent` (agent recovery).
    *Output:* intent classification, track, and confidence.
    > ⏸️ **STOP-AND-ASK #2 — Cannot classify intent; request is ambiguous.**
    > Cause: the request doesn't fit any known track, or could fit multiple
    > tracks with different implications. Ask one clarifying question:
    > "I see this could be X (which would mean Y) or Z (which would mean W).
    > Which direction is closer to what you need?" Do not guess a track.

12. **Determine required depth.** Map the classified intent + scope estimate to
    a build mode: `vibe` (trivial, ≤1 file, no gates), `mvp` (moderate, ≤5
    files, light gates), or `production` (complex, any file count, full gates).
    Use `mode-decision` skill or `.aspis/config/policy/modes.yaml` ceilings.
    *Output:* mode decision with rationale.

13. **Select the owning lead.** Map intent to lead:
    | Intent | Lead | Rationale |
    |--------|------|-----------|
    | feature-plan | planning-lead | Owns spec, architecture, task decomposition. |
    | feature-build | build-lead | Owns implementation from approved plan. |
    | bug-fix | fix-lead | Owns root-cause diagnosis and repair. |
    | research-question | research-lead | Owns knowledge acquisition and packaging. |
    | status-report | project-lead (self) | Project-lead owns status aggregation. |
    | mode-change | system-lead | Owns configuration and policy changes. |
    | system-change | system-lead | Owns infrastructure and runtime changes. |
    | emergency-rollback | fix-lead + system-lead | Joint: fix-lead diagnoses, system-lead executes. |
    | unknown-request | project-lead (self) | Project-lead triages novel requests directly. |
    | stuck-agent | project-lead (self) | Project-lead intervenes in deadlocked agents. |
    *Output:* lead assignment.
    > ⏸️ **STOP-AND-ASK #3 — No lead matches the request; new capability needed.**
    > Cause: the request requires a lead or subagent that doesn't exist. Tell the
    > user: "This request needs a [role] that isn't in the current agent catalog.
    > Options: (a) handle it manually this session, (b) defer until F-019 adds the
    > capability, (c) scope a new feature to build the missing agent." Do not
    > silently route to the wrong lead.

14. **Package request context.** Assemble the context packet the lead needs:
    - L1 hot context (CURRENT_STATE, RECENT_CHANGES, active_feature.json)
    - Feature context (SPEC, PLAN, TASKS — if feature-build or bug-fix)
    - The raw request (verbatim)
    - Classification decision (intent, track, mode)
    - Any constraints (timebox, scope boundary, specific files/don't-touch)
    - Previous session context (if continuation)
    *Output:* context packet assembled.

15. **Verify lead availability.** Check: is the lead's agent file valid
    (`validate-runtime` passes for it)? Is the lead already mid-session on
    another task? Does the lead have the required skills and tools for this
    request?
    *Output:* lead status (ready / blocked / missing-skill).

16. **Hand off to owning lead.** Dispatch the lead with the context packet as
    its initial prompt. The lead receives: identity, request, context, and
    constraints. It returns: output artifacts or a block reason.
    *Output:* lead dispatched.
    > ⏸️ **STOP-AND-ASK #4 — Lead reports it cannot handle this request.**
    > Cause: scope gap — the lead doesn't have the tools, skills, or permissions
    > needed. Present the lead's block reason to the user: "The [lead] says it
    > can't handle this because [reason]. Options: (a) adjust the request to fit
    > the lead's scope, (b) handle it manually, (c) scope a feature to extend the
    > lead." Do not force the lead to operate outside its scope.

17. **Record hand-off.** Log: request ID, lead assigned, timestamp, expected
    response window (based on mode and task complexity), and context packet hash.
    *Output:* tracking entry in session log.

18. **Monitor for initial response.** If the lead doesn't respond within the
    expected window: first, check if it's processing (deep work takes time);
    second, check if it's stuck (see §7 Error Recovery). Do not re-dispatch the
    same request to a different lead without diagnosing the silence.
    *Output:* response received (with artifact) or timeout (flagged for recovery).

---

## §3 — Orchestration Loop

**Purpose:** Keep the multi-lead pipeline flowing. Between each orchestration
step, re-read the live state to catch drift. Detect and correct misrouted work
before it compounds.

19. **Dispatch work to the qualified lead.** After triage (§2), hand the lead
    its enriched context packet and the specific task or question. The lead owns
    execution; project-lead owns coordination.
    *Output:* work started; lead acknowledged.

20. **Recontextualize between orchestrations.** Before each new dispatch or
    phase transition, minimally re-read:
    - `CURRENT_STATE.md` — has the branch or commit changed?
    - `RECENT_CHANGES.md` — did a parallel lead commit something?
    - `active_feature.json` — is the feature, phase, or mode still current?
    - The lead's last output — did it produce what was expected?
    If state has changed materially, adjust the context packet before the next
    dispatch. Do NOT re-read the full feature plan — only what changed.
    *Output:* fresh context confirmed or drift detected.
    > ⏸️ **STOP-AND-ASK #5 — State changed significantly during orchestration.**
    > Cause: a parallel lead committed work that changes the plan, a mode change
    > was applied, or a gate failed and blocked downstream work. Present the delta:
    > "Since the last dispatch: [changes]. This may affect [tasks]. Options:
    > (a) continue — changes don't affect current work, (b) pause and replan
    > affected tasks, (c) abort this orchestration and restart." Do not silently
    > continue with stale context.

21. **Consume lead output artifacts.** When a lead returns, verify:
    - The output matches the expected format (SPEC, PLAN, BUILD_REPORT, etc.)
    - The output covers the requested scope (no missing sections)
    - The output references real files (no hallucinated paths)
    - The output is internally consistent (no contradictory statements)
    *Output:* validated artifacts (accepted) or rejected with reason.

22. **Detect misrouted work.** Signs of misrouting:
    - A lead produces output outside its domain (e.g., build-lead writing a SPEC)
    - A lead asks questions that belong to a different lead's scope
    - A lead reports "this isn't my job" or "I need [other lead] for this"
    - The output quality is poor because the lead lacks the right skills
    *Output:* misroute detected (or confirmed correct routing).

23. **Reroute misdirected tasks.** If misrouting is detected:
    - Extract the correct domain from the output or error
    - Reclassify per §2's intent map
    - Package a corrected context packet for the right lead
    - Include a note: "Previously misrouted to [wrong lead]; reclassified as
      [correct intent] because [reason]."
    *Output:* task reassigned to correct lead.

24. **Chain leads in dependency order.** The standard pipeline:
    ```
    planning-lead → build-lead → reviewer → committer
                        ↑             ↓
                    fix-lead ←── (review finds defects)
    ```
    No lead receives work until its upstream dependency has produced accepted
    output. Build-lead doesn't start until planning-lead's PLAN is approved.
    Reviewer doesn't review until build-lead's task is complete.
    *Output:* pipeline flowing in order.

25. **Track progress across leads.** After each lead completes a task:
    - Update the task's status in session tracking (not TASKS.md yet — that's
      §6)
    - Record: lead, task ID, result (pass/fail/blocked), timestamp, artifacts
    - Flag any task that took >2× its expected window for review
    *Output:* progress tracking current.

26. **Detect phase completion.** When all tasks in the current layer/phase are
    done, do not auto-advance. Signal to §6 (Phase Completion) for gate
    enforcement and review before the next phase starts.
    *Output:* phase ready for gate.

27. **Signal phase readiness to gate enforcement (§4).** Hand off the completed
    phase's tasks and artifacts to the gate enforcement section. Include: what
    was built, by which leads, with what evidence.
    *Output:* phase handoff to gate enforcement.

---

## §4 — Gate Enforcement

**Purpose:** Every phase has exit gates. No phase advances until its gates pass.
The project-lead runs the gates, records the evidence, and blocks progress on
failure.

28. **Identify required gates for the current phase.** Per-mode gate list:
    | Mode | Gates required |
    |------|---------------|
    | vibe | None (no gates) |
    | mvp | pytest (if code), ruff (if code), validate-runtime |
    | production | pytest, ruff, validate-runtime, validate-index, byte-parity, aspis doctor |
    *Output:* gate checklist for current phase.

29. **Run `pytest`** (if the phase changed source code or tests). Must exit 0.
    If the environment blocks subprocess tests, all non-subprocess tests must
    pass; blocked tests documented as `BLOCKED: env`.
    *Output:* pytest evidence (pass / fail-with-evidence / blocked-env).
    > ⏸️ **STOP-AND-ASK #6 — pytest fails with non-trivial failures.**
    > Cause: real test failures that aren't env artifacts or known blocked items.
    > Present: failure count, failed test names, and stack traces. Ask: "pytest
    > shows [N] failures. Options: (a) route to fix-lead for root-cause fix,
    > (b) these are known and documented — proceed with waiver, (c) these are
    > env-only — mark BLOCKED: env." Do not proceed with real failures
    > unaddressed.

30. **Run `ruff format --check .` and `ruff check .`** (if the phase changed
    Python files). Both must exit 0. Ruff failures are mechanical — format or
    lint the affected files and re-run.
    *Output:* ruff evidence (pass / fail-with-fix).

31. **Run `validate-runtime --runtime all`.** All agents (existing + new) must
    validate. Checks: frontmatter completeness, skill references resolve,
    delegate references resolve, no orphan delegates, no broken refs.
    *Output:* runtime validation evidence.

32. **Run `validate-index`.** The file registry and code map must be consistent
    with the actual file tree. Drift here means the generated brain is stale —
    refresh with `aspis context` and re-run.
    *Output:* index validation evidence.

33. **Run `byte-parity --dry-run`.** Catalog source must match deployed runtime
    for every asset. Any difference means the runtime was hand-edited or the
    catalog wasn't re-exported after a change. Fix in catalog source, not in
    runtime.
    *Output:* parity report (CLEAN / DRIFT-details).

34. **Run `aspis doctor`.** System-wide health check — finds permission gaps,
    missing files, config inconsistencies, and structural issues.
    *Output:* health report (pass / FAIL-findings).

35. **Aggregate gate results.** All identified gates must pass. If any gate
    fails:
    - Non-blocking (ruff format): fix and re-run immediately
    - Blocking (pytest failure, runtime validation failure): route to the
      appropriate lead (fix-lead, system-lead) and block phase advance
    *Output:* gate verdict (ALL-GREEN / BLOCKED-with-reasons).
    > ⏸️ **STOP-AND-ASK #7 — Gate fails and fix is beyond current scope.**
    > Cause: a gate failure whose root cause is outside the current feature's
    > scope (e.g., a pre-existing bug in the runtime validator, an
    > infrastructure issue). Present: failed gate, root cause, and fix estimate.
    > Ask: "Gate [name] failed because [root cause], which is outside this
    > feature's scope. Options: (a) file a separate bug/fix task and proceed
    > with documented waiver, (b) pause this feature until the fix is done,
    > (c) you handle this one manually." Do not silently waive a real gate
    > failure.

36. **Record gate evidence.** Write the gate report to
    `.aspis/features/<id>/Review/B-<phase>-gate.md`. Include: phase name,
    gates run, results (pass/fail per gate), evidence (pasted output or file
    references), and the final verdict.
    *Output:* gate report filed.

---

## §5 — Human-Gate Handling (R-008)

**Purpose:** R-008 requires owner approval for protected-path changes
(`.claude/settings.json`, `.opencode/config.json`, permission blocks, hook
configurations). The project-lead detects these changes, files governance
requests, waits for approval, applies the change, and verifies.

37. **Detect permissions-change surface.** Before any task that touches
    protected paths begins, flag it. Protected paths per R-008:
    - `.claude/settings.json` — Claude Code hooks, permissions, configuration
    - `.opencode/config.json` — OpenCode hooks, permissions, configuration
    - Any agent frontmatter `permissions:` block that expands tool access
    - `.aspis/rules/` — system rule changes
    - `.aspis/config/policy/` — policy configuration changes
    *Output:* protected-path changes flagged.

38. **Identify exact protected path and required approval scope.** For each
    flagged change: the exact file, the exact lines/fields to change, the
    current value, the proposed value, and the rationale.
    *Output:* approval scope defined per change.

39. **File governance request.** Use the governance subagent to file a
    structured request containing:
    - Request ID (auto-generated)
    - Protected path(s)
    - Proposed change (diff or field-level)
    - Rationale (why this change is needed)
    - Rollback plan (how to undo if it causes issues)
    - Requestor (project-lead, on behalf of the feature)
    - Timestamp
    *Output:* governance request filed.
    > ⏸️ **STOP-AND-ASK #8 — Governance request filed; pause for owner approval.**
    > Present: request ID, protected path, proposed change, and rationale. Tell
    > the user: "R-008 requires your approval to modify [path]. The proposed
    > change is: [summary]. Approval needed before this work can proceed. The
    > rest of the feature continues in parallel where possible." Do not apply
    > the change. Do not proceed past this task.

40. **Wait for owner approval.** The governance subagent tracks the request.
    Poll periodically; the project-lead does not busy-wait. Continue with
    non-blocked tasks in the meantime. If the SLA expires (default 48 hours),
    escalate (step 45).
    *Output:* approval received (or still pending — continue other work).

41. **Apply approved change.** Once owner approves via governance subagent's
    `approve` verb, apply the exact change specified in the governance request.
    Do not alter the scope — if the owner approved a modified version, use the
    approved version, not the original request.
    *Output:* change applied exactly as approved.

42. **Verify change applied correctly.** Run the relevant gate:
    - `.claude/settings.json` → validate JSON syntax, hook references resolve
    - Permissions changes → `validate-runtime --runtime all`
    - Config changes → `aspis doctor`
    *Output:* verification evidence.

43. **Record human-gate outcome.** Log: request ID, protected path, approval
    timestamp, approver, change applied (commit hash), verification result.
    Write to the feature's gate report and the governance ledger.
    *Output:* human-gate log entry.

44. **Handle denial.** If owner denies:
    - Document the denial reason verbatim
    - Determine: revise and resubmit, or abandon the change
    - If the change is optional: abandon and document the descope
    - If the change is critical: escalate (next step)
    *Output:* denial handled (revised / abandoned / escalated).
    > ⏸️ **STOP-AND-ASK #9 — Owner denies governance request.**
    > Cause: owner rejected the proposed change. Present the denial reason.
    > Ask: "The owner denied the governance request for [path] because [reason].
    > Options: (a) revise the proposal addressing the concern and resubmit,
    > (b) abandon this change and descope the dependent work, (c) the change is
    > critical — escalate to project-lead override discussion."
    > > ⏸️ **STOP-AND-ASK #10 — Change denied but is critical; escalate.**
    > > This is the escalation within a denial. Present the impasse: "This change
    > > is required for [feature/task] to proceed, but the owner denied it.
    > > We're at an impasse. Options: (a) you (the user) override the denial
    > > directly, (b) we discuss alternatives that achieve the goal without the
    > > protected-path change, (c) we pause this feature until this is resolved."
    > > Do not bypass the governance ledger.

45. **Handle timeout.** If no owner response within the SLA (48 hours default):
    - Re-notify with urgency
    - If another 24 hours pass with no response: escalate
    - Document the timeout in the governance ledger
    *Output:* timeout escalated or resolved.

---

## §6 — Phase Completion

**Purpose:** Each phase (L0, L1, L2, L3, L4, final) has a formal completion
sequence: review, gate aggregation, TASKS update, and handoff to the next phase.

46. **Trigger per-phase review.** For every completed phase, delegate plan
    review (for planning phases) or build review (for build phases) to the
    reviewer. The reviewer receives: the completed artifacts, the gate results,
    and the acceptance criteria.
    *Output:* review dispatched.

47. **Collect review reports.** The reviewer returns a structured review with:
    findings (BLOCKER/WARN/INFO), per-criterion verdict, and an overall
    pass/fail/revise recommendation.
    *Output:* review evidence collected.

48. **Aggregate review findings.** Categorize every finding:
    - **BLOCKER**: must be fixed before phase advance (circular dep, missing
      file, gate failure, security issue)
    - **WARN**: should be fixed but doesn't block (missing edge case, weak
      acceptance criteria, style deviation)
    - **INFO**: note for future work (optimization opportunity, documentation
      gap, deferred refactor)
    *Output:* finding summary with counts per category.

49. **Determine phase pass/fail.** A phase passes when:
    - All gates from §4 are green
    - All review BLOCKERs are resolved
    - All WARNs are either resolved or explicitly deferred with owner
    A phase fails if: any BLOCKER remains unresolved after the fix window.
    *Output:* phase verdict (PASS / FAIL / PASS-WITH-WAIVERS).
    > ⏸️ **STOP-AND-ASK #11 — Reviewer finds an architecture-level issue.**
    > Cause: the review uncovered a structural problem that affects the plan's
    > design — not a simple bug but a design flaw. Present the finding verbatim.
    > Ask: "The reviewer found an architecture issue: [finding]. This may require
    > replanning. Options: (a) accept the finding and route to planning-lead for
    > plan revision, (b) the finding is a misunderstanding — document the
    > rebuttal, (c) accept the risk and proceed with a documented deviation."
    > Do not silently override a structural review finding.

50. **Update TASKS.md.** For every completed task in the phase:
    - Flip `[ ]` → `[x]`
    - If a task was blocked/waived, leave `[ ]` and add a note
    - Flip the phase gate task checkbox (e.g., `T-020 [x]`)
    *Output:* TASKS.md updated with current completion state.

51. **Write phase gate report.** Create
    `.aspis/features/<id>/Review/B-<phase>-gate.md` with: phase name, gates
    run and results, review summary, BLOCKER/WARN/INFO counts, final verdict,
    and timestamp.
    *Output:* phase gate report filed.

52. **Update RECENT_CHANGES.** Commit the gate report (via committer) with a
    conventional commit message:
    `docs(F-<id>/<phase>): record <phase> gate — <N> tasks, <verdict>`
    *Output:* RECENT_CHANGES updated via commit.

53. **Signal next phase readiness.** If the phase passed: notify the lead that
    owns the next phase (per the dependency chain in PLAN.md). If the phase
    failed: route back to the owning lead for fixes. If this was the final
    phase: proceed to §8 (Session Close).
    *Output:* handoff signal (next phase / fix needed / feature complete).

---

## §7 — Error Recovery

**Purpose:** When things go wrong — stuck agents, repeated failures, blocked
tasks — the project-lead intervenes, diagnoses, fixes or escalates, and
restores forward progress. Never leave a broken state unaddressed.

54. **Detect stuck/deadlocked agents.** Signs of a stuck agent:
    - No response beyond 2× the expected window for its task
    - Circular delegation (agent A delegates to B, B delegates back to A)
    - Repeatedly asking the same question without progress
    - Producing output that doesn't advance the task state
    *Output:* stuck agent identified with evidence.
    > ⏸️ **STOP-AND-ASK #12 — Agent is stuck and cannot self-recover.**
    > Present: agent name, task, time stuck, and observed symptom. Ask:
    > "The [agent] is stuck on [task] — it's been [symptom] for [duration].
    > Options: (a) kill the task and reassign with clarified instructions,
    > (b) kill the task and handle manually, (c) give the agent a specific
    > unblocking hint." Do not let a stuck agent consume unlimited time.

55. **Identify BLOCKED items.** Scan the active feature's TASKS.md and the
    session tracking log for tasks marked BLOCKED. Categorize by blocker type:
    - `BLOCKED: env` — environment issue (subprocess, platform, missing tool)
    - `BLOCKED: dependency` — upstream task not yet complete
    - `BLOCKED: human-gate` — waiting for R-008 approval
    - `BLOCKED: external` — depends on something outside the project
    *Output:* blocked items inventory with blocker type and age.

56. **Apply 3-attempt cap.** For any task that fails with the same root cause:
    - Attempt 1: initial failure → record root cause, pass to fix-lead
    - Attempt 2: same failure after fix → escalate diagnosis effort
    - Attempt 3: same failure again → **cap reached**; do not retry
    After 3 attempts, the task is capped. Document: task ID, root cause,
    attempts (timestamps, what was tried, why it failed), and recommended
    action (replan / descope / external fix / manual).
    *Output:* capped task with evidence log.

57. **Diagnose root cause of repeated failure.** If a fix-lead is available,
    delegate root-cause analysis. The fix-lead returns: the true cause (not the
    symptom), the minimal fix, and the verification that the fix doesn't
    regress. If fix-lead is unavailable, diagnose heuristically: compare the
    working state to the failing state, isolate the delta, and test the
    hypothesis.
    *Output:* root cause identified (or "unknown — escalated").

58. **Apply minimal fix if root cause is in scope.** The fix must:
    - Address the root cause, not the symptom
    - Touch the minimum files necessary
    - Include verification (re-run the failing test/gate)
    - Not introduce new failures (re-run the full gate sweep for the phase)
    *Output:* fix applied and verified.

59. **Escalate persistent failures.** If 3 attempts are exhausted and the root
    cause is out of scope or unknown:
    - Write an escalation report: task ID, root cause (or "unknown"), attempts
      log, impact (what's blocked downstream), and recommendation
    - Present to the user
    *Output:* escalation report filed.
    > ⏸️ **STOP-AND-ASK #13 — Persistent failure blocks the feature.**
    > Present the escalation report. Ask: "Task [T-NNN] has failed 3 times with
    > root cause [cause]. This blocks [downstream tasks]. Options:
    > (a) descope this task and adjust the plan, (b) you handle this one
    > manually, (c) we defer the feature until [condition] is met." Do not
    > silently skip a blocked task.

60. **Rollback on regression.** If a fix introduces new failures:
    - Identify the last known green state (git log, gate report)
    - Revert to that commit (via `git revert` or checkout)
    - Re-run the phase gates to confirm the revert restored green
    - Document: what was reverted, why, and what the fix attempt was
    - Route the original problem back to diagnosis with the new evidence
    *Output:* rollback complete; system at last known green.

61. **Document recovery evidence.** After any recovery action (unsticking an
    agent, fixing a failure, unblocking a task, rolling back), write a brief
    recovery log: what happened, what was tried, what resolved it, what state
    the system is in now. Attach to the feature's Review/ directory or session
    log.
    *Output:* recovery log filed.

---

## §8 — Session Close

**Purpose:** Leave the project in a clean, documented state that the next
session can pick up without archaeology. Update every live-state file, commit
everything, and write handover notes.

62. **Final gate sweep.** Before closing, re-run the full gate suite one last
    time:
    - `pytest` (if code changed)
    - `ruff format --check . && ruff check .`
    - `validate-runtime --runtime all`
    - `validate-index`
    - `byte-parity --dry-run`
    - `aspis doctor`
    All must pass. Any failure at this point is an unaddressed issue — route to
    §7 before closing.
    *Output:* all-green confirmation (or last-minute fix).

63. **Update and commit RECENT_CHANGES.** The session's final commit(s) must
    update `.aspis/context/RECENT_CHANGES.md` via `aspis context`. Route all
    remaining uncommitted work through the committer with conventional commit
    messages.
    *Output:* RECENT_CHANGES current; all work committed.

64. **Flip TASKS.md boxes.** Every task completed this session: `[ ]` → `[x]`.
    Every task blocked: leave `[ ]` with `BLOCKED: <reason>` annotation.
    Every task in progress: leave `[ ]` with `IN PROGRESS: <state>`.
    Commit the updated TASKS.md.
    *Output:* TASKS.md reflects session reality.

65. **Write BUILD_REPORT** (if the feature is complete). Aggregate all phase
    gate reports into a single BUILD_REPORT.md at
    `.aspis/features/<id>/BUILD_REPORT.md`. Sections:
    - Feature summary (ID, title, mode, dates)
    - Phase-by-phase gate results (L0→L4, each with verdict and evidence refs)
    - Test summary (total tests, passed, failed, skipped, blocked)
    - Review summary (BLOCKER/WARN/INFO counts, reviewer sign-off)
    - Human-gate log (requests filed, approved, denied, pending)
    - Final verdict (PASS / PASS-WITH-WAIVERS / FAIL)
    *Output:* BUILD_REPORT.md filed (if feature complete).

66. **Write handover notes.** If the feature is NOT complete (more sessions
    needed), write a concise handover note covering:
    - **Done**: what was completed this session (task IDs, commits)
    - **In progress**: what's mid-execution and its state
    - **Blocked**: what's stuck and why (with blocker type and age)
    - **Next**: what the next session should do first (specific task IDs)
    - **Context**: any tribal knowledge the next sessioner needs (e.g., "the
      test failure in test_export.py is a known env issue — documented in
      L0_GATE_REPORT.txt")
    Save to `.aspis/features/<id>/HANDOVER.md` and commit.
    *Output:* handover notes filed.

67. **Verify clean tree.** Final `git status` should show:
    - No modified tracked files (all changes committed)
    - Only expected untracked files: feature artifacts (SPEC, PLAN, TASKS,
      Review/, Research/, HANDOVER.md) and generated brain files
      (`.aspis/index/`, `.aspis/context/`)
    If anything unexpected remains, diagnose and resolve before closing.
    *Output:* clean tree confirmed.

68. **Signal session complete.** Update `CURRENT_STATE.md` (via `aspis context`
    or commit). Record session metrics: duration, tasks completed, gates passed,
    leads used, human-gate interactions, errors recovered. The next session
    reads this state and starts from a known baseline.
    *Output:* session closed; state recorded.

---

## Per-delegate profiles

*When to use each lead — integrated into the orchestration loop. Use these
profiles to select the right delegate for the right work.*

### planning-lead
- **When**: Any new feature, change to existing feature scope, or architecture
  decision. The request is a goal or problem, not a task list.
- **What it produces**: SPEC.md, PLAN.md, TASKS.md, task packets, clarification
  log, architecture decisions.
- **Hand-off**: Give it the raw request + L1 context + mode. It returns a
  complete, reviewable plan.
- **Do not use for**: Building code, fixing bugs, reviewing work, answering
  factual questions. It plans; it does not execute.

### build-lead
- **When**: An approved plan exists (SPEC + PLAN + TASKS). The request is a
  feature to implement from a build-ready plan.
- **What it produces**: Implemented code, test evidence, gate reports, build
  artifacts. Orchestrates general-builder and other builders.
- **Hand-off**: Give it the approved plan + active feature context. It returns
  a built, tested, reviewed, committed feature.
- **Do not use for**: Planning, fixing bugs without a plan, research, reviewing.
  It builds from plans; it does not create them.

### reviewer
- **When**: Any completed plan or build task needs independent quality
  validation before it advances. Gate-enforced — production mode requires
  per-task review.
- **What it produces**: Review reports with BLOCKER/WARN/INFO findings,
  per-criterion verdicts, and pass/fail/revise recommendation.
- **Hand-off**: Give it the completed artifact + acceptance criteria + any
  relevant context (plan, constitution, standards). It returns a structured
  review.
- **Do not use for**: Building, planning, fixing. It validates; it does not
  create or repair.

### system-lead
- **When**: Configuration changes, runtime infrastructure, mode/policy changes,
  export management, catalog synchronization, or any system-level operation.
- **What it produces**: Config updates, runtime exports, catalog fixes,
  infrastructure changes, health reports.
- **Hand-off**: Give it the system change request + current config state. It
  returns the applied change + verification.
- **Do not use for**: Feature planning, feature building, review. It operates on
  the system itself, not on features.

### fix-lead
- **When**: A defect is reported (bug, regression, test failure, gate failure).
  The request is a broken thing that needs repair.
- **What it produces**: Root-cause analysis, minimal fix, regression
  verification, recovery log.
- **Hand-off**: Give it the defect evidence (stack trace, test output, gate
  failure) + the codebase context. It returns a fixed, verified state.
- **Do not use for**: New features, planning, review. It repairs; it does not
  build new things.

### research-lead
- **When**: A knowledge gap blocks planning or building — a library version
  question, an API capability check, a best-practice lookup.
- **What it produces**: Research assets (reference files in `.aspis/research/`),
  knowledge summaries, version comparisons, source rankings.
- **Hand-off**: Give it a structured RESEARCH_REQUEST (topic, scope, deadline,
  output format). It returns packaged knowledge.
- **Do not use for**: Building, planning, fixing. It acquires knowledge; it does
  not apply it to product code.

### test-lead
- **When**: Test evidence is needed — generating tests, running test suites,
  capturing coverage, or validating test quality independent of the builder.
- **What it produces**: Test reports, test evidence (pass/fail/coverage), test
  generation for uncovered paths.
- **Hand-off**: Give it the scope to test + the test evidence template. It
  returns a structured TEST_REPORT with execution evidence.
- **Do not use for**: Building features, planning, fixing bugs. It tests; it
  does not build or repair.

---

## Recontextualization protocol

*What to re-read between orchestrations — the minimum to catch drift without
reloading the world.*

After each lead completes a task and before dispatching the next, re-read in
this order:

1. **`CURRENT_STATE.md`** (1 file, ~8 lines) — has the branch, commit, or
   feature changed? If yes, the world shifted underneath you.
2. **`RECENT_CHANGES.md`** (1 file, ~15 lines) — did a parallel lead commit
   something that affects your context? The newest commit tells you.
3. **`active_feature.json`** (1 file) — is the active feature, phase, or mode
   still the same? A mode change mid-orchestration changes gate requirements.
4. **The last lead's output** — did it produce what you expected? If the
   planning-lead returned a SPEC when you expected a PLAN, something is wrong.
5. **Only if the above indicate drift:** re-read the feature's TASKS.md to see
   if dependency order or scope changed.

**Rule:** If nothing changed in steps 1-4, proceed with the existing context.
Do not re-read the full SPEC/PLAN/TASKS "just in case" — trust the live state
files. If they're stale, run `aspis context` once to refresh all three.

---

## Human-gate flow

*R-008: the full detect → file → wait → apply → verify lifecycle.*

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   DETECT    │───▶│     FILE     │───▶│     WAIT    │───▶│    APPLY     │───▶│    VERIFY    │
│ protected   │    │ governance   │    │ for owner   │    │ approved     │    │ change is    │
│ path change │    │ request      │    │ approval    │    │ change       │    │ correct      │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └──────────────┘
                         │                    │                  │                   │
                         ▼                    ▼                  ▼                   ▼
                   ┌──────────┐        ┌──────────┐       ┌──────────┐        ┌──────────┐
                   │ DENIED?  │        │ TIMEOUT? │       │ PARTIAL? │        │ FAILED?  │
                   │ → revise │        │ → escalate│      │ → re-file│        │ → revert │
                   │ or abandon│       │ (48h SLA)│       │ remaining│        │ + re-file│
                   └──────────┘        └──────────┘       └──────────┘        └──────────┘
```

### Detect
Scan planned changes for protected paths (`.claude/settings.json`,
`.opencode/config.json`, permission blocks, `.aspis/rules/`,
`.aspis/config/policy/`). Flag before the task starts — not after it's built.

### File
Use the governance subagent `request` verb. Structured request: path, proposed
change (diff), rationale, rollback plan. Request is recorded in the governance
ledger (`.aspis/approvals/`).

### Wait
Do not apply the change. Continue other non-blocked work. Poll periodically.
SLA: 48 hours default. No busy-waiting.

### Apply
On `approve` from owner, apply the exact approved change. If the owner modified
the proposal, use the approved version, not the original.

### Verify
Run the relevant gate to confirm the change is correct: JSON syntax, hook
reference resolution, `validate-runtime --runtime all`, `aspis doctor`.

---

## Common flows

*The 10 most frequent request patterns — how the project-lead routes and
orchestrates each end-to-end.*

### 1. feature-plan
**Request:** "Plan feature X" or "I have an idea for Y."
**Route:** planning-lead
**Pipeline:** classify → planning-lead (intake → clarify → spec → architecture
→ tasks → plan review) → reviewer (plan review) → project-lead (approve plan)
→ handoff to build-lead or wait.
**Gates:** constitution_check.py, plan_quality_check.py, task_compile.py exit 0.

### 2. feature-build
**Request:** "Build feature X" (plan already approved).
**Route:** build-lead
**Pipeline:** build-lead (verify plan → orchestrate builders → per-task review
→ gate sweep) → committer (commit each task) → project-lead (BUILD_REPORT).
**Gates:** pytest, ruff, validate-runtime, validate-index, byte-parity, doctor.

### 3. bug-fix
**Request:** "Fix the bug where..." or "Test Y is failing."
**Route:** fix-lead
**Pipeline:** fix-lead (reproduce → diagnose root cause → apply minimal fix →
verify no regression) → reviewer (verify fix) → committer (commit).
**Gates:** The failing test now passes; full suite doesn't regress.

### 4. research-question
**Request:** "What version of X supports Y?" or "Is Z compatible with W?"
**Route:** research-lead
**Pipeline:** research-lead (search cache first → if stale, fetch → rank sources
→ cross-ref → package as reference asset).
**Gates:** Staleness check passes; sources ranked T1-T6; cross-ref agreement.

### 5. status-report
**Request:** "What's the status?" or "Where are we on feature X?"
**Route:** project-lead (self) — no delegation.
**Pipeline:** project-lead reads CURRENT_STATE, RECENT_CHANGES, TASKS.md,
active gate reports, handover notes → assembles status summary.
**Gates:** None. This is read-only.

### 6. mode-change
**Request:** "Switch to production mode" or "This is vibe-mode only."
**Route:** system-lead
**Pipeline:** system-lead (validate mode string → check ceilings → apply to
active feature → update modes.yaml if permanent → signal mode change to any
active leads).
**Gates:** mode_validator.py exits 0; active_feature.json updated.

### 7. system-change
**Request:** "Update the export script" or "Add a new skill to the catalog."
**Route:** system-lead
**Pipeline:** system-lead (assess change → if protected path, file R-008 →
apply change → export → validate-runtime → byte-parity).
**Gates:** validate-runtime, byte-parity, validate-index, doctor.

### 8. emergency-rollback
**Request:** "Revert the last change — it broke everything."
**Route:** fix-lead + system-lead (joint)
**Pipeline:** fix-lead (identify breaking commit, confirm regression) →
system-lead (execute revert, verify gates) → project-lead (confirm system
healthy).
**Gates:** All pre-regression gates pass again; no new failures introduced.

### 9. unknown-request
**Request:** Something that doesn't fit any known track.
**Route:** project-lead (self) — handle directly.
**Pipeline:** project-lead asks one clarifying question → classifies → if still
unknown, presents the user with the closest 2-3 interpretations → on
resolution, routes per the classified track.
**Gates:** Classification must be explicit before any work starts.

### 10. stuck-agent
**Request:** "The build-lead has been spinning for 20 minutes" or implicit
(timeout detected by project-lead).
**Route:** project-lead (self) — intervene directly.
**Pipeline:** project-lead diagnoses the stuck state (step 54) → unsticks with
clarified instructions or kills and reassigns → if the task is mid-execution,
determines whether to resume or restart → documents the incident.
**Gates:** Agent resumes forward progress within 1× the task window.

---

## Output template

*What every orchestration step produces — the project-lead's artifact format.*

For each lead dispatch and result, record:

```
### Orchestration entry — <timestamp>

- **Request ID**: <auto-incremented, e.g. REQ-042>
- **Intent**: <feature-plan | feature-build | bug-fix | research-question |
  status-report | mode-change | system-change | emergency-rollback |
  unknown-request | stuck-agent>
- **Mode**: <vibe | mvp | production>
- **Lead assigned**: <planning-lead | build-lead | reviewer | system-lead |
  fix-lead | research-lead | test-lead | project-lead (self)>
- **Context packet**: <summary of what was handed off (not the full packet)>
- **Dispatched at**: <timestamp>
- **Expected response by**: <timestamp>
- **Actual response at**: <timestamp>
- **Result**: <completed | blocked | failed | stuck | misrouted>
- **Artifacts produced**: <file paths>
- **Gate results**: <pass | fail | waived — with evidence ref>
- **Next action**: <next step, next lead, or "feature complete — session close">
```

This entry is appended to the session log for tracking. The session log is
informal — it's for the project-lead's own continuity, not for the permanent
record (that's what BUILD_REPORT and gate reports are for).

---

## Stop-and-ask index

*Quick-reference list of all 13 stop-and-ask conditions — where the
project-lead MUST pause and ask the user before proceeding.*

| # | Location | Trigger | Question |
|---|----------|---------|----------|
| 1 | Step 5 | aspis preflight fails | "Resolve this blocker before we proceed." |
| 2 | Step 11 | Cannot classify request | "Which direction is closer?" |
| 3 | Step 13 | No lead matches request | "Options: handle manually, defer, or scope new feature." |
| 4 | Step 16 | Lead cannot handle request | "Options: adjust request, handle manually, or scope extension." |
| 5 | Step 20 | State changed significantly | "Options: continue, replan, or abort and restart." |
| 6 | Step 29 | pytest fails non-trivially | "Options: fix, waive, or mark env-blocked." |
| 7 | Step 35 | Gate fails beyond scope | "Options: file bug, pause feature, or handle manually." |
| 8 | Step 39 | Governance request filed | "R-008 requires your approval. Pausing this work." |
| 9 | Step 44 | Owner denies governance | "Options: revise, abandon, or escalate." |
| 10 | Step 44 (nested) | Denied but critical | "Options: override, find alternative, or pause feature." |
| 11 | Step 49 | Architecture issue found | "Options: replan, rebut, or accept risk." |
| 12 | Step 54 | Agent stuck, can't recover | "Options: reassign, handle manually, or give hint." |
| 13 | Step 59 | Persistent failure blocks feature | "Options: descope, handle manually, or defer feature." |
