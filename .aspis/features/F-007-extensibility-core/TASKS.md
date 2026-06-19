# F-007 — Tasks

Format: `- [x] T-NN [P?] [US?] <description> (<exact file path>)`. Mode: **mvp**.
Built directly (no task packets); committed per unit; gate green at each checkpoint.

---

## Phase 1 — P1: the extensibility core

- [x] T-01 [US1] Add the asset-kind registry: `AssetKind` + `KINDS` (discovered default `(brain, copy)` + override table) + helpers `target/op/is_per_runtime/names` (`src/aspis/assetkinds.py`)
- [x] T-02 [US1] Refactor `profiles.py` — `assets: dict[str,list[str]]` via before-validator (YAML format unchanged), `assets()`/`merge()` over the dict, drop the hardcoded `ASSET_KINDS` (`src/aspis/profiles.py`)
- [x] T-03 [US2] Runtime capability model — `capabilities`/`supports(kind)` on `RuntimeAdapter` (permissive default) (`src/aspis/runtimes/base.py`)
- [x] T-04 [US1] [US2] Refactor `export.py` to use the registry + `adapter.supports` (remove `_target_and_op` map + `_RUNTIME_KINDS`) (`src/aspis/export.py`)
- [x] T-05 [US1] [US2] Tests: `test_assetkinds.py` (registry + new-kind drop-in proof) + capability-gating case in `test_export.py` (`tests/test_assetkinds.py`, `tests/test_export.py`)

**Checkpoint**: full suite green; a new brain kind exports via registry + profile alone; per-runtime placement is capability-gated.

---

## Phase 2 — P2: the architecture constitution

- [x] T-06 [US3] Author the constitution (north-star/cost-of-change, automation-before-intelligence→R-003, extension rules, agent-oriented file rules) (`src/aspis/data/catalog/rules/architecture-constitution.md`)
- [x] T-07 [US3] Machine checklist — each rule: `id`, `statement`, `enforced_by`, `review_question` (`src/aspis/data/catalog/config/constitution-checks.yaml`)
- [x] T-08 [US4] Wire the constitution into planning-lead, build-lead, reviewer (thin references, role-scoped) (`src/aspis/data/catalog/agents/planning-lead.md`, `build-lead.md`, `reviewer.md`)
- [x] T-09 [US3] Ship constitution + checklist in the base profile (`src/aspis/data/profiles/base.yaml`)
- [x] T-10 [US3] Tests: `test_constitution.py` — checklist well-formed (ids/roles) + present after a base export (`tests/test_constitution.py`)

**Checkpoint**: constitution ships + parses; the three leads reference it.

---

## Phase 3 — the why + docs

- [x] T-11 Decisions D-008 (everything-extensible) + D-009 (constitution layer) (`.aspis/context/DECISIONS.md`)
- [x] T-12 Update `ARCHITECTURE.md` (asset-kind registry + capability model) and `ROADMAP.md` (F-007 entry; F-005/F-006 deferred + backed up) (`.aspis/context/ARCHITECTURE.md`, `.aspis/context/ROADMAP.md`)
- [x] T-13 Set `active_feature.json` → F-007 (`.aspis/current/active_feature.json`)
- [x] T-14 Final gate sweep — ruff format, ruff check, pytest all green (all files)

**Checkpoint**: full gate green; feature complete; docs reflect the new architecture.

---

## Dependencies

```
T-01 → T-02, T-04;  T-03 → T-04;  T-01..T-04 → T-05
T-06 → T-07 → T-08;  T-06,T-07 → T-09 → T-10
P1 (T-01..T-05) before P2 (T-06..T-10) before P3 (T-11..T-14)
```
