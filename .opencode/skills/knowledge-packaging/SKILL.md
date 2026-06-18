---
name: knowledge-packaging
description: Use to turn research findings into a concise, reusable reference asset the whole system can consume — so the same question is never researched twice. Caches knowledge with its source and version.
---

# Knowledge Packaging

## Purpose

Make knowledge reusable. A one-off answer helps one task; a packaged reference helps
every future task that hits the same question — that is the "research once, reuse
everywhere" payoff.

## When to use

After `knowledge-research` produces validated findings worth keeping.

## Procedure

1. **Check for an existing reference** first; update it rather than duplicating.
2. **Distil.** Capture the answer concisely: what it is, how to use it, the key
   facts/snippets a consumer needs — drop the noise.
3. **Stamp provenance.** Record the source and the version the reference reflects,
   so staleness is detectable later.
4. **Make it findable.** Write it where consumers look for references, named for the
   topic so planning/build/fix can locate it.
5. **Hand back** a short summary plus the reference location for the requester.

## Outputs

- A concise, sourced, versioned reference asset, and a pointer to it.

## Anti-patterns

- Returning a raw research dump instead of a distilled reference.
- Duplicating a reference that already exists.
- Omitting source and version, so no one can tell when it's gone stale.
