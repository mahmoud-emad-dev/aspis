# F-014 — System Hardening: Determinism, Permissions, Context, Prestart

**Status:** brief (pre-plan) · **Branch:** `feat/F-014-system-hardening` (off F-013)
**Sources:** current ASPIS catalog · old ASPS `.claude` assets · `demo_win2` repo state ·
3 live OpenCode session transcripts (`ses_10fc` project-lead, `ses_10fa` build-lead, the
planning-lead run). **Date:** 2026-06-22.

---

## 0. The one core problem

> **ASPIS works by asking agents to *choose* to follow prose. The deterministic substrate
> that would make the right behaviour automatic and the wrong behaviour impossible —
> permissions, prestart gates, context tools, runtime hooks — is incomplete or, in places,
> contradicts the prose.**

Every finding below is an instance of this. The architecture and the agent *reasoning* are
sound; we proved that in the transcripts. What fails is everywhere a guarantee depends on an
agent remembering, or where a machine rule (a permission allowlist) silently overrides the
instruction we wrote. This is the constitution's own lesson — *machine-checked invariants
hold, prose-asserted ones rot* — turned back on us.

The fix is not "write better prose." It is **move each load-bearing guarantee down one layer**:
from instruction → to a tool/script the agent runs → to a permission/hook that makes the
wrong path impossible. F-014 does that, agent by agent, skill by skill.

---

## 1. Consolidated evidence

| # | Finding | Source | Layer it belongs to |
|---|---|---|---|
| E1 | **Committer's permission allowlist forbids `aspis commit`** but allows raw `git add`/`git commit`. It was *instructed* to use `aspis commit`, physically couldn't, fell back to raw git. | `ses_10fa` L7456, L8555; `committer.md` perms | **Permissions (L4)** — root cause |
| E2 | Raw-git fallback left **`COMMIT_MSG_TMP.txt`** junk at repo root. | demo tree; `ses_10fa` L7456 | consequence of E1 |
| E3 | Raw `git add <dir>` **over-staged unrelated files** into commit `ee3bd6a` (T-09 swept in AI-test files). `aspis commit <paths>` stages exact paths. | `ses_10fa` L6514-6525 | consequence of E1 |
| E4 | Committer **trapped** — tried `git reset` to recover, not in allowlist, **escalated to human** mid-build. | `ses_10fa` L6814 | Permissions (L4) |
| E5 | **Inconsistent commit messages** — two scope grammars (`feat(F-001/T-13)` vs `feat(F-001): … (T-15)`) because messages were hand-typed and echoed through raw git, no normalizer. | demo git log | consequence of E1 + missing guard (L5) |
| E6 | **Planning-phase output never committed** — Project-Lead saw `.aspis/features/…` + `.aspis/current/` untracked **5×**, narrated it, never routed to committer. No owner / no commit step for plan artifacts. | `ses_10fc` L258,2574,4391,4782,5108 | Missing prestart/finish gate (L5) + role gap |
| E7 | **`commit: deny` on leads is theatre on OpenCode** — build-lead's denies didn't matter; runtime doesn't enforce per-agent bash denies as hard walls. | `ses_10fa` (committed despite deny) | Permissions semantics (L4) + need runtime hooks (L5) |
| E8 | **No enforced clean-tree start** — agents *observe* a dirty tree (`clean-tree-precondition` is prose) and proceed anyway. | `ses_10fc` L305; `ses_10fa` L161 | Prestart skill (L1) |
| E9 | **Context loaded by raw dumps** — Project-Lead ran bare `git diff`, pulled ~1000 lines of unrelated agent-file changes into context, couldn't tell they weren't its own. | `ses_10fc` L3242 | Context skill (L1/L6) |
| E10 | **Context can be stale** — brain (CURRENT_STATE/REGISTRY/CODE_MAP) only refreshes on post-commit; between commits agents may read stale state unless they manually run `update.py`. | `project-awareness`, demo | Context tool (L6) |
| E11 | **Context discipline regressed from ASPS** — ASPS had a crisp numbered ladder (`asps-context-navigation` L1-L4 + "stop when enough / ask before deeper") and dedicated `context-feeder`/`context-summarizer`. ASPIS softened this into `project-awareness` with no explicit levels. | ASPS vs ASPIS skills | Context skill (L1) |
| E12 | **Orchestrator does mechanical work** — Project-Lead ran `task_compile.py`, `update.py` itself instead of it being a silent tool/hook. | `ses_10fc` L1798,4665 | Tools-for-scope (L6) |
| E13 | **Opaque mega-turns** — build-lead ran all 16 tasks in one 7316s (2h) turn; no incremental checkpoint surfaced to PL; a late failure would lose hours of un-checkpointed context. | `ses_10fc` L4964; `ses_10fa` durations | Loop design (L2) |
| E14 | **Missing system-side agents/skills** — no specialist for "change models via the right `aspis` command", no system-repair dispatcher, no single gated path for adding skills/workflows/scripts (must go only through system-lead). | catalog gap | Missing agents (L7) |

**What was NOT broken (proven, so we don't touch it):** request classification, lead routing,
context packaging, the builder→reviewer→committer cycle, review gating, and the committer's own
reasoning (it correctly *noticed* the over-stage and tried to stop). The system's skeleton is good.

---

## 2. The seven levels (the work structure)

These are your 7 points, restated as the F-014 work breakdown, each mapped to a concrete
deterministic mechanism and to the abstraction rules in `.aspis/rules/architecture-constitution.md`
(new capability = new file; cheapest mechanism first: script → tool → hook → agent; every guarantee
machine-checked, not asserted).

### L1 — Prestart skill + per-agent context skill (the agent's first two moves)
Every agent's instructions open with **two cheap, mechanical moves, not thinking**:
1. **Prestart checks** — a *small, direct* skill that tells the agent to run one script
   (`aspis preflight` / a scoped check) which: verifies clean tree, branch/pointer match, and
   **any open findings**; on a problem it **triggers a resolver** (fixer script/agent) or routes
   to a specialist — the agent does not improvise. Lowest tokens: the skill is ~10 lines + one command.
2. **Get-correct-context** — how *this* agent gets exactly the context it needs, lowest tokens.
   - Heavy roles (project-lead, the leads) get a **specialized context skill** (port the ASPS
     numbered ladder: L1 always → L4 only-the-files-the-task-touches, "stop when enough").
   - Light subagents get **a few lines of rule** inline (no skill), or a **tool that returns
     scoped context** (e.g. a command that runs `update.py` first, then reads its scope/variables
     from a file). Context is **dynamic per agent's real need**, driven by a script/var, not a wall of prose.

### L2 — Start from the first loop / subsystem
Map the **build loop and each subsystem** end to end; for each agent define its **one main role**
and the subsystems it touches. Instructions point in the correct direction only. Includes a focused
pass on **prompt-engineering the agents** — how to give smart scoped context and make them follow
rules by ID, not restate them. (Addresses E13 loop opacity: define checkpoint/commit cadence so a
lead never runs a 2-hour opaque turn.)

### L3 — Minimal model per agent
For each agent, determine the **lowest-capability model** that still performs its role **given the
new instructions/tools/permissions** — and verify it actually works without degrading flow or
hygiene. Rule: **if anything breaks, it is fixed in the very next step — no broken state is carried
forward.** (This is also a forcing function: the more deterministic the tools, the cheaper the model
that suffices.)

### L4 — Correct per-agent settings (permissions · skills · subagents · tools)
For every agent, make **permissions match its role exactly** so it can do its job and *cannot* do
the wrong thing. **E1 is the canonical bug:** committer must `allow aspis commit*` and **lose** raw
`git add*`/`git commit*` footguns. Audit all 12 agents the same way — every "told to do X but
permission blocks X" gap (which happened repeatedly) gets closed. Also right-size skills/subagents/tools per agent.

### L5 — Deterministic validation guards + first-level runtime hooks
- **Deterministic checks** that detect a wrong state and **emit a finding** (or trigger a fixer
  script/agent), so the *next* agent's prestart skill (L1) finds it and resolves it before starting,
  or routes it to a specialist to review+fix. (Fixes E5, E6 normalization.)
- **Runtime-tool hooks**, not only git hooks. Today we lean almost entirely on git hooks, but most
  action is in **runtime tool calls**. OpenCode/Claude expose 30+ hook events; use a *few* smartly
  for continuous validation, context refresh, and first-level blocking of specific events. (Fixes E7:
  enforcement that git-deny can't give us on OpenCode.)

### L6 — Tools agents run for their own scope
Agents run **tools that maintain their own preconditions** — e.g. context may be stale because no
commit happened yet (E10), so the agent calls a script that **auto-refreshes context** before reading
it. Mechanical bookkeeping (E12) moves out of the orchestrator into silent tools.

### L7 — Missing agents & skills
Add the specialists we lack (E14):
- a **model-change** specialist that edits models **only via the correct `aspis` command** (not raw
  file edits) when a workflow needs it;
- a **system-repair / fixer** path for when the system itself breaks;
- the rule that **all** system customization (new skill / workflow / script / config) flows **only
  through `system-lead` and its subagents** — one gated authority.

---

## 3. F-014 scope & sequencing

**Goal:** before public publish, **revise and verify every agent, skill, tool, and template** so the
load-bearing guarantees are deterministic, permissions are correct, and context is scoped + cheap.

**Sequencing (one thing at a time, each shippable + gate-green before the next):**

1. **P0 — E1 fix (smallest, highest leverage):** give `committer` `aspis commit*` in its allowlist,
   drop raw `git add/commit` footguns; verify `aspis` is on PATH in the runtime shell. Re-run `demo_win2`.
   *This one change kills E2–E5.*
2. **P1 — L4 permission audit** across all 12 agents (role ↔ permission ↔ tools ↔ subagents).
3. **P2 — L1 prestart + context skills** (port ASPS ladder; add `aspis preflight`; per-agent context contract).
4. **P3 — L5 guards + first runtime hooks** (findings emitter; pick the few OpenCode/Claude hook events).
5. **P4 — L6 context-freshness tools** (auto-refresh before read; move bookkeeping off the orchestrator).
6. **P5 — L2 loop/subsystem map + prompt-engineering pass** (checkpoint cadence; kill mega-turns).
7. **P6 — L7 missing specialists** (model-change agent; system-repair; system-lead-only customization gate).
8. **P7 — L3 minimal-model assignment + full re-verification** of every agent/skill/tool/template before publish.

**Order rationale:** permissions and prestart (P0-P2) must exist before we can trust a smaller model
(P3-L3 last). Determinism first, then let each agent do its exact role on the cheapest model that holds.

---

## 4. Branch / merge plan

- `feat/F-014-system-hardening` branched **off F-013** (carries F-013's commits; reversible).
- **F-013 → main:** validate gate green, then merge (pending explicit go — see open question).
- Each P-step above lands as its own scoped commit on F-014, gate-green on Windows (gate of record).

## 5. Open question (needs your call)

**Merge `feat/F-013-install-ux` into `main` now** (then rebase F-014 on main), or **keep F-013
unmerged** and let F-014 stack on top until the whole hardening pass is done and we merge once?
`main` is the publish-facing branch, so this is your decision.
