# F-016 Local Synthesis — Rules-Compliance Review

**Reviewer:** Reviewer (independent quality authority)
**Scope:** `local/AGENT-SYSTEM-ARCHITECTURE.md` + 11 files in `local/agents/`
**Reference set:** `.aspis/rules/architecture-constitution.md` (12 rules), `.aspis/rules/system-rules.md` (R-001…R-009), `.aspis/context/CORE_LOOP.md`, `.aspis/context/DECISIONS.md`, and the live agent files at `.opencode/agents/` and `.claude/agents/`.
**Mode:** Strict (per request).
**Date:** 2026-06-25

---

## Overall verdict

**VIOLATIONS — overall NON-COMPLIANT.** The synthesis is well-structured and
broadly consistent with the project's design, but it ships **four blocking
issues** plus a thick layer of warnings that must be addressed before the
documents can be considered rule-clean.

| # | Severity | Where | Summary |
|---|---|---|---|
| 1 | **Blocker** | AGENT-SYSTEM-ARCHITECTURE.md, project-lead, system-lead, fix-lead | Cites "R-009" for the human gate and protected paths. R-009 is "Trace and learn"; the human gate is **R-008**. Misattribution across four files. |
| 2 | **Blocker** | test-lead | Claims `test-lead` is "Not deployed in live" and skills missing. Both are factually wrong — `.opencode/agents/test-lead.md` and `.opencode/skills/{test-generation,test-execution}/SKILL.md` all exist. |
| 3 | **Blocker** | AGENT-SYSTEM-ARCHITECTURE.md | Hardcodes concrete model strings ("Haiku 4.5 / DeepSeek Flash", "Sonnet 4.6 / DeepSeek Pro", "Opus 4.8 / DeepSeek Pro (thinking)"). Violates D-016 (canonical model catalog is the source of truth) and Constitution rules 2, 3, 9. |
| 4 | **Blocker** | project-lead | Self-contradiction: says "Never delegates directly to L3 workers" then "May also call `project-explorer` and `committer`" (which are L3). |
| 5 | Warning | All 11 agent files (except committer/general-builder) | Local docs reference skills (`request-classification`, `requirement-clarification`, `root-cause-analysis`, `scope-control`, `acceptance-decision`, `project-question-answering`) that exist in `.claude/skills/` but NOT in `.opencode/skills/`. The synthesis must declare which runtime it targets and align to that runtime's skill set. |
| 6 | Warning | reviewer's "What's missing" only | Model tier drift: local says "Standard" for reviewer and fix-lead. `.claude/agents/` says Opus 4.8 (deep); `.opencode/agents/` says minimax-m3 (cheap). Local captures the *intended* design but **does not flag this drift for fix-lead** (only reviewer). Same drift exists for system-lead, test-lead, research-lead and is not flagged anywhere. |
| 7 | Warning | system-lead | `websearch: allow` (live) vs `deny` (catalog) — flagged locally as "Drift — reconcile with catalog." Live diverges from least-privilege baseline. |
| 8 | Warning | planning-lead, project-lead, build-lead, fix-lead, system-lead | "What's missing" sections all name the same live/catalog drift. The local doc is honest about it, but the drift is structural — these should be F-016 follow-ups, not buried in a doc. |
| 9 | Warning | project-lead | The local doc says project-lead's task allow-list in the live file "should be removed" for `committer` and `test-lead` (test-lead is dangling). The local doc **describes the right thing** and flags the live drift, so this is correctly captured — but the live file has not been fixed. |
| 10 | Warning | committer | "git add* allow matches git add -A; rules forbid it." Soft least-privilege violation; local doc acknowledges. |
| 11 | Nit | All 11 agent files | Each file ends with a "What's missing" + "Gaps from research" section. These are valuable self-critiques but they leak process into the artifact. A clean synthesis would move these to a follow-up issue, not ship them in the role doc. |
| 12 | Nit | AGENT-SYSTEM-ARCHITECTURE.md | Uses "D-002" / "D-005" etc. implicitly but never cites the decisions by ID. A document this dense should anchor its claims to the durable record (D-008, D-009, D-015, D-016) to make drift checkable. |

---

## File-by-file verdicts

### 1. `local/AGENT-SYSTEM-ARCHITECTURE.md` — **VIOLATIONS**

**Constitution rules (12):**
- Rule 2 (Plugin First): agents are catalog assets, profiles are data — **PASS**.
- Rule 3 (Single Source of Truth): modes in `modes.yaml`, profiles in YAML — **PASS**.
- Rule 4 (Configuration over Code): modes are data, hooks are data — **PASS**.
- Rule 5 (Core is Stable): 3-layer system, agents in catalog — **PASS**.
- Rule 6 (Dependency Direction): L1 → L2 → L3, workers are leaves — **PASS**.
- Rule 7 (Discovery over Registration): bootstrap auto-promotes — **PASS**.
- Rule 8 (Generated Artifacts): templates/workflows, indexes — **PASS**.
- Rule 9 (No Special Cases): **VIOLATION** — hardcodes "Haiku 4.5 / DeepSeek Flash", "Sonnet 4.6 / DeepSeek Pro", "Opus 4.8 / DeepSeek Pro (thinking)". The model strings are concrete names that bypass the canonical catalog (D-016) and the tier map (`models.yaml`).
- Rule 11 (Architecture before Features): the system-lead ladder puts mechanism-decision before authoring — **PASS**.
- Rule 12 (Portable by Default): Python + uv, runtime-agnostic — **PASS** (implicit).

**System rules (R-001…R-009):**
- R-001: scope control (packet + subagent frontmatter + hook) — **PASS**.
- R-002: deterministic gate (pre-commit, post-commit, prereq-validate) — **PASS**.
- R-003: deterministic-first ladder — **PASS**.
- R-004: committer-only commit, `git commit*` denied elsewhere — **PASS**.
- R-005: tests-as-spec — **PASS** (gate is the closer, but tests are mentioned).
- R-006: thin agents, single source — **PASS** in spirit.
- R-007: pinned model tier — **VIOLATION** in effect: tier map lists concrete model names, not the canonical id + tier that R-007 expects an agent to declare.
- R-008: human gate — **VIOLATION by misattribution**: the doc says "R-009 protected paths ... can only be edited by the governance subagent, and only after a recorded human approval." and the error table says "Architecture/rules/model-routing change ... Human via R-009." R-008 is the human gate; R-009 is "Trace and learn."
- R-009: trace — the "Trace" row covers tool call recording, but the doc never says "R-009" for trace. The "Trace" row is consistent with R-009's *intent*; the misattribution is the blocker.

**Core-loop consistency (CORE_LOOP.md):** Consistent at the high level (plan → build → review → commit, mode as ceiling, deterministic gate, sub-agent isolation, packet handoffs). The doc compresses CORE_LOOP's 5 planning phases + 3 loops into 7 table rows, which is a faithful summary. **PASS** for consistency, with one note: CORE_LOOP.md is explicit that "Mode is a ceiling, not a floor"; the architecture doc says "Same loop, different depth" — same idea, less precise.

**DECISIONS.md contradictions:**
- D-001, D-003, D-004, D-005, D-007, D-011, D-013, D-015 — **PASS** in spirit.
- D-006 (three rule layers) — not mentioned. **WARNING**.
- D-008 (asset kinds are data) — implied via profile concept, not cited. **WARNING**.
- D-009 (architecture constitution) — never referenced. **WARNING**.
- D-010 (hooks non-blocking by default) — not stated; doc implies hooks are always enforcing. **WARNING**.
- D-012 (generated indexes untracked) — not mentioned. **WARNING**.
- D-014 (brain gitignore + test ledger) — not mentioned. **WARNING**.
- D-016 — **VIOLATION** (concrete model names instead of canonical ids).
- D-017, D-018 — not mentioned. **WARNING**.

**Permission model (deny-wins, least-privilege):**
- "deny → ask → allow, first match wins" — **PASS** (matches the runtime model).
- "Deny from any scope blocks an allow from any other" — **PASS**.
- `webfetch`/`websearch` denied by default except system-lead and research-lead — **PASS**.
- Reviewer is read-only — **PASS**.
- committer is the only committer — **PASS**.
- `git push*` denied for every agent — **PASS** (matches R-008).
- BUT: system-lead has `websearch: allow` in the live file (acknowledged in `system-lead.md`). The architecture doc is silent on whether system-lead should be allowed websearch at all. **WARNING**.

**Delegation model (no lead-to-lead-to-lead, project-lead is the only router):**
- 3 layers explicit; "Leads delegate to workers; workers are leaves" — **PASS**.
- L3 → L3 is parked (failed on OpenCode) — **PASS**.
- BUT: the doc says "5 primaries: project-lead + planning-lead + build-lead + reviewer + system-lead" and project-lead is L1. The other "primaries" are L2. The doc is internally consistent. **PASS**.

**Findings (this file):**
- **B1 (Blocker).** Misattributes R-008 (human gate) to R-009 in three places: the permissions section ("R-009 protected paths"), the error-handling table ("Human via R-009"), and the "Editor touched `rules/**`" row. The system-rules file states R-008 = human gate, R-009 = trace and learn. This is exactly the kind of "duplicated rule reference" that R-006 (single source) is meant to prevent.
- **B2 (Blocker).** Model tier table hardcodes "Haiku 4.5 / DeepSeek Flash", "Sonnet 4.6 / DeepSeek Pro", "Opus 4.8 / DeepSeek Pro (thinking)". D-016 declares `minimax-m3`, `claude-opus-4-8` etc. as the canonical ids; tier map should hold canonical ids only. This violates Constitution #2 (Plugin First), #3 (Single Source of Truth), #9 (No Special Cases).
- **W1 (Warning).** Decisions D-006, D-008, D-009, D-010, D-012, D-014, D-017, D-018 are not cited by ID. The doc is a synthesis of these decisions; failing to cite them makes drift check impossible.
- **W2 (Warning).** Hooks are described as enforcing (Permissions section, Error-handling table) but D-010 says **non-blocking by default** (`enforcement: warn`). The doc never says "warn by default, block behind a single switch." Readers will write hooks that block by default.
- **W3 (Warning).** No mention of the three rule layers (D-006), so the doc's own scope ("how the system works") is not aligned with the project's official rule taxonomy.
- **N1 (Nit).** "Built from 10 research files" is meta-commentary. The doc would be more self-contained if it cited the files inline.

---

### 2. `local/agents/project-lead.md` — **VIOLATIONS**

- Role clear, non-overlapping. The single L1 entry point. **PASS**.
- Permissions: least-privilege; `read`/`grep`/`glob` allow, `edit`/`write` deny, `webfetch`/`websearch` deny, `git commit/push` deny. **PASS**.
- Model tier: Standard, `opencode-go/deepseek-v4-pro` — matches live. **PASS**.
- Skills: `project-awareness`, `context-ladder`, `request-classification`, `lead-routing`, `context-packaging`, `project-question-answering`, `project-guidance`, `project-health`.
  - **`request-classification` and `project-question-answering` exist in `.claude/skills/` only — not in `.opencode/skills/`.** Same as live, so the local faithfully reproduces the drift. **WARNING**.
- Delegation routes to L2 leads only, plus `project-explorer` and `committer` (L3). **PASS** in concept, **VIOLATION** in wording (see B1).
- Use cases realistic. **PASS**.
- Escalation clear: human gate for R-009-listed items. **VIOLATION by misattribution** (R-009 is not the human gate).

**Findings:**
- **B1 (Blocker).** "Never delegates directly to L3 workers" (line 72) directly contradicts "May also call `project-explorer` for repo exploration and `committer` for lifecycle commits" (line 70–71). Both are L3 leaves per the architecture doc and the live task allow-list. The doc must pick one rule.
- **B2 (Blocker).** "Architecture / rules / security / model-routing / self-improvement → human gate (R-009)" (line 85). Human gate is R-008, not R-009. The system-rules file is the single source; the local doc must restate the correct id.
- **W1 (Warning).** "What's missing" acknowledges that the live file's task allow-list includes `committer` (should be removed) and `test-lead` (dangling). The local doc is honest about the drift; the live file has not been fixed.
- **W2 (Warning).** Skills `request-classification` and `project-question-answering` are not in `.opencode/skills/`. The synthesis must state the target runtime explicitly.

---

### 3. `local/agents/planning-lead.md` — **WARNINGS**

- Role clear, non-overlapping. Plans a lifecycle, not a single doc. **PASS**.
- Permissions: `edit`/`write` allow (for feature artifacts), `webfetch`/`websearch` deny, `git commit/push` deny. **PASS**.
- Model tier: Standard, `opencode-go/deepseek-v4-pro` — matches live. **PASS**.
- Skills: `planning-intake`, `prestart-checks`, `context-ladder`, `requirement-clarification`, `feature-planning`, `architecture-planning`, `task-decomposition`.
  - **`requirement-clarification` exists in `.claude/skills/` only.** **WARNING**.
- Delegation to `research-lead`, `reviewer`, `project-explorer` only. **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear: "If stuck, stop — don't guess." **PASS**.

**Findings:**
- **W1 (Warning).** Local doc claims "Never delegates to builders or committer" but the live file's task allow-list includes `committer: allow`. The local doc's "What's missing" flags this — good honesty, unresolved drift.
- **W2 (Warning).** `requirement-clarification` skill is not in `.opencode/skills/`. Same as live.
- **N1 (Nit).** "Recognizes defect-shaped requests ... → routes to fix-lead" appears in the "What's missing" / "Gaps" sections, not in the role description. A defect request is a non-trivial path; promote it to the role body.

---

### 4. `local/agents/build-lead.md` — **WARNINGS**

- Role clear, non-overlapping. The orchestrator. **PASS**.
- Permissions: `edit`/`write` allow (orchestration artifacts), `pytest` allow, `git commit/push` deny. **PASS**.
- Model tier: Standard, `opencode-go/deepseek-v4-pro` — matches live. **PASS**.
- Skills: `prestart-checks`, `context-ladder`, `build-readiness`, `task-orchestration`, `scope-control`, `selective-testing`.
  - **`scope-control` exists in `.claude/skills/` only.** **WARNING**.
- Delegation: `general-builder`, `reviewer`, `test-lead` (dangling), `fix-lead`, `committer`, `project-explorer`, `research-lead` (drift). **PASS** at intent, **WARNING** for the live drift.
- Use cases realistic. **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **W1 (Warning).** `scope-control` skill is not in `.opencode/skills/`.
- **W2 (Warning).** `test-lead` is a dangling delegate (test-lead is in fact deployed in live, but the local doc still says it's not — see test-lead entry below). The local doc says "should be in catalog" for `research-lead` — accurate.
- **W3 (Warning).** "The 'per-task context-isolated sub-agent reviewer' is designed ... but no `sub-reviewer` agent exists" — the live build always escalates to the Reviewer lead. The local doc identifies the gap; it should be a follow-up issue.

---

### 5. `local/agents/reviewer.md` — **WARNINGS**

- Role clear, non-overlapping. The independent quality authority. Read-only. **PASS**.
- Permissions: read-only, `edit`/`write` deny, `git commit/push` deny, `webfetch`/`websearch` deny. **PASS**.
- Model tier: Standard. Live is `opencode-go/minimax-m3` (cheap). **DRIFT, FLAGGED.**
- Skills: `review-strategy`, `context-ladder`, `quality-review`, `acceptance-decision`, `plan-critic`.
  - **`acceptance-decision` exists in `.claude/skills/` only.** **WARNING**.
- Delegation: `project-explorer`, `research-lead` (drift). **PASS** at intent.
- Use cases realistic (vibe, MVP, production modes). **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **W1 (Warning).** `acceptance-decision` skill is not in `.opencode/skills/`.
- **W2 (Warning).** Model drift — local says Standard, live `.opencode` is cheap (minimax-m3), live `.claude` is deep (Opus 4.8). Local correctly flags this in "What's missing," but the fix-lead case below is **not** flagged.
- **W3 (Warning).** No "no evidence = no verdict" rule in the local body. Catalog has it; the local body should keep it.

---

### 6. `local/agents/system-lead.md` — **VIOLATIONS**

- Role clear, non-overlapping. Owns the platform, not product features. **PASS**.
- Permissions: `edit`/`write` allow, `bash: '*': allow` (full system), `webfetch` allow, `websearch` allow (live) / deny (catalog). The local doc's table flags the **websearch drift** as the open issue. **MIXED**.
- Model tier: Standard. Live is `opencode-go/minimax-m3` (cheap). **DRIFT, NOT FLAGGED.**
- Skills: `prestart-checks`, `system-awareness`, `deterministic-first`, `asset-authoring`, `system-validation`, `system-repair`, `config-management`. All exist in both runtimes. **PASS**.
- Delegation: `project-explorer`, `reviewer`, `committer`. **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear: "Stop and request human approval for any change to rules, permissions, security posture, or model routing (R-009)." **VIOLATION by misattribution** — R-008 is the human gate.

**Findings:**
- **B1 (Blocker).** "Never edit `rules/**` or `profiles/defaults.yaml` — that's the governance subagent, R-009 gated" (line 90). The governance subagent is the right concept, but the rule id is wrong — the human gate is R-008.
- **B2 (Blocker).** Live `websearch: allow` violates least-privilege: the architecture doc and the system lead's own claim ("Default is **production**" via R-007) say deny by default. The local doc's "What's missing" flags this as a drift but does not state a recommended resolution (e.g., "remove `websearch: allow` from live; webfetch only").
- **W1 (Warning).** Model tier drift not flagged: local says Standard, live is cheap. Same drift pattern as reviewer but not acknowledged.
- **W2 (Warning).** Live `bash: '*': allow` is very broad. The local doc says "Full system access for validation, repair, authoring" which is correct in intent, but the system-lead is the only lead with web access. If system-lead and research-lead both have it, the principle "two agents, one tool" is not violated; but no other agent has the breadth, so the surface is correct in proportion.

---

### 7. `local/agents/fix-lead.md` — **WARNINGS**

- Role clear, non-overlapping. The recovery authority. **PASS**.
- Permissions: `edit`/`write` allow, `bash: '*': allow` (full debug), `webfetch`/`websearch` deny. **PASS**.
- Model tier: **local says Standard; live is `opencode-go/minimax-m3` (cheap); `.claude` is Opus 4.8 (deep).** **DRIFT, NOT FLAGGED.**
- Skills: `prestart-checks`, `context-ladder`, `root-cause-analysis`, `corrective-fix`, `scope-control`, `selective-testing`.
  - **`root-cause-analysis` and `scope-control` exist in `.claude/skills/` only.** **WARNING**.
- Delegation: `reviewer`, `committer`, `project-explorer`, `test-lead` (dangling). **PASS** at intent.
- Use cases realistic. **PASS**.
- Escalation clear: 3-attempt cap, hand to committer, R-009-gated for protected paths. **VIOLATION by misattribution**.

**Findings:**
- **B1 (Blocker).** "Architecture/rule changes → human gate (R-009)" (line 88). Human gate is R-008.
- **W1 (Warning).** `root-cause-analysis` and `scope-control` skills are not in `.opencode/skills/`.
- **W2 (Warning).** Model tier drift is **not** flagged in "What's missing" — the only model drift the local doc names is for the reviewer. The fix-lead's drift to cheap (`.opencode`) / deep (`.claude`) is silent.

---

### 8. `local/agents/test-lead.md` — **VIOLATIONS**

- Role clear, non-overlapping. The validation authority. Produces evidence, not verdicts. **PASS**.
- Permissions: `edit`/`write` allow (writing tests), `bash: '*': allow`, `webfetch`/`websearch` deny. **PASS**.
- Model tier: Standard. Live is `opencode-go/minimax-m3` (cheap). **DRIFT, NOT FLAGGED.**
- Skills: `test-generation`, `test-execution`. Both exist in `.opencode/skills/`. **PASS** at the skill level.
- Delegation: `project-explorer` only. **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **B1 (Blocker).** The "What's missing" section states: **"Not deployed in live. The catalog has the asset; `.opencode/agents/test-lead.md` doesn't exist."** This is **factually wrong** — the file exists at `.opencode/agents/test-lead.md` (and `.claude/agents/test-lead.md`). The local doc directly contradicts the actual live state.
- **B2 (Blocker).** Same section: **"No `test-generation` or `test-execution` skills in the live skill set (the catalog has them)."** Both skills exist at `.opencode/skills/test-generation/SKILL.md` and `.opencode/skills/test-execution/SKILL.md`. Same fact error.
- These two claims are the most concrete contradictions in the entire synthesis. They are the **single most important** issue to fix.
- **W1 (Warning).** Model tier drift not flagged (same pattern as fix-lead).
- **W2 (Warning).** The doc is the only one of the 11 that says "**Not deployed in live**" — a major false claim that should be removed.

---

### 9. `local/agents/research-lead.md` — **WARNINGS**

- Role clear, non-overlapping. The knowledge layer. **PASS**.
- Permissions: `write` allow, `edit` deny (asymmetry — author references, not source), `webfetch`/`websearch` allow, `bash` tightly scoped to context scripts. **PASS** in intent; the asymmetry is unusual but explained.
- Model tier: Standard. Live is `opencode-go/minimax-m3` (cheap). **DRIFT, NOT FLAGGED.**
- Skills: `context-ladder`, `knowledge-research`, `knowledge-packaging`. All exist in both runtimes. **PASS**.
- Delegation: `project-explorer` only. **PASS**.
- Use cases realistic. **PASS**.
- Escalation acknowledged as missing in the doc itself. **WARNING**.

**Findings:**
- **W1 (Warning).** Model tier drift not flagged.
- **W2 (Warning).** `edit: deny` / `write: allow` split is not present in the live file's frontmatter — the live file's `permission:` block does not declare an explicit `edit:` line, so the asymmetry is implied by the absence of an `edit` allow. The local doc is more explicit than the live; this is fine for a synthesis but should be added to the live.
- **W3 (Warning).** "If stuck, stop — don't guess" rule acknowledged as missing. Should be added; it's a project-wide rule (R-007 implies it; the project's other leads all have it).

---

### 10. `local/agents/committer.md` — **COMPLIANT**

- Role clear, non-overlapping. The single commit authority. **PASS**.
- Permissions: `edit`/`write` deny, `bash` allow for `git add*`/`git commit*`/`aspis commit*`, `git push` deny. **PASS**.
- Model tier: Cheap. Live is `opencode-go/deepseek-v4-flash` (cheap). **PASS**.
- Skills: `commit-message`, `commit-splitting`, `clean-tree-precondition`. All exist in both runtimes. **PASS**.
- No delegation (leaf). **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **N1 (Nit).** Live file has no `temperature:` field; the local doc notes this. Should be added for deterministic commits (R-007 spirit).
- **N2 (Nit).** Live file's `bash: 'git add*': allow` matches `git add -A`. Local doc correctly flags this. The hook (D-010, D-011) is the actual gate; the permission is a soft violation of least-privilege but documented.

---

### 11. `local/agents/general-builder.md` — **COMPLIANT**

- Role clear, non-overlapping. Disposable execution worker. **PASS**.
- Permissions: `edit`/`write` allow (within packet), `bash: '*': allow` minus commit/push, `webfetch`/`websearch` deny. **PASS**.
- Model tier: Cheap. Live is `opencode-go/minimax-m3` (cheap). **PASS**.
- Skills: `prestart-checks`, `clean-tree-precondition`. Exist in both runtimes. **PASS**.
- No delegation (leaf). **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **N1 (Nit).** Local doc notes: "the agent has no `task:` to receive a packet. It arrives as part of the task invocation from the build-lead. Add 'you are invoked by the build-lead with a packet.'" — fair; the live file's `task:` allow-list is empty because the builder is invoked, not delegated to. Documented gap, no rule violation.

---

### 12. `local/agents/project-explorer.md` — **COMPLIANT**

- Role clear, non-overlapping. Read-only exploration helper. **PASS**.
- Permissions: `read`/`grep`/`glob` allow, `edit`/`write` deny, `bash` tightly scoped to context scripts, `webfetch`/`websearch` deny. **PASS**.
- Model tier: Cheap. Live is `opencode-go/minimax-m3` (cheap). **PASS**.
- No skills in frontmatter (procedural). **PASS**.
- No delegation (leaf). **PASS**.
- Use cases realistic. **PASS**.
- Escalation clear. **PASS**.

**Findings:**
- **N1 (Nit).** Live file has no `temperature:` field; local notes this. Add for consistency with other agents that have it.
- **N2 (Nit).** Live file has no `name:` field; cosmetic.

---

## Summary of drift between local synthesis and live agents

| Item | Local says | Live (.opencode) | Live (.claude) | Status |
|---|---|---|---|---|
| `request-classification` skill | ref'd in project-lead | missing in `.opencode/skills/` | present in `.claude/skills/` | Drift (lives in both .opencode/agents/ and .claude/agents/, but only .claude has the skill) |
| `requirement-clarification` skill | ref'd in planning-lead | missing in `.opencode/skills/` | present | Drift |
| `root-cause-analysis` skill | ref'd in fix-lead | missing in `.opencode/skills/` | present | Drift |
| `scope-control` skill | ref'd in build-lead + fix-lead | missing in `.opencode/skills/` | present | Drift |
| `acceptance-decision` skill | ref'd in reviewer | missing in `.opencode/skills/` | present | Drift |
| `project-question-answering` skill | ref'd in project-lead | missing in `.opencode/skills/` | present | Drift |
| Reviewer model | Standard | minimax-m3 (cheap) | opus-4-8 (deep) | **Drift, flagged** in local "What's missing" |
| Fix-lead model | Standard | minimax-m3 (cheap) | opus-4-8 (deep) | **Drift, NOT flagged** in local |
| System-lead model | Standard | minimax-m3 (cheap) | sonnet-4-6 (standard) | **Drift, NOT flagged** |
| Test-lead model | Standard | minimax-m3 (cheap) | sonnet-4-6 (standard) | **Drift, NOT flagged** |
| Research-lead model | Standard | minimax-m3 (cheap) | sonnet-4-6 (standard) | **Drift, NOT flagged** |
| System-lead `websearch` | catalog says deny; live says allow | allow | allow | **Drift, flagged** in local |
| `test-lead` agent "not deployed" | Not deployed in live | **Deployed** (file exists) | Deployed | **False claim** |
| `test-generation` / `test-execution` skills | missing in live | **Present** | Present | **False claim** |
| `committer` in project-lead task list | "should be removed" | still present | still present | Drift, flagged |
| `test-lead` in build-lead/fix-lead task list | "dangling" (per local) | dangling in build; not in fix-lead task list | n/a | Drift, flagged |
| `research-lead` in build-lead/reviewer task list | "added in live vs. catalog — should be in catalog" | present | n/a | Drift, flagged |

---

## Recommendations (priority order)

1. **Fix the R-008 / R-009 misattribution** across `AGENT-SYSTEM-ARCHITECTURE.md`, `project-lead.md`, `system-lead.md`, `fix-lead.md`. Replace every "human gate (R-009)" / "R-009 protected paths" / "R-009-gated" with **R-008**. The system-rules file is the single source.
2. **Fix the test-lead "Not deployed" / "skills missing" claim** in `test-lead.md`. Both are factually wrong. Replace with a true "what's missing" entry — e.g., "no dedicated workflow doc; skill set is present in live."
3. **Replace the model tier table** in `AGENT-SYSTEM-ARCHITECTURE.md` with a tier-only map ("cheap / standard / deep") and reference the canonical catalog (`catalog/config/model_catalog.yaml`) and the tier map (`models.yaml`) for the concrete names. This upholds D-016 and Constitution rules 2, 3, 9.
4. **Resolve the project-lead L3 delegation rule.** Pick one: either the project-lead routes to L2 only (and project-explorer/committer are reached via the build-lead), or document the L1 → L3 exception explicitly ("project-lead may call `project-explorer` and `committer` directly because they are stateless read-only or single-purpose leaves; other leads route through L2").
5. **Choose a target runtime** for the synthesis (or write the synthesis to be runtime-agnostic and add a per-runtime mapping table). The skill set differs between `.opencode/skills/` and `.claude/skills/`. The local docs name skills that don't exist in `.opencode/skills/`.
6. **Flag the model tier drift** in `fix-lead.md`, `system-lead.md`, `test-lead.md`, `research-lead.md` (the reviewer is the only one that flags it). Drift the local synthesis claims is honest about is better than drift it silently papers over.
7. **Reconcile the system-lead `websearch`** with the architecture doc's "deny by default" rule. Either add a documented exception ("system-lead may websearch for current runtime docs; this is the only deviation") or remove `websearch: allow` from the live file.
8. **Cite decisions by ID** in the architecture doc. The synthesis is grounded in D-001…D-018; the doc should say so. This is the same single-source discipline that R-006 / Constitution #3 demand.

---

## Final verdict

**NON-COMPLIANT — must be revised before merge.**

- **Four blockers** (R-008/R-009 misattribution in 4 files, the test-lead false-claim, the model-string hardcoding, the project-lead L3 self-contradiction).
- **Eight to ten warnings** (skill availability across runtimes, model tier drift not consistently flagged, system-lead websearch drift, soft least-privilege on `git add*`).
- **Several nits** (process leakage into the artifact, missing temperature/name fields in leaves, R-008/R-009 attribution habit).

The synthesis is honest about much of its own drift (the per-agent "What's missing" / "Gaps from research" sections are valuable self-critique), and the architecture doc is broadly consistent with CORE_LOOP and the rest of the design. But the four blockers are exactly the kinds of issues a reviewer catches and a builder fixes — they're not "stylistic," they're rule violations. **Recommend: route to a fix that addresses blockers 1–4, then re-review.**
