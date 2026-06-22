# F-014 — System Hardening · Plan

> Approach for the SPEC. Determinism-first: build the substrate (permissions, prestart, guards)
> before trusting smaller models. Each P-step is independently shippable and gate-green on Windows
> before the next. New capability arrives as **new files**; we edit an agent/asset only to wire it.
> Every step honours the SPEC's guiding principles — **additive, balanced/non-rigid, whole-picture,
> one-at-a-time, practically correct**.

## Architecture principles in play
- **One guarantee, one mechanism, machine-checked.** Each load-bearing behaviour gets a
  script/tool/hook/permission that makes it automatic — prose only *names* the mechanism.
- **Cheapest mechanism first:** script → tool → hook → agent (R-003). A prestart check is a script.
- **Permissions are a contract** *and* an asset: an agent's allowlist permits exactly its role's commands
  (every `aspis …` it is told to run) and excludes write footguns it should not use. Edited per-agent now;
  single-source render deferred to scale.
- **Context is retrieved, scoped, fresh** — just-in-time, progressive disclosure, by reference; never dumped.
- **Findings flow forward:** a guard detects → emits a finding → the next agent's prestart resolves/routes it.
- **Flexibility is designed in:** flows support multiple valid entry paths; agents keep delegation latitude.
  We never harden a path so tightly that another valid use case breaks.

## Per-step "impact map" discipline
Because the system is growing, each step **first names the agents/files/workflows it must touch** (and the
ones it must *not*), then changes exactly those. This keeps changes additive and reviewable, and is recorded
in the step's task notes.

## The eight steps

### P0 — Committer permission fix (root cause; smallest)
Impact: `data/catalog/agents/committer.md`; both runtime-hook files (interpreter bug).
- Add `"aspis commit*": allow`; remove raw `"git add*"`/`"git commit*"` (read-only git stays). `aspis commit`
  stages/commits inside its own process, so no raw write verbs are needed.
- Fix the `python3` interpreter in `runtime-hooks/opencode/scope-guard.ts` + `runtime-hooks/claude/settings.json`
  (resolve a working interpreter; Windows often lacks `python3`) so the scope-guard actually fires.
- **Test:** committer can invoke `aspis commit`; permission test asserts the allowlist; re-run the `demo_win2`
  commit path → exact-path staging, no temp file, no escalation.

### P1 — Per-agent permission/role audit (L4)
Impact: all 12 `agents/*.md`; one new golden test.
- Build the {role → prescribed commands → allowlist → tools → subagents} table; close every mismatch.
- **Golden test:** for each agent, every `aspis …`/script named in its instructions ∈ its allowlist
  (machine-checked, so the bug class can't rot back in).
- Preserve each agent's existing valid abilities — tighten footguns, don't amputate working delegation.

### P2 — Prestart + context skills (L1, L6)
Impact: new `scripts/.../preflight.py` + CLI verb; new `skills/prestart-checks`, `skills/context-ladder`;
edited agent bodies (reference the skills); `scripts/context/` freshness wrapper.
- `aspis preflight`: clean-tree + branch/pointer match + open-findings; emits/routes on problem, non-zero
  exit + next action. Referenced **first** by editing agents via a ~10-line `prestart-checks` skill.
- **Context-ladder** skill (port ASPS `asps-context-navigation`: L1 always → L4 task-files-only, stop-when-
  enough; just-in-time + progressive disclosure) for heavy roles; **inline rules** for light subagents.
- Freshness tool: run `update.py` then return scoped context, so reads aren't stale between commits.

### P3 — Deterministic guards + a few runtime hook events (L5)
Impact: new findings emitter script; `runtime-hooks/opencode/scope-guard.ts`, `runtime-hooks/claude/settings.json`,
`config/policy/hooks.yaml`.
- **Findings emitter** (deterministic): structured finding on detected wrong-state, consumed by P2 preflight.
- **Extend the existing two hook surfaces** with a *small*, capability-checked, data-driven event set:
  e.g. session-start → preflight/clean-tree; a tool event → context-refresh; first-level block where git
  hooks can't reach. Degrade to no-op when the runtime/event is absent (capability check, not `if runtime==`).

### P4 — Context-freshness + bookkeeping tools (L6)
Impact: orchestrator agent bodies; small context/compile tool wrappers.
- Move mechanical work (compile, brain-refresh) out of the orchestrator into silent tools the agent invokes.

### P5 — Loop / subsystem map + prompt-engineering pass (L2)
Impact: a map doc; lead agent bodies + build workflow; all agent bodies (light pass).
- Document the build loop + each subsystem; per agent, its one main role + touched subsystems + valid entry paths.
- **Checkpoint/commit cadence** so a lead never runs a multi-hour opaque turn; sub-agents return distilled
  ~1–2k-token summaries (context isolation), not raw transcripts.
- Prompt pass: "right altitude" instructions (minimal ≠ short; load-bearing rules in the body; canonical
  examples; decision-trees for routing), market-standard, weak-model-robust with a stop-and-escalate path.

### P6 — Gated system-change path + missing specialists (L7)
Impact: `system-lead` agent; a new **config sub-agent** + its skills; relevant workflows/commands.
- The system-lead and a **config sub-agent** own model/mode/stack/config edits, performed **only via `aspis`
  commands/workflows/skills** (never direct agent-file edits). Skills grow over time: model-change (valid ids
  → sync → render → apply), mode-change, stack-change, config edits (e.g. add a secret regex), system-repair.
- **Non-rigid by design:** reachable **user → project-lead → system-lead** *and* **user → system-lead directly**
  (and project-lead may answer simple cases itself). The skill encodes *how to change safely*, not a single rail.

### P7 — Model bands + full re-verification (L3)
Impact: `agent-models.yaml`/catalog model declarations; all agents (verification); `demo_win2` re-run.
- Each agent declares a **band**: min floor · max cap · preferred — from capability scores + whether our
  instructions make that model comply. Deterministic roles may floor cheap (with examples); judgement roles
  (project-lead, planning/build leads) floor higher; cap to avoid wasting frontier models. R-007/R-008 aligned.
- Full re-verification of every agent/skill/tool/template; re-run `demo_win2` clean on assigned bands.

## Risks & mitigations
- **Breaking a valid flow** — the top risk per your principle. Mitigation: the per-step impact map + the
  "additive, don't regress" review check + `demo_win2` re-run as the regression oracle.
- **R-008 gate** — permission/model/hook/policy changes are human-gated; blanket-approved for F-014, reported
  per change; any *rules/* or policy-semantics edit still pauses for explicit approval.
- **Runtime-hook portability** — keep the event set small, data-driven, capability-checked, no-op when absent.
- **Smaller-model regressions** — P7 last; fix in-step, never carry a regression forward.

## Review & testing strategy
- Each P-step: red→green tests (R-005), ruff+mypy+pytest green on Windows, independent review before commit.
- The committer (P0) + the permission golden test (P1) are the backstops that keep the rest honest.
- Definition of done: `demo_win2` re-run is clean *and* no prior working flow regressed; every machine-checkable
  guarantee has a test.
