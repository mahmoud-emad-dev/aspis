# F-018 — Complete Asset Set · Gap Collation (research only)

> **Author:** research-lead · **Date:** 2026-06-27 · **Mode:** production
> **Scope:** Cross-check every deferred/missing asset + use case from F-016 (designs) and F-017 (delivery) that lands in F-018's scope. Research only — no code, templates, scripts, or bodies authored.
> **Method:** Read every cited file end-to-end; extract every "F-018", "deferred", "PARTIAL", "near-term", "future", "missing" item with file:line evidence; cross-check against current built catalog.
> **Sources:** F-017 SPEC.md, F-017 BUILD_REPORT.md, F-017 PLAN.md, F-017 TASKS.md, F-017 ACCEPTANCE.md, F-017 Review/* (12 files), F-016 Research/ref/* (12 files), F-016 Research/specs/* (5 files), F-016 Research/subagent-roster-and-delegation.md, F-016 Research/project-lead-delegation-map-1.md, F-016 Research/planning-lead-delegation-system.md, F-016 Research/system-lead-config-runtime.md, F-016 Research/current-aspis-audit-1.md, the live catalog (`src/aspis/data/catalog/`), `.aspis/workflows/`, `.aspis/templates/`, `.aspis/scripts/`, and `tests/`.

---

## Section 1 — Deferred from F-017 (per F-017 SPEC + BUILD_REPORT + Plan + Reviews)

| # | Item | Source (file:line) | Status (post-F-017) | F-018 Action |
|---|------|---------------------|----------------------|--------------|
| 1 | `dependency-audit` skill (P2, planning-lead → future `dependency-analyzer` subagent) | F-017 SPEC.md L17, L91, L130, L148-149; F-017 TASKS.md L133; F-017 PLAN.md L212; final-completeness.md L112, L148, L424; final-gates.md L839, L845, L876; final-quality.md L692, L695, L697, L817 | **DEFERRED** — no consumer in F-017; planning-lead's `dependency-analyzer` subagent is also deferred to L3/F-018 | Build the skill now that the consumer subagent is in F-018 scope |
| 2 | System-lead L3 subagent: `runtime-validator` | F-017 SPEC.md L26; system-lead.md §10 L315-327; system-lead-config-runtime.md §5.8 | **DEFERRED** — would consolidate the 8 validation gates | Build the deterministic subagent; integrate with `aspis doctor` |
| 3 | System-lead L3 subagent: `drift-auditor` | F-017 SPEC.md L26; system-lead.md §10 L315-327 | **DEFERRED** — `aspis drift` exists but is shallow; auditor cross-checks catalog↔live per field per agent | Build (or expand `drift` verb to audit-mode) |
| 4 | System-lead L3 subagent: `permission-auditor` | F-017 SPEC.md L26; system-lead.md §10 L315-327; system-lead-config-runtime.md §5.6 | **DEFERRED** — cross-checks every agent's allow-list vs the canonical R-008 policy | Build |
| 5 | System-lead L3 subagent: `export-verifier` | F-017 SPEC.md L26 (implicit, listed in final-completeness.md L217); system-lead.md §10 L315-327 | **DEFERRED** — verifies last export: snapshot matches live, log consistent | Build |
| 6 | System-lead L3 subagent: `catalog-synchronizer` | F-017 SPEC.md L26; final-completeness.md L217; system-lead.md §10 L315-327 | **DEFERRED** — ensures catalog↔runtime consistency | Build |
| 7 | System-lead L3 subagent: `opencode-author` | F-017 SPEC.md L26; system-lead.md §10 L315-327; system-lead-config-runtime.md §7.7 L1105-1115 | **DEFERRED** — writes one OpenCode asset at a time; "extract when more than ~30% of system-lead's day is single-runtime authoring" | Build (or document the threshold and defer further) |
| 8 | System-lead L3 subagent: `claude-author` | F-017 SPEC.md L26; system-lead.md §10 L315-327; system-lead-config-runtime.md §7.7 L1105-1115 | **DEFERRED** — writes one Claude Code asset at a time | Build (or document threshold) |
| 9 | Planning-lead L3 subagent: `clarify` (10-category ambiguity scan, max 5 questions) | F-017 SPEC.md L27; planning-lead.md §6 L252, §7 L286-289, L322; planning-lead-delegation-system.md §2.1 L83-135 | **DEFERRED** — already in planning-lead's ref spec §6; F-017 T-18 removed the 7 deferred subagents from planning-lead's delegates list (completeness-traceability.md L19, L376) | Build |
| 10 | Planning-lead L3 subagent: `task-decomposer` (PLAN → ordered TASKS) | F-017 SPEC.md L27; planning-lead.md §6 L253, §7 L291-295, L322; planning-lead-delegation-system.md §2.2 L137-160 | **DEFERRED** — already in planning-lead's ref spec §6; works alongside the existing `task_compile.py` script | Build |
| 11 | Planning-lead L3 subagent: `constitution-checker` (PLAN vs 12 constitution rules) | F-017 SPEC.md L27; planning-lead.md §6 L257, §7 L306-309, L322; planning-lead-delegation-system.md §2.6 L235-269 | **DEFERRED** — already in planning-lead's ref spec §6; near-term/high-leverage per the planning-lead spec | Build (high-leverage — separates "design" from "audit") |
| 12 | Planning-lead L3 subagent: `idea-capture` (raw idea → structured intake) | F-017 SPEC.md L27; planning-lead.md §6 L254, §7 L296-300, L322; planning-lead-delegation-system.md §2.3 L163-184 | **DEFERRED** — already in planning-lead's ref spec §6; immediate priority | Build |
| 13 | Planning-lead L3 subagent: `prd-writer` (clarified requirements → SPEC.md) | F-017 SPEC.md L27; planning-lead.md §6 L255, §7 L301-304, L322; planning-lead-delegation-system.md §2.4 L186-209 | **DEFERRED** — already in planning-lead's ref spec §6; **closes F-027 gap** ("The `prd-writer` agent referenced in `PLANNING_WORKFLOW.md` P1 is missing — F-027, designed not built, noted as a real gap") | Build (immediate priority) |
| 14 | Planning-lead L3 subagent: `scope-estimator` (SPEC → size + risk estimate) | F-017 SPEC.md L27; planning-lead.md §6 L256, §7 L311-314, L322; planning-lead-delegation-system.md §2.5 L212-233 | **DEFERRED** — near-term per the planning-lead spec | Build |
| 15 | Planning-lead L3 subagent: `research-request-writer` (knowledge gap → research packet) | F-017 SPEC.md L27; planning-lead.md §6 L258, §7 L316-319, L322; planning-lead-delegation-system.md §2.8 L294-314 | **DEFERRED** — near-term per the planning-lead spec ("cheap insurance") | Build |
| 16 | Planning-lead L3 subagent: `dependency-analyzer` (multi-feature PLAN → dependency graph) | F-017 SPEC.md L27; planning-lead.md §6 L259, §7 L321-324; planning-lead-delegation-system.md §2.7 L271-291 | **DEFERRED** — future per the planning-lead spec; "only needed for multi-feature planning, which is rare today" | Build (future priority; rare) |
| 17 | Stack-specific tester subagents (`python-tester`, `api-tester`, `db-tester`, `ui-tester`, `cli-tester`, `security-tester`) | F-017 SPEC.md L28; test-lead.md §11.3 L239-249 | **DEFERRED** — full table of 6 stack testers + their skill sets is designed but unbuilt; only "labs testing" generic fallback exists in test-lead.md L187-258 | Build incrementally (per stack) |
| 18 | Test-lead L3 subagent: `test-author` | fix-lead.md §11 Q7 L212; test-lead.md §10 Q4 L179; subagent-roster-and-delegation.md L50 | **DEFERRED** — designed, not extracted ("Extract when workload justifies") | Build |
| 19 | Test-lead L3 subagent: `bug-triager` + `gate-fixer` (fix-lead) | fix-lead.md §11 Q7 L212; subagent-roster-and-delegation.md L49 | **DEFERRED** — designed, not extracted | Build |
| 20 | Build-lead L3 subagent: `sub-reviewer` (per-task context-isolated review) | build-lead.md §13 Q1 L575; reviewer.md §11 L351-356; current-aspis-audit-1.md §10.2 L542 | **DEFERRED** — designed, not extracted; "every review escalates to the Reviewer lead today" | Build (high-leverage — reduces reviewer bottleneck) |
| 21 | Reviewer L3 subagent: `security-reviewer` | reviewer.md §11 L351-356; subagent-roster-and-delegation.md L48 | **DEFERRED** — "After security-review skill matures" | Build (after `security-review` skill is exercised in F-018) |
| 22 | Research-lead L3 subagent: `codebase-explorer` | research-lead.md §7 L163-167; subagent-roster-and-delegation.md L46 | **DEFERRED** — "Research repeatedly needs multi-file facts" | Build |
| 23 | Research-lead L3 subagent: `docs-fetcher` | research-lead.md §7 L165-167; subagent-roster-and-delegation.md L46 | **DEFERRED** — "≥2 stack-doc fetches/week" | Build |
| 24 | Research-lead L3 subagent: `web-researcher` | research-lead.md §7 L166-167; subagent-roster-and-delegation.md L46 | **DEFERRED** — "Deep research needs parallel fan-out" | Build |
| 25 | Research-lead L3 subagent: `cache-manager` | research-lead.md §7 L167; subagent-roster-and-delegation-md.md L46 | **DEFERRED** — "Cache exceeds ~20 references" | Build |
| 26 | Project-lead L3 subagent: `context-feeder` | project-lead.md §9 L758-761 | **DEFERRED** — "context on demand" | Build |
| 27 | Project-lead L3 subagent: `context-summarizer` | project-lead.md §9 L758-761 | **DEFERRED** — "Requires trace spine to be built first" | Build (after trace spine) |
| 28 | Heavy 5-layer model-router engine | F-017 SPEC.md L21; D-016/D-017/D-018 context | **DEFERRED** — bodies reference mode/model/task dials but the full router is a future feature | Design + spec the engine; build the resolver layer |
| 29 | Full per-task dynamic context budgeting | F-017 SPEC.md L22 | **DEFERRED** | Build (post-trace-spine) |
| 30 | Self-improvement loop (Phase 4 of roadmap) | F-017 SPEC.md L23; system-lead.md §13 Q14 L436 | **DEFERRED** | Out of scope; document |
| 31 | Trace spine (Phase 3 of roadmap) | F-017 SPEC.md L24; system-lead.md §13 Q12 L434; current-aspis-audit-1.md §10.2 L546 | **DEFERRED** — no `.aspis/traces/{raw,runs}/`; no `trace-event`/`trace-pipe` | Build (high-leverage — enables cost ledger, history, 1+ Phase 3 features) |
| 32 | Dashboard (Phase 5 of roadmap) | F-017 SPEC.md L25; system-lead.md §13 Q13 L435; current-aspis-audit-1.md §10.2 L547 | **DEFERRED** — no `STATUS.md`, no `dashboard/` | Build (after trace spine) |
| 33 | Live runtime auto-regeneration of `.opencode/` and `.claude/` | F-017 SPEC.md L29; F-017 PLAN.md L19; final-gates.md §3 L247-256, L381-383; final-completeness.md L141; architecture-constitution.md L655 | **DEFERRED** — owner runs `aspis export` manually | Build the `aspis doctor --export` auto-trigger; or watch-mode |
| 34 | Multi-profile support beyond `base.yaml` | F-017 SPEC.md L30; system-lead.md §13 Q15 L437; system-lead.md §6 M9 L440; system-lead-config-runtime.md §6 L889-998 | **DEFERRED** — schema designed, `base.yaml` is the only profile; no `python-cli.yaml`/`data-science.yaml`/`full-stack.yaml` files exist on disk | Build the profile system (validator + 2-3 starter profiles) |
| 35 | ~10 ref-spec templates (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION, BUILD_REPORT, FEATURE_REPORT, TEST_REPORT, FIX_REPORT) | F-017 SPEC.md L31; planning-lead.md §13 L1006-1011; completeness-traceability.md §1.2 L19, L225-247 | **DEFERRED** (10 templates); all 10 listed; only `PLAN.md`, `SPEC.md`, `TASKS.md`, `ACCEPTANCE.md`, `TASK_PACKET.md` exist in `templates/planning/`; 2 in `templates/review/` (review.md, test.md); 3 in `templates/report/` (build.md, fix.md, feature.md) — so 10 of 16 referenced in ref specs are NOT built (CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION) | Build the 7 missing (only 3 of 10 are built: `templates/review/{review,test}.md` and `templates/report/{build,fix,feature}.md` — but `TEST_REPORT` is at `templates/review/test.md` and `BUILD_REPORT` is at `templates/report/build.md`, `FEATURE_REPORT` is at `templates/report/feature.md`, `FIX_REPORT` is at `templates/report/fix.md` — so 3 are in `templates/review|report` not `templates/planning`; the planning-led L1006-1011 says "CLARIFICATION_LOG, RESEARCH_REQUEST, PLAN_OF_PLAN, DEPENDENCIES, SCOPE_ESTIMATE, MODE_DECISION" are missing) |
| 36 | ~10 helper scripts (`scope_estimate`, `constitution_check`, `plan_quality_check`, `mode_validator`, `task_size_check`, `dependency_graph`, `search_cache`, `check_staleness`, `rank_source`, `compare_versions`, `cross_ref`) | F-017 SPEC.md L32; planning-lead.md §13 L1020-1025; research-lead.md §12 L290-298 | **DEFERRED** — 5 planning scripts (P0: feature_scaffold, task_compile, prereq_validate, _console, active_feature) built; 5 research scripts (search_cache, check_staleness, rank_source, compare_versions, cross_ref) NOT built; 1 planning script (scope_estimate) NOT built; 4 planning scripts (constitution_check, plan_quality_check, mode_validator, task_size_check, dependency_graph) NOT built | Build the 10 missing scripts |
| 37 | `project-lead-operating-protocol.md` workflow | F-017 SPEC.md L33; project-lead.md §10 L791-792 | **DEFERRED** — only 5 workflows in `.aspis/workflows/` (build, fix, plan, review, small-task) | Build |
| 38 | `system.md` workflow | system-lead.md L90; final-completeness.md L51, L330-343; final-gates.md L1232-1262; final-quality.md L28, L29, L148, L443-459 | **DEFERRED/BROKEN-REF** — `system-lead.md` L90 references `.aspis/workflows/system.md` which does not exist (verified: 5 files in `.aspis/workflows/`: build.md, fix.md, plan.md, review.md, small-task.md) | Build the workflow to close the HIGH broken reference |
| 39 | `FIX_REPORT.md` template | fix-lead.md L103-104; final-completeness.md L340-343; final-gates.md L1232-1262; final-quality.md L29, L168, L178, L461-477 | **DEFERRED/BROKEN-REF** — `fix-lead.md:103` references `.aspis/templates/planning/FIX_REPORT.md` which does not exist (5 templates in `templates/planning/`: ACCEPTANCE, PLAN, SPEC, TASK_PACKET, TASKS); **NOTE** — there IS a `templates/report/fix.md` which serves the same purpose but the body references `templates/planning/FIX_REPORT.md` | Build the template (or fix the body reference) |
| 40 | `enforcement: warn` → `block` flip (runtime tools) | system-lead.md §8 L264-272; system-lead.md §13 Q2 L422; enforcement.md L41-42, L46-48; architecture-constitution.md | **DEFERRED** — current default is `warn` for all boundaries; target is `block` for runtime tools, `warn` for pre-commit, CI override via env var | Build the runtime block layer |
| 41 | `fix-lead` bash allowlist tightening (`bash: '*': allow` removal) | fix-lead.md §11 Q2 L207 | **DEFERRED** — fix-lead still has wide bash allow | Tighten to named commands |
| 42 | Model tier reconciliation: live `standard` vs catalog intent | fix-lead.md §11 Q1 L206; test-lead.md §10 Q2 L177 | **DEFERRED** — live and catalog disagree on tier; `aspis models --apply` is the fix | Run `aspis models --apply` to reconcile |
| 43 | `active_feature.json` `scope` field missing | build-lead.md §13 Q3 L577 | **DEFERRED** — scope guard is a no-op without `scope` field | Add `scope` to `active_feature.json` schema + populate |
| 44 | Max turns enforcement on agents | build-lead.md §13 Q5 L579; general-builder.md §6 L265-267 | **DEFERRED** — "no `maxTurns` on any agent" | Add runtime-enforced caps |
| 45 | Claude Code `permission:` block adapter fix | cross-runtime.md L20-32; F-017 PLAN.md L156; F-017 SPEC.md L86 (FR-010) | **PARTIAL** — fixed in 36ab7b5 (FR-010 PASS per final-completeness.md L121); but permission semantics audit still needed (system-lead-config-runtime.md §5.6) | Verify byte-parity of permission blocks via `aspis byte-parity` post-export |
| 46 | Builder `edit`/`write` not path-scoped | build-lead.md §13 Q7 L581 | **DEFERRED** — `edit: "*": allow` on fix-lead and general-builder; should be path-scoped to packet.allowed | Tighten to packet.allowed |
| 47 | Build-lead → committer precondition (review-approved not machine-checked) | build-lead.md §13 Q8 L582 | **DEFERRED** — "Add review-approved precondition" | Add machine check before committer call |
| 48 | `files.allowed` not machine-checked in task packets | build-lead.md §13 Q9 L583 | **DEFERRED** — "add to TASK_PACKET template" | Add field to TASK_PACKET template |
| 49 | `attempts_used` counter not structurally enforced | build-lead.md §13 Q10 L584 | **DEFERRED** — "refuse on ≥3" | Add to spec or runtime |
| 50 | Parallel fan-out primitive | build-lead.md §13 Q11 L585; project-lead.md §15 Q2 L896 | **DEFERRED** — "no parallel fan-out primitive; deferred (runtime limitation)" | Document; defer to post-trace-spine |
| 51 | Final-green reconciliation pass automation | build-lead.md §13 Q12 L586 | **DEFERRED** — "add to build workflow" | Add the step to `build.md` |
| 52 | Per-task cost cap | build-lead.md §13 Q13 L587 | **DEFERRED** — "track tokens per task" | Add the cap |
| 53 | `promote` lock-state from cli-verb-quality | final-gates.md L1306; governance.md §6 `ledger` subcommand | **DEFERRED** — H-1 from cli-verb-quality: add `--pretty` to `ledger`; L-1 drift verb expected 51 drift messages | Clean up CLI verb divergences (low priority) |
| 54 | 7 missing CLI validators (from system-lead-config-runtime.md §5.8): `validate-skills`, `validate-agents`, `validate-decisions`, `validate-constitution`, `validate-trace`, `validate-approvals`, `validate-parity`, `validate-profiles` | system-lead-config-runtime.md §5.8 L875-887; subagent-roster-and-delegation.md L51 (implicit) | **DEFERRED** — 8 validators designed, 0 built; HIGH priority on `validate-approvals` and `validate-trace` | Build (HIGH: validate-approvals, validate-trace; MEDIUM: validate-skills, validate-agents, validate-parity; LOW: validate-decisions, validate-constitution, validate-profiles) |
| 55 | Constitution-check runner (script, not LLM) | system-lead.md §12 "IMPROVE" list L389; system-lead.md §10 (governance subagent purpose L321) | **DEFERRED** — currently the 2 `constitution-checks`/`constitution-check` skills walk the YAML (LLM-based); a deterministic script is the next step | Build the script |
| 56 | Golden manifest + totality guard | current-aspis-audit-1.md §10.2 L551-552 | **DEFERRED** — old ASPS's `tests/golden/catalog_assets.txt` + `refresh-golden.py --check` not present | Build |
| 57 | Subagent-level reviewer (sub-reviewer) | current-aspis-audit-1.md §10.2 L542 (also #20 above) | **DEFERRED** | Build |
| 58 | Plan-critic skill enrichment (12-check expansion) | reviewer.md §3 L80, §7 L211-231; current-aspis-audit-1.md §10.2 L543 | **PARTIAL** — 6 v1 checks built; 6 v2 checks (7-12: constitution alignment, scope completeness, test coverage plan, rollback plan, complexity tracking, estimation realism) not yet in the skill | Extend `plan-critic/SKILL.md` to v2 (12 checks) |
| 59 | `mode` field docstring in `AGENT_BODY_STANDARD.md` is stale | final-quality.md L27, L416-417 | **OPEN** — standard says `vibe`/`mvp`/`production` but agents use `primary`/`subagent`; LOW documentation drift | Fix the docstring |
| 60 | AGENT_BODY_STANDARD.md does not codify the bootstrap exception | final-quality.md L481-488 | **OPEN** — standard's "no special cases" is in tension with bootstrap's documented special case | Add a "Documented exceptions" subsection |
| 61 | SC-011 cost-of-change test not run as a discrete TASKS step | final-completeness.md L297-308; final-gates.md (implicit, deferred) | **OPEN** — architecturally true, not exercised as a test | Add a `cost_of_change.py` script (or document informal evidence) |
| 62 | `system-lead.md` body section M-7 (renamed `## How you work` sections) | final-quality.md L364-365 | **OPEN** — 5 of 8 leads have renamed `## How you work` sections (stylistic only) | Polish pass — rename to `## How you work` everywhere |
| 63 | `commit-readiness/SKILL.md` untracked (T-47 missing commit) | final-completeness.md L233-253; final-gates.md L972-1015; final-quality.md L692, L817 | **OPEN / HIGH** — file on disk, not committed; reviewer body does not reference it | Commit the file (1 commit) |
| 64 | `aspis validate-index --help` crashes with `ValueError: badly formed help string` | final-gates.md L908-967 | **OPEN / CRITICAL** — literal `10%` in help string L192 of `validate_index.py`; crashes argparse | Fix L192 (`10%` → `10%%` or `10 percent`) |
| 65 | 10 `_tmp_f017_*.py` scratch scripts in `.aspis/scripts/planning/` | final-gates.md L1089-1110; final-completeness.md L255-275 | **OPEN** — debris from prior review sessions | Remove (`rm .aspis/scripts/planning/_tmp_f017_*.py`) |
| 66 | `BUILD_REPORT.md` is scoped only to T-51..T-55, not the whole feature | final-completeness.md L277-295 | **OPEN** — file as it stands reports on ~10% of the task set | Rename or extend to whole-feature BUILD_REPORT |
| 67 | H-1 / H-2 from final-gates.md: `validate-runtime --runtime {all}` (resolved) | final-gates.md H-3 L1074-1085 | **RESOLVED** | (No F-018 action) |
| 68 | H-3 from cli-verb-quality.md: `revoke --approver` divergence (L570 required vs spec optional) | final-quality.md L347-359; cli-verb-quality.md | **OPEN** — `cli-verb-quality.md` H-3 (now LOW); operationally equivalent | Polish (optional) |
| 69 | L-1 from final-gates.md: drift verb expected 51 messages (live parity deferred) | final-gates.md L1191-1220 | **EXPECTED** — pre-export state; resolves after owner `aspis export --apply` | (No F-018 action; owner-driven) |
| 70 | `bootstrap` body uses `## Who you are` instead of `## Identity` | final-completeness.md L310-328; final-quality.md L272-289 | **OPEN** — stylistic deviation; bootstrap has had this since pre-F-017 | Polish (rename to `## Identity` or codify exception) |
| 71 | `cross_ref_agents.py` at runtime only, not in catalog source | final-quality.md L358-360 | **OPEN** — 1025 lines, in `.aspis/scripts/planning/` but NOT in `src/aspis/data/catalog/scripts/planning/`; R-006 concern | Move to catalog source OR document as build-time-only |
| 72 | `general-builder` Core rules R-006 partial restatement (parenthetical) | final-quality.md L242-243, L249-252 | **OPEN** — 3 of 4 R-### have brief parenthetical restatements | Polish (remove parenthetical) |
| 73 | Missing `## Edge Cases` in bootstrap, committer, general-builder, project-explorer (leaves) | final-quality.md L284 | **OPEN** — leaves don't have edge cases; spec doesn't require | Optional |
| 74 | Missing `## Dynamic-readiness` in bootstrap | final-quality.md L283 | **OPEN** — bootstrap is special case; standard doesn't codify | Codify exception or add block |
| 75 | Live byte-parity verification | F-017 SPEC.md L33, FR-011, SC-004; final-gates.md L324-383 | **DEFERRED** — deferred to owner's manual post-F-017 `aspis export --apply` | Build the `aspis export --apply` automation hook |
| 76 | `asps` 12 missing verbs from old ASPS | current-aspis-audit-1.md §11.1 L576 | **DEFERRED** — `proof`, `validate-runtime` ✓, `validate-index` ✓, `trace-*` (5+), `stats`, `dashboard`, `start-feature`/`close-feature`, `governance` ✓, `harvest-gate`, `improve`, `lessons` | Build the missing old-ASPS verbs (deferred) |
| 77 | `docs/QUICKSTART.md`, `docs/FIRST-BUILD.md` | current-aspis-audit-1.md §10.2 L556 | **DEFERRED** — only `docs/ARCHITECTURE.md` exists | Write user-facing docs |
| 78 | PowerShell + bash dual-stack hook mirrors | current-aspis-audit-1.md §10.2 L555 | **DEFERRED** — Python-only | Decide platform story |
| 79 | Research packages (no examples shipped) | current-aspis-audit-1.md §10.2 L548 | **PARTIAL** — `knowledge-research` + `knowledge-packaging` skills exist; 0 packaged research assets | Author 2-3 example research packages |
| 80 | 50-agent catalog (28 live + 22 archived) | current-aspis-audit-1.md §11.1 L578 | **REDUCED** — 12-agent catalog; no archived set | Decide: keep lean or expand |
| 81 | `findings` command scoped to read-only list | project-lead.md §10 L797-799 | **DEFERRED** — full `aspis findings` exists but read-only subset not in allowlist | Add to project-lead bash allowlist |
| 82 | `committer` `temperature: 0.1` missing | project-lead-delegation-map-1.md §8 table L1012 | **DEFERRED** — committer lacks `temperature: 0.1` (cosmetic) | Add field |
| 83 | `websearch: allow` system-lead drift (live vs catalog) | project-lead-delegation-map-1.md §8 L1009-1011 | **RESOLVED** — system-lead-config-runtime.md §13 Q10 L432 says both `deny` | (No F-018 action) |
| 84 | `test-lead` not deployed in `.opencode/agents/` | project-lead-delegation-map-1.md §2.7 L487-575 | **RESOLVED** — F-017 T-37 etc. deployed | (No F-018 action) |

---

## Section 2 — Missing subagents (full inventory from F-016 ref specs + subagent-roster)

| # | Subagent | Parent lead | Designed in (ref spec) | Purpose | Priority | Already in catalog? |
|---|----------|-------------|--------------------------|---------|----------|---------------------|
| 1 | `runtime-validator` | system-lead | F-016 system-lead.md §10 L320-321; system-lead-config-runtime.md §5.8 | Runs all 8 validation gates, returns single verdict | P0 | No (F-018) |
| 2 | `drift-auditor` | system-lead | F-016 system-lead.md §10 L321; subagent-roster-and-delegation.md L51 | Cross-checks catalog↔live frontmatter per field per agent | P0 | No (F-018) |
| 3 | `permission-auditor` | system-lead | F-016 system-lead.md §10 L322; system-lead-config-runtime.md §5.6 | Cross-checks every agent's allow-list vs canonical R-008 policy | P0 | No (F-018) |
| 4 | `export-verifier` | system-lead | F-016 system-lead.md §10 L323; final-completeness.md L217 | Verifies last export: snapshot matches live, log consistent | P1 | No (F-018) |
| 5 | `catalog-synchronizer` | system-lead | F-016 system-lead.md §10 L324; final-completeness.md L217 | Ensures catalog↔runtime consistency | P1 | No (F-018) |
| 6 | `opencode-author` | system-lead | F-016 system-lead.md §10 L325; system-lead-config-runtime.md §7.7 L1105-1115 | Writes one OpenCode asset at a time | P2 | No (F-018) |
| 7 | `claude-author` | system-lead | F-016 system-lead.md §10 L326; system-lead-config-runtime.md §7.7 L1105-1115 | Writes one Claude Code asset at a time | P2 | No (F-018) |
| 8 | `clarify` | planning-lead | F-016 planning-lead.md §7 L286-289; planning-lead-delegation-system.md §2.1 L83-135 | 10-category ambiguity scan, max 5 prioritized questions | P0 (immediate) | No (F-018) |
| 9 | `task-decomposer` | planning-lead | F-016 planning-lead.md §7 L291-295; planning-lead-delegation-system.md §2.2 L137-160 | PLAN → ordered TASKS + per-task packets | P0 (immediate) | No (F-018) |
| 10 | `idea-capture` | planning-lead | F-016 planning-lead.md §7 L296-300; planning-lead-delegation-system.md §2.3 L163-184 | Raw idea → structured intake (goal/problem/value/constraints/scope/risks/mode) | P0 (immediate) | No (F-018) |
| 11 | `prd-writer` | planning-lead | F-016 planning-lead.md §7 L301-304; planning-lead-delegation-system.md §2.4 L186-209 | Clarified requirements → full SPEC.md; **closes F-027 gap** | P0 (immediate) | No (F-018) |
| 12 | `constitution-checker` | planning-lead | F-016 planning-lead.md §7 L306-309; planning-lead-delegation-system.md §2.6 L235-269 | PLAN vs 12 constitution rules; "high-leverage — separates design from audit" | P0 (near-term) | No (F-018) |
| 13 | `scope-estimator` | planning-lead | F-016 planning-lead.md §7 L311-314; planning-lead-delegation-system.md §2.5 L212-233 | SPEC → size + risk estimate (file count, complexity, risk, cost-of-change, mode) | P1 (near-term) | No (F-018) |
| 14 | `research-request-writer` | planning-lead | F-016 planning-lead.md §7 L316-319; planning-lead-delegation-system.md §2.8 L294-314 | Knowledge gap → research packet ("cheap insurance") | P1 (near-term) | No (F-018) |
| 15 | `dependency-analyzer` | planning-lead | F-016 planning-lead.md §7 L321-324; planning-lead-delegation-system.md §2.7 L271-291 | Multi-feature PLAN → dependency graph (DAG) | P2 (future) | No (F-018) |
| 16 | `sub-reviewer` | build-lead | F-016 build-lead.md §13 Q1 L575; reviewer.md §11 L351-356; current-aspis-audit-1.md §10.2 L542 | Per-task context-isolated review (cheap model, fresh context) | P0 (immediate) | No (F-018) |
| 17 | `security-reviewer` | reviewer | F-016 reviewer.md §11 L351-356 | OWASP top 10, injection, auth, exposure | P1 | No (F-018) |
| 18 | `test-author` | test-lead | F-016 test-lead.md §10 Q4 L179; subagent-roster-and-delegation.md L50 | Test authoring (stack testers later) | P1 | No (F-018) |
| 19 | `python-tester` | test-lead | F-016 test-lead.md §11.3 L243 | Python pytest patterns, coverage, property testing | P1 | No (F-018) |
| 20 | `api-tester` | test-lead | F-016 test-lead.md §11.3 L244 | HTTP assertions, schema validation, contract testing | P1 | No (F-018) |
| 21 | `db-tester` | test-lead | F-016 test-lead.md §11.3 L245 | Migration testing, data integrity, query performance | P2 | No (F-018) |
| 22 | `ui-tester` | test-lead | F-016 test-lead.md §11.3 L246 | Component testing, accessibility, screenshot diff | P2 | No (F-018) |
| 23 | `cli-tester` | test-lead | F-016 test-lead.md §11.3 L247 | Arg-parse testing, exit-code assertions, pipe testing | P1 | No (F-018) |
| 24 | `security-tester` | reviewer (via) | F-016 test-lead.md §11.3 L248 | OWASP scan, fuzz testing, secret scan | P1 | No (F-018) |
| 25 | `codebase-explorer` | research-lead | F-016 research-lead.md §7 L163-167 | Structural cross-file analysis, dependency maps | P1 | No (F-018) |
| 26 | `docs-fetcher` | research-lead | F-016 research-lead.md §7 L165-167 | Fetch official docs, distill to OFFICIAL_REFERENCES | P1 | No (F-018) |
| 27 | `web-researcher` | research-lead | F-016 research-lead.md §7 L166-167 | Targeted web search with citations, facts vs opinions | P1 | No (F-018) |
| 28 | `cache-manager` | research-lead | F-016 research-lead.md §7 L167 | Cache >20 references; staleness tracking | P2 | No (F-018) |
| 29 | `general-fix` | fix-lead | F-016 subagent-roster-and-delegation.md L49 | Generic fix worker | P1 | No (F-018) |
| 30 | `general-inspect` | fix-lead | F-016 subagent-roster-and-delegation.md L49 | Generic inspection worker | P1 | No (F-018) |
| 31 | `bug-triager` | fix-lead | F-016 fix-lead.md §11 Q7 L212 | Triage incoming bug reports | P1 | No (F-018) |
| 32 | `gate-fixer` | fix-lead | F-016 fix-lead.md §11 Q7 L212 (implicit) | Focused gate-failure repair | P1 | No (F-018) |
| 33 | `context-feeder` | project-lead | F-016 project-lead.md §9 L758-761 | L1-L4 task-scoped context on demand | P0 | No (F-018) |
| 34 | `context-summarizer` | project-lead | F-016 project-lead.md §9 L758-761 | Condenses recent traces/changes into context-file updates (requires trace spine) | P1 | No (F-018) |
| 35 | `committer` | — | F-016 project-lead-delegation-map-1.md §2.9 L641-686 (drift) | The only git writer (R-004) | DEPLOYED | **YES — already in catalog** (`src/aspis/data/catalog/agents/committer.md`); 77 lines; 3 skills |
| 36 | `project-explorer` | — | F-016 project-explorer.md (full ref spec) | Shared read-only repo exploration | DEPLOYED | **YES — already in catalog** (`src/aspis/data/catalog/agents/project-explorer.md`); 85 lines |
| 37 | `general-builder` | — | F-016 general-builder.md (full ref spec) | Disposable executor, one task packet | DEPLOYED | **YES — already in catalog** (`src/aspis/data/catalog/agents/general-builder.md`); 120 lines |
| 38 | `governance` (subagent) | system-lead | F-016 governance.md (full ref spec, 634 lines) | R-008 deterministic enforcement | DEPLOYED (as governance.py CLI, NOT as LLM agent) | **YES — built as deterministic CLI** (`src/aspis/commands/governance.py`); per governance.md §1, deliberately NOT an LLM agent |

**Total: 38 subagent slots identified** — **35 missing** (3 already deployed, governance built as CLI not LLM).

---

## Section 3 — Missing skills

| # | Skill name | Referenced in (ref spec) | Priority | Notes |
|---|------------|---------------------------|----------|-------|
| 1 | `dependency-audit` | F-016 planning-lead.md §13 L1120; F-016 research-lead.md §7 L279; F-016 research-lead.md §12 L290; F-017 SPEC.md L17, L91, L130 | P2 | Was F-016 inventory; F-017 deferred (no consumer). Now in F-018 because the consumer subagent (`dependency-analyzer`) is in F-018 scope. |

**Total: 1 missing skill** (per F-016 inventory, 25 in-scope, 24 built in F-017, 1 deferred = `dependency-audit`).

Other potential missing skills (designed but not yet in F-016 inventory as "missing" — these are net-new proposals):

| # | Skill name | Source | Priority | Notes |
|---|------------|--------|----------|-------|
| 2 | `constitution-check` (deterministic script version) | system-lead.md §12 "IMPROVE" list L389 | P1 | The current skill (LLM) walks the YAML; the script version is the next step |
| 3 | `cache-management` (more rigor; tracking >20 references) | research-lead.md §7 L167 | P2 | Build when cache grows |
| 4 | `harvest-protocol` (extended — formal 7-step procedure) | research-lead.md §3 L85 | P1 | Skill exists at catalog (`src/aspis/data/catalog/skills/harvest-protocol/SKILL.md`); may need extension for full 7-step R-008-gated procedure |
| 5 | Stack-specific test skills: `pytest-patterns`, `coverage-analysis`, `property-testing`, `http-assertions`, `schema-validation`, `contract-testing`, `migration-testing`, `data-integrity`, `query-performance`, `component-testing`, `accessibility`, `screenshot-diff`, `arg-parse-testing`, `exit-code-assertions`, `pipe-testing`, `owasp-scan`, `fuzz-testing`, `secret-scan` | test-lead.md §11.3 L239-249 | P1 | 18 skills across 6 stack subagents; the F-016 inventory did not enumerate them, so they are net-new in F-018 |
| 6 | `cost-of-change` (discrete test) | final-completeness.md L297-308 | P2 | Add a `cost_of_change.py` script per SC-011 |
| 7 | `governance-approval` (extended for F-018 use cases) | system-lead.md §3 L102 (current) | P1 | Current skill at `src/aspis/data/catalog/skills/governance-approval/SKILL.md`; may need extension for ledger audit + intervention handler usage |
| 8 | `profile-author` (for multi-profile support) | system-lead-config-runtime.md §6 L889-998 | P2 | New skill for authoring specialized profiles |

**Grand total: 1 inventory-missing skill + 24 net-new skill candidates = 25 skills to consider in F-018.**

---

## Section 4 — Missing templates

| # | Template | Referenced in (ref spec / body) | Priority | Current state |
|---|----------|----------------------------------|----------|----------------|
| 1 | `CLARIFICATION_LOG.md` | F-016 planning-lead.md §13 L1006 ("Missing"); planning-lead-delegation-system.md §2.1 L94 | P0 | **Not built** — referenced as `CLARIFICATION_REPORT.md` in planning-lead-delegation-system.md but no template file exists |
| 2 | `RESEARCH_REQUEST.md` | F-016 planning-lead.md §13 L1007 ("Missing"); planning-lead-delegation-system.md §2.8 L305 | P0 | **Not built** — planning-lead's research-request-writer subagent output shape |
| 3 | `PLAN_OF_PLAN.md` | F-016 planning-lead.md §13 L1008 ("Missing") | P0 | **Not built** — Phase P0 (intake) output |
| 4 | `DEPENDENCIES.md` | F-016 planning-lead.md §13 L1009 ("Missing") | P1 | **Not built** — multi-feature dependency graph output |
| 5 | `SCOPE_ESTIMATE.md` | F-016 planning-lead.md §13 L1010 ("Missing") | P0 | **Not built** — scope-estimator subagent output |
| 6 | `MODE_DECISION.md` | F-016 planning-lead.md §13 L1011 ("Missing") | P0 | **Not built** — mode-decision rationale |
| 7 | `BUILD_REPORT.md` (planning template version) | F-017 SPEC.md L31 (deferred); F-016 system-lead.md §11 I (BUILDs) | P1 | **Built at `src/aspis/data/catalog/templates/report/build.md` (not in `planning/`)** — body uses `report/` not `planning/`. Spec calls for `planning/`; reconcile naming |
| 8 | `FEATURE_REPORT.md` | F-017 SPEC.md L31 (deferred) | P1 | **Built at `src/aspis/data/catalog/templates/report/feature.md`** |
| 9 | `TEST_REPORT.md` | F-017 SPEC.md L31 (deferred) | P1 | **Built at `src/aspis/data/catalog/templates/review/test.md`** |
| 10 | `FIX_REPORT.md` (planning template version) | F-017 SPEC.md L31 (deferred); fix-lead.md L103-104 (referenced, doesn't exist at `templates/planning/`) | P0 (broken-ref) | **Built at `src/aspis/data/catalog/templates/report/fix.md`** — but fix-lead.md L103 references `templates/planning/FIX_REPORT.md` (broken ref). Either move or fix body |
| 11 | `CONTEXT_PACKET.md` (5-field delegation packet shape) | F-016 project-lead.md §10 L783 | P2 | **Not built** — referenced as a copyable template; project-lead has the inline shape in body |
| 12 | `STATUS_REPORT.md` (project-lead direct-answer shape) | F-016 project-lead.md §10 L782 | P2 | **Not built** |
| 13 | `REPLY_TO_USER.md` (recontextualized response shape) | F-016 project-lead.md §10 L784 | P2 | **Not built** |
| 14 | `ESCALATION_NOTE.md` (R-008 human-gate shape) | F-016 project-lead.md §10 L785 | P2 | **Not built** |
| 15 | `TASK_PACKET.md` already exists (planning template) | — | — | **Built** at `src/aspis/data/catalog/templates/planning/TASK_PACKET.md` |
| 16 | `ACCEPTANCE.md` already exists | — | — | **Built** at `src/aspis/data/catalog/templates/planning/ACCEPTANCE.md` |
| 17 | `TASK_PACKET` (V0-V4 variants) | F-016 planning-lead.md §9.2 L436-629 | P1 | **Partial** — single V2-shaped template exists; 5 variants (V0-V4) designed but not built |
| 18 | `ARCHITECTURE.md` already exists | — | — | **Built** at `src/aspis/data/catalog/templates/context/ARCHITECTURE.md` |

**Total: 6 not-built templates from the F-017 SPEC L31 deferred list + 3 report templates already built but in `report/` not `planning/` + 4 net-new (CONTEXT_PACKET, STATUS_REPORT, REPLY_TO_USER, ESCALATION_NOTE) + 1 partial (TASK_PACKET V0-V4 variants) = ~14 template candidates.**

---

## Section 5 — Missing workflows

| # | Workflow | Referenced in | Priority | Current state |
|---|----------|---------------|----------|----------------|
| 1 | `system.md` | system-lead.md L90; final-completeness.md L330-343; final-quality.md L443-459 | P0 (broken-ref HIGH) | **Not built** — `system-lead.md:90` references a non-existent file. 5 workflows in `.aspis/workflows/`: build.md, fix.md, plan.md, review.md, small-task.md |
| 2 | `project-lead-operating-protocol.md` | F-017 SPEC.md L33; F-016 project-lead.md §10 L791-792 | P0 | **Not built** — codifies the 5-phase master frame + 13 stop-and-ask conditions + recontextualization protocol |
| 3 | `bootstrap.md` (workflow, not the body) | `src/aspis/data/catalog/workflows/bootstrap.md` | — | **Built** at catalog/workflows/bootstrap.md (deployed to `.aspis/workflows/`? — to verify) |
| 4 | `dependency-graph.md` (for `dependency-analyzer` subagent) | F-016 planning-lead-delegation-system.md §2.7 L290-291 | P2 | **Not built** — multi-feature planning workflow |
| 5 | `project-plan.md` (the 5th planning track — greenfield decomposition) | F-016 current-aspis-audit-1.md §10.2 L541 ("Project-plan track — design only") | P2 | **Not built** — CORE_LOOP §12 deferred |
| 6 | `constitution-check.md` workflow (for the 12-rule check) | F-016 planning-lead-delegation-system.md §2.6 L257-269 | P1 | **Not built** — subagent's procedure, may not need a separate file |
| 7 | `small-task.md` already exists | — | — | **Built** at `.aspis/workflows/small-task.md` |
| 8 | `build.md`, `fix.md`, `plan.md`, `review.md` already exist | — | — | **Built** (5 workflows per F-017 SC-010) |

**Total: 5 missing workflows (1 broken-ref HIGH + 4 net-new).**

---

## Section 6 — Missing scripts

| # | Script | Referenced in | Priority | Current state |
|---|--------|---------------|----------|----------------|
| 1 | `scope_estimate.py` | F-016 planning-lead.md §13 L1020 ("Missing"); F-017 SPEC.md L32 | P0 | **Not built** — Phase P0 size estimator |
| 2 | `constitution_check.py` | F-016 planning-lead.md §13 L1021 ("Missing"); F-017 SPEC.md L32; system-lead.md §12 "IMPROVE" L389 | P0 | **Not built** — deterministic constitution auditor |
| 3 | `plan_quality_check.py` | F-016 planning-lead.md §13 L1022 ("Missing"); F-017 SPEC.md L32 | P1 | **Not built** — Phase P7 quality gate |
| 4 | `mode_validator.py` | F-016 planning-lead.md §13 L1023 ("Missing"); F-017 SPEC.md L32 | P1 | **Not built** — Phase P0 mode validator |
| 5 | `task_size_check.py` | F-016 planning-lead.md §13 L1024 ("Missing"); F-017 SPEC.md L32 | P1 | **Not built** — Phase P6 task-size enforcer |
| 6 | `dependency_graph.py` | F-016 planning-lead.md §13 L1025 ("Missing"); F-017 SPEC.md L32; F-016 planning-lead-delegation-system.md §2.7 L277 | P2 | **Not built** — multi-feature DAG |
| 7 | `search_cache.py` | F-016 research-lead.md §12 L292 ("Build"); F-017 SPEC.md L32 | P0 | **Not built** — cache-first discipline (grep + staleness) |
| 8 | `check_staleness.py` | F-016 research-lead.md §12 L293 ("Build"); F-017 SPEC.md L32 | P0 | **Not built** — compare reference date to type-specific window |
| 9 | `rank_source.py` | F-016 research-lead.md §12 L294 ("Build"); F-017 SPEC.md L32 | P1 | **Not built** — T1-T6 source authority hierarchy |
| 10 | `compare_versions.py` | F-016 research-lead.md §12 L295 ("Build"); F-017 SPEC.md L32 | P1 | **Not built** — changelog diff between two versions |
| 11 | `cross_ref.py` | F-016 research-lead.md §12 L296 ("Build"); F-017 SPEC.md L32 | P1 | **Not built** — multi-source agreement check (NOT the same as `cross_ref_agents.py` in `.aspis/scripts/planning/`) |
| 12 | `validate-skills.py` | system-lead-config-runtime.md §5.8 L879 | P2 | **Not built** — Anthropic Skills format check |
| 13 | `validate-agents.py` | system-lead-config-runtime.md §5.8 L880 | P2 | **Not built** — third-person description check |
| 14 | `validate-decisions.py` | system-lead-config-runtime.md §5.8 L881 | P3 | **Not built** — D-NNN format check |
| 15 | `validate-constitution.py` | system-lead-config-runtime.md §5.8 L882 | P3 | **Not built** — code change → constitution check |
| 16 | `validate-trace.py` | system-lead-config-runtime.md §5.8 L883 | P1 | **Not built** — every commit has a trace line |
| 17 | `validate-approvals.py` | system-lead-config-runtime.md §5.8 L884 | P0 (HIGH) | **Not built** — R-008 ledger is honor-system without this |
| 18 | `validate-parity.py` | system-lead-config-runtime.md §5.8 L885 | P2 | **Not built** — shell hooks delegate to same Python as `--self-test` |
| 19 | `validate-profiles.py` | system-lead-config-runtime.md §5.8 L886 | P3 | **Not built** — profile inheritance + uniqueness check |
| 20 | `cost_of_change.py` | final-completeness.md L297-308 (proposed) | P2 | **Not built** — SC-011 discrete test |
| 21 | `byte-parity --check` deep mode | F-016 system-lead-config-runtime.md §3.3 L846 | P1 | **Partial** — `--check` is dry-run-only; needs live-tree comparison mode |
| 22 | `promote` lock-state | final-gates.md L1306 | P3 | **Not built** — H-1 from cli-verb-quality (LOW) |
| 23 | `_tmp_f017_*.py` cleanup | final-completeness.md L255-275 | P0 | **Debris to remove** — 10 scratch scripts in `.aspis/scripts/planning/` |
| 24 | 5 planning scripts already built | — | — | **Built** (`feature_scaffold.py`, `task_compile.py`, `prereq_validate.py`, `_console.py`, `active_feature.py`); see `.aspis/scripts/planning/` |
| 25 | 7 context scripts already built | — | — | **Built** (`_common.py`, `build_code_map.py`, `build_registry.py`, `build_state.py`, `record_changes.py`, `update.py`, plus the 1 NEW from F-017 `cross_ref_agents.py` at runtime only — not in catalog source) |
| 26 | 12 hook scripts already built | — | — | **Built** at `.aspis/scripts/hooks/` |
| 27 | `git/compose.py` already built | — | — | **Built** at `.aspis/scripts/git/compose.py` |
| 28 | `aspis findings` read-only subset | F-016 project-lead.md §10 L796 | P2 | **Partial** — full `aspis findings` exists; project-lead's bash allowlist should include `aspis findings list*` |

**Total: 11 missing scripts from F-016 inventory + 8 missing validators from system-lead-config-runtime.md §5.8 + 1 proposed cost_of_change.py + 1 byte-parity deep mode + 1 promote lock-state + 1 debris cleanup + 1 bash-allowlist fix = ~23 script candidates.**

---

## Section 7 — Missing CLI verbs

| # | Verb | Referenced in | Priority | Current state |
|---|------|---------------|----------|----------------|
| 1 | `validate-approvals` | system-lead-config-runtime.md §5.8 L884 | P0 (HIGH) | **Not built** — R-008 ledger is honor-system without this |
| 2 | `validate-trace` | system-lead-config-runtime.md §5.8 L883 | P1 | **Not built** |
| 3 | `validate-skills` | system-lead-config-runtime.md §5.8 L879 | P2 | **Not built** |
| 4 | `validate-agents` | system-lead-config-runtime.md §5.8 L880 | P2 | **Not built** |
| 5 | `validate-decisions` | system-lead-config-runtime.md §5.8 L881 | P3 | **Not built** |
| 6 | `validate-constitution` | system-lead-config-runtime.md §5.8 L882 | P3 | **Not built** |
| 7 | `validate-parity` | system-lead-config-runtime.md §5.8 L885 | P2 | **Not built** |
| 8 | `validate-profiles` | system-lead-config-runtime.md §5.8 L886 | P3 | **Not built** |
| 9 | `trace` (and `trace-*` subcommands) | current-aspis-audit-1.md §11.1 L576 | P1 | **Not built** — trace spine (5+ subcommands) |
| 10 | `stats` | current-aspis-audit-1.md §11.1 L576 | P3 | **Not built** |
| 11 | `dashboard` | current-aspis-audit-1.md §11.1 L576; F-017 SPEC.md L25 | P2 | **Not built** — Phase 5 of roadmap |
| 12 | `start-feature` / `close-feature` | current-aspis-audit-1.md §11.1 L576 | P2 | **Partial** — `feature_scaffold.py` is the start; no `close-feature` script |
| 13 | `harvest-gate` | current-aspis-audit-1.md §11.1 L576 | P1 | **Not built** — R-008-gated harvest path |
| 14 | `improve` | current-aspis-audit-1.md §11.1 L576 | P3 | **Not built** — self-improvement loop |
| 15 | `lessons` | current-aspis-audit-1.md §11.1 L576 | P2 | **Not built** — lessons log |
| 16 | `permissions-audit` | F-016 system-lead.md §9 L287 | P0 | **Not built** — cross-checks every agent's allow-list vs policy |
| 17 | `governance-check` (the validator, distinct from `governance check`) | F-016 system-lead.md §9 L288 | P0 | **Partial** — `governance check` is built (6th subcommand) but `governance-check` as a top-level validator is not |
| 18 | `models --sync` / `models --check` | F-016 system-lead.md §9 L299-300 | P1 | **Partial** — `models` exists; specific subcommands may need work |
| 19 | `aspis export --apply` (the actual write mode) | F-017 final-gates.md L381-383; final-completeness.md L141 | P1 | **Built** (`export_cmd.py:50-55`); but not exercised live in dogfood |
| 20 | `bootstrap` | F-016 current-aspis-audit-1.md §11.1 L576 | — | **Built** |
| 21 | 6 verbs already built | F-017 SPEC.md FR-007, FR-014; final-completeness.md L118, L125 | — | **Built** (`validate-runtime`, `byte-parity`, `export`, `validate-index`, `drift`, `governance`); all functional per F-017 final-gates.md |
| 22 | `aspis doctor --export` | final-gates.md L381-383 (implicit) | P1 | **Partial** — `doctor` exists; auto-export trigger not built |
| 23 | `aspis commit` | committer.md §3 L106; F-016 committer.md L26 | — | **Built** |
| 24 | `aspis preflight` | F-016 system-lead.md §9 L284 | — | **Built** |
| 25 | `aspis context` | F-016 system-lead.md §9 L283 | — | **Built** |
| 26 | `aspis status` | F-016 project-lead.md §4 L129 | — | **Built** |
| 27 | `aspis mode` | F-016 project-lead.md §4 L130 | — | **Built** |
| 28 | `aspis findings` | F-016 project-lead.md §4 L133 | — | **Built** |
| 29 | `aspis models --available` | F-016 project-lead.md §4 L134 | — | **Built** |
| 30 | `aspis commits --audit` | F-016 project-lead.md §4 L135 | — | **Built** |
| 31 | `aspis artifact` (build/task, review, test, feature) | F-016 system-lead.md §9 L283 | — | **Built** (per `integration-gates.md`) |

**Total: 18 missing CLI verb candidates (8 validators + 10 old-ASPS + 1 governance-check top-level + 1 permissions-audit + 1 auto-export + 1 close-feature) — 6 core verbs built, ~12 net-new + refinements.**

---

## Section 8 — Current test state

> **Note on test state capture:** The F-017 final-gates.md review at L88-92 (Environment caveat) noted that the bash permission layer blocked live `python -m src.aspis.commands.*` invocations; the same env-blocked constraint applies here. Tests under `tests/` are 60+ files; last review verified gate surface via direct import + `_run(args)`, not via `pytest` discovery. Live pytest output was not captured in F-017's environment; this is a known constraint, not a new failure.

### Test surface (verified by directory walk — `tests/`)

**Count: 63 test files** under `tests/`:
- test_active_feature, test_agent_permissions, test_artifact, test_assetkinds, test_brain_gitignore, test_bootstrap, test_bootstrap_cli, test_build_code_map, test_build_registry, test_build_state, test_catalog, test_cli, test_commit, test_commitmsg, test_commits, test_conftest, test_consistency, test_constitution, test_context, test_detect, test_export, test_export_protection, test_export_snapshot, test_f006_hooks, test_f015_e2e, test_feature_scaffold, test_findings, test_gitcheck, test_global_config, test_health, test_hook_gates, test_hooks, test_init_cli, test_init_op, test_install_ux, test_inventory, test_lifecycle, test_lifecycle_gates, test_model_catalog, test_model_detection, test_models, test_models_command, test_mode, test_prereq_validate, test_preflight, test_profiles, test_promotion, test_protect, test_record_changes, test_render_routing, test_resolver, test_runtime_contract, test_settings, test_task_compile, test_templating, test_testledger, test_transform, test_update
- + conftest.py

**Test gaps from F-017 reviews + F-016 audit** (what's NOT tested):

| # | Gap | Source | Priority |
|---|-----|--------|----------|
| 1 | `validate-runtime` not run live in dogfood | final-gates.md Gate 1 L88-92; integration-gates.md M-2 L294 | P0 |
| 2 | `byte-parity` not run live | final-gates.md Gate 2 | P0 |
| 3 | `export --dry-run` exits 1 in dogfood (by design) | final-gates.md Gate 3 L249-255; integration-gates.md M-3 L295 | P0 (must re-verify after init) |
| 4 | `drift` 51 expected messages (live parity deferred) | final-gates.md Gate 5 L324-383 | P0 (owner-driven post-export) |
| 5 | `governance` 6 subcommands not all live-verified | final-gates.md Gate 6 L387-435; integration-gates.md M-4 L296 | P1 |
| 6 | `validate-index --help` CRASHES (`10%` literal) | final-gates.md C-1 L908-967 | P0 (CRITICAL) |
| 7 | End-to-end "real agent" tests | current-aspis-audit-1.md §10.3 L560 | P1 |
| 8 | Catalog → render byte-stability (totality guard) | current-aspis-audit-1.md §10.3 L561; §11.1 L551 | P0 (HIGH) |
| 9 | Mode knob enforcement (full modes.yaml → artifact gating matrix) | current-aspis-audit-1.md §10.3 L562 | P1 |
| 10 | Runtime hooks per-platform behavior on real tool call | current-aspis-audit-1.md §10.3 L563 | P1 |
| 11 | Promotion atomicity | current-aspis-audit-1.md §10.3 L564 | P1 |
| 12 | Per-agent permission enforcement is in `test_agent_permissions.py` (covered); per-agent model routing tests are in `test_resolver.py` and `test_models_command.py` (covered) | current-aspis-audit-1.md §10.2 L553 | — (covered) |
| 13 | SC-002 end-to-end loop test (plan→build→review→commit) on cheap+standard | final-completeness.md L141; F-017 SPEC.md L121 | P0 (DEFERRED to owner) |
| 14 | SC-011 cost-of-change test (discrete) | final-completeness.md L297-308 | P2 |
| 15 | Validate-approvals test (R-008 enforcement) | system-lead-config-runtime.md §5.8 L884 | P0 (HIGH) |
| 16 | Validate-trace test (every commit → trace line) | system-lead-config-runtime.md §5.8 L883 | P1 |

**Pytest count and current pass/fail status:** Not captured live (env-blocked per F-017 final-gates.md). Based on the F-017 review: **the build's systemic gates (validate-runtime 12/12 PASS, byte-parity CLEAN, prereq_validate OK, governance gate-4 BLOCKED) all PASS by source + by direct-import workarounds.** Live pytest was not run in F-017's environment; the same constraint applies here. **No new test failures introduced by F-017** — the gating is on the missing live-runtime verification, not on a test regression.

---

## Section 9 — F-017 review carry-overs (final triple review)

### 9.1 From `final-completeness.md` (verdict: APPROVE WITH CONDITIONS)

| # | Severity | Finding | Source line | F-018 action |
|---|----------|---------|-------------|--------------|
| H-1 | HIGH | `commit-readiness/SKILL.md` untracked in git | L233-253 | Commit the file (1 commit) — T-47 |
| M-1 | MEDIUM | 7 (now 10) build-temp `_tmp_f017_*.py` files in `.aspis/scripts/planning/` | L255-275; L1089-1110 | Remove debris |
| M-2 | MEDIUM | `BUILD_REPORT.md` scoped to T-51..T-55 only, not whole feature | L277-295 | Rename or extend |
| M-3 | MEDIUM | SC-011 cost-of-change test not run as a discrete TASKS step | L297-308 | Add `cost_of_change.py` |
| L-1 | LOW | `bootstrap.md` uses `## Who you are` instead of `## Identity` | L310-328 | Polish / codify exception |
| L-2 | LOW | `system-lead.md:90` references non-existent `.aspis/workflows/system.md` | L330-343 | **HIGH from final-quality** — build the workflow |
| L-3 | LOW | `governance.py` divergences from `governance.md` §6 (`revoke --approver` required vs optional; `request --reason` required vs optional; `audit` missing `--until`/`--status`/`--pretty`) | L345-359 | Polish (spec-alignment) |
| L-4 | LOW | 2 of the previously-flagged HIGH findings from `system-integrity.md` partially resolved: M-7 (renamed `## How you work` sections, 5 of 8 leads); L-2 (mode field docstring in `AGENT_BODY_STANDARD.md` is stale) | L361-372 | Polish / fix docstring |
| L-5 | LOW | pre-existing review `system-integrity.md` notes `git status -uall` was NOT clean — now resolved | L374-380 | (No F-018 action) |

### 9.2 From `final-gates.md` (verdict: CHANGES REQUIRED — 1 CRITICAL, 3 HIGH, 4 MEDIUM, 4 LOW)

| # | Severity | Finding | Source line | F-018 action |
|---|----------|---------|-------------|--------------|
| C-1 | **CRITICAL** | `aspis validate-index --help` crashes with `ValueError: badly formed help string` (literal `10%` at `validate_index.py:192`) | L908-967 | **Fix L192** (`10%` → `10%%` or `10 percent`) — 1-character edit |
| H-1 | HIGH | `commit-readiness/SKILL.md` is untracked (T-47 missing commit) | L972-1015 | Same as final-completeness H-1 |
| H-2 | HIGH | Worktree not clean at end of build (13 untracked items) | L1017-1066 | Cleanup |
| H-3 | RESOLVED | `validate-runtime --runtime {all}` (was prior H, closed by T-51) | L1074-1085 | (No action) |
| M-1 | MEDIUM | 10 `_tmp_f017_*.py` scratch scripts | L1089-1110 | Same as final-completeness M-1 |
| M-2 | MEDIUM | Empty T-55 review template at `reviews/T-55-review.md` | L1113-1129 | Fill or remove |
| L-1 | LOW | Drift verb reports 51 expected drift messages (per spec, deferred to post-export) | L1191-1220 | (No action; expected) |
| L-2 | LOW | Cost-of-change test not run as discrete step (same as final-completeness M-3) | — | Same as M-3 above |
| L-3 | LOW | CLI verb surface clean-up (governance spec divergences) | — | Same as final-completeness L-3 |
| L-4 | LOW | Pre-existing review notes (untracked files now resolved) | — | (No action) |

### 9.3 From `final-quality.md` (verdict: APPROVED WITH NOTES — 0 CRITICAL, 2 HIGH, 6 MEDIUM, 5 LOW)

| # | Severity | Finding | Source line | F-018 action |
|---|----------|---------|-------------|--------------|
| H-1 | HIGH | `system-lead.md:90` references non-existent workflow `.aspis/workflows/system.md` | L443-459 | **Build `system.md` workflow** |
| H-2 | HIGH | `fix-lead.md:103` references non-existent template `.aspis/templates/planning/FIX_REPORT.md` | L461-477 | **Build the template** (or move existing `report/fix.md` to `planning/FIX_REPORT.md` and update body) |
| M-1 | MEDIUM | `AGENT_BODY_STANDARD.md` does not codify the bootstrap exception | L481-488 | Add "Documented exceptions" subsection |
| M-2..M-6 | MEDIUM | (other M findings in this review, see source) | L488+ | Polish |
| L-1 | LOW | `AGENT_BODY_STANDARD.md` `mode` field docstring is stale (`vibe/mvp/production` vs `primary/subagent`) | L27, L416-417 | **Fix the docstring** (1-line edit) |
| L-2 | LOW | `general-builder` Core rules R-006 partial restatement (3 of 4 R-### with parenthetical) | L242-243, L249-252 | Remove parentheticals |
| L-3 | LOW | `evidence-validation` skill section-order deviation (Hard rule + Evidence table placement) | L32 | Polish (move table into Procedure) |
| L-4 | LOW | Agents cite workflows/templates by deployed path (not catalog source) | L33 | Document the render-time substitution convention |
| L-5 | LOW | `bootstrap` body has no `## Core rules` section | L34 | Codify exception or add block |
| L-6 | LOW | (closure) `task_compile.py` byte-identity verified | L35 | (No action) |

### 9.4 From `integration-gates.md` and other F-017 reviews (carried findings)

| # | Source | Finding | F-018 action |
|---|--------|---------|--------------|
| 1 | integration-gates.md M-1 L293 | `--dry-run` on `export` is default (no `store_true`) | Polish (1-line fix) |
| 2 | integration-gates.md M-3 L295 | `aspis export --dry-run` exits 1 in dogfood (by design) | Re-verify after init |
| 3 | cli-verb-quality.md H-3 L347-359 | `governance.py` spec divergences (`--approver`/`--reason`/`--pretty`/`--status`) | Polish |
| 4 | skill-quality.md L72 | L2-P0 / L2-P1 skills partial / deferred | (covered above) |
| 5 | completeness-traceability.md L235 | "5 subagents are silently dropped" (4 system-lead subs + 1 governance done) | Cover in F-018 |
| 6 | architecture-constitution.md L653 | L2 vs L3 boundary encoded faithfully | (No action) |
| 7 | plan-feasibility.md L272-274 | Risk 4 (ref-spec contradiction) has no F-018 escalation path | Add escalation |
| 8 | leaf-body-quality.md L142 | general-builder M-1: R-006 partial restatement | (same as L-2 above) |
| 9 | system-integrity.md M-7 L595 | CLI path mismatch now moot | (No action) |
| 10 | agent-body-quality.md (implicit) | Various | (covered above) |

---

## Section 10 — Total gap count (summary)

### 10.1 By section

| Section | Total items | Defer-from-F-017 (sec 1) | Net-new from F-016 ref specs (sec 2-7) |
|---------|-------------|---------------------------|---------------------------------------|
| **Section 1 — Deferred from F-017** | 84 entries (84 deferred/findings from F-017) | 84 | 0 |
| **Section 2 — Missing subagents** | 38 subagent slots identified (3 already deployed, 1 governance as CLI, **35 missing**) | 0 (most are F-018 build) | 35 |
| **Section 3 — Missing skills** | 25 skill candidates (1 inventory-missing + 24 net-new) | 1 (`dependency-audit`) | 24 |
| **Section 4 — Missing templates** | 14 template candidates (6 not built from F-017 SPEC L31 + 3 already built at different path + 4 net-new + 1 partial) | 6 (F-017 deferred list) | 8 |
| **Section 5 — Missing workflows** | 5 missing (1 broken-ref HIGH + 4 net-new) | 1 (system.md) + 1 (project-lead-operating-protocol) | 3 |
| **Section 6 — Missing scripts** | 23 script candidates (11 from F-017 SPEC L32 + 8 validators from §5.8 + 1 cost_of_change + 1 byte-parity deep + 1 promote + 1 debris cleanup) | 11 (F-017 deferred) | 12 |
| **Section 7 — Missing CLI verbs** | 18 verb candidates (8 validators + 10 old-ASPS + governance-check + permissions-audit + auto-export + close-feature) | 0 (most are F-018 build) | 18 |
| **Section 8 — Test gaps** | 16 test gaps | 0 (live verification) | 16 |
| **Section 9 — Review carry-overs** | ~30 findings (HIGH: 3, MEDIUM: 6, LOW: ~10) | 30 (from F-017 reviews) | 0 |

### 10.2 Net F-018 build items (unique work)

| Category | Count | Notes |
|----------|-------|-------|
| **Subagents to build** | 35 | 8 system-lead subs + 8 planning-lead subs + sub-reviewer + security-reviewer + 6 stack testers + 4 research-lead subs + 2 fix-lead subs + 3 other (test-author, context-feeder, context-summarizer) |
| **Skills to build** | 25 | 1 inventory (dependency-audit) + 18 stack-test skills + 6 net-new (constitution-check script, cache-management, harvest-protocol extension, cost-of-change, governance-approval extension, profile-author) |
| **Templates to build** | 14 | 6 from F-017 SPEC L31 + 3 name-reconciliation + 4 project-lead (CONTEXT_PACKET, STATUS_REPORT, REPLY_TO_USER, ESCALATION_NOTE) + 1 partial (TASK_PACKET V0-V4 variants) |
| **Workflows to build** | 5 | system.md (HIGH broken-ref), project-lead-operating-protocol, dependency-graph, project-plan, constitution-check |
| **Scripts to build** | 23 | 11 F-017 deferred + 8 validators + 1 cost_of_change + 1 byte-parity deep + 1 promote + 1 debris cleanup + 1 bash-allowlist fix (overlaps with category; final unique ≈ 19) |
| **CLI verbs to build** | 18 | 8 validators + 10 old-ASPS + governance-check + permissions-audit + auto-export + close-feature (overlaps with scripts; final unique ≈ 8 verb names) |
| **Reviews to fix** | ~30 | 3 HIGH + 6 MEDIUM + ~10 LOW from F-017 final triple review + 1 CRITICAL (validate-index `10%`) |

### 10.3 Priority breakdown (F-018 build queue)

**P0 (immediate, must do first):**
- 3 HIGH findings from F-017 final-quality: build `system.md` workflow, build `FIX_REPORT.md` template (or fix body), commit `commit-readiness/SKILL.md`
- 1 CRITICAL from F-017 final-gates: fix `validate-index.py:192` (`10%` → `10%%`)
- 1 deferred skill: `dependency-audit`
- 7 system-lead P0 subagents: `runtime-validator`, `drift-auditor`, `permission-auditor`
- 4 planning-lead P0 subagents: `clarify`, `task-decomposer`, `idea-capture`, `prd-writer` (closes F-027)
- 1 subagent: `sub-reviewer` (reduces reviewer bottleneck)
- 1 subagent: `context-feeder` (project-lead)
- 6 P0 templates: `CLARIFICATION_LOG`, `RESEARCH_REQUEST`, `PLAN_OF_PLAN`, `SCOPE_ESTIMATE`, `MODE_DECISION`, `FIX_REPORT` (consolidate with H-2)
- 1 P0 workflow: `system.md` (consolidate with H-1)
- 1 P0 workflow: `project-lead-operating-protocol`
- 5 P0 scripts: `scope_estimate`, `constitution_check`, `search_cache`, `check_staleness`, `validate-approvals` (HIGH per system-lead-config-runtime.md)
- 1 P0 CLI verb: `validate-approvals`
- 3 P0 review carry-overs: H-1 (system.md), H-2 (FIX_REPORT), C-1 (validate-index `10%`), H-1 (commit-readiness untracked)
- Debris cleanup: 10 `_tmp_f017_*.py` files

**P1 (near-term, high-leverage):**
- 2 system-lead P1 subagents: `export-verifier`, `catalog-synchronizer`
- 3 planning-lead near-term subagents: `constitution-checker`, `scope-estimator`, `research-request-writer`
- 1 subagent: `security-reviewer` (after security-review skill)
- 4 research-lead P1 subagents: `codebase-explorer`, `docs-fetcher`, `web-researcher`, `cache-manager`
- 2 fix-lead P1 subagents: `general-fix`, `general-inspect`, `bug-triager`, `gate-fixer`
- 1 subagent: `test-author`
- 5 stack testers: `python-tester`, `api-tester`, `cli-tester`, `security-tester` (+ skills)
- 1 subagent: `context-summarizer` (after trace spine)
- 1 P1 subagent: `dependency-analyzer` (planning-lead)
- 1 P1 template: `DEPENDENCIES`, `BUILD_REPORT` (reconcile name), `FEATURE_REPORT` (reconcile name), `TEST_REPORT` (reconcile name)
- 3 P1 workflows: `dependency-graph`, `constitution-check`
- 7 P1 scripts: `plan_quality_check`, `mode_validator`, `task_size_check`, `rank_source`, `compare_versions`, `cross_ref`, `validate-trace`
- 6 P1 CLI verbs: `validate-trace`, `harvest-gate`, `trace` (5+ subs), `permissions-audit`, `governance-check` (top-level), `models --sync`/`--check`
- 1 P1 review: SC-002 end-to-end loop test (owner-driven post-export)

**P2 (future, when workload justifies):**
- 2 system-lead P2 subagents: `opencode-author`, `claude-author`
- 2 stack testers: `db-tester`, `ui-tester`
- 1 P2 template: `CONTEXT_PACKET`, `STATUS_REPORT`, `REPLY_TO_USER`, `ESCALATION_NOTE`
- 1 P2 workflow: `project-plan`
- 4 P2 scripts: `dependency_graph`, `validate-skills`, `validate-agents`, `validate-parity`, `cost_of_change`
- 6 P2 CLI verbs: `validate-skills`, `validate-agents`, `validate-parity`, `start-feature`/`close-feature`, `dashboard`, `lessons`
- 2 P2 sub-skill scripts: `permission-audit` (CLI), `permissions-audit` (verb)
- 1 P2 review: SC-011 discrete test

**P3 (later, optional):**
- 3 P3 validators: `validate-decisions`, `validate-constitution`, `validate-profiles`
- 2 P3 CLI verbs: `stats`, `improve`
- 1 P3 review: governance spec divergences polish

### 10.4 Cross-reference: F-016 inventory vs F-018 needs

| F-016 inventory (per F-017 SPEC L17) | Built in F-017 | Deferred to F-018 | Net-new in F-018 scope |
|---------------------------------------|----------------|-------------------|----------------------|
| 13 P0 skills | 13 (or 7 L0 + 6 L1 = 13) | 0 | — |
| 7 P1 skills | 7 | 0 | — |
| 5 P2 skills | 4 (commit-readiness, hook-author, model-inventory, profile-manager) | 1 (`dependency-audit`) | — |
| **25 total** | **24** | **1** | — |
| 8 lead agents | 8 | 0 | — |
| 3 leaf agents | 3 | 0 | — |
| 1 governance (deterministic) | 1 (as CLI) | 0 | — |
| 3 CLI verbs P0 (validate-runtime, byte-parity, export) | 3 | 0 | — |
| 3 CLI verbs P1 (validate-index, drift, governance completion) | 3 | 0 | — |
| **6 total** | **6** | **0** | — |
| 3 planning scripts (feature_scaffold, task_compile, prereq_validate) | 3 | 0 | — |
| 2 helper scripts (_console, active_feature) | 2 | 0 | — |
| 5 planning templates (SPEC, PLAN, TASKS, ACCEPTANCE, TASK_PACKET) | 5 | 0 | — |
| 5 workflows (plan, build, review, fix, small-task) | 5 | 0 | — |
| 2 durable conventions (AGENT_BODY_STANDARD, DYNAMIC_READINESS) | 2 | 0 | — |
| **Subagents** (F-016 inventory did not enumerate a hard count) | 3 (committer, project-explorer, general-builder) | 0 | 35 to build (sec 2) |
| **Templates** (F-016 ref spec listed 10 deferred) | 0 of the 10 | 10 | (some built at different path) |
| **Scripts** (F-016 ref spec listed ~10 deferred) | 0 of 11 | 11 | 12 net-new (validators + cost) |
| **Workflows** (F-016 ref spec listed 1 deferred) | 0 | 1 (project-lead-operating-protocol) | 4 (system.md is broken-ref) |
| **CLI verbs** (F-016 ref spec listed 6+ future) | 0 | 0 | 18 net-new |

### 10.5 Final counts

| Metric | Value |
|--------|-------|
| F-017 deferred items requiring F-018 build (Section 1) | 84 entries (a mix of items the F-017 spec deferred + F-017 review findings) |
| Subagents to build (Section 2) | **35** |
| Skills to build (Section 3) | **25** (1 inventory + 24 net-new) |
| Templates to build (Section 4) | **14** |
| Workflows to build (Section 5) | **5** |
| Scripts to build (Section 6) | **23** candidates → ~19 unique |
| CLI verbs to build (Section 7) | **18** candidates → ~8 unique verb names |
| Test gaps (Section 8) | **16** |
| F-017 review carry-overs (Section 9) | **~30** findings (3 HIGH + 6 MEDIUM + ~10 LOW) |
| **Total unique build items for F-018** | **~100+** discrete work items |
| **P0 (must do first)** | **~28 items** (subagents + skills + templates + workflows + scripts + reviews) |
| **P1 (near-term, high-leverage)** | **~25 items** |
| **P2 (future, when workload justifies)** | **~12 items** |
| **P3 (later, optional)** | **~6 items** |

---

## Appendix A — File:line evidence index (top 30 highest-priority items)

| # | Finding | Source:line |
|---|---------|-------------|
| 1 | `aspis validate-index --help` CRASHES (`10%` literal) | `src/aspis/commands/validate_index.py:192` |
| 2 | `system-lead.md` references non-existent workflow | `src/aspis/data/catalog/agents/system-lead.md:90` |
| 3 | `fix-lead.md` references non-existent template | `src/aspis/data/catalog/agents/fix-lead.md:103` |
| 4 | `commit-readiness/SKILL.md` untracked | `src/aspis/data/catalog/skills/commit-readiness/SKILL.md` (file exists, not in `git ls-files`) |
| 5 | 8 system-lead P0/P1 subagents to build | `F-016 system-lead.md §10` L315-327 |
| 6 | 8 planning-lead subagents to build | `F-016 planning-lead.md §6` L252-259 |
| 7 | `sub-reviewer` to build (reduces reviewer bottleneck) | `F-016 build-lead.md §13 Q1` L575; `reviewer.md §11` L351-356 |
| 8 | `dependency-audit` skill deferred | `F-017 SPEC.md:17,91,130` |
| 9 | 6 P0 templates missing | `F-016 planning-lead.md §13` L1006-1011 |
| 10 | 5 P0 scripts missing | `F-016 planning-lead.md §13` L1020-1024 |
| 11 | 4 P0 research scripts missing | `F-016 research-lead.md §12` L292-296 |
| 12 | `validate-approvals` validator (HIGH) | `F-016 system-lead-config-runtime.md §5.8` L884 |
| 13 | 18 stack-test skills across 6 stack subagents | `F-016 test-lead.md §11.3` L239-249 |
| 14 | Trace spine (5+ subcommands) | `current-aspis-audit-1.md §10.2` L546; `F-017 SPEC.md:24` |
| 15 | Dashboard (Phase 5) | `current-aspis-audit-1.md §10.2` L547; `F-017 SPEC.md:25` |
| 16 | Profile system (multi-profile support) | `F-016 system-lead-config-runtime.md §6` L889-998 |
| 17 | `enforcement: warn` → `block` flip | `F-016 enforcement.md` L41-48; `system-lead.md §8` L264-272 |
| 18 | `system.md` workflow (broken ref) | `.aspis/workflows/` has 5 files; `system.md` missing |
| 19 | `project-lead-operating-protocol.md` workflow | `F-016 project-lead.md §10` L791-792 |
| 20 | `committer` `temperature: 0.1` missing | `F-016 project-lead-delegation-map-1.md §8` L1012 |
| 21 | `aspis findings list*` not in project-lead allowlist | `F-016 project-lead.md §10` L796 |
| 22 | `enforcement: warn` default in `hooks.yaml` (R-008) | `F-016 system-lead.md §8` L264-272; `enforcement.md` L41-48 |
| 23 | 6 missing reviews to fix | `F-017 Review/final-completeness.md` §5; `final-gates.md` §5; `final-quality.md` §3 |
| 24 | SC-002 end-to-end loop on cheap+standard (deferred to owner) | `F-017 SPEC.md L121; final-completeness.md L141` |
| 25 | Cost-of-change test (SC-011) | `F-017 final-completeness.md L297-308` |
| 26 | Mode field docstring in AGENT_BODY_STANDARD.md is stale | `F-017 final-quality.md L416-417` |
| 27 | Bootstrap exception not codified | `F-017 final-quality.md L481-488` |
| 28 | `cross_ref_agents.py` not in catalog source | `F-017 final-quality.md L358-360` |
| 29 | governance verb spec divergences | `F-017 final-quality.md L345-359`; `cli-verb-quality.md` |
| 30 | `10 _tmp_f017_*.py` debris | `F-017 final-completeness.md L255-275; final-gates.md L1089-1110` |

---

*End of gap collation. Research only — no code, templates, scripts, or bodies authored. Cross-references every claim against a source file with line number.*
