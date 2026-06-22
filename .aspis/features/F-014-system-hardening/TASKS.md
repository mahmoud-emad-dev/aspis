# F-014 — System Hardening · Tasks

> Build-ready packets, dependency-ordered. `[P]` = parallelizable within its step. Each task:
> names its **impact** (files/agents it must touch and must not), red→green tests, ruff+mypy+pytest
> green on Windows, independent review, committed via the committer. No task starts on a dirty tree;
> no broken state carries forward; **no task may regress a previously-working flow** (re-run `demo_win2`).

## P0 — Committer permission fix (root cause)
- **T-01** Add `aspis commit*` to `committer.md` allowlist; remove raw `git add*`/`git commit*` as the
  commit path (retain read-only git). Impact: `agents/committer.md` only. Acceptance: committer runs
  `aspis commit`; raw add/commit no longer sanctioned.
- **T-02** Fix the runtime-guard interpreter so the hook fires cross-platform (resolve a working python;
  Windows often lacks `python3`). Impact: `runtime-hooks/opencode/scope-guard.ts`,
  `runtime-hooks/claude/settings.json`. Acceptance: scope-guard vetoes an out-of-scope edit on Windows + Linux.
- **T-03** Tests + reproduction: permission test asserts `aspis commit*` ∈ allowlist & footgun removed;
  re-run the `demo_win2` commit path → exact-path staging, no `COMMIT_MSG_TMP.txt`, no escalation. Acceptance: green + clean tree.

## P1 — Per-agent permission/role audit
- **T-04** Build the {role → prescribed commands → allowlist → tools → subagents} table for all 12 agents.
  Impact: an audit note under `research/`. Acceptance: every mismatch identified; existing valid abilities flagged to preserve.
- **T-05** [P] Fix each agent's allowlist to match its role — close every "told to do X, blocked from X";
  tighten footguns without amputating valid delegation. Impact: `agents/*.md`. Acceptance: no agent blocked from a command its instructions name; no valid flow lost.
- **T-06** Golden test: for each agent, every `aspis …`/script command in its instructions ∈ its allowlist.
  Impact: new test. Acceptance: machine-checked; fails if a future edit reintroduces a gap.
  *(Single-source permission render is a deferred follow-up, not a task here.)*

## P2 — Prestart + context
- **T-07** `aspis preflight` script/verb: clean-tree + branch/pointer match + open-findings; emits/routes on
  problem, non-zero exit + next action. Impact: new `scripts/.../preflight.py` + CLI. Acceptance: happy path + each failure path tested.
- **T-08** `prestart-checks` skill (~10 lines + the command); referenced first in every editing agent.
  Impact: new `skills/prestart-checks/SKILL.md`, `agents/*.md`. Acceptance: present + referenced; agent doesn't improvise on a problem.
- **T-09** Context-ladder skill (port ASPS `asps-context-navigation`: L1→L4, stop-when-enough; just-in-time
  + progressive disclosure) for heavy roles; inline context rules for light subagents. Impact: new
  `skills/context-ladder/SKILL.md`, `agents/*.md`. Acceptance: heavy roles reference it; no raw-dump context.
- **T-10** Context-freshness tool: wrapper that runs `update.py` then returns scoped context; agents call it
  before reading state. Impact: `scripts/context/`. Acceptance: stale-read path closed, tested.

## P3 — Guards + runtime hooks
- **T-11** Deterministic findings emitter: structured finding on detected wrong-state, consumed by preflight (T-07).
  Impact: new `scripts/.../findings.py` + a findings store path. Acceptance: emit→consume round-trips, tested.
- **T-12** Add a small, capability-checked, data-driven runtime-hook event set to the *existing* surfaces
  (session-start → preflight; tool event → context-refresh; first-level block where git hooks can't reach).
  Impact: `runtime-hooks/opencode/scope-guard.ts`, `runtime-hooks/claude/settings.json`, `config/policy/hooks.yaml`.
  Acceptance: events fire in the runtime; absent runtime/event = no-op; cross-platform. *(Needs the hook-surface research — see open item.)*

## P4 — Bookkeeping tools off the orchestrator
- **T-13** Move compile/brain-refresh bookkeeping into silent scoped tools the agent invokes; thin the
  orchestrator's instructions. Impact: orchestrator agent bodies + small wrappers. Acceptance: orchestrator no longer runs mechanical scripts by hand.

## P5 — Loop / subsystem map + prompt pass
- **T-14** Document the build loop + each subsystem + per-agent role/touched-subsystems **+ valid entry paths**.
  Impact: a map doc under `research/`. Acceptance: every agent's role + entry paths captured.
- **T-15** Checkpoint/commit cadence: leads commit incrementally; sub-agents return distilled ~1–2k-token
  summaries; no multi-hour opaque turn. Impact: lead agents + build workflow. Acceptance: cadence stated + a guard/finding for over-long single turns where feasible.
- **T-16** [P] Prompt-engineering pass per agent: "right altitude" (minimal≠short, load-bearing rules in body,
  canonical examples, decision-trees for routing), weak-model-robust + stop-and-escalate. Impact: `agents/*.md`. Acceptance: each agent reviewed; no valid behaviour lost.

## P6 — Gated system-change path + specialists
- **T-17** System config sub-agent + a model-change skill that edits models **only via `aspis` commands**
  (valid ids → sync → render → apply). Impact: new agent + skill; `system-lead` wiring. Acceptance: model change works end-to-end via the command path, not file edits.
- **T-18** Reachability/non-rigid: the path works **user → project-lead → system-lead** *and* **user →
  system-lead directly** (project-lead may handle simple cases). Impact: `project-lead`, `system-lead` bodies.
  Acceptance: both entry paths delegate correctly; neither breaks the other.
- **T-19** [P] Grow the sub-agent's skills: mode-change, stack-change, config edits (e.g. add a secret regex),
  and a **system-repair** skill wired to findings (T-11). Impact: new skills. Acceptance: each change-type works via commands; out-of-gate direct edits are flagged.

## P7 — Model bands + full re-verification
- **T-20** Assign each agent a band (min floor · max cap · preferred) from capability scores + instruction-
  adherence; record rationale. Impact: `agent-models.yaml`/catalog. Acceptance: every agent has a justified band; no judgement role floored too cheap, no role capped to waste a frontier model.
- **T-21** Full re-verification: re-run `demo_win2` end-to-end on assigned bands → clean, consistent, no
  escalations, **no regressed flow**; revise+re-verify every agent/skill/tool/template. Acceptance: ACCEPTANCE.md all met.

## Sequencing & cross-cutting notes
- P0 → P1 first (substrate). P2–P4 build on correct permissions. P3 (T-12) needs the OpenCode/Claude hook-event
  research before it can be fully specced. P6 is non-rigid by design (multiple entry paths). P7 last (smaller
  models only after determinism).
- Every task records its **impact map** and confirms **no previously-working flow regressed**.
- R-008: permission/model/hook edits are blanket-approved for F-014 and reported per change; any `rules/` or
  policy-semantics edit pauses for explicit human approval.
