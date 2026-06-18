---
name: system-validation
description: Use to validate a system change before declaring it done — the asset parses and renders for every target runtime, its references resolve, nothing is duplicated, the project gate is green, and every dependent file was updated.
---

# System Validation

## Purpose

Guard system integrity. No system change is done until it is proven correct — this
is how the System Lead prevents broken runtimes and silent drift.

## When to use

After authoring or changing any system asset, before recording or handing off.

## Procedure

1. **Parses & renders.** The asset is valid and renders for every target runtime
   (the adapters produce correct output, dropping unsupported fields).
2. **References resolve.** Profiles point at real paths; agents' `skills` and
   `delegates` name assets that exist; no dangling references.
3. **No duplication.** The change didn't recreate something that already exists.
4. **Gate green.** Run the project's checks (lint, types, tests). Never weaken a
   test to pass.
5. **Consistency.** Every file that depends on the change was updated — entrypoints,
   profiles, the index, docs.

## Outputs

- A pass/fail verdict with the specific check that failed, if any.

## Anti-patterns

- Declaring done on "it looks right" without running the gate.
- Shipping an asset that renders for one runtime but breaks another.
- Leaving a dangling profile/skill reference, or a stale entrypoint.
