# F-014 — Research & Decisions (pre-plan)

> The "plan what we actually need" step before refining SPEC/PLAN/TASKS. Combines:
> (A) the user's decisions on the open questions, (B) internal code research, (C) market
> research (mid-2026 best practice). Nothing here is committed; it drives edits to the
> planning docs. Checked against `.aspis/rules/architecture-constitution.md` + `system-rules.md`.

---

## A. Decisions (from the user, locked)

1. **Permissions edited per-agent, in the catalog, now.** The constitution's
   Cost-of-Change/Single-Source rule governs **core code**, not **asset files**. Agent
   permission blocks are assets — editing all 12 directly is correct and *not* a violation.
   A single-source role→permission **render** mechanism is a **later** feature (for 50–100+
   agents, managed by role-category). **Not now.**
2. **R-008 path is the design, not just a gate.** Blanket approval for F-014, *but* all
   config/model/permission/mode/stack changes must flow **user → project-lead → system-lead →
   a system "config" sub-agent**, which acts **only through provided `aspis` commands/
   workflows/skills** — never by editing agent files directly. Model changes go through the
   models commands (valid ids → sync → render → apply), guided by a skill. That sub-agent
   grows skills over time (model-change, mode-change, stack-change, config edits like adding a
   secret regex, system-repair). This *is* L7/P6.
3. **Instruction philosophy: practical correctness > dogmatic minimization.** Reduce tokens,
   but **put a load-bearing rule in the agent body if cheaper models fail without it.** Write
   complete, market-standard agent prompts (mid-2026). Agents ~15–50 lines as the role needs;
   skills ~10–50 lines, split when a real case warrants. Never so terse the agent skips a skill
   or misses a critical rule. **Real usage wins over satisfying a rule in a way that's bad in practice.**
4. **Models get a band per agent: min floor · max cap · preferred.** Derived from capability
   scores + whether our instructions can make that model comply. Never a model so cheap it
   breaks the rules; never an expensive model where it's wasted (heavy instructions would just
   slow a frontier model). E.g. project-lead and the important leads get a floor that excludes
   the cheapest models; some agents are capped so they never burn a frontier model. Per agent.

---

## B. Internal research (code-confirmed)

### B1. The P0 fix location is exact
`runtimes/opencode.py::_permission()` renders the catalog agent's `permissions.bash` **verbatim**
into the agent's permission block, with an implicit `*: deny`. The committer's bash map lists
`git add*` / `git commit*` but **not** `aspis commit*` → OpenCode denied `aspis commit`.
**OpenCode *does* enforce the allowlist** — that enforcement is *why* it fell back to raw git.
- **Fix:** in `data/catalog/agents/committer.md`, add `"aspis commit*": allow` and **remove**
  `"git add*"` / `"git commit*"` (the `aspis commit` tool does staging+commit inside its own
  process, not via the bash tool, so the committer needs no raw-git write verbs). Re-render.
- **Corrects finding E7:** leads did *not* commit despite `deny`; the build-lead delegated to
  the committer, and the deny held. **We can rely on OpenCode bash-allowlist enforcement.** That
  is the lever for the whole permission strategy.

### B2. Runtime hooks already exist — P3 extends, not invents
- OpenCode: `runtime-hooks/opencode/scope-guard.ts` — a `tool.execute.before` plugin that vetoes
  an out-of-scope Edit/Write by calling the shared `runtime_guard.py` (throw = veto). Proven.
- Claude: `runtime-hooks/claude/settings.json` — a `PreToolUse` matcher on `Edit|Write` running
  the same `runtime_guard.py`.
- The adapter declares `runtime_hooks = ((catalog_path, export_path), …)` — data-driven, Discovery-style.
- **So P3 = add a few more events** to these two surfaces (e.g. session-start → preflight/clean-tree;
  a tool event → context-refresh; first-level block where git hooks can't reach). Same pattern.
- **Portability note:** both hooks call `python3`. On Windows `python3` may be absent → the hook
  silently no-ops (OpenCode `.nothrow()`, Claude non-fatal). A real C-PORTABLE bug to fix (resolve
  the interpreter), and a reason the scope-guard may not have fired in `demo_win2` on Windows.

### B3. Runtimes are already data + capabilities (no special-casing)
`data/runtimes/{opencode,claude,codex,cursor,gemini}.yaml` declare `detect`, `run`, `headless`,
`dir`, `capabilities{mode, subagents, subagent_depth, exportable}`. P3/P6 must use these
**capability checks**, never `if runtime == "x"` (constitution rule 9).

---

## C. Market research (mid-2026) — and how it maps to our levels

The external best-practice strongly **validates** F-014's thesis and sharpens specific designs.

| Finding (source) | Maps to | What we adopt |
|---|---|---|
| **"Scope is enforced by architecture, not just by instruction — a subagent that can only read cannot delete, regardless of what it's told."** (foojay) | L4 permissions, L5 hooks | The core F-014 principle, externally confirmed. Permissions/hooks are the enforcement; prose only names them. |
| **Just-in-time context** — load lightweight identifiers (paths, queries) at runtime, not exhaustive upfront; **progressive disclosure / lazy loading**; metadata (folders, names) as navigation cues. (Anthropic) | L1 context skill | Exactly the ASPS numbered ladder + your "hot then graduated cold load by reference." Port it; agents pull by `FILE_REGISTRY`/`CODE_MAP` reference, not dumps. |
| **"Right altitude"** — not brittle-specific, not vague; minimal set that *fully* outlines behaviour (minimal ≠ short); canonical examples over edge-case lists; XML/Markdown sections. (Anthropic) | L1/L2 instruction design | Confirms your philosophy: load-bearing rules in the body, examples not laundry-lists, structured sections, "minimal but not short." |
| **Compaction · structured note-taking · sub-agent isolation**; a sub-agent returns a **1–2k-token distilled summary**; clean context windows per agent. (Anthropic) | L2 loop / E13 mega-turn | Kill the 2-hour opaque turn: leads checkpoint, sub-agents return distilled summaries, not raw transcripts. |
| **Decision trees over lists** for routing — classify then act. (system-prompt patterns) | lead-routing / classification | Give leads an explicit decision tree, not a rule list. |
| **Self-healing = parse → validate against schema → fallback**; combine rule-filters + small-model validators. (guardrails) | L5 guards/findings | Deterministic check emits a finding; next agent's prestart consumes/resolves it. |
| **Small/cheap models work for guardrail & deterministic roles with strong few-shot examples**; reserve large models for judgement. (guardrails) | L3 model bands | Cheap floor is fine for deterministic roles *if* we give examples; judgement roles (planning/build lead, project-lead) get a higher floor. |

---

## D. Resulting edits to the planning docs (SPEC / PLAN / TASKS)

1. **Reframe the feature** around the rules it restores: **R-004 (one writer / committer-only)**
   and **R-003 (deterministic-first)** made *machine-enforced*; cite the external "enforced by
   architecture not instruction" principle.
2. **P0 unchanged but precise** — edit `committer.md` bash map (add `aspis commit*`, drop raw
   git write verbs); also fix the `python3` interpreter in both runtime hooks (B2 portability).
3. **P1 → per-agent permission edit in the catalog now** (12 agents), *plus* the **golden test**
   (every `aspis …`/script an agent is told to run ∈ its allowlist). Drop the "single-source render"
   from F-014 scope; record it as a **deferred follow-up** (later, at agent-count scale).
4. **P2 context skill = port the ASPS numbered ladder** with just-in-time + progressive disclosure
   wording; heavy roles get the skill, light subagents get inline rules; reference `FILE_REGISTRY`/
   `CODE_MAP`, never raw dumps.
5. **P3 = extend the existing two hook surfaces** (scope-guard.ts + settings.json) with a small,
   capability-checked, data-driven event set; fix the interpreter-resolution bug.
6. **P5 loop pass** adopts compaction / distilled sub-agent summaries / checkpoint cadence (kill E13);
   instruction design follows "right altitude" + decision-trees-for-routing.
7. **P6 = the system-lead config sub-agent** (decision A2): one gated path for model/mode/stack/config
   changes via `aspis` commands + per-change skills; grows skills over time (incl. system-repair).
8. **P7 model bands**: each agent declares min floor · max cap · preferred, justified by capability
   scores + instruction-adherence; deterministic roles may floor cheap (with examples), judgement
   roles floor higher. Stays R-007/R-008 aligned.

## E. Still-open research (flagged, not blocking the plan)
- Full **OpenCode + Claude hook-event catalog** (the 30+) to finalize the P3 event picks (T-12).
- A **capability-score → model-band** table per agent for P7 (needs our benchmark scores).

---

**Sources:**
[Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) ·
[foojay — Best practices for AI agents, subagents, skills & MCP](https://foojay.io/today/best-practices-for-working-with-ai-agents-subagents-skills-and-mcp/) ·
[PE Collective — System prompt design: 9 patterns for production LLMs (2026)](https://pecollective.com/blog/system-prompt-design-guide/) ·
[Leanware — LLM guardrails: strategies & best practices](https://www.leanware.co/insights/llm-guardrails) ·
[Anthropic — Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)
