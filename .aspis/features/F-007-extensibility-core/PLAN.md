# F-007 — Extensibility core + architecture constitution · Plan

Mode: **mvp**. Branched from the F-004 baseline (`4d5d458`). Built directly by the
planning lead + builder (no task packets), committed per unit.

## Approach

A structural refactor with one new seam, then a rules asset on top, then the docs.
Behaviour of existing exports must not change — the unchanged test suite is the
proof — while the *shape* changes so new kinds/runtimes are drop-in.

### The core mechanism (P1)

**One registry, two consumers.**

```
catalog dirs  ──discover──▶  assetkinds.KINDS  ◀──override──  small table
                                   │
                ┌──────────────────┴──────────────────┐
            profiles.py                            export.py
        (assets = kind→paths,                 (target/op + per-runtime
         ASSET_KINDS from registry)            placement from registry,
                                               gated by adapter.supports)
```

- **`assetkinds.py`** — `AssetKind(name, placement, op)`. `placement ∈ {brain,
  per_runtime}`, `op ∈ {copy, render_agent, render_command}`. The registry =
  every catalog subdir defaulting to `(brain, copy)`, with an override table:
  `agents → (per_runtime, render_agent)`, `commands → (per_runtime, render_command)`,
  `skills → (per_runtime, copy)`. Helpers: `target(kind, runtime, rel)`,
  `op(kind)`, `is_per_runtime(kind)`, `names()`.
- **`profiles.py`** — `Profile.assets: dict[str, list[str]]`; a `model_validator`
  folds top-level list keys (everything except `name`/`runtimes`/`include_all`)
  into `assets`, so `base.yaml` is untouched. `assets()` and `merge()` iterate the
  dict; `ASSET_KINDS` is gone (registry owns the order).
- **`runtimes/base.py`** — add `capabilities: frozenset[str] | None = None` and
  `supports(kind) -> bool` (None ⇒ supports everything). `claude.py`/`opencode.py`
  leave it None (no behaviour change).
- **`export.py`** — `_target_and_op` → `assetkinds`; `_RUNTIME_KINDS` →
  `assetkinds.is_per_runtime` + `adapter.supports(kind)`.

### The constitution (P2)

- `catalog/rules/architecture-constitution.md` — the human standards doc.
- `catalog/config/constitution-checks.yaml` — machine checklist (id / statement /
  enforced_by / review_question).
- Thin references added to `agents/planning-lead.md`, `agents/build-lead.md`,
  `agents/reviewer.md`. Ship both via `base.yaml`.

### The why + docs (P3)

- `DECISIONS.md`: D-008, D-009. `ARCHITECTURE.md`: registry + capability model.
- `ROADMAP.md`: F-007 entry; F-005/F-006 deferred + backed up.
- `active_feature.json` → F-007.

## Risks / mitigations

- **Silent export behaviour change** → keep the full suite green at every step;
  `test_export.py`/`test_profiles.py` are the guardrail. Add Story-1/2 tests.
- **Pydantic dict coercion edge cases** (extra keys) → explicit before-validator;
  unit-test that `base.yaml` round-trips to the same asset set as today.
- **Over-engineering the capability model** → keep it to `supports()` with a
  permissive default; no capability registry, no YAML, until hooks return.

## Test strategy

Reuse the existing suite as the regression net. Add: `test_assetkinds.py`
(registry + new-kind drop-in), capability gating in `test_export.py`,
`test_constitution.py` (checklist well-formed + ships in base).
