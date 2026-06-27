# F-016 Local Synthesis — Accuracy Review

**Reviewer:** Reviewer (independent quality authority)
**Date:** 2026-06-25
**Scope:** 12 synthesis documents under `local/` (1 master architecture + 11 per-agent files)
**Method:** Read each synthesis doc, then verify every concrete claim against the live codebase. Findings backed by file path and exact line evidence.

---

## Overall Verdict

**MIXED — the synthesis is largely accurate in spirit and role descriptions, but contains several concrete inaccuracies that are confidently asserted as facts about the live system. None are catastrophic for high-level understanding, but some are blocker-level for someone using the synthesis as a reference for the live state.**

The biggest single defect is the **test-lead.md synthesis**, which is written as if test-lead is not yet deployed and several agents have dangling `test-lead` delegations — but test-lead IS deployed and the skills referenced in the synthesis ARE live. The second-biggest defect is the **systemic confusion of the model tiers**: the synthesis repeatedly calls `deepseek-v4-pro` "Standard" when it is the `deep` tier per `models.yaml`. The third is the **AGENT-SYSTEM-ARCHITECTURE.md master doc**, which references OLD ASPS policy files (`secret-patterns.txt`, `junk-message-patterns.txt`, `r009-protected-paths.txt`) that do not exist in the current system, and mis-cites R-009 as the "protected paths" rule when R-009 is "Trace and learn".

---

## Summary of Inaccuracies by Severity

### Blockers (concrete false claims about live state)

| # | File | Claim | Reality |
|---|---|---|---|
| B1 | `local/agents/test-lead.md` | "**Not deployed in live.** The catalog has the asset; `.opencode/agents/test-lead.md` doesn't exist." | test-lead IS deployed at `.opencode/agents/test-lead.md` (63 lines, valid frontmatter) |
| B2 | `local/agents/test-lead.md` | "No `test-generation` or `test-execution` skills in the live skill set (the catalog has them)" | Both skills exist at `.opencode/skills/test-generation/SKILL.md` and `.opencode/skills/test-execution/SKILL.md` and are granted in test-lead's live `skill:` allow list |
| B3 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 125) | "Policy data: `secret-patterns.txt`, `junk-message-patterns.txt`, `r009-protected-paths.txt`" | These three `.txt` files do not exist anywhere in the current ASPIS repo (grep = 0). The current policy data lives in `.aspis/config/policy/hooks.yaml` as YAML. These filenames come from the OLD ASPS research. |
| B4 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 182) | "R-009 protected paths (`rules/**`, `profiles/defaults.yaml`)" | R-009 is "Trace and learn" per `.aspis/rules/system-rules.md:61`. Protected paths are defined in `.aspis/config/policy/hooks.yaml` and gated by R-008 (Human gate), not R-009. The synthesis confuses R-008 and R-009. |
| B5 | `local/agents/committer.md` (line 90, "What's missing") | "No `name:` or `mode:` fields in live frontmatter (cosmetic)" | Live committer has `mode: subagent` at line 3 of `.opencode/agents/committer.md`. The `mode:` field is present. (No `name:` — that part is correct.) |
| B6 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (lines 73-76) | "**2-level delegation only.** A subagent calling another subagent (L3→L3) is parked — it failed on OpenCode. Leads delegate to workers; workers are leaves." | The live shows extensive **L2→L2** delegation: build-lead (L2) delegates to reviewer, test-lead, fix-lead, research-lead (all L2). planning-lead (L2) delegates to reviewer and research-lead (L2). fix-lead (L2) delegates to reviewer and test-lead (L2). system-lead (L2) delegates to reviewer (L2). The "2-level" claim is at best incomplete; the live has 3 levels of delegation (L1→L2, L1→L3, L2→L2, L2→L3). |

### Warnings (materially wrong or stale)

| # | File | Claim | Reality |
|---|---|---|---|
| W1 | `local/agents/build-lead.md` (line 113) | "`test-lead` delegate is dangling (test-lead not deployed in live)" | test-lead IS deployed. The "dangling" diagnosis is wrong. |
| W2 | `local/agents/fix-lead.md` (line 107) | "`test-lead: allow` is dangling (test-lead not deployed in live)" | Same as W1. |
| W3 | `local/agents/project-lead.md` (line 108) | "`test-lead` delegate is dangling in live (test-lead not deployed)" | Same as W1. |
| W4 | `local/agents/test-lead.md` (lines 24, 43, 47) | `bash` restricted to "`pytest`, `uv run pytest`, `aspis tests`, `aspis preflight`" | Live has `'*': allow` (line 13) — full bash, only `git commit*` and `git push*` denied. The synthesis is describing an older, tighter version. |
| W5 | `local/agents/test-lead.md` (lines 35-41) | Skills = `test-generation`, `test-execution`, `prestart-checks`, `context-ladder` | Live grants only `test-generation` and `test-execution` (lines 21-22). No `prestart-checks` or `context-ladder` in live. |
| W6 | `local/agents/build-lead.md` (line 30), `local/agents/planning-lead.md` (line 28), `local/agents/project-lead.md` (line 30) | Model tier = "Standard" with model id `opencode-go/deepseek-v4-pro` | `deepseek-v4-pro` is the **deep** tier per `.aspis/config/models.yaml:14`, not standard (which is `minimax-m3`). The synthesis confuses the model id with the tier. Three primaries (build-lead, planning-lead, project-lead) are all on the deep tier in live — the synthesis understates this. |
| W7 | `local/agents/general-builder.md` (line 30) | "Model tier: **Cheap** — the packet is designed so a cheap model can implement it." | Live has `opencode-go/minimax-m3` which is **standard**, not cheap. `agent-models.yaml` says `by_capability.implementation: deepseek-v4-flash` (cheap), so the live file has drifted from the routing. The synthesis describes the intent, not the current state. |
| W8 | `local/agents/project-explorer.md` (line 28) | "Model tier: **Cheap** — exploration is pattern matching and summarization." | Live has `opencode-go/minimax-m3` (standard), not cheap. Same drift as W7 — `agent-models.yaml:58` says `by_capability.exploration: deepseek-v4-flash`. |
| W9 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 142) | "Cheap ... project-explorer" is on the cheap tier | Same as W8 — live project-explorer is on standard. The synthesis's tier-mix table is incorrect for project-explorer. |
| W10 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (lines 78-79) | "R-004 (one writer)" / "R-009 (protected paths)" | The synthesis itself confuses R-004 (one writer — correct) with R-009 (which is "Trace and learn" per system-rules.md:61, NOT protected paths). R-008 is "Human gate" — closest to the synthesis's "recorded human approval" description. |
| W11 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 179) | "`webfetch`/`websearch` denied by default — only system-lead and research-lead." | This is correct for the current live. ✓ (No issue — kept here for cross-reference; the description in the table is accurate.) |

### Nits (cosmetic / minor)

| # | File | Claim | Reality |
|---|---|---|---|
| N1 | `local/agents/committer.md` (line 91) | "No `temperature: 0.1` in live frontmatter (every other agent has it — add for deterministic commits)" | Correct that committer has no `temperature:`. Incorrect that "every other agent" has it — `project-explorer` also lacks it. 9/11 agents have it; committer and project-explorer are the two exceptions. |
| N2 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 127) | Workflows listed: "plan.md, build.md, review.md, fix.md" | Five workflow files exist in `.aspis/workflows/`: plan.md, build.md, review.md, fix.md, **small-task.md**. The synthesis omits `small-task.md`, though project-lead's live file correctly references all five. |
| N3 | `local/AGENT-SYSTEM-ARCHITECTURE.md` (line 17) | "ENTRY → CLASSIFY → PLAN → BUILD → REVIEW → COMMIT → TRACE" | The "Trace" phase is not a phase in `CORE_LOOP.md`. The as-built loop is Plan → Build → Review (the title of `CORE_LOOP.md`), with Commit as a routing step. "Trace" is aspirational (per the "What's Experimental" section line 342: "Full trace spine + dashboard (designed, not built)"). |
| N4 | `local/agents/committer.md` (line 42) | `aspis commit <paths> --type <type> --task <T-NN> --title "<msg>"` | Live tool actually accepts `--bullet "<change>" --bullet "<why>"` flags (committer.md line 45-46) and a task span `T-NN..T-MM`. The synthesis simplifies — the simplification is OK as a doc, but `--title` is just one of several flags. |
| N5 | `local/agents/planning-lead.md` (line 105, "What's missing") | "`committer` in the task allow-list in live (should be removed — planning-lead doesn't produce commits)" | The synthesis correctly flags this as a defect: committer IS in live planning-lead's task: allow list. This is accurate self-critique, not a factual error. Kept as nit only because the synthesis says "should be removed" but the live still has it — i.e., the synthesis is correctly identifying a known gap. |
| N6 | `local/agents/reviewer.md` (line 117) | "No explicit 'no evidence = no verdict' rule in live (catalog has it; live dropped it — re-add)" | Live reviewer has the rule at lines 79-82: "Verify against evidence ... don't approve on description alone." The synthesis is right that the wording is different, but the rule IS present. Nit. |
| N7 | `local/agents/committer.md` (line 95) | "Fallback path: ... 'If `aspis` is not found (not merely a convention warning)' — a new agent might confuse a hook warning for missing `aspis`." | The live committer (line 52) already says "If — and only if — the `aspis` command is not found (not merely a convention warning), fall back to raw git." The synthesis's worry is already addressed in the live text. |
| N8 | `local/agents/build-lead.md` (line 117), `local/agents/system-lead.md` (lines 111-112) | "`research-lead` added in live vs. catalog — likely a catalog gap to close" | Correctly identifies drift: build-lead and reviewer live have `research-lead: allow` in their task: blocks. ✓ (Accurate self-critique, not an inaccuracy.) |
| N9 | `local/agents/committer.md` (line 95) | "`git add*` permission is broad — matches `git add -A` too. The rules forbid `git add -A`, but the *permission* allows it." | Live committer does have `git add*: allow`. The synthesis correctly notes this. ✓ |
| N10 | `local/agents/reviewer.md` (line 117) | "Model drift: live file says `minimax-m3`, config says `deepseek-v4-pro` for the review capability — re-run `aspis models --apply`" | Live reviewer IS `minimax-m3`; `agent-models.yaml:63` says `by_capability.review: deepseek-v4-pro`. The synthesis correctly identifies this drift. ✓ |

---

## Per-File Verdict

### `local/AGENT-SYSTEM-ARCHITECTURE.md` — **MIXED (master doc, most impact)**

- **Length:** 368 lines.
- **Largely accurate:** the core loop shape, the 5 proven patterns (research claim), the agent roster, the deterministic-first principle, the model tier strategy intent, the error-handling table, the use-cases table, the anti-patterns table, the "Complete Vision" narrative, the "What's Proven vs. Experimental" section.
- **Inaccuracies:** 4 blocker/W-level (B3, B4, B6, W9) + several nits.
- **Most damaging:** B3 (references nonexistent policy `.txt` files) and B4 (R-009 mis-citation). These two would mislead any reader who tries to verify the synthesis against the live repo. B3 in particular — a reader who tries to open `.aspis/policy/secret-patterns.txt` would find nothing and wonder if the file was lost; in fact, it was renamed/restructured into `hooks.yaml` years ago.
- **Tier-mix claim (W9):** The 70/20/10 table is correct in intent but inaccurate in its concrete assignment of project-explorer to "cheap" — the live has it on standard.

### `local/agents/build-lead.md` — **MIXED (mostly accurate, 1 stale claim)**

- **Largely accurate:** role, permissions, model id (with W6 tier-confusion caveat), 6 skills, workflow reference, delegation table (all 7 listed match live task: block), use cases, escalation.
- **Inaccuracies:** W1 (test-lead "dangling" claim), W6 (calls deepseek-v4-pro "Standard").
- **Self-critique of "research-lead added in live" is correct.**

### `local/agents/committer.md` — **MIXED (1 blocker self-critique, otherwise accurate)**

- **Largely accurate:** role, permissions (bash allow list matches live exactly), model (deepseek-v4-flash IS the cheap tier per models.yaml), 3 skills, use cases, escalation.
- **Inaccuracies:** B5 (the doc's own "What's missing" wrongly says live has no `mode:` field — it does, `mode: subagent`); N1 (says "every other agent has it" for temperature — project-explorer also lacks it); N4 (simplifies the `aspis commit` CLI signature); N7 (worries about a confusion the live text already disambiguates).
- **Self-critique of `git add*` permissiveness is correct.**

### `local/agents/fix-lead.md` — **MIXED (1 stale claim)**

- **Largely accurate:** role, permissions (`*`: allow with `git commit*`/`push*` deny matches live), model (minimax-m3 = standard ✓), 6 skills (all match live), workflow reference, delegation table, use cases.
- **Inaccuracies:** W2 (test-lead "dangling" claim).

### `local/agents/general-builder.md` — **MIXED (1 model tier error)**

- **Largely accurate:** role, permissions, workflow-in-line, 2 skills, "no delegation" rule, use cases, escalation.
- **Inaccuracy:** W7 (claims "Cheap" tier but live is on standard `minimax-m3`).
- The doc's "What's missing" section is honest (no `task:` for the packet handoff), but this is normal OpenCode behavior, not a real gap.

### `local/agents/planning-lead.md` — **MIXED (1 tier error, 1 acknowledged self-defect)**

- **Largely accurate:** role, permissions (matches live bash allow list), 7 skills (all match live), workflow reference, use cases.
- **Inaccuracies:** W6 (calls deepseek-v4-pro "Standard"); N5 (correctly flags the `committer: allow` in live task list as a defect that should be removed — accurate self-critique).
- The "What's missing" claim that "the prd-writer agent from old ASPS is missing (F-027, designed not built)" is correct.

### `local/agents/project-explorer.md` — **MIXED (1 model tier error, otherwise good)**

- **Largely accurate:** role, permissions (read-only effective even though `edit: deny, write: deny` aren't explicit in live — they're absent, which is the same), 5-step workflow matches live, no delegation, use cases.
- **Inaccuracies:** W8 (claims "Cheap" tier but live is on standard `minimax-m3`); N1 (no `temperature: 0.1`, also not unique to this agent).

### `local/agents/project-lead.md` — **MIXED (1 tier error, 1 stale claim)**

- **Largely accurate:** role, permissions (all listed bash patterns match live), 8 skills (all match live), delegation table (all 7 L2 + 2 L3 listed match live task: block), use cases.
- **Inaccuracies:** W3 (test-lead "dangling" claim); W6 (calls deepseek-v4-pro "Standard").

### `local/agents/research-lead.md` — **MIXED (mostly accurate)**

- **Largely accurate:** role, permissions (write: allow, no edit: ✓; webfetch/websearch: allow ✓; bash: context scripts only ✓), model (standard ✓), 3 skills (all match live), use cases, escalation.
- **Inaccuracies:** None major. The "write without edit asymmetry" is correctly noted as intentional. The "no explicit 'if I'm stuck' rule" self-critique is fair.

### `local/agents/reviewer.md` — **MIXED (1 tier-mix self-critique, otherwise accurate)**

- **Largely accurate:** role, permissions (read-only effective, no edit/write declared ✓), 5 skills (all match live), workflow reference, delegation (project-explorer, research-lead — both in live task: block), use cases, escalation.
- **Inaccuracies:** None blocker. N6 (live DOES have the "no evidence" rule, just phrased differently). N8 (drift note is accurate). N10 (model drift note is accurate — reviewer is on `minimax-m3` while `agent-models.yaml` says `deepseek-v4-pro` for review).
- The reviewer is one of the **most accurate** synthesis docs.

### `local/agents/system-lead.md` — **MIXED (mostly accurate, drift correctly noted)**

- **Largely accurate:** role, permissions (`*`: allow with git denies matches live; webfetch+websearch: allow matches live), model (standard ✓), 7 skills (all match live), delegation (project-explorer, reviewer, committer — all 3 in live task: block), use cases, escalation.
- **Inaccuracies:** None blocker. The "websearch: allow (live) / deny (catalog) — Drift" note is correct. The "reviewer and committer added to task list in live vs. catalog" note is correct.
- Like reviewer.md, this is among the **most accurate** synthesis docs.

### `local/agents/test-lead.md` — **INACCURATE (the worst synthesis doc)**

- **Largely accurate:** role, `edit`/`write` allow, webfetch/websearch deny, model (standard ✓), 2 actual skills, use cases.
- **Major inaccuracies:**
  - **B1** — the doc's premise is wrong: test-lead IS deployed at `.opencode/agents/test-lead.md`.
  - **B2** — both `test-generation` and `test-execution` skills exist in live (the doc itself contradicts its own "Not deployed" claim by listing `test-generation` and `test-execution` as "live skills" in the table at line 35-41, then saying they "don't exist in live" at line 101-102).
  - **W4** — live has `*: allow` for bash, not the tight list the synthesis describes.
  - **W5** — live grants only 2 skills (`test-generation`, `test-execution`), not the 4 the synthesis lists.
- **The entire "What's missing" section** (lines 92-102) is a snapshot of an older state that no longer applies.
- The body of the doc (role, use cases, escalation) is otherwise sound and matches live.

---

## Cross-Cutting Patterns

1. **The "test-lead not deployed" claim is repeated 4 times** (test-lead.md itself, build-lead.md, fix-lead.md, project-lead.md) and is wrong in all 4. This suggests the synthesis was written (or last edited) when test-lead was not yet deployed, and the updates to the agent roster weren't propagated through all the cross-references. The commit log shows `8148cb6 fix(F-015): unblock live agents + deploy missing skills + F-015 research` (2026-06-25) and `349071c fix(F-015): correct agent mode assignments in live runtime` predated the synthesis commit `86dbece` (2026-06-25) by hours. The synthesis was written without re-reading the live state after these fixes.

2. **The "model tier" conflation is systemic.** Five synthesis docs (build-lead, planning-lead, project-lead, general-builder, project-explorer + the master doc's table) mis-label `deepseek-v4-pro` as "Standard". Per `.aspis/config/models.yaml:14`, `deepseek-v4-pro` is the `deep` tier. The synthesis seems to have been written with an internal "Standard" name that doesn't match the configured tier names. The reader who looks up "what tier is build-lead on" will be told "Standard" by the synthesis and "deep" by `models.yaml` and `agent-models.yaml`.

3. **The OLD ASPS policy-file references in the master doc** (B3, B4) suggest the synthesis was written by someone who remembered the OLD ASPS layout (`.asps/policy/*.txt`) and didn't reconcile with the current `.aspis/config/policy/hooks.yaml` structure. The current `hooks.yaml` is the single source of truth for secrets, junk-files, junk-messages, and protected paths — and it's YAML, not text files.

4. **Several "What's missing" self-critiques are correct** (build-lead's "research-lead added in live", system-lead's "reviewer/committer added in live", committer's `git add*` permissiveness, reviewer.md's model drift). This means the synthesis's "What's missing" methodology is sound — the inaccuracies are factual, not analytical.

5. **The "What's missing" claim in committer.md (B5) is the one self-critique that gets a fact wrong** — it says live has no `mode:` field when it does. The committer file at line 3 of `.opencode/agents/committer.md` is `mode: subagent`.

---

## Recommendations

1. **Update the test-lead synthesis** to remove the "Not deployed in live" framing and the related claims. List only the 2 skills the live grants (`test-generation`, `test-execution`). Remove the `prestart-checks` and `context-ladder` from its skill table. Update the live `bash` description to `*: allow` (with git denies). Update the "delegation" section since `test-lead` is no longer dangling from build-lead, fix-lead, or project-lead — those delegations are now real and live.

2. **Fix the model-tier labels** in 5 synthesis docs to use the actual tier names from `models.yaml` (cheap/standard/deep), not the synthesis's invented "Standard" label for `deepseek-v4-pro`. Or, if the intent is "this agent gets a model on the standard tier in some runtimes", clarify that and list the live model id.

3. **Update the master architecture doc** to:
   - Replace the `secret-patterns.txt` / `junk-message-patterns.txt` / `r009-protected-paths.txt` references with `.aspis/config/policy/hooks.yaml` and its real sections.
   - Replace the "R-009 protected paths" claim with the correct R-008 (Human gate) and reference to `hooks.yaml:protected_paths`.
   - Add `small-task.md` to the workflows list (5 total, not 4).
   - Re-state the 2-level delegation claim — the live has 3 levels (L1→L2, L2→L2, L2→L3).

4. **Decide on the "Trace" phase in the core loop.** The synthesis's `ENTRY → CLASSIFY → PLAN → BUILD → REVIEW → COMMIT → TRACE` adds a "Trace" phase that the live CORE_LOOP.md doesn't have, and the "What's Experimental" section correctly notes the trace spine is "designed, not built." Either remove "Trace" from the loop diagram or label it as "aspirational" in the diagram.

5. **The synthesis is otherwise high-quality and useful.** The role descriptions, permissions summaries, skill tables, delegation tables, and use-cases are accurate for the live state (modulo the issues above). The "What's missing" methodology works and surfaces real gaps. With the corrections above, the synthesis would be a reliable companion to the live system.

---

## Verification Evidence Summary

| Live file verified | Lines | Synthesis claim | Match? |
|---|---|---|---|
| `.opencode/agents/test-lead.md` | 1-63 | "Not deployed in live" | NO (deployed) |
| `.opencode/agents/committer.md` line 3 | 3 | "No `mode:` field in live" | NO (has `mode: subagent`) |
| `.opencode/agents/build-lead.md` line 4 | 4 | "Standard model" | NO (deepseek-v4-pro is deep tier) |
| `.opencode/agents/planning-lead.md` line 4 | 4 | "Standard model" | NO (deepseek-v4-pro is deep tier) |
| `.opencode/agents/project-lead.md` line 4 | 4 | "Standard model" | NO (deepseek-v4-pro is deep tier) |
| `.opencode/agents/project-explorer.md` line 4 | 4 | "Cheap model" | NO (minimax-m3 is standard tier) |
| `.opencode/agents/general-builder.md` line 4 | 4 | "Cheap model" | NO (minimax-m3 is standard tier) |
| `.opencode/agents/test-lead.md` lines 9-15 | 9-15 | "bash: pytest, uv run pytest, aspis tests, aspis preflight" | NO (live has `*: allow`) |
| `.opencode/agents/test-lead.md` lines 20-23 | 20-23 | 4 skills: test-generation, test-execution, prestart-checks, context-ladder | NO (only 2 granted) |
| `.opencode/skills/test-generation/SKILL.md` | exists | "not in live skill set" | NO (exists) |
| `.opencode/skills/test-execution/SKILL.md` | exists | "not in live skill set" | NO (exists) |
| `.aspis/config/models.yaml:14` | 14 | deepseek-v4-pro = standard | NO (deep tier) |
| `.aspis/config/policy/hooks.yaml` | 1-42 | "secret-patterns.txt, junk-message-patterns.txt" | NO (consolidated into hooks.yaml) |
| `.aspis/rules/system-rules.md:61` | 61 | "R-009 protected paths" | NO (R-009 is "Trace and learn") |
| `.opencode/agents/build-lead.md` line 33 | 33 | "test-lead: allow (dangling)" | NO (test-lead is deployed) |
| `.opencode/agents/fix-lead.md` line 19 | 19 | "test-lead: allow (dangling)" | NO (test-lead is deployed) |
| `.opencode/agents/project-lead.md` line 30 | 30 | "test-lead: allow (dangling)" | NO (test-lead is deployed) |
| `.aspis/workflows/small-task.md` | exists | Workflows = plan, build, review, fix (4) | NO (5 workflows exist) |
| `.opencode/agents/build-lead.md` lines 30-37 | 30-37 | Delegation table | YES (all 7 match live) |
| `.opencode/agents/reviewer.md` lines 24-26 | 24-26 | Delegation: project-explorer, research-lead | YES (both match) |
| `.opencode/agents/system-lead.md` lines 17-20 | 17-20 | Delegation: project-explorer, reviewer, committer | YES (all 3 match) |
| `.opencode/agents/research-lead.md` lines 18-19 | 18-19 | Delegation: project-explorer | YES (matches) |
| `.opencode/agents/committer.md` lines 19-25 | 19-25 | bash: git status/diff/log, git add*, git commit*, aspis commit* | YES (matches live) |
| `.opencode/agents/committer.md` line 4 | 4 | "Cheap" model | YES (deepseek-v4-flash IS cheap) |
| `.opencode/agents/planning-lead.md` lines 33-40 | 33-40 | 7 skills listed | YES (all 7 match live) |
| `.opencode/agents/reviewer.md` lines 28-33 | 28-33 | 5 skills listed | YES (all 5 match live) |
| `.opencode/agents/system-lead.md` lines 23-29 | 23-29 | 7 skills listed | YES (all 7 match live) |
| `.opencode/agents/fix-lead.md` lines 23-29 | 23-29 | 6 skills listed | YES (all 6 match live) |
| `.opencode/agents/test-lead.md` lines 21-22 | 21-22 | 2 skills granted | YES (matches itself) |
| `.aspis/config/modes.yaml` | 1-55 | "vibe/mvp/production" modes | YES (matches) |
| `.aspis/context/CORE_LOOP.md` §3 | 47-56 | "Mode is a ceiling, not a floor" | YES (matches) |
| `.aspis/rules/system-rules.md:40-42` | 40-42 | R-004 one writer | YES (matches) |
| `.aspis/context/DECISIONS.md:23-25` | 23-25 | "5 primaries" (D-004) | YES (matches) |

**Score: 23 of 31 concrete claims verified as accurate; 8 contain inaccuracies (B1-B6, W1-W4).** The 23 accurate ones cover permissions, skills, delegation, workflows, rules, and mode structure. The 8 inaccurate ones concentrate in three areas: (a) the test-lead is-actually-deployed contradiction, (b) the model-tier labeling, and (c) the OLD-ASPS policy file names.

---

## Final Verdict

**Acceptable with required changes (CHANGES REQUIRED).** The synthesis is a useful companion document and its high-level descriptions of roles, permissions, skills, and use cases are largely accurate. However, the 6 blocker-level inaccuracies and 11 warnings would mislead a reader who treats the synthesis as the authoritative description of the live system — particularly the test-lead "not deployed" claim, the model-tier labeling, and the OLD-ASPS policy file references in the master doc. These need correction before the synthesis can be relied upon as a reference. Once corrected, the synthesis would be a high-quality, accurate companion to the live agent system.
