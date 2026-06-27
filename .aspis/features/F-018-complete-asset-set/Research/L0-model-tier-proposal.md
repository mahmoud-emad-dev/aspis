# F-018/L0 — Per-Lead Model-Tier Proposal

> Generated: 2026-06-27
> Purpose: Document the model-tier fix decision for T-001b.
> Scope: 7 of 8 confirmed L0 failures (Bucket A).
> Mode: PRODUCTION

## Diagnosis

The 5 catalog agent bodies that the failing tests assert are "deep-tier" leads
(system-lead, planning-lead, reviewer, build-lead, fix-lead) all currently
declare `model: standard` in their frontmatter. Tests assert these agents
should resolve to the **deep** tier.

### Why the bodies must change, not the tests

1. **Test intent is documented in test names and comments.**
   - `test_system_lead_is_a_deep_authoring_primary` — comment: `# deep tier — authoring/governance`
   - `test_planning_lead_is_a_deep_planning_subagent` — comment: `# deep tier — planning is reasoning-heavy`
   - `test_reviewer_is_a_deep_readonly_authority` — comment: `# deep tier — quality judgment`
   - `test_build_lead_is_a_deep_orchestrator` — comment: `# deep tier — the reasoning orchestrator`
   - `test_fix_lead_is_a_deep_repair_subagent` — comment: `# deep tier — diagnosis needs reasoning`
   - `test_build_lead_is_a_deep_orchestrator` (line 220) — `assert fm["mode"] == "subagent"  # promoted at bootstrap`

2. **F-010 established pattern.** Commit `eedbc7b` ("chore(F-010): re-tier
   general-builder to cheap and research-lead to deep") updated catalog bodies
   to match test intent — same pattern, same fix shape.

3. **`test_models.py::test_project_override_and_pin_apply_on_export` REQUIRES
   build-lead to be on the deep tier.** Line 62 asserts the post-init rendered
   model equals `resources.model_map("opencode")["deep"]` — which is the
   bundled catalog's `opencode.deep: opencode/nemotron-3-ultra-free`. That
   assertion only holds if the body says `model: deep`.

4. **Bundled catalog tier map is already correct.**
   - `claude.deep: claude-opus-4-8` — matches what claude-runtime tests expect.
   - `opencode.deep: opencode/nemotron-3-ultra-free` — matches what opencode-runtime tests expect.

5. **The body `mode: primary` in build-lead is inconsistent** with the other 3
   leads (system-lead, planning-lead, reviewer all ship as `subagent`).
   `PROMOTE_TO_PRIMARY` lists all 4 — so all 4 should ship as `subagent` and
   be flipped to `primary` by the bootstrap promotion step. This is also
   asserted by `test_promotion.py::test_all_promote_leads_are_present_and_flipped`.

## Resolution trace (with my fix applied)

**`test_system_lead_is_a_deep_authoring_primary` (claude)**

| Step | Value |
|------|-------|
| Body `model:` | `deep` (after fix) |
| Bundled `claude.deep` | `claude-opus-4-8` |
| `_tier("claude", "deep")` | `claude-opus-4-8` |
| Rendered `fm["model"]` | `claude-opus-4-8` |
| Assertion | PASS |

**`test_planning_lead_is_a_deep_planning_subagent` (claude)** — same resolution as system-lead. PASS

**`test_reviewer_is_a_deep_readonly_authority` (claude)** — same resolution. PASS

**`test_build_lead_is_a_deep_orchestrator` (opencode)**

| Step | Value |
|------|-------|
| Body `model:` | `deep` (after fix) |
| Body `mode:` | `subagent` (after fix; was `primary`) |
| Bundled `opencode.deep` | `opencode/nemotron-3-ultra-free` |
| `_tier("opencode", "deep")` | `opencode/nemotron-3-ultra-free` |
| Rendered `fm["model"]` | `opencode/nemotron-3-ultra-free` |
| Rendered `fm["mode"]` | `subagent` |
| Assertions | PASS (both model and mode) |

**`test_fix_lead_is_a_deep_repair_subagent` (opencode)** — same as build-lead. PASS

**`test_models.py::test_project_override_and_pin_apply_on_export` (opencode)**

- Step 1: `assert _model(build_lead) == opencode/nemotron-3-ultra-free` (bundled deep). With body=`deep`, rendered = `opencode/nemotron-3-ultra-free`. PASS.
- Step 2: project.yaml sets `models.opencode.deep: custom-deep` + `agents.reviewer: cheap`. Re-export.
  - build-lead resolver: pin=None → tier=deep → table override → `custom-deep`. PASS.
  - reviewer resolver: pin=`cheap` (a tier) → table merged → `opencode.cheap` = `opencode/deepseek-v4-flash-free`. PASS.

**`test_promotion.py::test_all_promote_leads_are_present_and_flipped` (opencode)**

- After init, all 4 files exist (system-lead, planning-lead, build-lead, reviewer).
- `promote_leads()` reads each, sees `mode: subagent` in all 4 (after fix for build-lead), flips them.
- `result.promoted` = `{"system-lead", "planning-lead", "build-lead", "reviewer"}` = `PROMOTE_TO_PRIMARY`.
- `result.missing` = `[]`.
- PASS.

## Changes applied (5 catalog bodies, 1 line each)

| File | Line | Before | After |
|------|------|--------|-------|
| `src/aspis/data/catalog/agents/system-lead.md` | 5 | `model: standard` | `model: deep` |
| `src/aspis/data/catalog/agents/planning-lead.md` | 5 | `model: standard` | `model: deep` |
| `src/aspis/data/catalog/agents/reviewer.md` | 5 | `model: standard` | `model: deep` |
| `src/aspis/data/catalog/agents/build-lead.md` | 4 | `mode: primary` | `mode: subagent` |
| `src/aspis/data/catalog/agents/build-lead.md` | 5 | `model: standard` | `model: deep` |
| `src/aspis/data/catalog/agents/fix-lead.md` | 5 | `model: standard` | `model: deep` |

## What was NOT changed (scope-control)

- No project config (`.aspis/config/models.yaml`, `.aspis/config/agent-models.yaml`) — these are
  user-tunable data, not catalog source.
- No test files (except for the rule-layers assertion — separate commit).
- No promotion logic, no model resolver, no renderer.
- No other agent bodies (project-lead, committer, test-lead, general-builder,
  bootstrap, project-explorer, research-lead).

## Residual risk

- **LOW.** The change aligns the catalog bodies with the test's stated intent
  and with the established F-010 pattern. The bundled `models.yaml` is already
  set up to resolve `deep` to the expected model ids. No other tests reference
  these bodies' `model` or `mode` fields in a way that would be invalidated
  (verified by re-running the full pytest suite — 369/369 pass excluding the
  2 documented BLOCKED: env files).
- Project-config overrides (e.g., a project's own `agent-models.yaml`) still
  take precedence over the body — the F-010 capability-based routing is
  preserved.
