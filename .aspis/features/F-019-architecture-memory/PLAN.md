# F-019 — Architecture Memory · Implementation Plan

> Mode: **mvp** — Summary + Technical context + Steps, light note.

## Summary
Add a file-first "Architecture Memory" subsystem: one living markdown file per subsystem
under `.aspis/architecture/subsystems/`, scaffolded by `aspis artifact subsystem <name>`,
read and updated through a mode-gated planning loop owned by `project-lead` via a new
`architecture-memory` skill. Build it deterministic-first (template + CLI artifact kind +
INDEX refresh reuse an existing context script), then the skill + workflow wiring carry the
human "how". Nothing blocks light-mode users; nothing updates a file without explicit
confirmation. Only ONE subsystem file is seeded now — this feature's own.

## Technical context
- **Language / version**: Python 3.12 (engine); markdown (assets).
- **Key dependencies**: existing `aspis artifact` machinery (D-013), assetkinds/templating, modes.yaml, context scripts.
- **Storage / interfaces**: plain markdown under `.aspis/architecture/subsystems/`; CLI `aspis artifact subsystem <name>`.
- **Testing**: pytest (uv/py3.12). Few focused tests; no required-section CI gate.
- **Project type / structure**: brain assets in `src/aspis/data/catalog/` (templates, skill, scaffold) + small engine touch for the new artifact kind + brain location; new top-level brain dir `.aspis/architecture/`.
- **Constraints**: catalog-first (live dirs regenerated, never hand-edited); do NOT run `aspis export`/`models --apply` (models still frozen, pre-models-feature); lean — no daemon/DB/auto-update/new agent.

## Gate check
- [x] **R-001 Scope** — changes stay within the SPEC's in-scope paths (catalog templates/skill/scaffold, modes.yaml, artifact kind, new brain dir).
- [x] **R-002 Gates** — ruff + pytest + validate-runtime stay green.
- [x] **R-005 Tests-as-spec** — artifact creation, INDEX listing, and vibe-skip are pinned by tests.
- [x] **R-008 Human gate** — this IS an architecture change to ASPIS itself → owner approval of this PLAN is the gate; subsystem-file updates are themselves user-confirmed by design.

## Components
1. **Subsystem file template** — `catalog/templates/context/subsystem.md` (lean 7-section format, FR-002).
2. **Impact report template** — `catalog/templates/report/architecture-impact.md` (FR-007 [C]).
3. **Artifact kind `subsystem`** — `aspis artifact subsystem <name>` writes to `.aspis/architecture/subsystems/<name>.md`, stamps name + dates (FR-003). Register in base.yaml + artifact-kind registry.
4. **INDEX refresh** — extend an existing context script to (re)build `.aspis/architecture/subsystems/INDEX.md` from the files' frontmatter. Advisory; reuse the CURRENT_STATE pattern (no new heavy generator).
5. **Skill `architecture-memory`** — `catalog/skills/architecture-memory/SKILL.md`: read-before-design, detect architectural change, write Impact Report, confirm Current/Proposed/Reason with the user, apply dated update, post-review verification. Wired to project-lead (owner); referenced by planning-lead.
6. **Workflow wiring** — add the loop steps to the planning workflow / planning-lead + project-lead bodies: [A] Impact Analysis (pre-plan), [B] read, [C] Impact Report, [D] confirm, [E] Verification.
7. **Mode gating** — `modes.yaml` knob: full (production) / collapsed (mvp) / skipped (vibe).
8. **Brain location + registry** — create `.aspis/architecture/` as a recognized brain dir; register purposes (FR-010).

## Steps
| Step | Files | Gate |
|------|-------|------|
| 1. Subsystem file template | `catalog/templates/context/subsystem.md` | file exists; 7 required sections present |
| 2. Impact report template | `catalog/templates/report/architecture-impact.md` | file exists |
| 3. Register `subsystem` artifact kind + target path | artifact/assetkinds + `base.yaml` | `aspis artifact subsystem X` creates conformant file |
| 4. INDEX refresh in an existing context script | `.../scripts/context/*` (catalog source) | INDEX lists a created subsystem |
| 5. `architecture-memory` skill | `catalog/skills/architecture-memory/SKILL.md` | SKILL.md valid; ref resolves (cross_ref clean) |
| 6. Wire project-lead (owner) + planning-lead (consumer) + planning workflow | `catalog/agents/project-lead.md`, `…/planning-lead.md`, `catalog/workflows/…` | validate-runtime 33/33; refs resolve |
| 7. Mode-gate the loop | `catalog/config/modes.yaml` | vibe-skip test passes |
| 8. Register new brain dir + purposes | `purposes.json` / FILE_REGISTRY config | `build_registry --check` no blank purpose |
| 9. Seed first subsystem file (this feature's own) | `.aspis/architecture/subsystems/architecture-memory.md` + `INDEX.md` | conformant; listed in INDEX |
| 10. Focused tests | `tests/…` | artifact-creates-conformant, INDEX-lists, vibe-skip; ruff + pytest green |

## Verification
Run before declaring done:
```bash
uv run ruff format --check src tests && uv run ruff check src tests
uv run pytest -q                      # minus known env-hang files if needed
python -m aspis validate-runtime --runtime all   # expect 33/33
python -m aspis artifact subsystem _smoketest && ls .aspis/architecture/subsystems/
```

## Risks & rollback
- **Risk**: the loop becomes heavy process (the 895-line-protocol problem) → mitigated by mode-gating (vibe skips entirely, mvp collapses) and advisory-only INDEX.
- **Risk**: files rot from over- or under-updating → mitigated by FR-004 (only architectural change) + named owner (project-lead) + in-workflow trigger + Last-reviewed date.
- **Risk**: new top-level brain dir not picked up by export/registry → covered by Step 8 (register) + tests; the dir is brain-only, not a runtime asset.
- **Rollback**: the branch is isolated; revert `feature/F-019-architecture-memory`. No live runtime export happens, so deployed projects are untouched until re-init/export.

## Decisions needing approval (R-008)
- **Folder location**: new top-level `.aspis/architecture/` (vs nesting under `context/`). Owner indicated top-level — confirming via this PLAN.
- **F-019 number reassigned** from the previously-noted "models" to Architecture Memory (models/git shift to later numbers). Owner instruction.
- **Mode-gating profile** of the loop (production full / mvp collapsed / vibe skipped). Owner confirmed.
