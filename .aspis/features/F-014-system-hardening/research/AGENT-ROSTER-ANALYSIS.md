# F-014 — Agent roster analysis

A per-agent review: does each agent have the right **skills · delegates · permissions · tools** for
its role, and does it use the **subsystems** (prestart, context, findings, commit, config) correctly?
Verdicts as of the F-014 hardening. ✅ = right for its role · ⚠ = note · ❌ = gap (fixed below).

## L1 — Project Lead
- **Role:** the only primary; project intelligence + router. **Model:** deep.
- **Tools:** read/grep/glob/bash (read-only git + `aspis status/context/bootstrap --check`). No edit/write — it routes, never builds. ✅
- **Skills:** project-awareness, **context-ladder**, request-classification, lead-routing, context-packaging, project-question-answering, project-guidance. ✅ (covers classify → route → answer)
- **Delegates:** all 8 leads + project-explorer. ✅ (can reach every role)
- **Subsystems:** reads context via the ladder + `aspis context`; routes findings surfaced at session start to fix-lead. ⚠ can't *inspect* findings itself (`aspis findings` not in its allowlist) — minor; it routes, doesn't resolve.

## L2 — Leads
### planning-lead — idea → plan (deep)
- Skills: prestart-checks, context-ladder, planning-intake, requirement-clarification, feature-planning, architecture-planning, task-decomposition. ✅
- Permissions: git read, `aspis preflight/findings/context`, python context+planning. ✅
- Delegates: ~~reviewer, project-explorer~~ → **+ research-lead (FIXED).** ❌→✅ It is told to "request research from the Research Lead" but research-lead was **not** a delegate — the delegation-layer analog of the committer bug.
- Subsystems: preflight before planning; context-ladder; planning scripts (feature_scaffold/task_compile/prereq_validate). ✅

### build-lead — plan → software (deep)
- Skills: prestart-checks, context-ladder, build-readiness, task-orchestration, scope-control, selective-testing. ✅
- Permissions: git read, `aspis preflight/findings/context/artifact`, python context+planning, commit/push **deny**. ✅
- Delegates: general-builder, reviewer, test-lead, fix-lead, committer, project-explorer. ✅ (full build cycle)
- Subsystems: preflight → delegate → review/test → committer; **checkpoints per task** (no opaque mega-turn). ✅

### reviewer — independent verdict (deep)
- Skills: context-ladder, review-strategy, quality-review, acceptance-decision, plan-critic. ✅
- Permissions: git read, `aspis artifact/context`, python context+planning, commit/push deny. **Read-only on product.** ✅
- Delegates: project-explorer. ✅
- Subsystems: reads only the diff/acceptance via the ladder; stamps the artifact report; **withholds a verdict without evidence** (escalate rule). ✅

### fix-lead — defect → repair (deep)
- Skills: prestart-checks, context-ladder, root-cause-analysis, corrective-fix, scope-control, selective-testing. ✅
- Permissions: `*: allow` (needs broad bash to reproduce), commit/push deny. ✅
- Delegates: reviewer, committer, project-explorer. ⚠ tests fixes itself (selective-testing) rather than delegating test-lead — fine for now; add test-lead if the work repeats.
- Subsystems: preflight; reproduce→cause→fix→verify; routes the commit to the committer. ✅

### test-lead — objective evidence (standard)
- Skills: test-generation, test-execution. ✅ Permissions: `*: allow` (runs the suite), commit/push deny. ✅
- Delegates: project-explorer. ✅ (mentions the Reviewer as the *consumer* of its evidence, not a delegate — no gap.)
- ⚠ has no prestart-checks/context-ladder skill — acceptable (it validates a given target), but could read context via the ladder for richer tests later.

### research-lead — external knowledge (deep)
- Skills: context-ladder, knowledge-research, knowledge-packaging. Tools: read/grep/glob/write/**webfetch/websearch**, **no bash**. ✅ for a web-research role.
- Delegates: none. ✅ Subsystems: reads L1 via the read tool (ladder's bash steps are optional for it — treated as read-only). ✅

### system-lead — the ASPIS machine + config (deep)
- Skills: prestart-checks, system-awareness, deterministic-first, asset-authoring, system-validation, system-repair, **config-management**. ✅
- Permissions: `*: allow` (+ webfetch), commit/push deny. ✅ Delegates: project-explorer. ⚠ does authoring/repair/config itself — a dedicated **config/author sub-agent** is the natural next extraction once that work repeats (per its own "extract when justified" rule).
- Subsystems: owns config changes via `aspis` commands (models/mode/policy/stack); R-008 changes confirm with the user. ✅

### bootstrap — one-time onboarding (standard, primary, export-only)
- Skills: prestart-checks (exempt), project-onboarding. Permissions: `aspis *`, git read, python context. ✅ Self-deletes after. ✅

## L3 — Workers
- **general-builder** (cheap): implements one packet; `*: allow`, commit/push deny; no skills (inline rules incl. preflight + scope + stop-and-report). ✅ right for a disposable worker.
- **committer** (cheap): the only commit authority; `aspis commit` primary + guarded raw-git fallback; skills commit-message/commit-splitting/clean-tree-precondition. ✅ (P0 fix)
- **project-explorer** (cheap): read-only context helper; python-context only; returns a "not found" rather than a guess. ✅

## Findings & recommendations
1. **❌→✅ planning-lead → research-lead delegation** — fixed (added to `delegates`). This is a *new gap class*: an agent told to delegate to an agent not in its `delegates` list. The golden test checks commands, **not** delegations.
2. **Recommendation (follow-up):** a machine-check that every `delegates` entry is a real agent (catch dangling/typo delegates) — safe to add; the "told-to-delegate but not listed" direction is fuzzier (e.g. test-lead *names* the Reviewer without delegating to it) and is better caught by review.
3. **Minor:** give project-lead `aspis findings` if we want the router to inspect (not just route) findings.
4. **Future extraction (when repeats):** a system **config/author sub-agent** under system-lead; **test-lead** as a fix-lead delegate.
5. **Tiers look right:** deep for judgement (project/planning/build/fix/reviewer/research/system), standard for test-lead/bootstrap, cheap for the disposable workers (general-builder/committer/project-explorer) — to be re-validated with real-usage data (the deferred model-bands work, P7).
