# F-009 / T-015 — ASPS predecessor salvage review

Pre-publish skim of the predecessor **ASPS** repo
(`/mnt/p/AI_Empire/Projects/Agentic Software Production System/ASPS`) for anything worth
salvaging into ASPIS before it goes public. Read-only; no ASPS files were modified.

## Verdicts

| Item (ASPS) | Verdict | Why | Publish | Effort |
|---|---|---|---|---|
| `SECURITY.md` | **KEEP** | ASPIS had none; port + rewrite paths/deps | HIGH | trivial |
| `CODE_OF_CONDUCT.md` | **KEEP** | ASPIS had none; Contributor Covenant 2.1 | HIGH | trivial |
| `CONTRIBUTING.md` | **KEEP (rewrite)** | Port the shape; rewrite commands to ASPIS's gate/CLI/workflow | HIGH | small |
| `ATTRIBUTIONS.md` | **KEEP** | Required — planning skills descend from GitHub Spec Kit (MIT) | HIGH | trivial |
| `CHANGELOG.md` | **KEEP (fresh)** | Write from ASPIS's own F-001…F-009 history; don't copy ASPS | MED-HIGH | trivial |
| Tracing subsystem | **SKIP (mine later)** | ASPIS Phase 4 (reserved); ~5k LOC; not publish-blocking | LOW | large |
| `session_analyzer.py` | **SKIP, cite later** | Valuable *knowledge*: verified OpenCode/Claude transcript field maps — capture as a knowledge asset when Phase 4 starts | LOW today | medium later |
| analyze-session / `asps-analyze` | **ALREADY-IN-ASPIS** | = the `plan-critic` skill (both descend from Spec Kit `analyze.md`) | LOW | — |
| Dashboard / dashboard-ui | **SKIP** | ASPIS Phase 6 (reserved); web UI is a maintenance/security liability for v0 | LOW | large |
| planning-kit | **MOSTLY ALREADY-IN-ASPIS** | Maps to planning-intake/feature-planning/architecture-planning/task-decomposition/plan-critic; 3 checklists optionally shippable as reference data | LOW | small |
| policy data (secret/junk/protected) | **ALREADY-IN-ASPIS** | Rebuilt as `catalog/config/hooks.yaml` | LOW | verify |
| profiles, agents, skills | **ALREADY-IN-ASPIS** | ASPIS roster + skills supersede them | LOW | — |
| `docs/faq.md` | **KEEP (optional)** | Nice public touch; rewrite for ASPIS | LOW-MED | small |
| `.pre-commit-config.yaml`, ASPS-internal docs | **SKIP** | Duplicate ASPIS's own hook surface / stale | LOW | — |

## Do before publish today (HIGH, low-effort) — T-016
Add the five OSS governance files ASPIS currently lacks: **SECURITY.md, CODE_OF_CONDUCT.md,
CONTRIBUTING.md, ATTRIBUTIONS.md, CHANGELOG.md** — tailored to ASPIS reality (MIT, `uv`+ruff+pytest
gate, `aspis` CLI, file-first workflow). None touch engine code.

## Verified (no gap)
- **Fallback/recovery** is covered by ASPIS's `corrective-fix` + `system-repair` skills (+ `fix-lead`).
- **Spec Kit provenance** is already acknowledged in `.aspis/context/IDENTITY.md` and `CORE_LOOP.md`
  ("not a clone… harvests good ideas"; spec→plan→tasks→implement discipline) — basis for ATTRIBUTIONS.

## Defer / post-publish
Tracing spine (Phase 4, mine `session_analyzer.py` knowledge + the one-writer/run_id design),
dashboard (Phase 6), planning-kit checklists as reference data, `docs/faq.md`. The models/routing
work (review points 2, 3) is **deferred to feature F-010**.
