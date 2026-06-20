# F-009 — pre-publish review hardening · Specification

Mode: **mvp** — focused rigor, built directly (no task packets), committed per unit.

## Goal

Work through the user's file-by-file pre-publish review: tighten the parts of ASPIS that
a real user would hit first. Each review point lands as its own task with tests and a
green gate. Models (point 2) is a parallel track gated on the user's model knowledge.

## Review points (source: user, 2026-06-20)

1. **File-purpose detection (3-layer) + code-map skeleton.** FILE_REGISTRY purpose must be
   the best line we can derive. Layer A: extract from the file's own docstring/comment.
   Layer B: a static common-purpose map by filename/glob, shipped defaults + user override,
   authoritative for known meta-files whose first line is a title. Layer C: agent-registered
   purpose for created files that can't carry a comment. Plus a way to pull one file's
   skeleton section from CODE_MAP without reading the whole map.
2. **Models** (parallel track, gated on user knowledge). Correct ids per runtime; free-to-test
   default; OpenCode provider/subscription name formats + detection; per-role pins. The
   tier→model routing machinery already exists; only the data and the free/detection layers
   are new.
3. **Modes ↔ task size.** Task size = f(mode, model capability). Vibe = larger direct tasks on
   a frontier model; cheap models get smaller tasks. Lighter-but-present SPEC/architecture in
   vibe mode.
4. **Dual architecture file.** Initial/BRD architecture stays fixed in root/`docs/` (planning
   lead reads it for the next feature); a second *as-built* architecture in `.aspis/context/`
   records what really exists and is what build/review/planning subagents compare against.
5. **Context-file consolidation + identity discipline.** Review/merge `.aspis/context/` core
   files; drop duplication; keep ASPIS_IDENTITY short, grown only via a strict workflow by the
   system agent.
6. **Active-feature integrity.** `active_feature.json` must be auto-updated/validated by
   scripts+checks on a real feature/phase change, guarded against wrong overwrite and against
   switching while a previous feature is unfinished.
7. **Strip stray `.gitkeep`.** A `.gitkeep` belongs only in an empty dir; remove it the moment
   a dir has real files. Verified stray: `.aspis/features/`, `.aspis/scripts/`.
8. **Production feature artifacts.** A production feature folder can hold SPEC/PLAN/TASKS/
   ACCEPTANCE/(review) + per-task packet folders + per-task builder/reviewer/test report
   folders — but agents don't hand-author them: a tool copies templates in, and creation is
   mode/model-gated (vibe/MVP or a frontier planner-builder may skip reports).
9. **Remove the duplicate hooks dir.** `.aspis/hooks/` (empty) duplicates `.aspis/scripts/hooks/`
   (real). Drop the empty one from the brain skeleton.
10. **System gitignore + categorized templates + incremental test ledger.** A `.gitignore` for
    the system's own generated artifacts; reorganize the flat `templates/` into categories
    (feature/planning/review/report/context); a dated, cached test ledger so the reviewer/tester
    can skip a test that already ran with no relevant change.

## Scope

### Allowed
- `src/aspis/data/catalog/scripts/context/**` — registry/code-map/state builders (points 1, 6).
- `src/aspis/data/catalog/config/**`, `.aspis/config/**` — common-purpose map, models data.
- `src/aspis/data/catalog/agents/**`, `skills/**` — purpose-registration + architecture-read duties.
- `.aspis/context/**`, `.aspis/current/**` — as-built architecture, consolidation, active-feature.
- `tests/**` for every behaviour change; `.aspis/features/F-009-*/**` feature docs.

### Forbidden
- `rules/**`, permission configs — R-009 human gate (raise, don't edit).
- Tracing spine, dashboard (post-v0).

## Acceptance
- Each point: deterministic behaviour, covered by tests, full gate green on Windows.
- No vendor model ids invented for point 2 — they come from the user's knowledge.
