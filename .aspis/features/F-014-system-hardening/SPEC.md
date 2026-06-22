# F-014 — System Hardening · Specification

> Mode: **production**. Pre-publish hardening. The agent/skill architecture is sound (proven
> in live transcripts); this feature makes its load-bearing guarantees **deterministic and
> machine-enforced** instead of prose-asserted, fixes **permission/role mismatches**, and makes
> **context loading scoped and cheap** — agent by agent, without breaking anything that already
> works. Evidence + research: `research/FINDINGS-AND-SCOPE.md` and `research/RESEARCH-AND-DECISIONS.md`
> (read those first).

## Goal
Make the right agent behaviour **automatic** and the wrong behaviour **impossible**, by moving each
load-bearing guarantee down one layer — instruction → tool/script → permission/hook. This restores
two system rules the `demo_win2` run violated, **as machine-checked invariants**:
- **R-004 (one writer):** only the committer commits; no agent commits its own work.
- **R-003 (deterministic-first):** the cheapest mechanism that works — script → tool → hook → agent.

External best-practice states the same principle: *"scope is enforced by architecture, not just by
instruction."* Concretely, F-014 delivers: a cheap deterministic **prestart check** + a **scoped
context** move at the start of each agent; **per-agent permissions that exactly match the role**;
**deterministic guards** (git *and* a few runtime-tool hook events) that emit findings the next agent
resolves; one **gated path** for system/config changes; and each agent on the **right model band**.

## Guiding principles (how we change the system without breaking it)
1. **Additive & non-breaking.** Every change preserves existing valid flows and use cases. We improve;
   we do not regress something that already works. If a change would break a valid path, it is wrong.
2. **Balanced, not rigid.** Flows are guidance with judgement, not rails. The system supports **multiple
   valid entry paths** — e.g. a model/config change can come **user → project-lead → system-lead** *or*
   **user → system-lead directly**; both are first-class. Agents keep full context, instructions, and
   delegation latitude so they can handle the real case, not only the happy path.
3. **Whole-picture aware.** A change considers the other subsystems it touches. When a new capability is
   added, we identify **which agents / files / workflows must include it** and update exactly those —
   no more, no less.
4. **One thing at a time.** Each step is scoped, shippable, gate-green on Windows, and reviewed before
   the next. Focus per agent / per skill / per subsystem.
5. **Practical correctness over dogma.** Reduce tokens, but a load-bearing rule lives in the agent body
   if cheaper models fail without it. Real, reliable usage beats satisfying a rule in a way that's bad in
   practice (constitution rules are the means; a working system is the goal).

## Problem
Three live OpenCode sessions building one feature in `demo_win2` showed the system relies on agents
*choosing* to follow prose, and that one machine rule actively contradicted the prose:
- **The committer was told to use `aspis commit` but its allowlist forbids it** (permits raw
  `git add`/`git commit`). OpenCode *enforced* the denial, so it fell back to raw git → junk
  `COMMIT_MSG_TMP.txt`, an **over-staged** commit, a **mid-build human escalation** (no `git reset`
  allowed), and **two commit-message grammars**. One missing allowlist line caused all of it.
- **No one commits the planning phase's output** — the Project-Lead saw it untracked five times and
  never routed it to the committer.
- **Context is loaded by raw dumps** (a bare `git diff` pulled ~1000 unrelated lines in) and can be
  **stale** (brain refreshes only on post-commit). The crisp numbered context ladder ASPS had was softened.
- **Missing gated path** for model / mode / stack / config changes and for system self-repair.

## Scope
In scope (data + catalog + scripts; new files over edits per the constitution; permissions are *assets*,
so editing each agent file directly is correct and not a Cost-of-Change violation):
- **Permissions** — each of the 12 catalog agents (`data/catalog/agents/*.md`): allowlist matches role;
  every `aspis …`/script the agent is told to run is permitted; write footguns removed. (P0 committer first.)
  A single-source role→permission *render* is a **deferred follow-up** (for 50–100+ agents), **not F-014**.
- **Prestart** — an `aspis preflight` script + a small `prestart-checks` skill referenced first by editing
  agents; on a problem it emits a finding / routes, agent doesn't improvise.
- **Context** — a ported numbered **context ladder** skill (just-in-time, progressive disclosure) for heavy
  roles; inline context rules for light subagents; a freshness tool agents call before reading state.
- **Guards + hooks** — a deterministic findings emitter; a few **runtime-tool hook events** added to the
  *existing* OpenCode `scope-guard.ts` + Claude `settings.json` surfaces (capability-checked, data-driven,
  degrade to no-op); fix the `python3` interpreter bug that no-ops the guard on Windows.
- **Gated system changes** — the **system-lead + a config sub-agent** own model/mode/stack/config edits,
  performed **only via `aspis` commands/workflows/skills**, reachable by multiple entry paths (principle 2).
- **Models** — each agent declares a **band** (min floor · max cap · preferred), justified by capability
  scores + instruction-adherence.
- **Tests** for every new behaviour (red→green, R-005); re-verification of every agent/skill/tool/template.

Out of scope:
- New product features for `demo_win2` (it is the test fixture, not the deliverable).
- The single-source permission render (deferred); tracing/self-improvement beyond what guards need.
- Any rules/permission-policy change needing the R-009 human gate ships **only** with explicit approval
  (the user has given blanket approval for F-014's permission/model/hook edits, reported per change).

## Behaviour (acceptance-shaping)
- Re-running the `demo_win2` build → **no junk files, no over-staged commits, one commit grammar, zero
  tooling-caused human escalations** — and **no previously-working flow regresses**.
- Every agent can perform its stated role with its own permissions — **no "told to do X, blocked from X"**.
- An agent on a dirty/again-stale repo **resolves or routes the problem before editing**, deterministically.
- Context is loaded **scoped and fresh**, never as a raw whole-tree dump.
- System/config changes work from **both** entry paths (direct-to-system-lead and via project-lead).

See `research/FINDINGS-AND-SCOPE.md` §2 (seven levels) and `research/RESEARCH-AND-DECISIONS.md` (decisions
+ research) for the basis; `PLAN.md` for the approach; `TASKS.md` for the build-ready packets.
