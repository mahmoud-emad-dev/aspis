# F-016 — Implementation Plan

> Mode: **production** — full plan.

## Summary
F-016 delivers the complete, documented agent system architecture for ASPIS. The approach is **specification-first, catalog-second**: finalize the 8 already-produced reference specs through adversarial review, produce lighter specs for the 3 leaf agents, update all 11 catalog agent files to match, specify 30+ missing skills, specify missing infrastructure (governance subagent, modes.yaml, enforcement mode, CLI verbs, planning scripts), and resolve the documented live-vs-catalog gaps. The feature is primarily a **documentation and specification** effort — the actual code changes (catalog file updates, skill stubs) are lightweight. The heavy lifting was the research and design phase, which is complete.

## Technical context
- **Language / version**: N/A — this feature produces markdown specifications, catalog YAML frontmatter, and body instructions. No Python code changes unless a catalog update reveals a rendering bug.
- **Key dependencies**: The research phase output (12 research files + 8 reference specs), the live codebase (`.opencode/agents/`, `.claude/agents/`, `src/aspis/data/catalog/`), the architecture constitution, system rules, and existing decisions (D-001–D-018).
- **Storage / interfaces**: Agent specs in `.aspis/features/F-016-agent-system-architecture/Research/ref/`. Catalog files in `src/aspis/data/catalog/agents/`. Missing skill specs in `.aspis/features/F-016-agent-system-architecture/Research/skills/`. Systemic specs in feature folder.
- **Testing**: Adversarial reviewer audit is the primary verification method. Cross-reference consistency script (`cross_ref_agents.py`) validates no overlapping responsibilities, no orphaned delegation edges, no references to non-existent skills. Catalog frontmatter validator (`aspis validate-runtime` once built) checks structural correctness.
- **Project type / structure**: Documentation/specification feature. New files in feature Research folder; edits to catalog agent files; no product code changes.
- **Constraints**: Must preserve catalog as single source of truth. Must not break existing agent rendering. Must pass architecture constitution gate check (cost-of-change ≤10 files touched).

## Gate check
The plan must clear the project's rules before any build.

- [x] **R-001 Scope** — Changes stay within `src/aspis/data/catalog/agents/` (11 files, focused edits) and `Research/ref/` (3 new leaf specs). No product code changes. No runtime files edited directly. PASS.
- [x] **R-002 Gates** — Deterministic gates: (1) `cross_ref_agents.py` validates cross-agent consistency, (2) reviewer adversarial audit on every spec, (3) catalog frontmatter structural validation. PASS.
- [x] **R-005 Tests-as-spec** — Agent acceptance criteria serve as the "tests." Every spec's checkbox list is verifiable. Cross-reference script provides deterministic pass/fail. PASS.
- [x] **R-009 Human gate** — Governance subagent design, enforcement mode flip, and mode routing changes flagged for R-008 approval below. PASS (flagged, not bypassed).

## Components

### Component 1 — Agent Reference Specs (the truth layer)
The 8 already-produced specs in `Research/ref/` pass through adversarial review, are refined against findings, and become the authoritative agent contracts. The 3 leaf agents get lighter specs produced fresh. Each spec follows the standard template: Identity → Responsibilities→Skills → Model Tier → Permission Surface → Delegation Map → Procedural Flows → Use Cases → Assets Inventory → Anti-Patterns → Error Handling → Acceptance Criteria.

### Component 2 — Catalog Agent Files (the source layer)
The 11 catalog files at `src/aspis/data/catalog/agents/` are updated: frontmatter fields (mode, model, permissions, delegates, skills, runtimes) are aligned with reference specs; body instructions are refined to reflect the spec's identity and rules. Changes are focused — existing structure preserved, only drifted or missing content updated.

### Component 3 — Missing Skills Specification
30+ skills identified across the 8 reference specs are specified with: purpose statement, owning agent, priority (P0/P1/P2), and estimated effort. Stored in `Research/skills/` as individual spec files or a consolidated inventory.

### Component 4 — Systemic Infrastructure Specs
- **Governance subagent spec**: protected paths, R-008 workflow, approval ledger, intervention handler
- **modes.yaml spec**: per-mode knob values (spec, architecture, task_size, plan_review, build_review, test_depth, docs, promotable)
- **Enforcement mode spec**: block for runtime tools, warn for pre-commit, CI override
- **Planning scripts deployment spec**: feature_scaffold.py, task_compile.py, prereq_validate.py
- **Missing CLI verbs spec**: validate-runtime, validate-index, byte-parity, drift, export, governance

### Data flow
```
Research files (12) + Live codebase audit
        ↓
  Reference specs (8 leads) — REFINE via reviewer audit
        ↓
  Leaf specs (3 workers) — PRODUCE lighter
        ↓
  Cross-reference validation — VERIFY consistency
        ↓
  Catalog agent file updates — ALIGN to specs
        ↓
  Missing skills spec — ENUMERATE
        ↓
  Systemic infrastructure specs — SPECIFY
        ↓
  Final reviewer audit — APPROVE all artifacts
        ↓
  Handoff to build-lead: catalog updates + skill stubs
```

## Steps
| Step | Files | Gate |
|------|-------|------|
| 1. **Finalize 8 lead reference specs** — Adversarial review pass, refine any findings, lock as authoritative | `Research/ref/project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`, `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md` | Reviewer audit: 0 CRITICAL, 0 HIGH unresolved |
| 2. **Produce 3 leaf agent reference specs** — Lighter 6–8 section specs for committer, general-builder, project-explorer | `Research/ref/committer.md`, `general-builder.md`, `project-explorer.md` (new) | Review: identity clear, R-004/R-006 compliance, no role overlap with leads |
| 3. **Cross-reference validation** — Run consistency script: no overlapping responsibilities, no orphaned delegation edges, every skill reference resolves | All 11 `Research/ref/*.md` | `cross_ref_agents.py` exit 0 |
| 4. **Update catalog agent files** — Align frontmatter + body for all 11 agents | `src/aspis/data/catalog/agents/{project-lead,planning-lead,build-lead,reviewer,system-lead,fix-lead,test-lead,research-lead,committer,general-builder,project-explorer}.md` | `aspis validate-runtime` structural pass (or manual schema check until CLI built) |
| 5. **Specify missing skills** — Consolidated inventory of 30+ skill gaps with purpose, owner, priority | `Research/skills/inventory.md` (new) | Cross-ref: every skill reference in agent specs has an entry |
| 6. **Specify governance subagent** — Protected paths, R-008 workflow, approval ledger, intervention handler | `Research/ref/governance.md` (new) or feature-level SPEC section | R-008 compliance review |
| 7. **Specify modes.yaml** — Complete knob values per mode | `Research/specs/modes.yaml` (new spec) | Planning-lead review: all knobs covered, values consistent with planning workflow |
| 8. **Specify enforcement mode** — Block/warn boundary, CI override | `Research/specs/enforcement.md` (new) | Security review |
| 9. **Specify planning scripts deployment** — Source, destination, trigger, validation per script | `Research/specs/planning-scripts.md` (new) | Cross-ref: matches planning-lead reference spec §P1/P6/P8 |
| 10. **Specify missing CLI verbs** — 6 verbs with purpose, priority, interface | `Research/specs/cli-verbs.md` (new) | Cross-ref: matches system-lead reference spec §System Health |
| 11. **Specify cross-runtime parity** — Claude adapter permission-block preservation | `Research/specs/cross-runtime.md` (new) | Byte-parity check spec |
| 12. **Final acceptance review** — All artifacts, all specs, all catalog files pass independent reviewer audit | All files in scope | Reviewer verdict: approved; SC-001 through SC-012 met |
| 13. **Handoff to build-lead** — Package feature folder, catalog file paths, task list | N/A | `prereq_validate.py --phase build` |

## Verification
Run before declaring done:
```bash
# Cross-agent consistency
python .aspis/scripts/planning/cross_ref_agents.py --feature F-016

# Catalog frontmatter structural check (if CLI built)
aspis validate-runtime

# Manual checks:
# - Every agent spec has all 6 required sections (identity, permissions, delegation, procedures, anti-patterns, acceptance)
# - Every FR-### maps to a completed step
# - Every SC-### has evidence
# - 0 CRITICAL, 0 HIGH unresolved reviewer findings across all artifacts
```

## Risks & rollback
- **Risk**: Catalog file updates break agent rendering → **Mitigation**: Only frontmatter field alignment and body refinement; no structural changes to the frontmatter schema. Test rendering before commit (`aspis export --check`).
- **Risk**: Reference spec and catalog file diverge over time → **Mitigation**: Reference spec is the source of truth; catalog file carries a `> Derived from Research/ref/<agent>.md` header. Byte-parity check catches drift.
- **Risk**: 30+ skill specs create scope creep → **Mitigation**: Skills are *specified* (purpose + priority), not *built*. Building them is a follow-up feature. This feature only enumerates the gap.
- **Rollback**: Git revert the feature branch. All changes are to markdown files and YAML frontmatter — no database migrations, no API changes, no runtime behavior changes. Catalog files can be reverted individually if a specific agent update causes issues.

## Complexity tracking
Fill ONLY if a gate-check row is violated and the complexity is justified.

No gate-check violations. All changes stay within scope, pass deterministic gates, and are testable.

## Decisions needing approval
The following require R-008 human gate sign-off before build:

1. **Governance subagent scope**: The spec defines a new subagent that is the ONLY agent permitted to edit `rules/**` and `profiles/defaults.yaml`. This changes the system's permission architecture. → **Approval needed**: scope, protected paths list, R-008 workflow design.
2. **Enforcement mode flip (warn→block)**: Changing runtime tool enforcement from `warn` (reports only) to `block` (hard wall) affects every agent's write operations. → **Approval needed**: confirm block for runtime, warn for pre-commit, CI override env var.
3. **Model tier assignments**: Some agents in the reference specs have different tier assignments than the live runtime (e.g., planning-lead reference says standard, live is deep). → **Approval needed**: confirm tier assignments per the reference specs before catalog update.
4. **Claude Code adapter permission-block fix**: The adapter currently strips the `permission:` block from Claude-rendered agents. Fixing this changes the permission enforcement surface for Claude users. → **Approval needed**: confirm the fix should be applied, and whether it should be backward-compatible.
