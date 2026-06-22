# F-014 — System Hardening · Acceptance

The feature is done when **all** of the following hold, each backed by a test or a
reproducible check (machine-checked wherever possible — prose-only acceptance is not enough).

## Root cause closed (P0)
- [ ] `committer.md` allowlist permits `aspis commit*`; raw `git add*`/`git commit*` are no longer the
      sanctioned commit path. (permission test)
- [ ] `aspis` resolves in the runtime shell; `aspis commit` runs in a fresh export. (doctor/check)
- [ ] Re-running the `demo_win2` commit path leaves **no `COMMIT_MSG_TMP.txt`**, stages **exact paths only**,
      and needs **no human escalation**. (reproduction)

## Permissions correct (P1)
- [ ] Golden test: for every agent, each `aspis …`/script command named in its instructions is in its
      allowlist. No "told to do X, blocked from X" gap remains.

## Prestart + context (P2)
- [ ] Every editing agent references `prestart-checks` first; `aspis preflight` detects dirty tree /
      branch-pointer mismatch / open findings and emits-or-routes with a non-zero exit + next action. (tests per path)
- [ ] Heavy roles use the numbered context ladder (stop-when-enough); light subagents have inline rules.
      No agent loads context as a raw whole-tree dump.
- [ ] Context is fresh on read between commits (freshness tool closes the stale-read path). (test)

## Guards + runtime hooks (P3)
- [ ] A detected wrong-state emits a structured finding that the next agent's prestart consumes. (round-trip test)
- [ ] A small, data-driven set of runtime-tool hook events fires in OpenCode/Claude and degrades to no-op when
      the runtime is absent; cross-platform. (test + manual runtime check)

## Loop + specialists (P4–P6)
- [ ] Mechanical bookkeeping runs as silent scoped tools, not by the orchestrator by hand.
- [ ] Leads commit incrementally; sub-agents return distilled summaries — no multi-hour opaque single turn in a re-run.
- [ ] The system config sub-agent edits models/mode/stack/config only via the correct `aspis` commands;
      system-repair path exists; all system customization flows through `system-lead` + sub-agent. (tests/guards)
- [ ] **Non-rigid:** the change path works **user → project-lead → system-lead** *and* **user → system-lead
      directly** — both succeed and neither breaks the other. (test both entry paths)

## Model bands + full re-verification (P7)
- [ ] Each agent declares a band (min floor · max cap · preferred) with recorded rationale — no judgement role
      floored too cheap; no role capped so it wastes a frontier model.
- [ ] Full `demo_win2` re-run on assigned bands is clean, consistent (one commit grammar), and escalation-free.
- [ ] Every agent, skill, tool, and template revised and re-verified for publish.

## Global gates (every task)
- [ ] ruff + mypy + pytest green on Windows (gate of record).
- [ ] No broken state carried forward — each task starts clean and ends clean.
- [ ] **No previously-working flow or valid use case regressed** (additive-change principle; `demo_win2` re-run is the oracle).
- [ ] Each task recorded its **impact map** (files/agents touched and not touched).
- [ ] No R-009 policy/rules change shipped without explicit human approval.
