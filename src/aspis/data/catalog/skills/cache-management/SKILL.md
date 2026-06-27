---
name: cache-management
description: Enforce cache-first discipline — check existing research before any new research; route to new research only on cache miss or staleness.
---

# cache-management

## Purpose
The research-lead's cache-first override: before any new research, check the two
cache locations (`.aspis/research/` global and per-feature `Research/`) for an
existing, in-date reference. A cache hit saves a web fetch and keeps the system
cheap. A cache miss or stale entry triggers the full research procedure. This
skill encodes the cache-check logic so the research-lead never skips it.

## When to use
- At step 2 of the research-lead's 4-step procedure, before `knowledge-research`.
- Whenever a delegating lead asks for research on a topic that might already
  be cached.
- When the research-lead detects a topic it has seen before.

## Procedure
1. **Extract the cache key** from the research question:
   - For a library/API question: `{library}@{version}` (e.g. `fastapi@0.115`)
   - For a bug/search question: `{library}@{version}/{symptom-slug}`
   - For a general topic: the topic slug from the question
   - For a validation question: `{claim-hash}` (deterministic hash of the claim)
2. **Check global cache** — scan `.aspis/research/<cache-key>/` for a matching
   reference (`RESEARCH_NOTE.md`, `OFFICIAL_REFERENCES.md`, or a validation
   report).
3. **Check per-feature cache** — if a feature is active, scan
   `.aspis/features/<F-NNN>/Research/` for the same key.
4. **Evaluate staleness** — if a cached reference is found:
   - Check its `Retrieved:` date against the staleness window for its type
     (see the research-lead body for the windows: stable stdlib 6-12mo,
     fast-moving frameworks 30-90d, security advisories 7d, etc.).
   - **Cache hit + fresh** → return a pointer to the cached reference. Skip
     steps 2-3 of the 4-step procedure.
   - **Cache hit + stale** → mark the reference as needing re-validation.
     Proceed with new research but bias toward confirming/updating rather than
     replacing.
   - **Cache miss** → proceed with the full 4-step research procedure.
5. **Record the cache decision** — in the research output, note whether the
   answer came from cache or new research, and the cache key used.

## Outputs
- A cache decision: HIT (fresh), HIT (stale — needs re-validation), or MISS.
- For a cache hit: the cached reference path and its retrieval date.
- For a cache miss: confirmation that the cache was checked and the full
  research procedure is running.

## Anti-patterns
- Skipping the cache check because "it's faster to just search" — web fetches
  cost money and time; cache hits are nearly free.
- Trusting a stale cache entry — 90-day-old framework docs are likely outdated.
  Mark as stale and re-validate.
- Checking only one cache location — both global and per-feature caches are
  valid sources; a feature-scoped reference from a prior feature may answer a
  new question.
- Using the cache key too broadly — "Python" is not a useful cache key. Use
  `{library}@{version}` for specificity.
